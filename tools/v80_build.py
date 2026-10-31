"""Version 80: Streets of Rage 4 style hits, Tim first. Run from the repo root: python3 tools/v80_build.py. Safe to run again.

Code: tools/v80/fx.js (between `// V80 js start` and `// V80 js end`, after Version 79), plus three hooks patched here:
- startPunch queues a swoosh trail (v80Swoosh) for each combo hit
- drawPart draws it (v80DrawSwoosh): glowing, in the lad's colour, snapped to three colours like the pixel art
- applyHit plays the lad's own directional spark (v80Spark) instead of the old star, flipped the way the hit goes
Sparks: tools/v80/src/tim-hit-spark-{light,heavy}.png from PixelLab's VFX workbench (My effects: "Tim hit spark
(light)" and "(heavy)"), copied to web/fx/tim_spark.png and tim_spark_big.png. Which lads get it: FX_LADS in fx.js."""
import os, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, 'web', 'index.html')
subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'v79_build.py')], check=True)
read = lambda p: open(p, encoding='utf-8').read()
s = read(PAGE)
start, end = '// V80 js start', '// V80 js end'
if start in s: a = s.index(start); b = s.index(end) + len(end) + 1; s = s[:a] + s[b:]
anchor = '// V79 js end\n'
if s.count(anchor) != 1: sys.exit('v80_build: run tools/v79_build.py first')
s = s.replace(anchor, anchor + start + '\n' + read(os.path.join(ROOT, 'tools', 'v80', 'fx.js')).rstrip('\n') + '\n' + end + '\n')
SWAPS = [
    ('the swoosh in startPunch', "  p.atkT = 0; sfx('swing');\n}\nfunction kickBall(",
     "  p.atkT = 0; sfx('swing'); v80Swoosh(p);   // Version 80\n}\nfunction kickBall("),
    ('drawing it', "  if (p.k === 'fx') { const m = FX[p.fx];",
     "  if (p.k === 'swoosh') { v80DrawSwoosh(p); return; }   // Version 80\n  if (p.k === 'fx') { const m = FX[p.fx];"),
    ('the spark in applyHit', "  spark(t.x - dir * t.half * 0.4, t.y, t.z + hz, big);\n",
     "  if (!v80Spark(a, t.x - dir * t.half * 0.4, t.y, t.z + hz, big, dir)) spark(t.x - dir * t.half * 0.4, t.y, t.z + hz, big);   // Version 80\n"),
]
for label, old, new in SWAPS:
    if new in s: continue
    if s.count(old) != 1: sys.exit(f'v80_build: could not find {label} (found {s.count(old)})')
    s = s.replace(old, new)
open(PAGE, 'w', encoding='utf-8').write(s)
for src, dst in (('tim-hit-spark-light.png', 'tim_spark.png'), ('tim-hit-spark-heavy.png', 'tim_spark_big.png')):
    shutil.copyfile(os.path.join(ROOT, 'tools', 'v80', 'src', src), os.path.join(ROOT, 'web', 'fx', dst))
print('v80_build: web/index.html updated, Tim\'s sparks in web/fx/')
