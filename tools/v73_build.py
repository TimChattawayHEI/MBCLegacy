"""Version 73: Orpington 2001 rebuilt as one-screen places (Tim, 31 October: the stitched backdrops didn't blend, the mechanics
weren't explained, it was too short). Run from the repo root after tools/v72_build.py has been run once:
python3 tools/v73_build.py. Safe to run again.

- The chapter's code is now tools/v73/orp2001.js; it replaces tools/v72/orp2001.js between `// V72 js start` and
  `// V72 js end` (the V72 hooks into the page stay: updateOrp, orpEvent, orpDrawFore, orpBeatMult, Mick's boss wave).
- drawStageBg draws the current place's painting (web/bg/orp/<scene>.png, tools/v73/scenes.py) first.
- The comic pages are web/bg/comic/pages/{p2001,pspill,pmick,pdoor,p2am}_<n>.png (tools/v73/comics.py).
- The old stitched tiles (web/bg/meshy/orp_*.png) are no longer used and are deleted.
"""
import glob, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, 'web', 'index.html')
read = lambda p: open(p, encoding='utf-8').read()
s = read(PAGE)
start, end = '// V72 js start', '// V72 js end'
if start not in s: sys.exit('v73_build: run tools/v72_build.py first')
block = start + '\n' + read(os.path.join(ROOT, 'tools', 'v73', 'orp2001.js')).rstrip('\n') + '\n' + end + '\n'
a = s.index(start); b = s.index(end) + len(end) + 1; s = s[:a] + block + s[b:]
SWAPS = [
    ('backdrop', "function drawStageBg() {\n  if (meshyBg()) return;", "function drawStageBg() {\n  if (orpBg()) return;   // Version 73: Orpington 2001's places\n  if (meshyBg()) return;"),
]
for label, old, new in SWAPS:
    if new in s: continue
    if s.count(old) != 1: sys.exit(f'v73_build: could not find the {label} (found {s.count(old)})')
    s = s.replace(old, new)
open(PAGE, 'w', encoding='utf-8').write(s)
for f in glob.glob(os.path.join(ROOT, 'web', 'bg', 'meshy', 'orp_*.png')): os.remove(f)
print('v73_build: web/index.html updated')
