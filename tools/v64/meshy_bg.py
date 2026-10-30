"""Version 64: whole-stage backdrops painted in Meshy -> web/bg/meshy/<stage>_<n>.png.  python3 tools/v64/meshy_bg.py [stage ...]

Each stage was painted as a run of 16:9 Meshy panels (tools/v64/img/<stage>/<panel>.webp, 1376x768, one screen each),
every panel after the first made by giving Meshy the previous panel's right quarter and asking it to carry the scene on
(tools/v64/meshy_free.py for the first, tools/v64/meshy_cont.py for the rest). Here they are laid out a quarter overlapped and cross-faded across the overlap, then fitted
to the game: the line where the buildings meet the ground ("base", a panel pixel row) goes to the stage's FT, the
picture above it (from row "top") fills the screen above FT and the ground below it fills the screen below, at the
game's native scale (1 pixel = 2 units, so 480x270 a screen). The stage's ST.len units across are cut into 512 pixel
wide tiles, which the game draws edge to edge (tools/v64/meshy_bg.js).
"""
import json, os, sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, 'web', 'bg', 'meshy'); os.makedirs(OUT, exist_ok=True)
CFG = json.load(open(os.path.join(HERE, 'stages.json')))
TILE, PW, PH = 512, 1376, 768
Q = PW // 4                       # each panel overlaps the one before by a quarter
FADE = (72, 272)                  # cross-fade from the old panel to the new one between these columns of the overlap


def stitch(stage, panels):
    ims = [np.asarray(Image.open(os.path.join(HERE, 'img', stage, p + '.webp')).convert('RGB').resize((PW, PH))).astype(np.float32) for p in panels]
    out = np.zeros((PH, PW + (PW - Q) * (len(ims) - 1), 3), np.float32)
    out[:, :PW] = ims[0]
    for i, im in enumerate(ims[1:], 1):
        x0 = i * (PW - Q)
        a = np.clip((np.arange(PW) - FADE[0]) / (FADE[1] - FADE[0]), 0, 1)[None, :, None]
        out[:, x0:x0 + PW] = out[:, x0:x0 + PW] * (1 - a) + im * a
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def fit(strip, c):
    w = round(strip.width * 480 / PW); ft = c['ft'] // 2
    top = strip.crop((0, c['top'], strip.width, c['base'])).resize((w, ft), Image.LANCZOS)
    bot = strip.crop((0, c['base'], strip.width, PH)).resize((w, 270 - ft), Image.LANCZOS)
    out = Image.new('RGB', (w, 270)); out.paste(top, (0, 0)); out.paste(bot, (0, ft))
    return out.crop((0, 0, c['len'] // 2, 270))


for stage in sys.argv[1:] or list(CFG):
    c = CFG[stage]
    full = fit(stitch(stage, c['panels']), c)
    for f in os.listdir(OUT):
        if f.startswith(stage + '_'): os.remove(os.path.join(OUT, f))
    n = 0
    for x in range(0, full.width, TILE):
        full.crop((x, 0, min(full.width, x + TILE), 270)).save(os.path.join(OUT, f'{stage}_{n}.png'), optimize=True); n += 1
    print(stage, full.size, n, 'tiles')
