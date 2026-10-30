"""Version 65: the health bars painted in Meshy -> web/bg/hud/*.png.  python3 tools/v65/hud.py [--layout | --make]

--layout writes the layout Meshy repaints (tools/v65/img/hud_layout.png): the player's plate (portrait window, health
and special troughs as flat magenta holes), the boss bar's frame, and four bar fills as flat colour strips, each at 6x
its native size (1 native pixel = 2 game units, as everything else is drawn). --make sends it to Meshy (9 credits,
tools/v64/meshy_free.py) and keeps the result as tools/v65/img/hud.webp. With no flag, hud.webp is cut back into the
pieces at native size: the frames keep the layout's holes exactly (see-through), the fills are shrunk to one tile the
game stretches along the bar and crops to how full it is.
"""
import os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, 'web', 'bg', 'hud'); os.makedirs(OUT, exist_ok=True)
K, PW, PH, MAG = 6, 1376, 768, (255, 0, 255)
# name: (x, y, native w, native h, holes [(x0, y0, x1, y1)] in native pixels)
FRAMES = {
    'plate': (30, 30, 182, 42, [(3, 3, 33, 39), (38, 17, 175, 24), (38, 30, 114, 35)]),
    'boss': (30, 318, 216, 14, [(8, 4, 208, 10)]),
}
FILLS = {   # name: (x, y, native w, native h, colour)
    'fill_hp': (30, 440, 137, 7, (110, 200, 80)),
    'fill_sp': (30, 512, 76, 5, (240, 180, 50)),
    'fill_boss': (30, 572, 200, 6, (242, 150, 50)),
    'fill_foe': (30, 650, 98, 4, (220, 64, 64)),
}


def layout():
    im = Image.new('RGB', (PW, PH), (40, 40, 46)); d = ImageDraw.Draw(im)
    for x, y, w, h, holes in FRAMES.values():
        d.rectangle((x, y, x + w * K - 1, y + h * K - 1), fill=(70, 74, 82), outline=(20, 20, 24), width=K)
        for a, b, c, e in holes: d.rectangle((x + a * K, y + b * K, x + c * K - 1, y + e * K - 1), fill=MAG)
    for x, y, w, h, col in FILLS.values():
        d.rectangle((x, y, x + w * K - 1, y + h * K - 1), fill=col, outline=(20, 20, 24), width=K)
    return im


def cut():
    new = Image.open(os.path.join(HERE, 'img', 'hud.webp')).convert('RGB').resize((PW, PH))
    for n, (x, y, w, h, holes) in FRAMES.items():
        p = new.crop((x, y, x + w * K, y + h * K)).resize((w, h), Image.LANCZOS).convert('RGBA')
        a = np.asarray(p).copy()
        for x0, y0, x1, y1 in holes: a[y0:y1, x0:x1, 3] = 0
        Image.fromarray(a).save(os.path.join(OUT, n + '.png')); print(n, (w, h))
    for n, (x, y, w, h, _) in FILLS.items():
        # inside the dark outline only; one tile 24 native pixels wide (taken from the middle), repeated by the game
        p = new.crop((x + K, y + K, x + (w - 1) * K, y + (h - 1) * K)).resize((w - 2, h - 2), Image.LANCZOS)
        t = p.crop(((w - 2) // 2 - 12, 0, (w - 2) // 2 + 12, h - 2))
        t.save(os.path.join(OUT, n + '.png')); print(n, t.size)


if __name__ == '__main__':
    if '--layout' in sys.argv or '--make' in sys.argv:
        lp = os.path.join(HERE, 'img', 'hud_layout.png'); layout().save(lp); print('layout', lp)
    if '--make' in sys.argv:
        work = os.environ.get('MESHY_WORK', '/tmp/meshy_work')
        prompt = ("Repaint the first image as a set of chunky, polished 16-bit arcade beat 'em up HUD pieces in the gritty pixel art style of the other images. "
                  "Keep every shape exactly where it is and exactly the same size. The two grey panels become heavy bevelled gunmetal plates with brass rivets and "
                  "scuffed edges, like an old fruit machine or a pub sign, with a recessed dark lip around each hole. Every flat bright magenta hole must stay exactly "
                  "flat bright magenta (#FF00FF), untouched, with crisp edges. The four coloured strips become glossy bars of glowing liquid in glass tubes, keeping "
                  "their own colours (green, gold, orange, red): a bright highlight along the top, deeper colour at the bottom, small even notches along their length. "
                  "The plain dark grey background stays plain dark grey. No text, no people.")
        subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'v64', 'meshy_free.py'), 'hud', 'hud', prompt, lp + ',street,alley'], check=True, env=dict(os.environ, MESHY_WORK=work))
        Image.open(os.path.join(work, 'hud', 'hud_raw.png')).save(os.path.join(HERE, 'img', 'hud.webp'), quality=94, method=6)
    if os.path.exists(os.path.join(HERE, 'img', 'hud.webp')): cut()
