"""Nightlife 2006 backgrounds and props: python3 tools/v53/bg_process.py

Takes the PixelLab images in tools/v53/img and writes the game's copies into web/bg/nightlife/ (and the few props
into web/bg/props, web/bg/weapons). Signs the generator garbled are repainted with real names in a 3x5 pixel font,
and the train and bus windows are cut out so the scenery strip shows through them.
"""
import os, sys
from collections import Counter
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import pxfont

ROOT = os.path.dirname(os.path.dirname(HERE)); IMG = os.path.join(HERE, 'img')
OUT = os.path.join(ROOT, 'web', 'bg', 'nightlife')

# image: list of (x0, y0, x1, y1, lines) rectangles to repaint (inclusive, native pixels)
SIGNS = {
    'st_front': [(135, 39, 187, 44, ['ORPINGTON'])],
    'st_hall': [(1, 38, 24, 49, ['TICKET', 'OFFICE']), (130, 39, 238, 50, ['TICKET HALL'])],
    'tr_wall': [(20, 11, 139, 17, ['PLEASE OFFER YOUR SEAT']), (182, 11, 302, 17, ['NO SMOKING ON THIS TRAIN'])],
}
# image: boxes to paint out with the sky beside them (a moon that would repeat every tile of a scrolling strip)
ERASE = {'sc_suburb': [(190, 6, 218, 32)]}
# image: rectangles to make see-through (windows), or a glass colour: every blob of it (bigger than a few
# dozen pixels) becomes tinted glass, alpha GLASS, so the scenery drawn behind shows through
WINDOWS = {'tr_wall': (10, 12, 20)}
GLASS = 60
DOORWAY = (3, 31, 60, 124)   # tr_door: where the leaves sit in the frame


def cut_glass(px, col, tol=10, min_area=60):
    near = (np.abs(px[..., :3].astype(int) - np.array(col)).sum(-1) <= tol) & (px[..., 3] > 0)
    h, w = near.shape; seen = np.zeros_like(near)
    for y in range(h):
        for x in range(w):
            if near[y, x] and not seen[y, x]:
                st = [(y, x)]; seen[y, x] = True; pts = []
                while st:
                    cy, cx = st.pop(); pts.append((cy, cx))
                    for yy, xx in ((cy + 1, cx), (cy - 1, cx), (cy, cx + 1), (cy, cx - 1)):
                        if 0 <= yy < h and 0 <= xx < w and near[yy, xx] and not seen[yy, xx]: seen[yy, xx] = True; st.append((yy, xx))
                if len(pts) >= min_area:
                    ys, xs = zip(*pts); px[list(ys), list(xs), 3] = GLASS


def repaint(px, x0, y0, x1, y1, lines):
    box = px[y0:y1 + 1, x0:x1 + 1]
    cols = Counter(tuple(c) for c in box.reshape(-1, 4))
    (bg, _), *rest = cols.most_common()
    # the text colour: the most common colour that stands out from the plate
    lum = lambda c: 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]
    fg = next((c for c, _ in rest if abs(lum(c) - lum(bg)) > 70), (255, 255, 255, 255))
    box[:] = bg
    w, h = x1 - x0 + 1, y1 - y0 + 1
    s = 2 if all(pxfont.width(l, 2) <= w - 2 for l in lines) and len(lines) * 12 - 2 <= h else 1
    th = len(lines) * (5 * s + s + 1) - (s + 1)
    y = y0 + (h - th) // 2
    for l in lines:
        pxfont.draw(px, x0 + (w - pxfont.width(l, s)) // 2, y, l, fg, s); y += 5 * s + s + 1


def process(name):
    p = os.path.join(IMG, name + '.png')
    if not os.path.exists(p): return False
    px = np.array(Image.open(p).convert('RGBA'))
    for r in SIGNS.get(name, []): repaint(px, *r)
    for x0, y0, x1, y1 in ERASE.get(name, []):
        # paint the sky over it, row by row, from just left of the box (the sky is in flat bands)
        px[y0:y1 + 1, x0:x1 + 1] = px[y0:y1 + 1, x0 - 3:x0 - 2]
    win = WINDOWS.get(name)
    if win and isinstance(win[0], int): cut_glass(px, win)
    elif win:
        for x0, y0, x1, y1 in win: px[y0:y1 + 1, x0:x1 + 1, 3] = 0
    os.makedirs(OUT, exist_ok=True)
    if name == 'tr_door':
        # the frame with an empty doorway, and the two leaves on their own so the game can slide them apart
        x0, y0, x1, y1 = DOORWAY
        leaves = px[y0:y1 + 1, x0:x1 + 1].copy()
        for gx0, gy0, gx1, gy1 in ((6, 13, 21, 52), (36, 13, 51, 52)):
            g = leaves[gy0:gy1 + 1, gx0:gx1 + 1]; dark = g[..., :3].astype(int).sum(-1) < 120; g[dark, 3] = GLASS
        frame = px.copy(); frame[y0:y1 + 1, x0:x1 + 1, 3] = 0
        Image.fromarray(leaves, 'RGBA').save(os.path.join(OUT, 'tr_door.png'), optimize=True)
        Image.fromarray(frame, 'RGBA').save(os.path.join(OUT, 'tr_doorframe.png'), optimize=True)
        return True
    Image.fromarray(px, 'RGBA').save(os.path.join(OUT, name + '.png'), optimize=True)
    return True


if __name__ == '__main__':
    names = sys.argv[1:] or sorted(f[:-4] for f in os.listdir(IMG) if f.endswith('.png'))
    for n in names: print(n, 'ok' if process(n) else 'missing')
