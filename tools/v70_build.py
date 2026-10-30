"""Version 70: more Meshy (Tim, 30 October: "start on all"). Patches web/index.html and tools/v64/meshy_bg.js in place
(run from the repo root): python3 tools/v70_build.py. Safe to run again; like V66 to V69 it doesn't re-run the earlier
build scripts. The art is cut by tools/v70/cut.py; the stage skies by tools/v64/meshy_bg.py ("parasky").

- tools/v70/v70.js goes in between `// V70 js start` and `// V70 js end`, after the V69 block.
- The sunny and sunset stages (Elba airport, the beach, the dive bar's track) draw their sky as a slower layer first.
- A foreground layer (station columns, lamps, railings, a trolley) at Charing Cross, Orpington station, the Frequency
  and the alley, drawn after the fighters.
- The train and the bus have Meshy ceilings and floors.
- The stage title, GAME OVER and win banners sit on a Meshy caption plate, with the game over and victory pictures
  behind those two.
- Darts is played on Meshy's pub wall and cabinet; the kiss game is in the Meshy Soundz flat.
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, 'web', 'index.html')
MESHY_JS = os.path.join(ROOT, 'tools', 'v64', 'meshy_bg.js')
read = lambda p: open(p, encoding='utf-8').read()

SWAPS = [
    ('meshy sky',
     "  for (let i = 0; i < files.length; i++) bgPut(bgImg(files[i]), i * MESHY_TILE * 2, H);\n",
     "  meshySky(k);   // Version 70: the sky drifts slower behind\n  for (let i = 0; i < files.length; i++) bgPut(bgImg(files[i]), i * MESHY_TILE * 2, H);\n", 'js'),
    ('train ceiling',
     "  // the carriage: walls with see-through windows, doors, the end wall and the toilets\n",
     "  nlTrainCeilFloor('ceil');   // Version 70: Meshy's carriage ceiling\n  // the carriage: walls with see-through windows, doors, the end wall and the toilets\n", 'page'),
    ('train floor',
     "  pxFloor(0, ST.len, '#2b2f3a', '#262a33', 36, 64, '#323744');\n",
     "  if (NLX.img('tr_floor')) nlTrainCeilFloor('floor'); else pxFloor(0, ST.len, '#2b2f3a', '#262a33', 36, 64, '#323744');   // Version 70\n", 'page'),
    ('bus ceiling',
     "  for (let wx = -40; wx < W + 640; wx += 640) nlPut('bus_deck', wx, FT + 6);\n",
     "  nlBusCeilFloor('ceil');   // Version 70: Meshy's bus ceiling\n  for (let wx = -40; wx < W + 640; wx += 640) nlPut('bus_deck', wx, FT + 6);\n", 'page'),
    ('bus floor',
     "  pxFloor(0, W, '#3a2c2e', '#33272a', 30, 60, '#42343a');\n",
     "  if (!nlBusCeilFloor('floor')) pxFloor(0, W, '#3a2c2e', '#33272a', 30, 60, '#42343a');   // Version 70\n", 'page'),
    ('foreground',
     "  else if (ST.bg === 'ramsden') { if (bgReady(RAM_FILES)) drawRamsdenForePixel(); }\n  nlDrawFore();\n",
     "  else if (ST.bg === 'ramsden') { if (bgReady(RAM_FILES)) drawRamsdenForePixel(); }\n  nlDrawFore();\n  drawFG();   // Version 70: the foreground layer\n", 'page'),
    ('banner plate',
     "  ctx.fillStyle = 'rgba(15,22,25,0.6)'; ctx.fillRect(0, y - 54, W, 104);\n  ctx.fillStyle = '#f2a23a'; ctx.fillRect(0, y - 54, W, 3); ctx.fillRect(0, y + 47, W, 3);\n",
     "  // Version 70: the game over and victory pictures behind those banners, and every banner on Meshy's caption plate\n"
     "  if (mode === 'over' || mode === 'win') { const pic = bgImg('screens/' + mode); if (pic) { ctx.save(); ctx.globalAlpha = a * Math.min(1, modeT / 0.8); ctx.imageSmoothingEnabled = false; ctx.drawImage(pic, 0, 0, W, H); ctx.fillStyle = 'rgba(8,10,14,0.3)'; ctx.fillRect(0, 0, W, H); ctx.restore(); } }\n"
     "  const plate = bgImg('hud/banner');\n"
     "  if (plate) { ctx.save(); ctx.imageSmoothingEnabled = false; ctx.drawImage(plate, 0, y - 60, W, 112); ctx.restore(); }\n"
     "  else { ctx.fillStyle = 'rgba(15,22,25,0.6)'; ctx.fillRect(0, y - 54, W, 104); ctx.fillStyle = '#f2a23a'; ctx.fillRect(0, y - 54, W, 3); ctx.fillRect(0, y + 47, W, 3); }\n", 'page'),
    ('darts wall',
     "    const wall = bgImg('social/wall');\n    if (wall) {",
     "    const dwall = bgImg('mini/darts');   // Version 70: Meshy's pub wall and open cabinet, the board space under the board\n"
     "    if (dwall) { ctx.save(); ctx.imageSmoothingEnabled = false; ctx.drawImage(dwall, 0, 0, W, H); ctx.restore(); }\n"
     "    const wall = dwall ? null : bgImg('social/wall');\n    if (wall) {", 'page'),
    ('darts cabinet',
     "    ctx.fillStyle = '#5a3a22'; ctx.fillRect(DBX - 250, DBY - 230, 500, 470);",
     "    if (!dwall) { ctx.fillStyle = '#5a3a22'; ctx.fillRect(DBX - 250, DBY - 230, 500, 470); }\n    if (!dwall) {", 'page'),
    ('darts panels',
     "    ctx.fillStyle = '#1e4a28'; ctx.fillRect(DBX - 372, DBY - 222, 104, 454); ctx.fillRect(DBX + 268, DBY - 222, 104, 454);\n",
     "    ctx.fillStyle = '#1e4a28'; ctx.fillRect(DBX - 372, DBY - 222, 104, 454); ctx.fillRect(DBX + 268, DBY - 222, 104, 454); }\n", 'page'),
    ('kiss flat',
     "cam.x = s.camX; bgSoundzPixel(); }",
     "cam.x = s.camX; if (!meshyStage('soundz')) bgSoundzPixel(); }   /* Version 70: the Meshy flat */", 'page'),
]


def patch(path, kinds):
    s = read(path)
    for label, old, new, kind in SWAPS:
        if kind not in kinds or new in s:
            continue
        if s.count(old) != 1:
            sys.exit(f'v70_build: could not find the {label} in {os.path.relpath(path, ROOT)} (found {s.count(old)})')
        s = s.replace(old, new)
    if path == PAGE:
        start, end = '// V70 js start', '// V70 js end'
        block = start + '\n' + read(os.path.join(ROOT, 'tools', 'v70', 'v70.js')).rstrip('\n') + '\n' + end + '\n'
        if start in s:
            a = s.index(start); b = s.index(end) + len(end) + 1; s = s[:a] + block + s[b:]
        else:
            k = s.index('// V69 js end\n') + len('// V69 js end\n'); s = s[:k] + block + s[k:]
    open(path, 'w', encoding='utf-8').write(s)


patch(MESHY_JS, {'js'})
patch(PAGE, {'js', 'page'})
print('v70_build: web/index.html and tools/v64/meshy_bg.js updated')
