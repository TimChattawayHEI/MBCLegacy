"""Version 55 art: python3 tools/v55/art.py

Builds web/bg/pub/ from the PixelLab images in tools/v55/img/ and the workbench animation sheets in tools/v55/src/
(`pixelart_workbench inspect character:<id>:<dir>:<anim> --scale 2`, cut with tools/v53/foe_sheets.frames_of).

- Plain images are copied: the arcade cabinet, chalkboard, fruit machine face, reel symbols, penalty pitch, energy can.
- Animations become strips (frames left to right, one cell each) with their cell size, frame count and foot anchor in
  tools/v55/strips.json, which v55_build.py writes into the page as PUB_STRIPS.
- The dartboard is drawn here, pixel by pixel, from a real board's ring sizes, because the game scores darts from the
  same geometry (PixelLab can't be trusted to put twenty segments in the right places). Same for the tiny dart,
  golf ball and tee.
"""
import json, math, os, shutil, sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, 'web', 'bg', 'pub')
sys.path.insert(0, os.path.join(ROOT, 'tools', 'v53'))
from foe_sheets import frames_of  # noqa: E402

os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- plain images
for n in ['cabinet', 'fruitface', 'pitch', 'can', 'sym_cherry', 'sym_lemon', 'sym_bell', 'sym_bar', 'sym_seven', 'sym_grapes'] + ['tornado', 'tornado2']:
    shutil.copy(os.path.join(HERE, 'img', n + '.png'), os.path.join(OUT, n + '.png'))


# ---------------------------------------------------------------- animation strips
def drop_red_blobs(f):
    """the kick came with a ball of its own: drop loose reddish blobs (the game draws the real ball)"""
    a = f[..., 3] > 0; h, w = a.shape; lab = np.zeros((h, w), int); n = 0; comps = []
    for y in range(h):
        for x in range(w):
            if a[y, x] and not lab[y, x]:
                n += 1; st = [(y, x)]; lab[y, x] = n; pts = []
                while st:
                    cy, cx = st.pop(); pts.append((cy, cx))
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            ny, nx = cy + dy, cx + dx
                            if 0 <= ny < h and 0 <= nx < w and a[ny, nx] and not lab[ny, nx]:
                                lab[ny, nx] = n; st.append((ny, nx))
                comps.append(pts)
    if len(comps) < 2: return f
    comps.sort(key=len, reverse=True)
    for pts in comps[1:]:
        cols = np.array([f[y, x, :3] for y, x in pts], float); r, g, b = cols.mean(0)
        if len(pts) < 160 and r > g + 25 and r > b + 25:
            for y, x in pts: f[y, x] = 0
    return f


def strip(name, src, pick=None, fix=None):
    fr, cell = frames_of(os.path.join(HERE, 'src', src + '.png'))
    if pick: fr = [fr[i] for i in pick]
    if fix: fr = [fix(f.copy()) for f in fr]
    im = Image.new('RGBA', (cell * len(fr), cell), (0, 0, 0, 0))
    for i, f in enumerate(fr): im.paste(Image.fromarray(f), (i * cell, 0))
    im.save(os.path.join(OUT, name + '.png'))
    a = fr[0][..., 3] > 0; ys, xs = np.nonzero(a)
    foot = ys.max(); fx = xs[ys >= foot - 2]
    return {'cell': cell, 'n': len(fr), 'ax': int(round((fx.min() + fx.max()) / 2)), 'ay': int(foot) + 1}


strips = {}
# The Parkie in goal: ready (his first two frames, still holding the rake), then the dive to his left (mirrored for the right)
strips['keeper_ready'] = strip('keeper_ready', 'keeper_ready', pick=[0, 1])
strips['keeper_dive'] = strip('keeper_dive', 'keeper_dive', pick=list(range(1, 11)))
# Byron from behind: stance, run-up, strike, follow-through
strips['byron_kick'] = strip('byron_kick', 'byron_kick', fix=drop_red_blobs)
if os.path.exists(os.path.join(HERE, 'src', 'pearcy_golf.png')):
    # pixminimax take 3: address (F3), backswing (F10-F14), impact (F15), finish (F16-F17)
    strips['pearcy_golf'] = strip('pearcy_golf', 'pearcy_golf', pick=[2, 9, 10, 11, 12, 13, 14, 15, 16])
# the chalkboard: PixelLab's slate (img/slate.png) in a wooden frame drawn here, and where the slate is, so the scores
# can be written inside it
sl = Image.open(os.path.join(HERE, 'img', 'slate.png')).convert('RGBA'); sl = sl.crop(sl.getbbox())
_a = np.array(sl).astype(int); _d = (_a[..., 3] > 200) & (_a[..., :3].max(-1) < 90)
_r = [y for y in range(_d.shape[0]) if _d[y].mean() > 0.6]; _c = [x for x in range(_d.shape[1]) if _d[:, x].mean() > 0.6]
sl = sl.crop((min(_c), min(_r), max(_c) + 1, max(_r) + 1))   # just the dark slate, not its pale border
F = 5; cw, chh = sl.width + F * 2, sl.height + F * 2
fr = np.zeros((chh, cw, 4), np.uint8)
OUTL, MID, HI, LO = (22, 16, 12), (110, 70, 40), (146, 98, 56), (70, 42, 24)
for y in range(chh):
    for x in range(cw):
        e = min(x, y, cw - 1 - x, chh - 1 - y)
        if e == 0: col = OUTL
        elif e < F: col = HI if (x < F and y < chh - F) or (y < F and x < cw - F) else LO if (x >= cw - F or y >= chh - F) else MID
        else: continue
        if 0 < e < F and (x * 7 + y * 3) % 11 == 0: col = tuple(max(0, c - 18) for c in col)   # a bit of grain
        fr[y, x] = (*col, 255)
board = Image.fromarray(fr); board.alpha_composite(sl, (F, F))
board.save(os.path.join(OUT, 'chalk.png'))
strips['chalk_slate'] = [F + 2, F + 2, cw - F - 2, chh - F - 6]
json.dump(strips, open(os.path.join(HERE, 'strips.json'), 'w'), indent=1)


# ---------------------------------------------------------------- the dartboard, from a real board's sizes
# ring radii in board pixels (double outer 76px = 170mm); keep these in step with DART_R in pub.js
R = {'bull': 3, 'obull': 7, 'tin': 44, 'tout': 48, 'din': 72, 'dout': 76, 'rim': 92}
ORDER = [20, 1, 18, 4, 13, 6, 10, 15, 2, 17, 3, 19, 7, 16, 8, 11, 14, 9, 12, 5]
SZ = R['rim'] * 2 + 2; C = SZ / 2
BLACK, CREAM, RED, GREEN = (26, 24, 22), (232, 218, 182), (196, 46, 40), (36, 128, 58)
RIM, RIM2, WIRE = (18, 16, 16), (44, 40, 38), (150, 150, 146)
img = np.zeros((SZ, SZ, 4), np.uint8)
for y in range(SZ):
    for x in range(SZ):
        dx, dy = x + 0.5 - C, y + 0.5 - C; r = math.hypot(dx, dy)
        if r > R['rim']: continue
        a = (math.degrees(math.atan2(dx, -dy)) + 360 + 9) % 360; seg = int(a // 18); dark = seg % 2 == 0
        if r <= R['bull']: col = RED
        elif r <= R['obull']: col = GREEN
        elif r <= R['tin']: col = BLACK if dark else CREAM
        elif r <= R['tout']: col = RED if dark else GREEN
        elif r <= R['din']: col = BLACK if dark else CREAM
        elif r <= R['dout']: col = RED if dark else GREEN
        else: col = RIM2 if r > R['rim'] - 2 else RIM
        img[y, x] = (*col, 255)
# thin silver wires round the rings and along the spider, every other pixel so it reads as wire, not paint
for y in range(SZ):
    for x in range(SZ):
        dx, dy = x + 0.5 - C, y + 0.5 - C; r = math.hypot(dx, dy)
        if r > R['dout'] + 0.5 or r < R['obull'] - 0.5: continue
        on_ring = any(abs(r - R[k]) < 0.5 for k in ('obull', 'tin', 'tout', 'din', 'dout'))
        a = (math.degrees(math.atan2(dx, -dy)) + 360 + 9) % 18
        on_spoke = r > R['obull'] and min(a, 18 - a) * math.pi / 180 * r < 0.5
        if (on_ring or on_spoke) and (x + y) % 2 == 0: img[y, x, :3] = WIRE
Image.fromarray(img).save(os.path.join(OUT, 'dartboard.png'))

# ---------------------------------------------------------------- small bits
def sprite(rows, pal, name):
    h = len(rows); w = max(len(r) for r in rows); im = np.zeros((h, w, 4), np.uint8)
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch != '.': im[y, x] = (*pal[ch], 255)
    Image.fromarray(im).save(os.path.join(OUT, name + '.png'))

# a dart stuck in the board, seen nearly head on: the flight fanned out above the point
sprite(['.k.k.k.',
        'krkrkrk',
        '.krrrk.',
        '..kgk..',
        '..kgk..',
        '...k...'],
       {'k': (16, 14, 14), 'r': (220, 60, 40), 'g': (190, 190, 186)}, 'dart')
# the dart in the hand, flying away from you: a long barrel and a flight
sprite(['......kk',
        '.....krk',
        'kkkkkkrk',
        'kggggkkk',
        'kkkkkk..'],
       {'k': (16, 14, 14), 'r': (220, 60, 40), 'g': (190, 190, 186)}, 'dart_fly')
sprite(['.kk.', 'kwwk', 'kwsk', '.kk.'], {'k': (20, 20, 20), 'w': (246, 246, 240), 's': (190, 190, 184)}, 'golfball')
sprite(['kwwwk', '.kwk.', '.kwk.', '.kwk.', '.kwk.'], {'k': (20, 20, 20), 'w': (232, 208, 160)}, 'tee')
print('v55 art:', ', '.join(sorted(os.listdir(OUT))))
