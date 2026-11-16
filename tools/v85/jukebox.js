// ================================================================== Version 85: THE JUKEBOX in the Harvest Moon
// At the far end of the pub, past the Snake cabinet. Three pages:
// SONGS: the songs with vocals (MCs, sung choruses, the lads in the words) and GUITAR: the indie songs. Each has an A side
//   and a B side (the two takes PixelLab made). They aren't in the app: they stream from the repo's jukebox/ folder on
//   GitHub at the commit the app was built from (or main), so they need signal, and they cost the update nothing.
// SOUNDTRACK: the game's own tracks, from the app, so they play offline.
// Pick one and it plays in the pub in place of the pub track, while you walk about and play the other games; it stops
// when you leave. Sound off or the music slider at 0 mutes it like the rest of the music.
let JUKE_RAW = 'https://raw.githubusercontent.com/TimChattawayHEI/MBCLegacy/main/jukebox/';
const JUKE_X = 3190;
const JUKE = {
  pages: [
    { id: 'songs', title: 'SONGS', note: 'Streamed: needs signal', list: [
      ['vocal_frequency', 'The Frequency', 'Vocal garage. MC Mystery in the house', 1999],
      ['vocal_soundz', 'Soundz FM', 'Pirate radio speed garage', 1999],
      ['vocal_arrivals', 'Arrivals', 'Sunny house. Peaceful. Yeah, right', 2002],
      ['vocal_highstreet', 'The High Street', 'Garage. Coach at half ten', 2001],
      ['vocal_blacksmith', 'Ye Olde Blacksmith', 'Sue, Sue, don’t turn around', 2001],
      ['vocal_atlantis', 'Atlantis', 'Garage MC and a sung chorus', 2001],
      ['vocal_train', 'The 21:12', 'Bassline to Charing Cross', 2006],
      ['vocal_smoking', 'The Smoking Area', 'Grime. Mind your phone', 2006],
      ['vocal_nightbus', 'The N47', 'Top deck, front seat', 2006],
      ['vocal_naval', 'Naval Operations', 'Whispered garage. Gary lives', 2007],
      ['vocal_social', 'The Social', 'Bassline. No refunds', 2007],
      ['vocal_ramsden', 'Ramsden', 'Grime. Never changed', 2007],
      ['vocal_passmic', 'Pass the Mic', 'Jungle. Four MCs', 2007],
      ['vocal_passmic5', 'Pass the Mic 2', 'Jungle. Five voices', 2007],
    ] },
    { id: 'guitar', title: 'GUITAR', note: 'Streamed: needs signal', list: [
      ['indie_station', 'Orpington Station', 'Fast and choppy indie', 2006],
      ['indie_cross', 'Charing Cross', 'Swaggering fuzz riff', 2006],
      ['indie_miles', 'Fourteen Miles', 'Marc walks home at dawn', 2006],
    ] },
    { id: 'game', title: 'SOUNDTRACK', note: 'The game’s own music: plays offline', list: [
      ['title', 'Carp Diem', 'The title theme'], ['garage', 'The Frequency', 'Act 1, 1999'], ['soundz', 'Soundz FM', 'The pirate station'],
      ['boss1999', 'Pirate Signal', 'Boss, 1999'], ['airport', 'Duty Free', 'Elba arrivals'], ['road', 'Coast Road', 'The drive'],
      ['divebar', 'Che Succede', 'The dive bar'], ['beach', 'Factor Nothing', 'The beach'], ['club', 'Biggest Club', 'The club'],
      ['bosselba', 'Vendetta', 'Boss, Elba'], ['codered', 'Code Red', 'The High Street, 2001'], ['heist', 'Heist', 'The Blacksmiths'],
      ['alarmcall', 'Alarm Call', 'Atlantis'], ['platform', 'Platform 2', 'Orpington station'], ['train', 'The 21:12', 'The train'],
      ['terminus', 'Terminus', 'Charing Cross'], ['smoking', 'The Smoking Area', 'Round the back'], ['nightbus', 'The N47', 'Top deck'],
      ['boss2006', 'Boss, 2006', 'The night out'], ['arrival', 'Seize the Streets', 'The lake'], ['naval', 'Night Bite', 'The dinghy'],
      ['social', 'Last Orders', 'The social'], ['pegnine', 'Peg Nine', 'Dawn standoff'], ['boss', 'The Big One', 'Boss'],
      ['ramsden', 'Always on Fire', 'Ramsden'], ['lady', 'Rewind Selecta', 'Lady Addict'], ['lockdown', 'Lockdown', 'Spare'],
      ['pub', 'The Harvest Moon', 'This pub'], ['pubgames', 'Pub Games', 'Darts and the fruit machine'], ['snake', 'Snake', 'The Nokia'],
    ] },
  ],
  page: 0, sel: 0, side: 1, scroll: 0,
  now: null,      // { page, i, side, title } what's playing
  el: null,       // the <audio> for streamed songs
  state: '',      // 'loading' | 'playing' | 'error'
};
JUKE.pages[2].list = JUKE.pages[2].list.filter(r => TRACKS[r[0]]);
function jukeVol() { return settings.sound ? TRACK_GAIN * 0.6 * (settings.mus ?? 10) / 10 : 0; }
function jukeUrl(k, side) { return JUKE_RAW + k + '_' + side + '.mp3'; }
function jukeStopStream() { const a = JUKE.el; if (a) { try { a.pause(); a.removeAttribute('src'); a.load(); } catch (e) { /* gone */ } } }
function jukeStop(quiet) {
  jukeStopStream();
  const was = JUKE.now; JUKE.now = null; JUKE.state = '';
  if (was && (mode === 'pub' || mode === 'juke')) musicSet('pub');
  if (!quiet && was) sfx('page');
}
function jukePlay(pg, i, side) {
  const P = JUKE.pages[pg], r = P.list[i]; if (!r) return;
  jukeStopStream();
  JUKE.now = { page: pg, i, side, title: r[1] + (P.id === 'game' ? '' : ' (' + (side === 1 ? 'A' : 'B') + ' side)'), stream: P.id !== 'game' };
  sfx('pickup');
  if (P.id === 'game') {   // the game's own track, through the music player (it loops)
    JUKE.state = 'playing'; mus.key = null; musicSet(r[0]);
    return;
  }
  musicSet(null);
  let a = JUKE.el;
  if (!a) {
    a = JUKE.el = new Audio(); a.preload = 'auto';
    a.addEventListener('playing', () => { if (JUKE.now && JUKE.now.stream) JUKE.state = 'playing'; });
    a.addEventListener('waiting', () => { if (JUKE.now && JUKE.now.stream) JUKE.state = 'loading'; });
    a.addEventListener('error', () => { if (JUKE.now && JUKE.now.stream && a.getAttribute('src')) JUKE.state = 'error'; });
    a.addEventListener('ended', () => {   // on to the next song, same side
      const n = JUKE.now; if (!n || !n.stream) return;
      const L = JUKE.pages[n.page].list; jukePlay(n.page, (n.i + 1) % L.length, n.side);
    });
  }
  JUKE.state = 'loading';
  a.volume = jukeVol(); a.src = jukeUrl(r[0], side);
  const p = a.play(); if (p && p.catch) p.catch(() => { if (JUKE.now && JUKE.now.stream && JUKE.state !== 'playing') JUKE.state = 'error'; });
}
// keeps the stream's volume with the settings, and stops it anywhere but the pub and its games
function jukeTick() {
  const a = JUKE.el;
  if (JUKE.now && JUKE.now.stream && a) { const v = jukeVol(); if (Math.abs(a.volume - v) > 0.001) a.volume = v; }
  if (JUKE.now && !['pub', 'juke', 'mini', 'endings', 'trophies'].includes(mode)) jukeStop(true);
  // a pub game or a sting changed the music: the jukebox's own track stops, a stream pauses until we're back
  if (JUKE.now && JUKE.now.stream && a) {
    const away = mode === 'mini';
    if (away && !a.paused) a.pause(); else if (!away && a.paused && JUKE.state !== 'error' && a.getAttribute('src')) { const p = a.play(); if (p && p.catch) p.catch(() => {}); }
  }
  if (JUKE.now && JUKE.now.stream && (mode === 'pub' || mode === 'juke') && mus.key) musicSet(null);
  if (JUKE.now && !JUKE.now.stream && mode === 'pub') { const k = JUKE.pages[2].list[JUKE.now.i][0]; if (mus.key !== k) { mus.key = null; musicSet(k); } }
}
function jukeOpen() { mode = 'juke'; modeT = 0; sfx('page'); JUKE.sel = Math.min(JUKE.sel, JUKE.pages[JUKE.page].list.length - 1); }
function jukeClose() { mode = 'pub'; modeT = 0; sfx('page'); }
// the layout: page tabs along the top, the list on the left, the record on the right
const JK = { x: 70, y: 60, w: W - 140, h: H - 120, rowH: 34, rows: 8 };
function jukeRowsTop() { return JK.y + 96; }
function jukeTabRect(i) { const w = 170; return { x: JK.x + 24 + i * (w + 10), y: JK.y + 20, w, h: 40 }; }
function jukeRowRect(j) { return { x: JK.x + 20, y: jukeRowsTop() + j * JK.rowH, w: 470, h: JK.rowH - 4 }; }
function jukeBtn(id) {
  const rx = JK.x + 520, rw = JK.w - 540;
  if (id === 'A') return { x: rx, y: JK.y + 300, w: rw / 2 - 6, h: 46 };
  if (id === 'B') return { x: rx + rw / 2 + 6, y: JK.y + 300, w: rw / 2 - 6, h: 46 };
  if (id === 'play') return { x: rx, y: JK.y + 300, w: rw, h: 46 };
  if (id === 'stop') return { x: rx, y: JK.y + 356, w: rw, h: 40 };
  if (id === 'close') return { x: JK.x + JK.w - 64, y: JK.y + 20, w: 44, h: 40 };
  return null;
}
const inR = (t, r) => r && t.x >= r.x && t.x <= r.x + r.w && t.y >= r.y && t.y <= r.y + r.h;
function updateJuke() {
  if (modeT < 0.15) return;
  const P = JUKE.pages[JUKE.page], n = P.list.length, stream = P.id !== 'game';
  const keep = () => { JUKE.scroll = clamp(JUKE.scroll, Math.max(0, JUKE.sel - JK.rows + 1), Math.min(JUKE.sel, Math.max(0, n - JK.rows))); };
  if (pressed.has('escape') || pressed.has('back') || pressed.has('jump')) { jukeClose(); return; }
  if (pressed.has('up')) { JUKE.sel = (JUKE.sel + n - 1) % n; keep(); sfx('swing'); }
  if (pressed.has('down')) { JUKE.sel = (JUKE.sel + 1) % n; keep(); sfx('swing'); }
  if (pressed.has('left') || pressed.has('right')) {
    if (stream && !(pressed.has('left') && JUKE.side === 1) && !(pressed.has('right') && JUKE.side === 2)) { JUKE.side = pressed.has('left') ? 1 : 2; sfx('swing'); }
    else { JUKE.page = (JUKE.page + (pressed.has('left') ? JUKE.pages.length - 1 : 1)) % JUKE.pages.length; JUKE.sel = 0; JUKE.scroll = 0; JUKE.side = pressed.has('left') ? 2 : 1; sfx('page'); }
  }
  if (pressed.has('punch') || pressed.has('start')) jukePlay(JUKE.page, JUKE.sel, stream ? JUKE.side : 1);
  if (pressed.has('special') || pressed.has('grab')) jukeStop();
  for (const t of taps) {
    if (inR(t, jukeBtn('close'))) { jukeClose(); return; }
    for (let i = 0; i < JUKE.pages.length; i++) if (inR(t, jukeTabRect(i)) && i !== JUKE.page) { JUKE.page = i; JUKE.sel = 0; JUKE.scroll = 0; JUKE.side = 1; sfx('page'); return; }
    for (let j = 0; j < JK.rows; j++) { const i = JUKE.scroll + j; if (i < n && inR(t, jukeRowRect(j))) { if (JUKE.sel === i && !stream) jukePlay(JUKE.page, i, 1); JUKE.sel = i; sfx('swing'); } }
    if (inR(t, { x: JK.x + 20, y: jukeRowsTop() - 30, w: 470, h: 26 }) && JUKE.scroll > 0) { JUKE.scroll = Math.max(0, JUKE.scroll - JK.rows + 1); }
    if (inR(t, { x: JK.x + 20, y: jukeRowsTop() + JK.rows * JK.rowH, w: 470, h: 30 }) && JUKE.scroll + JK.rows < n) { JUKE.scroll = Math.min(n - JK.rows, JUKE.scroll + JK.rows - 1); }
    if (stream && inR(t, jukeBtn('A'))) { JUKE.side = 1; jukePlay(JUKE.page, JUKE.sel, 1); }
    if (stream && inR(t, jukeBtn('B'))) { JUKE.side = 2; jukePlay(JUKE.page, JUKE.sel, 2); }
    if (!stream && inR(t, jukeBtn('play'))) jukePlay(JUKE.page, JUKE.sel, 1);
    if (JUKE.now && inR(t, jukeBtn('stop'))) jukeStop();
  }
}
function jukeButton(r, label, on, col) {
  ctx.save(); rrect(r.x, r.y, r.w, r.h, 10);
  ctx.fillStyle = on ? (col || '#ff2e8a') : 'rgba(255,255,255,0.08)'; ctx.fill();
  ctx.strokeStyle = col || '#ff2e8a'; ctx.lineWidth = 2; ctx.stroke();
  ctx.font = '800 15px ' + BODY; ctx.fillStyle = on ? '#fff' : '#efe6d2'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillText(label, r.x + r.w / 2, r.y + r.h / 2 + 1); ctx.restore();
}
function drawJuke() {
  drawPub();
  ctx.save();
  ctx.fillStyle = 'rgba(6,4,10,0.72)'; ctx.fillRect(0, 0, W, H);
  rrect(JK.x, JK.y, JK.w, JK.h, 16); ctx.fillStyle = '#1b0b14'; ctx.fill();
  const g = ctx.createLinearGradient(JK.x, 0, JK.x + JK.w, 0); g.addColorStop(0, '#ff2e8a'); g.addColorStop(1, '#16c6d9');
  ctx.strokeStyle = g; ctx.lineWidth = 4; ctx.stroke();
  const P = JUKE.pages[JUKE.page], n = P.list.length, stream = P.id !== 'game';
  JUKE.pages.forEach((pg, i) => jukeButton(jukeTabRect(i), pg.title, i === JUKE.page, i === 2 ? '#16c6d9' : '#ff2e8a'));
  jukeButton(jukeBtn('close'), '✕', false, '#93a3a1');
  ctx.font = '700 12px ' + BODY; ctx.fillStyle = '#c79ab0'; ctx.textAlign = 'left'; ctx.textBaseline = 'middle';
  ctx.fillText(P.note + (JUKE.scroll > 0 ? '   ▲ more' : ''), JK.x + 26, jukeRowsTop() - 16);
  for (let j = 0; j < JK.rows; j++) {
    const i = JUKE.scroll + j; if (i >= n) break;
    const r = P.list[i], R = jukeRowRect(j), sel = i === JUKE.sel, playing = JUKE.now && JUKE.now.page === JUKE.page && JUKE.now.i === i;
    if (sel) { rrect(R.x, R.y, R.w, R.h, 8); ctx.fillStyle = 'rgba(255,46,138,0.22)'; ctx.fill(); }
    ctx.fillStyle = playing ? '#ffd23f' : sel ? '#fff' : '#efe6d2'; ctx.font = '800 15px ' + BODY; ctx.textAlign = 'left';
    ctx.fillText((playing ? '♫ ' : '') + r[1], R.x + 12, R.y + R.h / 2);
    ctx.font = '600 12px ' + BODY; ctx.fillStyle = '#93a3a1'; ctx.textAlign = 'right';
    ctx.fillText(r[3] ? String(r[3]) : r[2], R.x + R.w - 10, R.y + R.h / 2);
  }
  if (JUKE.scroll + JK.rows < n) { ctx.font = '700 12px ' + BODY; ctx.fillStyle = '#c79ab0'; ctx.textAlign = 'left'; ctx.fillText('▼ ' + (n - JUKE.scroll - JK.rows) + ' more', JK.x + 26, jukeRowsTop() + JK.rows * JK.rowH + 12); }
  // the record: what's selected, and its two sides
  const r = P.list[JUKE.sel] || P.list[0], rx = JK.x + 520, rw = JK.w - 540;
  const cx = rx + rw / 2, cy = JK.y + 170, spin = JUKE.now && JUKE.state === 'playing' ? time * 3 : 0;
  ctx.save(); ctx.translate(cx, cy); ctx.rotate(spin);
  ctx.fillStyle = '#0c0c10'; ctx.beginPath(); ctx.arc(0, 0, 78, 0, Math.PI * 2); ctx.fill();
  ctx.strokeStyle = 'rgba(255,255,255,0.08)'; ctx.lineWidth = 1; for (let k = 30; k < 76; k += 6) { ctx.beginPath(); ctx.arc(0, 0, k, 0, Math.PI * 2); ctx.stroke(); }
  ctx.fillStyle = stream ? (JUKE.side === 1 ? '#ff2e8a' : '#16c6d9') : '#ffd23f'; ctx.beginPath(); ctx.arc(0, 0, 26, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = '#0c0c10'; ctx.beginPath(); ctx.arc(0, 0, 4, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = 'rgba(0,0,0,0.5)'; ctx.font = '900 13px ' + BODY; ctx.textAlign = 'center'; ctx.fillText(stream ? (JUKE.side === 1 ? 'A' : 'B') : '♪', 0, -12);
  ctx.restore();
  ctx.textAlign = 'center'; ctx.font = '800 17px ' + BODY; ctx.fillStyle = '#fff'; ctx.fillText(r[1], cx, JK.y + 268);
  ctx.font = '600 12px ' + BODY; ctx.fillStyle = '#c79ab0'; ctx.fillText(r[2], cx, JK.y + 286);
  if (stream) { jukeButton(jukeBtn('A'), '▶ A SIDE', JUKE.side === 1); jukeButton(jukeBtn('B'), '▶ B SIDE', JUKE.side === 2, '#16c6d9'); }
  else jukeButton(jukeBtn('play'), '▶ PLAY', false, '#ffd23f');
  if (JUKE.now) jukeButton(jukeBtn('stop'), '■ STOP', false, '#93a3a1');
  // now playing
  ctx.textAlign = 'left'; ctx.font = '700 13px ' + BODY;
  const msg = !JUKE.now ? (touchUI ? 'Tap a song, then A SIDE or B SIDE. The two sides are two takes of the same song.' : 'Up and down to pick, left and right for the side, HIT to play, JUMP to close.')
    : JUKE.state === 'error' ? 'Can’t reach that one: it needs signal. The SOUNDTRACK page plays offline.'
    : JUKE.state === 'loading' ? 'Loading ' + JUKE.now.title + '…' : 'Now playing: ' + JUKE.now.title;
  ctx.fillStyle = JUKE.state === 'error' ? '#ff8a8a' : JUKE.now ? '#ffd23f' : '#93a3a1';
  ctx.fillText(msg, JK.x + 26, JK.y + JK.h - 16);
  ctx.restore();
}
// in the pub: the jukebox itself, its glow, and a little "now playing" plate
function jukeDraw(cx) {
  const img = pubImg('jukebox'); if (!img) return;
  bgPut(img, JUKE_X - img.width, 414);
  const on = JUKE.now && JUKE.state === 'playing';
  const x = Math.round((JUKE_X - img.width - cx) / 2) * 2, w = img.width * 2;
  ctx.save(); ctx.globalCompositeOperation = 'lighter';
  const pulse = on ? 0.22 + 0.1 * Math.sin(time * 8) : 0.08 + 0.03 * Math.sin(time * 2);
  const gr = ctx.createRadialGradient(x + w / 2, 414 - img.height * 1.4, 4, x + w / 2, 414 - img.height * 1.4, 120);
  gr.addColorStop(0, 'rgba(255,46,138,' + pulse.toFixed(3) + ')'); gr.addColorStop(1, 'rgba(22,198,217,0)');
  ctx.fillStyle = gr; ctx.fillRect(x - 100, 414 - img.height * 2 - 80, w + 200, img.height * 2 + 120);
  ctx.restore();
}
// what's playing, top left in the pub (under the lives and LEAVE)
function jukePlate() {
  if (!JUKE.now) return;
  ctx.save(); const t = '\u266B ' + (JUKE.state === 'error' ? 'No signal' : JUKE.now.title); ctx.font = '800 12px ' + BODY;
  const tw = ctx.measureText(t).width + 24; pubPanel(16, 74, tw, 32);
  ctx.fillStyle = JUKE.state === 'error' ? '#ff8a8a' : '#ffd23f'; ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; ctx.fillText(t, 28, 90); ctx.restore();
}
