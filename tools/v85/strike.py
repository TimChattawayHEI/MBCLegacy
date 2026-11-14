import numpy as np
from PIL import Image
KIND = {'jab': 'punch', 'hook': 'punch', 'swing': 'punch', 'kick': 'kick', 'knee': 'knee', 'round': 'kick', 'upper': 'upper'}
def strike(f, kind):
    a = f[..., 3] > 40; ys, xs = np.where(a); top, bot = ys.min(), ys.max(); h = bot - top + 1
    if kind == 'upper':
        y = top; x = xs[ys == top].mean(); return float(x), float(y)
    lo, hi = {'punch': (0.08, 0.6), 'kick': (0.0, 0.93), 'knee': (0.3, 0.8)}[kind]
    m = (ys >= top + lo * h) & (ys <= top + hi * h)
    xs2, ys2 = xs[m], ys[m]; xr = xs2.max()
    sel = xs2 >= xr - 2
    return float(xr), float(ys2[sel].mean())
def world(meta, pt):   # forward, up in world units from the feet
    return [round((pt[0] - meta['ax']) * 2), round((meta['ay'] - pt[1]) * 2)]
def cell(sheet, meta, row, k):
    c = meta['cell']; r = meta['rows'][row][0]
    return sheet[r * c:(r + 1) * c, k * c:(k + 1) * c]
