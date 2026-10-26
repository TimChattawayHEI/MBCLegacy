// ================================================================== Version 61: quality of life
// 1. A new version is out: the app knows its own build number (build.json, written by the APK build) and asks GitHub
//    for the latest release; if there's a newer one, a card says so and UPDATE downloads it (the phone's browser takes
//    the download, then you install over the top).
// 2. Your progress follows your name: unlocks, stage ranks, the pub tab, the open cabinets and your pub bests are saved
//    in Firebase under your name and this phone's secret key (saves/<NAME>/<KEY>), merged both ways when the app
//    opens and pushed when they change. A save code (8 letters and numbers, on the You screen) brings it all back on a
//    new phone: pick the same name, "It's me", type the code (restore/<NAME>/<CODE> holds the key).
// 3. Continue on the tab: out of lives, and you can put another one on the tab (10,000, then 20,000, then 30,000;
//    three a run) and carry on where you fell with a full set of lives. Not online, not in the kebab siege.

// ------------------------------------------------------------------ 1. a new version is out
const UPD = { mine: 0, latest: 0, url: '', dismissed: 0, checkedT: -1e9, el: null, busy: false };
const UPD_API = 'https://api.github.com/repos/TimChattawayHEI/MBCLegacy/releases/latest';
const UPD_APK = 'https://github.com/TimChattawayHEI/MBCLegacy/releases/latest/download/MBC-Legacies.apk';
async function updCheck() {
  if (!window.MBC_APP || UPD.busy) return;
  UPD.busy = true; UPD.checkedT = performance.now();
  try {
    if (!UPD.mine) { const r = await withTimeout(fetch('build.json', { cache: 'no-store' }), 5000); if (!r.ok) return; UPD.mine = (await r.json()).build | 0; }
    if (!UPD.mine) return;
    const r = await withTimeout(fetch(UPD_API, { cache: 'no-store', headers: { Accept: 'application/vnd.github+json' } }), 8000); if (!r.ok) return;
    const j = await r.json(), n = parseInt(String(j.tag_name || '').replace(/\D/g, ''), 10) || 0;
    const apk = (j.assets || []).find(a => /\.apk$/i.test(a.name || ''));
    if (n > UPD.mine && apk) { UPD.latest = n; UPD.url = apk.browser_download_url || UPD_APK; }
  } catch (e) { /* no signal: try again later */ } finally { UPD.busy = false; }
}
function updCardEl() {
  if (UPD.el) return UPD.el;
  const el = document.createElement('div'); el.id = 'updCard';
  el.style.cssText = 'position:fixed;z-index:59;display:none;align-items:center;gap:12px;padding:10px 12px 10px 14px;background:#121a1e;border:2px solid #7fe07a;border-radius:12px;box-shadow:0 8px 30px rgba(0,0,0,.6);font:600 14px Rubik,system-ui,sans-serif;color:#efe6d2;max-width:min(560px,94vw)';
  el.innerHTML = '<div style="flex:1;min-width:0"><div id="updWhat" style="font:400 18px \'Pixelify Sans\',monospace;color:#7fe07a">NEW VERSION OUT</div><div id="updSub" style="color:#93a3a1;font-size:12px"></div></div>' +
    '<button id="updLater" type="button" style="font:700 13px Rubik,sans-serif;padding:10px 12px;border-radius:9px;border:2px solid #7fe07a;background:transparent;color:#7fe07a;cursor:pointer">Later</button>' +
    '<button id="updGo" type="button" style="font:700 13px Rubik,sans-serif;padding:10px 16px;border-radius:9px;border:2px solid #7fe07a;background:#7fe07a;color:#10200f;cursor:pointer">Update</button>';
  document.body.appendChild(el); UPD.el = el;
  el.querySelector('#updGo').addEventListener('click', e => { e.stopPropagation(); updGo(); });
  el.querySelector('#updLater').addEventListener('click', e => { e.stopPropagation(); UPD.dismissed = UPD.latest; sfx('page'); });
  ['pointerdown', 'keydown'].forEach(t => el.addEventListener(t, e => e.stopPropagation()));
  return el;
}
// the app opens anything off its own pages in the phone's browser, which downloads the APK
function updGo() {
  UPD.dismissed = UPD.latest; sfx('life');
  try { cloudPush(true); } catch (e) { /* best effort */ }
  const sub = UPD.el && UPD.el.querySelector('#updSub'); if (sub) sub.textContent = 'Downloading. Open it when it finishes and install over the top.';
  setTimeout(() => { window.location.href = UPD.url || UPD_APK; }, 150);
}
function updTick() {
  const quiet = ['title', 'select', 'pub', 'board'].includes(mode) && !NET.on && !PROFILE.asking;
  // look when the app opens, then every 20 minutes while it's on a menu
  if (quiet && performance.now() - UPD.checkedT > (UPD.mine ? 20 * 60000 : 4000)) updCheck();
  const el = UPD.latest || UPD.el ? updCardEl() : null; if (!el) return;
  const show = quiet && UPD.latest > UPD.mine && UPD.dismissed !== UPD.latest && !(HUB.card && HUB.card.style.display !== 'none');
  if (!show) { if (el.style.display !== 'none') el.style.display = 'none'; return; }
  if (el.style.display === 'none') {
    el.querySelector('#updWhat').textContent = 'NEW VERSION: 1.' + UPD.latest;
    el.querySelector('#updSub').textContent = "You've got 1." + UPD.mine + '. Your progress is saved under your name.';
    sfx('incoming');
  }
  const r = canvas.getBoundingClientRect();
  el.style.display = 'flex'; el.style.left = Math.max(8, r.left + r.width / 2 - el.offsetWidth / 2) + 'px'; el.style.top = Math.max(8, r.bottom - el.offsetHeight - 12) + 'px';
}

// ------------------------------------------------------------------ 2. your progress follows your name
const CODE_ABC = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
const CLOUD = { name: null, state: 'idle', last: '', pushT: 0, retryT: -1e9, code: lsGet('mbc.code', null), codeFor: lsGet('mbc.code.pub', null), dev: lsGet('mbc.dev', null), restoreFor: null };
if (!CLOUD.code) { CLOUD.code = Array.from({ length: 8 }, () => CODE_ABC[Math.floor(nativeRandom() * 32)]).join(''); lsSet('mbc.code', CLOUD.code); }
if (!CLOUD.dev) { CLOUD.dev = Array.from({ length: 10 }, () => CODE_ABC[Math.floor(nativeRandom() * 32)]).join(''); lsSet('mbc.dev', CLOUD.dev); }
const cloudOn = () => appFb() && NT.kind === 'fb' && !!NT.db;
// what's worth keeping: progress, not this phone's settings or a run in progress
function cloudSnap() {
  return { v: 1, unlocked: !!settings.unlocked, thet: !!settings.thet, ash: !!settings.ash, ranks: stageRanks(),
    wallet: Math.round(PUB.wallet || 0), cabs: Object.assign({}, PUB.cabs), pb: Object.assign({}, PUB.pb), pbLad: Object.assign({}, PUB.pbLad),
    ach: typeof achSnap === 'function' ? achSnap() : null };   // trophies (Version 62)
}
// merge a save into this phone: unlocks and open cabinets add up, the better rank and the higher best win; the tab is
// taken from the save when it's newer than this phone's last sync from another phone (or on a restore)
function cloudApply(c, takeTab) {
  if (!c || typeof c !== 'object') return false;
  let ch = false;
  for (const k of ['unlocked', 'thet', 'ash']) if (c[k] && !settings[k]) { settings[k] = true; ch = true; }
  if (ch) saveSettings();
  const rk = stageRanks(); let rc = false;
  for (const k in c.ranks || {}) { const r = c.ranks[k]; if (RANKS.includes(r) && r.length === 1 && (!rk[k] || RANKS.indexOf(r) < RANKS.indexOf(rk[k]))) { rk[k] = r; rc = true; } }
  if (rc) lsSet('carpdiem.ranks', rk);
  let pc = false;
  for (const g in c.cabs || {}) if (c.cabs[g] && !PUB.cabs[g]) { PUB.cabs[g] = true; pc = true; }
  for (const g in c.pb || {}) { const v = +c.pb[g] || 0; if (v > (PUB.pb[g] || 0)) { PUB.pb[g] = v; if (c.pbLad && c.pbLad[g]) PUB.pbLad[g] = c.pbLad[g]; pc = true; } }
  if (takeTab && typeof c.wallet === 'number' && isFinite(c.wallet) && c.wallet >= 0 && c.wallet !== PUB.wallet) { PUB.wallet = Math.round(c.wallet); pc = true; }
  if (pc) pubSave();
  const ac = !!(c.ach && typeof achMerge === 'function' && achMerge(c.ach));   // trophies (Version 62)
  return ch || rc || pc || ac;
}
function cloudPath(n, key) { return 'saves/' + n + '/' + (key || PROFILE.key); }
// when the app opens (and when your name changes): pull, merge, push back
async function cloudStart() {
  const n = PROFILE.name; CLOUD.state = 'busy'; CLOUD.retryT = performance.now();
  try {
    await withTimeout(NT.init(), 8000); if (!cloudOn()) { CLOUD.state = 'idle'; return; }
    const snap = await withTimeout(NT.db.ref(cloudPath(n)).once('value'), 8000), c = snap.val();
    const syncAt = lsGet('mbc.sync.at', 0);
    if (c) cloudApply(c, c.dev !== CLOUD.dev && (c.at || 0) > syncAt);
    CLOUD.name = n; CLOUD.state = 'on'; CLOUD.last = '';
    await cloudPush(true);
    cloudCodePublish();
  } catch (e) { CLOUD.state = denied(e) ? 'norules' : 'idle'; }
}
async function cloudPush(force) {
  if (CLOUD.state !== 'on' || !cloudOn() || CLOUD.name !== PROFILE.name) return;
  const s = JSON.stringify(cloudSnap());
  if (!force && s === CLOUD.last) return;
  CLOUD.last = s; CLOUD.pushT = performance.now();
  try { await withTimeout(NT.db.ref(cloudPath(PROFILE.name)).set(Object.assign(JSON.parse(s), { at: Date.now(), dev: CLOUD.dev })), 8000); lsSet('mbc.sync.at', Date.now()); }
  catch (e) { CLOUD.last = ''; if (denied(e)) CLOUD.state = 'norules'; }
}
// the save code: restore/<NAME>/<CODE> holds this phone's key, so the code alone gets a new phone in
async function cloudCodePublish() {
  if (CLOUD.codeFor === PROFILE.name || !cloudOn()) return;
  try { await withTimeout(NT.db.ref('restore/' + PROFILE.name + '/' + CLOUD.code).set(PROFILE.key), 8000); CLOUD.codeFor = PROFILE.name; lsSet('mbc.code.pub', PROFILE.name); profileCodeShow(); }
  catch (e) { /* rules not in yet: no code to show */ }
}
const codeFmt = c => c.slice(0, 4) + ' ' + c.slice(4);
function cloudCodeLine() { return PROFILE.claimed && CLOUD.codeFor === PROFILE.name ? ' Save code: ' + codeFmt(CLOUD.code) + '. Keep it to get your progress back on a new phone.' : ''; }
function profileCodeShow() { if (PROFILE.asking && !PROFILE.first && !CLOUD.restoreFor && !PROFILE.busy) nameEls.sum.textContent = 'It goes on every scoreboard and in the online lobby. Letters and numbers, 3 to 12.' + cloudCodeLine(); }
function cloudTick() {
  if (!PROFILE.name || !PROFILE.claimed || !appFb()) return;
  if (CLOUD.state === 'busy') return;
  if (CLOUD.state !== 'on' || CLOUD.name !== PROFILE.name) { if (performance.now() - CLOUD.retryT > (CLOUD.state === 'norules' ? 120000 : 30000)) cloudStart(); return; }
  if (performance.now() - CLOUD.pushT > 15000) cloudPush(false);
}
document.addEventListener('visibilitychange', () => { if (document.hidden) cloudPush(false); });
// a new phone: the name's taken, but it's you
const nameAltEl = (() => {
  const row = nameEls.form && nameEls.form.querySelector('.row'); if (!row) return null;
  const b = document.createElement('button'); b.className = 'btn'; b.type = 'button'; b.id = 'nameAlt'; b.textContent = "It's me"; b.hidden = true;
  row.insertBefore(b, row.firstChild);
  b.addEventListener('click', () => cloudRestoreBegin());
  return b;
})();
const nameLabelEl = document.querySelector('label[for="nameInput"]');
function cloudOfferRestore(n) {
  if (!appFb() || !nameAltEl) return;
  CLOUD.offerFor = n; nameAltEl.hidden = false;
  nameEls.sum.textContent = 'Someone already plays as ' + n + ". If that's you on a new phone, tap \"It's me\" and type your save code. If not, try another name.";
}
function cloudRestoreBegin() {
  const n = CLOUD.offerFor; if (!n || PROFILE.busy) return;
  CLOUD.restoreFor = n; nameAltEl.hidden = true; sfx('page');
  nameEls.title.textContent = 'Welcome back, ' + n;
  nameEls.sum.textContent = 'Type the save code from the You screen on your old phone (8 letters and numbers).';
  if (nameLabelEl) nameLabelEl.textContent = 'Save code';
  nameEls.input.value = ''; nameEls.skip.hidden = false; nameEls.skip.textContent = 'Back';
  const save = document.getElementById('nameSave'); if (save) save.textContent = 'Restore';
  try { nameEls.input.focus(); } catch (e) { /* optional */ }
}
function cloudRestoreEnd() {
  const n = CLOUD.restoreFor; CLOUD.restoreFor = null; CLOUD.offerFor = null; if (nameAltEl) nameAltEl.hidden = true;
  if (nameLabelEl) nameLabelEl.textContent = 'Your name';
  nameEls.title.textContent = 'Pick a name'; nameEls.skip.hidden = PROFILE.first; nameEls.skip.textContent = 'Cancel';
  const save = document.getElementById('nameSave'); if (save) save.textContent = "That's me";
  nameEls.input.value = n || ''; nameEls.sum.textContent = 'Letters and numbers, 3 to 12.';
}
// called from the name box first: true if it handled the press
function cloudRestoreHook(skip) {
  if (!CLOUD.restoreFor) { if (nameAltEl && !nameAltEl.hidden && !skip) { nameAltEl.hidden = true; CLOUD.offerFor = null; } return false; }
  if (skip) { cloudRestoreEnd(); return true; }
  if (PROFILE.busy) return true;
  const code = cleanName(nameEls.input.value).slice(0, 8), n = CLOUD.restoreFor;
  if (!/^[A-Z2-9]{8}$/.test(code)) { nameEls.sum.textContent = 'A save code is 8 letters and numbers, like K7QM 2XPA.'; sfx('grab'); return true; }
  PROFILE.busy = true; nameEls.sum.textContent = 'Looking for ' + n + "'s save...";
  const save = document.getElementById('nameSave'); if (save) save.disabled = true;
  cloudRestore(n, code).then(r => {
    PROFILE.busy = false; if (save) save.disabled = false;
    if (r !== 'ok') { nameEls.sum.textContent = r === 'nocode' ? "That code isn't " + n + "'s. Check it on your old phone (You, on the select screen)." : 'No signal. Try again in a moment.'; sfx('grab'); return; }
    sfx('life'); nameEls.sum.textContent = 'Got it. Welcome back, ' + n + '.';
    setTimeout(() => window.location.reload(), 900);   // start again with everything in place (the lads you'd unlocked, your ranks)
  });
  return true;
}
async function cloudRestore(n, code) {
  try {
    await withTimeout(NT.init(), 8000); if (!cloudOn()) return 'offline';
    const k = (await withTimeout(NT.db.ref('restore/' + n + '/' + code).once('value'), 8000)).val();
    if (typeof k !== 'string' || k.length < 16) return 'nocode';
    const c = (await withTimeout(NT.db.ref(cloudPath(n, k)).once('value'), 8000)).val();
    PROFILE.key = k; lsSet('mbc.key', k);
    CLOUD.code = code; lsSet('mbc.code', code); CLOUD.codeFor = n; lsSet('mbc.code.pub', n);
    if (c) cloudApply(c, true);
    lsSet('mbc.sync.at', Date.now());
    CLOUD.restoreFor = null; CLOUD.offerFor = null;
    profileSet(n, true);
    CLOUD.state = 'idle'; CLOUD.retryT = -1e9;
    return 'ok';
  } catch (e) { return denied(e) ? 'nocode' : 'offline'; }
}

// ------------------------------------------------------------------ 3. continue on the tab
const CONT_COST = [10000, 20000, 30000];
const CONT = { on: false, t: 0, p: null, cost: 0, dry: false, sel: 0 };
// out of lives: offer a continue (or say the tab's dry), otherwise it's game over as before
function contOffer(p) {
  if (!run || run.mini || NET.on || mode !== 'play') { gameOver(); return; }
  const n = run.conts || 0;
  if (n >= CONT_COST.length) { gameOver(); return; }
  pubBankStage();   // this stage's points so far go on the tab first, so they count
  CONT.p = p; CONT.cost = CONT_COST[n]; CONT.dry = PUB.wallet < CONT.cost; CONT.t = 0; CONT.sel = 0; CONT.on = true;
  mode = 'cont'; modeT = 0; held.clear(); pressed.clear(); banner = null;
  CONT.music = mus.key; musicSet(null); sfx(CONT.dry ? 'grab' : 'incoming');
}
function contButtons() {
  return CONT.dry ? [{ id: 'no', label: 'FAIR ENOUGH', x: W / 2 - 110, y: 352, w: 220, h: 48 }]
    : [{ id: 'yes', label: 'ON THE TAB', x: W / 2 - 236, y: 352, w: 220, h: 48 }, { id: 'no', label: "I'M DONE", x: W / 2 + 16, y: 352, w: 220, h: 48 }];
}
function contYes() {
  if (!pubSpend(CONT.cost)) { contNo(); return; }
  CONT.on = false; run.conts = (run.conts || 0) + 1;
  run.lives = (DIFFS[run.diff] || DIFFS.normal).lives;
  mode = 'play'; modeT = 0;
  const p = CONT.p || player; respawn(p);
  showBanner('ANOTHER ON THE TAB', run.lives + ' lives · ' + fmtN(PUB.wallet) + ' left on your tab', 2.2);
  sfx('life'); buzz(60);
  musicSet(CONT.music || ST.music || null, true);
}
function contNo() { CONT.on = false; mode = 'play'; gameOver(); }
function contUpdate(dt) {
  CONT.t += dt; updateParts(dt);
  const left = (CONT.dry ? 2.6 : 10) - CONT.t;
  if (!CONT.dry && Math.floor(left + dt) !== Math.floor(left) && left > 0 && left < 9.5) sfx('swing');
  if (left <= 0) { contNo(); return; }
  if (CONT.t < 0.5) return;
  const bs = contButtons();
  if (pressed.has('left') || pressed.has('right')) { CONT.sel = (CONT.sel + 1) % bs.length; sfx('swing'); }
  if (pressed.has('escape') || pressed.has('back')) { contNo(); return; }
  if (pressed.has('punch') || pressed.has('start') || pressed.has('special')) { const b = bs[Math.min(CONT.sel, bs.length - 1)]; if (b.id === 'yes') contYes(); else contNo(); return; }
  for (const t of taps) for (const b of bs) if (t.x > b.x && t.x < b.x + b.w && t.y > b.y && t.y < b.y + b.h) { if (b.id === 'yes') contYes(); else contNo(); return; }
}
function contDraw() {
  ctx.setTransform(scale, 0, 0, scale, 0, 0); ctx.globalAlpha = 1;
  ctx.fillStyle = 'rgba(10,14,16,0.78)'; ctx.fillRect(0, 0, W, H);
  ctx.textBaseline = 'middle';
  if (CONT.dry) {
    textOut("YOUR TAB'S DRY", W / 2, 190, '44px ' + DISPLAY, '#ff8a7a', OUT, 7, 'center');
    ctx.font = '600 16px ' + BODY; ctx.fillStyle = '#efe6d2'; ctx.textAlign = 'center';
    ctx.fillText('Another go costs ' + fmtN(CONT.cost) + '. You’ve got ' + fmtN(PUB.wallet) + ' on your tab.', W / 2, 252);
    ctx.fillStyle = '#93a3a1'; ctx.font = '600 13px ' + BODY; ctx.fillText('Every stage you clear puts its points on your tab.', W / 2, 282);
  } else {
    const left = Math.max(0, Math.ceil(10 - CONT.t));
    textOut('CONTINUE?', W / 2, 150, '48px ' + DISPLAY, '#f2a23a', OUT, 7, 'center');
    textOut(String(left), W / 2, 228, '64px ' + DISPLAY, left <= 3 ? '#ff8a7a' : '#ffd23f', OUT, 8, 'center');
    ctx.font = '600 16px ' + BODY; ctx.fillStyle = '#efe6d2'; ctx.textAlign = 'center';
    ctx.fillText('Put another one on the tab: ' + fmtN(CONT.cost) + '. Carry on from here with ' + (DIFFS[run.diff] || DIFFS.normal).lives + ' lives.', W / 2, 290);
    ctx.fillStyle = '#93a3a1'; ctx.font = '600 13px ' + BODY;
    ctx.fillText('Your tab: ' + fmtN(PUB.wallet) + '   ·   continues left this run: ' + (CONT_COST.length - (run.conts || 0)), W / 2, 316);
  }
  contButtons().forEach((b, i) => {
    const on = i === Math.min(CONT.sel, contButtons().length - 1), yes = b.id === 'yes';
    rrect(b.x, b.y, b.w, b.h, 12); ctx.fillStyle = on ? (yes ? '#7fe07a' : '#f2a23a') : 'rgba(24,36,42,0.95)'; ctx.fill();
    ctx.strokeStyle = yes ? '#7fe07a' : '#f2a23a'; ctx.lineWidth = 2; ctx.stroke();
    ctx.font = '18px ' + DISPLAY; ctx.fillStyle = on ? '#10200f' : '#efe6d2'; ctx.textAlign = 'center'; ctx.fillText(b.label, b.x + b.w / 2, b.y + b.h / 2 + 1);
  });
  if (!touchUI) { ctx.font = '600 12px ' + BODY; ctx.fillStyle = '#93a3a1'; ctx.textAlign = 'center'; ctx.fillText(CONT.dry ? 'Any button.' : '← → pick, HIT to choose, Esc for game over.', W / 2, 424); }
}

// every frame, before anything else
function qolTick() {
  try { updTick(); } catch (e) { glitch('update', e); }
  try { cloudTick(); } catch (e) { glitch('cloud', e); }
  if (typeof achTick === 'function') try { achTick(); } catch (e) { glitch('trophies', e); }   // Version 62
}
