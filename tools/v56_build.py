"""Version 56: your name.

Patches web/index.html in place (run from the repo root, after tools/v55_build.py):  python3 tools/v56_build.py
Safe to run again. The code itself lives in tools/v55/pub.js (the "Version 56: your name" section), which v55_build.py
injects; this wires it into the rest of the game. Also edits tools/title3d/title3d.html and .js (a "You: NAME" button)
and re-runs title3d_build.py and v55_build.py.

- The first time you reach the select screen you pick a name (letters and numbers, 3 to 12). It's kept on the phone and
  used on every board and in the online lobby. In the app it's claimed in Firebase (players/<NAME>, with a secret key
  only that phone has), so nobody else can take it. Change it with the "You: NAME" button on the select screen.
- Every board has one row per player, their best, with the lad they used beside it: the pub games and the main high
  scores, which are now shared through Firebase in the app too (boards/runs).
- The end of a run saves your score under your name without asking.
"""
import os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, 'web', 'index.html')
T3 = os.path.join(ROOT, 'tools', 'title3d')
read = lambda p: open(p, encoding='utf-8').read()


def swap(s, old, new, label):
    if new in s:
        return s
    if s.count(old) != 1:
        sys.exit(f'v56_build: could not find the {label} (found {s.count(old)} matches)')
    return s.replace(old, new)


# ---------------------------------------------------------------- the 3D select screen: who you are
h = read(os.path.join(T3, 'title3d.html'))
h = swap(h, """          <button class="t3ghost" id="t3-pub" type="button">Harvest Moon</button>""",
         """          <button class="t3ghost" id="t3-me" type="button">You</button>
          <button class="t3ghost" id="t3-pub" type="button">Harvest Moon</button>""", '3D name button')
open(os.path.join(T3, 'title3d.html'), 'w', encoding='utf-8').write(h)
j = read(os.path.join(T3, 'title3d.js'))
j = swap(j, """  click('pub', () => pubFromSelect(chosen().id));   // Version 55""",
         """  click('pub', () => pubFromSelect(chosen().id));   // Version 55
  click('me', () => profileAsk(false));   // Version 56""", '3D name click')
j = swap(j, """    q('online').hidden = !netAvailable();""", """    q('online').hidden = !netAvailable();
    profileFoot();""", '3D name label')
open(os.path.join(T3, 'title3d.js'), 'w', encoding='utf-8').write(j)
subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'v55_build.py')], check=True)

s = read(PAGE)
# the name box sits over the 3D screens too
s = swap(s, """.overlay[hidden]{display:none!important}""", """.overlay[hidden]{display:none!important}
#nameOverlay{z-index:6}""", 'overlay above 3D')
# every frame: the first select screen asks for a name, and nothing moves while the box is open
s = swap(s, """  musicTick();
  if (mode === 'title') {""", """  musicTick();
  if (profileTick()) return true;   // Version 56
  if (mode === 'title') {""", 'name check')
s = swap(s, """  nameEls.form.addEventListener('submit', e => { e.preventDefault(); submitName(false); });
  nameEls.skip.addEventListener('click', () => submitName(true));
  nameEls.input.addEventListener('keydown', e => { if (e.key === 'Escape') { e.preventDefault(); submitName(true); } });""",
         """  // picking a name uses the same box (Version 56)
  nameEls.form.addEventListener('submit', e => { e.preventDefault(); if (!profileHook(false)) submitName(false); });
  nameEls.skip.addEventListener('click', () => { if (!profileHook(true)) submitName(true); });
  nameEls.input.addEventListener('keydown', e => { if (e.key === 'Escape') { e.preventDefault(); if (!profileHook(true)) submitName(true); } });""", 'name form')
# the end of a run saves under your name without asking
s = swap(s, """function openNameEntry() {
  mode = 'name'; modeT = 0;""", """function openNameEntry() {
  mode = 'name'; modeT = 0;
  if (PROFILE.name && run) { if (run.score <= 0) { openBoard(null, 'select'); return; } nameEls.input.value = PROFILE.name; submitName(false); return; }   // Version 56""", 'run score under your name')
# the main board: shared through Firebase in the app, one row each
s = swap(s, """async function boardInit() {
  try {""", """async function boardInit() {
  if (appFb()) { boardFbInit(); return; }   // the app shares it through Firebase (Version 56)
  try {""", 'main board in the app')
s = swap(s, """async function boardAdd(entry) {
  if (board.db && board.uid) {""", """async function boardAdd(entry) {
  if (board.fb) return boardFbAdd(entry);
  if (board.db && board.uid) {""", 'main board save in the app')
s = swap(s, """function boardList(all) {
  const seen = new Set(), out = [];
  for (const e of board.shared.concat(board.local)) { const s = sanitizeEntry(e); if (!s || seen.has(s.id)) continue; seen.add(s.id); out.push(s); }
  out.sort((a, b) => b.score - a.score);""", """function boardList(all) {
  // one row per player: their best run (Version 56)
  const best = {};
  for (const e of board.shared.concat(board.local)) { const s = sanitizeEntry(e); if (!s) continue; const b = best[s.name]; if (!b || s.score > b.score || (s.score === b.score && !s.local && b.local)) best[s.name] = s; }
  const out = Object.values(best);
  out.sort((a, b) => b.score - a.score);""", 'main board one row each')
s = swap(s, """board.mode === 'shared' ? 'Everyone who opens this link sees the same board.' : 'Scores are saved on this device.'""",
         """board.mode === 'shared' ? 'Everyone\\u2019s best run, one row each.' : 'Scores are saved on this device.'""", 'main board subtitle')
s = swap(s, """where === 'shared' ? 'Saved. Everyone who opens this link sees the same board.' : 'Saved on this device.'""",
         """where === 'shared' ? 'Saved under ' + PROFILE.name + '. Everyone sees the same board.' : 'Saved on this device.'""", 'main board saved line')
# the online lobby: names, and a name first
s = swap(s, """  const me = { here: true, lad: PLAYABLE[NL.lad].id, ready: NL.ready };""",
         """  const me = { here: true, lad: PLAYABLE[NL.lad].id, ready: NL.ready, name: PROFILE.name || '' };""", 'lobby name')
s = swap(s, """slot(W / 2 - 230, hostIsMe ? mine : them, 'PLAYER 1' + (hostIsMe ? ' (YOU)' : ''),""",
         """slot(W / 2 - 230, hostIsMe ? mine : them, lobbyName(hostIsMe, 1),""", 'lobby slot 1')
s = swap(s, """slot(W / 2 + 230, hostIsMe ? them : mine, 'PLAYER 2' + (hostIsMe ? '' : ' (YOU)'),""",
         """slot(W / 2 + 230, hostIsMe ? them : mine, lobbyName(!hostIsMe, 2),""", 'lobby slot 2')
s = swap(s, """function openNetLobby() {
""", """function openNetLobby() {
  if (!PROFILE.name) { profileAsk(false, openNetLobby); return; }   // Version 56
""", 'lobby needs a name')

open(PAGE, 'w', encoding='utf-8').write(s)
print('v56_build: web/index.html updated')
