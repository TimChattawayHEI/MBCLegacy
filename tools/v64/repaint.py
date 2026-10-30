"""Repaint pieces of art in Meshy, same shapes, new look: python3 tools/v64/repaint.py <sheet> [--make]

For stages built from pieces the game moves about (the train's carriage, doors and toilets; the bus deck; the scenery
strips past the windows), each piece keeps its size and its see-through parts and only its paint changes, so the game
code is untouched. SHEETS lists pieces laid out on one 16:9 picture (see-through parts filled flat magenta); --make sends
it to Meshy (9 credits) with the style pictures, and without --make the last Meshy result (tools/v64/img/repaint/<sheet>.webp)
is cut back into the pieces: each is shrunk to its old size, and its old alpha is kept exactly, over web/bg/<path>.png.
The old pieces are kept in tools/v64/img/repaint/old/ the first time, and are always what the layout is built from.
"""
import os, shutil, subprocess, sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
BG = os.path.join(ROOT, 'web', 'bg'); R = os.path.join(HERE, 'img', 'repaint'); OLD = os.path.join(R, 'old')
os.makedirs(OLD, exist_ok=True)
PW, PH = 1376, 768
# sheet -> (scale, [(path, x, y)], what it is)
SHEETS = {
    'train_wall': (4, [('nightlife/tr_wall', 48, 96)],
                   "the inside wall of a 2006 London suburban commuter train carriage at night, seen straight on: blue and grey moquette seats in a row, grey plastic wall panels, yellow grab poles, signs reading PLEASE OFFER YOUR SEAT and NO SMOKING ON THIS TRAIN, the carriage number, windows"),
    'train_bits': (4, [('nightlife/tr_doorframe', 0, 96), ('nightlife/tr_end', 278, 96), ('nightlife/tr_toilet', 556, 96), ('nightlife/tr_door', 834, 192), ('nightlife/bus_stairs', 1112, 96)],
                   "five separate parts from the inside of a 2006 London commuter train and a night bus, side by side: a door frame, the carriage end wall with its door, a train toilet door with a light above it, a pair of sliding train doors with yellow stripes and windows, and the night bus staircase"),
    'bus_deck': (4, [('nightlife/bus_deck', 48, 96)],
                 "the top deck of a London night bus at 2am, seen from inside, side on: red and blue tartan moquette seats, a yellow grab pole, the bus's red side panels and windows, dim interior lights"),
    'fishery_bits': (5, [('set/board', 20, 30), ('set/peg', 720, 30), ('set/chair', 950, 30)],
                     "three separate things from a carp fishing lake: a big weathered wooden notice board on two posts holding a blank laminated cream paper sheet (nothing written on it), a small wooden peg marker post with a blank white plate on top (nothing written on it), and a blue folding camping chair"),
    'fishery_smoker': (6, [('set/smoker', 100, 100)],
                       "a big black barbecue smoker on a little two-wheeled trailer, with a chimney, a firebox and a temperature gauge, seen from the side"),
    # the 3D title street (Version 65): the old Stage 1 shop fronts and street furniture, repainted, saved as new files in bg/title
    'title_shops': (2, [('orpington/chippy', 20, 40, 'title/chippy'), ('orpington/kebab', 200, 40, 'title/kebab'), ('orpington/pub', 432, 40, 'title/pub'),
                        ('orpington/video', 732, 40, 'title/video'), ('orpington/bookies', 952, 40, 'title/bookies'), ('orpington/phones', 1152, 40, 'title/phones'),
                        ('orpington/lamp', 60, 420, 'title/lamp'), ('orpington/phonebox', 220, 500, 'title/phonebox'), ('orpington/bench', 380, 600, 'title/bench')],
                    "the fronts of six small shops on a London suburban high street at dusk, side by side, each one a two storey brick building with its shop front below and a flat window above: a chip shop, a kebab house, a pub called the Harvest Moon, a video rental shop, a bookmakers and a mobile phone shop, with their lit signs and windows; and below them a Victorian street lamp, a red telephone box and a wooden park bench"),
    'naval': (4, [('naval/raft', 40, 120), ('naval/bbq', 1130, 220)],
              "two separate things from a midnight carp lake, side by side: a big orange inflatable dinghy seen from the side and slightly above, with yellow straps and grab ropes and a grey floor, and a small black kettle barbecue on legs with glowing coals"),
    'scenery': (3.44, [('nightlife/sc_suburb', 0, 40), ('nightlife/sc_platform', 0, 400)],
                "two separate long strips of scenery seen from a train window at night, one above the other: a row of south-east London terraced houses with lit windows under a starry sky, and a lit suburban railway platform with lamps, benches and a few waiting commuters"),
    'highst': (3.44, [('nightlife/sc_highst', 0, 220)],
               "a long strip of a south London high street at night seen from a bus window: a row of lit shop fronts reading KEBABS, FRIED CHICKEN, PHONES UNLOCKED, OFF LICENCE and BOOKMAKER, flats above, the pavement in front"),
}


BOOST = {'naval/raft': (1.35, 1.25)}   # (colour, brightness): Meshy painted the dinghy a dull rust; it is a bright orange one
WRAP = {'nightlife/sc_suburb', 'nightlife/sc_platform', 'nightlife/sc_highst', 'nightlife/bus_deck', 'nightlife/tr_wall'}


def old(path):
    o = os.path.join(OLD, path.replace('/', '__') + '.png')
    if not os.path.exists(o): shutil.copy(os.path.join(BG, path + '.png'), o)
    return Image.open(o).convert('RGBA')


def layout(name):
    k, pieces, what = SHEETS[name]
    sheet = Image.new('RGB', (PW, PH), (40, 40, 46))
    for path, x, y, *_ in pieces:
        im = old(path); big = im.resize((round(im.width * k), round(im.height * k)), Image.NEAREST)
        a = np.asarray(big); rgb = a[..., :3].copy(); rgb[a[..., 3] < 128] = (255, 0, 255)
        sheet.paste(Image.fromarray(rgb), (x, y))
    return sheet, what


def make(name):
    sheet, what = layout(name)
    work = os.environ.get('MESHY_WORK', '/tmp/meshy_work'); os.makedirs(os.path.join(work, 'repaint'), exist_ok=True)
    sp = os.path.join(work, 'repaint', name + '_layout.png'); sheet.save(sp)
    prompt = ("Repaint the first image as rich, detailed, gritty 16-bit pixel art in exactly the style, pixel size, texture and " + os.environ.get('LIGHT', 'moody night lighting') + " of the other images. "
              f"It shows {what}. Keep every shape exactly where it is and exactly the same size: the same outlines, the same layout, the same text. "
              "Every flat bright magenta area must stay exactly flat bright magenta (#FF00FF), untouched, with crisp edges. The plain dark grey background stays plain dark grey. No people other than any already there.")
    subprocess.run([sys.executable, os.path.join(HERE, 'meshy_free.py'), 'repaint', name, prompt, sp + ',' + os.environ.get('STYLES', 'street,alley')], check=True,
                   env=dict(os.environ, MESHY_WORK=work))
    Image.open(os.path.join(work, 'repaint', name + '_raw.png')).save(os.path.join(R, name + '.webp'), quality=95, method=6)


def cut(name):
    k, pieces, _ = SHEETS[name]
    new = Image.open(os.path.join(R, name + '.webp')).convert('RGB').resize((PW, PH))
    for path, x, y, *dest in pieces:   # Meshy keeps the layout where it was put
        im = old(path); w, h = round(im.width * k), round(im.height * k)
        part = new.crop((x, y, x + w, y + h)).resize(im.size, Image.LANCZOS)
        if path in BOOST:
            from PIL import ImageEnhance
            part = ImageEnhance.Brightness(ImageEnhance.Color(part).enhance(BOOST[path][0])).enhance(BOOST[path][1])
        o = np.asarray(im).astype(np.int32); a = o[..., 3]; p = np.asarray(part).astype(np.int32)
        out = np.dstack([p, a])
        # see-through parts (window glass, sky) keep their old paint; so does any magenta that bled into an edge
        mag = (p[..., 0] - p[..., 1] > 55) & (p[..., 2] - p[..., 1] > 55)
        keep = (a < 255) | mag
        out[keep] = o[keep]
        if path in WRAP:   # it repeats side by side: ease both ends to the same column so the repeat has no edge
            n = 8; f = out[..., :3].astype(np.float32); mid = (f[:, :1] + f[:, -1:]) / 2
            for i in range(n):
                t_ = i / n; f[:, i] = mid[:, 0] * (1 - t_) + f[:, i] * t_; f[:, -1 - i] = mid[:, 0] * (1 - t_) + f[:, -1 - i] * t_
            out[..., :3] = np.where(keep[..., None], out[..., :3], f.round())
        Image.fromarray(out.astype(np.uint8), 'RGBA').save(os.path.join(BG, (dest[0] if dest else path) + '.png'))
        print(path, im.size)


if __name__ == '__main__':
    for n in [a for a in sys.argv[1:] if not a.startswith('--')] or list(SHEETS):
        if '--make' in sys.argv: make(n)
        if os.path.exists(os.path.join(R, n + '.webp')): cut(n)
