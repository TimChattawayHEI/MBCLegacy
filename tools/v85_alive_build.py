"""Version 85: livelier backgrounds. python3 tools/v85_alive_build.py (re-runnable; patches web/index.html in place).
Code: tools/v85/alive.js, between `// V85 alive start` and `// V85 alive end`, after the smashables. Art: the PixelLab
animation strips in tools/v85/alive_src are copied to web/bg/alive. Hook: the first line of meshyOver, so everything
lands on top of the Meshy painting and under the stage's own extras and the fighters. The paintings are not touched."""
import os, shutil
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); PAGE = os.path.join(ROOT, 'web', 'index.html')
SRC, DST = os.path.join(ROOT, 'tools', 'v85', 'alive_src'), os.path.join(ROOT, 'web', 'bg', 'alive')
os.makedirs(DST, exist_ok=True)
for f in sorted(os.listdir(SRC)):
    if f.endswith('.png'): shutil.copyfile(os.path.join(SRC, f), os.path.join(DST, f))
s = open(PAGE, encoding='utf-8').read()
start, end = '// V85 alive start', '// V85 alive end'
if start in s: a = s.index(start); b = s.index(end) + len(end) + 1; s = s[:a] + s[b:]
anchor = '// V85 smash end\n'
assert s.count(anchor) == 1
s = s.replace(anchor, anchor + start + '\n' + open(os.path.join(ROOT, 'tools', 'v85', 'alive.js'), encoding='utf-8').read().rstrip('\n') + '\n' + end + '\n')
old, new = 'function meshyOver(k) {\n', 'function meshyOver(k) {\n  aliveDraw(k);   // Version 85: livelier backgrounds\n'
if new not in s:
    assert s.count(old) == 1; s = s.replace(old, new)
open(PAGE, 'w', encoding='utf-8').write(s); print('v85 alive: patched')
