// ================================================================== Version 62: trophies
// 29 achievements across the campaign, the fights, the Harvest Moon and the online side. Each one puts a bonus on your
// tab the moment you get it, with a card at the top of the screen. TROPHIES on the select screen lists them all.
// Kept on the phone (mbc.ach), and in your cloud save (Version 61) so a new phone keeps them.
// Most are spotted by looking at the game each frame; the rest come from three hooks: the pub games' flashes
// (pubFlash), their results (miniEnd) and the big banners (showBanner).
const ACH_LIST = [
  // the campaign
  { id: 'c1999', name: 'Back to the Future', what: 'Finish 1999', tab: 2000 },
  { id: 'celba', name: 'Lads on Tour', what: 'Finish Elba 2002', tab: 2000 },
  { id: 'cnight', name: 'Last Orders', what: 'Finish Nightlife 2006', tab: 2000 },
  { id: 'ccarp', name: 'Carp Diem', what: 'Land Big Gary and finish the campaign', tab: 5000 },
  { id: 'cram', name: 'Up the Estate', what: 'Survive Ramsden', tab: 3000 },
  { id: 'chard', name: 'Hard as Nails', what: 'Finish the campaign on Hard', tab: 10000 },
  { id: 'cnotab', name: 'Paid Up', what: 'Finish the campaign without a continue', tab: 5000 },
  // the fights
  { id: 'untouched', name: 'Untouchable', what: 'Clear a stage without taking a hit', tab: 3000 },
  { id: 'srank', name: 'Top Marks', what: 'Get an S rank on a stage', tab: 2000 },
  { id: 'alls', name: 'Straight S', what: 'S rank on every stage', tab: 20000 },
  { id: 'chain30', name: 'Chain Gang', what: 'Land a 30-hit chain', tab: 2000 },
  { id: 'multi4', name: 'Wrecking Ball', what: 'Knock out four at once', tab: 2000 },
  { id: 'secret', name: 'Glint in the Eye', what: 'Find a hidden extra life', tab: 1000 },
  { id: 'squad', name: 'Full Squad', what: 'Fire a special with all seven lads', tab: 3000 },
  { id: 'kos1000', name: 'Body Count', what: '1,000 knockouts, all time', tab: 5000 },
  { id: 'tab', name: 'On the Tab', what: 'Put a continue on the tab', tab: 500 },
  // the Harvest Moon
  { id: 'd180', name: 'One Hundred and Eighty!', what: 'Three darts, 180', tab: 2000 },
  { id: 'jackpot', name: 'Three Marcs', what: 'Hit the fruit machine jackpot', tab: 2000 },
  { id: 'pens5', name: 'Top Bins', what: 'Five from five on penalties', tab: 2000 },
  { id: 'midnight', name: 'Midnight Kiss', what: 'A kiss in the last five seconds of Kiss Chase', tab: 2000 },
  { id: 'gary', name: "Gary's Had It", what: 'Hit Big Gary with a drive', tab: 2000 },
  { id: 'awake', name: 'Wide Awake', what: 'Drive 1,500 m in Stay Awake', tab: 2000 },
  { id: 'kebab', name: "Your Kebab's Up", what: 'Get your kebab in the siege', tab: 2000 },
  { id: 'wave10', name: 'Last Man Standing', what: 'Reach wave 10 in the siege', tab: 3000 },
  { id: 'round', name: 'Your Round', what: 'Buy the lads a round', tab: 500 },
  // the lads
  { id: 'coop', name: "Two's Company", what: 'Play an online co-op game', tab: 1000 },
  { id: 'chat', name: 'Chatterbox', what: 'Say something in the Harvest Moon chat', tab: 250 },
  { id: 'thet', name: 'Low Profile', what: 'Unlock Thet', tab: 2000 },
  { id: 'ash', name: "He's Back", what: 'Unlock Ash', tab: 5000 },
];
const ACH_BY_ID = Object.fromEntries(ACH_LIST.map(a => [a.id, a]));
const SQUAD = ['tim', 'seb', 'byron', 'pearcy', 'kelly', 'marc', 'sam'];
const ACH = { got: lsGet('mbc.ach', {}) || {}, st: Object.assign({ kos: 0, sp: {} }, lsGet('mbc.stats', {}) || {}),
  queue: [], el: null, showT: 0, lastRun: null, lastK: 0, saveT: 0, dirty: false };
const achHave = id => !!ACH.got[id];
const achCount = () => ACH_LIST.filter(a => ACH.got[a.id]).length;
function achGive(id) {
  const a = ACH_BY_ID[id]; if (!a || ACH.got[id]) return false;
  ACH.got[id] = Date.now(); lsSet('mbc.ach', ACH.got);
  pubBank(a.tab); ACH.queue.push(a);
  return true;
}
// for the cloud save (Version 61): what you've got and the running totals; merging never pays the bonus twice
function achSnap() { return { got: Object.assign({}, ACH.got), kos: ACH.st.kos || 0, sp: Object.assign({}, ACH.st.sp) }; }
function achMerge(c) {
  if (!c || typeof c !== 'object') return false;
  let ch = false;
  for (const id in c.got || {}) if (ACH_BY_ID[id] && !ACH.got[id]) { ACH.got[id] = c.got[id] || Date.now(); ch = true; }
  if ((+c.kos || 0) > (ACH.st.kos || 0)) { ACH.st.kos = +c.kos; ch = true; }
  for (const k in c.sp || {}) if (!ACH.st.sp[k]) { ACH.st.sp[k] = true; ch = true; }
  if (ch) { lsSet('mbc.ach', ACH.got); lsSet('mbc.stats', ACH.st); }
  return ch;
}
// the hooks
function achFlash(text) {
  const t = String(text || '');
  if (t === 'ONE HUNDRED AND EIGHTY!') achGive('d180');
  else if (/^THREE MARCS/.test(t)) achGive('jackpot');
  else if (/^MIDNIGHT KISS/.test(t)) achGive('midnight');
  else if (/^BIG GARY'S HAD IT/.test(t)) achGive('gary');
}
function achMini(id, score, reason) {
  if (id === 'pens' && reason === 'FIVE FROM FIVE') achGive('pens5');
  if (id === 'awake' && score >= 1500) achGive('awake');
}
function achBanner(text) { if (/KEBAB.S UP/.test(String(text || ''))) achGive('kebab'); }
// a stage is the last of its chapter when the next one on the route is in another chapter
function achChapterEnd(key) {
  const i = ROUTE.indexOf(key); if (i < 0) return null;
  const c = chapterOf(key), n = ROUTE[i + 1];
  return !n || chapterOf(n) !== c ? c : null;
}
// everything else: look at the game
function achWatch() {
  if (settings.thet) achGive('thet');
  if (settings.ash) achGive('ash');
  if (CHAT && CHAT.sentAt > 0) achGive('chat');
  if (mode === 'pub' && PUB.round) achGive('round');
  if (!run) return;
  if ((run.conts || 0) > 0) achGive('tab');
  if (mode === 'play' && S && player) {
    if (NET.on) achGive('coop');
    if (S.chain >= 30) achGive('chain30');
    if (S.koN >= 4) achGive('multi4');
    if (S.secretFound) achGive('secret');
    if (S.key === 'kebab' && (S.waveIdx || 0) >= 9) achGive('wave10');
    if (player.state === 'special' && player.def && SQUAD.includes(player.def.id) && !ACH.st.sp[player.def.id]) { ACH.st.sp[player.def.id] = true; ACH.dirty = true; }
    if (SQUAD.every(id => ACH.st.sp[id])) achGive('squad');
  }
  // knockouts, all time
  if (ACH.lastRun !== run) { ACH.lastRun = run; ACH.lastK = run.kills || 0; }
  const k = run.kills || 0; if (k > ACH.lastK) { ACH.st.kos = (ACH.st.kos || 0) + (k - ACH.lastK); ACH.lastK = k; ACH.dirty = true; }
  if (ACH.st.kos >= 1000) achGive('kos1000');
  // a stage cleared
  if (mode === 'clear' && clearInfo && !clearInfo.achSeen && S) {
    clearInfo.achSeen = true;
    if ((clearInfo.rows || []).some(r => r[0] === 'Untouched')) achGive('untouched');
    if (clearInfo.rank === 'S') achGive('srank');
    const ranks = stageRanks(); if (ROUTE.concat(['ramsden']).every(k2 => ranks[k2] === 'S')) achGive('alls');
    if (S.key === 'ramsden') achGive('cram');
    const ch = achChapterEnd(S.key);
    if (ch === '1999') achGive('c1999'); else if (ch === 'elba') achGive('celba'); else if (ch === 'nightlife') achGive('cnight');
  }
  // the campaign won
  if (mode === 'win' && !run.achSeen) {
    run.achSeen = true;
    if (run.ramsdenCleared) achGive('cram');
    if ((run.route || []).includes('pegnine')) achGive('ccarp');
    if (run.diff === 'hard') achGive('chard');
    if (!(run.conts > 0)) achGive('cnotab');
  }
  if (ACH.dirty && performance.now() - ACH.saveT > 5000) { ACH.dirty = false; ACH.saveT = performance.now(); lsSet('mbc.stats', ACH.st); }
}
// the card at the top of the screen, one at a time
function achCardEl() {
  if (ACH.el) return ACH.el;
  const el = document.createElement('div'); el.id = 'achCard';
  el.style.cssText = 'position:fixed;z-index:61;display:none;align-items:center;gap:12px;padding:10px 16px 10px 12px;background:#121a1e;border:2px solid #ffd23f;border-radius:12px;box-shadow:0 8px 30px rgba(0,0,0,.6);font:600 13px Rubik,system-ui,sans-serif;color:#efe6d2;pointer-events:none;transition:transform .25s ease-out,opacity .25s;max-width:min(520px,92vw)';
  el.innerHTML = '<canvas id="achCup" width="16" height="16" style="width:40px;height:40px;image-rendering:pixelated;flex:none"></canvas><div style="min-width:0"><div style="font:800 10px Rubik,sans-serif;letter-spacing:2px;color:#ffd23f">TROPHY</div><div id="achName" style="font:400 19px \'Pixelify Sans\',monospace;color:#efe6d2"></div><div id="achWhat" style="color:#93a3a1;font-size:12px"></div></div>';
  document.body.appendChild(el); ACH.el = el;
  achCup(el.querySelector('#achCup').getContext('2d'), 0, 0, 1, true);
  return el;
}
// a little gold cup, pixel by pixel (16x16), or its grey outline when you haven't got it
const CUP = ['...kkkkkkkkkk...', '...kwyyyyyyok...', 'kkkkwyyyyyyokkkk', 'k..kwyyyyyyok..k', 'k..kwyyyyyyok..k', '.k.kwyyyyyyok.k.', '..kkwyyyyyyokk..', '....kwyyyyok....', '.....kwyyok.....', '......kyok......', '......kyok......', '.....kyyyok.....', '....kyyyyyok....', '....kkkkkkkk....', '................', '................'];
function achCup(c, x, y, s, on) {
  const pal = on ? { k: '#16120f', y: '#ffd23f', w: '#fff4b8', o: '#c88a1e' } : { k: '#55626a', y: '#1e2a30', w: '#26343b', o: '#1a2328' };
  for (let r = 0; r < 16; r++) for (let q = 0; q < 16; q++) { const ch = CUP[r][q]; if (!ch || ch === '.') continue; c.fillStyle = pal[ch]; c.fillRect(x + q * s, y + r * s, s, s); }
}
function achCardTick(dt) {
  if (!ACH.queue.length && !ACH.showT) return;
  const el = achCardEl();
  if (!ACH.showT && ACH.queue.length && mode !== 'tledit' && mode !== 'cont') {   // not over the layout editor or a continue
    const a = ACH.queue.shift(); ACH.showT = 3.8;
    el.querySelector('#achName').textContent = a.name;
    el.querySelector('#achWhat').textContent = a.what + '  ·  +' + fmtN(a.tab) + ' on your tab';
    el.style.display = 'flex'; el.style.opacity = '0'; el.style.transform = 'translateY(-16px)';
    requestAnimationFrame(() => { el.style.opacity = '1'; el.style.transform = 'translateY(0)'; });
    sfx('life'); setTimeout(() => sfx('incoming'), 120);
  }
  const r = canvas.getBoundingClientRect();
  el.style.left = Math.max(8, r.left + r.width / 2 - el.offsetWidth / 2) + 'px'; el.style.top = Math.max(8, r.top + 56) + 'px';
  ACH.showT = Math.max(0, ACH.showT - dt);
  if (ACH.showT < 0.3) el.style.opacity = '0';
  if (!ACH.showT) el.style.display = 'none';
}
let achLastT = 0;
function achTick() {
  const now = performance.now(), dt = Math.min(0.1, (now - (achLastT || now)) / 1000); achLastT = now;
  achWatch(); achCardTick(dt);
  const b = document.getElementById('t3-trophy'); if (b) { const t = 'Trophies ' + achCount() + '/' + ACH_LIST.length; if (b.textContent !== t) b.textContent = t; }
}

// ------------------------------------------------------------------ the trophy room (a screen of its own)
let trophyBack = 'select', trophyPage = 0;
function trophyOpen(back) { trophyBack = back || 'select'; trophyPage = 0; mode = 'trophies'; modeT = 0; sfx('page'); }
function trophyClose() { mode = trophyBack === 'pub' ? 'pub' : 'select'; modeT = 0; sfx('page'); }
function updateTrophies() {
  if (modeT < 0.3) return;
  if (pressed.has('escape') || pressed.has('back') || pressed.has('jump') || pressed.has('punch') || pressed.has('start')) { trophyClose(); return; }
  if (taps.length) trophyClose();
}
function drawTrophies() {
  ctx.fillStyle = '#0d1417'; ctx.fillRect(0, 0, W, H);
  const g = ctx.createLinearGradient(0, 0, 0, 200); g.addColorStop(0, 'rgba(255,210,63,0.16)'); g.addColorStop(1, 'rgba(255,210,63,0)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, 200);
  textOut('TROPHIES', W / 2, 40, '36px ' + DISPLAY, '#ffd23f', OUT, 7);
  const n = achCount(), earned = ACH_LIST.filter(a => ACH.got[a.id]).reduce((t, a) => t + a.tab, 0);
  ctx.font = '600 12px ' + BODY; ctx.fillStyle = '#93a3a1'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillText(n + ' of ' + ACH_LIST.length + '   ·   ' + fmtN(earned) + ' put on your tab   ·   knockouts all time: ' + fmtN(ACH.st.kos || 0), W / 2, 70);
  const half = Math.ceil(ACH_LIST.length / 2);
  ACH_LIST.forEach((a, i) => {
    const col = i < half ? 0 : 1, row = i < half ? i : i - half, x = 40 + col * 450, y = 92 + row * 28, on = !!ACH.got[a.id];
    rrect(x, y, 430, 26, 6); ctx.fillStyle = on ? 'rgba(255,210,63,0.10)' : 'rgba(24,36,42,0.7)'; ctx.fill();
    achCup(ctx, x + 6, y + 3, 1.25, on);
    ctx.textAlign = 'left'; ctx.font = '15px ' + DISPLAY; ctx.fillStyle = on ? '#efe6d2' : '#6d7b80'; ctx.fillText(a.name, x + 32, y + 9);
    ctx.font = '600 10px ' + BODY; ctx.fillStyle = on ? '#b9b09a' : '#56636a'; ctx.fillText(a.what + (a.id === 'kos1000' && !on ? ' (' + fmtN(ACH.st.kos || 0) + ')' : a.id === 'squad' && !on ? ' (' + SQUAD.filter(s => ACH.st.sp[s]).length + '/7)' : ''), x + 32, y + 20);
    ctx.textAlign = 'right'; ctx.font = '800 11px ' + BODY; ctx.fillStyle = on ? '#7fe07a' : '#56636a'; ctx.fillText('+' + fmtN(a.tab), x + 420, y + 13);
  });
  ctx.textAlign = 'center'; ctx.font = '600 12px ' + BODY; ctx.fillStyle = '#93a3a1';
  ctx.fillText(touchUI ? 'Tap to go back.' : 'Any button to go back.', W / 2, H - 14);
}
