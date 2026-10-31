"""Build the Orpington 2001 crowd's character sheets: python3 tools/v76/foe_sheets.py [key ...]

The source for each kind is one PixelLab workbench sheet, tools/v76/src/<key>.png: `join character:<id>:east:<anim> ...
--as rows` (the preview it saves: an 18 px label strip on top, then one animation per row, every cell the same size, the
smaller template animations set on the bottom edge, empty cells and the background one flat colour). Row order is ROWS
below. Writes web/sprites/<key>.png and the SPRITE_META / FOE_FRAMES entries into tools/v76/sheets.json, the same way
tools/v72/foe_sheets.py does (its helpers come from tools/v53/foe_sheets.py): every row lined up on the idle's first frame,
stray specks cleaned off, the knockdown built from PixelLab's falling-back-death + getting-up templates.

Frame numbers in KINDS count from 0 (0 is the standing reference frame in the v3 animations)."""
import importlib.util, json, os, re, sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
spec = importlib.util.spec_from_file_location('fs53', os.path.join(ROOT, 'tools', 'v53', 'foe_sheets.py'))
fs = importlib.util.module_from_spec(spec); spec.loader.exec_module(fs)
STD = fs.STD
LAB = 18
BASE = ['idle', 'walk', 'attack', 'hurt', 'fall', 'getup']   # the source rows every kind has, in this order, then its own

# key: (its own rows, in source order after BASE), options
#   moves: pre / hit / post frames for a row's strike;  wind / hits: which row a state shows (pre frames / hit frame)
#   loop: a state that plays a run of a row's frames round and round (the scooter ride, the MC on the mic)
#   lean: a state drawn leaning forward by this much (the builder's barge)
KINDS = {
    'kappa': (['whip'], {'moves': {'attack': {'pre': [1], 'hit': 2, 'post': [3]}, 'whip': {'pre': [1, 4], 'hit': 5, 'post': [8]}},
                         'wind': {'whipWind': 'whip'}, 'hits': {'whip': 'whip'}}),
    'razor': (['ride', 'kick'], {'moves': {'attack': {'pre': [1, 2], 'hit': 3, 'post': [5]}, 'kick': {'pre': [3, 4], 'hit': 7, 'post': [8]},
                                           'ride': {'pre': [1, 2], 'hit': 4, 'post': [8]}},
                                 'wind': {'rideWind': 'ride', 'kickWind': 'kick'}, 'hits': {'kick': 'kick'}, 'loop': {'ride': ['ride', [3, 4, 5, 6, 7]]}}),
    'frosted': (['spin', 'slide'], {'moves': {'attack': {'pre': [1, 8], 'hit': 3, 'post': [4]}, 'spin': {'pre': [1, 2], 'hit': 3, 'post': [5]},
                                              'slide': {'pre': [0, 1], 'hit': 2, 'post': [4]}},
                                    'wind': {'spinKickWind': 'spin', 'kneeSlideWind': 'slide'}, 'hits': {'spinKick': 'spin', 'kneeSlide': 'slide'}}),
    'scrunchie': (['throw'], {'moves': {'attack': {'pre': [5, 6], 'hit': 7, 'post': [8]}, 'throw': {'pre': [1], 'hit': 2, 'post': [3]}},
                              'wind': {'throwWind': 'throw'}, 'hits': {'throwing': 'throw'}}),
    'garagemc': (['bars'], {'speck': 30, 'moves': {'attack': {'pre': [2, 3], 'hit': 4, 'post': [6]}, 'bars': {'pre': [1, 2, 3], 'hit': 4, 'post': [8]}},
                            'wind': {'barsWind': 'bars'}, 'loop': {'bars': ['bars', [1, 2, 3, 4, 5, 6, 7, 8]]}}),
    'builder': (['barge', 'throw'], {'speck': 40, 'moves': {'attack': {'pre': [5, 6], 'hit': 8, 'post': [4]}, 'barge': {'pre': [1, 2, 3], 'hit': 7, 'post': [8]},
                                                            'throw': {'pre': [3, 4, 5, 6], 'hit': 8, 'post': [7]}},
                                     'wind': {'bargeWind': 'barge', 'throwWind': 'throw'}, 'hits': {'throwStool': 'throw', 'stars': 'barge'},
                                     'loop': {'barge': ['barge', [6, 7]]}, 'lean': {'barge': 0.2}}),
    'codger': (['hook'], {'moves': {'attack': {'pre': [4, 5], 'hit': 7, 'post': [6]}, 'hook': {'pre': [3, 4, 5], 'hit': 7, 'post': [6]}},
                          'wind': {'hookWind': 'hook'}, 'hits': {'hookOut': 'hook', 'crook': 'hook', 'dig': 'attack'}}),
    'shark': (['break'], {'moves': {'attack': {'pre': [2], 'hit': 4, 'post': [6]}, 'break': {'pre': [3, 4, 5], 'hit': 7, 'post': [8]}},
                          'wind': {'breakWind': 'break'}, 'hits': {'breakShot': 'break'}}),
    'moschino': (['spray'], {'moves': {'attack': {'pre': [4, 5], 'hit': 8, 'post': [7]}, 'spray': {'pre': [2, 3, 4, 5, 4, 3, 4], 'hit': 5, 'post': [8]}},
                             'wind': {'shakeWind': 'spray'}, 'hits': {'spray': 'spray'}}),
    'raver': (['whistle'], {'moves': {'attack': {'pre': [1], 'hit': 3, 'post': [4]}, 'whistle': {'pre': [1, 2, 3], 'hit': 6, 'post': [8]}},
                            'wind': {'whistleWind': 'whistle', 'flurryWind': 'attack'}, 'loop': {'flurry': ['attack', [2, 3, 5, 6]], 'whistle': ['whistle', [4, 5, 6, 7]]}}),
}


def load(key, own, speck):
    """the joined sheet as {row name: [frames]} and its cell size"""
    im = np.array(Image.open(os.path.join(HERE, 'src', key + '.png')).convert('RGBA'))
    names = BASE + own; nrows = len(names)
    cell = (im.shape[0] - LAB) // nrows; bg = im[LAB // 2, 2, :3].copy(); ncol = im.shape[1] // cell
    out = {}
    for r, name in enumerate(names):
        fr = []
        for c in range(ncol):
            blk = im[LAB + r * cell: LAB + (r + 1) * cell, c * cell: (c + 1) * cell].copy()
            key_ = (np.abs(blk[..., :3].astype(int) - bg.astype(int)).sum(-1) <= 3)
            if key_.all(): break
            blk[key_] = 0; blk[..., 3] = np.where(key_, 0, 255)
            fr.append(fs.clean(blk, speck, 8))
        out[name] = fr
    return out, cell


def put(f, dx, dy, c):
    out = np.zeros((c, c, 4), np.uint8); ys, xs = np.where(f[..., 3] > 0); ty, tx = ys + dy, xs + dx
    ok = (ty >= 0) & (ty < c) & (tx >= 0) & (tx < c); out[ty[ok], tx[ok]] = f[ys[ok], xs[ok]]; return out


def knockdown(rows, c):
    """fall (standing first) + its last frame again + the get-up moved so its first (lying) frame sits on the fall's last"""
    fall, up = rows['fall'], rows['getup']
    a = fs.bbox(fall[-1]); b = fs.bbox(up[0])
    dx = round((a[0] + a[2]) / 2 - (b[0] + b[2]) / 2); dy = a[3] - b[3]
    return fall + [fall[-1]] + [put(f, dx, dy, c) for f in up]


def build(key):
    own, opts = KINDS[key]
    src, c = load(key, own, opts.get('speck', 20))
    rows = STD + own
    loaded = {r: src[r] for r in rows if r != 'knockdown'}; loaded['knockdown'] = knockdown(src, c)
    cell = c + 4 + (c + 4) % 2
    ref = fs.bbox(loaded['idle'][0]); base = (cell - c) // 2
    ncol = max(len(f) for f in loaded.values())
    sheet = np.zeros((len(rows) * cell, ncol * cell, 4), np.uint8); meta_rows = {}
    for ri, r in enumerate(rows):
        fr = loaded[r]; b = fs.bbox(fr[0])
        # line every row up on the idle's first frame: same middle, same feet (the fall and get-up keep their own feet)
        dx = round((ref[0] + ref[2]) / 2 - (b[0] + b[2]) / 2) + base; dy = ref[3] - b[3] + base
        for k, f in enumerate(fr):
            ys, xs = np.where(f[..., 3] > 0); ty, tx = ys + dy, xs + dx; ok = (ty >= 0) & (ty < cell) & (tx >= 0) & (tx < cell)
            sheet[ri * cell + ty[ok], k * cell + tx[ok]] = f[ys[ok], xs[ok]]
        meta_rows[r] = [ri, len(fr)]
    Image.fromarray(sheet, 'RGBA').save(os.path.join(ROOT, 'web', 'sprites', key + '.png'), optimize=True)
    ax = round((ref[0] + ref[2]) / 2 + base + 0.5, 1); ay = int(ref[3] + 1 + base); h = int(ref[3] - ref[1] + 1)
    meta = {'cell': int(cell), 'ax': ax, 'ay': ay, 'h': h, 'rows': meta_rows, 'fist': {}}
    n = lambda r: meta_rows[r][1]
    F = {'attack': fs.mv(n('attack'))}
    for r in own: F[r] = fs.mv(n(r))
    F['hurt'] = [1, min(3, n('hurt') - 1)]
    F.update({'fall': [1, 2, 3, 4, 5], 'lie': 6, 'up': [8, 9, 10, 11, 12]})   # the template fall (0-6), held (7), get-up (8-12)
    F.update(opts.get('moves', {}))
    for k in ('wind', 'hits', 'loop', 'lean'):
        if opts.get(k): F[k] = opts[k]
    F['fallFlip'] = False   # the templates fall backwards, away from the hit, as drawn
    js = re.sub(r'"(\w+)": ', r'\1: ', json.dumps(F, separators=(', ', ': ')))
    return {'meta': meta, 'frames': js}


if __name__ == '__main__':
    out_p = os.path.join(HERE, 'sheets.json')
    out = json.load(open(out_p)) if os.path.exists(out_p) else {}
    for key in (sys.argv[1:] or [k for k in KINDS if os.path.exists(os.path.join(HERE, 'src', k + '.png'))]):
        r = build(key); out[key] = r
        print(key, 'cell', r['meta']['cell'], 'rows', {k: v[1] for k, v in r['meta']['rows'].items()})
    json.dump(out, open(out_p, 'w'), indent=1)
