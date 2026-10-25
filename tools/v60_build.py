"""Version 60: painted floors.

Patches web/index.html in place (run from the repo root, after tools/v59_build.py):  python3 tools/v60_build.py
Safe to run again; it re-runs v59_build.py first. The code is tools/v60/floor.js, put in whole between
`// FLOOR js start` and `// FLOOR js end` (after the kebab shop's block). The pictures are web/bg/floors/, made by
tools/v60/floors.py from PixelLab's inpaints in tools/v60/img/.

Every walking stage's floor was a flat colour with drawn lines, which cut the painted backdrops off at the wall. Now
each one is painted down from its own backdrop and repeats along the stage with no join: The Frequency (pavement,
underpass, park), Soundz FM (carpet, corridor, roof), the airport (apron, taxi rank), the dive bar (inside, the track),
the club's street, Orpington station (ticket hall, platform), Charing Cross, the smoking area, the fishery (car park, the
bank by day and at dawn) and Ramsden. Road markings, car park bays and the fire glow are still drawn on top. The airport
terminal's tiles and the club's dance floor stay as they were (they already sit right), as do the beach, train, bus,
road, boat and social. Until a picture has loaded, the old floor is drawn.
"""
import os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, 'web', 'index.html')
read = lambda p: open(p, encoding='utf-8').read()


def swap(s, old, new, label):
    if new in s:
        return s
    if s.count(old) != 1:
        sys.exit(f'v60_build: could not find the {label} (found {s.count(old)} matches)')
    return s.replace(old, new)


subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'v59_build.py')], check=True)
s = read(PAGE)

start, end = '// FLOOR js start', '// FLOOR js end'
block = start + '\n' + read(os.path.join(ROOT, 'tools', 'v60', 'floor.js')).rstrip('\n') + '\n' + end + '\n'
if start in s:
    a = s.index(start); b = s.index(end) + len(end) + 1
    s = s[:a] + block + s[b:]
else:
    s = swap(s, "// KB js end\n", "// KB js end\n" + block, 'floor module')

# Orpington station: the ticket hall, then the platform past the gates
s = swap(s, """  nlFloors([[0, NL_ST_GATE, '#4a4d5c', '#424553', 40, 80, '#545767'], [NL_ST_GATE, ST.len + W, '#3a3746', '#33303e', 40, 80, '#44404f']]);
  ctx.fillStyle = '#2c2a33'; ctx.fillRect(0, FT, W, 2);""",
         """  if (!floorAll([['st_hall', 0, NL_ST_GATE], ['st_plat', NL_ST_GATE, ST.len + W]])) {   // painted (Version 60)
  nlFloors([[0, NL_ST_GATE, '#4a4d5c', '#424553', 40, 80, '#545767'], [NL_ST_GATE, ST.len + W, '#3a3746', '#33303e', 40, 80, '#44404f']]);
  ctx.fillStyle = '#2c2a33'; ctx.fillRect(0, FT, W, 2); }""", 'station floor')
# Charing Cross
s = swap(s, """  nlFloors([[0, ST.len + W, '#5a5b6b', '#515262', 48, 96, '#646576']]);
  ctx.fillStyle = '#3a3846'; ctx.fillRect(0, FT, W, 2);""",
         """  if (!floorTex('cx', 0, ST.len + W)) {   // painted (Version 60)
  nlFloors([[0, ST.len + W, '#5a5b6b', '#515262', 48, 96, '#646576']]);
  ctx.fillStyle = '#3a3846'; ctx.fillRect(0, FT, W, 2); }""", 'charing cross floor')
# the smoking area
s = swap(s, """  pxFloor(0, ST.len + W, '#2c2a33', '#25232b', 32, 72, '#36343d');
  ctx.fillStyle = '#1c1a22'; ctx.fillRect(0, FT, W, 2);""",
         """  if (!floorTex('alley', 0, ST.len + W)) {   // painted (Version 60)
  pxFloor(0, ST.len + W, '#2c2a33', '#25232b', 32, 72, '#36343d');
  ctx.fillStyle = '#1c1a22'; ctx.fillRect(0, FT, W, 2); }""", 'alley floor')
# the fishery bank, by day (The Arrangement) and at dawn (Peg Nine)
s = swap(s, """  pxFloor(0, ST.len + 400, P.ground, null, 0, 0, P.speck);
  ctx.fillStyle = P.bankTop; ctx.fillRect(0, FT - 6, W, 6); ctx.fillStyle = P.bank; ctx.fillRect(0, FT, W, 4);""",
         """  const bankTex = floorTex(S.key === 'pegnine' ? 'peg' : 'bank', 0, ST.len + 400);   // painted (Version 60)
  if (!bankTex) pxFloor(0, ST.len + 400, P.ground, null, 0, 0, P.speck);
  ctx.fillStyle = P.bankTop; ctx.fillRect(0, FT - 6, W, 6); if (!bankTex) { ctx.fillStyle = P.bank; ctx.fillRect(0, FT, W, 4); }""", 'fishery floor')
# the fishery car park: painted tarmac under the bays (the strip is cached, so it's redrawn once the picture is in)
s = swap(s, """  ctx.fillStyle = '#56565c'; ctx.fillRect(a, 322, b - a, H - 322);
  ctx.fillStyle = '#4a4a50'; for (let i = 0; i < 40; i++)""",
         """  const parkTex = !!floorImg('carpark');   // painted (Version 60)
  ctx.fillStyle = '#56565c'; ctx.fillRect(a, 322, b - a, (parkTex ? FT : H) - 322);
  if (parkTex) floorTex('carpark', 0, 1000, camx, FT, wmax);
  ctx.fillStyle = '#4a4a50'; if (!parkTex) for (let i = 0; i < 40; i++)""", 'car park floor')
s = swap(s, """  if (!fshCarParkCv) {""", """  if (!fshCarParkCv || (!fshCarParkCv.tex && floorImg('carpark'))) {""", 'car park redraw')
s = swap(s, """    fshCarParkCv = c;""", """    fshCarParkCv = c; c.tex = !!floorImg('carpark');""", 'car park drawn with the picture')
# Ramsden: the road (the double yellows and the fire glow still go on top)
s = swap(s, """  pxFloor(0, ST.len + 400, '#30242a', null, 0, 0, ['#3a2a28', '#241a1e', '#40302c', '#1e1616']);""",
         """  if (!floorTex('ram', 0, ST.len + 400)) pxFloor(0, ST.len + 400, '#30242a', null, 0, 0, ['#3a2a28', '#241a1e', '#40302c', '#1e1616']);   // painted (Version 60)""", 'ramsden floor')
# The Frequency: the high street pavement, the underpass, the park
s = swap(s, """  pxFloor(0, 1500, '#5e5a64', '#4e4a54', 30, 60, ['#6a6670', '#4a4650', '#3e3a44']);
  pxFloor(1500, 2300, '#4a4a50', '#3e3e44', 44, 88, ['#58585e', '#3a3a40']);
  pxFloor(2300, 3400, '#26402a', null, 0, 0, ['#2e4c32', '#335a38', '#1e3422', '#3c6a40']);
  for (let y = FT + 28, k = 0; y < H; y += 28, k++) if (k % 2 === 0) fillZone(2300, 3400, y, Math.min(H, y + 28), 'rgba(60,110,64,0.22)');
  fillZone(0, 2300, FT, FT + 8, '#8a8690'); fillZone(0, 2300, FT + 8, FT + 10, '#4a4650');
  fillZone(2300, 3400, FT, FT + 4, '#1e3422');""",
         """  if (!floorAll([['freq_pave', 0, 1500], ['freq_under', 1500, 2300], ['freq_park', 2300, 3400]])) {   // painted (Version 60)
  pxFloor(0, 1500, '#5e5a64', '#4e4a54', 30, 60, ['#6a6670', '#4a4650', '#3e3a44']);
  pxFloor(1500, 2300, '#4a4a50', '#3e3e44', 44, 88, ['#58585e', '#3a3a40']);
  pxFloor(2300, 3400, '#26402a', null, 0, 0, ['#2e4c32', '#335a38', '#1e3422', '#3c6a40']);
  for (let y = FT + 28, k = 0; y < H; y += 28, k++) if (k % 2 === 0) fillZone(2300, 3400, y, Math.min(H, y + 28), 'rgba(60,110,64,0.22)');
  fillZone(0, 2300, FT, FT + 8, '#8a8690'); fillZone(0, 2300, FT + 8, FT + 10, '#4a4650');
  fillZone(2300, 3400, FT, FT + 4, '#1e3422'); }""", 'frequency floor')
# Soundz FM: the studio carpet, the corridor lino, the roof
s = swap(s, """  pxFloor(0, 1300, '#6a3a2a', null, 0, 0, ['#7a4632', '#5a3022', '#8a5038', '#4e2a1e']);
  pxChecker(1300, 2400, 44, '#52524f', '#3a3a38');
  pxFloor(2400, 3600, '#3a3634', null, 0, 0, ['#4a4542', '#2a2624', '#56504c', '#302c2a']);
  fillZone(0, 2400, FT, FT + 6, '#2a1e18');""",
         """  if (!floorAll([['sz_carpet', 0, 1300], ['sz_corr', 1300, 2400], ['sz_roof', 2400, 3600]])) {   // painted (Version 60)
  pxFloor(0, 1300, '#6a3a2a', null, 0, 0, ['#7a4632', '#5a3022', '#8a5038', '#4e2a1e']);
  pxChecker(1300, 2400, 44, '#52524f', '#3a3a38');
  pxFloor(2400, 3600, '#3a3634', null, 0, 0, ['#4a4542', '#2a2624', '#56504c', '#302c2a']);
  fillZone(0, 2400, FT, FT + 6, '#2a1e18'); }""", 'soundz floor')
# the airport apron (the taxi line still painted on) and the taxi rank (its kerb is in the picture)
s = swap(s, """  pxFloor(0, AIR_T0 + 40, '#8a8a90', null, 0, 0, ['#7a7a80', '#9a9aa0', '#848490']);""",
         """  if (!floorTex('air_apron', 0, AIR_T0 + 40)) pxFloor(0, AIR_T0 + 40, '#8a8a90', null, 0, 0, ['#7a7a80', '#9a9aa0', '#848490']);   // painted (Version 60)""", 'apron floor')
s = swap(s, """      ctx.fillStyle = '#6a6a70'; ctx.fillRect(a, FT, b - a, 6); } }""",
         """      if (!floorImg('air_apron')) { ctx.fillStyle = '#6a6a70'; ctx.fillRect(a, FT, b - a, 6); } } }""", 'apron edge')
s = swap(s, """    ctx.fillStyle = '#9a9aa2'; ctx.fillRect(a, FT, W - a, H - FT);
    ctx.fillStyle = '#c8c4b8'; ctx.fillRect(a, FT, W - a, 40); ctx.fillStyle = '#7a7a80'; ctx.fillRect(a, FT + 40, W - a, 4);""",
         """    if (!floorTex('air_rank', cx + a, cx + W)) {   // painted (Version 60)
    ctx.fillStyle = '#9a9aa2'; ctx.fillRect(a, FT, W - a, H - FT);
    ctx.fillStyle = '#c8c4b8'; ctx.fillRect(a, FT, W - a, 40); ctx.fillStyle = '#7a7a80'; ctx.fillRect(a, FT + 40, W - a, 4); }""", 'taxi rank floor')
# the dive bar: the gravel track outside, the tiles inside
s = swap(s, """    ctx.fillStyle = '#b8a888'; ctx.fillRect(a, FT, W - a, H - FT);
    const r = seeded(Math.floor(cx / 40) + 7);""",
         """    if (!floorTex('bar_out', cx + a, cx + W)) {   // painted (Version 60)
    ctx.fillStyle = '#b8a888'; ctx.fillRect(a, FT, W - a, H - FT);
    const r = seeded(Math.floor(cx / 40) + 7);""", 'track floor')
s = swap(s, """    ctx.fillStyle = '#5a8a3a'; ctx.fillRect(a, H - 30, W - a, 30); ctx.fillStyle = '#6a9a46'; for (let x = a; x < W; x += 8) ctx.fillRect(x, H - 34 - (x % 24 === 0 ? 4 : 0), 4, 6);""",
         """    ctx.fillStyle = '#5a8a3a'; ctx.fillRect(a, H - 30, W - a, 30); ctx.fillStyle = '#6a9a46'; for (let x = a; x < W; x += 8) ctx.fillRect(x, H - 34 - (x % 24 === 0 ? 4 : 0), 4, 6); }""", 'track floor end')
s = swap(s, """    ctx.fillStyle = '#9a5a3a'; ctx.fillRect(0, FT, W, H - FT);
    ctx.fillStyle = '#8a4a2e'; for (let wx = Math.floor(cx / 48) * 48; wx < cx + W; wx += 48) ctx.fillRect(Math.round((wx - cx) / 2) * 2, FT, 2, H - FT);
    for (let y = FT + 32; y < H; y += 32) ctx.fillRect(0, y, W, 2);
    for (let wx = Math.floor(cx / 96) * 96; wx < cx + W; wx += 96) { const x = Math.round((wx - cx) / 2) * 2; ctx.fillStyle = '#a8684a'; ctx.fillRect(x + 4, FT + 4, 40, 24); }""",
         """    if (!floorTex('bar_in', 0, BAR_DOOR)) {   // painted (Version 60)
    ctx.fillStyle = '#9a5a3a'; ctx.fillRect(0, FT, W, H - FT);
    ctx.fillStyle = '#8a4a2e'; for (let wx = Math.floor(cx / 48) * 48; wx < cx + W; wx += 48) ctx.fillRect(Math.round((wx - cx) / 2) * 2, FT, 2, H - FT);
    for (let y = FT + 32; y < H; y += 32) ctx.fillRect(0, y, W, 2);
    for (let wx = Math.floor(cx / 96) * 96; wx < cx + W; wx += 96) { const x = Math.round((wx - cx) / 2) * 2; ctx.fillStyle = '#a8684a'; ctx.fillRect(x + 4, FT + 4, 40, 24); } }""", 'bar floor')
# the club's street (the bay lines still painted on)
s = swap(s, """    ctx.fillStyle = '#2a2a32'; ctx.fillRect(a, FT, W - a, H - FT);""",
         """    if (!floorTex('club_out', cx + a, cx + W)) { ctx.fillStyle = '#2a2a32'; ctx.fillRect(a, FT, W - a, H - FT); }   // painted (Version 60)""", 'club street floor')

open(PAGE, 'w', encoding='utf-8').write(s)
print('v60_build: web/index.html updated')
