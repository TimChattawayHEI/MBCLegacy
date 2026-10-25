"""Version 60 floors: python3 tools/v60/floors.py

Each stage's floor was painted by PixelLab's inpainting, straight down from that stage's own backdrop: a 256x256 crop of
the game's 480x270 picture (rows 14 to 270, so the floor top FT/2 sits at row FT/2 - 14), with everything from the floor
top down masked and repainted. tools/v60/img/<name>.png are those results, untouched.

This cuts the floor rows out and makes them repeat with no join: it finds the repeat width whose start matches what comes
after it best, then dissolves the first 32 columns from the overrun into the start with an ordered dither, so the pixels
stay crisp. The game draws them at 2x from FT to the bottom of the screen, anchored to the world, so they scroll
(floorTex in tools/v60/floor.js). Output: web/bg/floors/<name>.png.
"""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, 'web', 'bg', 'floors')
os.makedirs(OUT, exist_ok=True)

# name: the row in the 256 crop where the floor starts (FT / 2 - 14)
TOP = {
    'freq_pave': 158, 'freq_under': 158, 'freq_park': 158,
    'sz_carpet': 160, 'sz_corr': 160, 'sz_roof': 160,
    'air_apron': 158, 'air_rank': 158,
    'bar_in': 158, 'bar_out': 158, 'club_out': 161,
    'st_hall': 162, 'st_plat': 162, 'cx': 164, 'alley': 164,
    'carpark': 156, 'bank': 156, 'peg': 156, 'ram': 159,
}
# fix-ups, by name: cols = only these columns of the crop (a parked taxi sat in the rest; the corridor's checker only
# runs straight near its middle), top = the first rows come from just below (wheels and shadows of what stood at the
# back), p = the range of repeat widths to try, b = columns dissolved across the join
FIX = {
    'air_rank': {'cols': (0, 100), 'p': (60, 84), 'b': 16},
    'carpark': {'top': 9},
    'air_apron': {'top': 7},
    'sz_corr': {'checker': (134.3, -0.137, 16.8, 0.215, 24)},
}


def checker(t, c0, ck, w0, k, sq):
    """the corridor's lino was painted in perspective, its lines fanning out from the middle, which can't repeat; this
    lays it straight: squares sq wide, each filled from the square either side of the middle line on that row (one
    light, one dark), so the scuffs and the row heights are PixelLab's"""
    h = t.shape[0]; out = np.zeros((h, sq * 2, 3), int)
    for y in range(h):
        wr, cx = w0 + k * y, c0 + ck * y   # the middle line drifts a little and the squares widen down the floor
        for x in range(sq * 2):
            u = (x % sq + 0.5) / sq
            sx = cx + u * wr if x < sq else cx - wr + u * wr
            out[y, x] = t[y, min(255, int(sx))]
    return out
B = 32   # columns dissolved across the join
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16 + 1 / 32


def tile(name, top):
    f = FIX.get(name, {})
    t = np.array(Image.open(os.path.join(HERE, 'img', name + '.png')).convert('RGB')).astype(int)[top:]
    if 'checker' in f:
        out = checker(t, *f['checker'])
        Image.fromarray(out.astype(np.uint8)).save(os.path.join(OUT, name + '.png'))
        return out.shape[1], out.shape[0]
    if 'cols' in f: t = t[:, f['cols'][0]:f['cols'][1]]
    if 'top' in f: n = f['top']; t[:n] = t[n:2 * n]
    h, w = t.shape[:2]
    b = f.get('b', B); lo, hi = f.get('p', (150, w - b))
    # the repeat width: where the next b columns look most like the first b
    best = min(range(lo, hi + 1), key=lambda p: np.abs(t[:, p:p + b] - t[:, :b]).mean() - p * 0.002)
    out = t[:, :best].copy()
    for x in range(b):
        k = (x + 0.5) / b   # 0: all overrun, 1: all start
        for y in range(h):
            if k < BAYER[y % 4, x % 4]: out[y, x] = t[y, best + x]
    Image.fromarray(out.astype(np.uint8)).save(os.path.join(OUT, name + '.png'))
    return best, h


if __name__ == '__main__':
    for n, top in TOP.items():
        if os.path.exists(os.path.join(HERE, 'img', n + '.png')):
            print(n, *tile(n, top))
