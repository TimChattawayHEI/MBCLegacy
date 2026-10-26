"""Version 61: quality of life.

Patches web/index.html in place (run from the repo root, after tools/v60_build.py):  python3 tools/v61_build.py
Safe to run again; it re-runs v60_build.py first. The code is tools/v61/qol.js, put in whole between `// QOL js start`
and `// QOL js end` (after the floors' block); the name box hooks are in tools/v55/pub.js ("Version 61").

1. A new version is out: the APK build writes www/build.json ({"build": run number}); the app compares it with the
   latest GitHub release and shows a card on the menus with UPDATE (downloads the APK through the phone's browser).
2. Your progress follows your name: unlocks, stage ranks, the pub tab, open cabinets and pub bests in Firebase at
   saves/<NAME>/<KEY>, merged when the app opens and pushed when they change. A save code on the You screen
   (restore/<NAME>/<CODE>) gets it back on a new phone: same name, "It's me", the code.
3. Continue on the tab: out of lives, put another one on the tab (10,000, 20,000, 30,000; three a run) and carry on
   where you fell with a full set of lives. Not online, not in the kebab siege.
"""
import os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, 'web', 'index.html')
read = lambda p: open(p, encoding='utf-8').read()


def swap(s, old, new, label):
    if new in s:
        return s
    if s.count(old) != 1:
        sys.exit(f'v61_build: could not find the {label} (found {s.count(old)} matches)')
    return s.replace(old, new)


subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'v60_build.py')], check=True)
s = read(PAGE)

start, end = '// QOL js start', '// QOL js end'
block = start + '\n' + read(os.path.join(ROOT, 'tools', 'v61', 'qol.js')).rstrip('\n') + '\n' + end + '\n'
if start in s:
    a = s.index(start); b = s.index(end) + len(end) + 1
    s = s[:a] + block + s[b:]
else:
    s = swap(s, "// FLOOR js end\n", "// FLOOR js end\n" + block, 'quality of life module')

# every frame: the update check and the cloud save run from profileTick (tools/v55/pub.js), which calls qolTick()
# out of lives: a continue first
s = swap(s, "if (run.lives > 0) respawn(p); else if (!netOutOfLives(p)) gameOver();",
         "if (run.lives > 0) respawn(p); else if (!netOutOfLives(p)) contOffer(p);   // continue on the tab (Version 61)", 'continue offer')
s = swap(s, "  if (mode === 'pause') { updatePause(); return true; }",
         "  if (mode === 'pause') { updatePause(); return true; }\n  if (mode === 'cont') { contUpdate(dt); return true; }   // Version 61", 'continue step')
s = swap(s, "  if (mode === 'pause') drawPause();",
         "  if (mode === 'pause') drawPause();\n  if (mode === 'cont') contDraw();   // Version 61", 'continue screen')
# (put before the play line: the lines after it are Version 55's swap, which must stay as it wrote them)
s = swap(s, "  if (mode === 'play') { openPause(); return true; }\n",
         "  if (mode === 'cont') { contNo(); return true; }   // Version 61\n  if (mode === 'play') { openPause(); return true; }\n", 'continue back button')

open(PAGE, 'w', encoding='utf-8').write(s)
print('v61_build: web/index.html updated')
