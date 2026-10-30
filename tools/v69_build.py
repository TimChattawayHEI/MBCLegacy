"""Version 69: joins, painted things that block the way, and real fire (Tim, 30 October). Patches web/index.html and
tools/v64/meshy_bg.js in place (run from the repo root): python3 tools/v69_build.py. Safe to run again. Like V66 to V68
it doesn't re-run the earlier build scripts.

- tools/v69/v69.js goes in between `// V69 js start` and `// V69 js end`, just after the Meshy backdrop code: the floor
  blocks for each stage (FLOOR_BLOCK) and the fire (realFire).
- physics() and the allies' movement check the floor blocks, so a painted wall end, open door, pillar or bench stops
  everyone instead of being walked through.
- The Espace burning on the dive bar's track (and in the drive when it crashes), Ramsden's wrecks and its bins burn
  with realFire instead of rows of the small looping flame sprite; the Espace's smoke is thin and drifts away.
- The train: each carriage draws its own walls so its end wall (tools/v69/tr_end.py) fits; the bus's grab poles are
  redrawn floor to ceiling (tools/v69/pole.py).
The new stage pictures (the joins) are made by tools/v64/meshy_bg.py from the patches listed in tools/v64/stages.json.
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, 'web', 'index.html')
MESHY_JS = os.path.join(ROOT, 'tools', 'v64', 'meshy_bg.js')
read = lambda p: open(p, encoding='utf-8').read()

SWAPS = [
    ('physics',
     "  e.x += e.vx * dt; e.y += e.vy * dt;\n  if (!noClamp) e.y = clamp(e.y, FT, FB);\n}",
     "  const px0 = e.x, py0 = e.y;   // Version 69: where it was, for the floor blocks\n  e.x += e.vx * dt; e.y += e.vy * dt;\n  if (!noClamp) { e.y = clamp(e.y, FT, FB); floorBlock(e, px0, py0); }\n}", 'page'),
    ('ally move',
     "    a.x += a.vx * dt; a.y = clamp(a.y + a.vy * dt, FT, FB);\n",
     "    { const ax = a.x, ay = a.y; a.x += a.vx * dt; a.y = clamp(a.y + a.vy * dt, FT, FB); floorBlock(a, ax, ay); }   // Version 69\n", 'page'),
    ('espace fire',
     "        for (let i = 0; i < 5; i++) drawFireSprite(x + 20 + i * (w - 40) / 4, b - img.height * 2 + 18 + (i % 2) * 8, wx + i);\n",
     "        realFire('espace', x + 24, b - img.height * 2 + 24, 94, 74, 1);   // Version 69: real fire along the roof\n", 'js'),
    ('espace smoke',
     "        for (let i = 0; i < 4; i++) { const k2 = (time * 0.35 + i / 4) % 1; pxCircle(x + w / 2 + Math.sin(k2 * 5 + i) * 16, b - img.height * 2 - k2 * 180, Math.round(12 + k2 * 34), 'rgba(40,36,36,' + (0.5 * (1 - k2)).toFixed(2) + ')'); } } } }\n",
     "        // Version 69: thin smoke rising off the top of the flames and drifting away, not dark balls\n        for (let i = 0; i < 7; i++) { const k2 = (time * 0.22 + i / 7) % 1; pxCircle(x + w / 2 + Math.sin(k2 * 4 + i) * 14 + (k2 - 0.5) * 60 + Math.sin(i * 2.3) * 40, b - img.height * 2 - 110 - k2 * 170, Math.round(10 + k2 * 30), 'rgba(80,72,74,' + (0.14 * (1 - k2) * Math.min(1, k2 * 5)).toFixed(3) + ')'); } } } }\n", 'js'),
    ('ramsden fire',
     "      for (let i = 0; i < 3; i++) drawFireSprite(x - 40 + i * 36, FT - 74 + (i % 2) * 8, wx + i); }\n",
     "      const rf = RAMS_FIRE[wx]; realFire('rams' + wx, x + rf[0] - rf[1], FT + rf[2], rf[1], 66, rf[3]); }   // Version 69: real fire\n", 'js'),
    ('ramsden bins',
     "  if (b.type === 'bin' && ST && ST.bg === 'ramsden') drawFlame(x, y - 70, 16, b.x);\n",
     "  if (b.type === 'bin' && ST && ST.bg === 'ramsden') realFire(b.fid || (b.fid = 'bin' + (++FIRE_N)), x - 20, y - 62, 20, 40, 0.8);   // Version 69: real fire\n", 'page'),
    ('drive crash fire',
     "    for (let i = 0; i < 6; i++) drawFireSprite(snap2(x - w / 2 + 30 + i * (w - 60) / 5), snap2(y - h + 30 + (i % 2) * 10), 9000 + i);\n",
     "    realFire('drive', x - w / 2 + 20, y - h + 34, Math.round((w - 40) / 2), 74, 1);   // Version 69: real fire\n", 'page'),
    ('train walls',
     "  for (let wx = Math.floor(cam.x / TRAIN.seg) * TRAIN.seg - TRAIN.seg; wx < cam.x + W + TRAIN.seg; wx += TRAIN.seg) nlPut('tr_wall', wx, FT + 6);\n",
     "  // Version 69: each carriage draws its own three wall sections from its front, so its end wall comes right after the\n"
     "  // third (the wall repeats every 640 and a carriage is 2048, so a running wall cut the end wall into a window)\n"
     "  for (let c = Math.max(0, Math.floor(cam.x / TRAIN.car) - 1); c * TRAIN.car < cam.x + W + TRAIN.car; c++) for (let k = 0; k < 3; k++) nlPut('tr_wall', c * TRAIN.car + k * TRAIN.seg, FT + 6);\n", 'page'),
]


def patch(path, kinds):
    s = read(path)
    for label, old, new, kind in SWAPS:
        if kind not in kinds or new in s:
            continue
        if s.count(old) != 1:
            sys.exit(f'v69_build: could not find the {label} in {os.path.relpath(path, ROOT)} (found {s.count(old)})')
        s = s.replace(old, new)
    if path == PAGE:
        start, end = '// V69 js start', '// V69 js end'
        block = start + '\n' + read(os.path.join(ROOT, 'tools', 'v69', 'v69.js')).rstrip('\n') + '\n' + end + '\n'
        if start in s:
            a = s.index(start); b = s.index(end) + len(end) + 1; s = s[:a] + block + s[b:]
        else:
            k = s.index('// V64 js end\n') + len('// V64 js end\n'); s = s[:k] + block + s[k:]
    open(path, 'w', encoding='utf-8').write(s)


patch(MESHY_JS, {'js'})
patch(PAGE, {'js', 'page'})
print('v69_build: web/index.html and tools/v64/meshy_bg.js updated')
