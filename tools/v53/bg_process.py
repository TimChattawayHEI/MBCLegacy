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
import pxfont, seams

ROOT = os.path.dirname(os.path.dirname(HERE)); IMG = os.path.join(HERE, 'img')
OUT = os.path.join(ROOT, 'web', 'bg', 'nightlife')

# image: list of (x0, y0, x1, y1, lines) rectangles to repaint (inclusive, native pixels)
SIGNS = {
    'st_front': [(135, 39, 187, 44, ['ORPINGTON'])],
    'st_hall': [(1, 38, 24, 49, ['TICKET', 'OFFICE']), (130, 39, 238, 50, ['TICKET HALL'])],
    'cx_hall': [(2, 72, 63, 84, ['ORPINGTON 2345', 'SEVENOAKS 2350']), (70, 72, 123, 84, ['HAYES 2348', 'DARTFORD 2352']),
                (138, 72, 179, 84, ['CANCELLED', 'DELAYED']), (186, 72, 248, 84, ['GROVE PARK 0003', 'BROMLEY S 2358']),
                (251, 72, 314, 84, ['ASHFORD 0020', 'GILLINGHAM 0015'])],
    'sc_highst': [(59, 29, 114, 38, ['KEBABS']), (181, 30, 247, 37, ['PHONES UNLOCKED']), (257, 32, 308, 38, ['OFF LICENCE']),
                  (317, 30, 363, 37, ['BOOKMAKER'])],
    'st_hall2': [(72, 36, 216, 42, ['TRAINS TO LONDON CHARING CROSS']), (64, 58, 84, 61, ['']), (143, 58, 162, 61, ['']),
                 (172, 58, 191, 61, ['']), (201, 58, 220, 61, [''])],
    'cx_platform': [(0, 77, 25, 83, ['PLAT 4'])],
    'cx_shops': [(0, 79, 41, 84, ['NEWS']), (143, 80, 178, 84, ['TOILETS']), (188, 80, 251, 84, ['SANDWICHES'])],
    'alley2': [(219, 63, 296, 70, ['FIRE EXIT'])],
    'tr_wall': [(20, 11, 139, 17, ['PLEASE OFFER YOUR SEAT']), (182, 11, 302, 17, ['NO SMOKING ON THIS TRAIN'])],
}
# image: boxes to paint out with the sky beside them (a moon that would repeat every tile of a scrolling strip)
ERASE = {'sc_suburb': [(190, 6, 218, 32)], 'bus_deck': [(211, 50, 220, 58)]}
# image: rectangles to make see-through (windows), or a glass colour: every blob of it (bigger than a few
# dozen pixels) becomes tinted glass, alpha GLASS, so the scenery drawn behind shows through
# image: (glass colour, tolerance, top row, bottom row, biggest speck to glass over)
WINDOWS = {'tr_wall': ((10, 12, 20), 10, 20, 90, 24), 'bus_deck': ((8, 23, 57), 26, 12, 112, 80)}
GLASS = 60
UNUSED = {'kebab', 'alarm', 'window_hammer', 'cx_barrier'}   # made for the brief, not needed in the end (the game has its own kebab; the gateline uses gate.png)
POLE_CUT = 41   # seat_pole rows kept for the weapon: the pole and the top of the red seat back
DOORWAY = (3, 31, 60, 124)   # tr_door: where the leaves sit in the frame
# Backgrounds that sit on the walkway: keep only the rows above this (the generator ends most of them in a dark band that
# reads as a platform edge or a kerb right behind the fight), then pad the top with sky so a stage's pieces share a height.
CROP = {'st_front': 124, 'st_hall': 134, 'st_hall2': 134, 'st_platform': 105, 'cx_platform': 136, 'cx_hall': 133, 'cx_shops': 145, 'cx_exit': 138,
        'alley': 150, 'alley2': 150, 'alley3': 148}
# rows taken off the top of a whole stage's row (pieces and joins), where padding would show as a flat band under a roof
TOPCUT = {'cx_platform': 12, 'cx_hall': 12, 'cx_shops': 12, 'cx_exit': 12, 'cx_j1': 12, 'cx_j2': 12, 'cx_j3': 12}
PAD = {'st_front': 134, 'st_platform': 134, 'cx_platform': 145, 'cx_hall': 145, 'cx_exit': 145, 'alley3': 150}


def cut_glass(px, col, tol=10, min_area=60, y0=0, y1=None, speck=24):
    near = (np.abs(px[..., :3].astype(int) - np.array(col)).sum(-1) <= tol) & (px[..., 3] > 0)
    rows = np.zeros(near.shape, bool); rows[y0:(y1 or near.shape[0]) + 1] = True; near &= rows
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
    # stars and moons painted on the glass would sit still while the scenery scrolls: glass them too
    from scipy import ndimage
    solid = px[..., 3] != GLASS; lab, n = ndimage.label(solid)
    sizes = ndimage.sum(solid, lab, range(1, n + 1))
    for k, sz in enumerate(sizes, 1):
        if sz < speck:
            m = lab == k; ys, xs = np.where(m)
            if ys.min() > 0 and xs.min() > 0 and ys.max() < h - 1 and xs.max() < w - 1:
                px[m] = list(col) + [GLASS]


def repaint(px, x0, y0, x1, y1, lines):
    box = px[y0:y1 + 1, x0:x1 + 1]
    cols = Counter(tuple(c) for c in box.reshape(-1, 4))
    (bg, _), *rest = cols.most_common()
    # the text colour: the most common colour that stands out from the plate
    lum = lambda c: 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]
    fg = next((c for c, _ in rest if abs(lum(c) - lum(bg)) > 70), (255, 255, 255, 255))
    box[:] = bg
    w, h = x1 - x0 + 1, y1 - y0 + 1
    s = 2 if all(pxfont.width(l, 2) <= w - 2 for l in lines) and len(lines) * 12 <= h else 1
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
    if win and isinstance(win[0], tuple): cut_glass(px, win[0], win[1], 60, win[2], win[3], win[4])
    elif win:
        for x0, y0, x1, y1 in win: px[y0:y1 + 1, x0:x1 + 1, 3] = 0
    if name in seams.SEAMS: px = seams.paste_edges(name, px)   # a join: its ends are the neighbours' exact pixels
    if name in CROP: px = px[:CROP[name]]
    if name in PAD and PAD[name] > px.shape[0]:
        row = px[0].reshape(-1, 4); sky = Counter(tuple(c) for c in row).most_common(1)[0][0]
        top = np.zeros((PAD[name] - px.shape[0], px.shape[1], 4), np.uint8); top[:] = sky
        px = np.concatenate([top, px], 0)
    os.makedirs(OUT, exist_ok=True)
    if name in UNUSED: return False
    if name in TOPCUT: px = px[TOPCUT[name]:]
    if name == 'luggage':
        Image.fromarray(px, 'RGBA').save(os.path.join(ROOT, 'web', 'bg', 'props', 'luggage.png'), optimize=True); return True
    if name == 'seat_pole':
        # the breakable pole on the bus, and the weapon it leaves: the pole and its stop button, laid flat, held by the button
        Image.fromarray(px, 'RGBA').save(os.path.join(ROOT, 'web', 'bg', 'props', 'pole.png'), optimize=True)
        w = px[:POLE_CUT].copy(); w[34:, :5] = 0; w[34:, 13:] = 0   # a narrow red grip, not the whole seat back
        im = Image.fromarray(w, 'RGBA').rotate(-90, expand=True); im = im.crop(im.getbbox())
        im.save(os.path.join(ROOT, 'web', 'bg', 'weapons', 'pole.png'), optimize=True); return True
    if name == 'gate':
        # one ticket gate cabinet, side-on: the gateline is a column of these across the walkway. Green light open, red shut.
        im = Image.fromarray(px, 'RGBA'); im = im.crop(im.getbbox()); a = np.array(im)
        Image.fromarray(a, 'RGBA').save(os.path.join(OUT, 'gate_open.png'), optimize=True)
        g = (a[..., 1].astype(int) > a[..., 0].astype(int) + 40) & (a[..., 1].astype(int) > a[..., 2].astype(int) + 30) & (a[..., 3] > 0)
        a[g] = (232, 58, 50, 255)
        Image.fromarray(a, 'RGBA').save(os.path.join(OUT, 'gate_shut.png'), optimize=True)
        return True
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
    names.sort(key=lambda n: n in seams.SEAMS)   # the joins last: they take their ends from the finished pieces
    for n in names: print(n, 'ok' if process(n) else 'skipped')
