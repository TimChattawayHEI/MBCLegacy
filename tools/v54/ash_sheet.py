"""Build Ash's sprite sheets: python3 tools/v54/ash_sheet.py

Reads the PixelLab workbench sheets in tools/v54/src/<anim>.png (`inspect character:<id>:east:<anim> --scale 2`:
frames on a grid at 2x, each under an 18px label) and writes
  web/sprites/ash.png         Ash: one row per animation, cell 92 px, frames left to right
  web/sprites/ashn.png        the Ashinator (his special): idle, walk, shoot, cell 96 px
  web/sprites/pose_ash.png    his select-screen pose (south-east), a strip at ash.png's cell size, feet on its anchor
  tools/v54/ash_meta.json     SPRITE_META entries (cell, anchor, height, rows, hand points; the gun muzzle for the
                              Ashinator's shoot row) and LAD_FRAMES entries
Every animation's first frame is the same standing reference, so each animation is lined up on it.

PixelLab: Ash is the "Idle" state 46901346-2812-4d49-8ffb-c6afd8be03d4 of the character "Ash" (88px, pro mode);
the Ashinator is the "Ashinator" state 8518ebde-d77f-4838-8df5-223f42c1d259 of the same character.
"""
import json, os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(HERE, 'src')
S, LAB = 2, 18

# Ash. Row order matches the other lads' sheets. He was a kickboxer as a kid and never throws a punch (Version 54.1):
# the 'jab' row is a quick low kick and the 'hook' row his high roundhouse, so every move that borrows a lad's jab or
# hook (the combo, the dash, the Duck and Cover helpers) is a kick. 'swing' is the old arm thrust, for weapons only.
# PICK reorders or trims a generated animation (frame 0 is always the standing reference).
ASH_ROWS = ['idle', 'walk', 'jab', 'hook', 'kick', 'jumpkick', 'hurt', 'knockdown', 'special', 'run', 'grab', 'knee', 'throw',
            'backkick', 'pickup', 'swing', 'mini']
ASH_PICK = {}
ASH_SRC = {'jab': 'lowkick', 'hook': 'mini', 'swing': 'jab'}
# the Ashinator: the stiff idle (the frames that stay side on), the march, the pistol
ASHN_ROWS = ['idle', 'walk', 'shoot']
ASHN_PICK = {'idle': [0, 1, 2]}   # the later frames turned to face the camera
ASHN_SRC = {'idle': 'n_idle', 'walk': 'n_walk', 'shoot': 'n_shoot'}


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


ash, _ = build(ASH_ROWS, ASH_PICK, lambda n: ASH_SRC.get(n, n), 112, os.path.join(ROOT, 'web', 'sprites', 'ash.png'))
ashn, _ = build(ASHN_ROWS, ASHN_PICK, lambda n: ASHN_SRC[n], 112, os.path.join(ROOT, 'web', 'sprites', 'ashn.png'))

# the select pose: the south-east strip, feet on ash.png's anchor, at its cell size
SEL = os.path.join(SRC, 'select_se.png')
fr = [] if not os.path.exists(SEL) else frames_of(os.path.join(SRC, 'select_se.png'), canvas_of(os.path.join(SRC, 'select_se.png'))); cell = ash['cell']
b = bbox(fr[0]) if fr else (0, 0, 0, 0); dx = round(ash['ax'] - (b[0] + b[2] + 1) / 2); dy = ash['ay'] - 1 - b[3]
pose = np.zeros((cell, cell * max(1, len(fr)), 4), np.uint8)
for k, f in enumerate(fr):
    for y in range(f.shape[0]):
        for x in range(f.shape[1]):
            if f[y, x, 3] == 0: continue
            tx, ty = x + dx, y + dy
            if 0 <= tx < cell and 0 <= ty < cell: pose[ty, k * cell + tx] = f[y, x]
if fr: Image.fromarray(pose, 'RGBA').save(os.path.join(ROOT, 'web', 'sprites', 'pose_ash.png'), optimize=True)

n = {k: v[1] for k, v in ash['rows'].items()}
seq = lambda a, b: ', '.join(str(i) for i in range(a, b))
# hit frames picked by eye from each run (frame 0 is the standing reference)
ash_frames = ("{ jab: { pre: [2, 3], hit: 4, post: [5, 6] }, hook: { pre: [2, 3, 4], hit: 5, post: [6, 7, 8] }, kick: { pre: [1, 2, 3], hit: 4, post: [5, 6] },"
              " tuck: ['jumpkick', 3], air: ['jumpkick', 5], crouch: ['jumpkick', 1], hurt: [2, 3], fall: [3, 4, 5, 6], lie: 8, up: [11, 12, 13, 14, 15, 16],"
              f" special: [{seq(1, n['special'])}], run: [{seq(1, n['run'])}], grab: [1, 2, 3, 4],"
              " knee: { pre: [2, 3], hit: 4, post: [5, 6] }, throw: { pre: [3, 5], hit: 7, post: [8] }, backkick: { pre: [1, 2, 3], hit: 4, post: [5, 6] },"
              f" pickup: [3, 4], swing: {{ pre: [1, 2, 3], hit: 4, post: [5, 6] }}, mini: [{seq(1, n['mini'])}], fallFlip: true }}")
ashn_frames = "{ idle: [0, 1, 2], walk: [1, 2, 3, 4, 5, 6, 7, 8], aim: 5, fire: [6, 7], raise: [2, 3], hurt: [0], fall: [0], lie: 0, up: [0], tuck: ['idle', 0], air: ['idle', 0], crouch: ['idle', 0], jab: { pre: [], hit: 0, post: [] } }"
json.dump({'ash': ash, 'ashn': ashn, 'frames': {'ash': ash_frames, 'ashn': ashn_frames}}, open(os.path.join(HERE, 'ash_meta.json'), 'w'), indent=1)
print('ash sheet', ash['cell'], 'anchor', ash['ax'], ash['ay'], 'height', ash['h'], 'rows', n)
print('ashinator sheet', ashn['cell'], 'anchor', ashn['ax'], ashn['ay'], 'height', ashn['h'], 'muzzle', ashn.get('gun', {}).get('shoot'))
