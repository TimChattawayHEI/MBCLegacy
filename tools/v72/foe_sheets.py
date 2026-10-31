"""Build the Orpington 2001 character sheets: python3 tools/v72/foe_sheets.py [key ...]

Same as tools/v53/foe_sheets.py (whose helpers it uses): PixelLab workbench sheets from tools/v72/src/<key>/<anim>.png
become web/sprites/<key>.png plus SPRITE_META / FOE_FRAMES entries in tools/v72/sheets.json.

One difference: where a kind has no knockdown.png but has fall.png and getup.png (PixelLab's falling-back-death and
getting-up templates, used because the generated knockdowns kept falling forward onto the face), the knockdown row is
built from them: the fall's 7 frames, the last one held, then the get-up's 5, the get-up's lying frame set where the
fall ended so nothing jumps."""
import importlib.util, json, os, re, sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
spec = importlib.util.spec_from_file_location('fs53', os.path.join(ROOT, 'tools', 'v53', 'foe_sheets.py'))
fs = importlib.util.module_from_spec(spec); spec.loader.exec_module(fs)
STD = fs.STD

KINDS = {
    # Sue's hurt has a white smear on its third frame, so the snap back uses frames 1 and 3
    'sue': (STD + ['shout'], {'moves': {'shout': {'pre': [1, 2, 3, 4], 'hit': 6, 'post': [8]}}, 'hurtPick': [1, 3],
                              'wind': {'oiWind': 'shout'}, 'hits': {'oi': 'shout'}}),
    'alan': (STD, {'speck': 60, 'moves': {'attack': {'pre': [2, 3, 4], 'hit': 6, 'post': [8]}}}),
    'jeff': (STD, {'speck': 40, 'moves': {'attack': {'pre': [2, 3, 4], 'hit': 7, 'post': [8]}}}),
    # Mick's knockdown is his own (it falls the right way); its frame 3 has speed lines and 6 to 8 white specks
    'mick': (STD + ['belly'], {'speck': 80, 'kdPick': {'fall': [4, 5, 9, 10], 'lie': 11, 'up': [13, 14, 15, 16]},
                               'moves': {'attack': {'pre': [4, 5, 6], 'hit': 7, 'post': [8]}, 'belly': {'pre': [2, 3, 4, 5], 'hit': 8, 'post': [8]}},
                               'wind': {'bellyWind': 'belly', 'bellWind': 'attack'}, 'hits': {'belly': 'belly'}}),
}


def knockdown_frames(d, speck):
    """fall (standing first) + its last frame again + getup moved so its first (lying) frame sits on the fall's last"""
    fall, c1 = fs.frames_of(os.path.join(d, 'fall.png'), speck); up, c2 = fs.frames_of(os.path.join(d, 'getup.png'), speck)
    c = max(c1, c2)
    def put(f, dx, dy):
        out = np.zeros((c, c, 4), np.uint8); ys, xs = np.where(f[..., 3] > 0); ty, tx = ys + dy, xs + dx
        ok = (ty >= 0) & (ty < c) & (tx >= 0) & (tx < c); out[ty[ok], tx[ok]] = f[ys[ok], xs[ok]]; return out
    off = (c - c1) // 2
    fall = [put(f, off, c - c1) for f in fall]
    a = fs.bbox(fall[-1]); b = fs.bbox(up[0])
    dx = round((a[0] + a[2]) / 2 - (b[0] + b[2]) / 2); dy = a[3] - b[3]
    up = [put(f, dx, dy) for f in up]
    return fall + [fall[-1]] + up, c


def build(key):
    rows, opts = KINDS[key]; d = os.path.join(HERE, 'src', key); speck = opts.get('speck', 12)
    loaded = {}
    for r in rows:
        p = os.path.join(d, r + '.png')
        if r == 'knockdown' and not os.path.exists(p): loaded[r] = knockdown_frames(d, speck); continue
        loaded[r] = fs.frames_of(p, speck, opts.get('conn', 8))
    canvas = max(c for _, c in loaded.values()); cell = canvas + 4 + (canvas + 4) % 2
    ref = fs.bbox(loaded['idle'][0][0]); refc = loaded['idle'][1]
    ncol = max(len(f) for f, _ in loaded.values())
    sheet = np.zeros((len(rows) * cell, ncol * cell, 4), np.uint8); meta_rows = {}
    base_dx = (cell - refc) // 2
    for ri, r in enumerate(rows):
        fr, c = loaded[r]; b = fs.bbox(fr[0])
        dx = round((ref[0] + ref[2]) / 2 - (b[0] + b[2]) / 2) + base_dx; dy = ref[3] - b[3] + (cell - refc) // 2
        for k, f in enumerate(fr):
            ys, xs = np.where(f[..., 3] > 0)
            ty, tx = ys + dy, xs + dx; ok = (ty >= 0) & (ty < cell) & (tx >= 0) & (tx < cell)
            sheet[ri * cell + ty[ok], k * cell + tx[ok]] = f[ys[ok], xs[ok]]
        meta_rows[r] = [ri, len(fr)]
    Image.fromarray(sheet, 'RGBA').save(os.path.join(ROOT, 'web', 'sprites', key + '.png'), optimize=True)
    ax = round((ref[0] + ref[2]) / 2 + base_dx + 0.5, 1); ay = int(ref[3] + 1 + (cell - refc) // 2); h = int(ref[3] - ref[1] + 1)
    meta = {'cell': int(cell), 'ax': ax, 'ay': ay, 'h': h, 'rows': meta_rows, 'fist': {}}
    n = lambda r: meta_rows[r][1]
    F = {'attack': fs.mv(n('attack'))}
    for r in rows:
        if r not in STD: F[r] = fs.mv(n(r))
    F['hurt'] = opts.get('hurtPick', [min(1, n('hurt') - 1), min(2, n('hurt') - 1)])
    if os.path.exists(os.path.join(d, 'knockdown.png')): F.update(opts.get('kdPick', {'fall': [3, 4, 5, 6], 'lie': 8, 'up': [11, 12, 13, 14, 15]}))
    else: F.update({'fall': [1, 2, 3, 4, 5], 'lie': 6, 'up': [8, 9, 10, 11, 12]})   # the template fall (0-6), held (7), get-up (8-12)
    F.update(opts.get('moves', {}))
    if opts.get('wind'): F['wind'] = opts['wind']
    if opts.get('hits'): F['hits'] = opts['hits']
    F['fallFlip'] = False   # all four fall backwards, away from the hit, as drawn (the game flips sheets that fall face first)
    js = re.sub(r'"(\w+)": ', r'\1: ', json.dumps(F, separators=(', ', ': ')))
    return {'meta': meta, 'frames': js}


if __name__ == '__main__':
    out_p = os.path.join(HERE, 'sheets.json')
    out = json.load(open(out_p)) if os.path.exists(out_p) else {}
    for key in (sys.argv[1:] or KINDS):
        r = build(key); out[key] = r
        print(key, 'cell', r['meta']['cell'], 'rows', {k: v[1] for k, v in r['meta']['rows'].items()})
    json.dump(out, open(out_p, 'w'), indent=1)
