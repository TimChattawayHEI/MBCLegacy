"""Orpington 2001 glow layers (Version 77): python3 tools/v77/glow.py [--make] [scene ...]

For every place, Meshy (nano-banana-pro image-to-image, 9 credits) repaints the place's backdrop (web/bg/orp/<scene>.png) as a
light map: only the light sources and the light they throw, everything else black. That picture decides WHERE the light is;
the colour comes from the backdrop's own pixels, so the layer always sits exactly on the painting even if Meshy nudges
something by a pixel or two. A soft bloom goes round it. Out: web/bg/orp/<scene>_glow.png (480x270, light on black), which
the game adds over the backdrop ('lighter') and pulses (tools/v77/light.js).

--make asks Meshy for the scenes that have no tools/v77/img/<scene>.webp yet (the kept Meshy pictures); without it, just
rebuilds the layers from the kept pictures."""
import os, shutil, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
ORP = os.path.join(ROOT, 'web', 'bg', 'orp'); KEEP = os.path.join(HERE, 'img'); WORK = '/tmp/meshy_glow'
SCENES = ['busstop', 'cross', 'rambaba', 'front', 'lounge', 'bar', 'pool', 'queue', 'floor']
# what counts as a light in each place, for the prompt
WHAT = {
    'busstop': 'the lit shop windows, the street lamp and its glow, the lit Pizza Express sign, the barber pole, lit doorways',
    'cross': 'the street lamps and the pools of light under them, the orange Belisha beacons, the lit windows of the pub at the top',
    'rambaba': 'the lit windows of Ram Ba Ba, the street lamps and their pools of light, the orange Belisha beacon, the moon',
    'front': 'the lit pub windows, the wall lanterns, the lit sign board, the lamp post and the pool of light it throws on the pavement, the moon',
    'lounge': 'the wall lamps and the warm light round them, the fruit machine screens and lights, the lit window',
    'bar': 'the lights over the bar, the lit optics and bottles, the beer pump lights, the wall lamps, the fruit machine lights',
    'pool': 'the lamp over the pool table and the cone of light it throws on the table, the wall lamps, the fruit machine screen, the fire exit sign',
    'queue': 'the lit ATLANTIS NIGHTCLUB sign, the purple neon round the door, the lit DJ EZ posters, the canopy lights',
    'floor': 'the stage lights and their beams, the DJ EZ sign, the glowing bar shelves, the disco ball sparkle, the lit speakers edges',
}
PROMPT = ("Repaint this exact picture as a light map. Keep ONLY the light sources and the light they give off, glowing in their own "
          "colours: {what}. Everything that is not a light or lit by one (walls, roofs, sky, pavement, road, floor, furniture, people) "
          "becomes pure black. Keep the exact same framing and every light in exactly the same place and size, nothing moved, "
          "nothing added. Flat black background, no text.")


def ask(scene):
    src = os.path.join(ORP, scene + '.png'); big = os.path.join(WORK, scene + '_in.png'); os.makedirs(WORK, exist_ok=True)
    Image.open(src).convert('RGB').resize((1376, 774), Image.LANCZOS).save(big)
    env = dict(os.environ, MESHY_WORK=WORK)
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'v64', 'meshy_free.py'), 'glow', scene, PROMPT.format(what=WHAT[scene]), big],
                       capture_output=True, text=True, env=env)
    out = os.path.join(WORK, 'glow', scene + '_raw.png')
    if not os.path.exists(out): print(scene, 'FAILED', (r.stdout + r.stderr)[-400:]); return
    os.makedirs(KEEP, exist_ok=True); Image.open(out).convert('RGB').save(os.path.join(KEEP, scene + '.webp'), quality=92); print(scene, 'kept')


def lum(a): return a[..., 0] * 0.3 + a[..., 1] * 0.59 + a[..., 2] * 0.11


def build(scene):
    src = np.asarray(Image.open(os.path.join(ORP, scene + '.png')).convert('RGB')).astype(np.float32)
    g = Image.open(os.path.join(KEEP, scene + '.webp')).convert('RGB').resize((480, 270), Image.LANCZOS)
    gl = lum(np.asarray(g).astype(np.float32))
    # where Meshy says there is light: a soft mask, widened a pixel or two so a small shift can't lose a lamp
    m = np.clip((gl - 50) / 110, 0, 1)
    mi = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
    m = np.asarray(mi).astype(np.float32) / 255
    # the light itself: the painting's own colour there, brightest where the painting is brightest
    # (only where the painting itself is bright, so anything Meshy made up or moved over a dark wall stays dark)
    sl = lum(src); w = np.clip((sl - 90) / 140, 0, 1) ** 0.8
    core = src * (m * w)[..., None]
    # and a bloom round it
    bloom = np.asarray(Image.fromarray(core.clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(7))).astype(np.float32)
    out = (core * 0.75 + bloom * 0.7).clip(0, 255).astype(np.uint8)
    Image.fromarray(out).save(os.path.join(ORP, scene + '_glow.png'), optimize=True)
    # how well Meshy kept the layout: how much of its light falls on bright parts of the painting
    hit = float((m * (sl > 120)).sum() / max(1, m.sum()))
    print(scene, 'glow layer, light on bright pixels %.0f%%' % (hit * 100))


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')] or SCENES
    if '--make' in sys.argv:
        todo = [s for s in args if not os.path.exists(os.path.join(KEEP, s + '.webp'))]
        with ThreadPoolExecutor(3) as ex: list(ex.map(ask, todo))
    for s in args:
        if os.path.exists(os.path.join(KEEP, s + '.webp')): build(s)
