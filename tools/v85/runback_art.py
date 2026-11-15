"""Version 85 the run back, art: python3 tools/v85/runback_art.py  (writes web/bg/orp/run_*.png)
- run_street.png: the High Street from Ram Ba Ba (left) to Ye Olde Blacksmith (right), rows 0-201 of a 1160x270 strip.
  The two Meshy paintings (orp/rambaba, orp/front) with the gap between them (the car park wall, the trees, the pub's
  white wing) painted by PixelLab's inpainting (tools/v85/runback_src/win1_done.png); the second moon taken out.
  Built by the steps in strip.png's history; this script only cuts and lights it.
- run_ground.png: a 112x69 tile of the Blacksmiths' pavement, kerb and road (its own row colours, slabs every 14px,
  a few cracks) that repeats, so the ground can scroll at running speed under the street.
- run_bollard.png: the black and white Orpington bollard (IB 798 on Ram Ba Ba's corner), drawn here.
- run_coach.png: the Atlantis coach (PixelLab, in the style of orp/bus)."""
import os
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(HERE, 'runback_src'); OUT = os.path.join(ROOT, 'web', 'bg', 'orp')
A = np.array(Image.open(os.path.join(SRC, 'strip.png')).convert('RGB')).astype(float)
# warm light pools under the two new lamp posts
for lx in (314, 472):
    for y in range(196, 236):
        for x in range(lx - 40, lx + 41):
            d = ((x - lx) / 40) ** 2 + ((y - 214) / 18) ** 2
            if d < 1: A[y, x] = A[y, x] * (1 + 0.45 * (1 - d) ** 1.5) + np.array([30, 18, 0]) * (1 - d)
Image.fromarray(np.clip(A[:202], 0, 255).astype('uint8')).save(os.path.join(OUT, 'run_street.png'))
# ground tile: the pavement rows of the Blacksmiths' side, median colour per row away from the window light
g = A[201:270, 690:1150]; warm = (g[:, :, 0] > 100) & (g[:, :, 0] > g[:, :, 2] + 15)
prof = np.array([np.median(g[y][~warm[y]], axis=0) for y in range(g.shape[0])])
rng = np.random.default_rng(3); TW = 112
T = np.repeat(prof[:, None, :], TW, axis=1)
J = np.array([62, 68, 78])
for ya, yb, off in ((0, 15, 0), (15, 31, 14)):
    for sx in range(0, TW, 28):
        T[ya:yb, (sx + off) % TW:min(TW, (sx + off) % TW + 28)] += rng.uniform(-5, 5)
        T[ya:yb, (sx + off) % TW] = J
    T[ya, :] = J if off else T[ya, :]
for _ in range(1):
    x, y = int(rng.uniform(4, TW - 16)), int(rng.uniform(3, 27))
    for _ in range(10):
        T[y, x] = J * 0.9; x += 1; y = min(28, max(2, y + int(rng.choice([-1, 0, 1]))))
T[51:] += rng.normal(0, 1.6, (T.shape[0] - 51, TW, 1))
Image.fromarray(np.clip(T, 0, 255).astype('uint8')).save(os.path.join(OUT, 'run_ground.png'))
# the bollard, 9x22: black post, white band, rounded top, outline
rows = ['..OOOOO..', '.OKKHKKO.', 'OKKKHKKKO', 'OKKKHKKKO', 'OWWWWWWWO', 'OWWWWWWGO', 'OKKKHKKKO', 'OKKKHKKKO', 'OKKKHKKKO',
        'OKKKHKKKO', 'OKKKHKKKO', 'OKKKHKKKO', 'OKKKHKKKO', 'OKKKHKKKO', 'OKKKHKKKO', 'OKKKHKKKO', 'OKKKHKKKO', 'OKKKHKKKO',
        'OKKKHKKKO', 'OKKKKKKKO', 'OOOOOOOOO', '.OOOOOOO.']
P = {'O': (12, 12, 16, 255), 'K': (36, 38, 46, 255), 'H': (78, 82, 96, 255), 'W': (226, 228, 222, 255), 'G': (170, 172, 168, 255)}
im = Image.new('RGBA', (9, 22), (0, 0, 0, 0)); px = im.load()
for y, r in enumerate(rows):
    for x, c in enumerate(r):
        if c in P: px[x, y] = P[c]
im.save(os.path.join(OUT, 'run_bollard.png'))
c = os.path.join(SRC, 'coach.png')
if os.path.exists(c):
    co = Image.open(c).convert('RGBA'); co.crop(co.getbbox()).save(os.path.join(OUT, 'run_coach.png'))
print('run art written')
