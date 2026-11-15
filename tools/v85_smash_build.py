"""Version 85: things to smash. python3 tools/v85_smash_build.py (re-runnable; patches web/index.html in place).
Code: tools/v85/smash.js, between `// V85 smash start` and `// V85 smash end`, after the hit effects. Art: the PixelLab
props in tools/v85/smash_src (whole, _d damaged, _w wrecked; the old bin, keg, cool box and suitcase keep their whole
sprite) are copied to web/bg/props. Hooks: drawBreakable (the damaged look and the new props), hitBreakable (colours,
the wreck and the pop), the floor layer of drawWorld (wrecks, popping items), the two resets, the stage lists."""
import os, shutil, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); PAGE = os.path.join(ROOT, 'web', 'index.html')
SRC, DST = os.path.join(ROOT, 'tools', 'v85', 'smash_src'), os.path.join(ROOT, 'web', 'bg', 'props')
for f in sorted(os.listdir(SRC)):
    if f.endswith('.png'): shutil.copyfile(os.path.join(SRC, f), os.path.join(DST, f))
s = open(PAGE, encoding='utf-8').read()
start, end = '// V85 smash start', '// V85 smash end'
if start in s: a = s.index(start); b = s.index(end) + len(end) + 1; s = s[:a] + s[b:]
anchor = '// V85 hitfx end\n'
assert s.count(anchor) == 1
s = s.replace(anchor, anchor + start + '\n' + open(os.path.join(ROOT, 'tools', 'v85', 'smash.js'), encoding='utf-8').read().rstrip('\n') + '\n' + end + '\n')
SWAPS = [
    ("  drawBinSprite(x, y, b.flash > 0, b.type === 'bin' ? null : b.type);\n",
     "  if (!smashDraw(b, x, y)) drawBinSprite(x, y, b.flash > 0, b.type === 'bin' ? null : b.type);   // Version 85\n"),
    ("    const col = b.type === 'coolbox' ? '#e9eef0' : b.type === 'keg' ? '#a8adb2' : b.type === 'luggage' ? '#6a4630' : '#8a9096';   // Version 64\n",
     "    const col = smashCol(b.type), n0 = items.length;   // Version 64, 85\n"),
    ("    if (b.drop) { if (b.drop.startsWith('w:')) dropItemWeapon(b.drop.slice(2), b.x, b.y + 4); else dropFood(b.drop, b.x, b.y + 4); }\n",
     "    if (b.drop) { if (b.drop.startsWith('w:')) dropItemWeapon(b.drop.slice(2), b.x, b.y + 4); else dropFood(b.drop, b.x, b.y + 4); }\n    smashBreak(b, n0);   // Version 85\n"),
    ("  for (const it of items) drawItem(it);\n  for (const h of hazards) if (h.kind !== 'moped') drawHazardFloor(h);\n",
     "  smashWrecksDraw();   // Version 85\n  for (const it of items) smashItem(it);\n  for (const h of hazards) if (h.kind !== 'moped') drawHazardFloor(h);\n"),
    ("  for (const b of breakables) list.push({ y: b.y, f: () => drawBreakable(b) });\n",
     "  for (const b of breakables) list.push({ y: b.y, f: () => drawBreakable(b) });\n  smashWrecksList(list);   // Version 85\n"),
    ("items.length = 0; breakables.length = 0; S.npcs = [];", "items.length = 0; breakables.length = 0; smashWrecks.length = 0; S.npcs = [];"),
    ("  (sc.breakables || []).forEach(b => breakables.push({ ...b, hp: 3, flash: 0, half: 22 }));",
     "  (sc.breakables || []).forEach(b => breakables.push({ ...b, hp: 3, flash: 0, half: smashHalf(b.type) }));"),
    ("items = []; breakables = []; timers.length = 0;", "items = []; breakables = []; smashWrecks = []; timers.length = 0;"),
    ("  (ST.breakables || []).forEach(b => breakables.push({ ...b, hp: 3, flash: 0, half: 22 }));",
     "  (ST.breakables || []).forEach(b => breakables.push({ ...b, hp: 3, flash: 0, half: smashHalf(b.type) }));"),
]
# new props, put in front of each stage's own list (found by its first breakable, which is unique)
ADD = [
    ("breakables: [{ type: 'bin', x: 1000, y: 476,", "{ type: 'phonebox', x: 2350, y: 430, drop: 'chips' }, { type: 'aboard', x: 2650, y: 480, drop: 'chips' }"),   # The Frequency
    ("breakables: [{ type: 'keg', x: 1150, y: 480,", "{ type: 'crate', x: 1750, y: 470, drop: 'chips' }"),   # Soundz FM
    ("breakables: [{ type: 'coolbox', x: 1520, y: 400,", "{ type: 'crate', x: 2000, y: 460, drop: 'bacon' }"),   # The Arrangement
    ("breakables: [{ type: 'keg', x: 1120, y: 484,", "{ type: 'pubtable', x: 1650, y: 470, drop: 'w:guinness' }"),   # The Social
    ("breakables: [{ type: 'coolbox', x: 1260, y: 470,", "{ type: 'deckchair', x: 1850, y: 450, drop: 'bacon' }"),   # Peg Nine
    ("breakables: [{ type: 'bin', x: 1260, y: 476,", "{ type: 'trolley', x: 1900, y: 470, drop: 'pizza' }, { type: 'vending', x: 3000, y: 420, drop: 'w:alcopop' }"),   # Arrivals
    ("breakables: [{ type: 'keg', x: 1100, y: 480,", "{ type: 'pubtable', x: 2300, y: 470, drop: 'w:alcopop' }"),   # The Dive Bar
    ("breakables: [{ type: 'coolbox', x: 1200, y: 480,", "{ type: 'deckchair', x: 1800, y: 450, drop: 'gelato' }, { type: 'deckchair', x: 3200, y: 480, drop: 'pizza' }"),   # La Spiaggia
    ("breakables: [{ type: 'keg', x: 1250, y: 480,", "{ type: 'pubtable', x: 1850, y: 460, drop: 'w:alcopop' }"),   # The Club
    ("breakables: [{ type: 'bin', x: 1300, y: 470, drop: 'kebab' },", "{ type: 'trolley', x: 1800, y: 460, drop: 'kebab' }"),   # Ramsden
    ("breakables: [{ type: 'bin', x: 1180, y: 476,", "{ type: 'vending', x: 1500, y: 420, drop: 'chips' }, { type: 'aboard', x: 2700, y: 480, drop: 'chips' }"),   # Orpington Station
    ("breakables: [{ type: 'bin', x: 1300, y: 470, drop: 'chips' },", "{ type: 'phonebox', x: 1800, y: 420, drop: 'kebab' }, { type: 'vending', x: 2850, y: 430, drop: 'w:alcopop' }"),   # Charing Cross
    ("breakables: [{ type: 'keg', x: 980, y: 480,", "{ type: 'crate', x: 1600, y: 470, drop: 'kebab' }, { type: 'trolley', x: 2600, y: 460, drop: 'w:alcopop' }"),   # The Smoking Area
    ("breakables: [{ type: 'keg', x: 640, y: 484,", "{ type: 'pubtable', x: 420, y: 480, drop: 'chips' }"),   # the pub lounge
    ("breakables: [{ type: 'keg', x: 140, y: 484,", "{ type: 'pubtable', x: 760, y: 470, drop: 'w:guinness' }"),   # the pub bar
]
for old, new in SWAPS:
    if new in s: continue
    assert s.count(old) == 1, old[:70]
    s = s.replace(old, new)
for key, extra in ADD:
    done = 'breakables: [' + extra + ', ' + key[len('breakables: ['):]
    if done in s: continue
    assert s.count(key) == 1, key
    s = s.replace(key, done)
open(PAGE, 'w', encoding='utf-8').write(s); print('v85 smash: patched')
