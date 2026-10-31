"""Version 81: every lad's own spark sheets, recoloured from Tim's (tools/v80/src, PixelLab VFX workbench).
python3 tools/v81/sparks.py  ->  web/fx/<lad>_spark.png and <lad>_spark_big.png for every lad in FX_COL.
Tim's sheets have five colours: an outline, a shade, the base blue, a light tint and white. Each is swapped for the
same step of the lad's ramp, so the sparks keep their shape and shading."""
import os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Keep in step with FX_COL in tools/v81/fx.js
FX_COL = {'tim': '#6aa8e8', 'seb': '#b0d050', 'byron': '#4fd8d0', 'pearcy': '#ffcf3a', 'kelly': '#b98ce6',
          'marc': '#ff6a6a', 'sam': '#ff7ab8', 'thet': '#dfe8f8', 'ash': '#f07a2a'}
TIM = {(26, 8, 2): 'outline', (59, 111, 196): 'shade', (106, 168, 232): 'base', (191, 224, 255): 'tint', (255, 255, 255): 'white'}


def rgb(h): return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
def mix(a, b, k): return tuple(round(x + (y - x) * k) for x, y in zip(a, b))


def ramp(h):
    c = rgb(h)
    return {'outline': mix(c, (12, 6, 4), 0.86), 'shade': mix(c, (0, 0, 0), 0.38), 'base': c, 'tint': mix(c, (255, 255, 255), 0.55), 'white': (255, 255, 255)}


def recolour(src, dst, h):
    im = Image.open(src).convert('RGBA'); px = im.load(); r = ramp(h)
    for y in range(im.height):
        for x in range(im.width):
            p = px[x, y]
            if p[3] == 0: continue
            px[x, y] = r[TIM.get(p[:3], 'base')] + (p[3],)
    im.save(dst, optimize=True)


if __name__ == '__main__':
    src = os.path.join(ROOT, 'tools', 'v80', 'src')
    for lad, h in FX_COL.items():
        if lad == 'tim': continue   # Tim's are the originals, copied by v80_build
        recolour(os.path.join(src, 'tim-hit-spark-light.png'), os.path.join(ROOT, 'web', 'fx', lad + '_spark.png'), h)
        recolour(os.path.join(src, 'tim-hit-spark-heavy.png'), os.path.join(ROOT, 'web', 'fx', lad + '_spark_big.png'), h)
    print('sparks: web/fx/<lad>_spark(_big).png for', ', '.join(k for k in FX_COL if k != 'tim'))
