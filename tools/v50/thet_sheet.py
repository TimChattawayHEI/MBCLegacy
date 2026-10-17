"""Build Thet's sprite sheet: python3 tools/v50/thet_sheet.py

Reads the PixelLab workbench sheets in tools/v50/src/<anim>.png (`inspect character:<id>:east:<anim> --scale 2`:
frames on a grid at 2x, each under an 18px label, canvas 60px) and writes
  web/sprites/thet.png         17 rows, one per animation, cell CELL px, frames left to right
  tools/v50/thet_meta.json     SPRITE_META entry (cell, anchor, height, rows, hand points) and LAD_FRAMES entry
Every animation's first frame is the same standing reference, so each animation is lined up on it.
"""
import json, os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CANVAS, S, LAB, CELL = 60, 2, 18, 64
# row order matches every other lad's sheet; frame picks reorder or trim a generated animation
ROWS = ['idle', 'walk', 'jab', 'hook', 'kick', 'jumpkick', 'hurt', 'knockdown', 'special', 'run', 'grab', 'knee', 'throw',
        'backkick', 'pickup', 'swing', 'mini']
PICK = {'idle': [0, 3, 4, 5, 6, 5, 4]}
FLIP = {'backkick'}   # generated kicking forwards: mirrored, he turns and kicks behind him
SRC = {}   # an animation borrowed from another while its own is missing
for r in ROWS:
    SRC[r] = r
FALLBACK = {'backkick': 'kick', 'pickup': 'hurt', 'swing': 'hook', 'mini': 'run', 'throw': 'hook', 'knee': 'kick', 'grab': 'jab',
            'run': 'walk', 'special': 'jumpkick', 'knockdown': 'hurt'}
SKIN = {(0xea, 0xa8, 0x7b), (0xad, 0x63, 0x48), (0xa1, 0x57, 0x42), (0xf3, 0xb6, 0x83), (0x9e, 0x55, 0x3e)}


def frames_of(path):
    im = np.array(Image.open(path).convert('RGBA'))
    cw = CANVAS * S; ch = cw + LAB; cols = im.shape[1] // cw; rows = im.shape[0] // ch
    bg = im[2, 2, :3]; out = []
    for r in range(rows):
        for c in range(cols):
            blk = im[r * ch + LAB: r * ch + LAB + cw, c * cw: (c + 1) * cw]
            if blk.shape[0] < cw or blk.shape[1] < cw: continue
            f = blk[::S, ::S].copy(); key = (f[..., :3] == bg).all(-1)
            if key.all(): continue
            f[key] = 0; out.append(f)
    return out


def bbox(f):
    ys, xs = np.where(f[..., 3] > 0); return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())


def hand(f, face_x):
    """the frontmost bit of skin below the head: where a weapon goes"""
    x0, y0, x1, y1 = bbox(f); h = y1 - y0
    ys, xs = np.where(np.array([[tuple(px[:3]) in SKIN and px[3] > 0 for px in row] for row in f]))
    ok = ys > y0 + h * 0.28
    if not ok.any(): return [int(face_x + 6), int(y0 + h * 0.45)]
    i = np.argmax(xs[ok]); return [int(xs[ok][i]), int(ys[ok][i])]


ref = None; sheet = np.zeros((len(ROWS) * CELL, 17 * CELL, 4), np.uint8); rows = {}; fist = {}; missing = []
for ri, name in enumerate(ROWS):
    src = name
    while not os.path.exists(os.path.join(HERE, 'src', src + '.png')):
        src = FALLBACK.get(src, 'idle')
    if src != name: missing.append(f'{name}<-{src}')
    fr = frames_of(os.path.join(HERE, 'src', src + '.png'))
    if ref is None: ref = bbox(fr[0])
    b = bbox(fr[0]); dx = round((ref[0] + ref[2]) / 2 - (b[0] + b[2]) / 2); dy = ref[3] - b[3]
    pick = PICK.get(name, list(range(len(fr)))) if src == name else list(range(len(fr)))
    off = (CELL - CANVAS) // 2
    fist[name] = []
    for k, fi in enumerate(pick):
        f = fr[fi]
        if name in FLIP and k > 0:
            cx = (b[0] + b[2]) / 2; m = np.zeros_like(f)
            for y in range(CANVAS):
                for x in range(CANVAS):
                    tx = int(round(2 * cx - x))
                    if 0 <= tx < CANVAS: m[y, tx] = f[y, x]
            f = m
        for y in range(CANVAS):
            for x in range(CANVAS):
                if f[y, x, 3] == 0: continue
                tx, ty = x + dx + off, y + dy + off
                if 0 <= tx < CELL and 0 <= ty < CELL: sheet[ri * CELL + ty, k * CELL + tx] = f[y, x]
        hx, hy = hand(f, (ref[0] + ref[2]) / 2); fist[name].append([hx + dx + off, hy + dy + off])
    rows[name] = [ri, len(pick)]
Image.fromarray(sheet, 'RGBA').save(os.path.join(ROOT, 'web', 'sprites', 'thet.png'), optimize=True)
ax = round((ref[0] + ref[2]) / 2 + (CELL - CANVAS) // 2 + 0.5, 1); ay = int(ref[3] + 1 + (CELL - CANVAS) // 2); h = int(ref[3] - ref[1] + 1)
meta = {'cell': CELL, 'ax': ax, 'ay': ay, 'h': h, 'rows': rows, 'fist': fist}
n = {k: v[1] for k, v in rows.items()}
last = lambda k: n[k] - 1
# hit frames: the middle of each generated strike (frame 0 is the standing reference)
frames = ("{ jab: { pre: [1, 2, 3, 4], hit: 5, post: [6] }, hook: { pre: [1, 2, 3], hit: 4, post: [5, 6] }, kick: { pre: [1, 2, 3], hit: 4, post: [5, 6] },"
          f" tuck: ['jumpkick', 2], air: ['jumpkick', 4], crouch: ['jumpkick', 1], hurt: [2, 3], fall: [3, 4, 5, 6, 7, 8], lie: 10, up: [13, 14, 15, 16],"
          f" special: [{', '.join(str(i) for i in range(1, n['special']))}], run: [3, 4, 5, 6, 7, 8], grab: [1, 2, 3, 4],"
          " knee: { pre: [3, 4], hit: 5, post: [6] }, throw: { pre: [3, 5], hit: 7, post: [8] }, backkick: { pre: [1, 2], hit: 3, post: [4, 5] },"
          f" pickup: [3, 4], swing: {{ pre: [1, 2, 3], hit: 4, post: [5, 6] }}, mini: [{', '.join(str(i) for i in range(1, n['mini']))}] }}")
json.dump({'meta': meta, 'frames': frames}, open(os.path.join(HERE, 'thet_meta.json'), 'w'), indent=1)
print('thet sheet', sheet.shape, 'anchor', ax, ay, 'height', h, 'borrowed:', ', '.join(missing) or 'none')
