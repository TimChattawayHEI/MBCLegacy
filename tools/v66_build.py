"""Version 66: in-app updates. Patches web/index.html in place (run from the repo root): python3 tools/v66_build.py

The app (android/.../Ota.java) now updates the game files itself: the APK build lists every file with its hash
(tools/ota/manifest.py, ota.txt), and the app downloads only the ones that changed, checks them and switches them in on
a restart. The game side is the update card in tools/v61/qol.js (UPDATE READY / Restart, or the old APK card when the
Android side changed).

This script only puts tools/v61/qol.js back in place between its markers. It does not re-run the earlier build
scripts: re-running v64_build.py adds another copy of the Meshy backdrop line in drawStageBg each time.
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, 'web', 'index.html')
read = lambda p: open(p, encoding='utf-8').read()

s = read(PAGE)
start, end = '// QOL js start', '// QOL js end'
if s.count(start) != 1 or s.count(end) != 1:
    sys.exit('v66_build: the quality of life block is missing; run tools/v61_build.py first')
block = start + '\n' + read(os.path.join(ROOT, 'tools', 'v61', 'qol.js')).rstrip('\n') + '\n' + end + '\n'
a = s.index(start)
b = s.index(end) + len(end) + 1
s = s[:a] + block + s[b:]
open(PAGE, 'w', encoding='utf-8').write(s)
print('v66_build: web/index.html updated')
