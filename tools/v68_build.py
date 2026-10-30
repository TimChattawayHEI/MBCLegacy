"""Version 68: Seb redrawn from Tim's photos (no sunglasses, no camo). Patches web/index.html in place (run from the
repo root): python3 tools/v68_build.py. Safe to run again. Like v66 and v67, it patches the page in place and doesn't re-run the earlier build scripts.

The sheets are made by tools/v68/seb_sheet.py (web/sprites/seb.png, pose_seb.png and tools/v68/seb_meta.json); this puts
his new SPRITE_META entry (anchor, rows, hand points) and frame picks into the page, and his new outfit into the few
places the game describes him.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, 'web', 'index.html')
read = lambda p: open(p, encoding='utf-8').read()


def swap(s, old, new, label):
    if new in s:
        return s
    if s.count(old) != 1:
        sys.exit(f'v68_build: could not find the {label} (found {s.count(old)} matches)')
    return s.replace(old, new)


def obj_end(s, i):
    """index just past the {...} that starts at s[i] (no braces inside strings in these entries)"""
    d = 0
    for j in range(i, len(s)):
        if s[j] == '{': d += 1
        elif s[j] == '}':
            d -= 1
            if d == 0: return j + 1
    raise SystemExit('v68_build: unbalanced braces')


s = read(PAGE)
meta = json.load(open(os.path.join(ROOT, 'tools', 'v68', 'seb_meta.json')))
# SPRITE_META: the "seb" entry
i = s.index('const SPRITE_META = {'); k = s.index('"seb":{', i); a = k + len('"seb":')
s = s[:a] + json.dumps(meta['seb'], separators=(',', ':')) + s[obj_end(s, a):]
# LAD_FRAMES: his frame picks
k = s.index('\n  seb: { jab:'); a = k + len('\n  seb: ')
s = s[:a] + meta['frames'] + s[obj_end(s, a):]
open(PAGE, 'w', encoding='utf-8').write(s)
print('v68_build: web/index.html updated')
