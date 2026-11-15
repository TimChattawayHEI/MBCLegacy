"""Version 85: hand-drawn small effects. python3 tools/v85_vfx_build.py (re-runnable; patches web/index.html in place).
Art: python3 tools/v85/vfx_art.py first (writes web/fx/*.png and prints the FX lines this pastes in).
Code: tools/v85/vfx.js between `// V85 vfx start` and `// V85 vfx end`, after the music; one hook in the particle
drawing hands puffs, dust, flames, sparkles, drops, hearts, Zs and debris to v85Part, which falls back to the old
drawing until the sheets have loaded."""
import os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); PAGE = os.path.join(ROOT, 'web', 'index.html')
lines = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'v85', 'vfx_art.py')], check=True, capture_output=True, text=True).stdout.strip()
s = open(PAGE, encoding='utf-8').read()
start, end = '// V85 vfx start', '// V85 vfx end'
if start in s: a = s.index(start); b = s.index(end) + len(end) + 1; s = s[:a] + s[b:]
js = open(os.path.join(ROOT, 'tools', 'v85', 'vfx.js'), encoding='utf-8').read().replace('/*FX_LINES*/', lines)
anchor = '// V85 music end\n'
assert s.count(anchor) == 1
s = s.replace(anchor, anchor + start + '\n' + js.rstrip('\n') + '\n' + end + '\n')
SWAPS = [
    ("  if (p.k === 'swoosh') { v80DrawSwoosh(p); return; }   // Version 80\n",
     "  if (p.k === 'swoosh') { v80DrawSwoosh(p); return; }   // Version 80\n"
     "  if (typeof v85Part === 'function' && v85Part(p, x, y, k)) return;   // Version 85: hand-drawn small effects\n"),
]
for old, new in SWAPS:
    if new in s: continue
    assert s.count(old) == 1, old[:70]
    s = s.replace(old, new)
open(PAGE, 'w', encoding='utf-8').write(s); print('v85 vfx: patched,', lines.count('FX.'), 'sheets')
