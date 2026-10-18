"""Build the Nightlife 2006 character sheets: python3 tools/v53/foe_sheets.py [key ...]

Reads PixelLab workbench sheets (`inspect character:<id>:east:<anim> --scale 2`) from tools/v53/src/<key>/<anim>.png and
writes web/sprites/<key>.png (one row per animation, frames left to right, every animation lined up on its first,
standing frame) plus the SPRITE_META / FOE_FRAMES entries for each into tools/v53/sheets.json.
Stray specks the generator sometimes leaves round a sprite are cleaned off.
"""
import json, os, re, sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
LAB, S = 18, 2

# key: rows in order, then which states use which rows (FOE_FRAMES wind / hits)
STD = ['idle', 'walk', 'attack', 'hurt', 'knockdown']
KINDS = {
    'city': (STD + ['throw'], {}), 'itgirl': (STD + ['kick'], {}), 'burb': (STD, {}), 'hoops': (STD + ['pull'], {}),
    'snood': (STD, {}), 'puffer': (STD + ['dash'], {}), 'hood': (STD, {}),
    'grappler': (STD + ['hold'], {'hits': {'hug': 'hold'}}),
    'dipper': (STD + ['dodge', 'steal'], {'hits': {'dodge': 'dodge'}}),
    'lookout': (STD + ['whistle'], {'hits': {'whistle': 'whistle'}}),
    'stag': (STD + ['stagger'], {}), 'groom': (STD, {}),
    'inspector': (STD + ['attack2', 'block', 'shout'], {'wind': {'slapWind': 'attack2', 'fineWind': 'shout', 'blockWind': 'block'},
                                                          'hits': {'slap': 'attack2', 'fine': 'shout', 'block': 'block'}}),
    'lenny': (STD + ['attack2', 'pull', 'charge'], {'wind': {'alarmWind': 'pull', 'doorWind': 'pull', 'kneeWind': 'attack2', 'chargeWind': 'charge'},
                                                     'hits': {'alarm': 'pull', 'doorOpen': 'pull', 'knee': 'attack2', 'charge': 'charge'}}),
    'jeweller': (STD + ['glint', 'grab'], {'wind': {'whipWind': 'attack', 'glintWind': 'glint', 'grabWind': 'grab'},
                                           'hits': {'whip': 'attack', 'glint': 'glint', 'grabLunge': 'grab', 'grabHold': 'grab'}}),
    'commuter': (['idle', 'walk'], {'srcmap': {'walk': 'run'}}), 'oldboy': (['idle', 'walk'], {'srcmap': {'walk': 'run'}}),
    'smiler': (['idle', 'walk', 'throw'], {'srcmap': {'walk': 'idle'}, 'hits': {'throw': 'throw'}}),
}


def frames_of(path):
    im = np.array(Image.open(path).convert('RGBA'))
    H, Wd = im.shape[:2]
    canvas = None
    for c in (3, 4, 5, 6):
        if Wd % c: continue
        cw = Wd // c
        if cw % 2 == 0 and H % (cw + LAB) == 0: canvas = cw // 2; cols = c; break
    if canvas is None: raise ValueError(f'{path}: can\'t work out the grid ({Wd}x{H})')
    cw = canvas * S; ch = cw + LAB; rows = H // ch; bg = im[2, 2, :3]; out = []
    for r in range(rows):
        for c in range(cols):
            blk = im[r * ch + LAB: r * ch + LAB + cw, c * cw: (c + 1) * cw]
            f = blk[::S, ::S].copy(); key = (f[..., :3] == bg).all(-1)
            if key.all(): continue
            f[key] = 0; out.append(clean(f))
    return out, canvas


def clean(f):
    """drop specks: keep the biggest blob and anything of a dozen pixels or more"""
    a = f[..., 3] > 0; h, w = a.shape; lab = np.zeros((h, w), int); n = 0; sizes = {}
    for y in range(h):
        for x in range(w):
            if a[y, x] and not lab[y, x]:
                n += 1; st = [(y, x)]; lab[y, x] = n; cnt = 0
                while st:
                    cy, cx = st.pop(); cnt += 1
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            yy, xx = cy + dy, cx + dx
                            if 0 <= yy < h and 0 <= xx < w and a[yy, xx] and not lab[yy, xx]: lab[yy, xx] = n; st.append((yy, xx))
                sizes[n] = cnt
    if not sizes: return f
    big = max(sizes, key=sizes.get)
    for k, v in sizes.items():
        if k != big and v < 12: f[lab == k] = 0
    return f


def bbox(f):
    ys, xs = np.where(f[..., 3] > 0); return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())


def mv(n):
    """pre / hit / post frames for a generated strike of n frames (frame 0 is the standing reference)"""
    if n >= 9: return {'pre': [2, 3, 4], 'hit': 5, 'post': [6, 7]}
    if n >= 7: return {'pre': [1, 2, 3], 'hit': 4, 'post': [5, 6]}
    return {'pre': [1, 2], 'hit': 3, 'post': [n - 1]}


def build(key):
    rows, opts = KINDS[key]; srcmap = opts.get('srcmap', {}); d = os.path.join(HERE, 'src', key)
    loaded = {}
    for r in rows:
        src = srcmap.get(r, r); p = os.path.join(d, src + '.png')
        if not os.path.exists(p):
            p = os.path.join(d, 'attack.png' if r not in ('idle', 'walk', 'hurt', 'knockdown') else 'idle.png')
            if not os.path.exists(p): p = os.path.join(d, 'idle.png')
        if not os.path.exists(p): return None
        loaded[r] = frames_of(p)
    canvas = max(c for _, c in loaded.values()); cell = canvas + 4 + (canvas + 4) % 2
    ref = bbox(loaded['idle'][0][0]); refc = loaded['idle'][1]
    ncol = max(len(f) for f, _ in loaded.values())
    sheet = np.zeros((len(rows) * cell, ncol * cell, 4), np.uint8); meta_rows = {}
    base_dx = (cell - refc) // 2
    for ri, r in enumerate(rows):
        fr, c = loaded[r]; b = bbox(fr[0])
        dx = round((ref[0] + ref[2]) / 2 - (b[0] + b[2]) / 2) + base_dx; dy = ref[3] - b[3] + (cell - refc) // 2 + (refc - refc)
        for k, f in enumerate(fr):
            ys, xs = np.where(f[..., 3] > 0)
            ty, tx = ys + dy, xs + dx; ok = (ty >= 0) & (ty < cell) & (tx >= 0) & (tx < cell)
            sheet[ri * cell + ty[ok], k * cell + tx[ok]] = f[ys[ok], xs[ok]]
        meta_rows[r] = [ri, len(fr)]
    Image.fromarray(sheet, 'RGBA').save(os.path.join(ROOT, 'web', 'sprites', key + '.png'), optimize=True)
    ax = round((ref[0] + ref[2]) / 2 + base_dx + 0.5, 1); ay = int(ref[3] + 1 + (cell - refc) // 2); h = int(ref[3] - ref[1] + 1)
    meta = {'cell': int(cell), 'ax': ax, 'ay': ay, 'h': h, 'rows': meta_rows, 'fist': {}}
    F = {}
    n = lambda r: meta_rows[r][1]
    if 'attack' in meta_rows: F['attack'] = mv(n('attack'))
    for r in rows:
        if r not in STD: F[r] = mv(n(r))
    if 'hurt' in meta_rows: F['hurt'] = [min(2, n('hurt') - 1), min(3, n('hurt') - 1)]
    if 'knockdown' in meta_rows and n('knockdown') >= 16:
        F.update({'fall': [3, 4, 5, 6], 'lie': 8, 'up': [11, 12, 13, 14, 15]})
    else:
        F.update({'fall': [1], 'lie': 1, 'up': [1]})
        F.setdefault('hurt', [1, 1]); F.setdefault('attack', {'pre': [1], 'hit': 1, 'post': [1]})
    if opts.get('wind'): F['wind'] = opts['wind']
    if opts.get('hits'): F['hits'] = opts['hits']
    F['fallFlip'] = True
    js = re.sub(r'"(\w+)": ', r'\1: ', json.dumps(F, separators=(', ', ': ')))
    return {'meta': meta, 'frames': js}


if __name__ == '__main__':
    out_p = os.path.join(HERE, 'sheets.json')
    out = json.load(open(out_p)) if os.path.exists(out_p) else {}
    for key in (sys.argv[1:] or KINDS):
        if not os.path.isdir(os.path.join(HERE, 'src', key)): continue
        try:
            r = build(key)
        except Exception as e:
            print(key, 'skipped:', e); continue
        if r: out[key] = r; print(key, 'cell', r['meta']['cell'], 'rows', {k: v[1] for k, v in r['meta']['rows'].items()})
    json.dump(out, open(out_p, 'w'), indent=1)
