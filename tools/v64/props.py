"""Version 64: the breakables, painted in Meshy -> web/bg/props/{bin,keg,coolbox,luggage}.png.  python3 tools/v64/props.py

tools/v64/img/props/sheet1.webp is one Meshy picture of the four props in a row on flat magenta. Each is keyed out,
found as the biggest blob in its quarter of the picture, and shrunk to the game's native scale (1 pixel = 2 units),
standing on its bottom edge as the game draws them (drawBinSprite).
"""
import os
import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, 'web', 'bg', 'props')
SIZE = {'bin': ('h', 36), 'keg': ('h', 34), 'coolbox': ('h', 30), 'luggage': ('h', 32)}   # native pixels
im = np.asarray(Image.open(os.path.join(HERE, 'img', 'props', 'sheet1.webp')).convert('RGB')).astype(int)
r, g, b = im[..., 0], im[..., 1], im[..., 2]
fg = ~((r > 150) & (b > 150) & (g < 110) & (np.abs(r - b) < 90))
fg = np.asarray(Image.fromarray((fg * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(5)).filter(ImageFilter.MaxFilter(3))) > 0
H, W = fg.shape
for i, name in enumerate(['bin', 'keg', 'coolbox', 'luggage']):
    x0, x1 = W * i // 4, W * (i + 1) // 4
    m = fg[:, x0:x1]; ys, xs = np.nonzero(m)
    t, bt, l, rt = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    rgb = im[t:bt, x0 + l:x0 + rt].astype(np.float32); a = m[t:bt, l:rt].astype(np.float32)
    # magenta fringe: pull edge colours toward their non-magenta neighbours by clamping red/blue excess over green
    ex = np.minimum(rgb[..., 0], rgb[..., 2]) - rgb[..., 1]; fringe = (ex > 40) & (a > 0)
    rgb[fringe, 0] -= ex[fringe] * 0.6; rgb[fringe, 2] -= ex[fringe] * 0.6
    k, n = SIZE[name]; h, w = a.shape
    s = n / (h if k == 'h' else w); nw, nh = max(1, round(w * s)), max(1, round(h * s))
    pre = np.dstack([rgb * a[..., None], a * 255]).clip(0, 255).astype(np.uint8)
    small = np.asarray(Image.fromarray(pre, 'RGBA').resize((nw, nh), Image.LANCZOS)).astype(np.float32)
    al = small[..., 3:4] / 255; col = np.where(al > 0, small[..., :3] / np.maximum(al, 1e-3), 0)
    out = np.dstack([col, np.where(al[..., 0] > 0.5, 255, 0)]).clip(0, 255).astype(np.uint8)
    Image.fromarray(out, 'RGBA').save(os.path.join(OUT, name + '.png'))
    print(name, (nw, nh))
