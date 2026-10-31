"""Repaint only the pavement and road along a stretch of the stitched Orpington strip, so a narrow pavement widens smoothly
into a deep one (Meshy, 9 credits). python3 tools/v72/ground.py <strip.png> <x0> <name> <y_base> <kerb_left> <kerb_right> <xa> <xb>

Takes the 1376 px from x0, replaces the rows below y_base with a flat guide (pavement grey down to a kerb line that runs
at kerb_left until xa, slopes to kerb_right by xb, then flat; road below) and asks Meshy to keep everything above and paint
the ground. Saves MESHY_WORK/orp01/<name>_raw.png; compose only its rows below y_base back in (orp_strip.py does)."""
import os, subprocess, sys
import numpy as np
from PIL import Image, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); V64 = os.path.join(HERE, '..', 'v64')
D = os.path.join(os.environ.get('MESHY_WORK', '/tmp/meshy_work'), 'orp01')
sp, x0, name, yb, kl, kr, xa, xb = sys.argv[1], *map(int, sys.argv[2:3]), sys.argv[3], *map(int, sys.argv[4:9])
crop = Image.open(sp).convert('RGB').crop((x0, 0, x0 + 1376, 768)); a = np.asarray(crop).astype(float)
pave = np.median(a[yb + 10:kr - 10, 1376 - 200:].reshape(-1, 3), 0); road = np.median(a[kr + 15:, 1376 - 200:].reshape(-1, 3), 0)
g = a.copy()
for x in range(1376):
    k = kl if x < xa - x0 else kr if x > xb - x0 else kl + (kr - kl) * (x - (xa - x0)) / (xb - xa)
    g[yb:int(k), x] = pave; g[int(k):int(k) + 6, x] = pave * 0.7; g[int(k) + 6:, x] = road
gi = Image.fromarray(g.astype('uint8')); low = gi.crop((0, yb, 1376, 768)).filter(ImageFilter.GaussianBlur(3)); gi.paste(low, (0, yb))
cp = os.path.join(D, name + '_canvas.png'); gi.save(cp)
prompt = ("The first image is a wide pixel art background for a side-scrolling beat 'em up game: a night street in Orpington. Keep everything above the "
          f"pavement exactly as it is, pixel for pixel. Repaint only the flat bottom part, the pavement and the road, following the flat colours there as a guide: "
          "a grey paving slab pavement along the front of the buildings and the car park (with a dropped kerb at the car park entrance), whose kerb edge runs "
          "where the guide shows (narrow on the left, gently widening, then wide and level), and the dark tarmac road below it with a yellow line along the kerb, "
          "a few cracks and drain covers, lit softly by the street lamps. Same pixel art style, pixel size and night colours as the rest of the picture and the "
          "second image. No people, no cars, nothing standing on the pavement or the road.")
subprocess.run([sys.executable, os.path.join(V64, 'meshy_free.py'), 'orp01', name, prompt, cp + ',' + os.path.join(D, 'p3n_raw.png')], check=True)
