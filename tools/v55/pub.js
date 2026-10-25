// ================================================================== Version 55: the pub, its games and their boards
// Points are the currency: every stage banks what it earned onto your tab, and the pub spends it.
// The pub sits between chapters on a run (offline), and is open from the select screen any time.
// Four mini-games turn up once in the campaign, played by the lad they belong to, and then live in the pub as arcade
// cabinets: PENALTIES (Byron, after The Frequency), KISS CHASE (Seb, after Soundz FM), STAY AWAKE (Sam, after The Club)
// and THE LONG DRIVE (Pearcy, after The Arrangement). Darts and the fruit machine are always there.
// Every game has an all-time board (Firebase in the app, the shared store on claude.ai, this device as a fallback):
// top five on a chalkboard by its cabinet, your personal best under them, and the record holder's face on the screen.
const PUB_TAB0 = 5000;   // the landlord starts everyone with a tab
const PUB = { wallet: lsGet('mbc.pub.wallet', PUB_TAB0), cabs: lsGet('mbc.pub.cabs', {}), pb: lsGet('mbc.pub.pb', {}), pbLad: lsGet('mbc.pub.pblad', {}),
  lad: 'tim', x: 200, y: 470, face: 1, walk: 0, moving: false, target: null, from: null, next: null, near: null,
  msg: null, msgT: 0, pints: 0, round: false, view: null, boardGame: null, t: 0 };
function pubSave() { lsSet('mbc.pub.wallet', PUB.wallet); lsSet('mbc.pub.cabs', PUB.cabs); lsSet('mbc.pub.pb', PUB.pb); lsSet('mbc.pub.pblad', PUB.pbLad); }
function pubBank(n) { n = Math.round(n || 0); if (n > 0) { PUB.wallet += n; pubSave(); } return n; }
function pubSpend(n) { if (PUB.wallet < n) return false; PUB.wallet -= n; pubSave(); return true; }
const fmtN = n => Math.round(n).toLocaleString('en-GB');
function pubImg(n) { return bgImg('pub/' + n); }
const PUB_FILES = ['cabinet', 'chalk', 'fruitface', 'pitch', 'can', 'dartboard', 'dart', 'dart_fly', 'golfball', 'tee',
  'sym_cherry', 'sym_lemon', 'sym_grapes', 'sym_bell', 'sym_bar', 'sym_seven', 'keeper_ready', 'keeper_dive', 'byron_kick', 'pearcy_golf', 'tornado', 'tornado2'];
function pubPreload() { PUB_FILES.forEach(pubImg); ['social/wall', 'social/bar', 'social/fruit', 'set/dartboard', 'set/window', 'fishery/treeline', 'fishery/goose', 'fish/gary'].forEach(bgImg); }
// one cell of a PUB_STRIPS strip, feet on (x, y), k sprite pixels per... k game units per sprite pixel (2 = 1:1 on the pixel layer)
function pubStrip(name, f, x, y, k, flip) {
  const img = pubImg(name), m = PUB_STRIPS[name]; if (!img || !m) return;
  f = clamp(f | 0, 0, m.n - 1);
  ctx.save(); ctx.imageSmoothingEnabled = false; ctx.translate(snap2(x), snap2(y)); if (flip) ctx.scale(-1, 1);
  ctx.drawImage(img, f * m.cell, 0, m.cell, m.cell, -m.ax * k, -m.ay * k, m.cell * k, m.cell * k);
  ctx.restore();
}

// the games, and where each one turns up on a run
const MINI_AFTER = { frequency: 'pens', soundz: 'kiss', club: 'awake', arrival: 'golf' };
const MINI_DEF = {
  darts: { title: 'NINE DARTS', short: 'DARTS', price: 1500, unit: '', board: 'BEST NINE DARTS', music: 'social', pay: s => s * 15,
    how: ['Nine darts. Score as many as you can.', 'Your hand sways. Throw when it lines up.', 'Every pint you have makes it sway more.'],
    keys: 'Stick or arrows to aim, HIT to throw', touch: 'Stick to aim, HIT to throw' },
  fruit: { title: 'FRUIT MACHINE', short: 'FRUITS', price: 0, unit: '', board: 'BIGGEST WINS', music: 'social', pay: () => 0,
    how: ['500 a spin, off your tab.', 'HOLDS and NUDGES come up after a losing spin.', 'Three Marcs is the jackpot.'],
    keys: 'HIT to spin, arrows hold or nudge a reel', touch: 'SPIN to spin, tap a reel to hold or nudge it' },
  pens: { title: 'PENALTIES', short: 'PENS', lad: 'byron', price: 1000, unit: '', board: 'TOP SCORES', music: 'garage', pay: s => s * 0.5,
    after: 'The Frequency', how: ['Five penalties against the Parkie.', 'Stop the arrow for the side, then the height.', 'Corners score more. JUMP once: the under-12s heckle him.'],
    keys: 'HIT to stop the arrow, JUMP for the whistle', touch: 'Tap to stop the arrow, WHISTLE once' },
  kiss: { title: 'KISS CHASE', short: 'KISS', lad: 'seb', price: 1000, unit: '', board: 'TOP SCORES', music: 'soundz', pay: s => s * 0.3,
    after: 'Soundz FM', how: ["New Year's Eve, 11:59. Seb's it.", 'Catch as many girls as you can before midnight. Quick kisses chain.', 'Mind the boyfriends. JUMP once: THE ULTIMATE SEX TORNADO.'],
    keys: 'Stick or arrows to run, JUMP for the tornado', touch: 'Stick to run, JUMP once for the tornado' },
  awake: { title: 'STAY AWAKE', short: 'AWAKE', lad: 'sam', price: 1000, unit: 'm', board: 'FURTHEST', music: 'road', pay: s => s * 1.5,
    after: 'The Club', how: ['4am, the drive back to the villa. Sam is fading.', 'Grab energy drinks to keep his eyes open.', 'A crash wakes him up, but four and the car’s done.'],
    keys: 'Up and down to change lanes', touch: 'Stick up and down to change lanes' },
  golf: { title: 'THE LONG DRIVE', short: 'DRIVE', lad: 'pearcy', price: 1000, unit: 'yds', board: 'LONGEST DRIVES', music: 'naval', pay: s => s * 8,
    after: 'The Arrangement', how: ['Three balls into the lake. Longest one counts.', 'HIT to swing, HIT for power, HIT on the line.', 'JUMP once first: CARP DIEM. More power, less control.'],
    keys: 'HIT three times to swing, JUMP for the pills', touch: 'Tap three times to swing, PILLS once' },
};
const PUB_GAMES = ['darts', 'fruit', 'pens', 'golf', 'awake', 'kiss'];
const cabOpen = id => !MINI_DEF[id].lad || !!PUB.cabs[id];

// ------------------------------------------------------------------ the boards
const PUBB = { remote: {}, local: lsGet('mbc.pub.boards', {}), kind: null, uid: null, db: null, started: false };
function pubBoardsStart() {
  if (PUBB.started) return; PUBB.started = true;
  (async () => {
    try {
      if (typeof FB_CFG !== 'undefined' && FB_CFG && window.MBC_APP) {
        await NT.init();
        if (NT.kind !== 'fb') return;
        PUBB.db = NT.db; PUBB.kind = 'fb';
        for (const g of PUB_GAMES) {
          PUBB.db.ref('boards/' + g).orderByChild('score').limitToLast(40).on('value', snap => {
            const out = []; snap.forEach(c => { const e = pubEntry(c.val()); if (e) out.push(e); }); PUBB.remote[g] = out;
            pubSyncMine(g);
          }, () => { PUBB.kind = 'local'; });
        }
        return;
      }
      if (window.claude && typeof window.claude.use === 'function') {
        const db = await window.claude.use('db'); if (!db) return;
        const user = await window.claude.use('user'); PUBB.uid = user ? await user.id() : null;
        PUBB.db = db; PUBB.kind = 'claude';
        db.collection('pubboards').onSnapshot(snap => {
          const all = {};
          snap.docs.forEach(d => { const es = (d.data() || {}).entries || {}; for (const g in es) if (Array.isArray(es[g])) es[g].forEach(e => { const s = pubEntry(e); if (s) (all[g] = all[g] || []).push(s); }); });
          PUBB.remote = all;
        }, () => { PUBB.kind = 'local'; });
      }
    } catch (e) { PUBB.kind = 'local'; }
  })();
}
function pubEntry(e) {
  if (!e || typeof e !== 'object') return null;
  const score = Number(e.score); if (!isFinite(score) || score <= 0) return null;
  const name = String(e.name || 'ANON').toUpperCase().slice(0, 12);
  return { id: name, name, lad: CHAR_BY_ID[e.lad] ? e.lad : 'tim', score: Math.round(score), at: Number(e.at) || 0 };
}
// one row per player: their best, whichever lad they used (Version 56)
function pubBoard(g) {
  const best = {};
  for (const e of (PUBB.remote[g] || []).concat(PUBB.local[g] || [])) { const s = pubEntry(e); if (!s) continue; const b = best[s.name]; if (!b || s.score > b.score) best[s.name] = s; }
  return Object.values(best).sort((a, b) => b.score - a.score || a.at - b.at);
}
// a best made before the name was claimed (or with no signal) goes up as soon as it can
function pubSyncMine(g) {
  if (PUBB.kind !== 'fb' || !PROFILE.name || !PROFILE.claimed || !PUB.pb[g] || !PUB.pbLad[g]) return;
  const mine = (PUBB.remote[g] || []).find(e => e.name === PROFILE.name);
  if (mine && mine.score >= PUB.pb[g]) return;
  PUBB.db.ref('boards/' + g + '/' + PROFILE.name).set({ name: PROFILE.name, lad: PUB.pbLad[g], score: PUB.pb[g], at: Date.now() }).catch(() => {});
}
async function pubBoardAdd(g, entry) {
  PUBB.local[g] = (PUBB.local[g] || []).filter(e => pubEntry(e) && pubEntry(e).name !== entry.name).concat([entry]).sort((a, b) => b.score - a.score).slice(0, 40); lsSet('mbc.pub.boards', PUBB.local);
  try {
    if (PUBB.kind === 'fb') { await PUBB.db.ref('boards/' + g + '/' + entry.name).set(entry); return 'shared'; }
    if (PUBB.kind === 'claude' && PUBB.uid) {
      const ref = PUBB.db.doc('pubboards/' + PUBB.uid), snap = await ref.get();
      const es = snap.exists ? Object.assign({}, (snap.data() || {}).entries) : {};
      es[g] = [entry];
      await ref.set({ entries: es }); return 'shared';
    }
  } catch (e) { /* this device only */ }
  return 'local';
}
// your best goes on the board under your name, with the lad you used (Version 56: one row each, not one per lad)
function pubRecord(g, lad, score, then) {
  score = Math.round(score);
  if (score <= 0 || score <= (PUB.pb[g] || 0)) { then({ newBest: false, place: 0 }); return; }
  PUB.pb[g] = score; PUB.pbLad[g] = lad; pubSave();
  const go = () => {
    const entry = { name: PROFILE.name || 'ANON', lad, score, at: Date.now() };
    pubBoardAdd(g, entry).then(w => { if (MG) MG.saved = w; });
    const place = pubBoard(g).filter(e => e.name !== entry.name && e.score >= score).length + 1;
    then({ newBest: true, place, entry });
  };
  if (PROFILE.name) go(); else profileAsk(false, go);
}
let pubNameCb = null, pubNameMode = null;
function pubNameHook() { return false; }

// ------------------------------------------------------------------ touch: where fingers are, and buttons drawn on screen
const pubPtr = new Map();
canvas.addEventListener('pointerdown', e => { if (mode === 'pub' || mode === 'mini') { const p = toLogical(e); pubPtr.set(e.pointerId, { x: p.x, y: p.y, ox: p.x, oy: p.y, t: time }); } });
canvas.addEventListener('pointermove', e => { const q = pubPtr.get(e.pointerId); if (q) { const p = toLogical(e); q.x = p.x; q.y = p.y; } });
const pubUp = e => { const q = pubPtr.get(e.pointerId); if (q && (mode === 'pub' || mode === 'mini')) pubReleases.push(q); pubPtr.delete(e.pointerId); };
canvas.addEventListener('pointerup', pubUp); canvas.addEventListener('pointercancel', pubUp);
let pubReleases = [], pubRel = [], PUI = [], pubHits = new Set(), pubFree = [];
// the pub and the moving games use the same stick and buttons as a fight (Version 55.2)
function pubStick() { return (mode === 'pub' && !PUB.view) || (mode === 'mini' && !!MG && MG.phase === 'play' && ['kiss', 'awake', 'darts'].includes(MG.id)); }
const pubPadTouch = () => touchUI && !padOn();
function pubFinger() { for (const q of pubPtr.values()) if (!PUI.some(b => q.ox > b.x && q.ox < b.x + b.w && q.oy > b.y && q.oy < b.y + b.h)) return q; return null; }
// at the start of each update: which drawn buttons were tapped, and the taps that weren't on one
function pubTapsIn() {
  pubHits = new Set(); pubFree = []; pubRel = pubReleases; pubReleases = [];
  for (const t of taps) { const b = PUI.find(b => t.x > b.x - 6 && t.x < b.x + b.w + 6 && t.y > b.y - 6 && t.y < b.y + b.h + 6); if (b) pubHits.add(b.id); else pubFree.push(t); }
}
function pubBtn(id, x, y, w, h, label, hot, col) {
  PUI.push({ id, x, y, w, h });
  ctx.save(); rrect(x, y, w, h, 10); ctx.fillStyle = hot ? (col || '#f2a23a') : 'rgba(20,28,32,0.9)'; ctx.fill();
  ctx.strokeStyle = col || '#f2a23a'; ctx.lineWidth = 2; ctx.stroke();
  ctx.font = '15px ' + DISPLAY; ctx.fillStyle = hot ? '#1a1206' : '#ffd23f'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(label, x + w / 2, y + h / 2 + 1);
  ctx.restore();
}
const pubGo = () => pressed.has('punch') || pressed.has('start') || pubHits.has('go') || pubFree.length > 0;
const pubBack = () => pressed.has('escape') || pressed.has('back') || pubHits.has('back');

// the world layer at 480x270, scaled up in whole steps like the fights (Version 15), then sharp text on top
function pubPixel(fn) {
  const main = ctx; ctx = lowCtx; passScale = 0.5;
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.fillStyle = '#000'; ctx.fillRect(0, 0, LOW_W, LOW_H);
  ctx.setTransform(0.5, 0, 0, 0.5, 0, 0);
  try { fn(); } catch (e) { glitch('pub draw', e); }
  ctx = main; passScale = scale;
  const k = Math.max(1, Math.ceil(canvas.width / LOW_W));
  if (midCv.width !== LOW_W * k) { midCv.width = LOW_W * k; midCv.height = LOW_H * k; }
  midCtx.imageSmoothingEnabled = false; midCtx.drawImage(lowCv, 0, 0, midCv.width, midCv.height);
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.imageSmoothingEnabled = true; ctx.imageSmoothingQuality = 'high';
  ctx.drawImage(midCv, 0, 0, canvas.width, canvas.height);
  ctx.setTransform(scale, 0, 0, scale, 0, 0);
}
function pubLad(id, x, y, state, face, walk, s, extra) {
  const sh = ladSprite(id); if (!sh || !sh.ready) return;
  const c = CHAR_BY_ID[id];
  const e = Object.assign({ def: c, look: c.look, state: state || 'idle', face: face || 1, z: 0, t: time, walk: walk || 0, vx: state === 'walk' || state === 'run' ? 100 : 0, vy: 0, flash: 0, atkT: 0, x, y, scale: 1 }, extra || {});
  drawLad(e, x, y, s || 1, sh);
}
function pubFoe(kind, x, y, state, face, walk) {
  const sh = ladSprite(kind); if (!sh || !sh.ready) return;
  drawLad({ kind, state, face, z: 0, t: time, walk, vx: state === 'walk' ? 100 : 0, vy: 0, flash: 0, atkT: 0, x, y }, x, y, 1, sh);
}
function pubPanel(x, y, w, h) { ctx.save(); rrect(x, y, w, h, 12); ctx.fillStyle = 'rgba(14,20,24,0.88)'; ctx.fill(); ctx.strokeStyle = '#f2a23a'; ctx.lineWidth = 2; ctx.stroke(); ctx.restore(); }
function pubTabHud(label) {
  pubPanel(W - 236, 14, 220, 52);
  ctx.font = '800 11px ' + BODY; ctx.fillStyle = '#93a3a1'; ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; ctx.fillText(label || 'YOUR TAB', W - 222, 30);
  textOut(fmtN(PUB.wallet), W - 28, 46, '24px ' + DISPLAY, '#ffd23f', OUT, 5, 'right');
}
function pubSay(text, t) { PUB.msg = text; PUB.msgT = t || 2.4; }

// ================================================================== the pub itself
const PUB_W = 2120, PUB_FLOOR = 400;
const PUB_OBJ = [
  { id: 'door', x: 60 }, { id: 'bar', x: 540 }, { id: 'darts', x: 960 }, { id: 'fruit', x: 1300 },
  { id: 'pens', x: 1480 }, { id: 'golf', x: 1650 }, { id: 'awake', x: 1820 }, { id: 'kiss', x: 1990 },
];
function openPub(from, next, lad) {
  pubPreload(); pubBoardsStart();
  PUB.from = from; PUB.next = next || null; PUB.lad = lad || PUB.lad || 'tim';
  PUB.x = 150; PUB.y = 470; PUB.face = 1; PUB.target = null; PUB.view = null; PUB.round = false; PUB.t = 0;
  if (from === 'run') PUB.pints = 0;
  cam.x = 0; mode = 'pub'; modeT = 0; banner = null; musicSet('social');
  pubSay(from === 'run' ? 'The lads pile into the Harvest Moon. HIT at the bar for a round.' : 'The Harvest Moon. Walk up to anything, or anyone, and press HIT.', 3);
}
function pubLeave() {
  sfx('page'); PUB.view = null;
  const n = PUB.next; PUB.next = null; PUB.from = null;
  if (n) n(); else { mode = 'select'; modeT = 0; musicSet(null); }
}
function pubNear() {
  let best = null;
  for (const g of hubGhosts()) { const d = Math.abs(PUB.x - g.x) + Math.abs(PUB.y - g.y) * 0.5; if (d < 70 && (!best || d < best.d)) best = { o: { id: 'player', g }, d: d * 0.5 }; }
  for (const o of PUB_OBJ) { const d = Math.abs(PUB.x - o.x); if (d < (o.id === 'bar' ? 220 : o.id === 'door' ? 90 : 62) && (!best || d < best.d)) best = { o, d }; }
  return best ? best.o : null;
}
function pubPrompt(o) {
  if (!o) return null;
  if (o.id === 'player') return hubPrompt(o.g);
  if (o.id === 'door') return PUB.from === 'run' ? 'BACK OUT INTO THE NIGHT' : 'LEAVE THE PUB';
  if (o.id === 'bar') return PUB.from === 'run' ? (PUB.round ? 'ANOTHER? YOU’VE HAD YOUR ROUND' : 'BUY A ROUND · ' + fmtN(PUB_ROUND) + ' · +1 LIFE') : 'HAVE A PINT · ' + fmtN(PUB_PINT);
  const d = MINI_DEF[o.id];
  if (!cabOpen(o.id)) return 'OUT OF ORDER · PLAY IT AFTER ' + d.after.toUpperCase();
  return 'PLAY ' + d.title + (d.price ? ' · ' + fmtN(d.price) : '');
}
const PUB_ROUND = 20000, PUB_PINT = 300;
function pubAct(o) {
  if (!o) return;
  if (o.id === 'player') { hubInvite(o.g); return; }
  if (o.id === 'door') { pubLeave(); return; }
  if (o.id === 'bar') {
    if (PUB.from === 'run') {
      if (PUB.round) { pubSay('Landlord says one round per visit.'); sfx('grab'); return; }
      if (run && run.lives >= MAX_LIVES) { pubSay("You've got all the lives you can carry."); return; }
      if (!pubSpend(PUB_ROUND)) { pubSay('Not enough on your tab. It’s all about the numbers.'); sfx('grab'); return; }
      PUB.round = true; if (run) run.lives++; sfx('life'); pubSay('A round for the lads! EXTRA LIFE', 2.6); return;
    }
    if (!pubSpend(PUB_PINT)) { pubSay('Not enough on your tab for a pint.'); sfx('grab'); return; }
    PUB.pints++; sfx('pickup'); pubSay(PUB.pints === 1 ? 'Lovely. The darts will be a bit wobblier now.' : PUB.pints + ' pints. The dartboard is moving.'); return;
  }
  if (!cabOpen(o.id)) { sfx('grab'); pubSay('OUT OF ORDER. It turns up on the campaign first, after ' + MINI_DEF[o.id].after + '.', 3); return; }
  const d = MINI_DEF[o.id];
  if (d.price && PUB.wallet < d.price) { sfx('grab'); pubSay('Not enough on your tab. ' + fmtN(d.price) + ' a go.'); return; }
  openMini(o.id, 'pub', () => { mode = 'pub'; modeT = 0; musicSet('social'); });
}
function updatePub(dt) {
  pubTapsIn(); PUB.t += dt; if (PUB.msgT > 0) PUB.msgT -= dt;
  if (PUB.view === 'board') {
    if (modeT > 0.3 && (pubGo() || pubBack() || pressed.has('jump') || pubHits.has('close'))) { PUB.view = null; sfx('page'); }
    return;
  }
  if (pubHits.has('leave') || pressed.has('escape') || pressed.has('back')) { pubLeave(); return; }
  const near = pubNear(); PUB.near = near;
  if (near && (pressed.has('punch') || pressed.has('start') || pubHits.has('act'))) { PUB.target = null; pubAct(near); return; }
  if (near && (pressed.has('jump') || pubHits.has('board')) && MINI_DEF[near.id]) { PUB.view = 'board'; PUB.boardGame = near.id; modeT = 0; sfx('page'); return; }
  // walking: the stick or arrows, or tap where to go
  const inp = readInput(); let ix = inp.ix, iy = inp.iy; PUB.target = null;
  const runK = (held.has('run') || (pubPadTouch() && stickRun())) ? 1.6 : 1;
  const sway = PUB.pints > 1 ? Math.sin(PUB.t * 1.7) * Math.min(4, PUB.pints) * 12 : 0;
  PUB.x = clamp(PUB.x + ix * 270 * runK * dt + sway * dt, 30, PUB_W - 40);
  PUB.y = clamp(PUB.y + iy * 150 * dt, 436, 500);
  PUB.moving = !!(ix || iy);
  if (ix) PUB.face = ix;
  if (PUB.moving) PUB.walk += dt * 11;
  cam.x = clamp(PUB.x - W / 2, 0, PUB_W - W);
}
function pubDrawWorld() {
  const cx = cam.x, wall = bgImg('social/wall');
  ctx.fillStyle = '#1c120b'; ctx.fillRect(0, 0, W, 104);
  for (let wx = Math.floor(cx / 160) * 160; wx < cx + W + 160; wx += 160) { ctx.fillStyle = '#2c1c12'; ctx.fillRect(snap2(wx - cx), 0, 18, 100); ctx.fillStyle = '#3a2618'; ctx.fillRect(snap2(wx - cx), 0, 4, 100); }
  ctx.fillStyle = '#3a2416'; ctx.fillRect(0, 96, W, 10); ctx.fillStyle = '#5a3a22'; ctx.fillRect(0, 96, W, 2);
  if (wall) {
    const w = wall.width * 2, h = wall.height * 2;
    ctx.save(); ctx.imageSmoothingEnabled = false;
    for (let wx = Math.floor(cx / w) * w; wx < cx + W; wx += w) {
      const x = snap2(wx - cx);
      ctx.drawImage(wall, 0, 0, wall.width, 20, x, 106, w, 40);
      ctx.drawImage(wall, x, PUB_FLOOR - h, w, h);
    }
    ctx.restore();
  }
  // the floor: dark boards, staggered joins
  ctx.fillStyle = '#3e2618'; ctx.fillRect(0, PUB_FLOOR, W, H - PUB_FLOOR);
  for (let y = PUB_FLOOR, r = 0; y < H; y += 22, r++) {
    ctx.fillStyle = r % 2 ? '#47301e' : '#422b1b'; ctx.fillRect(0, y + 2, W, 18);
    ctx.fillStyle = '#2a190f'; ctx.fillRect(0, y, W, 2);
    for (let wx = Math.floor(cx / 180) * 180 - (r % 2) * 90; wx < cx + W + 180; wx += 180) ctx.fillRect(snap2(wx - cx), y, 2, 22);
  }
  ctx.fillStyle = '#2a190f'; ctx.fillRect(0, PUB_FLOOR, W, 6);
  // the room, left to right: window, bar, darts, fruit machine, the arcade corner
  const win = bgImg('set/window'); if (win) bgPut(win, 110, 330);
  const bar = bgImg('social/bar'); if (bar) bgPut(bar, 300, 420);
  const db = bgImg('set/dartboard'); if (db) bgPut(db, 960 - db.width, 330);
  // the oche
  { const x = snap2(960 - 70 - cx); ctx.fillStyle = '#c8b070'; ctx.fillRect(x, 506, 140, 4); }
  for (const id of ['darts', 'fruit', 'pens', 'golf', 'awake', 'kiss']) { const c = pubChalkX(id), img = pubImg('chalk'); if (img) bgPut(img, c - img.width, CHALK_B); }
  const fr = bgImg('social/fruit'); if (fr) bgPut(fr, 1300 - fr.width, 414);
  const cab = pubImg('cabinet');
  for (const id of ['pens', 'golf', 'awake', 'kiss']) {
    const o = PUB_OBJ.find(o => o.id === id); if (!cab) break;
    bgPut(cab, o.x - cab.width, 414);
    // the screen: dark when it's out of order, the record holder's colours when it's lit
    const sx = snap2(o.x - 10 - cx), sy = 414 - 176 + 52;
    if (!cabOpen(id)) { ctx.fillStyle = '#0a0c10'; ctx.fillRect(sx, sy, 30, 26); }
    else { ctx.fillStyle = 'rgba(80,160,255,' + (0.18 + 0.08 * Math.sin(time * 3 + o.x)).toFixed(2) + ')'; ctx.fillRect(sx, sy, 30, 26); }
  }
  // everyone else who's online, then you, back to front
  const people = hubGhosts().map(g => ({ y: g.y, f: () => pubLad(g.lad, g.x - cx, g.y, g.moving ? 'walk' : 'idle', g.face, g.walk) }));
  people.push({ y: PUB.y, f: () => pubLad(PUB.lad, PUB.x - cx, PUB.y, PUB.moving ? 'walk' : 'idle', PUB.face, PUB.walk, 1, PUB.pints > 2 ? { state: 'drowsy' } : null) });
  people.sort((a, b) => a.y - b.y); for (const p of people) p.f();
}
const pubChalkX = id => id === 'darts' ? 1130 : PUB_OBJ.find(o => o.id === id).x;
const CHALK_B = 238;   // the chalkboards' bottom edge on the wall
function pubChalkText(id) {
  const cx = cam.x, img = pubImg('chalk'), sl = PUB_STRIPS.chalk_slate; if (!img || !sl) return;
  const L = pubChalkX(id) - img.width - cx, T = CHALK_B - img.height * 2, x0 = L + sl[0] * 2 + 6, x1 = L + sl[2] * 2 - 6, y0 = T + sl[1] * 2 + 4, y1 = T + sl[3] * 2 - 2;
  if (x1 < -20 || x0 > W + 20) return;
  const d = MINI_DEF[id], list = pubBoard(id).slice(0, 3), mid = (x0 + x1) / 2, lh = (y1 - y0) / 5.2;
  ctx.save(); ctx.textBaseline = 'middle'; ctx.shadowColor = 'rgba(255,255,255,0.15)'; ctx.shadowBlur = 2;
  ctx.font = '12px ' + DISPLAY; ctx.fillStyle = '#f6f0dc'; ctx.textAlign = 'center'; ctx.fillText(d.short + (cabOpen(id) ? '' : ' SOON'), mid, y0 + lh * 0.55);
  ctx.fillStyle = 'rgba(246,240,220,0.5)'; ctx.fillRect(mid - 24, y0 + lh * 1.05, 48, 1);
  ctx.font = '700 11px ' + BODY;
  if (!list.length) { ctx.fillStyle = 'rgba(246,240,220,0.75)'; ctx.fillText('NO SCORES YET', mid, y0 + lh * 2.5); }
  list.forEach((e, i) => {
    const y = y0 + lh * (1.75 + i);
    ctx.textAlign = 'left'; ctx.fillStyle = i === 0 ? '#ffe680' : '#efe8d4'; ctx.fillText((i + 1) + ' ' + e.name.slice(0, 7), x0, y);
    ctx.textAlign = 'right'; ctx.fillText(fmtN(e.score), x1, y);
  });
  const pb = PUB.pb[id]; if (pb) { ctx.textAlign = 'center'; ctx.fillStyle = '#9fd0ff'; ctx.fillText('YOU ' + fmtN(pb) + (d.unit ? ' ' + d.unit : ''), mid, y0 + lh * 4.7); }
  ctx.restore();
}
function drawPub() {
  pubPixel(pubDrawWorld);
  PUI = [];
  const cx = cam.x;
  // sharp text over the room: the pub's name, chalkboards, cabinet marquees and the record holders' faces
  { const x = 540 - cx; if (x > -200 && x < W + 200) textOut('THE HARVEST MOON', x, 128, '26px ' + DISPLAY, '#ffd23f', OUT, 6); }
  for (const id of ['darts', 'fruit', 'pens', 'golf', 'awake', 'kiss']) pubChalkText(id);
  for (const id of ['pens', 'golf', 'awake', 'kiss']) {
    const o = PUB_OBJ.find(o => o.id === id), x = o.x - cx; if (x < -60 || x > W + 60) continue;
    ctx.font = '9px ' + DISPLAY; ctx.fillStyle = '#2a1a06'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(MINI_DEF[id].short, x + 10, 414 - 176 + 29);
    if (!cabOpen(id)) { ctx.save(); ctx.translate(x + 4, 414 - 176 + 64); ctx.rotate(-0.12); ctx.fillStyle = '#efe6d2'; ctx.fillRect(-26, -9, 52, 18); ctx.font = '800 8px ' + BODY; ctx.fillStyle = '#b23a32'; ctx.fillText('OUT OF', 0, -3); ctx.fillText('ORDER', 0, 5); ctx.restore(); continue; }
    const top = pubBoard(id)[0]; if (top) drawPortrait(top.lad, x - 8, 414 - 176 + 54, 26, '#ffd23f');
  }
  hubTags();
  chatBubbles();
  // the prompt by whatever you're stood at
  const o = PUB.near, label = pubPrompt(o);
  if (label && !PUB.view) {
    const w = Math.max(300, Math.min(700, label.length * 11 + 120)), x = W / 2 - w / 2, y = H - 92;
    pubPanel(x, y, w, 62);
    textOut(label, W / 2, y + 22, '17px ' + DISPLAY, '#efe6d2', OUT, 4);
    ctx.font = '800 11px ' + BODY; ctx.fillStyle = '#ffd23f'; ctx.textAlign = 'center';
    ctx.fillText(o.id === 'player' && !hubCanInvite(o.g) ? '' : (touchUI ? 'HIT' : 'J / ENTER') + (MINI_DEF[o.id] ? '  ·  JUMP FOR THE FULL BOARD' : ''), W / 2, y + 47);
  }
  pubTabHud();
  hubCountHud();
  if (PUB.from === 'run' && run) { pubPanel(16, 14, 170, 52); ctx.font = '800 11px ' + BODY; ctx.fillStyle = '#93a3a1'; ctx.textAlign = 'left'; ctx.fillText('LIVES', 30, 30); textOut(String(run.lives), 30, 47, '22px ' + DISPLAY, '#7fe07a', OUT, 5, 'left'); ctx.fillStyle = '#93a3a1'; ctx.fillText(run.c.name, 72, 47); }
  if (touchUI && !padOn()) pubBtn('leave', PUB.from === 'run' ? 200 : 16, 14, 110, 40, PUB.from === 'run' ? 'CARRY ON' : 'LEAVE');
  if (PUB.msgT > 0 && PUB.msg) { const a = Math.min(1, PUB.msgT / 0.3); ctx.save(); ctx.globalAlpha = a; textOut(PUB.msg, W / 2, 92, '18px ' + DISPLAY, '#ffd23f', OUT, 5); ctx.restore(); }
  if (PUB.view === 'board') drawPubBoard(PUB.boardGame); else if (pubPadTouch()) drawTouch();
}
function drawPubBoard(g) {
  const d = MINI_DEF[g], shared = PUBB.kind === 'fb' || PUBB.kind === 'claude';
  ctx.fillStyle = 'rgba(8,12,14,0.94)'; ctx.fillRect(0, 0, W, H);
  textOut(d.title, W / 2, 50, '36px ' + DISPLAY, '#f2a23a', OUT, 7);
  ctx.font = '600 12px ' + BODY; ctx.fillStyle = '#93a3a1'; ctx.textAlign = 'center';
  ctx.fillText(d.board + ' · ALL TIME · EVERYONE’S BEST' + (shared ? '' : ' · THIS PHONE'), W / 2, 82);
  const list = pubBoard(g), u = d.unit ? ' ' + d.unit : '', me = PROFILE.name, x0 = W / 2 - 290, x1 = W / 2 + 290;
  ctx.textBaseline = 'middle';
  if (!list.length) { ctx.font = '600 15px ' + BODY; ctx.fillStyle = '#e9dcc0'; ctx.fillText('No scores yet. Be the first on the board.', W / 2, 240); }
  const row = (e, i, y) => {
    const mine = e.name === me;
    if (mine) { rrect(x0 - 14, y - 15, x1 - x0 + 28, 30, 6); ctx.fillStyle = 'rgba(242,162,58,0.22)'; ctx.fill(); }
    else if (i % 2 === 0) { ctx.fillStyle = 'rgba(255,255,255,0.04)'; ctx.fillRect(x0 - 14, y - 15, x1 - x0 + 28, 30); }
    textOut(String(i + 1), x0, y, '16px ' + DISPLAY, i === 0 ? '#ffd23f' : '#efe6d2', OUT, 4, 'left');
    ctx.font = '800 15px ' + BODY; ctx.fillStyle = '#efe6d2'; ctx.textAlign = 'left'; ctx.fillText(e.name + (mine ? '  (YOU)' : ''), x0 + 48, y);
    drawPortrait(e.lad, x0 + 330, y - 11, 22); ctx.font = '800 12px ' + BODY; ctx.fillStyle = CHAR_BY_ID[e.lad].color; ctx.fillText(CHAR_BY_ID[e.lad].name, x0 + 360, y);
    textOut(fmtN(e.score) + u, x1, y, '16px ' + DISPLAY, i === 0 ? '#ffd23f' : '#efe6d2', OUT, 4, 'right');
  };
  list.slice(0, 10).forEach((e, i) => row(e, i, 118 + i * 30));
  const at = list.findIndex(e => e.name === me);
  if (at >= 10) { ctx.fillStyle = '#93a3a1'; ctx.font = '800 14px ' + BODY; ctx.textAlign = 'center'; ctx.fillText('· · ·', W / 2, 420); row(list[at], at, 446); }
  else if (at < 0 && PUB.pb[g]) { ctx.font = '800 13px ' + BODY; ctx.fillStyle = '#9fd0ff'; ctx.textAlign = 'center'; ctx.fillText('YOUR BEST: ' + fmtN(PUB.pb[g]) + u + (shared ? ' (going up when there’s signal)' : ''), W / 2, 446); }
  if (!shared) { ctx.font = '600 11px ' + BODY; ctx.fillStyle = '#93a3a1'; ctx.textAlign = 'center'; ctx.fillText('Scores are saved on this phone until the shared boards are switched on.', W / 2, 472); }
  if (touchUI && !padOn()) pubBtn('close', W / 2 - 60, H - 52, 120, 40, 'CLOSE');
  else if (Math.floor(time * 2) % 2) { ctx.font = '800 13px ' + BODY; ctx.fillStyle = '#ffd23f'; ctx.textAlign = 'center'; ctx.fillText('J TO GO BACK', W / 2, H - 32); }
}

// ================================================================== the games
let MG = null;
function openMini(id, from, next) {
  const d = MINI_DEF[id]; pubPreload(); pubBoardsStart();
  if (from === 'pub' && d.price && !pubSpend(d.price)) return false;
  const lad = d.lad || (from === 'run' && run ? run.c.id : PUB.lad);
  MG = { id, d, from, next, lad, phase: 'intro', t: 0, score: 0, s: {}, res: null, saved: null, paid: 0 };
  if (from === 'run') PUB.cabs[id] = true, pubSave();
  MGAME[id].init(MG);
  mode = 'mini'; modeT = 0; banner = null; musicSet(d.music || null);
  return true;
}
function miniEnd(reason) {
  if (!MG || MG.phase !== 'play') return;
  MG.phase = 'result'; MG.t = 0; MG.reason = reason || '';
  const sc = Math.max(0, Math.round(MG.score));
  const pay = MG.forfeit ? 0 : Math.round(MG.d.pay(sc) * (MG.from === 'run' ? 2 : 1));
  MG.paid = pay;
  if (pay > 0) { if (MG.from === 'run') { if (run) addScore(pay, true); } else pubBank(pay); }
  if (!MG.forfeit) pubRecord(MG.id, MG.lad, MG.id === 'fruit' ? MG.s.best || 0 : sc, r => { if (MG) MG.res = r; });
  musicSet(null); sfx(pay > 0 ? 'life' : 'ko');
}
function updateMiniGame(dt) {
  pubTapsIn(); if (!MG) { mode = 'select'; return; }
  MG.t += dt;
  if (MG.phase === 'intro') {
    if (pubBack() && MG.from === 'pub') { if (MG.d.price) pubBank(MG.d.price); closeMini(); return; }
    if (MG.t > 0.5 && (pubGo() || pressed.has('jump'))) { MG.phase = 'play'; MG.t = 0; sfx('start'); }
    return;
  }
  if (MG.phase === 'play') {
    if (pressed.has('escape') || (pressed.has('back') && !pubStick()) || pubHits.has('quit')) { if (MG.id === 'fruit') { miniEnd('CASHED OUT'); return; } MG.forfeit = true; MGAME[MG.id].quit && MGAME[MG.id].quit(MG); miniEnd('Gave up'); return; }
    try { MGAME[MG.id].update(MG, dt); } catch (e) { glitch('mini ' + MG.id, e); miniEnd('Glitch'); }
    return;
  }
  if (MG.phase === 'result' && MG.t > 1.2 && (pubGo() || pubBack())) closeMini();
}
function closeMini() { const n = MG && MG.next; MG = null; pubPtr.clear(); if (n) n(); else { mode = 'select'; modeT = 0; } }
function drawMiniGame() {
  PUI = [];
  if (!MG) return;
  const G = MGAME[MG.id];
  pubPixel(() => G.draw(MG));
  try { G.hud(MG); } catch (e) { glitch('mini hud', e); }
  if (MG.phase === 'play' && pubPadTouch()) { if (pubStick()) { drawTouch(); pubBtn('quit', W / 2 + 140, 16, 92, 34, 'QUIT'); } else pubBtn('quit', 14, H - 50, 92, 36, MG.id === 'fruit' ? 'CASH OUT' : 'QUIT'); }
  if (MG.phase === 'intro') drawMiniIntro();
  if (MG.phase === 'result') drawMiniResult();
}
function drawMiniIntro() {
  const d = MG.d;
  ctx.fillStyle = 'rgba(8,12,14,0.86)'; ctx.fillRect(0, 0, W, H);
  if (MG.from === 'run') textOut('BONUS ROUND', W / 2, 70, '20px ' + DISPLAY, '#7fe07a', OUT, 5);
  textOut(d.title, W / 2, 112, '44px ' + DISPLAY, '#f2a23a', OUT, 8);
  drawPortrait(MG.lad, W / 2 - 40, 146, 80, CHAR_BY_ID[MG.lad].color);
  ctx.font = '600 16px ' + BODY; ctx.fillStyle = '#efe6d2'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  d.how.forEach((l, i) => ctx.fillText(l, W / 2, 268 + i * 28));
  const tch = touchUI && !padOn();
  ctx.font = '800 13px ' + BODY; ctx.fillStyle = '#93a3a1'; ctx.fillText(tch ? d.touch : d.keys, W / 2, 372);
  const pb = PUB.pb[MG.id]; if (pb) { ctx.fillStyle = '#9fd0ff'; ctx.fillText('YOUR BEST: ' + fmtN(pb) + (d.unit ? ' ' + d.unit : ''), W / 2, 400); }
  ctx.fillStyle = '#93a3a1'; ctx.font = '600 12px ' + BODY;
  ctx.fillText(MG.from === 'run' ? 'Free, and the points go on your score (double).' : MG.id === 'fruit' ? '500 a spin from your tab of ' + fmtN(PUB.wallet) + '.' : fmtN(d.price) + ' paid from your tab. Winnings go back on it.', W / 2, 426);
  if (tch) pubBtn('go', W / 2 - 80, 450, 160, 48, "LET'S GO", true);
  else if (Math.floor(time * 2) % 2) { ctx.font = '800 15px ' + BODY; ctx.fillStyle = '#ffd23f'; ctx.fillText((padOn() ? 'HIT' : 'J') + ' TO START', W / 2, 470); }
}
function drawMiniResult() {
  const d = MG.d, k = clamp(MG.t / 0.4, 0, 1), u = d.unit ? ' ' + d.unit : '';
  ctx.save(); ctx.globalAlpha = k;
  ctx.fillStyle = 'rgba(8,12,14,0.86)'; ctx.fillRect(0, 0, W, H);
  textOut(MG.forfeit ? 'GAVE UP' : MG.reason || 'FULL TIME', W / 2, 96, '40px ' + DISPLAY, '#f2a23a', OUT, 8);
  const sc = MG.id === 'fruit' ? (MG.s.best || 0) : Math.round(MG.score);
  ctx.font = '800 13px ' + BODY; ctx.fillStyle = '#93a3a1'; ctx.textAlign = 'center'; ctx.fillText(MG.id === 'fruit' ? 'BIGGEST WIN' : 'SCORE', W / 2, 150);
  textOut(fmtN(sc) + u, W / 2, 190, '46px ' + DISPLAY, '#ffd23f', OUT, 8);
  const r = MG.res;
  if (r && r.newBest) textOut('NEW PERSONAL BEST!', W / 2, 250, '24px ' + DISPLAY, '#7fe07a', OUT, 5);
  if (r && r.place) { ctx.font = '800 15px ' + BODY; ctx.fillStyle = r.place <= 5 ? '#ffd23f' : '#efe6d2'; ctx.fillText(r.place === 1 ? 'TOP OF THE BOARD. Your face is on the cabinet.' : 'Number ' + r.place + ' on the board' + (r.place <= 5 ? '. On the chalkboard!' : '.'), W / 2, 286); }
  if (MG.paid > 0) { ctx.font = '800 15px ' + BODY; ctx.fillStyle = '#efe6d2'; ctx.fillText(MG.from === 'run' ? '+' + fmtN(MG.paid) + ' POINTS' : '+' + fmtN(MG.paid) + ' ON YOUR TAB', W / 2, 330); }
  if (MG.from === 'pub' || MG.id === 'fruit') { ctx.font = '600 13px ' + BODY; ctx.fillStyle = '#93a3a1'; ctx.fillText('Tab: ' + fmtN(PUB.wallet), W / 2, 358); }
  if (MG.from === 'run' && !MG.forfeit) { ctx.font = '600 13px ' + BODY; ctx.fillStyle = '#9fd0ff'; ctx.fillText('The ' + d.title.toLowerCase() + ' cabinet is now open in the pub.', W / 2, 386); }
  if (MG.t > 1.2) {
    if (touchUI && !padOn()) pubBtn('go', W / 2 - 80, 430, 160, 48, 'CARRY ON', true);
    else if (Math.floor(time * 2) % 2) { ctx.font = '800 15px ' + BODY; ctx.fillStyle = '#ffd23f'; ctx.fillText((padOn() ? 'HIT' : 'J') + ' TO CARRY ON', W / 2, 454); }
  }
  ctx.restore();
}
function pubFlash(s, text, col, t) { s.msg = text; s.msgCol = col || '#ffd23f'; s.msgT = t || 1.4; }
function drawGameMsg(s, y) { if (s.msgT > 0 && s.msg) { ctx.save(); ctx.globalAlpha = Math.min(1, s.msgT / 0.25); textOut(s.msg, W / 2, y || 120, '30px ' + DISPLAY, s.msgCol || '#ffd23f', OUT, 7); ctx.restore(); } }

const MGAME = {};

// ------------------------------------------------------------------ NINE DARTS
const DART_R = { bull: 3, obull: 7, tin: 44, tout: 48, din: 72, dout: 76, rim: 92 };   // board pixels, as tools/v55/art.py draws it
const DART_ORDER = [20, 1, 18, 4, 13, 6, 10, 15, 2, 17, 3, 19, 7, 16, 8, 11, 14, 9, 12, 5];
const DBX = 480, DBY = 262;
function dartScore(x, y) {
  const dx = (x - DBX) / 2, dy = (y - DBY) / 2, r = Math.hypot(dx, dy);
  if (r <= DART_R.bull) return [50, 'BULLSEYE!'];
  if (r <= DART_R.obull) return [25, 'OUTER BULL'];
  if (r > DART_R.dout) return [0, r > DART_R.rim ? 'MISSED THE BOARD' : 'BOUNCED OUT'];
  const a = ((Math.atan2(dx, -dy) * 180 / Math.PI) + 369) % 360, n = DART_ORDER[Math.floor(a / 18)];
  if (r > DART_R.tin && r <= DART_R.tout) return [n * 3, 'TREBLE ' + n];
  if (r > DART_R.din) return [n * 2, 'DOUBLE ' + n];
  return [n, String(n)];
}
MGAME.darts = {
  init(M) { M.s = { ax: DBX, ay: DBY - 92, darts: [], n: 0, visit: 0, visits: [], fly: null, wait: 0, msgT: 0, drag: null, sw: 0 }; },
  sway(M) { const s = M.s, A = 15 + PUB.pints * 9, t = M.t; return [A * Math.sin(t * 1.7) + A * 0.45 * Math.sin(t * 4.1 + 1), A * 0.8 * Math.sin(t * 2.3 + 0.5) + A * 0.35 * Math.sin(t * 5.3)]; },
  update(M, dt) {
    const s = M.s; if (s.msgT > 0) s.msgT -= dt;
    if (s.fly) {
      s.fly.t += dt;
      if (s.fly.t >= 0.22) {
        const [v, label] = dartScore(s.fly.x, s.fly.y); sfx('dart'); if (v === 0) sfx('grab');
        s.darts.push({ x: s.fly.x, y: s.fly.y, v, label, out: v === 0 && label !== 'MISSED THE BOARD' });
        s.visit += v; M.score += v; s.n++; s.fly = null;
        pubFlash(s, v ? label + (v > 3 && label.length > 3 ? ' · ' + v : '') : label, v >= 50 ? '#7fe07a' : v ? '#ffd23f' : '#ff7a5a', 1.1);
        if (s.darts.length % 3 === 0) { s.wait = 1.6; if (s.visit === 180) { pubFlash(s, 'ONE HUNDRED AND EIGHTY!', '#ff5a3c', 2.2); sfx('airhorn'); } else pubFlash(s, 'VISIT: ' + s.visit, '#ffd23f', 1.5); s.visits.push(s.visit); }
      }
      return;
    }
    if (s.wait > 0) { s.wait -= dt; if (s.wait <= 0) { if (s.n >= 9) { miniEnd(M.score >= 300 ? 'TON-PLUS PLAYER' : 'GAME SHOT'); return; } s.darts = []; s.visit = 0; } return; }
    // aim: the stick, or drag a finger; throw: HIT, or let go
    const inp = readInput(); s.ax = clamp(s.ax + inp.ix * 160 * dt, DBX - 200, DBX + 200); s.ay = clamp(s.ay + inp.iy * 160 * dt, DBY - 200, DBY + 200);
    const go = pressed.has('punch') || pressed.has('start');
    if (go) { const [wx, wy] = this.sway(M); s.fly = { x: s.ax + wx + rand(-2, 2), y: s.ay + wy + rand(-2, 2), t: 0 }; sfx('throw'); }
  },
  draw(M) {
    const s = M.s;
    ctx.fillStyle = '#2a1a10'; ctx.fillRect(0, 0, W, H);
    const wall = bgImg('social/wall');
    if (wall) { ctx.save(); ctx.imageSmoothingEnabled = false;   // lamp-free wallpaper from the wall's left side, tiled; the panelling along the bottom
      for (let y = 0; y < 400; y += 80) for (let x = 0; x < W; x += 160) ctx.drawImage(wall, 0, 20, 80, 40, x, y, 160, 80);
      for (let x = 0; x < W; x += 160) ctx.drawImage(wall, 0, 88, 80, 40, x, 460, 160, 80);
      ctx.restore(); }
    // the cabinet doors open round the board, then the board
    ctx.fillStyle = '#5a3a22'; ctx.fillRect(DBX - 250, DBY - 230, 500, 470); ctx.fillStyle = '#3a2416'; ctx.fillRect(DBX - 236, DBY - 216, 472, 442); ctx.fillStyle = '#33200f'; for (let y = DBY - 210; y < DBY + 222; y += 18) ctx.fillRect(DBX - 236, y, 472, 2);
    ctx.fillStyle = '#2e6a3a'; ctx.fillRect(DBX - 380, DBY - 230, 120, 470); ctx.fillRect(DBX + 260, DBY - 230, 120, 470);
    ctx.fillStyle = '#1e4a28'; ctx.fillRect(DBX - 372, DBY - 222, 104, 454); ctx.fillRect(DBX + 268, DBY - 222, 104, 454);
    const b = pubImg('dartboard'); if (b) { ctx.save(); ctx.imageSmoothingEnabled = false; ctx.drawImage(b, snap2(DBX - b.width), snap2(DBY - b.height), b.width * 2, b.height * 2); ctx.restore(); }
    const dt = pubImg('dart');
    for (const d of s.darts) if (dt && !d.out) { ctx.save(); ctx.imageSmoothingEnabled = false; ctx.drawImage(dt, snap2(d.x - dt.width * 2), snap2(d.y - dt.height * 4 + 4), dt.width * 4, dt.height * 4); ctx.restore(); }
    if (s.fly) {
      const k = s.fly.t / 0.22, x = lerp(720, s.fly.x, k), y = lerp(540, s.fly.y, k) - Math.sin(k * Math.PI) * 60, df = pubImg('dart_fly');
      if (df) { const z = Math.max(1, Math.round(6 - k * 4)); ctx.save(); ctx.imageSmoothingEnabled = false; ctx.translate(snap2(x), snap2(y)); ctx.rotate(-2.4); ctx.drawImage(df, 0, 0, df.width * z, df.height * z); ctx.restore(); }
    }
  },
  hud(M) {
    const s = M.s;
    // the numbers round the board
    ctx.save(); ctx.font = '15px ' + DISPLAY; ctx.fillStyle = '#efe6d2'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    DART_ORDER.forEach((n, i) => { const a = i * 18 * Math.PI / 180, r = 168; ctx.fillText(String(n), DBX + Math.sin(a) * r, DBY - Math.cos(a) * r); });
    ctx.restore();
    if (M.phase === 'play' && !s.fly && s.wait <= 0) {
      const [wx, wy] = this.sway(M), x = s.ax + wx, y = s.ay + wy;
      ctx.save(); ctx.strokeStyle = 'rgba(255,240,180,0.95)'; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(x, y, 9, 0, Math.PI * 2); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(x - 16, y); ctx.lineTo(x - 5, y); ctx.moveTo(x + 5, y); ctx.lineTo(x + 16, y); ctx.moveTo(x, y - 16); ctx.lineTo(x, y - 5); ctx.moveTo(x, y + 5); ctx.lineTo(x, y + 16); ctx.stroke();
      ctx.fillStyle = 'rgba(255,90,60,0.9)'; ctx.fillRect(x - 1, y - 1, 2, 2); ctx.restore();
    }
    pubPanel(16, 14, 170, 120);
    ctx.font = '800 11px ' + BODY; ctx.fillStyle = '#93a3a1'; ctx.textAlign = 'left'; ctx.textBaseline = 'middle';
    ctx.fillText('TOTAL', 30, 32); textOut(String(M.score), 30, 56, '28px ' + DISPLAY, '#ffd23f', OUT, 5, 'left');
    ctx.font = '800 11px ' + BODY; ctx.fillStyle = '#93a3a1'; ctx.textAlign = 'left'; ctx.fillText('DARTS LEFT', 30, 86); ctx.fillStyle = '#efe6d2'; ctx.font = '15px ' + DISPLAY; ctx.fillText('| '.repeat(9 - s.n).trim() || '-', 30, 108);
    pubPanel(W - 186, 14, 170, 40 + s.visits.length * 22);
    ctx.font = '800 11px ' + BODY; ctx.fillStyle = '#93a3a1'; ctx.fillText('VISITS', W - 172, 32);
    s.visits.forEach((v, i) => { ctx.font = '15px ' + DISPLAY; ctx.fillStyle = v >= 100 ? '#7fe07a' : '#efe6d2'; ctx.fillText((i + 1) + '.  ' + v, W - 172, 54 + i * 22); });
    if (PUB.pints) { ctx.font = '800 12px ' + BODY; ctx.fillStyle = '#f2a23a'; ctx.textAlign = 'right'; ctx.fillText(PUB.pints + (PUB.pints === 1 ? ' PINT' : ' PINTS') + ' IN', W - 20, H - 24); }
    drawGameMsg(s, 470);
  },
};

// ------------------------------------------------------------------ FRUIT MACHINE
const FR_SYMS = ['cherry', 'lemon', 'grapes', 'bell', 'bar', 'seven', 'marc'];
const FR_PAY = { cherry: 8, lemon: 10, grapes: 12, bell: 20, bar: 30, seven: 80, marc: 200 };
const FR_REEL = ['cherry', 'lemon', 'grapes', 'cherry', 'bell', 'lemon', 'bar', 'cherry', 'grapes', 'seven', 'lemon', 'cherry', 'grapes', 'bell', 'marc', 'bar'];
const FR_STAKE = 500, FRX = 320, FRY = 70;   // the machine face's top left, in game units (it is drawn 1:1)
const FR_WIN = { x: FRX + 80, y: FRY + 116, w: 152, h: 96 };   // the reel panel over the face's three windows
MGAME.fruit = {
  init(M) { M.s = { p: [rand(0, 16) | 0, rand(0, 16) | 0, rand(0, 16) | 0], spin: null, hold: [false, false, false], holds: false, nudges: 0, last: 0, best: 0, msgT: 0, lights: 0 }; },
  sym(i, p) { return FR_REEL[((Math.round(p) % 16) + 16) % 16]; },
  line(M) { return M.s.p.map((p, i) => this.sym(i, p)); },
  win(L) {
    if (L[0] === L[1] && L[1] === L[2]) return FR_PAY[L[0]];
    if (L.filter(x => x === 'cherry').length === 2) return 2;
    return 0;
  },
  settle(M) {
    const s = M.s, L = this.line(M), x = this.win(L);
    if (x) {
      const won = x * FR_STAKE; pubBank(won); s.last = won; s.best = Math.max(s.best, won); M.score = s.best; s.lights = 2;
      if (L[0] === 'marc' && L[1] === 'marc' && L[2] === 'marc') { pubFlash(s, 'THREE MARCS! JACKPOT!', '#ff5a3c', 3); sfx('jackpot'); sfx('airhorn'); sfx('meh'); }
      else { pubFlash(s, 'WIN ' + fmtN(won), '#7fe07a', 1.8); sfx('jackpot'); }
      s.hold = [false, false, false]; s.holds = false; s.nudges = 0;
      return true;
    }
    return false;
  },
  update(M, dt) {
    const s = M.s; if (s.msgT > 0) s.msgT -= dt; if (s.lights > 0) s.lights -= dt;
    if (s.spin) {
      s.spin.t += dt; let done = true;
      s.spin.r.forEach((r, i) => {
        if (s.hold[i]) return;
        const k = clamp(s.spin.t / r.dur, 0, 1); if (k < 1) done = false;
        const e = 1 - Math.pow(1 - k, 3); s.p[i] = r.from + (r.to - r.from) * e;
        if (k >= 1 && !r.clunk) { r.clunk = true; s.p[i] = r.to; sfx('thud'); }
      });
      if (done) {
        s.spin = null; const held = s.hold.some(h => h); s.hold = [false, false, false]; s.holds = false;
        if (!this.settle(M)) {
          s.last = 0;
          if (!held && chance(0.32)) { s.holds = true; pubFlash(s, 'HOLDS!', '#ffd23f', 1.4); sfx('pickup'); }
          else if (chance(0.22)) { s.nudges = 1 + (rand(0, 3) | 0); pubFlash(s, s.nudges + (s.nudges === 1 ? ' NUDGE' : ' NUDGES'), '#ffd23f', 1.4); sfx('pickup'); }
        }
      }
      return;
    }
    const reelTap = i => pubHits.has('reel' + i) || pressed.has(['left', 'up', 'right'][i]) || (i === 1 && pressed.has('down'));
    for (let i = 0; i < 3; i++) if (reelTap(i)) {
      if (s.nudges > 0) { s.p[i] = Math.round(s.p[i]) + 1; s.nudges--; sfx('dart'); if (this.settle(M)) s.nudges = 0; }
      else if (s.holds) { s.hold[i] = !s.hold[i]; sfx('page'); }
    }
    if (pressed.has('punch') || pressed.has('start') || pubHits.has('spin')) {
      if (s.nudges > 0) { s.nudges = 0; pubFlash(s, 'NUDGES GONE', '#93a3a1', 1); }
      if (PUB.wallet < FR_STAKE) { pubFlash(s, 'SKINT', '#ff7a5a', 1.6); sfx('grab'); return; }
      pubSpend(FR_STAKE); sfx('brrap');
      s.spin = { t: 0, r: [0, 1, 2].map(i => ({ from: s.p[i], to: Math.round(s.p[i]) + 24 + i * 6 + (rand(0, 16) | 0), dur: 0.8 + i * 0.4 })) };
    }
  },
  symImg(n) { return n === 'marc' ? portraitImg('marc') : pubImg('sym_' + n); },
  draw(M) {
    const s = M.s;
    ctx.fillStyle = '#1a1210'; ctx.fillRect(0, 0, W, H);
    for (let i = 0; i < 12; i++) { ctx.fillStyle = (i + Math.floor(time * 4)) % 2 ? '#2a1a14' : '#24160f'; ctx.fillRect(i * 80, 0, 80, H); }
    const face = pubImg('fruitface'); if (face) { ctx.save(); ctx.imageSmoothingEnabled = false; ctx.drawImage(face, FRX, FRY, face.width * 2, face.height * 2); ctx.restore(); }
    // the reels, three windows on one dark panel
    const R = FR_WIN; ctx.fillStyle = '#16100a'; ctx.fillRect(R.x - 6, R.y - 6, R.w + 12, R.h + 12); ctx.fillStyle = '#c89a3a'; ctx.fillRect(R.x - 6, R.y - 6, R.w + 12, 2); ctx.fillRect(R.x - 6, R.y + R.h + 4, R.w + 12, 2);
    for (let i = 0; i < 3; i++) {
      const x = R.x + i * 52; ctx.fillStyle = '#f4ecd6'; ctx.fillRect(x, R.y, 48, R.h);
      ctx.save(); ctx.beginPath(); ctx.rect(x, R.y, 48, R.h); ctx.clip(); ctx.imageSmoothingEnabled = false;
      const p = s.p[i], base = Math.floor(p), fr = p - base;
      for (let k = -2; k <= 2; k++) {
        const n = FR_REEL[(((base + k) % 16) + 16) % 16], img = this.symImg(n), y = R.y + R.h / 2 - 24 + (k - fr) * 48;
        if (img) ctx.drawImage(img, x, snap2(y), 48, 48);
      }
      ctx.fillStyle = 'rgba(0,0,0,0.28)'; ctx.fillRect(x, R.y, 48, 14); ctx.fillRect(x, R.y + R.h - 14, 48, 14);
      if (s.hold[i]) { ctx.fillStyle = 'rgba(255,210,63,0.25)'; ctx.fillRect(x, R.y, 48, R.h); }
      ctx.restore();
    }
    ctx.fillStyle = s.lights > 0 && Math.floor(time * 10) % 2 ? '#ffe680' : '#d84a3a'; ctx.fillRect(R.x - 6, R.y + R.h / 2 - 1, 4, 2); ctx.fillRect(R.x + R.w + 2, R.y + R.h / 2 - 1, 4, 2);
  },
  hud(M) {
    const s = M.s, R = FR_WIN, tch = touchUI && !padOn();
    for (let i = 0; i < 3; i++) {
      PUI.push({ id: 'reel' + i, x: R.x + i * 52, y: R.y, w: 48, h: R.h });
      if (s.holds || s.nudges) { const x = R.x + i * 52 + 24, y = R.y + R.h + 26; textOut(s.nudges ? 'NUDGE' : s.hold[i] ? 'HELD' : 'HOLD', x, y, '12px ' + DISPLAY, s.hold[i] ? '#7fe07a' : '#ffd23f', OUT, 4); if (!tch) { ctx.font = '700 10px ' + BODY; ctx.fillStyle = '#93a3a1'; ctx.textAlign = 'center'; ctx.fillText(['←', '↑', '→'][i], x, y + 16); } }
    }
    pubTabHud('YOUR TAB');
    pubPanel(16, 14, 236, 236);
    ctx.font = '800 11px ' + BODY; ctx.fillStyle = '#93a3a1'; ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; ctx.fillText('PAYS (500 A SPIN)', 30, 32);
    const rows = [['marc', 'JACKPOT'], ['seven'], ['bar'], ['bell'], ['grapes'], ['lemon'], ['cherry']];
    rows.forEach(([n, l], i) => {
      const y = 56 + i * 26, img = this.symImg(n);
      if (img) { ctx.save(); ctx.imageSmoothingEnabled = false; for (let j = 0; j < 3; j++) ctx.drawImage(img, 30 + j * 22, y - 10, 20, 20); ctx.restore(); }
      ctx.font = '13px ' + DISPLAY; ctx.fillStyle = n === 'marc' ? '#ff5a3c' : '#efe6d2'; ctx.textAlign = 'right'; ctx.fillText(fmtN(FR_PAY[n] * FR_STAKE), 236, y);
    });
    ctx.font = '700 11px ' + BODY; ctx.fillStyle = '#93a3a1'; ctx.textAlign = 'left'; ctx.fillText('Any two cherries: ' + fmtN(2 * FR_STAKE), 30, 238);
    if (s.best) { pubPanel(W - 236, 76, 220, 44); ctx.font = '800 11px ' + BODY; ctx.fillStyle = '#93a3a1'; ctx.textAlign = 'left'; ctx.fillText('BIGGEST WIN', W - 222, 98); textOut(fmtN(s.best), W - 28, 98, '18px ' + DISPLAY, '#7fe07a', OUT, 4, 'right'); }
    if (M.phase === 'play') {
      if (tch) pubBtn('spin', W - 196, H - 92, 170, 60, s.nudges ? 'COLLECT' : 'SPIN', !s.spin, '#7fe07a');
      else { ctx.font = '800 13px ' + BODY; ctx.fillStyle = '#ffd23f'; ctx.textAlign = 'center'; ctx.fillText((padOn() ? 'HIT' : 'J') + ' SPIN  ·  ' + (padOn() ? 'BACK' : 'ESC') + ' CASH OUT', W / 2, H - 24); }
    }
    drawGameMsg(s, 46);
  },
};

// ------------------------------------------------------------------ PENALTIES (Byron v the Parkie)
const GOAL = { l: 278, r: 682, t: 208, b: 370 };   // the goal mouth on the pitch picture, in game units
MGAME.pens = {
  init(M) { M.s = { n: 0, goals: 0, phase: 'x', mx: 0, my: 0, tx: 480, ty: 300, speed: 1, whistle: false, heckle: 0, kickT: 0, ball: null, kdir: 0, kT: -1, res: null, msgT: 0, log: [] }; },
  update(M, dt) {
    const s = M.s; if (s.msgT > 0) s.msgT -= dt; if (s.heckle > 0) s.heckle -= dt;
    const go = pressed.has('punch') || pressed.has('start') || pubFree.length > 0;
    if ((pressed.has('jump') || pressed.has('special') || pubHits.has('whistle')) && !s.whistle && (s.phase === 'x' || s.phase === 'y')) {
      s.whistle = true; s.heckle = 3.5; sfx('whistle'); pubFlash(s, "UNDER 12'S, GET EM!", '#7fe07a', 2);
    }
    if (s.phase === 'x') { s.mx += dt * 0.9 * s.speed; s.tx = 480 + Math.sin(s.mx * Math.PI) * 236; if (go) { s.phase = 'y'; s.my = 0; sfx('page'); } }
    else if (s.phase === 'y') { s.my += dt * 0.8 * s.speed; s.ty = 289 - Math.sin(s.my * Math.PI * 2 - Math.PI / 2) * 108; if (go) { s.phase = 'kick'; s.kickT = 0; sfx('page'); } }
    else if (s.phase === 'kick') {
      s.kickT += dt;
      if (s.kickT >= 0.62 && !s.ball) {
        sfx('heavy'); s.ball = { t: 0 };
        // the Parkie guesses, unless the under-12s have got in his head
        s.kdir = s.heckle > 0 ? 0 : [-1, 0, 1][rand(0, 3) | 0]; s.kT = 0; s.frozen = s.heckle > 0;
      }
      if (s.ball) {
        s.ball.t += dt; if (s.kT >= 0) s.kT += dt;
        if (s.ball.t >= 0.42 && !s.res) this.judge(M);
        if (s.res && s.ball.t > 1.7) { s.n++; if (s.n >= 5) { if (s.goals === 5) { M.score += 2000; } miniEnd(s.goals === 5 ? 'FIVE FROM FIVE' : s.goals + ' FROM 5'); return; } s.phase = 'x'; s.ball = null; s.res = null; s.kT = -1; s.kdir = 0; s.speed *= 1.12; s.mx = rand(0, 2); }
      }
    }
  },
  judge(M) {
    const s = M.s, x = s.tx, y = s.ty, G = GOAL;
    let res;
    if (y < G.t - 6 || x < G.l - 6 || x > G.r + 6) res = y < G.t - 6 ? 'OVER THE BAR' : 'WIDE';
    else if (y < G.t + 6 || x < G.l + 6 || x > G.r - 6) res = 'OFF THE POST';
    else {
      const side = Math.sign(x - 480), off = Math.abs(x - 480), high = y < 260;
      let saved;
      if (s.frozen) saved = off < 36 && y > 280;
      else if (s.kdir === 0) saved = off < 80 && y > 236;
      else saved = side === s.kdir && off < 196 && !(high && off > 150) && chance(0.85);
      res = saved ? 'SAVED' : 'GOAL';
    }
    s.res = res;
    if (res === 'GOAL') {
      const bonus = Math.round(clamp(Math.abs(x - 480) / 202, 0, 1) * 500 + clamp((370 - y) / 162, 0, 1) * 500);
      s.goals++; M.score += 1000 + bonus; s.log.push(1); sfx('jackpot'); pubFlash(s, bonus > 650 ? 'TOP BINS!' : 'GOAL!', '#7fe07a', 1.6);
    } else { s.log.push(0); sfx(res === 'SAVED' ? 'heavy' : 'thud'); pubFlash(s, res === 'SAVED' ? 'SAVED BY THE PARKIE' : res, '#ff7a5a', 1.6); }
  },
  draw(M) {
    const s = M.s, p = pubImg('pitch');
    if (p) { ctx.save(); ctx.imageSmoothingEnabled = false; ctx.drawImage(p, 0, 0, p.width * 2, p.height * 2); ctx.restore(); }
    // the Parkie on his line: ready, then the dive (his left on the sheet, mirrored for the other way)
    const kx = 480, ky = 372;
    if (s.kT >= 0 && s.kdir !== 0) { const f = Math.min(9, Math.floor(s.kT / 0.05)), slide = Math.min(1, s.kT / 0.45) * 70; pubStrip('keeper_dive', f, kx + s.kdir * slide, ky, 2, s.kdir < 0); }
    else pubStrip('keeper_ready', s.frozen ? 0 : Math.floor(time * 4) % 2, kx + (s.frozen ? Math.sin(time * 20) * 2 : 0), ky, 2);
    // the ball: on the spot, then off towards the target, getting smaller
    const ball = bgImg('weapons/ball');
    if (ball) {
      let bx = 470, by = 508, z = 4;
      if (s.ball) {
        const k = clamp(s.ball.t / 0.42, 0, 1);
        if (s.res && s.res !== 'GOAL') { const kk = clamp((s.ball.t - 0.42) / 0.6, 0, 1); bx = lerp(s.tx, s.tx + (s.tx - 480) * 0.6 + 60, kk); by = lerp(s.ty, s.res === 'SAVED' ? 420 : s.ty - 60, kk) - Math.sin(kk * Math.PI) * 40; z = 2; }
        else if (s.res === 'GOAL') { bx = s.tx; by = s.ty + Math.min(10, (s.ball.t - 0.42) * 40); z = 2; }
        else { bx = lerp(470, s.tx, k); by = lerp(508, s.ty, k) - Math.sin(k * Math.PI) * 30; z = k < 0.5 ? 3 : 2; }
      }
      ctx.save(); ctx.imageSmoothingEnabled = false; ctx.fillStyle = 'rgba(10,10,10,0.3)'; if (!s.ball) ctx.fillRect(snap2(bx - 14), snap2(by + 20), 28, 4);
      ctx.drawImage(ball, snap2(bx - ball.width * z / 2), snap2(by - ball.height * z / 2), ball.width * z, ball.height * z); ctx.restore();
    }
    // Byron from behind, big, right in front of you
    const f = s.phase === 'kick' ? Math.min(10, Math.floor(s.kickT / 0.07)) : 0;
    pubStrip('byron_kick', f, 392, 580, 4);
  },
  hud(M) {
    const s = M.s;
    if (M.phase === 'play' && (s.phase === 'x' || s.phase === 'y')) {
      // the aim: a marker sliding along the goal, then up and down at the side you picked
      ctx.save();
      if (s.phase === 'x') { ctx.fillStyle = '#ffd23f'; ctx.beginPath(); ctx.moveTo(s.tx, GOAL.b + 30); ctx.lineTo(s.tx - 12, GOAL.b + 52); ctx.lineTo(s.tx + 12, GOAL.b + 52); ctx.closePath(); ctx.fill(); ctx.strokeStyle = OUT; ctx.lineWidth = 2; ctx.stroke(); ctx.setLineDash([6, 6]); ctx.strokeStyle = 'rgba(255,210,63,0.7)'; ctx.beginPath(); ctx.moveTo(s.tx, GOAL.t - 10); ctx.lineTo(s.tx, GOAL.b + 26); ctx.stroke(); }
      else { ctx.strokeStyle = 'rgba(255,240,180,0.95)'; ctx.lineWidth = 3; ctx.beginPath(); ctx.arc(s.tx, s.ty, 14, 0, Math.PI * 2); ctx.stroke(); ctx.fillStyle = '#ffd23f'; ctx.beginPath(); ctx.moveTo(s.tx + 28, s.ty); ctx.lineTo(s.tx + 48, s.ty - 12); ctx.lineTo(s.tx + 48, s.ty + 12); ctx.closePath(); ctx.fill(); }
      ctx.restore();
    }
    pubPanel(16, 14, 220, 64);
    ctx.font = '800 11px ' + BODY; ctx.fillStyle = '#93a3a1'; ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; ctx.fillText('PENALTIES', 30, 30);
    for (let i = 0; i < 5; i++) { const v = s.log[i]; ctx.fillStyle = v === 1 ? '#7fe07a' : v === 0 ? '#ff5a3c' : '#3a4a52'; circle(38 + i * 26, 54, 9); ctx.fill(); ctx.strokeStyle = OUT; ctx.lineWidth = 2; ctx.stroke(); }
    pubPanel(W - 196, 14, 180, 52); ctx.font = '800 11px ' + BODY; ctx.fillStyle = '#93a3a1'; ctx.fillText('SCORE', W - 182, 30); textOut(fmtN(M.score), W - 30, 46, '22px ' + DISPLAY, '#ffd23f', OUT, 5, 'right');
    if (M.phase === 'play') {
      if (touchUI && !padOn() && !s.whistle) pubBtn('whistle', W - 150, H - 66, 134, 46, 'WHISTLE', false, '#7fe07a');
      ctx.font = '800 13px ' + BODY; ctx.fillStyle = '#efe6d2'; ctx.textAlign = 'center';
      if (s.phase === 'x') ctx.fillText('STOP IT FOR THE SIDE', W / 2, 30); else if (s.phase === 'y') ctx.fillText('STOP IT FOR THE HEIGHT', W / 2, 30);
    }
    drawGameMsg(s, 150);
  },
};

// ------------------------------------------------------------------ THE LONG DRIVE (Pearcy, at the fishery)
const GOLF_TEE = 300, GOLF_YD = 4;   // the tee's world x, game units per yard
MGAME.golf = {
  init(M) { M.s = { ball: 0, best: 0, drives: [], phase: 'ready', m: 0, power: 0, err: 0, pill: false, pillOn: false, fly: null, camX: 0, swingT: -1, msgT: 0, gary: null, goose: { x: GOLF_TEE + rand(160, 260) * GOLF_YD } }; },
  update(M, dt) {
    const s = M.s; if (s.msgT > 0) s.msgT -= dt;
    const go = pressed.has('punch') || pressed.has('start') || pubFree.length > 0;
    const spd = s.pillOn ? 1.8 : 1;
    if ((pressed.has('jump') || pressed.has('special') || pubHits.has('pills')) && !s.pill && s.phase === 'ready') { s.pill = true; s.pillOn = true; sfx('special'); pubFlash(s, 'CARP DIEM!', '#ff5a3c', 1.8); }
    if (s.phase === 'ready') { if (go) { s.phase = 'power'; s.m = 0; sfx('swing'); } }
    else if (s.phase === 'power') { s.m += dt * 1.05 * spd; if (go || s.m >= 1) { s.power = Math.min(1, s.m); s.phase = 'acc'; sfx('page'); } }
    else if (s.phase === 'acc') {
      s.m -= dt * 1.6 * spd;
      if (go || s.m < -0.12) { s.err = s.m - 0.1; this.hit(M); }
    } else if (s.phase === 'swing') {
      s.swingT += dt;
      if (s.swingT > 0.22 && !s.fly) this.launch(M);
    } else if (s.phase === 'fly') {
      const f = s.fly; f.t += dt; const k = clamp(f.t / f.dur, 0, 1);
      f.x = GOLF_TEE + f.yd * GOLF_YD * k; f.y = 430 - Math.sin(k * Math.PI) * f.apex - k * 0;
      s.camX = clamp(f.x - 320, 0, 1e6);
      // Big Gary comes up for a look as it lands
      if (s.gary) { s.gary.t += dt; const g = s.gary, gx = g.x, gy = 500 - Math.sin(clamp(g.t / 1.1, 0, 1) * Math.PI) * 150; if (!g.hit && g.t > 0 && g.t < 1.1 && Math.abs(f.x - gx) < 60 && Math.abs(f.y - gy) < 60) { g.hit = true; f.bonus += 50; pubFlash(s, "BIG GARY'S HAD IT! +50", '#7fe07a', 2); sfx('blub'); } }
      if (k >= 1 && !f.landed) {
        f.landed = true; sfx('splash');
        if (Math.abs(f.x - s.goose.x) < 50) { f.bonus += 25; pubFlash(s, 'GOOSED! +25', '#ffd23f', 2); sfx('honk'); }
        const yd = Math.round(f.yd + f.bonus); s.drives.push(yd); s.best = Math.max(s.best, yd); M.score = s.best; s.landT = 0;
        if (!s.msgT || s.msgT < 0.5) pubFlash(s, yd + ' YARDS', yd >= 300 ? '#7fe07a' : '#ffd23f', 2);
      }
      if (f.landed) { s.landT += dt; if (s.landT > 1.8) { s.ball++; if (s.ball >= 3) { miniEnd(s.best >= 300 ? 'MONSTER DRIVE' : 'THAT’S YOUR LOT'); return; } s.phase = 'ready'; s.fly = null; s.camX = 0; s.swingT = -1; s.pillOn = false; s.gary = null; s.goose.x = GOLF_TEE + rand(160, 280) * GOLF_YD; } }
    }
  },
  hit(M) {
    const s = M.s, e = s.err; s.phase = 'swing'; s.swingT = 0;
    const miss = Math.abs(e) > 0.2;
    s.shot = miss ? (e > 0 ? 'SLICE' : 'HOOK') : Math.abs(e) < 0.035 ? 'PERFECT' : e > 0 ? 'A BIT EARLY' : 'A BIT LATE';
    if (s.power < 0.12) s.shot = 'AIR SHOT';
  },
  launch(M) {
    const s = M.s, e = s.err;
    if (s.shot === 'AIR SHOT') { pubFlash(s, 'AIR SHOT', '#ff7a5a', 1.6); sfx('swing'); s.fly = { t: 0, dur: 0.6, yd: 0, apex: 0, x: GOLF_TEE, y: 430, bonus: 0 }; s.phase = 'fly'; return; }
    const acc = 1 - clamp(Math.abs(e) * 2.6, 0, 0.65);
    const yd = Math.max(20, s.power * 310 * acc * (s.pillOn ? 1.35 : 1) + rand(-6, 6));
    s.fly = { t: 0, dur: 1.1 + yd / 170, yd, apex: 90 + yd * 0.55 * (e > 0 ? 1.3 : e < -0.05 ? 0.7 : 1), x: GOLF_TEE, y: 430, bonus: 0, landed: false };
    s.phase = 'fly'; sfx('heavy'); pubFlash(s, s.shot, s.shot === 'PERFECT' ? '#7fe07a' : '#efe6d2', 1.2);
    if (chance(0.3)) s.gary = { x: GOLF_TEE + yd * GOLF_YD * rand(0.55, 0.85), t: -(s.fly.dur * rand(0.4, 0.6)) };
  },
  draw(M) {
    const s = M.s, cx = s.camX;
    pxSky(['#2a5a9a', '#3a6aa8', '#4a7ab4', '#5a8abe', '#7a9ec6', '#a4b4c4', '#d6c0a0', '#f0c890'], 0, 300);
    ctx.fillStyle = '#2d5a6e'; ctx.fillRect(0, 290, W, 60);
    // the far bank and trees, slow; then the lake
    const tl = bgImg('fishery/treeline');
    if (tl) { const w = tl.width * 2, h = tl.height * 2, off = ((cx * 0.3) % w + w) % w; ctx.save(); ctx.imageSmoothingEnabled = false; for (let x = -off; x < W; x += w) ctx.drawImage(tl, snap2(x), 330 - h, w, h); ctx.restore(); }
    ctx.fillStyle = '#2d5a6e'; ctx.fillRect(0, 330, W, H - 330);
    ctx.fillStyle = '#3a6a7e'; for (let y = 336; y < H; y += 14) ctx.fillRect(0, y, W, 2);
    ctx.fillStyle = 'rgba(255,255,255,0.35)'; for (let i = 0; i < 30; i++) { const x = snap2((((i * 173 - cx * 0.9) % W) + W) % W), y = 344 + (i * 47) % 180; if (Math.sin(time * 1.5 + i) > 0.3) ctx.fillRect(x, y, 8, 2); }
    // distance markers: buoys every 50 yards, labelled in the HUD pass
    for (let yd = 50; yd <= 500; yd += 50) { const x = snap2(GOLF_TEE + yd * GOLF_YD - cx); if (x < -20 || x > W + 20) continue; ctx.fillStyle = OUT; ctx.fillRect(x - 6, 418, 12, 18); ctx.fillStyle = yd % 100 ? '#efe6d2' : '#d84a3a'; ctx.fillRect(x - 4, 420, 8, 14); ctx.fillStyle = '#d84a3a'; ctx.fillRect(x - 4, 420, 8, 4); }
    const goose = bgImg('fishery/goose'); if (goose) bgPutAt(goose, s.goose.x - cx, 452 + Math.sin(time * 2) * 2, false);
    // the bank Pearcy tees off from
    ctx.fillStyle = '#4a7a3a'; ctx.fillRect(snap2(-cx - 40), 430, 470, 120); ctx.fillStyle = '#5a8a46'; ctx.fillRect(snap2(-cx - 40), 430, 470, 6);
    ctx.fillStyle = '#3a2a1a'; ctx.fillRect(snap2(-cx + 420), 430, 10, 120);
    const tee = pubImg('tee'); if (tee) { ctx.save(); ctx.imageSmoothingEnabled = false; ctx.drawImage(tee, snap2(GOLF_TEE - cx - 5), 430 - 10, 10, 10); ctx.restore(); }
    // Pearcy: the swing follows the meter (back) and HIT (through)
    // strip: 0 address, 1-5 backswing, 6 impact, 7-8 finish
    let f = 0;
    if (s.phase === 'power') f = 1 + Math.round(clamp(s.m, 0, 1) * 4);
    else if (s.phase === 'acc') f = 1 + Math.round(clamp(s.power, 0, 1) * 4);
    else if (s.phase === 'swing') f = Math.min(8, 6 + Math.floor(s.swingT / 0.08));
    else if (s.phase === 'fly') f = 8;
    const pe = s.pillOn ? rand(-1.5, 1.5) : 0;
    if (PUB_STRIPS.pearcy_golf) pubStrip('pearcy_golf', f, GOLF_TEE - 34 - cx + pe, 432, 2);
    else pubLad('pearcy', GOLF_TEE - 40 - cx, 432, 'idle', 1, 0);
    // Gary
    if (s.gary && s.gary.t > 0 && s.gary.t < 1.1) { const g = bgImg('fish/gary'); if (g) { const gy = 500 - Math.sin(s.gary.t / 1.1 * Math.PI) * 150; ctx.save(); ctx.imageSmoothingEnabled = false; ctx.translate(snap2(s.gary.x - cx), snap2(gy)); ctx.rotate(-0.45 + s.gary.t / 1.1 * 0.9); ctx.drawImage(g, -g.width, -g.height, g.width * 2, g.height * 2); ctx.restore(); } }
    // the ball
    const gb = pubImg('golfball');
    if (gb) { const bx = s.fly ? s.fly.x : GOLF_TEE, by = s.fly ? s.fly.y : 422; if (!(s.fly && s.fly.landed)) { ctx.save(); ctx.imageSmoothingEnabled = false; ctx.drawImage(gb, snap2(bx - cx - 4), snap2(by - 8), 8, 8); ctx.restore(); } }
    if (s.fly && s.fly.landed && s.landT < 0.6) { const x = s.fly.x - cx, k = s.landT / 0.6; ctx.fillStyle = 'rgba(230,245,255,' + (1 - k).toFixed(2) + ')'; ctx.fillRect(snap2(x - 4 - k * 20), 420 - k * 30, 8, 30 * (1 - k) + 6); ctx.fillRect(snap2(x + 4 + k * 20), 424 - k * 20, 6, 20 * (1 - k) + 4); }
  },
  hud(M) {
    const s = M.s, cx = s.camX;
    ctx.font = '800 12px ' + BODY; ctx.fillStyle = '#efe6d2'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    for (let yd = 50; yd <= 500; yd += 50) { const x = GOLF_TEE + yd * GOLF_YD - cx; if (x > -20 && x < W + 20) { ctx.fillStyle = 'rgba(10,14,16,0.55)'; ctx.fillRect(x - 22, 392, 44, 18); ctx.fillStyle = '#efe6d2'; ctx.fillText(yd + ' yd', x, 401); } }
    if (s.fly && !s.fly.landed) { ctx.font = '22px ' + DISPLAY; ctx.fillStyle = '#ffd23f'; ctx.fillText(Math.round((s.fly.x - GOLF_TEE) / GOLF_YD) + ' yds', W / 2, 70); }
    pubPanel(16, 14, 210, 92);
    ctx.font = '800 11px ' + BODY; ctx.fillStyle = '#93a3a1'; ctx.textAlign = 'left'; ctx.fillText('BALL ' + Math.min(3, s.ball + 1) + ' OF 3', 30, 30);
    ctx.fillText('BEST', 30, 54); textOut(s.best + ' yds', 30, 78, '22px ' + DISPLAY, '#ffd23f', OUT, 5, 'left');
    if (s.drives.length) { ctx.font = '700 11px ' + BODY; ctx.fillStyle = '#efe6d2'; ctx.textAlign = 'right'; ctx.fillText(s.drives.join('  ·  '), 214, 30); }
    // the swing meter: power out to the right, then back to the line
    if (M.phase === 'play' && (s.phase === 'ready' || s.phase === 'power' || s.phase === 'acc')) {
      const mx = W / 2 - 220, my = H - 70, mw = 440, zx = mx + mw * 0.1;
      pubPanel(mx - 14, my - 18, mw + 28, 50);
      ctx.fillStyle = '#1a2428'; ctx.fillRect(mx, my - 4, mw, 18);
      const g = ctx.createLinearGradient(mx, 0, mx + mw, 0); g.addColorStop(0, '#3a8a4a'); g.addColorStop(0.7, '#e8c040'); g.addColorStop(1, '#d84a3a');
      ctx.fillStyle = g; ctx.fillRect(mx, my - 4, mw * (s.phase === 'ready' ? 0 : s.phase === 'power' ? clamp(s.m, 0, 1) : s.power), 18);
      ctx.fillStyle = '#ffffff'; ctx.fillRect(zx - 2, my - 10, 4, 30);
      if (s.phase !== 'ready') { const x = mx + mw * clamp(s.m, -0.12, 1); ctx.fillStyle = '#ffd23f'; ctx.beginPath(); ctx.moveTo(x, my - 12); ctx.lineTo(x - 8, my - 24); ctx.lineTo(x + 8, my - 24); ctx.closePath(); ctx.fill(); }
      ctx.font = '800 12px ' + BODY; ctx.fillStyle = '#efe6d2'; ctx.textAlign = 'center';
      ctx.fillText(s.phase === 'ready' ? 'HIT TO START THE SWING' : s.phase === 'power' ? 'HIT FOR POWER' : 'HIT ON THE WHITE LINE', W / 2, my - 34);
      if (touchUI && !padOn() && !s.pill && s.phase === 'ready') pubBtn('pills', W - 150, H - 140, 134, 46, 'PILLS', false, '#ff5a3c');
    }
    drawGameMsg(s, 130);
  },
};
function bgPutAt(img, x, bottom) { ctx.save(); ctx.imageSmoothingEnabled = false; ctx.drawImage(img, snap2(x - img.width), snap2(bottom - img.height * 2), img.width * 2, img.height * 2); ctx.restore(); }

// ------------------------------------------------------------------ STAY AWAKE (Sam, the 4am drive back on Elba)
MGAME.awake = {
  init(M) {
    M.s = { d: { phase: 'drive', sx: 240, y: ROAD.lanes[1], speed: 520, dents: 0, inv: 0, bounce: 0, tilt: 0,
      crew: ['sam', 'tim', 'seb', 'byron', 'pearcy'].map(id => ({ id, def: CHAR_BY_ID[id] })) },
      x: 0, meter: 100, obs: [], next: 900, lids: 0, cans: 0, msgT: 0, ty: null, endT: -1, why: '' };
  },
  update(M, dt) {
    const s = M.s, d = s.d; if (s.msgT > 0) s.msgT -= dt; if (d.inv > 0) d.inv -= dt; if (d.bounce > 0) d.bounce -= dt;
    if (s.endT >= 0) { s.endT += dt; s.lids = Math.min(1, s.lids + dt * 1.4); d.speed = Math.max(0, d.speed - 500 * dt); s.x += d.speed * dt; if (s.endT > 1.6) miniEnd(s.why); return; }
    const T = M.t; d.speed = Math.min(980, 520 + T * 7); s.x += d.speed * dt; M.score = Math.floor(s.x / 20);
    s.meter -= (6 + T * 0.13) * dt;
    // input: up and down, or tap above or below the car
    const inp = readInput();
    let vy = inp.iy * 330; if (inp.iy) s.ty = null;
    if (s.ty != null) { const dd = s.ty - d.y; vy = Math.abs(dd) < 4 ? 0 : Math.sign(dd) * 330; if (!vy) s.ty = null; }
    // nodding off: the car wanders
    const drowsy = clamp(1 - s.meter / 40, 0, 1); vy += Math.sin(T * 1.3) * 120 * drowsy;
    d.y = clamp(d.y + vy * dt, ROAD.lanes[0] - 10, ROAD.lanes[2] + 10); d.tilt += ((vy / 330 * 0.025) - d.tilt) * Math.min(1, dt * 8);
    s.lids = s.meter < 35 ? clamp((1 - s.meter / 35) * 0.7 + (s.meter < 18 && (T % 2.2) < 0.25 ? 0.3 : 0), 0, 0.98) : Math.max(0, s.lids - dt * 2);
    // traffic, barriers, goats and cans
    while (s.x + W + 200 > s.next) {
      const lane = ROAD.lanes[rand(0, 3) | 0], low = s.meter < 45;
      const kind = chance(low ? 0.42 : 0.28) ? 'can' : ['fiat', 'fiat', 'ape', 'barrier', 'goat'][rand(0, 5) | 0];
      s.obs.push({ kind, x: s.next, y: lane, z: 0, t: 0, v: kind === 'fiat' || kind === 'ape' ? -rand(140, 260) : 0, gy: kind === 'goat' ? (lane === ROAD.lanes[0] ? ROAD.lanes[1] : ROAD.lanes[0]) : null });
      s.next += rand(260, 520) * (1 + T * 0.004);
    }
    const carX = s.x + d.sx;
    for (const o of s.obs) {
      o.t += dt; o.x += o.v * dt;
      if (o.gy != null && o.x - carX < 500) o.y += clamp(o.gy - o.y, -90 * dt, 90 * dt);
      if (o.done || Math.abs(o.x - carX) > (o.kind === 'can' ? 70 : 150) || Math.abs(o.y - d.y) > 28) continue;
      if (o.kind === 'can') { o.done = true; s.cans++; s.meter = Math.min(100, s.meter + 32); sfx('pickup'); pubFlash(s, chance(0.5) ? 'SLURP!' : 'WIDE AWAKE!', '#7fe07a', 1); continue; }
      if (d.inv > 0) continue;
      o.done = true; d.dents++; d.inv = 1.3; d.bounce = 0.4; s.meter = Math.min(100, s.meter + 22); sfx('smash'); sfx('heavy');
      pubFlash(s, d.dents >= 4 ? 'WRITTEN OFF' : ['THAT WOKE HIM UP', 'SORRY! SORRY!', 'WHO PUT THAT THERE?'][d.dents - 1], '#ff7a5a', 1.4);
      if (d.dents >= 4) { s.why = 'WRITTEN OFF'; s.endT = 0; return; }
    }
    s.obs = s.obs.filter(o => o.x > s.x - 300 && !(o.done && o.kind === 'can'));
    if (s.meter <= 0) { s.meter = 0; s.why = 'SLEEPY SAM'; s.endT = 0; pubFlash(s, 'What happened?', '#efe6d2', 2); sfx('ko'); }
  },
  draw(M) {
    const s = M.s, d = s.d, keepS = S, keepCam = cam.x;
    try {
      S = { drv: { phase: 'drive' } }; cam.x = s.x % 27000;
      bgRoadPixel();
    } finally { S = keepS; cam.x = keepCam; }
    // night: everything dark blue, then the headlights
    ctx.fillStyle = 'rgba(6,10,34,0.68)'; ctx.fillRect(0, 0, W, H);
    for (let i = 0; i < 40; i++) { const x = snap2((i * 97 + 13) % W), y = snap2((i * 53) % 220); if (Math.sin(time * 2 + i) > 0.6) { ctx.fillStyle = 'rgba(255,255,230,0.7)'; ctx.fillRect(x, y, 2, 2); } }
    cam.x = s.x;
    const list = [];
    for (const o of s.obs) if (!o.done || o.kind !== 'can') list.push({ y: o.y, f: () => o.kind === 'can' ? this.can(o) : drawObs(o) });
    list.push({ y: d.y, f: () => { const L = d.sx + 150, g = ctx.createLinearGradient(L, 0, L + 360, 0); g.addColorStop(0, 'rgba(255,240,170,0.45)'); g.addColorStop(1, 'rgba(255,240,170,0)'); ctx.fillStyle = g; ctx.beginPath(); ctx.moveTo(L, d.y - 30); ctx.lineTo(L + 360, d.y - 80); ctx.lineTo(L + 360, d.y + 20); ctx.lineTo(L, d.y - 6); ctx.closePath(); ctx.fill(); drawDriveCar(d); } });
    list.sort((a, b) => a.y - b.y);
    try { for (const o of list) o.f(); } finally { cam.x = keepCam; }
  },
  can(o) { const img = pubImg('can'), x = o.x - cam.x; if (!img) return; const bob = Math.sin(time * 5 + o.x) * 4; ctx.save(); ctx.imageSmoothingEnabled = false; ctx.fillStyle = 'rgba(255,240,140,0.25)'; circle(snap2(x), snap2(o.y - 30 + bob), 30); ctx.fill(); ctx.drawImage(img, snap2(x - img.width), snap2(o.y - img.height * 2 + bob), img.width * 2, img.height * 2); ctx.restore(); },
  hud(M) {
    const s = M.s;
    // Sam's eyelids
    if (s.lids > 0.005) { const k = s.lids, h = (H / 2 + 30) * k, curve = 70 * (1 - k); ctx.fillStyle = '#000';
      ctx.beginPath(); ctx.moveTo(-20, -20); ctx.lineTo(W + 20, -20); ctx.lineTo(W + 20, h - curve); ctx.quadraticCurveTo(W / 2, h + curve, -20, h - curve); ctx.closePath(); ctx.fill();
      ctx.beginPath(); ctx.moveTo(-20, H + 20); ctx.lineTo(W + 20, H + 20); ctx.lineTo(W + 20, H - h + curve); ctx.quadraticCurveTo(W / 2, H - h - curve, -20, H - h + curve); ctx.closePath(); ctx.fill(); }
    pubPanel(16, 14, 300, 70);
    ctx.font = '800 11px ' + BODY; ctx.fillStyle = '#93a3a1'; ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; ctx.fillText('AWAKE', 30, 30);
    ctx.fillStyle = '#1a2428'; ctx.fillRect(30, 40, 200, 14);
    ctx.fillStyle = s.meter < 25 ? (Math.floor(time * 6) % 2 ? '#ff5a3c' : '#a83a2a') : s.meter < 50 ? '#e8c040' : '#7fe07a'; ctx.fillRect(30, 40, 200 * clamp(s.meter / 100, 0, 1), 14);
    ctx.fillStyle = '#93a3a1'; ctx.fillText('DENTS ' + s.d.dents + '/4', 30, 70); ctx.fillText('CANS ' + s.cans, 120, 70);
    textOut(fmtN(M.score) + ' m', 300, 46, '22px ' + DISPLAY, '#ffd23f', OUT, 5, 'right');
    if (s.meter < 25 && s.endT < 0) { ctx.save(); ctx.globalAlpha = 0.5 + 0.5 * Math.sin(time * 6); textOut('Zzz', W / 2, 160, '30px ' + DISPLAY, '#efe6d2', OUT, 6); ctx.restore(); }
    drawGameMsg(s, 120);
  },
};

// ------------------------------------------------------------------ KISS CHASE (Seb, New Year's Eve 1999 at Soundz FM)
// Seb's it. The girls at the party scatter when he comes near; catch one and it's a kiss. Jealous boyfriends get in the way.
const KC = { x0: 60, x1: 1240, y0: 366, y1: 500, len: 60 };
MGAME.kiss = {
  init(M) { M.s = { x: 640, y: 440, face: 1, walk: 0, moving: false, daze: 0, inv: 0, kisses: 0, chain: 0, chainT: 0, girls: [], lads: [], spawnT: 0, torn: 0, tornUsed: false, whooshT: 0, msgT: 0, camX: 160, midnight: false, midKiss: false, endT: -1 }; },
  spawnGirl(M) {
    const s = M.s, L = chance(0.5);
    s.girls.push({ x: L ? KC.x0 - 30 : KC.x1 + 30, y: rand(KC.y0, KC.y1), face: L ? 1 : -1, walk: rand(0, 6), sp: 290 + Math.min(25, M.t * 0.5) + rand(-12, 12), wob: rand(0, 6), happy: 0, tx: rand(KC.x0 + 100, KC.x1 - 100), ty: rand(KC.y0, KC.y1), jinkT: rand(0.6, 1.4), jx: 0, jy: 0 });
  },
  spawnLad(M) { const s = M.s, L = s.x > 650; s.lads.push({ x: L ? KC.x0 - 30 : KC.x1 + 30, y: rand(KC.y0, KC.y1), face: L ? 1 : -1, walk: 0, sp: 130 + rand(0, 20), cool: 0 }); },
  update(M, dt) {
    const s = M.s; if (s.msgT > 0) s.msgT -= dt; if (s.daze > 0) s.daze -= dt; if (s.inv > 0) s.inv -= dt; if (s.torn > 0) { s.torn -= dt; s.whooshT -= dt; if (s.whooshT <= 0) { s.whooshT = 0.18; sfx('swing'); } } if (s.chainT > 0) s.chainT -= dt; else s.chain = 0;
    const left = KC.len - M.t;
    if (s.endT >= 0) { s.endT += dt; if (s.endT > 2.4) miniEnd('HAPPY NEW YEAR'); return; }
    if (left <= 0) { s.midnight = true; s.endT = 0; M.score += 1000; pubFlash(s, s.kisses ? 'HAPPY NEW YEAR!' : 'HAPPY NEW YEAR, ON YOUR OWN', '#ffd23f', 2.4); sfx('airhorn'); sfx('jackpot'); return; }
    // Seb: the stick, or run to your finger
    let ix = 0, iy = 0; const inp = readInput(); ix = inp.ix; iy = inp.iy;
    // THE ULTIMATE SEX TORNADO: once a game, four seconds of whirlwind
    if ((pressed.has('jump') || pressed.has('special')) && !s.tornUsed && s.daze <= 0) { s.tornUsed = true; s.torn = 4; s.whooshT = 0; sfx('special'); sfx('boom'); pubFlash(s, 'THE ULTIMATE SEX TORNADO!', '#ff4fb0', 2.2); }
    const sp = s.daze > 0 ? 0 : s.torn > 0 ? 450 : 300, n = Math.hypot(ix, iy) || 1, go = ix || iy ? 1 : 0;
    s.x = clamp(s.x + ix / n * sp * dt * go, KC.x0, KC.x1); s.y = clamp(s.y + iy / n * sp * 0.7 * dt * go, KC.y0, KC.y1);
    s.moving = !!go && s.daze <= 0; if (ix && s.daze <= 0) s.face = Math.sign(ix); if (s.moving) s.walk += dt * 13;
    s.camX = clamp(s.x - W / 2, 0, 1300 - W);
    // the party: girls to chase, more of them as it gets late; a jealous boyfriend, then two
    s.spawnT -= dt;
    if (s.spawnT <= 0 && s.girls.filter(g => !g.happy).length < Math.min(6, 3 + Math.floor(M.t / 15))) { this.spawnGirl(M); s.spawnT = 0.8; }
    if (s.lads.length < (M.t > 30 ? 2 : M.t > 6 ? 1 : 0)) this.spawnLad(M);
    for (const g of s.girls) {
      g.walk += dt * 10; g.wob += dt;
      if (g.happy) { g.happy += dt; g.x += g.face * 120 * dt; continue; }
      const dx = g.x - s.x, dy = (g.y - s.y) * 1.6, d = Math.hypot(dx, dy) || 1;
      let vx, vy, spd;
      if (d < (s.torn > 0 ? 420 : 270)) {
        // run away, bend off the walls so the corners aren't a dead end for long, and jink now and then
        vx = dx / d; vy = dy / d;
        if (g.x < KC.x0 + 80) vx += 1.2; if (g.x > KC.x1 - 80) vx -= 1.2; if (g.y < KC.y0 + 20) vy += 1; if (g.y > KC.y1 - 20) vy -= 1;
        g.jinkT -= dt; if (g.jinkT <= 0) { g.jinkT = rand(0.5, 1.2); g.jx = rand(-0.45, 0.45); g.jy = rand(-0.45, 0.45); }
        vx += g.jx; vy += g.jy; spd = g.sp;
      } else {
        // dancing about: drift to a spot, pick another
        vx = g.tx - g.x; vy = g.ty - g.y; spd = 70;
        if (Math.hypot(vx, vy) < 20) { g.tx = rand(KC.x0 + 60, KC.x1 - 60); g.ty = rand(KC.y0, KC.y1); }
      }
      const vn = Math.hypot(vx, vy) || 1;
      g.x = clamp(g.x + vx / vn * spd * dt, KC.x0 - 40, KC.x1 + 40); g.y = clamp(g.y + vy / vn * spd * 0.7 * dt, KC.y0, KC.y1); if (Math.abs(vx) > 0.1) g.face = vx < 0 ? -1 : 1;
      if (d < (s.torn > 0 ? 64 : 34) && s.daze <= 0) {
        g.happy = 0.01; g.face = g.x > s.x ? 1 : -1; s.kisses++; s.chain++; s.chainT = 3;
        let pts = 500 + (Math.min(5, s.chain) - 1) * 250; M.score += pts;
        if (left < 6 && !s.midKiss) { s.midKiss = true; M.score += 2000; pts += 2000; pubFlash(s, 'MIDNIGHT KISS! +' + fmtN(pts), '#ff4fb0', 1.8); }
        else pubFlash(s, (s.chain > 1 ? 'MWAH x' + s.chain : 'MWAH!') + '  +' + fmtN(pts), '#ff4fb0', 1.1);
        sfx('pickup');
      }
    }
    s.girls = s.girls.filter(g => !(g.happy && (g.x < -100 || g.x > 1400)));
    // they don't stack up on top of each other
    const live = s.girls.filter(g => !g.happy);
    for (let i = 0; i < live.length; i++) for (let j = i + 1; j < live.length; j++) {
      const A = live[i], B = live[j], dx = B.x - A.x, dy = (B.y - A.y) * 1.6, d = Math.hypot(dx, dy);
      if (d < 46 && d > 0.01) { const k = (46 - d) / 2 / d; A.x -= dx * k; B.x += dx * k; A.y = clamp(A.y - dy * k / 1.6, KC.y0, KC.y1); B.y = clamp(B.y + dy * k / 1.6, KC.y0, KC.y1); }
      else if (d <= 0.01) { A.x -= 10; B.x += 10; }
    }
    for (const l of s.lads) {
      l.walk += dt * 9; if (l.cool > 0) l.cool -= dt;
      const dx = s.x - l.x, dy = s.y - l.y, d = Math.hypot(dx, dy) || 1;
      if (l.cool <= 0) { l.x += dx / d * l.sp * dt; l.y = clamp(l.y + dy / d * l.sp * 0.7 * dt, KC.y0, KC.y1); l.face = dx < 0 ? -1 : 1; }
      if (s.torn > 0 && Math.hypot(dx, dy * 1.6) < 70 && l.cool <= 0) {
        // a boyfriend in the way gets spun off across the room
        l.cool = 2.2; l.x = clamp(l.x - Math.sign(dx || 1) * 260, KC.x0 - 20, KC.x1 + 20); sfx('heavy'); pubFlash(s, 'WHOOSH!', '#efe6d2', 0.9); continue;
      }
      if (Math.hypot(dx, dy * 1.6) < 36 && s.inv <= 0 && s.torn <= 0) {
        s.daze = 1; s.inv = 2.2; l.cool = 1.6; s.chain = 0; sfx('heavy');
        s.x = clamp(s.x + Math.sign(dx || 1) * 70, KC.x0, KC.x1);
        pubFlash(s, ["OI! THAT'S MY BIRD!", 'HANDS OFF, SOLDIER', 'NOT TONIGHT, MATE'][rand(0, 3) | 0], '#ff7a5a', 1.4);
      }
    }
  },
  draw(M) {
    const s = M.s, keep = { S, FT, FB, cx: cam.x };
    try { S = { fireworks: s.midnight }; FT = 348; FB = 506; cam.x = s.camX; bgSoundzPixel(); } finally { S = keep.S; FT = keep.FT; FB = keep.FB; }
    cam.x = s.camX;
    const list = [];
    for (const g of s.girls) list.push({ y: g.y, f: () => pubFoe('ladette', g.x - s.camX, g.y, 'walk', g.face, g.walk) });
    for (const l of s.lads) list.push({ y: l.y, f: () => pubFoe('townie', l.x - s.camX, l.y, l.cool > 0 ? 'idle' : 'walk', l.face, l.walk) });
    list.push({ y: s.y, f: () => {
      if (s.torn > 0) { this.tornado(s, s.x - s.camX, s.y); return; }
      if (s.inv > 0 && s.daze <= 0 && Math.floor(s.inv * 12) % 2) return; pubLad('seb', s.x - s.camX, s.y, s.daze > 0 ? 'drowsy' : s.moving ? 'run' : 'idle', s.face, s.walk); } });
    list.sort((a, b) => a.y - b.y); for (const o of list) o.f();
    if (s.midnight) { ctx.save(); ctx.globalAlpha = 0.7; drawFireworks(6, 1); ctx.restore(); }
    cam.x = keep.cx;
  },
  hud(M) {
    const s = M.s, left = Math.max(0, Math.ceil(KC.len - M.t));
    // a heart over each girl he's kissed, as she skips off
    for (const g of s.girls) if (g.happy && g.happy < 1.2) { const x = g.x - s.camX, y = g.y - 150 - g.happy * 40; ctx.save(); ctx.globalAlpha = 1 - g.happy / 1.2; this.heart(x, y, 1.4, '#ff4fb0'); ctx.restore(); }
    pubPanel(W / 2 - 90, 12, 180, 54);
    textOut(s.midnight ? '00:00' : '23:59:' + String(60 - left).padStart(2, '0'), W / 2, 40, '28px ' + DISPLAY, s.midnight ? '#7fe07a' : left <= 10 ? '#ff5a3c' : '#ffd23f', OUT, 5);
    pubPanel(16, 14, 200, 64);
    ctx.font = '800 11px ' + BODY; ctx.fillStyle = '#93a3a1'; ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; ctx.fillText('KISSES', 30, 30);
    this.heart(40, 54, 1, '#ff4fb0'); textOut('x ' + s.kisses, 58, 54, '22px ' + DISPLAY, '#ff4fb0', OUT, 5, 'left');
    pubPanel(W - 196, 14, 180, 52); ctx.font = '800 11px ' + BODY; ctx.fillStyle = '#93a3a1'; ctx.textAlign = 'left'; ctx.fillText('SCORE', W - 182, 30); textOut(fmtN(M.score), W - 30, 46, '22px ' + DISPLAY, '#ffd23f', OUT, 5, 'right');
    drawGameMsg(s, 120);
  },
  // the tornado: PixelLab's whirlwind with Seb's arms and boots, flipped fast so it spins, wobbling and bobbing, with dust
  tornado(s, x, y) {
    const ph = Math.floor(time * 16), img = pubImg(Math.floor(ph / 2) % 2 ? 'tornado2' : 'tornado') || pubImg('tornado');
    ctx.fillStyle = 'rgba(10,8,6,0.35)'; ctx.beginPath(); ctx.ellipse(snap2(x), snap2(y), 46, 9, 0, 0, Math.PI * 2); ctx.fill();
    for (let i = 0; i < 6; i++) { const a = time * 9 + i * 1.05, r = 52 + (i % 2) * 10; pxCircle(x + Math.cos(a) * r, y - 8 + Math.sin(a) * 8, 6 + (i % 3) * 2, 'rgba(200,190,170,0.5)'); }
    if (img) { ctx.save(); ctx.imageSmoothingEnabled = false; ctx.translate(snap2(x), snap2(y - img.height - Math.abs(Math.sin(time * 14)) * 6)); ctx.rotate(Math.sin(time * 23) * 0.12); if (ph % 2) ctx.scale(-1, 1); ctx.drawImage(img, -img.width, -img.height, img.width * 2, img.height * 2); ctx.restore(); }
    else pubLad('seb', x, y, 'run', ph % 2 ? 1 : -1, time * 20);
  },
  heart(x, y, k, col) { ctx.fillStyle = col; ctx.beginPath(); ctx.moveTo(x, y + 8 * k); ctx.bezierCurveTo(x - 14 * k, y - 2 * k, x - 6 * k, y - 12 * k, x, y - 4 * k); ctx.bezierCurveTo(x + 6 * k, y - 12 * k, x + 14 * k, y - 2 * k, x, y + 8 * k); ctx.fill(); },
};

// ------------------------------------------------------------------ hooks: the run, the clear screen, the select screen
// a mini-game after its stage (once a run, offline), then the pub between chapters
function pubAfterClear(go) {
  if (!run || NET.on) { go(); return; }
  const key = run.route[run.idx], g = MINI_AFTER[key];
  run.minis = run.minis || {};
  if (g && !run.minis[key]) { run.minis[key] = true; openMini(g, 'run', () => pubAfterClear(go)); return; }
  go();
}
function pubBetween(key, nk, go) {
  const ch = k => chapterOf(k) || '1999';
  if (!run || NET.on || !nk || ch(key) === ch(nk) || nk === 'ramsden' || key === 'ramsden') { go(); return; }
  openPub('run', go, run.c.id);
}
// what a stage banked, on the points screen
function pubClearLine(y) {
  if (!clearInfo || clearInfo.banked == null) return;
  ctx.font = '800 13px ' + BODY; ctx.fillStyle = '#9fd0ff'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillText('+' + fmtN(clearInfo.banked) + ' ON YOUR PUB TAB  ·  TAB ' + fmtN(PUB.wallet), W / 2, y);
}
function pubBankStage() {
  if (!run) return 0;
  const n = Math.max(0, run.score - (run.banked || 0)); run.banked = run.score;
  return pubBank(n);
}
function pubSelectLad() { try { const c = PLAYABLE[typeof sel === 'number' ? sel : 0]; return c && !ladLocked(c) ? c.id : 'tim'; } catch (e) { return 'tim'; } }
function pubFromSelect(id) { if (!PROFILE.name) { profileAsk(false, () => pubFromSelect(id)); return; } sfx('page'); const c = id && CHAR_BY_ID[id]; openPub('menu', null, c && !ladLocked(c) ? id : pubSelectLad()); }
function pubTyped() { if (typed.endsWith('ARCADE')) { typed = ''; PUB_GAMES.forEach(g => { PUB.cabs[g] = true; }); pubSave(); sfx('jackpot'); return true; } return false; }
// ================================================================== Version 56: your name
// Picked the first time you get to the select screen, kept on this phone, and used on every board and in the online
// lobby. In the app the name is claimed in Firebase (players/<NAME>) with a secret key only this phone has, so nobody
// else can take it; the boards (boards/<game>/<NAME>) keep one row per player, their best.
const PROFILE = { name: lsGet('mbc.name', null), key: lsGet('mbc.key', null), claimed: !!lsGet('mbc.claimed', false), asking: false, first: false, then: null, busy: false };
if (!PROFILE.key) { PROFILE.key = Array.from({ length: 24 }, () => 'abcdefghijkmnpqrstuvwxyz23456789'[Math.floor(nativeRandom() * 32)]).join(''); lsSet('mbc.key', PROFILE.key); }
const cleanName = v => String(v || '').toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 12);
const nameOk = n => /^[A-Z0-9]{3,12}$/.test(n);
const appFb = () => typeof FB_CFG !== 'undefined' && !!FB_CFG && !!window.MBC_APP;
function withTimeout(p, ms) { return Promise.race([p, new Promise((_, rej) => setTimeout(() => rej(new Error('timeout')), ms))]); }
const denied = e => /permission/i.test(String((e && (e.code || e.message)) || e));
// 'ok', 'taken', 'norules' (Firebase isn't set up for names yet) or 'offline'
async function claimName(n) {
  if (!appFb()) return 'ok';
  try { await withTimeout(NT.init(), 8000); } catch (e) { return 'offline'; }
  if (NT.kind !== 'fb') return 'offline';
  const ref = NT.db.ref('players/' + n); let taken = false;
  try { taken = (await withTimeout(ref.child('at').once('value'), 7000)).exists(); } catch (e) { return denied(e) ? 'norules' : 'offline'; }
  try { await withTimeout(ref.set({ key: PROFILE.key, at: Date.now() }), 7000); return 'ok'; } catch (e) { return denied(e) ? (taken ? 'taken' : 'norules') : 'offline'; }
}
function profileSet(n, claimed) {
  PROFILE.name = n; PROFILE.claimed = !!claimed; lsSet('mbc.name', n); lsSet('mbc.claimed', PROFILE.claimed);
  settings.lastName = n; saveSettings(); profileFoot();
  if (claimed) PUB_GAMES.forEach(pubSyncMine), boardSyncMine();
}
function profileFoot() { const b = document.getElementById('t3-me'); if (b) b.textContent = PROFILE.name ? 'You: ' + PROFILE.name : 'Pick a name'; hubFoot(); }
// the name box (the same overlay the high scores used)
function profileAsk(first, then, why) {
  const el = nameEls; if (!el.overlay || !el.form || PROFILE.asking) return;
  PROFILE.asking = true; PROFILE.first = !!first || !PROFILE.name; PROFILE.then = then || null;
  el.title.textContent = PROFILE.name && !why ? 'Change your name' : 'Pick a name';
  el.sum.textContent = why || 'It goes on every scoreboard and in the online lobby. Letters and numbers, 3 to 12.';
  el.input.value = PROFILE.name || cleanName(settings.lastName);
  el.skip.hidden = PROFILE.first; el.skip.textContent = 'Cancel';
  const save = document.getElementById('nameSave'); if (save) { save.textContent = "That's me"; save.disabled = false; }
  el.overlay.hidden = false; held.clear();
  try { el.input.focus(); el.input.select(); } catch (e) { /* optional */ }
}
function profileClose() {
  PROFILE.asking = false; closeNameEntry(); nameEls.skip.hidden = false; nameEls.skip.textContent = 'Skip';
  const save = document.getElementById('nameSave'); if (save) { save.textContent = 'Save score'; save.disabled = false; }
  const t = PROFILE.then; PROFILE.then = null; pressed.clear(); if (t) t();
}
function profileHook(skip) {
  if (!PROFILE.asking) return false;
  if (skip) { if (!PROFILE.first) { PROFILE.then = null; profileClose(); } return true; }
  if (PROFILE.busy) return true;
  const n = cleanName(nameEls.input.value);
  if (!nameOk(n)) { nameEls.sum.textContent = 'Letters and numbers only, 3 to 12 of them.'; return true; }
  if (n === PROFILE.name && (PROFILE.claimed || !appFb())) { profileClose(); return true; }
  PROFILE.busy = true; nameEls.sum.textContent = 'Checking nobody else is ' + n + '...';
  const save = document.getElementById('nameSave'); if (save) save.disabled = true;
  claimName(n).then(r => {
    PROFILE.busy = false; if (save) save.disabled = false;
    if (r === 'taken') { nameEls.sum.textContent = 'Someone already plays as ' + n + '. Try another.'; sfx('grab'); return; }
    profileSet(n, r === 'ok' && appFb()); sfx('life'); profileClose();
  });
  return true;
}
if (nameEls.input) nameEls.input.addEventListener('input', () => { if (!PROFILE.asking) return; const v = cleanName(nameEls.input.value); if (v !== nameEls.input.value) nameEls.input.value = v; });
// runs at the top of every frame: the first visit to the select screen asks for a name; nothing else moves while it's open
function profileTick() {
  try { hubTick(); } catch (e) { glitch('hub', e); }
  if (PROFILE.asking) { pressed.clear(); taps.length = 0; return true; }
  if (mode === 'select' && !PROFILE.name && modeT > 0.4) { profileAsk(true); return true; }
  return false;
}
// a name picked without signal (or before Firebase knew about names) is claimed the next time the app opens
setTimeout(async () => {
  profileFoot();
  if (!PROFILE.name || PROFILE.claimed || !appFb()) return;
  const r = await claimName(PROFILE.name);
  if (r === 'ok') profileSet(PROFILE.name, true);
  else if (r === 'taken') { PROFILE.claimed = false; const n = PROFILE.name; PROFILE.name = null; lsSet('mbc.name', null); profileAsk(true, null, 'Someone already plays as ' + n + '. Pick another name.'); }
}, 2500);
function lobbyName(isMe, n) { return isMe ? (PROFILE.name || 'PLAYER ' + n) + ' (YOU)' : ((NL.them && NL.them.name) || 'PLAYER ' + n); }

// the main high scores: shared through Firebase in the app (boards/runs), one row each, under your name
function boardFbInit() {
  board.ready = true;
  (async () => {
    try {
      await NT.init(); if (NT.kind !== 'fb') return;
      board.fb = NT.db; board.mode = 'shared';
      NT.db.ref('boards/runs').orderByChild('score').limitToLast(40).on('value', snap => {
        const out = []; snap.forEach(c => { const s = sanitizeEntry(Object.assign({}, c.val(), { id: 'fb:' + c.key })); if (s) out.push(s); });
        board.shared = out; boardSyncMine();
      }, () => { board.mode = 'local'; board.fb = null; });
    } catch (e) { board.mode = 'local'; }
  })();
}
async function boardFbAdd(entry) {
  board.local.push(Object.assign({}, entry, { local: true })); board.local.sort((a, b) => b.score - a.score); board.local = board.local.slice(0, 30); lsSet('carpdiem.scores', board.local);
  const mine = board.shared.find(e => e.name === entry.name);
  if (mine && mine.score >= entry.score) return 'shared';
  try { await withTimeout(board.fb.ref('boards/runs/' + entry.name).set({ name: entry.name, lad: entry.lad, score: entry.score, res: entry.res || '', at: entry.at || Date.now() }), 8000); return 'shared'; }
  catch (e) { return 'local'; }
}
function boardSyncMine() {
  if (!board.fb || !PROFILE.name || !PROFILE.claimed) return;
  const best = board.local.filter(e => String(e.name).toUpperCase() === PROFILE.name).sort((a, b) => b.score - a.score)[0];
  const mine = board.shared.find(e => e.name === PROFILE.name);
  if (best && (!mine || best.score > mine.score)) board.fb.ref('boards/runs/' + PROFILE.name).set({ name: PROFILE.name, lad: best.lad, score: best.score, res: best.res || '', at: best.at || Date.now() }).catch(() => {});
}

// ================================================================== Version 57: the Harvest Moon, where the lads meet
// Everyone with the app open is online (online/<NAME>: where they are, which lad, and in the pub where they're stood).
// In the pub you see them: the ones in the pub walk about live with their name over their head, the rest stand at the
// bar with what they're up to. Walk up to someone and HIT to invite them: you host an online game, they get a card
// (JOIN / NOT NOW) wherever they are in the menus or the pub, and JOIN drops them straight into your lobby.
const HUB = { kind: null, db: null, bc: null, subs: [], starting: false, others: {}, ghosts: {}, inv: {}, out: null, outNo: false,
  where: null, what: '', last: 0, lastX: 0, lastY: 0, hidden: false, seen: new Set(), card: null, cardFor: null };
async function hubStart() {
  if (HUB.kind || HUB.starting || !PROFILE.name || !appFb()) return;
  HUB.starting = true;
  try {
    if (netMockWanted()) { HUB.kind = 'mock'; HUB.mem = {}; try { for (let i = 0; i < localStorage.length; i++) { const k = localStorage.key(i); if (k.startsWith('mbchub/')) HUB.mem[k.slice(7)] = JSON.parse(localStorage.getItem(k)); } } catch (e) { /* ok */ } HUB.bc = new BroadcastChannel('mbc-hub'); HUB.bc.onmessage = ev => { const { path, val } = ev.data; if (val == null) delete HUB.mem[path]; else HUB.mem[path] = val; hubMockFire(path); }; }
    else { await withTimeout(NT.init(), 8000); if (NT.kind !== 'fb') return; HUB.kind = 'fb'; HUB.db = NT.db; }
    hubListen('online', v => { HUB.others = v || {}; });
    hubListen('invites/' + PROFILE.name, v => { HUB.inv = v || {}; });
    chatListen();
    hubPresence(true);
    if (HUB.kind === 'fb') HUB.db.ref('online/' + PROFILE.name).onDisconnect().remove();
    else window.addEventListener('pagehide', () => hubSet('online/' + PROFILE.name, null));
  } catch (e) { /* no signal: try again later */ } finally { HUB.starting = false; }
}
// a tiny store: Firebase in the app, or localStorage and a BroadcastChannel for testing two pages (?netmock)
function hubSet(path, val) {
  if (HUB.kind === 'fb') { const r = HUB.db.ref(path); (val == null ? r.remove() : r.set(val)).catch(() => {}); return; }
  if (HUB.kind !== 'mock') return;
  try { if (val == null) localStorage.removeItem('mbchub/' + path); else localStorage.setItem('mbchub/' + path, JSON.stringify(val)); } catch (e) { /* ok */ }
  if (val == null) delete HUB.mem[path]; else HUB.mem[path] = val;
  HUB.bc.postMessage({ path, val }); hubMockFire(path);
}
function hubMockRead(prefix) {
  const out = {}, pre = prefix + '/';
  for (const k in HUB.mem) if (k.startsWith(pre)) { const rest = k.slice(pre.length).split('/'); let o = out; for (let j = 0; j < rest.length - 1; j++) o = o[rest[j]] = o[rest[j]] || {}; o[rest[rest.length - 1]] = HUB.mem[k]; }
  return out;
}
function hubMockFire(path) { for (const sub of HUB.subs) if (path === sub.prefix || path.startsWith(sub.prefix + '/')) sub.cb(hubMockRead(sub.prefix)); }
function hubListen(prefix, cb) {
  if (HUB.kind === 'fb') { const r = HUB.db.ref(prefix), h = snap => cb(snap.val()); r.on('value', h, () => {}); return () => r.off('value', h); }
  const sub = { prefix, cb }; HUB.subs.push(sub); cb(hubMockRead(prefix)); return () => { HUB.subs = HUB.subs.filter(x => x !== sub); };
}
// where you are, in a word, and the detail people see in the pub
function hubWhere() {
  if (NET.on) return ['coop', 'an online game'];
  if (mode === 'net') return ['lobby', ''];
  if (mode === 'pub' || (mode === 'name' && PUB.from)) return ['pub', ''];
  if (mode === 'mini' && MG) return [MG.from === 'pub' ? 'cab' : 'run', MG.d.title];
  if (run && ['play', 'pause', 'chat', 'clear', 'loading', 'over', 'win', 'name'].includes(mode)) return ['run', ST ? ST.title : 'a run'];
  return ['menu', ''];
}
function hubPresence(force) {
  if (!HUB.kind || !PROFILE.name || HUB.hidden) return;
  const [where, what] = hubWhere(), now = Date.now(), inPub = where === 'pub';
  const moved = inPub && (Math.abs(PUB.x - HUB.lastX) > 6 || Math.abs(PUB.y - HUB.lastY) > 6);
  if (!force && where === HUB.where && what === HUB.what && !(moved && now - HUB.last > 150) && now - HUB.last < 20000) return;
  HUB.where = where; HUB.what = what; HUB.last = now; HUB.lastX = PUB.x; HUB.lastY = PUB.y;
  const lad = where === 'pub' || where === 'cab' ? PUB.lad : run ? run.c.id : (PLAYABLE[sel] && !ladLocked(PLAYABLE[sel]) ? PLAYABLE[sel].id : PUB.lad);
  hubSet('online/' + PROFILE.name, { where, what: String(what || '').slice(0, 30), lad, x: Math.round(PUB.x), y: Math.round(PUB.y), face: PUB.face, mv: !!PUB.moving, at: now });
}
document.addEventListener('visibilitychange', () => {
  HUB.hidden = document.hidden;
  if (!HUB.kind || !PROFILE.name) return;
  if (document.hidden) hubSet('online/' + PROFILE.name, null); else { hubPresence(true); if (HUB.kind === 'mock') for (const sub of HUB.subs) sub.cb(hubMockRead(sub.prefix)); }   // Firebase catches up by itself
});
// everyone else who's online, as people in the pub: walking about if they're in it, at the bar if they're not
function hubPeople() {
  const now = Date.now(), out = [];
  for (const n in HUB.others) { const o = HUB.others[n]; if (n === PROFILE.name || !o || !(now - (o.at || 0) < 90000)) continue; out.push(Object.assign({ name: n }, o)); }
  return out.sort((a, b) => a.name < b.name ? -1 : 1);
}
const BAR_SPOTS = [[350, 452], [430, 462], [510, 450], [590, 464], [670, 452], [750, 462], [390, 476], [550, 478], [710, 476]];
function hubGhosts() {
  if (!HUB.kind) return [];
  const list = [], keep = new Set(); let b = 0;
  for (const p of hubPeople()) {
    let tx, ty;
    if (p.where === 'pub' || p.where === 'cab') { tx = clamp(+p.x || 300, 30, PUB_W - 40); ty = clamp(+p.y || 470, 436, 500); }
    else { const sp = BAR_SPOTS[b++ % BAR_SPOTS.length]; tx = sp[0]; ty = sp[1]; }
    let g = HUB.ghosts[p.name];
    if (!g) g = HUB.ghosts[p.name] = { x: tx, y: ty, walk: 0, face: 1 };
    g.name = p.name; g.lad = CHAR_BY_ID[p.lad] ? p.lad : 'tim'; g.where = p.where; g.what = p.what || ''; g.tx = tx; g.ty = ty;
    keep.add(p.name); list.push(g);
  }
  for (const n in HUB.ghosts) if (!keep.has(n)) delete HUB.ghosts[n];
  return list;
}
function hubMoveGhosts(dt) {
  for (const g of Object.values(HUB.ghosts)) {
    const dx = g.tx - g.x, dy = g.ty - g.y, d = Math.hypot(dx, dy);
    g.moving = d > 3;
    if (d > 400) { g.x = g.tx; g.y = g.ty; }
    else if (g.moving) { const k = Math.min(1, dt * 380 / d); g.x += dx * k; g.y += dy * k; g.walk += dt * 11; if (Math.abs(dx) > 2) g.face = dx > 0 ? 1 : -1; }
  }
}
const hubCanInvite = g => g.where === 'pub' || g.where === 'menu' || g.where === 'cab';
function hubStatus(g) {
  return ({ pub: 'IN THE PUB', menu: 'PICKING A LAD', lobby: 'IN THE ONLINE LOBBY', cab: 'ON THE ' + (g.what || 'ARCADE').replace(/^THE /, ''), run: 'PLAYING ' + (g.what || 'A RUN'), coop: 'IN AN ONLINE GAME' })[g.where] || '';
}
function hubPrompt(g) { return hubCanInvite(g) ? 'INVITE ' + g.name + ' FOR A GAME' : g.name + ' IS ' + hubStatus(g).replace(/^IN /, 'IN ').replace(/^PLAYING/, 'PLAYING') + '. TRY THEM LATER'; }
// name tags over everyone's heads
function hubTags() {
  const cx = cam.x;
  for (const g of hubGhosts()) {
    const x = g.x - cx, y = g.y - 150; if (x < -80 || x > W + 80) continue;
    const col = (CHAR_BY_ID[g.lad] || {}).color || '#efe6d2';
    textOut(g.name, x, y, '14px ' + DISPLAY, col, OUT, 4);
    if (g.where !== 'pub') { ctx.font = '800 9px ' + BODY; ctx.fillStyle = '#c8d6d4'; ctx.textAlign = 'center'; ctx.fillText(hubStatus(g), x, y + 14); }
  }
  if (PROFILE.name) { const x = PUB.x - cx; textOut(PROFILE.name, x, PUB.y - 150, '14px ' + DISPLAY, '#ffd23f', OUT, 4); }
}
function hubCountHud() {
  if (!HUB.kind) return;
  const n = hubPeople().length, inPub = hubPeople().filter(p => p.where === 'pub' || p.where === 'cab').length;
  pubPanel(W - 236, 74, 220, 36);
  ctx.font = '800 12px ' + BODY; ctx.textAlign = 'left'; ctx.textBaseline = 'middle';
  ctx.fillStyle = n ? '#7fe07a' : '#93a3a1'; ctx.fillText(n ? '● ' + n + ' ONLINE' + (inPub ? ' · ' + inPub + ' IN HERE' : '') : '○ NOBODY ELSE ONLINE', W - 222, 92);
}
function hubFoot() {
  const b = document.getElementById('t3-pub'); if (!b) return;
  const n = HUB.kind ? hubPeople().length : 0;
  const u = chatUnread();
  b.textContent = 'Harvest Moon' + (n ? ' · ' + n + ' online' : '') + (u ? ' · ' + u + ' new' : '');
}
// sending an invite: you host, they get a card
async function hubInvite(g) {
  if (!HUB.kind) { pubSay('Inviting needs the app and a signal.'); sfx('grab'); return; }
  if (!hubCanInvite(g)) { pubSay(g.name + ' is busy. Try them later.'); sfx('grab'); return; }
  sfx('page'); pubSaveSpot();
  openNetLobby(); NL.lad = Math.max(0, PLAYABLE.findIndex(c => c.id === PUB.lad));
  await netHost();
  if (NL.screen !== 'host' || !NT.code) return;
  HUB.out = { to: g.name, code: NT.code }; HUB.outNo = false;
  hubSet('invites/' + g.name + '/' + PROFILE.name, { code: NT.code, at: Date.now(), lad: PUB.lad });
  HUB.outOff = hubListen('invites/' + g.name, v => { const mine = v && v[PROFILE.name]; if (mine && mine.no && HUB.out && !HUB.outNo) { HUB.outNo = true; NL.msg = g.name + ' said not now.'; sfx('grab'); } });
  NL.msg = 'Invited ' + g.name + '. Waiting for them...';
}
function hubCancelInvite() {
  if (!HUB.out) return;
  if (mode === 'net' && NL.msg && /^Invited /.test(NL.msg)) NL.msg = '';
  hubSet('invites/' + HUB.out.to + '/' + PROFILE.name, null);
  if (HUB.outOff) HUB.outOff(); HUB.out = null; HUB.outOff = null;
}
// where you were in the pub, so you're back at the same spot after a game
function pubSaveSpot() { PUB.spot = { x: PUB.x, y: PUB.y }; }
// receiving one: a card over whatever's on screen
function hubPendingInvite() {
  const now = Date.now(); let best = null;
  for (const from in HUB.inv) { const v = HUB.inv[from]; if (!v || v.no || !(now - (v.at || 0) < 180000) || HUB.seen.has(from + v.at)) continue; if (!best || v.at > best.at) best = Object.assign({ from }, v); }
  return best;
}
function hubCardEl() {
  if (HUB.card) return HUB.card;
  const el = document.createElement('div'); el.id = 'hubInvite';
  el.style.cssText = 'position:fixed;z-index:60;display:none;align-items:center;gap:12px;padding:12px 14px;background:#121a1e;border:2px solid #f2a23a;border-radius:12px;box-shadow:0 8px 30px rgba(0,0,0,.6);font:600 14px Rubik,system-ui,sans-serif;color:#efe6d2;max-width:min(520px,92vw)';
  el.innerHTML = '<img id="hubInvFace" width="44" height="44" style="image-rendering:pixelated;border:2px solid #16120f;background:#1a242a;flex:none" alt=""><div style="flex:1;min-width:0"><div id="hubInvWho" style="font:400 18px \'Pixelify Sans\',monospace;color:#ffd23f"></div><div style="color:#93a3a1;font-size:12px">wants a game. Online co-op, the two of you.</div></div>' +
    '<button id="hubInvNo" type="button" style="font:700 13px Rubik,sans-serif;padding:10px 12px;border-radius:9px;border:2px solid #f2a23a;background:transparent;color:#ffd23f;cursor:pointer">Not now</button>' +
    '<button id="hubInvYes" type="button" style="font:700 13px Rubik,sans-serif;padding:10px 16px;border-radius:9px;border:2px solid #7fe07a;background:#7fe07a;color:#10200f;cursor:pointer">Join</button>';
  document.body.appendChild(el); HUB.card = el;
  el.querySelector('#hubInvYes').addEventListener('click', e => { e.stopPropagation(); hubAccept(); });
  el.querySelector('#hubInvNo').addEventListener('click', e => { e.stopPropagation(); hubDecline(); });
  ['pointerdown', 'keydown'].forEach(t => el.addEventListener(t, e => e.stopPropagation()));
  return el;
}
function hubShowCard(inv) {
  const el = hubCardEl();
  if (!inv) { if (el.style.display !== 'none') el.style.display = 'none'; HUB.cardFor = null; return; }
  if (HUB.cardFor !== inv.from + inv.at) {
    HUB.cardFor = inv.from + inv.at; sfx('incoming');
    el.querySelector('#hubInvWho').textContent = inv.from;
    const img = portraitImg(CHAR_BY_ID[inv.lad] ? inv.lad : 'tim'); el.querySelector('#hubInvFace').src = img ? img.src : '';
  }
  const r = canvas.getBoundingClientRect();
  el.style.display = 'flex'; el.style.left = Math.max(8, r.left + r.width / 2 - el.offsetWidth / 2) + 'px'; el.style.top = Math.max(8, r.top + 10) + 'px';
}
function hubAccept() {
  const inv = hubPendingInvite(); if (!inv) return;
  HUB.seen.add(inv.from + inv.at); hubShowCard(null);
  hubSet('invites/' + PROFILE.name + '/' + inv.from, null);
  if (mode === 'pub') pubSaveSpot();
  if (T3 && T3.live && T3.live() && mode === 'title') mode = 'select';
  const lad = mode === 'pub' ? PUB.lad : (PLAYABLE[sel] && !ladLocked(PLAYABLE[sel]) ? PLAYABLE[sel].id : PUB.lad);
  openNetLobby(); NL.lad = Math.max(0, PLAYABLE.findIndex(c => c.id === lad));
  if (lad === inv.lad) NL.lad = PLAYABLE.findIndex((c, i) => i !== PLAYABLE.findIndex(d => d.id === inv.lad) && !ladLocked(c));
  netJoin(inv.code);
}
function hubDecline() {
  const inv = hubPendingInvite(); if (!inv) return;
  HUB.seen.add(inv.from + inv.at); hubShowCard(null);
  hubSet('invites/' + PROFILE.name + '/' + inv.from, { code: inv.code, at: inv.at, no: true });
  sfx('page');
}
// every frame (from profileTick): start once there's a name, keep presence fresh, move the regulars, show any invite
let hubT = 0;
function hubTick() {
  if (!HUB.kind) { if (PROFILE.name && appFb() && !HUB.starting && (hubT -= 1) < 0) { hubT = 600; hubStart(); } return; }
  hubPresence(false);
  const now = performance.now(), dt = Math.min(0.1, (now - (HUB.lastT || now)) / 1000); HUB.lastT = now; hubMoveGhosts(dt);
  if (HUB.out && (mode !== 'net' || NL.screen === 'lobby' || NL.screen === 'menu')) hubCancelInvite();   // they joined, or you left the lobby
  const showable = !NET.on && !PROFILE.asking && ['pub', 'select', 'title', 'board'].includes(mode);
  const inv = showable ? hubPendingInvite() : null;
  hubShowCard(inv);
  if (inv && pressed.has('start')) { pressed.clear(); hubAccept(); }
  if (now - (HUB.footT || 0) > 2000) { HUB.footT = now; hubFoot(); }
  chatTick();
  if (mode === 'select' && PUB.spot && !NET.on && !PROFILE.asking) hubBackToPub();   // a game that started in the pub ends back in it
}
// back to the pub after an online game that started there
function hubBackToPub() { if (PUB.spot) { const sp = PUB.spot; PUB.spot = null; openPub('menu', null, PUB.lad); PUB.x = sp.x; PUB.y = sp.y; } }

// ================================================================== Version 58: chat in the Harvest Moon
// A CHAT tab on the right of the pub slides out a panel: quick lines (everyday ones and one in your lad's voice), a box
// to type your own (140 characters), and the last 50 messages, newest first. What anyone says also pops up in a speech
// bubble over their head in the pub. Firebase chat/<id> in the app; the test relay with ?netmock.
const CHAT = { msgs: [], read: lsGet('mbc.chat.read', 0), open: false, el: null, tab: null, sentAt: 0, lastTop: 0, heard: 0 };
const CHAT_QUICK = ['Game?', 'Pint?', 'Get in!', 'Back in 5', 'Night lads'];
const CHAT_LAD = { tim: 'Right, lads!', seb: 'Sir, yes sir!', byron: "Ref! REF!", pearcy: 'CARP DIEM!', kelly: 'MASS HEAD!', marc: "It's all about the numbers. Meeeehhhhh", sam: 'What happened?', thet: "Can't see me!", ash: "I'll be back." };
function chatListen() {
  const take = v => {
    const out = [];
    for (const id in (v || {})) { const m = v[id]; if (!m || typeof m.text !== 'string' || !m.name) continue; out.push({ id, name: String(m.name).slice(0, 12), lad: CHAR_BY_ID[m.lad] ? m.lad : 'tim', text: m.text.slice(0, 140), at: +m.at || 0 }); }
    out.sort((a, b) => a.at - b.at); CHAT.msgs = out.slice(-50);
    const top = CHAT.msgs.length ? CHAT.msgs[CHAT.msgs.length - 1].at : 0;
    if (top > CHAT.lastTop) { const fresh = CHAT.msgs[CHAT.msgs.length - 1]; if (CHAT.lastTop && fresh.name !== PROFILE.name && mode === 'pub') sfx('page'); CHAT.lastTop = top; }
    chatRender();
  };
  if (HUB.kind === 'fb') HUB.db.ref('chat').orderByChild('at').limitToLast(50).on('value', snap => take(snap.val()), () => {});
  else hubListen('chat', take);
}
function chatSend(text) {
  text = String(text || '').replace(/\s+/g, ' ').trim().slice(0, 140);
  if (!text || !HUB.kind || !PROFILE.name) return false;
  const now = Date.now(); if (now - CHAT.sentAt < 1200) return false; CHAT.sentAt = now;
  const lad = mode === 'pub' ? PUB.lad : (PLAYABLE[sel] && !ladLocked(PLAYABLE[sel]) ? PLAYABLE[sel].id : PUB.lad);
  const id = HUB.kind === 'fb' ? HUB.db.ref('chat').push().key : now.toString(36) + Math.floor(nativeRandom() * 1e6).toString(36);
  hubSet('chat/' + id, { name: PROFILE.name, lad, text, at: now });
  sfx('pickup'); return true;
}
function chatUnread() { return CHAT.msgs.filter(m => m.at > CHAT.read && m.name !== PROFILE.name).length; }
function chatMarkRead() { const top = CHAT.msgs.length ? CHAT.msgs[CHAT.msgs.length - 1].at : 0; if (top > CHAT.read) { CHAT.read = top; lsSet('mbc.chat.read', top); } }
const chatEsc = t => String(t).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
function chatAgo(at) { const s = Math.max(0, (Date.now() - at) / 1000); return s < 60 ? 'now' : s < 3600 ? Math.floor(s / 60) + 'm' : s < 86400 ? Math.floor(s / 3600) + 'h' : Math.floor(s / 86400) + 'd'; }
function chatBuild() {
  if (CHAT.el) return;
  const css = document.createElement('style');
  css.textContent = `#chatTab{position:fixed;z-index:40;display:none;writing-mode:vertical-rl;transform:rotate(180deg);font:400 15px 'Pixelify Sans',monospace;letter-spacing:2px;color:#ffd23f;background:#121a1e;border:2px solid #f2a23a;border-right:0;border-radius:0 10px 10px 0;padding:12px 7px;cursor:pointer}
#chatTab b{display:inline-block;margin-top:6px;background:#ff5a3c;color:#fff;border-radius:9px;padding:3px 2px;font:700 11px Rubik,sans-serif;writing-mode:horizontal-tb;transform:rotate(180deg)}
#chatPanel{position:fixed;z-index:41;display:none;flex-direction:column;background:rgba(14,20,24,.97);border-left:2px solid #f2a23a;box-shadow:-10px 0 30px rgba(0,0,0,.5);font:600 13px Rubik,system-ui,sans-serif;color:#efe6d2;box-sizing:border-box}
#chatPanel header{display:flex;align-items:center;gap:8px;padding:8px 10px;border-bottom:1px solid #2b3b42}
#chatPanel header h3{flex:1;margin:0;font:400 16px 'Pixelify Sans',monospace;color:#ffd23f}
#chatPanel header span{font:700 11px Rubik,sans-serif;color:#7fe07a}
#chatPanel button{font:700 12px Rubik,sans-serif;cursor:pointer;border-radius:8px}
#chatClose{border:2px solid #2b3b42;background:transparent;color:#efe6d2;padding:4px 9px}
#chatQuick{display:flex;flex-wrap:wrap;gap:5px;padding:8px 10px 4px}
#chatQuick button{border:1px solid #3a4a52;background:#1a242a;color:#efe6d2;padding:5px 8px}
#chatQuick button.lad{border-color:#f2a23a;color:#ffd23f}
#chatForm{display:flex;gap:6px;padding:6px 10px 8px;border-bottom:1px solid #2b3b42}
#chatInput{flex:1;min-width:0;font:600 14px Rubik,sans-serif;background:#0c1014;color:#efe6d2;border:2px solid #2b3b42;border-radius:8px;padding:7px 9px}
#chatInput:focus{outline:none;border-color:#f2a23a}
#chatSend{border:2px solid #7fe07a;background:#7fe07a;color:#10200f;padding:0 12px}
#chatList{flex:1;overflow-y:auto;padding:4px 10px 10px;overscroll-behavior:contain}
#chatList .m{display:flex;gap:8px;padding:6px 0;border-bottom:1px solid rgba(255,255,255,.05)}
#chatList img{width:28px;height:28px;flex:none;image-rendering:pixelated;border:2px solid #16120f;background:#1a242a}
#chatList .n{font:400 13px 'Pixelify Sans',monospace}
#chatList .t{color:#93a3a1;font-size:10px;margin-left:6px}
#chatList .x{overflow-wrap:anywhere;line-height:1.35}
#chatList .none{color:#93a3a1;text-align:center;padding:24px 0}`;
  document.head.appendChild(css);
  const tab = document.createElement('button'); tab.id = 'chatTab'; tab.type = 'button'; tab.innerHTML = 'CHAT';
  const el = document.createElement('div'); el.id = 'chatPanel';
  el.innerHTML = `<header><h3>HARVEST MOON CHAT</h3><span id="chatWho"></span><button id="chatClose" type="button">Close</button></header>
<div id="chatQuick"></div><form id="chatForm" autocomplete="off"><input id="chatInput" maxlength="140" placeholder="Say something..." autocomplete="off" spellcheck="true" enterkeyhint="send"><button id="chatSend" type="submit">Send</button></form><div id="chatList"></div>`;
  document.body.appendChild(tab); document.body.appendChild(el); CHAT.el = el; CHAT.tab = tab;
  for (const n of [tab, el]) ['pointerdown', 'keydown', 'keyup'].forEach(t => n.addEventListener(t, e => e.stopPropagation()));
  tab.addEventListener('click', () => chatToggle(true));
  el.querySelector('#chatClose').addEventListener('click', () => chatToggle(false));
  el.querySelector('#chatForm').addEventListener('submit', e => { e.preventDefault(); const i = el.querySelector('#chatInput'); if (chatSend(i.value)) i.value = ''; });
  el.querySelector('#chatInput').addEventListener('keydown', e => { if (e.key === 'Escape') { e.preventDefault(); chatToggle(false); } });
}
function chatToggle(on) {
  chatBuild(); CHAT.open = on; held.clear(); pointers.clear();
  if (on) { chatMarkRead(); chatRender(); sfx('page'); } else { try { CHAT.el.querySelector('#chatInput').blur(); canvas.focus(); } catch (e) { /* ok */ } }
  chatPlace();
}
function chatRender() {
  if (!CHAT.el) return;
  const q = CHAT.el.querySelector('#chatQuick'), lad = PUB.lad, lines = CHAT_QUICK.concat(CHAT_LAD[lad] ? [CHAT_LAD[lad]] : []);
  const key = lad + lines.length;
  if (q.dataset.k !== key) {
    q.dataset.k = key; q.innerHTML = '';
    lines.forEach((l, i) => { const b = document.createElement('button'); b.type = 'button'; b.textContent = l; if (i >= CHAT_QUICK.length) b.className = 'lad'; b.addEventListener('click', () => chatSend(l)); q.appendChild(b); });
  }
  const list = CHAT.el.querySelector('#chatList');
  if (!CHAT.msgs.length) { list.innerHTML = '<div class="none">Nobody’s said anything yet.</div>'; return; }
  list.innerHTML = CHAT.msgs.slice().reverse().map(m => {
    const c = CHAR_BY_ID[m.lad] || CHAR_BY_ID.tim, img = portraitImg(m.lad);
    return `<div class="m"><img alt="" src="${img ? img.src : ''}"><div><span class="n" style="color:${m.name === PROFILE.name ? '#ffd23f' : c.color}">${chatEsc(m.name)}</span><span class="t">${chatAgo(m.at)}</span><div class="x">${chatEsc(m.text)}</div></div></div>`;
  }).join('');
  if (CHAT.open) chatMarkRead();
}
// the tab and panel sit on the right edge of the game, only in the pub
function chatPlace() {
  if (!CHAT.el) return;
  const show = mode === 'pub' && !!HUB.kind && !!PROFILE.name && !PUB.view, r = canvas.getBoundingClientRect();
  if (!show) { CHAT.tab.style.display = 'none'; CHAT.el.style.display = 'none'; return; }
  const w = Math.round(Math.min(380, Math.max(260, r.width * 0.42)));
  CHAT.el.style.display = CHAT.open ? 'flex' : 'none';
  CHAT.el.style.left = (r.right - w) + 'px'; CHAT.el.style.top = r.top + 'px'; CHAT.el.style.width = w + 'px'; CHAT.el.style.height = r.height + 'px';
  CHAT.tab.style.display = CHAT.open ? 'none' : 'block';
  const u = chatUnread(), tabH = CHAT.tab.offsetHeight || 90;
  CHAT.tab.innerHTML = 'CHAT' + (u ? '<b>' + (u > 9 ? '9+' : u) + '</b>' : '');
  CHAT.tab.style.left = (r.right - (CHAT.tab.offsetWidth || 32)) + 'px'; CHAT.tab.style.top = Math.round(r.top + r.height * 0.42 - tabH / 2) + 'px';
  const who = CHAT.el.querySelector('#chatWho'), n = hubPeople().length; who.textContent = n ? '● ' + (n + 1) + ' online' : '';
}
function chatTick() {
  if (!HUB.kind) return;
  chatBuild(); chatPlace();
  if (CHAT.open && mode !== 'pub') CHAT.open = false;
  if (CHAT.open && performance.now() - (CHAT.agoT || 0) > 30000) { CHAT.agoT = performance.now(); chatRender(); }
}
// speech bubbles in the pub: anything said in the last six seconds, over the sayer's head
function chatBubbles() {
  const now = Date.now(), cx = cam.x, ghosts = hubGhosts();
  const last = {}; for (const m of CHAT.msgs) if (now - m.at < 6000 && now - m.at > -5000) last[m.name] = m;
  for (const name in last) {
    const m = last[name], g = name === PROFILE.name ? { x: PUB.x, y: PUB.y } : ghosts.find(o => o.name === name); if (!g) continue;
    const x = g.x - cx; if (x < -150 || x > W + 150) continue;
    ctx.save(); ctx.font = '700 13px ' + BODY;
    const lines = wrapLines(m.text, 190).slice(0, 4), w = Math.min(214, Math.max(...lines.map(l => ctx.measureText(l).width)) + 22), h = lines.length * 17 + 14;
    const bx = clamp(x - w / 2, 6, W - w - 6), by = g.y - 176 - h, k = Math.min(1, (6000 - (now - m.at)) / 400);
    ctx.globalAlpha = k;
    rrect(bx, by, w, h, 9); ctx.fillStyle = '#fbf6ea'; ctx.fill(); ctx.strokeStyle = OUT; ctx.lineWidth = 3; ctx.stroke();
    ctx.beginPath(); ctx.moveTo(x - 7, by + h - 1); ctx.lineTo(x, by + h + 10); ctx.lineTo(x + 7, by + h - 1); ctx.closePath(); ctx.fillStyle = '#fbf6ea'; ctx.fill();
    ctx.fillStyle = '#1b1b1b'; ctx.textAlign = 'left'; ctx.textBaseline = 'top'; lines.forEach((l, i) => ctx.fillText(l, bx + 11, by + 8 + i * 17));
    ctx.restore();
  }
}

// headless tests only: ?pubtest lets tools/v55/shots.py reach the game from outside
if (/[?&]pubtest/.test(location.search)) window.__pub = s => eval(s);
