"""Version 55: the pub, its games, and their boards.

Patches web/index.html in place (run from the repo root, after tools/v54_build.py):  python3 tools/v55_build.py
Safe to run again. The art comes from tools/v55/art.py (run that first after changing anything in tools/v55/img or src).
Also edits tools/title3d/title3d.html and .js (a PUB button on the select screen) and re-runs tools/title3d_build.py.

- Points are the currency. Every stage banks what it earned onto your pub tab (shown on the points screen).
- THE LOCAL: a pub you walk round. The bar (a round between chapters on a run: +1 life; a pint from the menu: wobblier
  darts), the dartboard, the fruit machine, and four arcade cabinets. Between chapters on a run (offline) the lads go
  to the pub; it's also open from the select screen (PUB button, or N).
- Mini-games once per run, played by their own lad, then open in the pub: PENALTIES (Byron, after The Frequency),
  KISS CHASE (Seb, after Soundz FM), STAY AWAKE (Sam, after The Club), THE LONG DRIVE (Pearcy, after The Arrangement).
  Darts and the fruit machine are always on. Typing ARCADE on the select screen opens every cabinet.
- All-time boards for every game: Firebase `boards/<game>` in the app, the shared store on claude.ai, this device as a
  fallback. Top three on the chalkboard by each game, your best under it, the record holder's face on the cabinet,
  and the full board (top ten and the best for each lad) on JUMP.
"""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, 'web', 'index.html')
T3 = os.path.join(ROOT, 'tools', 'title3d')
read = lambda p: open(p, encoding='utf-8').read()


def swap(s, old, new, label):
    if new in s:
        return s
    if s.count(old) != 1:
        sys.exit(f'v55_build: could not find the {label} (found {s.count(old)} matches)')
    return s.replace(old, new)


# ---------------------------------------------------------------- the 3D select screen gets a PUB button
h = read(os.path.join(T3, 'title3d.html'))
h = swap(h, """          <button class="t3ghost" id="t3-board" type="button">High scores</button>""",
         """          <button class="t3ghost" id="t3-pub" type="button">Harvest Moon</button>
          <button class="t3ghost" id="t3-board" type="button">High scores</button>""", '3D pub button')
open(os.path.join(T3, 'title3d.html'), 'w', encoding='utf-8').write(h)
j = read(os.path.join(T3, 'title3d.js'))
j = swap(j, """  click('board', () => { sfx('page'); openBoard(null, 'select'); });""",
         """  click('board', () => { sfx('page'); openBoard(null, 'select'); });
  click('pub', () => pubFromSelect(chosen().id));   // Version 55""", '3D pub click')
j = swap(j, """    if (P('board')) { sfx('page'); openBoard(null, 'select'); return; }""",
         """    if (P('board')) { sfx('page'); openBoard(null, 'select'); return; }
    if (P('pub')) { pubFromSelect(chosen().id); return; }
    if (pubTyped()) toast('EVERY ARCADE CABINET IS OPEN');""", '3D pub key')
open(os.path.join(T3, 'title3d.js'), 'w', encoding='utf-8').write(j)
subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'title3d_build.py')], check=True)

s = read(PAGE)

# ---------------------------------------------------------------- the module
strips = json.load(open(os.path.join(ROOT, 'tools', 'v55', 'strips.json')))
mod = 'const PUB_STRIPS = ' + json.dumps(strips, separators=(',', ':')) + ';\n' + read(os.path.join(ROOT, 'tools', 'v55', 'pub.js'))
start, end = '// PUB js start', '// PUB js end'
block = start + '\n' + mod.rstrip('\n') + '\n' + end + '\n'
if start in s:
    a = s.index(start); b = s.index(end) + len(end) + 1
    s = s[:a] + block + s[b:]
else:
    s = swap(s, "window.__appBack = () => {\n", block + "window.__appBack = () => {\n", 'pub module')

# ---------------------------------------------------------------- keys, loop and screen
s = swap(s, """  if (e.pointerType === 'mouse' && !touchUI) return;
  if (mode !== 'play') return;""", """  if (e.pointerType === 'mouse' && !touchUI) return;
  if (mode !== 'play' && !pubStick()) return;   // the pub and its moving games use the stick too (Version 55.2)""", 'touch stick in the pub')
s = swap(s, """  if (!touchUI || mode !== 'play' || padOn()) return;""", """  if (!touchUI || (mode !== 'play' && !pubStick()) || padOn()) return;""", 'touch controls drawn in the pub')
s = swap(s, """    const on = touchHeld(b.id), ready = b.id === 'special' && player.meter >= 100;""", """    const on = touchHeld(b.id), ready = b.id === 'special' && mode === 'play' && !!player && player.meter >= 100;""", 'special ready outside a fight')
s = swap(s, """KeyB: 'board', KeyR: 'route', KeyT: 'diff', KeyP: 'pause' };""",
         """KeyB: 'board', KeyR: 'route', KeyT: 'diff', KeyP: 'pause', KeyN: 'pub' };""", 'pub key')
s = swap(s, """  if (mode === 'board') { updateBoard(); return true; }
  if (mode === 'name') return true;""",
         """  if (mode === 'board') { updateBoard(); return true; }
  if (mode === 'pub') { updatePub(dt); return true; }   // Version 55
  if (mode === 'mini') { updateMini(dt); return true; }
  if (mode === 'name') return true;""", 'step hooks')
s = swap(s, """  if (mode === 'board') { drawBoard(); return; }
  drawWorldPixel();""",
         """  if (mode === 'board') { drawBoard(); return; }
  if (mode === 'pub' || (mode === 'name' && pubNameCb && pubNameMode === 'pub')) { drawPub(); return; }   // Version 55
  if (mode === 'mini' || (mode === 'name' && pubNameCb)) { drawMini(); return; }
  drawWorldPixel();""", 'render hooks')
s = swap(s, """async function submitName(skip) {
  if (mode !== 'name') return;""", """async function submitName(skip) {
  if (mode !== 'name') return;
  if (pubNameHook(skip)) return;   // the pub boards borrow this form (Version 55)""", 'name form')
s = swap(s, """  if (mode === 'pause') { resumeGame(); return true; }
  return false;
};""", """  if (mode === 'pause') { resumeGame(); return true; }
  if (mode === 'pub') { if (PUB.view) PUB.view = null; else pubLeave(); return true; }   // Version 55
  if (mode === 'mini') { pressed.add('escape'); return true; }
  return false;
};""", 'app back button')
s = swap(s, """function updateSelect() {
  const n = PLAYABLE.length;""", """function updateSelect() {
  const n = PLAYABLE.length;
  if (pressed.has('pub')) { pubFromSelect(); return; }   // Version 55
  if (pubTyped()) showBanner('ARCADE OPEN', 'Every cabinet in the pub is on', 2.4);""", '2D select pub')

# ---------------------------------------------------------------- the run: bank each stage, games after their stages, the pub between chapters
s = swap(s, """  S.tally = true; addScore(total, true);""",
         """  S.tally = true; addScore(total, true);
  clearInfo.banked = pubBankStage();   // onto the pub tab (Version 55)""", 'bank on clear')
s = swap(s, """function startStageNow(key) {
  slowT = 0; finishFX = null;""", """function startStageNow(key) {
  slowT = 0; finishFX = null;
  if (run && run.banked == null) run.banked = run.score;   // a carried-on run has banked what it had (Version 55)""", 'bank start')
s = swap(s, """function gameOver() { if (!NET.on) clearSavedRun();""", """function gameOver() { pubBankStage(); if (!NET.on) clearSavedRun();""", 'bank on game over')
s = swap(s, """  run.winBonus = Math.round(run.lives * 10000 * D().score); addScore(run.winBonus, true);""",
         """  run.winBonus = Math.round(run.lives * 10000 * D().score); addScore(run.winBonus, true); pubBankStage();""", 'bank on win')
s = swap(s, """  if (done && clearInfo.lifeUp) textOut('EXTRA LIFE!', W / 2, yN + 6, '22px ' + DISPLAY, '#7fe07a', OUT, 5);""",
         """  if (done && clearInfo.lifeUp) textOut('EXTRA LIFE!', W / 2, yN + 6, '22px ' + DISPLAY, '#7fe07a', OUT, 5);
  if (done) pubClearLine(yN + (clearInfo.lifeUp ? 38 : 8));""", 'tab line')
s = swap(s, """function afterClear() {
  const key = run.route[run.idx];""", """function afterClear() { pubAfterClear(afterClearNow); }   // a mini-game first, if this stage has one (Version 55)
function afterClearNow() {
  const key = run.route[run.idx];""", 'after clear')
s = swap(s, """    openChat(CHATS[STAGES[nk].intro], () => startStage(nk), nk === 'ramsden'""",
         """    pubBetween(key, nk, () => openChat(CHATS[STAGES[nk].intro], () => startStage(nk), nk === 'ramsden'""", 'pub between chapters')
s = swap(s, """: 'HIDDEN STAGE') : null, STAGES[nk].era);
  } else {""", """: 'HIDDEN STAGE') : null, STAGES[nk].era));
  } else {""", 'pub between chapters close')

open(PAGE, 'w', encoding='utf-8').write(s)
print('v55_build: web/index.html updated')
