"""Pixel art drawn by hand (no generator) for the Blacksmiths: python3 tools/v74/props.py
- web/bg/weapons/horseshoe.png: an old iron horseshoe off the pub wall (a throwable weapon)
- web/bg/orp/wheel.png: a wooden cart wheel with an iron tyre, the size of the ones on the wall (rolls across the floor)"""
import math, os
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
OUTL = (24, 18, 16, 255)


def horseshoe():
    W_, H_ = 18, 18; im = Image.new('RGBA', (W_, H_), (0, 0, 0, 0)); px = im.load()
    cx, cy = 8.5, 8.0
    for y in range(H_):
        for x in range(W_):
            dx, dy = (x - cx) / 7.6, (y - cy) / 8.6; d = math.hypot(dx, dy)
            ix, iy = (x - cx) / 3.6, (y - cy + 1.2) / 5.0; di = math.hypot(ix, iy)
            if d > 1 or di < 1: continue                                    # a ring: outside the inner ellipse, inside the outer
            if y < cy - 3 and abs(x - cx) < 3.2: continue                    # the gap at the top, narrower than the inside: the ends curl in
            shade = 0.55 + 0.45 * max(0, (-(x - cx) * 0.5 - (y - cy) * 0.8) / 8)
            px[x, y] = (int(96 * shade + 40), int(98 * shade + 40), int(108 * shade + 44), 255)
    for (x, y) in [(3, 7), (14, 7), (3, 11), (14, 11), (6, 15), (11, 15)]:
        if px[x, y][3]: px[x, y] = (30, 28, 30, 255)   # nail holes
    out = Image.new('RGBA', (W_, H_), (0, 0, 0, 0)); op = out.load(); ip = im.load()
    for y in range(H_):
        for x in range(W_):
            if ip[x, y][3]: op[x, y] = ip[x, y]
            elif any(0 <= x + a < W_ and 0 <= y + b < H_ and ip[x + a, y + b][3] for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1))): op[x, y] = OUTL
    p = os.path.join(ROOT, 'web', 'bg', 'weapons', 'horseshoe.png'); out.save(p); print('horseshoe', out.size)


def wheel():
    N = 44; im = Image.new('RGBA', (N, N), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = (N - 1) / 2
    d.ellipse((0, 0, N - 1, N - 1), fill=OUTL)
    d.ellipse((1, 1, N - 2, N - 2), fill=(70, 70, 76, 255))                 # the iron tyre
    d.ellipse((4, 4, N - 5, N - 5), fill=OUTL)
    d.ellipse((5, 5, N - 6, N - 6), fill=(132, 84, 44, 255))                # the wooden felloe
    d.ellipse((9, 9, N - 10, N - 10), fill=(0, 0, 0, 0))
    for k in range(10):                                                     # spokes
        a = k * math.pi / 5; x1, y1 = c + math.cos(a) * 15, c + math.sin(a) * 15
        d.line((c, c, x1, y1), fill=(118, 74, 38, 255), width=3); d.line((c, c, x1, y1), fill=(160, 108, 60, 255), width=1)
    d.ellipse((c - 6, c - 6, c + 6, c + 6), fill=OUTL); d.ellipse((c - 5, c - 5, c + 5, c + 5), fill=(96, 64, 34, 255)); d.ellipse((c - 2, c - 2, c + 2, c + 2), fill=(60, 60, 66, 255))
    d.arc((6, 6, N - 7, N - 7), 200, 300, fill=(184, 128, 74, 255))          # a highlight
    os.makedirs(os.path.join(ROOT, 'web', 'bg', 'orp'), exist_ok=True)
    im.save(os.path.join(ROOT, 'web', 'bg', 'orp', 'wheel.png')); print('wheel', im.size)


if __name__ == '__main__':
    horseshoe(); wheel()
