"""Pixel art drawn by hand (no generator) for the Orpington 2001 crowd: python3 tools/v76/props.py
- web/bg/orp/scooter.png: a silver Razor scooter side on, front to the right (the Razor Kid rides it, then kicks it at you)
- web/bg/orp/stool.png: a pub bar stool, wooden, with a red seat (the Builder throws them)
- web/bg/orp/n3310.png: a Nokia 3310, blue-grey with the green screen (Scrunchie throws it and it comes back)
All drawn at the game's native pixel size; the game draws them at 2x like everything else."""
import os
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, 'web', 'bg', 'orp')
OL = (20, 18, 22, 255)


def outline(im):
    """a one pixel dark outline round everything drawn"""
    W_, H_ = im.size; ip = im.load(); out = Image.new('RGBA', im.size, (0, 0, 0, 0)); op = out.load()
    for y in range(H_):
        for x in range(W_):
            if ip[x, y][3]: op[x, y] = ip[x, y]
            elif any(0 <= x + a < W_ and 0 <= y + b < H_ and ip[x + a, y + b][3] for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1))): op[x, y] = OL
    return out


def scooter():
    im = Image.new('RGBA', (34, 32), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    silver, hi, dark, grip = (176, 182, 190, 255), (228, 232, 236, 255), (108, 114, 124, 255), (40, 40, 44, 255)
    d.rectangle((5, 25, 27, 26), fill=silver); d.line((6, 25, 26, 25), fill=hi)         # the deck
    d.rectangle((24, 22, 26, 26), fill=dark)                                             # the fork block
    d.line((26, 23, 28, 3), fill=silver, width=2); d.line((27, 22, 29, 4), fill=hi)      # the stem, leaning back a touch
    d.rectangle((25, 2, 31, 3), fill=grip)                                               # the bars, end on
    d.rectangle((2, 24, 6, 25), fill=dark)                                               # the rear brake
    for cx in (5, 28):                                                                   # wheels: clear urethane
        d.ellipse((cx - 3, 26, cx + 3, 31), fill=(214, 226, 214, 255)); d.ellipse((cx - 1, 28, cx + 1, 29), fill=dark)
    out = outline(im); out.save(os.path.join(OUT, 'scooter.png')); print('scooter', out.size)


def stool():
    im = Image.new('RGBA', (22, 30), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    wood, wd, red, rh = (128, 80, 42, 255), (90, 54, 28, 255), (150, 34, 36, 255), (196, 64, 60, 255)
    d.rectangle((2, 2, 19, 6), fill=red); d.line((3, 2, 18, 2), fill=rh)                 # the seat
    d.line((4, 7, 2, 28), fill=wood, width=2); d.line((17, 7, 19, 28), fill=wood, width=2)   # front legs
    d.line((8, 7, 7, 26), fill=wd); d.line((13, 7, 14, 26), fill=wd)                     # back legs, darker
    d.line((3, 18, 18, 18), fill=wood); d.line((3, 19, 18, 19), fill=wd)                 # the foot rail
    out = outline(im); out.save(os.path.join(OUT, 'stool.png')); print('stool', out.size)


def n3310():
    im = Image.new('RGBA', (9, 16), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    body, hi, scr, key = (70, 92, 128, 255), (110, 136, 172, 255), (154, 196, 96, 255), (196, 204, 214, 255)
    d.rounded_rectangle((0, 0, 8, 15), radius=2, fill=body); d.line((1, 1, 1, 13), fill=hi)
    d.rectangle((2, 2, 6, 5), fill=scr)                                                  # the screen
    d.rectangle((3, 7, 5, 7), fill=key)                                                  # the Navi key
    for y in (9, 11, 13):
        for x in (2, 4, 6): im.putpixel((x, y), key)
    out = outline(im); out.save(os.path.join(OUT, 'n3310.png')); print('n3310', out.size)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True); scooter(); stool(); n3310()
