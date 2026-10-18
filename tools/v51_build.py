"""Version 51: the last hand-drawn items replaced with PixelLab art.

Patches web/index.html in place (run from the repo root, after tools/v50_build.py):  python3 tools/v51_build.py
Safe to run again.

The pool cue, stick, landing net, laminated rota, Guinness and rum bottles (web/bg/weapons) and the thrown beer bottle,
CD, dart, letter, phone, pill pot, sausage roll and vinyl (web/bg/shots) were drawn pixel by pixel in code; they're
now PixelLab images (kept in the PixelLab Creator gallery), cropped and scaled to their old in-game sizes. The new
sprites have different shapes, so the hand grip points move with them.
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, 'web', 'index.html')


def swap(s, old, new, label):
    if new in s:
        return s
    if s.count(old) != 1:
        sys.exit(f'v51_build: could not find the {label} (found {s.count(old)} matches)')
    return s.replace(old, new)


s = open(PAGE, encoding='utf-8').read()
s = swap(s, """  stick: { grip: [3, 3], ang: 0 }, net: { grip: [3, 11], ang: 0 },
  guinness: { grip: [20, 4], ang: 2.39 }, rum: { grip: [20, 4], ang: 2.39 }, cue: { grip: [10, 2], ang: 0 }, lam: { grip: [4, 6], ang: 0 },""",
         """  stick: { grip: [3, 4], ang: 0 }, net: { grip: [2, 4], ang: 0 },   // grips for the PixelLab versions (Version 51)
  guinness: { grip: [19, 3], ang: 2.39 }, rum: { grip: [21, 3], ang: 2.39 }, cue: { grip: [10, 2], ang: 0 }, lam: { grip: [3, 10], ang: 0 },""", 'weapon grips')
open(PAGE, 'w', encoding='utf-8').write(s)
print('v51_build: web/index.html updated')
