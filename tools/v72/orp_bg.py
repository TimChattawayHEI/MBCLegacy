"""Orpington 2001 backdrops into the game: python3 tools/v72/orp_bg.py [--bridge door,door2]

Fits each stage's Meshy picture to the game the way tools/v64/meshy_bg.py does (the line where walls meet the floor,
"base", goes to the stage's FT; 1 pixel = 2 units, 270 pixels tall) and cuts it into 512 pixel tiles,
web/bg/meshy/<stage>_<n>.png, which tools/v64/meshy_bg.js draws (MESHY_BG lists the stages and their tile counts).

- orp_street: tools/v72/img/orp01/street_strip.webp (built by orp_strip.py)
- orp_pub: tools/v72/img/orp01/pub_strip.webp (bi0, bi1, bi2 stitched a quarter overlapped)
- orp_atlantis: at0 (outside) then ai1 (inside), each fitted to its own floor line, joined at the club doors by a Meshy
  repaint of the doorway (img/orp01/door.webp, then door2.webp over the cut door left; --bridge <names> paints them, 9 credits each)
"""
import importlib.util, os, subprocess, sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); IMG = os.path.join(HERE, 'img', 'orp01')
spec = importlib.util.spec_from_file_location('mb', os.path.join(ROOT, 'tools', 'v64', 'meshy_bg.py'))
mb = importlib.util.module_from_spec(spec); sys.argv, argv = [sys.argv[0], '--none'], sys.argv; spec.loader.exec_module(mb); sys.argv = argv
OUT = os.path.join(ROOT, 'web', 'bg', 'meshy')
CFG = {
    'orp_street': {'base': 588, 'top': 84, 'ft': 352},
    'orp_pub': {'base': 548, 'top': 44, 'ft': 352},
    'at0': {'base': 622, 'top': 118, 'ft': 352},
    'ai1': {'base': 505, 'top': 1, 'bottom': 768, 'ft': 352},   # after pad_top: 120 rows of dark ceiling added, the black band under the floor cut
}


def pad_top(im, n=120, cut=648):
    """the inside of the club was painted with less above the floor than the street has: add n rows of its dark ceiling
    (each column's top colour, darkened) so it fits at the same scale, and drop the black band below the floor"""
    a = np.asarray(im.convert('RGB')).astype(float)[:cut]; top = np.median(a[:6], 0) * 0.55
    pad = np.repeat(top[None], n, 0); out = np.concatenate([pad, a], 0)
    out = np.concatenate([out, np.repeat(out[-1:], 768 - out.shape[0], 0)], 0) if out.shape[0] < 768 else out[:768]
    return Image.fromarray(out.clip(0, 255).astype('uint8'))


def fit(im, c):
    c = dict(c); c['len'] = round(im.width * 480 / mb.PW) * 2; return mb.fit(im.convert('RGB'), c)


def tiles(stage, pic):
    n = (pic.width + mb.TILE - 1) // mb.TILE
    for i in range(n): pic.crop((i * mb.TILE, 0, min(pic.width, (i + 1) * mb.TILE), 270)).save(os.path.join(OUT, f'{stage}_{i}.png'), optimize=True)
    print(stage, 'len', pic.width * 2, 'tiles', n)


PROMPTS = {
    'door': ("The first image is a wide pixel art background for a side-scrolling beat 'em up game. Its left third is the outside of the Atlantis "
             "nightclub at night (yellow brick, blue bollards, the pavement) and its right third is inside the club (blue tiled pillars, speakers, the "
             "glossy dance floor). Keep the left and right thirds exactly as they are, pixel for pixel, and repaint the blurry middle third as the way in: "
             "the club's open dark blue double doors in the brick wall with purple light spilling out, a short dark entrance corridor with a cloakroom "
             "hatch, then it opens into the club, so the picture reads as one walk from the street into the club. The floor line stays at the same "
             "height and the bottom stays flat, empty floor the fighters walk on. Same pixel art style and pixel size. No people, no text."),
    'door2': ("The first image is a wide pixel art background for a side-scrolling beat 'em up game. Its left third is the entrance of the Atlantis "
              "nightclub (dark blue doors, yellow brick, the pavement) and its right third is inside the club (speakers, a gold merman, the glossy "
              "dance floor). Keep the left and right thirds exactly as they are, pixel for pixel. Repaint the blurry middle third so there is no cut "
              "between them: the club's front wall ends at a cut-away edge, like a cross-section of the building, and we see straight into the dark "
              "club behind it, lit purple and blue; the pavement on the left turns into the club's dark floor along a doorstep, not a straight line "
              "down the picture. The floor line stays at the same height. Same pixel art style and pixel size. No people, no text."),
}


def bridge(joined, x, name, paint):
    """the 480 native pixels around x, at Meshy's size: outer thirds kept, the middle a crossfade guide; Meshy (9 credits)
    repaints it when paint is set, and its middle goes back over the join faded in at the edges"""
    W_ = 480; crop = joined.crop((x - W_ // 2, 0, x + W_ // 2, 270)).resize((1376, 768), Image.LANCZOS)
    if paint:
        a = np.asarray(crop).astype(float); T = 1376 // 3; L = a[:, T - 1:T]; R = a[:, 1376 - T:1376 - T + 1]
        t = np.linspace(0, 1, 1376 - 2 * T)[None, :, None]; g = a.copy(); g[:, T:1376 - T] = L * (1 - t) + R * t
        work = os.environ.get('MESHY_WORK', '/tmp/meshy_work'); D = os.path.join(work, 'orp01'); os.makedirs(D, exist_ok=True)
        gp = os.path.join(D, name + '_canvas.png'); Image.fromarray(g.astype('uint8')).save(gp); cp = os.path.join(D, name + '_crop.png'); crop.save(cp)
        subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'v64', 'meshy_free.py'), 'orp01', name, PROMPTS[name], gp + ',' + cp], check=True)
        Image.open(os.path.join(D, name + '_raw.png')).convert('RGB').save(os.path.join(IMG, name + '.webp'), quality=92)
    p = os.path.join(IMG, name + '.webp')
    if not os.path.exists(p): return joined
    d = np.asarray(Image.open(p).convert('RGB').resize((480, 270), Image.LANCZOS)).astype(float)
    j = np.asarray(joined).astype(float); a = np.clip(1 - np.abs(np.arange(480) - 240) / 170, 0, 1); a = np.clip(a * 2.2, 0, 1)[None, :, None]
    j[:, x - 240:x + 240] = j[:, x - 240:x + 240] * (1 - a) + d * a
    return Image.fromarray(j.clip(0, 255).astype('uint8'))


if __name__ == '__main__':
    tiles('orp_street', fit(Image.open(os.path.join(IMG, 'street_strip.webp')), CFG['orp_street']))
    tiles('orp_pub', fit(Image.open(os.path.join(IMG, 'pub_strip.webp')), CFG['orp_pub']))
    out = fit(Image.open(os.path.join(IMG, 'at0.webp')), CFG['at0']); ins = fit(pad_top(Image.open(os.path.join(IMG, 'ai1.webp'))), CFG['ai1'])
    joined = Image.new('RGB', (out.width + ins.width, 270)); joined.paste(out, (0, 0)); joined.paste(ins, (out.width, 0)); x = out.width
    paint = sys.argv[sys.argv.index('--bridge') + 1].split(',') if '--bridge' in sys.argv else []
    joined = bridge(joined, x, 'door', 'door' in paint)
    joined = bridge(joined, x + 80, 'door2', 'door2' in paint)   # door left a cut where its right third began
    tiles('orp_atlantis', joined)
