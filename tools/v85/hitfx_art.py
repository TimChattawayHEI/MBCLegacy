"""Version 85 hit effects art: copies tools/v85/hitfx_src/{slam,sweat,thwack}.png to web/fx/ and recolours Tim's
special burst (tools/v85/hitfx_src/tim_burst.png, in his five spark colours) for every lad in FX_COL, as
tools/v81/sparks.py does for the sparks. python3 tools/v85/hitfx_art.py"""
import os, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'v81'))
from sparks import FX_COL, recolour
SRC, OUT = os.path.join(HERE, 'hitfx_src'), os.path.join(ROOT, 'web', 'fx')
for k in ('slam', 'sweat', 'thwack'): shutil.copy(os.path.join(SRC, k + '.png'), os.path.join(OUT, k + '.png'))
for lad, h in FX_COL.items():
    dst = os.path.join(OUT, lad + '_burst.png')
    if lad == 'tim': shutil.copy(os.path.join(SRC, 'tim_burst.png'), dst)
    else: recolour(os.path.join(SRC, 'tim_burst.png'), dst, h)
print('hitfx art: slam, sweat, thwack and a burst for', ', '.join(FX_COL))
