"""Stitch the Orpington 2001 High Street strip from the Meshy panels: python3 tools/v72/orp_strip.py <panel dir> <out.png> [x0:x1:y1,...]

Panels are pasted in order at their raw x (later ones on top), then the ground repaint g1 is laid over with feathered
sides, then the sky is eased across two panel joins (SHIFTS), and boxes given as x0:x1:y1 (extra moons) are filled with a
blend of the sky either side."""
import sys
import numpy as np
from PIL import Image
P, OUT = sys.argv[1], sys.argv[2]
ITEMS = [('p0', 0), ('p1n', 1032), ('b6', 512), ('p3n', 2877), ('b3', 2209), ('b7', 1642), ('b8', 1912), ('p4', 3909), ('b4', 3565)]
W = 3909 + 1376
def load(n):
    for ext in ('_raw.png', '.webp'):
        try: return Image.open(f'{P}/{n}{ext}').convert('RGB')
        except FileNotFoundError: pass
    raise SystemExit('missing ' + n)
im = Image.new('RGB', (W, 768))
for n, x in ITEMS: im.paste(load(n), (x, 0))
a = np.asarray(im).astype(float)
# ground repaint over Ram Ba Ba to the Blacksmiths, feathered 60 px each side
g = np.asarray(load('g1')).astype(float); gx = 1812; f = 60
w = np.ones(1376); w[:f] = np.linspace(0, 1, f); w[-f:] = np.linspace(1, 0, f)
a[:, gx:gx + 1376] = a[:, gx:gx + 1376] * (1 - w[None, :, None]) + g * w[None, :, None]
# sky joins: from a cut at x c, shift the sky on its right (pixels close to that side's sky colour, stars left alone) onto the
# left side's sky colours, easing back to its own colours by x e. Sky colours per row are medians over 40 px beside the cut.
SHIFTS = [(2715, 3700, 300), (3015, 3700, 300)]   # (cut x, ease end x, rows)
for c, e, rows in SHIFTS:
    L = np.median(a[:rows, c - 44:c - 4], 1); R = np.median(a[:rows, c + 4:c + 44], 1)
    for x in range(c, e):
        t = (x - c) / (e - c); col = a[:rows, x]
        sky = (np.abs(col - R).sum(1) < 45) & (col.sum(1) < 420)
        a[:rows, x][sky] = col[sky] + ((L - R) * (1 - t))[sky]
# sky: fill boxes (moons, a sky join) with a blend of the sky colours just left and right of each box, then a few stars
FILLS = [tuple(map(int, b.split(':'))) for b in (sys.argv[3].split(',') if len(sys.argv) > 3 else [])]   # x0:x1:y1
rng = np.random.default_rng(7)
for xa, xb, y1 in FILLS:
    L = np.median(a[:y1, xa - 16:xa], 1)[:, None]; R = np.median(a[:y1, xb:xb + 16], 1)[:, None]
    t = np.linspace(0, 1, xb - xa)[None, :, None]; a[:y1, xa:xb] = L * (1 - t) + R * t
    for _ in range((xb - xa) * y1 // 4000):
        x = rng.integers(xa + 3, xb - 3); y = rng.integers(3, max(4, y1 - 20)); a[y:y + 2, x:x + 2] = [200, 210, 235]
Image.fromarray(a.clip(0, 255).astype('uint8')).save(OUT)
print('saved', OUT, W)
