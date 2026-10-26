"""Version 63 art: the trophy cabinet in the Harvest Moon.  python3 tools/v63/trophy_art.py

tools/v63/img/cab_canvas.png is PixelLab's empty open-fronted cabinet (Create Image Pro, padded to 64x128) and
cab_full.png the same picture with the shelves inpainted full of trophies (cab_mask.png, the four shelf interiors).
The inpaint also nudged the shelf planks, so the empty cabinet the game draws is the full one with just the four rows
of trophies swapped back for the empty picture. Each shelf is cut into four slots at the quietest columns, and each
trophy is the full picture's pixels that differ from the empty one inside its slot. 16 trophies, top shelf first, left
to right; the game shows a share of them matching the share of trophies you've won.
Writes web/bg/pub/trophy_cab.png, web/bg/pub/trophy_items.png (the trophies side by side) and
tools/v63/trophy_items.json ([sheet x, sheet y, w, h, x and y in the cabinet] for each, and the cabinet's size).
"""
import json, os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, 'web', 'bg', 'pub')
E = np.array(Image.open(os.path.join(HERE, 'img', 'cab_canvas.png')).convert('RGBA')).astype(int)
F = np.array(Image.open(os.path.join(HERE, 'img', 'cab_full.png')).convert('RGBA')).astype(int)
d = np.abs(F[..., :3] - E[..., :3]).sum(-1)
BANDS = [(31, 42), (51, 62), (71, 81), (89, 99)]   # the rows the trophies stand in, above each plank
X0, X1 = 17, 47                                    # the cabinet's inside
base = F.copy()
for y0, y1 in BANDS: base[y0:y1 + 1, X0:X1 + 1] = E[y0:y1 + 1, X0:X1 + 1]
ys, xs = np.nonzero(base[..., 3] > 0); bx0, by0, bx1, by1 = xs.min(), ys.min(), xs.max(), ys.max()
items = []
for y0, y1 in BANDS:
    col = (d[y0:y1 + 1] > 90).sum(0)
    cuts = [X0] + [min(range(int(c) - 3, int(c) + 4), key=lambda x: (col[x], abs(x - c))) for c in (24.5, 32, 39.5)] + [X1 + 1]
    for i in range(4):
        a, b = cuts[i], cuts[i + 1]
        mk = np.zeros(d.shape, bool); mk[y0:y1 + 1, a:b] = d[y0:y1 + 1, a:b] > 40
        yy, xx = np.nonzero(mk); items.append((xx.min(), yy.min(), xx.max(), yy.max(), mk))
sw = sum(i[2] - i[0] + 1 for i in items); sh = max(i[3] - i[1] + 1 for i in items)
sheet = np.zeros((sh, sw, 4), np.uint8); meta = []; ox = 0
for (x0, y0, x1, y1, mk) in items:
    sub = np.where(mk[y0:y1 + 1, x0:x1 + 1, None], F[y0:y1 + 1, x0:x1 + 1], 0)
    sheet[:y1 - y0 + 1, ox:ox + x1 - x0 + 1] = sub
    meta.append([int(ox), 0, int(x1 - x0 + 1), int(y1 - y0 + 1), int(x0 - bx0), int(y0 - by0)]); ox += x1 - x0 + 1
Image.fromarray(base[by0:by1 + 1, bx0:bx1 + 1].astype(np.uint8)).save(os.path.join(OUT, 'trophy_cab.png'))
Image.fromarray(sheet).save(os.path.join(OUT, 'trophy_items.png'))
json.dump({'items': meta, 'w': int(bx1 - bx0 + 1), 'h': int(by1 - by0 + 1)}, open(os.path.join(HERE, 'trophy_items.json'), 'w'))
print('trophy cabinet', bx1 - bx0 + 1, 'x', by1 - by0 + 1, ',', len(meta), 'trophies')
