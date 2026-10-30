"""Version 68: Seb redrawn from Tim's photos. Builds web/sprites/seb.png and pose_seb.png: python3 tools/v68/seb_sheet.py

PixelLab character "Seb v4" 2086de59-ed32-490e-872e-e23cd2c44403 (v3, 64px, side view): buzz cut, ginger stubble, no
sunglasses, olive-grey short-sleeved shirt over a white tee, jeans, brown boots, watch. Frames are the PixelLab workbench
sheets in tools/v68/src/<anim>.png (`inspect character:<id>:east:<anim> --scale 2`). Rows and frame counts match the old
sheet, so LAD_FRAMES keeps working; the new picks are in seb_meta.json. The back kick is gone from the game (Version 65),
so its row is a copy of the kick.
"""
import json, os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(HERE, 'src')
S, LAB = 2, 18
ROWS = ['idle', 'walk', 'jab', 'hook', 'kick', 'jumpkick', 'hurt', 'knockdown', 'special', 'run', 'grab', 'knee', 'throw',
        'backkick', 'pickup', 'swing', 'mini']
# frames that turned away from the camera are swapped for their neighbours
PICK = {'hurt': [0, 1, 2, 2, 1], 'grab': [0, 1, 2, 2, 2]}
SRC_OF = {'backkick': 'kick'}

def frames_of(path, canvas):
    im = np.array(Image.open(path).convert('RGBA'))
    cw = canvas * S; ch = cw + LAB; cols = im.shape[1] // cw; rows = im.shape[0] // ch
    bg = im[2, 2, :3]; out = []
    for r in range(rows):
        for c in range(cols):
            blk = im[r * ch + LAB: r * ch + LAB + cw, c * cw: (c + 1) * cw]
            if blk.shape[0] < cw or blk.shape[1] < cw: continue
            f = blk[::S, ::S].copy(); key = (f[..., :3] == bg).all(-1)
            if key.all(): continue
            f[key] = 0; out.append(f)
    return out


def canvas_of(path):
    """the generated canvas: three frames across at 2x"""
    w, h = Image.open(path).size
    for c in (84, 88, 92, 96, 100, 104, 108, 112, 116, 120):
        if w % (c * S) == 0 and w // (c * S) in (3, 4, 5) and h % (c * S + LAB) == 0: return c
    raise SystemExit('ash_sheet: no canvas size fits ' + path)


def bbox(f):
    ys, xs = np.where(f[..., 3] > 0); return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())


def is_skin(px):
    r, g, b, a = (int(v) for v in px)
    return a > 0 and r > 200 and 140 < g < 215 and 110 < b < 190 and r - b > 40


def hand(f, face_x):
    """the frontmost bit of skin below the head: where a weapon goes"""
    x0, y0, x1, y1 = bbox(f); h = y1 - y0
    m = np.array([[is_skin(px) for px in row] for row in f])
    ys, xs = np.where(m)
    ok = ys > y0 + h * 0.28
    if not ok.any(): return [int(face_x + 6), int(y0 + h * 0.45)]
    i = np.argmax(xs[ok]); return [int(xs[ok][i]), int(ys[ok][i])]


def muzzle(f, hx, hy):
    """the end of the barrel: the frontmost dark pixel level with the gun hand (the muzzle flash is bright, so skipped)"""
    best = None
    for y in range(max(0, hy - 6), min(f.shape[0], hy + 4)):
        for x in range(hx, f.shape[1]):
            r, g, b, a = (int(v) for v in f[y, x])
            if a and max(r, g, b) < 120 and (best is None or x > best[0]): best = (x, y)
    return list(best) if best else [hx + 8, hy - 2]


def build(rows_list, pick, src_of, cell, out_png):
    ref = None; sheet = None; rows = {}; fist = {}; strips = {}
    for name in rows_list:
        path = os.path.join(SRC, src_of(name) + '.png')
        canvas = canvas_of(path)
        fr = frames_of(path, canvas)
        if ref is None: ref = bbox(fr[0]); ref_canvas = canvas
        b = bbox(fr[0]); off = (cell - canvas) // 2
        dx = round((ref[0] + ref[2]) / 2 + (cell - ref_canvas) // 2 - (b[0] + b[2]) / 2 - off)
        dy = ref[3] + (cell - ref_canvas) // 2 - b[3] - off
        idx = pick.get(name, list(range(len(fr))))
        strips[name] = [(fr[i], dx + off, dy + off) for i in idx]
    ncol = max(len(v) for v in strips.values())
    sheet = np.zeros((len(rows_list) * cell, ncol * cell, 4), np.uint8)
    ax = round((ref[0] + ref[2]) / 2 + (cell - ref_canvas) // 2 + 0.5, 1); ay = int(ref[3] + 1 + (cell - ref_canvas) // 2); h = int(ref[3] - ref[1] + 1)
    gun = {}
    for ri, name in enumerate(rows_list):
        fist[name] = []
        for k, (f, ox, oy) in enumerate(strips[name]):
            H, Wd = f.shape[:2]
            for y in range(H):
                for x in range(Wd):
                    if f[y, x, 3] == 0: continue
                    tx, ty = x + ox, y + oy
                    if 0 <= tx < cell and 0 <= ty < cell: sheet[ri * cell + ty, k * cell + tx] = f[y, x]
            hx, hy = hand(f, ax - ox)
            fist[name].append([hx + ox, hy + oy])
            if name == 'shoot':
                mx, my = muzzle(f, hx, hy); gun.setdefault('shoot', []).append([mx + ox, my + oy])
        rows[name] = [ri, len(strips[name])]
    Image.fromarray(sheet, 'RGBA').save(out_png, optimize=True)
    meta = {'cell': cell, 'ax': ax, 'ay': ay, 'h': h, 'rows': rows, 'fist': fist}
    if gun: meta['gun'] = gun
    return meta, sheet



seb, _ = build(ROWS, PICK, lambda n: SRC_OF.get(n, n), 88, os.path.join(ROOT, 'web', 'sprites', 'seb.png'))
SEL = os.path.join(SRC, 'select_se.png'); fr = frames_of(SEL, canvas_of(SEL)); cell = seb['cell']
b = bbox(fr[0]); dx = round(seb['ax'] - (b[0] + b[2] + 1) / 2); dy = seb['ay'] - 1 - b[3]
pose = np.zeros((cell, cell * len(fr), 4), np.uint8)
for k, f in enumerate(fr):
    for y in range(f.shape[0]):
        for x in range(f.shape[1]):
            if f[y, x, 3] == 0: continue
            tx, ty = x + dx, y + dy
            if 0 <= tx < cell and 0 <= ty < cell: pose[ty, k * cell + tx] = f[y, x]
Image.fromarray(pose, 'RGBA').save(os.path.join(ROOT, 'web', 'sprites', 'pose_seb.png'), optimize=True)
frames = ("{ jab: { pre: [2, 3], hit: 5, post: [6] }, hook: { pre: [2, 3, 4], hit: 5, post: [6] }, kick: { pre: [2, 3], hit: 4, post: [5, 6] },\n"
          "    tuck: ['jumpkick', 3], air: ['jumpkick', 4], crouch: ['jumpkick', 1], hurt: [1, 2], fall: [1, 2, 3, 4, 5, 6], lie: 9, up: [12, 13, 14, 15, 16],\n"
          "    special: [2, 3, 4, 5, 6, 7, 8],\n"
          "    run: [2, 3, 4, 5, 7, 8], grab: [1, 2, 3, 4], knee: { pre: [2, 3], hit: 4, post: [5] }, throw: { pre: [3, 5], hit: 7, post: [8] },\n"
          "    backkick: { pre: [2, 3], hit: 4, post: [5, 6] }, pickup: [3, 4], swing: { pre: [2, 3, 4], hit: 6, post: [7, 8] } }")
json.dump({'seb': seb, 'frames': frames}, open(os.path.join(HERE, 'seb_meta.json'), 'w'), indent=1)
print('seb sheet', seb['cell'], 'anchor', seb['ax'], seb['ay'], 'height', seb['h'], {k: v[1] for k, v in seb['rows'].items()})
