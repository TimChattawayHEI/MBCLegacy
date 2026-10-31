"""Version 82: the menus redesigned (Tim picked design A from the mockups). Run from the repo root after the other builds:
python3 tools/v82_build.py. Safe to run again.

- A start menu between the title and the lads: CARRY ON (the saved run), NEW GAME, PLAY ONLINE, THE HARVEST MOON, then
  TROPHIES / SCORES / SETTINGS; your name and sound top right. Everything that was along the bottom of the select screens
  lives here now, and the bottom bar is gone.
- The select screens get a header (back, the steps 1 LAD / 2 STAGE / 3 GO, which tick themselves off, your name), the lad
  roster shows faces (a square framed on each lad's own card, tools/v82/faces.json, so Byron's big-headed card matches the
  rest), PLAY AS <LAD> on the card.
- Where to start: the chapters down the side, a picture each, NEW on Orpington 2001 until you've a rank there; the chapter's
  stages as picture cards; the stage you're on underneath with START HERE.
- 3 GO: difficulty as before; the language toggle moves to Settings.
- SETTINGS opens the pause screen's settings panel from the menu (mode 'pause' with menuSettings set; nothing behind it).
The 3D title and select code is patched in the page between `// T3 js start` and `// T3 js end` (tools/title3d_build.py
would undo later fixes, so this patches the page, like V66 to V71 did). CSS and HTML: tools/v82/menu.css, menu.html."""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, 'web', 'index.html')
HERE = os.path.join(ROOT, 'tools', 'v82')
read = lambda p: open(p, encoding='utf-8').read()
s = read(PAGE)


def put(s, start, end, content, anchor, before=True):
    full = start + '\n' + content.rstrip('\n') + '\n' + end
    if start in s: return re.sub(re.escape(start) + r'.*?' + re.escape(end), lambda m: full, s, count=1, flags=re.S)
    if s.count(anchor) != 1: sys.exit(f'v82_build: could not find {anchor[:50]!r}')
    return s.replace(anchor, (full + '\n' + anchor) if before else (anchor + '\n' + full))


s = put(s, '/* V82 css start */', '/* V82 css end */', read(os.path.join(HERE, 'menu.css')), '/* T3 css end */')
s = put(s, '      <!-- V82 html start -->', '      <!-- V82 html end -->', read(os.path.join(HERE, 'menu.html')), '      <div class="t3sel" id="t3-foot">')

FACE = json.load(open(os.path.join(HERE, 'faces.json')))
a, b = s.index('// T3 js start'), s.index('// T3 js end')
t3 = s[a:b]
# faces.json can change after a build (Version 83 repainted Byron and Kelly), so refresh the FACE line if it is already in
t3 = re.sub(r"  const FACE = \{[^\n]*\};\n", lambda m: "  const FACE = " + json.dumps(FACE, separators=(',', ':')) + ";\n", t3)
T3_SWAPS = [
    ('data', "  const DIFF_NOTE = {",
     "  // Version 82: faces for the roster (a square on each lad's card: x, y, size, card width, card height) and a picture for each stage\n"
     "  const FACE = " + json.dumps(FACE, separators=(',', ':')) + ";\n"
     "  const THUMB = { frequency: 'meshy/frequency_0', soundz: 'meshy/soundz_0', orp_street: 'orp/busstop', orp_pub: 'orp/bar', orp_atlantis: 'orp/floor', airport: 'meshy/airport_0',\n"
     "    road: 'meshy/road_loop', divebar: 'meshy/divebar_0', beach: 'meshy/beach_0', club: 'meshy/club_1', nl_station: 'meshy/nl_station_0', nl_train: 'nightlife/tr_wall',\n"
     "    nl_cx: 'meshy/nl_cx_0', nl_alley: 'meshy/nl_alley_0', nl_bus: 'nightlife/bus_deck', arrival: 'meshy/arrival_0', naval: 'meshy/naval_loop', social: 'meshy/social_0',\n"
     "    pegnine: 'meshy/pegnine_0', ramsden: 'meshy/ramsden_0' };\n"
     "  const CH_SUB = { '1999': 'The Frequency', orp2001: 'A night out', elba: 'The holiday', nightlife: 'Up town', carpdiem: 'The fishery', ramsden: 'Off the route' };\n"
     "  let menuSel = 0;\n"
     "  const DIFF_NOTE = {"),
    ('title to menu', "      const sr = savedRun();\n      if (sr && !ladLocked(PLAYABLE[sr.ci])) { li = Math.max(0, ORDER.indexOf(PLAYABLE[sr.ci].id)); setView('cont'); } else setView('lad');\n",
     "      menuSel = 0; setView('menu');   // Version 82: the start menu (the saved run is its first button)\n"),
    ('menu next', "    } else if (view === 'cont') carryOn();\n",
     "    } else if (view === 'cont') carryOn();\n    else if (view === 'menu') { const it = menuItems()[menuSel]; if (it) menuAct(it); }\n"),
    ('carry on', "  function carryOn() { if (!savedRun()) { setView('lad'); return; } sfx('start'); carry = true; setView('go'); }",
     "  function carryOn() { const sr = savedRun(); if (!sr) { setView('lad'); return; } li = Math.max(0, ORDER.indexOf(PLAYABLE[sr.ci].id)); sfx('start'); carry = true; setView('go'); }"),
    ('back', "    if (view === 'cont') { sfx('page'); mode = 'title'; modeT = 0; lastMode = 'title'; restart(true); return true; }\n    if (view === 'lad') { sfx('page'); mode = 'title'; modeT = 0; lastMode = 'title'; restart(true); }\n",
     "    if (view === 'cont' || view === 'menu') { sfx('page'); mode = 'title'; modeT = 0; lastMode = 'title'; restart(true); return true; }\n    if (view === 'lad') { sfx('page'); setView('menu'); }\n"),
    ('enter select', "    setView('lad');\n    selectPose();", "    menuSel = 0; setView('menu');\n    selectPose();"),
    ('menu lineup', "    if (v === 'lad' || v === 'cont') for (const o of lads)", "    if (v === 'menu') for (const o of lads) { o.gx = o.tx; o.gz = o.tz; }\n    if (v === 'lad' || v === 'cont') for (const o of lads)"),
    ('sync', "    on('crumbs', menu); on('foot', menu || view === 'cont'); on('cont', view === 'cont');\n    on('lad', view === 'lad'); on('roster', view === 'lad');\n    on('stages', view === 'stage'); on('info', view === 'stage'); on('diff', view === 'diff');\n",
     "    on('crumbs', menu); on('foot', false); on('cont', false);\n    on('menu', view === 'menu'); on('head', menu || view === 'menu');\n"
     "    on('lad', view === 'lad'); on('roster', view === 'lad');\n    on('stages', view === 'stage'); on('scards', view === 'stage'); on('info', view === 'stage'); on('diff', view === 'diff');\n"
     "    q('hback').classList.toggle('hide', view === 'menu'); q('hsound').classList.toggle('hide', view !== 'menu');\n"
     "    q('hbackl').textContent = view === 'stage' ? 'Lads' : view === 'diff' ? 'Stages' : 'Menu';\n"),
    ('crumbs', "    root.querySelectorAll('#t3-crumbs span').forEach(s => {\n      const steps = ['lad', 'stage', 'diff'], i = steps.indexOf(s.dataset.step), cur = steps.indexOf(view);\n      s.className = i === cur ? 'now' : i < cur ? 'done' : '';\n    });\n",
     "    { const steps = ['lad', 'stage', 'diff'], cur = steps.indexOf(view), f = FLAT[stageSel], c = CHAR_BY_ID[chosen().id];   // Version 82: done steps say what you picked\n"
     "      root.querySelectorAll('#t3-crumbs span').forEach(s => {\n        const i = steps.indexOf(s.dataset.step);\n        s.className = i === cur ? 'now' : i < cur ? 'done' : '';\n"
     "        s.textContent = i < cur ? '\\u2713 ' + (i === 0 ? c.name : STAGES[f.k].hidden ? 'HIDDEN' : 'STAGE ' + STAGES[f.k].n) : ['1 LAD', '2 STAGE', '3 GO'][i];\n      });\n"
     "      root.querySelectorAll('#t3-crumbs i').forEach((el, i) => el.classList.toggle('done', i < cur)); }\n"),
    ('render menu', "    if (view === 'cont') renderCont();\n  }", "    if (view === 'cont') renderCont();\n    if (view === 'menu') renderMenu();\n  }"),
    ('hint', "      lad: pad ?", "      menu: pad ? 'Stick to choose · HIT to go' : tch ? '' : '↑ ↓ choose · J go · Esc back to the title',\n      lad: pad ?"),
    ('foot chips', "    q('online').hidden = !netAvailable();\n",
     "    q('online').hidden = !netAvailable();\n"
     "    { const hs = q('hsound'); hs.classList.toggle('off', !settings.sound); hs.setAttribute('aria-pressed', String(!!settings.sound)); hs.setAttribute('aria-label', 'Sound ' + (settings.sound ? 'on' : 'off')); }\n"
     "    q('hmel').textContent = PROFILE.name || 'Pick a name';\n"),
    ('pick label', "q('pick').textContent = lk ? 'LOCKED' : 'PICK ' + c.name;", "q('pick').textContent = lk ? 'LOCKED' : 'PLAY AS ' + c.name;"),
    ('menu input', "    if (P('punch') || P('start')) { next(); return; }\n",
     "    if (P('punch') || P('start')) { next(); return; }\n    if (view === 'menu') { if (P('up') || P('left')) moveMenu(-1); if (P('down') || P('right')) moveMenu(1); return; }\n"),
    ('menu clicks', "  click('online', () => { if (netAvailable()) { sfx('page'); openNetLobby(); } });\n",
     "  click('online', () => { if (netAvailable()) { sfx('page'); openNetLobby(); } });\n"
     "  ['mcarry', 'mnew', 'monline', 'mpub', 'mtrophy', 'mboard', 'mset'].forEach(id => click(id, () => menuAct(id)));   // Version 82\n"
     "  click('hback', back);\n  click('hme', () => profileAsk(false));\n  click('hsound', toggleSound);\n"
     "  click('sgrid', e => { const b = e.target.closest('button'); if (!b || b.disabled) return; const f = +b.dataset.f; if (f === stageSel) next(); else { stageSel = f; sfx('swing'); renderStage(); } });\n"),
    ('menu camera', "  function selectPose() {\n    const L = chosen();\n",
     "  function selectPose() {\n    const L = chosen();\n    if (view === 'menu') { tgt.pos.set(-70, 58, 300); tgt.look.set(-70, 46, -330); tgt.fov = 50; return; }   // Version 82: the line-up, off to the right of the menu\n"),
    ('menu tint', "      const pick = L === chosen() && view !== 'title';\n      const tt = view === 'title' || view === 'go' ?",
     "      const pick = L === chosen() && view !== 'title' && view !== 'menu';\n      const tt = view === 'title' || view === 'go' || view === 'menu' ?"),
    ('menu logo', "      const g = view !== 'title' ? { x: -PW / 2 + 52, y: PH / 2 - 17, s: 0.36, ry: 0, rx: 0 } :",
     "      const g = view === 'menu' ? { x: -PW / 2 + 116, y: PH / 2 - 48, s: 0.86, ry: 0, rx: 0 } : view !== 'title' ? { x: -PW / 2 + 52, y: PH / 2 + 70, s: 0.36, ry: 0, rx: 0 } :"),
    ('menu functions', "  function toast(msg, cls) {",
     """  // ---------------------------------------------------------------- the start menu (Version 82)
  function menuItems() {
    const sr = savedRun(), carryOk = !!(sr && !ladLocked(PLAYABLE[sr.ci]));
    return ['mcarry', 'mnew', 'monline', 'mpub', 'mtrophy', 'mboard', 'mset'].filter(id => (id !== 'mcarry' || carryOk) && (id !== 'monline' || netAvailable()));
  }
  function menuAct(id) {
    audioInit();
    if (id === 'mcarry') carryOn();
    else if (id === 'mnew') { sfx('page'); setView('lad'); }
    else if (id === 'monline') { if (netAvailable()) { sfx('page'); openNetLobby(); } }
    else if (id === 'mpub') pubFromSelect(chosen().id);
    else if (id === 'mtrophy') trophyOpen('select');
    else if (id === 'mboard') { sfx('page'); openBoard(null, 'select'); }
    else if (id === 'mset') openMenuSettings();
  }
  function renderMenu() {
    const items = menuItems(), sr = savedRun();
    if (menuSel >= items.length) menuSel = 0;
    q('mcarry').hidden = !items.includes('mcarry'); q('monline').hidden = !items.includes('monline');
    q('mnew').classList.toggle('prim', !items.includes('mcarry'));
    if (sr && items.includes('mcarry')) { const st = STAGES[sr.route[sr.idx]], d = DIFFS[sr.diff] || DIFFS.normal; q('mcline').textContent = (st.hidden ? 'Hidden stage' : 'Stage ' + st.n) + ' \\u00b7 ' + st.title + ' \\u00b7 ' + PLAYABLE[sr.ci].name + ' \\u00b7 ' + d.label; }
    q('mtline').textContent = achCount() + ' / ' + ACH_LIST.length;
    const n = HUB.kind ? hubPeople().length : 0, u = chatUnread();
    q('mpline').textContent = n || u ? [n ? n + ' online' : '', u ? u + ' new' : ''].filter(Boolean).join(' \\u00b7 ') : 'The pub \\u00b7 mini-games';
    ['mcarry', 'mnew', 'monline', 'mpub', 'mtrophy', 'mboard', 'mset'].forEach(id => q(id).classList.toggle('sel', items[menuSel] === id && !touchUI));
    q('mtip').textContent = hint();
  }
  function moveMenu(d) { const n = menuItems().length; menuSel = (menuSel + d + n) % n; sfx('swing'); renderMenu(); }
  function toast(msg, cls) {"""),
]
for label, old, new in T3_SWAPS:
    if new in t3: continue
    if t3.count(old) != 1: sys.exit(f'v82_build: could not find the {label} in the 3D select code (found {t3.count(old)})')
    t3 = t3.replace(old, new)

# the roster with faces, and the stage screen as chapters + picture cards (whole lines swapped by pattern)
ROSTER = r"""    q('roster').innerHTML = ORDER.map((id, i) => { const lk2 = ladLocked(CHAR_BY_ID[id]), F = FACE[id] || [0, 0, 60, 110, 150];   // Version 82: faces
      const bs = (F[3] / F[2] * 100).toFixed(1) + '%', px = F[3] > F[2] ? (F[0] / (F[3] - F[2]) * 100).toFixed(1) + '%' : '50%', py = F[4] > F[2] ? (F[1] / (F[4] - F[2]) * 100).toFixed(1) + '%' : '0%';
      return `<button type="button" data-i="${i}" aria-pressed="${i === li}" aria-label="${lk2 ? 'Locked' : CHAR_BY_ID[id].name}"${lk2 ? ' class="lock"' : ''}><i style="background-image:url(bg/ladcard/${id}.png);background-size:${bs} auto;background-position:${px} ${py}"></i><span>${lk2 ? '???' : CHAR_BY_ID[id].name}</span></button>`; }).join('');
"""
if 'background-image:url(bg/ladcard/' not in t3:
    t3, n = re.subn(r"    q\('roster'\)\.innerHTML = ORDER\.map\(\(id, i\) => `<button.*?\n", lambda m: ROSTER, t3, count=1)
    if n != 1: sys.exit('v82_build: could not find the roster line')
STAGE = r"""  function renderStage() {
    const f = FLAT[stageSel], ch = CHAPS[f.ci], locked = stageLocked(), st = STAGES[f.k];
    const RK = typeof stageRanks === 'function' ? stageRanks() : {};   // best rank per stage (Version 49)
    // Version 82: the chapters down the side with a picture each, the chapter's stages as picture cards
    const span = c => { const ns = c.keys.map(k => STAGES[k].n).filter(Boolean); return c.hidden || !ns.length ? 'Bonus' : ns.length > 1 ? 'Stages ' + ns[0] + '–' + ns[ns.length - 1] : 'Stage ' + ns[0]; };
    q('tabs').innerHTML = CHAPS.map((c, i) => { const lk = c.hidden && !settings.unlocked, fresh = !lk && c.id === 'orp2001' && !c.keys.some(k => RK[k]);
      return `<button type="button" role="tab" data-c="${i}" aria-selected="${i === f.ci}"${lk ? ' class="lock"' : ''}><img src="bg/${THUMB[c.keys[0]] || 'meshy/frequency_0'}.png" alt=""><span class="cw"><span class="cn">${lk ? '? ? ?' : c.name}</span><span class="cs">${lk ? 'Hidden' : span(c) + ' · ' + (CH_SUB[c.id] || '')}</span></span>${fresh ? '<span class="new">NEW</span>' : ''}</button>`; }).join('');
    const n = ch.keys.length;
    q('sgrid').style.gridTemplateColumns = 'repeat(' + Math.max(n, 3) + ',minmax(0,1fr))'; q('sgrid').classList.toggle('small', n > 3);
    q('scap').textContent = locked ? ch.name : ch.name + ' · ' + span(ch);
    q('sgrid').innerHTML = ch.keys.map(k => {
      const fi = FLAT.findIndex(x => x.k === k), s = STAGES[k];
      return `<button type="button" data-f="${fi}" aria-pressed="${fi === stageSel}"${locked ? ' disabled' : ''}><span class="im" style="background-image:url(bg/${THUMB[k] || 'meshy/frequency_0'}.png)${locked ? ';filter:brightness(.1)' : ''}"></span><span class="tx"><span class="sn">${s.hidden ? 'HIDDEN STAGE' : 'STAGE ' + String(s.n).padStart(2, '0')}${!locked && RK[k] ? ` · <span class="rk">${RK[k]}</span>` : ''}</span><span class="st">${locked ? '? ? ?' : s.title}</span><span class="sb">${locked ? '' : BOSS[k] || ''}</span></span></button>`;
    }).join('');
    q('snum').textContent = locked ? ch.name : stageNo(f.k) + ' · ' + ch.name;
    q('stitle').textContent = locked ? '? ? ?' : st.title;
    q('ssub').textContent = locked ? 'Hidden. Find the way in.' : st.sub;
    q('sboss').innerHTML = locked ? '' : '<span class="t3cap">Boss</span> ' + BOSS[f.k];
    const r = routeFrom(startFor(f.k));
    q('snote').textContent = locked ? '' : r.length === 1 ? 'Just this stage.' : r.length + ' stages from here to the end of the run.';
    q('here').disabled = locked;
  }
"""
if 'Version 82: the chapters down the side' not in t3:
    t3, n = re.subn(r"  function renderStage\(\) \{.*?\n  \}\n(?=  function renderDiff)", lambda m: STAGE, t3, count=1, flags=re.S)
    if n != 1: sys.exit('v82_build: could not find renderStage')
s = s[:a] + t3 + s[b:]

# settings from the start menu: the pause screen's settings panel with nothing behind it and BACK TO MENU
SWAPS = [
    ('menu settings', "function openPause() {\n",
     "// Version 82: SETTINGS on the start menu opens the pause screen's settings panel on its own\n"
     "let menuSettings = false;\n"
     "function openMenuSettings() { menuSettings = true; mode = 'pause'; modeT = 0; pauseSel = 0; pauseTab = 'settings'; pauseFocus = 'right'; setSel = 0; pauseConfirm = false; restartConfirm = false; held.clear(); pointers.clear(); sfx('page'); }\n"
     "function closeMenuSettings() { menuSettings = false; mode = 'select'; modeT = 0; held.clear(); pointers.clear(); sfx('page'); }\n"
     "function openPause() {\n"),
    ('resume', "function resumeGame() { mode = 'play';", "function resumeGame() { if (menuSettings) { closeMenuSettings(); return; } mode = 'play';"),
    ('items', "function pauseItems() {\n", "function pauseItems() {\n  if (menuSettings) return [{ id: 'menuback', label: 'BACK TO MENU', x: 64, y: 150, w: 300, h: 44 }];   // Version 82\n"),
    ('act', "function pauseAct(id) {\n", "function pauseAct(id) {\n  if (id === 'menuback') { closeMenuSettings(); return; }\n"),
    ('render', "  drawWorldPixel();\n  if (!cutin) { drawHUD();", "  if (mode === 'pause' && menuSettings) { ctx.fillStyle = '#0d0f17'; ctx.fillRect(0, 0, W, H); drawPause(); return; }   // Version 82\n  drawWorldPixel();\n  if (!cutin) { drawHUD();"),
    ('title', "  textOut('PAUSED', 64, 96, '44px ' + DISPLAY, '#f2a23a', OUT, 7, 'left');", "  textOut(menuSettings ? 'SETTINGS' : 'PAUSED', 64, 96, '44px ' + DISPLAY, '#f2a23a', OUT, 7, 'left');"),
    ('no run', "  const x = 430, dd = DIFFS[run.diff] || DIFFS.normal;", "  const x = 430, dd = DIFFS[run && run.diff] || DIFFS.normal;"),
    ('name chip', "function profileFoot() { const b = document.getElementById('t3-me'); if (b) b.textContent = PROFILE.name ? 'You: ' + PROFILE.name : 'Pick a name';",
     "function profileFoot() { const b = document.getElementById('t3-me'); if (b) b.textContent = PROFILE.name ? 'You: ' + PROFILE.name : 'Pick a name'; const h = document.getElementById('t3-hmel'); if (h) h.textContent = PROFILE.name || 'Pick a name';"),
]
for label, old, new in SWAPS:
    if new in s: continue
    if s.count(old) != 1: sys.exit(f'v82_build: could not find the {label} (found {s.count(old)})')
    s = s.replace(old, new)
open(PAGE, 'w', encoding='utf-8').write(s)
print('v82_build: web/index.html updated')
