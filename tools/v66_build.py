"""Version 66: Seb redrawn from Tim's photos (no sunglasses, no camo). Patches web/index.html in place (run from the
repo root): python3 tools/v66_build.py. Safe to run again; it re-runs v65_build.py first.

The sheets are made by tools/v66/seb_sheet.py (web/sprites/seb.png, pose_seb.png and tools/v66/seb_meta.json); this puts
his new SPRITE_META entry (anchor, rows, hand points) and frame picks into the page, and his new outfit into the few
places the game describes him.
"""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, 'web', 'index.html')
read = lambda p: open(p, encoding='utf-8').read()


def swap(s, old, new, label):
    if new in s:
        return s
    if s.count(old) != 1:
        sys.exit(f'v66_build: could not find the {label} (found {s.count(old)} matches)')
    return s.replace(old, new)


def obj_end(s, i):
    """index just past the {...} that starts at s[i] (no braces inside strings in these entries)"""
    d = 0
    for j in range(i, len(s)):
        if s[j] == '{': d += 1
        elif s[j] == '}':
            d -= 1
            if d == 0: return j + 1
    raise SystemExit('v66_build: unbalanced braces')


subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'v65_build.py')], check=True)
s = read(PAGE)
meta = json.load(open(os.path.join(ROOT, 'tools', 'v66', 'seb_meta.json')))
# SPRITE_META: the "seb" entry
i = s.index('const SPRITE_META = {'); k = s.index('"seb":{', i); a = k + len('"seb":')
s = s[:a] + json.dumps(meta['seb'], separators=(',', ':')) + s[obj_end(s, a):]
# LAD_FRAMES: his frame picks
k = s.index('\n  seb: { jab:'); a = k + len('\n  seb: ')
s = s[:a] + meta['frames'] + s[obj_end(s, a):]
open(PAGE, 'w', encoding='utf-8').write(s)
print('v66_build: web/index.html updated')
