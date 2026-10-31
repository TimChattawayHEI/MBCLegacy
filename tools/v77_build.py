"""Version 77: lighting for Orpington 2001. Run from the repo root: python3 tools/v77_build.py. Safe to run again.

- Runs tools/v76_build.py first (which runs v74 and v73, so the chapter and its crowd are current).
- The lighting code, tools/v77/light.js, goes in after the crowd's, between `// V77 js start` and `// V77 js end`. The
  chapter's own code calls it (orpBg draws the glow, updateOrp moves the headlights).
- Every fighter drawn from a sprite sheet gets lit in drawLad (Orpington 2001 only).
- Glow layers: web/bg/orp/<scene>_glow.png, from tools/v77/glow.py (Meshy light maps kept in tools/v77/img/)."""
import os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, 'web', 'index.html')
subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'v76_build.py')], check=True)
read = lambda p: open(p, encoding='utf-8').read()
s = read(PAGE)
start, end = '// V77 js start', '// V77 js end'
if start in s: a = s.index(start); b = s.index(end) + len(end) + 1; s = s[:a] + s[b:]
anchor = '// V76 js end\n'
if s.count(anchor) != 1: sys.exit('v77_build: run tools/v76_build.py first')
s = s.replace(anchor, anchor + start + '\n' + read(os.path.join(ROOT, 'tools', 'v77', 'light.js')).rstrip('\n') + '\n' + end + '\n')
SWAPS = [
    ('sprite light', "  drawSprCell(sh, idx * m.cell, row[0] * m.cell, m.cell, tint, -m.ax * k, -m.ay * k, m.cell * k, m.cell * k);\n",
     "  drawSprCell(sh, idx * m.cell, row[0] * m.cell, m.cell, tint, -m.ax * k, -m.ay * k, m.cell * k, m.cell * k);\n"
     "  if (!tint && ST && ST.era === 2001 && mode !== 'title') orpLightSprite(e, sh, idx * m.cell, row[0] * m.cell, m.cell, -m.ax * k, -m.ay * k, m.cell * k, m.cell * k, dir);   // Version 77\n"),
]
for label, old, new in SWAPS:
    if new in s: continue
    if s.count(old) != 1: sys.exit(f'v77_build: could not find the {label} (found {s.count(old)})')
    s = s.replace(old, new)
open(PAGE, 'w', encoding='utf-8').write(s)
print('v77_build: web/index.html updated')
