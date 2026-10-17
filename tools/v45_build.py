"""Version 45: quality of life.

Patches web/index.html in place (run from the repo root, after tools/title3d_build.py and tools/v44_build.py):
    python3 tools/v45_build.py
Safe to run again: each change is skipped if it is already there.

What it does
- Carry on a run: the run is saved as each stage starts (offline play only). If the app is closed or killed, the
  title offers CARRY ON (3D title) or a CARRY ON pill (2D select) and the run picks up at the start of that stage,
  with the score and lives it had then. Losing, winning or quitting a run clears it.
- Group chats: a SKIP button on touch screens, and the phone's back button skips the chat instead of closing the app.
- Vibration on the phone: getting hit, getting knocked down, landing a big hit, and firing a special. Can be turned off.
- Pause menu: RESTART STAGE (back to how the stage started), and a SETTINGS panel: music and effects volume, all
  sound, language, vibration, gentler screen shake, softer screen flashes, touch button size, see-through buttons
  and a left-handed layout (stick on the right).
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, 'web', 'index.html')
read = lambda p: open(p, encoding='utf-8').read()


def swap(s, old, new, label):
    if new in s:
        return s
    if s.count(old) != 1:
        sys.exit(f'v45_build: could not find the {label} (found {s.count(old)} matches)')
    return s.replace(old, new)


s = read(PAGE)

# ---------------------------------------------------------------- settings: new defaults, volumes, comfort, touch layout
s = swap(s, """const settings = Object.assign({ sweary: true, sound: true, unlocked: false, lastName: '', diff: 'normal' }, lsGet('carpdiem.settings', {}) || {});""",
         """const settings = Object.assign({ sweary: true, sound: true, unlocked: false, lastName: '', diff: 'normal',
  mus: 10, fx: 10, buzz: true, shake: 'full', flash: true, pad: 'm', ghost: false, lefty: false }, lsGet('carpdiem.settings', {}) || {});   // Version 45 adds the volumes, comfort and touch options""",
         'settings defaults')
s = swap(s, """  if (actx) { sfxBus.gain.value = settings.sound ? 1 : 0; musBus.gain.value = settings.sound ? 0.6 : 0; }""",
         """  if (actx) { sfxBus.gain.value = settings.sound ? (settings.fx ?? 10) / 10 : 0; musBus.gain.value = settings.sound ? 0.6 * (settings.mus ?? 10) / 10 : 0; }""",
         'volumes')
s = swap(s, """function addShake(v) { shake = Math.max(shake, reduceMotion ? v * 0.25 : v); }""",
         """function addShake(v) { shake = Math.max(shake, reduceMotion || settings.shake === 'less' ? v * 0.25 : v); }""", 'gentle shake')
s = swap(s, """  if (flashT > 0) { ctx.fillStyle = 'rgba(255,240,200,' + Math.min(0.85, flashT * 3).toFixed(3) + ')'; ctx.fillRect(0, 0, W, H); }""",
         """  if (flashT > 0) { ctx.fillStyle = 'rgba(255,240,200,' + (Math.min(0.85, flashT * 3) * (settings.flash === false ? 0.2 : 1)).toFixed(3) + ')'; ctx.fillRect(0, 0, W, H); }""",
         'soft flashes')

s = swap(s, """const STICK = { x: 130, y: 430, r: 70 };""", """const STICK = { x: 130, y: 430, r: 70 };
// touch layout options (Version 45): button size, and the stick on the right for left-handed players
const BTN0 = BTN.map(b => Object.assign({}, b)), STICK0 = Object.assign({}, STICK);
function applyTouchLayout() {
  const k = { s: 0.85, m: 1, l: 1.18 }[settings.pad] || 1, L = !!settings.lefty;
  BTN.forEach((b, i) => { const o = BTN0[i], x = W - (W - o.x) * k; b.x = L ? W - x : x; b.y = H - (H - o.y) * k; b.r = o.r * k; });
  STICK.r = STICK0.r * k; STICK.x = L ? W - STICK0.x : STICK0.x; STICK.y = H - (H - STICK0.y) * k;
}
applyTouchLayout();""", 'touch layout')
s = swap(s, """  if (!role && p.x < W * 0.5 && p.y > 120) role = 'stick';""",
         """  if (!role && (settings.lefty ? p.x > W * 0.5 : p.x < W * 0.5) && p.y > 120) role = 'stick';""", 'left-handed stick zone')
s = swap(s, """  if (!touchUI || mode !== 'play' || padOn()) return;
  ctx.save(); ctx.globalAlpha = 0.85;""", """  if (!touchUI || mode !== 'play' || padOn()) return;
  ctx.save(); ctx.globalAlpha = settings.ghost ? 0.4 : 0.85;""", 'see-through buttons')

# ---------------------------------------------------------------- vibration
s = swap(s, """function knockDown(t, dir, kb) {""", """// a short buzz on the phone for the local lad's big moments (Version 45); local only, never part of the shared game
let buzzT = 0;
const canBuzz = () => typeof navigator !== 'undefined' && typeof navigator.vibrate === 'function' && touchUI;
function isMine(p) { return NET.on ? p === PL[NET.me] : p === player; }
function buzz(ms) {
  if (!settings.buzz || !canBuzz()) return;
  const now = performance.now(); if (now < buzzT) return; buzzT = now + 70;
  try { navigator.vibrate(ms); } catch (e) { /* optional */ }
}
function knockDown(t, dir, kb) {""", 'vibration helper')
s = swap(s, """function hurtPlayer(p, k, dir, big) {
""", """function hurtPlayer(p, k, dir, big) {
  if (isMine(p)) buzz(big || k.kd ? 70 : 30);
""", 'buzz when hurt')
s = swap(s, """  if (a === player) { gainMeter(player, METER.hit, k);""", """  if (big && a && isMine(a) && t !== a) buzz(18);
  if (a === player) { gainMeter(player, METER.hit, k);""", 'buzz on a big hit')
s = swap(s, """function startSpecial(p) {
""", """function startSpecial(p) {
  if (isMine(p)) buzz(90);
""", 'buzz on a special')

# ---------------------------------------------------------------- carry on a run: saved at each stage start
s = swap(s, """function newRun(ci, start) {""", """// carry on a run after the app closes (Version 45): the run as it stood when this stage started
const RUN_SAVE = 'carpdiem.run';
let stageSnap = null;
function runData() { const r = Object.assign({}, run); delete r.c; return JSON.parse(JSON.stringify(r)); }
function savedRun() {
  const r = lsGet(RUN_SAVE, null);
  return r && r.v === 1 && PLAYABLE[r.ci] && Array.isArray(r.route) && STAGES[r.route[r.idx]] ? r : null;
}
function clearSavedRun() { stageSnap = null; try { window.localStorage.removeItem(RUN_SAVE); } catch (e) { /* storage optional */ } }
function savedRunLabel(r) { const st = STAGES[r.route[r.idx]]; return st.hidden ? 'HIDDEN STAGE' : 'STAGE ' + st.n; }
function restoreRun(r) {
  run = Object.assign(JSON.parse(JSON.stringify(r)), { c: PLAYABLE[r.ci] }); delete run.v; delete run.key; delete run.saved;
  sel = r.ci; player = makePlayer(run.c);
}
function continueRun() {
  const r = savedRun(); if (!r) return false;
  restoreRun(r);
  const key = run.route[run.idx];
  prefetchStageMusic(key);
  openChat(CHATS[STAGES[key].intro], () => startStage(key), 'CARRYING ON', STAGES[key].era);
  return true;
}
function restartStage() {
  if (!stageSnap) return;
  const snap = stageSnap;
  restoreRun(snap.run); held.clear(); pointers.clear(); pressed.clear();
  musicSet(null); startStage(snap.key);
}
function newRun(ci, start) {""", 'run save helpers')
s = swap(s, """  if (ST.drive) driveStart(); else setTimeout0(() => ladSay('start', 1, true), 2.2);
}""", """  if (ST.drive) driveStart(); else setTimeout0(() => ladSay('start', 1, true), 2.2);
  if (!NET.on && run) { const d = runData(); stageSnap = { key, run: d }; lsSet(RUN_SAVE, Object.assign({ v: 1, key, saved: Date.now() }, d)); }
}""", 'save at stage start')
s = swap(s, """function gameOver() { mode = 'over';""", """function gameOver() { if (!NET.on) clearSavedRun(); mode = 'over';""", 'clear save on game over')
s = swap(s, """function winGame() {
""", """function winGame() {
  if (!NET.on) clearSavedRun();
""", 'clear save on a win')

# the 2D select (no WebGL): a CARRY ON pill and the C key
s = swap(s, """  if (netAvailable()) pills.unshift({ id: 'online', cap: 'TWO PLAYERS', label: 'PLAY ONLINE', key: 'O', hot: true });""",
         """  if (netAvailable()) pills.unshift({ id: 'online', cap: 'TWO PLAYERS', label: 'PLAY ONLINE', key: 'O', hot: true });
  { const sr = savedRun(); if (sr) pills.unshift({ id: 'cont', cap: 'CARRY ON', label: savedRunLabel(sr) + '  ·  ' + PLAYABLE[sr.ci].name, key: 'C', hot: true }); }""", '2D carry on pill')
s = swap(s, """  else if (id === 'online') openNetLobby();""", """  else if (id === 'online') openNetLobby();
  else if (id === 'cont') { audioInit(); sfx('start'); continueRun(); }""", '2D carry on action')
s = swap(s, """  if (pressed.has('online') && netAvailable()) { toggleOption('online'); return; }""",
         """  if (pressed.has('online') && netAvailable()) { toggleOption('online'); return; }
  if (pressed.has('cont') && savedRun()) { toggleOption('cont'); return; }""", '2D carry on key')
s = swap(s, """    for (const p of pills) if (t.x > p.x && t.x < p.x + p.w && t.y > p.y && t.y < p.y + p.h) { toggleOption(p.id); used = true; }
    if (used) continue;""", """    for (const p of pills) if (t.x > p.x && t.x < p.x + p.w && t.y > p.y && t.y < p.y + p.h) { toggleOption(p.id); used = true; }
    if (mode !== 'select') return;
    if (used) continue;""", '2D pill tap leaves select')
s = swap(s, """KeyM: 'mute', KeyO: 'online',""", """KeyM: 'mute', KeyC: 'cont', KeyO: 'online',""", 'carry on key')

# ---------------------------------------------------------------- group chats: SKIP on touch, back button skips
s = swap(s, """function finishChat() {""", """// a SKIP button on touch screens (the portrait pad has JUMP to skip) (Version 45)
const CHAT_SKIP = { x: W - 118, y: 18, w: 100, h: 38 };
const chatSkipShown = () => touchUI && !padOn();
function skipChat() { while (chat.shown < chat.lines.length) revealChat(); finishChat(); }
function drawChatSkip() {
  if (!chat || !chatSkipShown()) return;
  const b = CHAT_SKIP;
  rrect(b.x, b.y, b.w, b.h, 10); ctx.fillStyle = 'rgba(24,36,42,0.92)'; ctx.fill(); ctx.strokeStyle = '#f2a23a'; ctx.lineWidth = 2; ctx.stroke();
  ctx.font = '15px ' + DISPLAY; ctx.fillStyle = '#ffd23f'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText('SKIP \\u203A', b.x + b.w / 2, b.y + b.h / 2 + 1);
}
function finishChat() {""", 'chat skip button')
s = swap(s, """function updateChat(dt) {
  chat.t += dt;""", """function updateChat(dt) {
  chat.t += dt;
  if (chatSkipShown() && modeT > 0.2 && taps.some(t => t.x > CHAT_SKIP.x - 8 && t.x < CHAT_SKIP.x + CHAT_SKIP.w + 8 && t.y > CHAT_SKIP.y - 8 && t.y < CHAT_SKIP.y + CHAT_SKIP.h + 8)) { sfx('page'); skipChat(); return; }""", 'chat skip tap')
s = swap(s, """  if (mode === 'chat') { drawChat(); drawStatic(); return; }""", """  if (mode === 'chat') { drawChat(); drawChatSkip(); drawStatic(); return; }""", 'chat skip draw')
s = swap(s, """  if (mode === 'loading') return true;   // the phone's back button never closes the app mid-load""",
         """  if (mode === 'loading') return true;   // the phone's back button never closes the app mid-load
  if (mode === 'chat' && chat) { skipChat(); return true; }   // and skips a group chat (Version 45)""", 'back button skips a chat')

# ---------------------------------------------------------------- pause menu: restart stage, and a settings panel
s = swap(s, """let pauseSel = 0, pauseTab = 'info', pauseConfirm = false,""", """let pauseFocus = 'left', setSel = 0, restartConfirm = false;
let pauseSel = 0, pauseTab = 'info', pauseConfirm = false,""", 'pause state')
if "{ id: 'restart', label:" not in s:
    s = re.sub(r"function pauseItems\(\) \{\n  const items = \[\n.*?\n  \];\n", lambda m: """function pauseItems() {
  const items = [
    { id: 'resume', label: 'RESUME' },
    { id: 'restart', label: restartConfirm ? 'SURE? START AGAIN' : 'RESTART STAGE' },
    { id: 'settings', label: 'SETTINGS' },
    { id: 'scores', label: pauseTab === 'scores' ? 'RUN INFO' : 'HIGH SCORES' },
    { id: 'quit', label: pauseConfirm ? 'SURE? YOUR RUN ENDS' : 'QUIT TO MENU' },
  ];
  if (!stageSnap) items.splice(1, 1);
""", s, count=1, flags=re.S)
if "{ id: 'restart', label:" not in s:
    sys.exit('v45_build: could not rewrite the pause items')
s = swap(s, """  mode = 'pause'; modeT = 0; pauseSel = 0; pauseTab = 'info'; pauseConfirm = false;""",
         """  mode = 'pause'; modeT = 0; pauseSel = 0; pauseTab = 'info'; pauseConfirm = false; restartConfirm = false; pauseFocus = 'left';""", 'pause open')

m = re.search(r"function pauseAct\(id\) \{\n.*?\n\}\nfunction updatePause\(\) \{\n.*?\n\}\n", s, re.S)
if not m:
    sys.exit('v45_build: could not find the pause actions')
if 'function setRows()' not in s:
    s = s.replace(m.group(0), """function pauseAct(id) {
  if (id !== 'quit') pauseConfirm = false;
  if (id !== 'restart') restartConfirm = false;
  if (id === 'resume') resumeGame();
  else if (id === 'restart') { if (!restartConfirm) { restartConfirm = true; sfx('page'); } else { restartConfirm = false; sfx('start'); restartStage(); } }
  else if (id === 'settings') { pauseTab = 'settings'; pauseFocus = 'right'; setSel = 0; sfx('page'); }
  else if (id === 'scores') { pauseTab = pauseTab === 'scores' ? 'info' : 'scores'; pauseFocus = 'left'; sfx('page'); }
  else if (id === 'quit') { if (!pauseConfirm) { pauseConfirm = true; sfx('page'); } else { pauseConfirm = false; clearSavedRun(); mode = 'select'; modeT = 0; banner = null; musicSet(null); } }
}
// the settings panel on the right of the pause screen (Version 45)
function setRows() {
  const rows = [
    { id: 'mus', label: 'MUSIC', vol: true },
    { id: 'fx', label: 'EFFECTS', vol: true },
    { id: 'sound', label: 'ALL SOUND', val: settings.sound ? 'ON' : 'OFF' },
    { id: 'lang', label: 'LANGUAGE', val: settings.sweary ? 'SWEARY' : 'FAMILY' },
    { id: 'buzz', label: 'VIBRATION', val: settings.buzz ? 'ON' : 'OFF', touch: true },
    { id: 'shake', label: 'SCREEN SHAKE', val: settings.shake === 'less' ? 'GENTLE' : 'FULL' },
    { id: 'flash', label: 'SCREEN FLASHES', val: settings.flash === false ? 'SOFT' : 'FULL' },
    { id: 'pad', label: 'BUTTON SIZE', val: ({ s: 'SMALL', m: 'MEDIUM', l: 'LARGE' })[settings.pad] || 'MEDIUM', touch: true },
    { id: 'ghost', label: 'BUTTONS', val: settings.ghost ? 'SEE-THROUGH' : 'SOLID', touch: true },
    { id: 'lefty', label: 'STICK', val: settings.lefty ? 'ON THE RIGHT' : 'ON THE LEFT', touch: true },
  ].filter(r => !r.touch || touchUI || (r.id === 'buzz' && canBuzz()));
  rows.forEach((r, i) => { r.x = 452; r.y = 112 + i * 34; r.w = 426; r.h = 30; r.vx = r.x + 196; });
  return rows;
}
function setAdj(id, d) {
  if (id === 'mus' || id === 'fx') { settings[id] = clamp((settings[id] ?? 10) + d, 0, 10); applySound(); if (id === 'fx') sfx('hit'); }
  else if (id === 'sound') { settings.sound = !settings.sound; applySound(); }
  else if (id === 'lang') settings.sweary = !settings.sweary;
  else if (id === 'buzz') { settings.buzz = !settings.buzz; if (settings.buzz) { buzzT = 0; buzz(40); } }
  else if (id === 'shake') settings.shake = settings.shake === 'less' ? 'full' : 'less';
  else if (id === 'flash') settings.flash = settings.flash === false;
  else if (id === 'pad') { const o = ['s', 'm', 'l'], i = o.indexOf(settings.pad); settings.pad = o[clamp((i < 0 ? 1 : i) + d, 0, 2)]; applyTouchLayout(); }
  else if (id === 'ghost') settings.ghost = !settings.ghost;
  else if (id === 'lefty') { settings.lefty = !settings.lefty; applyTouchLayout(); }
  saveSettings();
  if (id !== 'fx') sfx('swing');
}
function drawPauseSettings(x) {
  const rows = setRows();
  ctx.font = '800 12px ' + BODY; ctx.fillStyle = '#f2a23a'; ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; ctx.fillText('SETTINGS', x + 22, 96);
  rows.forEach((r, i) => {
    const on = pauseFocus === 'right' && i === setSel;
    if (on) { rrect(r.x - 8, r.y, r.w, r.h, 6); ctx.fillStyle = 'rgba(242,162,58,0.16)'; ctx.fill(); ctx.strokeStyle = '#f2a23a'; ctx.lineWidth = 2; ctx.stroke(); }
    ctx.font = '800 12px ' + BODY; ctx.fillStyle = on ? '#ffd23f' : '#93a3a1'; ctx.textAlign = 'left'; ctx.fillText(r.label, r.x + 6, r.y + r.h / 2 + 1);
    if (r.vol) {
      const v = settings[r.id] ?? 10, off = !settings.sound;
      ctx.font = '15px ' + DISPLAY; ctx.fillStyle = '#efe6d2'; ctx.fillText('\\u2039', r.vx, r.y + r.h / 2 + 1); ctx.fillText('\\u203A', r.vx + 196, r.y + r.h / 2 + 1);
      for (let k = 0; k < 10; k++) { ctx.fillStyle = k < v ? (off ? '#5d6a6c' : '#f2a23a') : '#2b3b42'; ctx.fillRect(r.vx + 18 + k * 17, r.y + 9, 13, 12); }
    } else {
      ctx.font = '14px ' + DISPLAY; ctx.fillStyle = '#efe6d2'; ctx.fillText(r.val, r.vx, r.y + r.h / 2 + 1);
    }
  });
}
function updatePause() {
  if (NET.on) { if (modeT > 0.15 && ['pause', 'escape', 'start', 'punch'].some(a => pressed.has(a))) resumeGame(); return; }
  const its = pauseItems();
  if (pauseSel >= its.length) pauseSel = its.length - 1;
  const rows = pauseTab === 'settings' ? setRows() : [];
  if (setSel >= rows.length) setSel = Math.max(0, rows.length - 1);
  if (pauseFocus === 'right' && rows.length) {
    if (modeT > 0.15 && (pressed.has('pause') || pressed.has('escape') || pressed.has('back') || pressed.has('jump'))) { pauseFocus = 'left'; sfx('page'); }
    else {
      if (pressed.has('up')) { setSel = (setSel + rows.length - 1) % rows.length; sfx('swing'); }
      if (pressed.has('down')) { setSel = (setSel + 1) % rows.length; sfx('swing'); }
      const r = rows[setSel];
      if (pressed.has('left')) setAdj(r.id, -1);
      if (pressed.has('right')) setAdj(r.id, 1);
      if (pressed.has('punch') || pressed.has('start')) setAdj(r.id, r.vol && (settings[r.id] ?? 10) >= 10 ? -10 : 1);
    }
  } else {
    if (modeT > 0.15 && (pressed.has('pause') || pressed.has('escape'))) { resumeGame(); return; }
    if (pressed.has('up')) { pauseSel = (pauseSel + its.length - 1) % its.length; pauseConfirm = false; restartConfirm = false; sfx('swing'); }
    if (pressed.has('down')) { pauseSel = (pauseSel + 1) % its.length; pauseConfirm = false; restartConfirm = false; sfx('swing'); }
    if (pauseTab === 'settings' && pressed.has('right')) { pauseFocus = 'right'; sfx('swing'); }
    else if (pressed.has('punch') || pressed.has('start')) pauseAct(its[pauseSel].id);
  }
  for (const t of taps) {
    for (let i = 0; i < its.length; i++) { const it = its[i]; if (t.x > it.x && t.x < it.x + it.w && t.y > it.y && t.y < it.y + it.h) { pauseSel = i; pauseAct(it.id); } }
    if (mode !== 'pause') return;
    rows.forEach((r, i) => {
      if (t.x < r.x - 8 || t.x > r.x + r.w || t.y < r.y - 3 || t.y > r.y + r.h + 3) return;
      pauseFocus = 'right'; setSel = i;
      if (r.vol) { if (t.x >= r.vx - 10) setAdj(r.id, t.x < r.vx + 98 ? -1 : 1); }
      else setAdj(r.id, 1);
    });
  }
}
""")

s = swap(s, """  if (pauseTab === 'scores') { drawPauseScores(x, dd); return; }""",
         """  if (pauseTab === 'scores') { drawPauseScores(x, dd); return; }
  if (pauseTab === 'settings') { drawPauseSettings(x); return; }""", 'pause settings panel')
s = swap(s, """  ctx.fillText(touchUI ? 'Tap an option.' : 'Arrows and J to pick. P or Esc to carry on.', 64, 448);""",
         """  ctx.fillText(touchUI ? (pauseTab === 'settings' ? 'Tap a setting to change it.' : 'Tap an option.') : pauseTab === 'settings' ? (pauseFocus === 'right' ? '\\u2191 \\u2193 pick, \\u2190 \\u2192 change, Esc back.' : '\\u2192 into settings. P or Esc to carry on.') : 'Arrows and J to pick. P or Esc to carry on.', 64, 448);""",
         'pause hint')

open(PAGE, 'w', encoding='utf-8').write(s)
print('v45_build: web/index.html updated')
