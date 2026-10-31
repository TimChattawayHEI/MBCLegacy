"""Version 76: Orpington 2001 gets a crowd of its own. Ten locals drawn and animated in PixelLab, each with a move nobody
else in the game has (the Kappa Kid's trackie whip, the Razor Kid's scooter, Frosted Tips' spin and knee slide,
Scrunchie's boomerang 3310, the Garage MC's sound waves, the Builder's barge and bar stools, the Old Boy's walking-stick
hook, the Pool Shark's break, Moschino's champagne, the Raver's whistle). Run from the repo root: python3 tools/v76_build.py.
Safe to run again.

- Runs tools/v74_build.py first (which re-runs v73_build.py, so the chapter's waves in tools/v73/orp2001.js are current).
- The crowd's code, tools/v76/crowd.js, goes in after the chapter's, between `// V76 js start` and `// V76 js end`.
- Sprite sheets: web/sprites/<key>.png from tools/v76/foe_sheets.py; their SPRITE_META / FOE_FRAMES entries come from
  tools/v76/sheets.json and go in between `/* ORP2 meta */` markers.
- Two small additions to the sprite code: a state can loop a run of a row's frames (F.loop: the scooter ride, the MC on
  the mic), and a state can be drawn leaning forward (F.lean: the barge).
- Props: tools/v76/props.py (the scooter, the bar stool, the 3310)."""
import json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, 'web', 'index.html')
subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'v74_build.py')], check=True)
read = lambda p: open(p, encoding='utf-8').read()
s = read(PAGE)

# the crowd's code, straight after the chapter's
start, end = '// V76 js start', '// V76 js end'
if start in s: a = s.index(start); b = s.index(end) + len(end) + 1; s = s[:a] + s[b:]
anchor = '// V72 js end\n'
if s.count(anchor) != 1: sys.exit('v76_build: could not find the end of the chapter code')
s = s.replace(anchor, anchor + start + '\n' + read(os.path.join(ROOT, 'tools', 'v76', 'crowd.js')).rstrip('\n') + '\n' + end + '\n')

# the sheets
sheets = json.load(open(os.path.join(ROOT, 'tools', 'v76', 'sheets.json')))
s = re.sub(r'/\* ORP2 meta \*/.*?/\* ORP2 meta end \*/', '', s, flags=re.S)
s = re.sub(r'  // ORP2 frames\n.*?  // ORP2 frames end\n', '', s, flags=re.S)
metas = ','.join(json.dumps(k) + ':' + json.dumps(v['meta'], separators=(',', ':')) for k, v in sheets.items())
frames = '\n'.join('  ' + k + ': ' + v['frames'] + ',' for k, v in sheets.items())
s = s.replace('const SPRITE_META = {', 'const SPRITE_META = {/* ORP2 meta */' + metas + ',/* ORP2 meta end */', 1)
s = s.replace('const FOE_FRAMES = {\n', 'const FOE_FRAMES = {\n  // ORP2 frames\n' + frames + '\n  // ORP2 frames end\n', 1)

SWAPS = [
    ('frame loops', "  const wRow = (F.wind && F.wind[st]) || FOE_WIND[st], hRow = (F.hits && F.hits[st]) || FOE_HIT[st];\n",
     "  if (F.loop && F.loop[st] && has(F.loop[st][0])) { const [r, fr] = F.loop[st]; return [r, fr[Math.floor(t * 10) % fr.length]]; }   // Version 76\n"
     "  const wRow = (F.wind && F.wind[st]) || FOE_WIND[st], hRow = (F.hits && F.hits[st]) || FOE_HIT[st];\n"),
    ('lean', "  if (st === 'dash') ctx.rotate(0.12);\n",
     "  if (st === 'dash') ctx.rotate(0.12);\n  else if (isFoe && F.lean && F.lean[st]) ctx.rotate(F.lean[st]);   // Version 76: the barge\n"),
]
for label, old, new in SWAPS:
    if new in s: continue
    if s.count(old) != 1: sys.exit(f'v76_build: could not find the {label} (found {s.count(old)})')
    s = s.replace(old, new)
open(PAGE, 'w', encoding='utf-8').write(s)
print('v76_build: web/index.html updated (' + ', '.join(sheets) + ')')
