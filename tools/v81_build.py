"""Version 81: every lad's own hits, and a signature effect on each mini special. Run from the repo root:
python3 tools/v81_build.py. Safe to run again.

Code: tools/v81/fx.js (between `// V81 js start` and `// V81 js end`, after Version 80), plus two hooks patched here:
- startMini calls v81MiniStart (the effects that play as the move starts)
- miniBurst calls v81MiniBurst (the effects on the last hit, and the flash in the lad's colour)
- drawPart draws both (v81DrawPart)
Art: tools/v81/sparks.py recolours Tim's spark sheets for every lad (web/fx/<lad>_spark(_big).png); the nine mini
special effects were made in PixelLab's VFX workbench (in Tim's My effects as "<Lad> mini: ...") and are kept in
tools/v81/src/mini_<lad>.png, copied to web/fx/. Colours: FX_COL; trail fits: SW_FIT; mini timing and placing: MINI_FX."""
import os, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, 'web', 'index.html')
subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'v80_build.py')], check=True)
subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'v81', 'sparks.py')], check=True)
read = lambda p: open(p, encoding='utf-8').read()
s = read(PAGE)
start, end = '// V81 js start', '// V81 js end'
if start in s: a = s.index(start); b = s.index(end) + len(end) + 1; s = s[:a] + s[b:]
anchor = '// V80 js end\n'
if s.count(anchor) != 1: sys.exit('v81_build: run tools/v80_build.py first')
s = s.replace(anchor, anchor + start + '\n' + read(os.path.join(ROOT, 'tools', 'v81', 'fx.js')).rstrip('\n') + '\n' + end + '\n')
SWAPS = [
    ('the start of a mini special', "  if (p.def.id === 'byron') sfx('whistle');\n}\n",
     "  if (p.def.id === 'byron') sfx('whistle');\n  v81MiniStart(p);   // Version 81\n}\n"),
    ('the mini special burst', "  addShake(last ? 6 : 3); if (last) sfx('heavy');\n",
     "  addShake(last ? 6 : 3); if (last) sfx('heavy');\n  v81MiniBurst(p, m, last);   // Version 81\n"),
    ('drawing them', "  if (p.k === 'swoosh') { v80DrawSwoosh(p); return; }   // Version 80\n",
     "  if (p.k === 'v81fx' || p.k === 'v81flash') { v81DrawPart(p); return; }   // Version 81\n  if (p.k === 'swoosh') { v80DrawSwoosh(p); return; }   // Version 80\n"),
]
for label, old, new in SWAPS:
    if new in s: continue
    if s.count(old) != 1: sys.exit(f'v81_build: could not find {label} (found {s.count(old)})')
    s = s.replace(old, new)
open(PAGE, 'w', encoding='utf-8').write(s)
for lad in ('tim', 'seb', 'byron', 'pearcy', 'kelly', 'marc', 'sam', 'thet', 'ash'):
    shutil.copyfile(os.path.join(ROOT, 'tools', 'v81', 'src', f'mini_{lad}.png'), os.path.join(ROOT, 'web', 'fx', f'mini_{lad}.png'))
print('v81_build: web/index.html updated, every lad\'s sparks and mini special effects in web/fx/')
