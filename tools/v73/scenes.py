"""Orpington 2001, Version 73: every place is one screen, one Meshy painting. python3 tools/v73/scenes.py

Each painting (tools/v72/img/orp01/*.webp, 1376x768) becomes web/bg/orp/<scene>.png at the game's native 480x270, fitted so
the row where its walls meet the floor ("base") lands on the scene's FT and nothing is squashed: above the base the
picture keeps its own shape (rows are cut off the top, or the top is extended with its own darkened colour if there
isn't enough), below it the floor fills the rest. The bus (a Meshy picture on magenta) is cut out to web/bg/orp/bus.png.
The scenes' FT values are in tools/v73/orp2001.js (ORP_SCENES): keep them in step with SCENES here.
"""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, 'tools', 'v72', 'img', 'orp01'); MINE = os.path.join(HERE, 'img'); OUT = os.path.join(ROOT, 'web', 'bg', 'orp')
os.makedirs(OUT, exist_ok=True)
S = 480 / 1376
# scene: (painting, base row, FT in game units, rows of ceiling to add first)
SCENES = {
    'busstop': ('p0', 580, 380, 0), 'cross': ('cross', 300, 209, 0), 'rambaba': ('p1n', 552, 380, 0), 'front': ('p3n', 592, 380, 0),
    'lounge': ('bi0', 545, 380, 0), 'bar': ('bi1', 545, 380, 0), 'pool': ('bi2', 545, 380, 0),
    'queue': ('at0', 625, 400, 0), 'floor': ('ai1', 385, 380, 160),
}


def load(name):
    for d in (MINE, SRC):
        p = os.path.join(d, name + '.webp')
        if os.path.exists(p): return Image.open(p).convert('RGB')
    raise SystemExit('missing ' + name)


def fit(im, base, ft, pad):
    a = np.asarray(im).astype(np.float32)
    if pad:   # more room above the floor: the top rows' own colour, darkened, and the black band under the club's floor dropped
        a = a[:648]; a = np.concatenate([np.repeat(np.median(a[:6], 0)[None] * 0.55, pad, 0), a], 0); base += pad
    need = round(ft / 2 / S)                        # source rows that fill the screen above FT at the picture's own scale
    top = base - need
    if top < 0: a = np.concatenate([np.repeat(np.median(a[:6], 0)[None] * 0.8, -top, 0), a], 0); base -= top; top = 0
    pic = Image.fromarray(a.clip(0, 255).astype(np.uint8))
    up = pic.crop((0, top, pic.width, base)).resize((480, ft // 2), Image.LANCZOS)
    dn = pic.crop((0, base, pic.width, min(pic.height, base + round((270 - ft // 2) / S)))).resize((480, 270 - ft // 2), Image.LANCZOS)
    out = Image.new('RGB', (480, 270)); out.paste(up, (0, 0)); out.paste(dn, (0, ft // 2)); return out


def bus():
    im = np.asarray(load('bus')).astype(int); r, g_, bl = im[..., 0], im[..., 1], im[..., 2]
    key = (r > 140) & (bl > 140) & (r - g_ > 70) & (bl - g_ > 70)   # magenta and the pinkish fringe round the edges
    ys, xs = np.where(~key); y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    rgba = np.dstack([im, np.where(key, 0, 255)]).astype(np.uint8)[y0:y1, x0:x1]
    b = Image.fromarray(rgba, 'RGBA'); w = 230; b = b.resize((w, round(b.height * w / b.width)), Image.LANCZOS)
    a = np.asarray(b).copy(); a[..., 3] = np.where(a[..., 3] > 200, 255, 0)
    pink = (a[..., 0].astype(int) - a[..., 1] > 90) & (a[..., 2].astype(int) - a[..., 1] > 60); a[..., 3][pink] = 0   # no magenta left in the edge
    Image.fromarray(a).save(os.path.join(OUT, 'bus.png'), optimize=True); print('bus', b.size)


if __name__ == '__main__':
    for k, (name, base, ft, pad) in SCENES.items():
        fit(load(name), base, ft, pad).save(os.path.join(OUT, k + '.png'), optimize=True); print(k, 'ft', ft)
    bus()
