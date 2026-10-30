"""Version 65: speech bubbles and word bursts painted in Meshy -> web/bg/comic/*.png.  python3 tools/v65/comic.py [--make]

One Meshy sheet (tools/v65/img/comic.webp) of flat shapes at 5x native size on dark grey: two speech balloons (the lads'
white, everyone else's cream), their tails, and four comic bursts (two spiky shapes in gold, two in orange) for the
words that pop off hits. --make lays the shapes out and sends them to Meshy (9 credits, tools/v64/meshy_free.py). The
cut keeps each shape's own outline exactly (the layout's), so the game can nine-slice the balloons and stretch the
bursts to fit the words; the words themselves are still written by the game.
"""
import os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, 'web', 'bg', 'comic'); os.makedirs(OUT, exist_ok=True)
K, PW, PH, BG = 5, 1376, 768, (40, 40, 46)


def burst(w, h, n, inner, seed):
    r = np.random.default_rng(seed); pts = []
    for i in range(n * 2):
        a = i / (n * 2) * 2 * np.pi; k = (1 if i % 2 == 0 else inner) * (r.uniform(0.9, 1.0) if i % 2 == 0 else r.uniform(0.95, 1.05))
        pts.append((w / 2 + np.cos(a) * w / 2 * k, h / 2 + np.sin(a) * h / 2 * k))
    return pts


# name: (x, y, native w, native h, kind, colour)
PIECES = {
    'bubble_lad': (40, 40, 56, 32, 'round', (250, 248, 238)),
    'bubble_foe': (40, 260, 56, 32, 'round', (238, 228, 205)),
    'tail_lad': (360, 60, 14, 12, 'tail', (250, 248, 238)),
    'tail_foe': (360, 280, 14, 12, 'tail', (238, 228, 205)),
    'burst_y1': (480, 30, 84, 46, ('burst', 11, 0.72, 1), (255, 210, 60)),
    'burst_y2': (480, 290, 84, 46, ('burst', 14, 0.8, 2), (255, 210, 60)),
    'burst_o1': (40, 470, 92, 52, ('burst', 12, 0.7, 3), (242, 140, 40)),
    'burst_o2': (560, 520, 92, 50, ('burst', 16, 0.78, 4), (242, 140, 40)),
}


def shape(name):
    _, _, w, h, kind, col = PIECES[name]
    m = Image.new('L', (w * K, h * K), 0); d = ImageDraw.Draw(m)
    if kind == 'round': d.rounded_rectangle((0, 0, w * K - 1, h * K - 1), radius=9 * K, fill=255)
    elif kind == 'tail': d.polygon([(0, 0), (w * K, 0), (w * K * 0.25, h * K)], fill=255)
    else: d.polygon(burst(w * K, h * K, kind[1], kind[2], kind[3]), fill=255)
    return m


def layout():
    im = Image.new('RGB', (PW, PH), BG)
    for n, (x, y, w, h, kind, col) in PIECES.items():
        m = shape(n); fill = Image.new('RGB', m.size, col)
        edge = Image.new('RGB', m.size, (16, 14, 20))
        im.paste(edge, (x, y), m)
        inner = m.resize((m.width - 4 * K, m.height - 4 * K)); im.paste(fill.crop((0, 0, inner.width, inner.height)), (x + 2 * K, y + 2 * K), inner)
    return im


def cut():
    new = Image.open(os.path.join(HERE, 'img', 'comic.webp')).convert('RGB').resize((PW, PH))
    for n, (x, y, w, h, kind, col) in PIECES.items():
        p = new.crop((x, y, x + w * K, y + h * K)).resize((w, h), Image.LANCZOS)
        a = np.asarray(shape(n).resize((w, h), Image.LANCZOS)) > 110
        out = np.dstack([np.asarray(p), (a * 255).astype(np.uint8)])
        # a dark rim where the shape meets see-through, so it reads on any background
        sh = np.zeros_like(a); sh[1:-1, 1:-1] = a[1:-1, 1:-1] & a[:-2, 1:-1] & a[2:, 1:-1] & a[1:-1, :-2] & a[1:-1, 2:]
        out[a & ~sh, :3] = (22, 18, 26)
        Image.fromarray(out, 'RGBA').save(os.path.join(OUT, n + '.png')); print(n, (w, h))


if __name__ == '__main__':
    if '--make' in sys.argv:
        lp = os.path.join(HERE, 'img', 'comic_layout.png'); layout().save(lp)
        work = os.environ.get('MESHY_WORK', '/tmp/meshy_work')
        prompt = ("Repaint the first image as bold, polished comic book art for a retro 16-bit beat 'em up game, in the comic style of the other images. "
                  "Keep every shape exactly where it is, exactly the same size and exactly the same outline. The four rounded and pointed shapes on the left are "
                  "comic speech balloons and their tails: keep them their own pale colours, with a thick black ink outline, a faint paper texture, a soft shadow "
                  "inside the bottom edge and a small glossy highlight at the top left, and completely empty inside, no text. The four spiky shapes are comic sound "
                  "effect bursts: keep their own colours (gold and orange), with a thick black outline, a bright starburst glow in the middle fading to a deeper "
                  "colour at the tips, halftone dots and a second inner spiky ring in a lighter tint, and completely empty in the middle, no text. "
                  "The plain dark grey background stays plain dark grey. No text, no letters, no people.")
        refs = lp + ',' + os.path.join(ROOT, 'tools', 'v65', 'img', 'bosscard', 'parkie.webp') + ',' + os.path.join(ROOT, 'tools', 'v65', 'img', 'bosscard', 'lenny.webp')
        subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'v64', 'meshy_free.py'), 'comic', 'comic', prompt, refs], check=True, env=dict(os.environ, MESHY_WORK=work))
        Image.open(os.path.join(work, 'comic', 'comic_raw.png')).save(os.path.join(HERE, 'img', 'comic.webp'), quality=94, method=6)
    if os.path.exists(os.path.join(HERE, 'img', 'comic.webp')): cut()
