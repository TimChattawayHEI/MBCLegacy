"""Version 79: quality of life. Run from the repo root: python3 tools/v79_build.py. Safe to run again.

Code: tools/v79/qol.js (between `// V79 js start` and `// V79 js end`, after the lighting), plus small hooks:
- the "!" warning for the Orpington crowd's big moves (orpCrowdFore calls qolTells), how-to cards only the first time
  (orpHowto), the carry-on scene (updateOrp, orpGoScene): in tools/v73/orp2001.js and tools/v76/crowd.js
- edge arrows (drawStageFore), auto-turn on a phone (startPunch), LIGHTING / HOW-TO CARDS / AUTO-TURN settings rows,
  and the settings list packed tighter so the extra rows fit on a phone: patched into the page here
- LIGHTING LOW: tools/v77/light.js"""
import os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, 'web', 'index.html')
subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'v77_build.py')], check=True)
read = lambda p: open(p, encoding='utf-8').read()
s = read(PAGE)
start, end = '// V79 js start', '// V79 js end'
if start in s: a = s.index(start); b = s.index(end) + len(end) + 1; s = s[:a] + s[b:]
anchor = '// V77 js end\n'
if s.count(anchor) != 1: sys.exit('v79_build: run tools/v77_build.py first')
s = s.replace(anchor, anchor + start + '\n' + read(os.path.join(ROOT, 'tools', 'v79', 'qol.js')).rstrip('\n') + '\n' + end + '\n')
SWAPS = [
    ('edge arrows', "  drawFG();   // Version 70: the foreground layer\n", "  drawFG();   // Version 70: the foreground layer\n  qolEdgeArrows();   // Version 79\n"),
    ('auto-turn', "function startPunch(p) {\n", "function startPunch(p) {\n  qolAutoFace(p);   // Version 79\n"),
    ('settings rows', "    { id: 'run', label: 'RUNNING', val: settings.run === 'push' ? 'ANY FULL PUSH' : 'HOLD THE STICK OUT', touch: true },\n",
     "    { id: 'run', label: 'RUNNING', val: settings.run === 'push' ? 'ANY FULL PUSH' : 'HOLD THE STICK OUT', touch: true },\n"
     "    { id: 'aim', label: 'AUTO-TURN', val: settings.aim === false ? 'OFF' : 'ON', touch: true },   // Version 79\n"
     "    { id: 'howto', label: 'HOW-TO CARDS', val: settings.howto === 'always' ? 'EVERY TIME' : 'FIRST TIME ONLY' },\n"
     "    { id: 'light', label: 'LIGHTING', val: settings.light === 'low' ? 'LOW' : 'FULL' },\n"),
    ('settings toggles', "  else if (id === 'run') settings.run = settings.run === 'push' ? 'hold' : 'push';\n",
     "  else if (id === 'run') settings.run = settings.run === 'push' ? 'hold' : 'push';\n"
     "  else if (id === 'aim') settings.aim = settings.aim === false;   // Version 79\n"
     "  else if (id === 'howto') settings.howto = settings.howto === 'always' ? 'first' : 'always';\n"
     "  else if (id === 'light') settings.light = settings.light === 'low' ? 'full' : 'low';\n"),
    ('settings spacing', "  rows.forEach((r, i) => { r.x = 452; r.y = 110 + i * (rows.length > 11 ? 30 : 32); r.w = 426; r.h = 28; r.vx = r.x + 196; });",
     "  rows.forEach((r, i) => { const sp = rows.length > 13 ? 26 : rows.length > 11 ? 30 : 32; r.x = 452; r.y = 110 + i * sp; r.w = 426; r.h = Math.min(28, sp - 2); r.vx = r.x + 196; });   // packed tighter for the Version 79 rows"),
]
for label, old, new in SWAPS:
    if new in s: continue
    if s.count(old) != 1: sys.exit(f'v79_build: could not find the {label} (found {s.count(old)})')
    s = s.replace(old, new)
open(PAGE, 'w', encoding='utf-8').write(s)
print('v79_build: web/index.html updated')
