"""Version 64: stages repainted in Meshy, one long picture each.

Patches web/index.html in place (run from the repo root):  python3 tools/v64_build.py
Safe to run again; it re-runs v63_build.py first. The code is tools/v64/meshy_bg.js, put in whole between
`// V64 js start` and `// V64 js end` just after the art preload, and drawStageBg() tries it first. The art is made by
tools/v64/meshy_bg.py from the Meshy panels in tools/v64/img (see tools/v64/stages.json).
"""
import os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, 'web', 'index.html')
read = lambda p: open(p, encoding='utf-8').read()


def swap(s, old, new, label):
    if new in s:
        return s
    if s.count(old) != 1:
        sys.exit(f'v64_build: could not find the {label} (found {s.count(old)} matches)')
    return s.replace(old, new)


subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'v63_build.py')], check=True)
s = read(PAGE)
start, end = '// V64 js start', '// V64 js end'
block = start + '\n' + read(os.path.join(ROOT, 'tools', 'v64', 'meshy_bg.js')).rstrip('\n') + '\n' + end + '\n'
if start in s:
    a = s.index(start); b = s.index(end) + len(end) + 1
    s = s[:a] + block + s[b:]
else:
    s = swap(s, 'setTimeout(preloadArt, 700);\n', 'setTimeout(preloadArt, 700);\n' + block, 'art preload')
s = swap(s, "function drawStageBg() {\n", "function drawStageBg() {\n  if (meshyBg()) return;   // Version 64: painted in Meshy\n", 'stage backdrop')
# the breakables are Meshy's now (tools/v64/props.py): a grey dustbin and a brown suitcase break into their own colours
s = swap(s, "const col = b.type === 'coolbox' ? '#e9eef0' : b.type === 'keg' ? '#a8adb2' : '#2f5a36';",
         "const col = b.type === 'coolbox' ? '#e9eef0' : b.type === 'keg' ? '#a8adb2' : b.type === 'luggage' ? '#6a4630' : '#8a9096';   // Version 64", 'breakable debris colours')
open(PAGE, 'w', encoding='utf-8').write(s)
print('v64_build: web/index.html updated')
