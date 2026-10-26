"""Version 63: the trophy cabinet in the Harvest Moon.

Patches web/index.html in place (run from the repo root, after tools/v62_build.py):  python3 tools/v63_build.py
Safe to run again; it re-runs v62_build.py first. The code is tools/v63/cabinet.js with the trophy positions from
tools/v63/trophy_items.json, put in whole between `// V63 js start` and `// V63 js end`; the pub's own changes (a
longer room, the cabinet as something to walk up to, drawing it) are in tools/v55/pub.js ("Version 63"). The art is
tools/v63/trophy_art.py (run it after changing anything in tools/v63/img).
"""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, 'web', 'index.html')
read = lambda p: open(p, encoding='utf-8').read()


def swap(s, old, new, label):
    if new in s:
        return s
    if s.count(old) != 1:
        sys.exit(f'v63_build: could not find the {label} (found {s.count(old)} matches)')
    return s.replace(old, new)


subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'v62_build.py')], check=True)
s = read(PAGE)
cab = json.load(open(os.path.join(ROOT, 'tools', 'v63', 'trophy_items.json')))
code = 'const TROPHY_CAB = ' + json.dumps(cab, separators=(',', ':')) + ';\n' + read(os.path.join(ROOT, 'tools', 'v63', 'cabinet.js')).rstrip('\n')
start, end = '// V63 js start', '// V63 js end'
block = start + '\n' + code + '\n' + end + '\n'
if start in s:
    a = s.index(start); b = s.index(end) + len(end) + 1
    s = s[:a] + block + s[b:]
else:
    s = swap(s, "// V62 js end\n", "// V62 js end\n" + block, 'version 63 module')
open(PAGE, 'w', encoding='utf-8').write(s)
print('v63_build: web/index.html updated')
