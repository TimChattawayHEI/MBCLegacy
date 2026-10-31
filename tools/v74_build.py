"""Version 74: horseshoes and cart wheels at the Blacksmiths, boss cards for Alan, Jeff and Mick, SNAKE (Kelly on the coach,
a bonus round after Atlantis and a cabinet at the far end of the Harvest Moon), and two trophies. Run from the repo root
after tools/v73_build.py: python3 tools/v74_build.py. Safe to run again.

The game code is in tools/v73/orp2001.js (its Version 74 section), so this re-runs v73_build.py for it, then patches the
pub (the room is longer, the Snake cabinet and its chalkboard) and the trophy list.
Art: tools/v74/props.py (horseshoe, wheel), tools/v74/bosscards.py (the three cards)."""
import os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, 'web', 'index.html')
subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'v73_build.py')], check=True)
s = open(PAGE, encoding='utf-8').read()
SWAPS = [
    ('pub length', "const PUB_W = 2840, PUB_FLOOR = 400;", "const PUB_W = 3100, PUB_FLOOR = 400;   /* Version 74: 2840 until the Snake cabinet */"),
    ('pub object', "  { id: 'endings', x: ENDINGS_X },   // the endings wall (Version 71)\n",
     "  { id: 'endings', x: ENDINGS_X },   // the endings wall (Version 71)\n  { id: 'snake', x: 2990 },   // SNAKE (Version 74)\n"),
    ('games', "const PUB_GAMES = ['darts', 'fruit', 'pens', 'golf', 'awake', 'kiss', 'kebab'];", "const PUB_GAMES = ['darts', 'fruit', 'pens', 'golf', 'awake', 'kiss', 'kebab', 'snake'];"),
    ('trophies', "  { id: 'cnight', name: 'Last Orders', what: 'Finish Nightlife 2006', tab: 2000 },\n",
     "  { id: 'cnight', name: 'Last Orders', what: 'Finish Nightlife 2006', tab: 2000 },\n"
     "  { id: 'c2001', name: 'Underage', what: 'Finish Orpington 2001', tab: 2000 },\n"
     "  { id: 'snake', name: 'Nokia Royalty', what: 'Score 300 in Snake', tab: 2000 },\n"),
    ('chapter trophy', "else if (ch === 'nightlife') achGive('cnight');", "else if (ch === 'nightlife') achGive('cnight'); else if (ch === 'orp2001') achGive('c2001');"),
    ('snake trophy', "  if (id === 'awake' && score >= 1500) achGive('awake');\n", "  if (id === 'awake' && score >= 1500) achGive('awake');\n  if (id === 'snake' && score >= 300) achGive('snake');\n"),
]
for label, old, new in SWAPS:
    if new in s: continue
    if s.count(old) != 1: sys.exit(f'v74_build: could not find the {label} (found {s.count(old)})')
    s = s.replace(old, new)
# the chalkboards and the cabinets are drawn from lists of their own (two of each)
for old, new in [("['darts', 'fruit', 'pens', 'golf', 'awake', 'kiss', 'kebab'])", "['darts', 'fruit', 'pens', 'golf', 'awake', 'kiss', 'kebab', 'snake'])"),
                 ("for (const id of ['pens', 'golf', 'awake', 'kiss', 'kebab'])", "for (const id of ['pens', 'golf', 'awake', 'kiss', 'kebab', 'snake'])")]:
    if new in s: continue
    if s.count(old) != 2: sys.exit(f'v74_build: expected two of {old[:40]} (found {s.count(old)})')
    s = s.replace(old, new)
open(PAGE, 'w', encoding='utf-8').write(s)
print('v74_build: web/index.html updated')
