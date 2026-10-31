// Version 71: the story told in comic pages, an ending for every lad, the damage report, and the endings wall at the
// Harvest Moon. The panels are painted in Meshy (tools/v71/comics.py); the game writes the captions and the speech so
// they're sharp and easy to change here.

// page -> its layout ('L3' a tall panel left and two stacked right, 'L2' two side by side, 'L1' one big), the title over
// it, and per panel a caption and any speech: [lad, words, x, y] with x, y where the bubble sits (0..1 of the panel)
const COMIC_PAGES = {
  p1999: { lay: 'L3', title: 'CHAPTER ONE', sub: 'ORPINGTON, 1999', panels: [
    { cap: "Present day. Seb's loft.", say: [['seb', 'Still got it.', 0.6, 0.12]] },
    { cap: '104.1 FM. Soundz. Where it all started.' },
    { cap: 'KRSSSHHHHHHHH', say: [['seb', 'Uh oh.', 0.62, 0.2]] } ] },
  pmill: { lay: 'L2', title: 'MIDNIGHT', sub: '1ST JANUARY 2000', panels: [
    { cap: 'Bromley. The year 2000 arrives on time.' },
    { cap: 'Seb heads for the transmitter.', say: [['seb', 'Hold on to something.', 0.55, 0.12]] } ] },
  pelba: { lay: 'L2', title: 'CHAPTER TWO', sub: 'ELBA, 2002', panels: [
    { cap: 'Elba, Italy. Two weeks. A nice quiet holiday.' },
    { cap: 'Day one.', say: [['pearcy', 'its well hot', 0.72, 0.12]] } ] },
  pespace: { lay: 'L2', title: 'NIGHT ONE', sub: 'THE HIRE CAR', panels: [
    { cap: 'Four kilometres. Easy.' },
    { cap: 'The excess was not easy.', say: [['sam', 'What happened?', 0.72, 0.2]] } ] },
  p2006: { lay: 'L2', title: 'CHAPTER THREE', sub: 'NIGHTLIFE, 2006', panels: [
    { cap: 'Orpington station. 8:55.', say: [['byron', '9pm means 8:55.', 0.62, 0.12]] },
    { cap: 'The 21:12 to Charing Cross. Sam is still in bed.' } ] },
  phome: { lay: 'L2', title: 'MORNING', sub: 'BROMLEY', panels: [
    { cap: '06:45. A man of principle.' },
    { cap: 'Present day. The group chat never sleeps.' } ] },
  pcarp: { lay: 'L3', title: 'CHAPTER FOUR', sub: 'CARP DIEM', panels: [
    { cap: "Tim's cooking device.", say: [['tim', "It's not an outbuilding.", 0.6, 0.1]] },
    { cap: "Denise's Fishery, Lincolnshire. 49 hours on the clock." },
    { cap: 'Somewhere under the water, Big Gary is waiting.' } ] },
  pfire: { lay: 'L2', title: 'MIDNIGHT', sub: 'NAVAL OPERATIONS', panels: [
    { cap: 'One dinghy. One paddle. One disposable barbecue.' },
    { cap: 'The lake was four feet deep.' } ] },
  pend: { lay: 'L1', title: 'SUNDAY', sub: '8:59AM', panels: [
    { cap: 'Big Gary. Forty years in that lake.', say: [['tim', 'GARY!', 0.7, 0.14]] } ] },
};
// which group chats get a page first (the jump into a chapter, or the moment itself) and which get one after
const COMIC_BEFORE = { airport: 'pelba', divebar: 'pespace', nlIntro: 'p2006', arrival: 'pcarp', soundzOutro: 'pmill', navalOutro: 'pfire' };
const COMIC_AFTER = { prologue: 'p1999', nlHome: 'phome' };
const COMIC_RECTS = {
  L3: [[24, 72, 372, 452], [408, 72, 528, 220], [408, 304, 528, 220]],
  L2: [[24, 129, 450, 338], [486, 129, 450, 338]],
  L1: [[78, 72, 804, 452]],
};
const comicFile = (id, i) => 'comic/pages/' + id + '_' + i;
function comicPreload(id) { const P = COMIC_PAGES[id]; if (P) P.panels.forEach((_, i) => bgImg(comicFile(id, i))); }
let comicPassed = null, comic = null; const COMIC_STOP = {};
function comicKeyOf(lines, table) { for (const k in table) if (CHATS[k] === lines) return k; return null; }
// called at the top of openChat: a page before this chat (once), and a page after it
function comicWrap(lines, next, headline, era) {
  if (comicPassed === lines) { comicPassed = null; }
  else { const kb = comicKeyOf(lines, COMIC_BEFORE); if (kb) { comicShow(COMIC_BEFORE[kb], () => { comicPassed = lines; openChat(lines, next, headline, era); }); return COMIC_STOP; } }
  const ka = comicKeyOf(lines, COMIC_AFTER); if (ka) { comicPreload(COMIC_AFTER[ka]); return () => comicShow(COMIC_AFTER[ka], next); }
  return next;
}
function comicShow(id, done) {
  const P = COMIC_PAGES[id]; if (!P) { done && done(); return; }
  comicPreload(id);
  comic = { id, P, done, n: 0, t: 0, nT: 0, wait: 0 };
  mode = 'comic'; modeT = 0; banner = null; sfx('page');
}
function comicEnd() { const d = comic && comic.done; comic = null; sfx('page'); if (d) d(); }
const COMIC_SKIP = { x: W - 104, y: 14, w: 86, h: 32 };
function updateComic(dt) {
  const c = comic; if (!c) return; c.t += dt; c.nT += dt;
  // wait for this panel's picture (a second at most) before it comes in
  if (c.n < c.P.panels.length && !bgImg(comicFile(c.id, c.n)) && c.wait < 1) { c.wait += dt; return; }
  if (c.n === 0) { c.n = 1; c.nT = 0; sfx('swing'); }
  const go = pressed.has('punch') || pressed.has('start') || pressed.has('jump') || taps.some(t => !(t.x > COMIC_SKIP.x - 8 && t.y < COMIC_SKIP.y + COMIC_SKIP.h + 8));
  if (pressed.has('escape') || pressed.has('back') || taps.some(t => t.x > COMIC_SKIP.x - 8 && t.y < COMIC_SKIP.y + COMIC_SKIP.h + 8)) { comicEnd(); return; }
  const last = c.n >= c.P.panels.length;
  if ((go && c.nT > 0.25) || (!last && c.nT > 3.2)) {
    if (last) { comicEnd(); return; }
    c.n++; c.nT = 0; c.wait = 0; sfx('swing');
  }
}
function comicPaper(tint) {
  ctx.fillStyle = '#130f1d'; ctx.fillRect(0, 0, W, H);
  const g = ctx.createRadialGradient(W / 2, H / 2, 60, W / 2, H / 2, W * 0.7); g.addColorStop(0, tint || 'rgba(242,162,58,0.12)'); g.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  ctx.fillStyle = 'rgba(255,255,255,0.035)';
  for (let y = 0; y < H; y += 12) for (let x = (y / 12) % 2 ? 6 : 0; x < W; x += 12) ctx.fillRect(x, y, 2, 2);   // halftone
}
function comicBubbleAt(x, y, words, lad, k) {
  ctx.save(); ctx.font = '700 15px ' + BODY;
  const lines = wrapLines(words, 200), w = Math.max(...lines.map(l => ctx.measureText(l).width)) + 26, h = lines.length * 19 + 16;
  const bx = Math.round(x - w / 2), by = Math.round(y);
  ctx.globalAlpha = k; ctx.translate(x, y + h / 2); ctx.scale(0.8 + 0.2 * k, 0.8 + 0.2 * k); ctx.translate(-x, -(y + h / 2));
  ctx.beginPath(); ctx.moveTo(bx + w * 0.35, by + h - 2); ctx.lineTo(bx + w * 0.28, by + h + 16); ctx.lineTo(bx + w * 0.5, by + h - 2); ctx.closePath();
  ctx.fillStyle = '#fbf6ea'; ctx.fill(); ctx.strokeStyle = OUT; ctx.lineWidth = 3; ctx.stroke();
  rrect(bx, by, w, h, 14); ctx.fillStyle = '#fbf6ea'; ctx.fill(); ctx.stroke();
  ctx.fillStyle = '#fbf6ea'; ctx.fillRect(bx + w * 0.35 + 2, by + h - 4, w * 0.15 - 4, 4);
  ctx.fillStyle = '#1b1b1b'; ctx.textAlign = 'center'; ctx.textBaseline = 'top';
  lines.forEach((l, i) => ctx.fillText(l, x, by + 9 + i * 19));
  const C = CHAR_BY_ID[lad]; if (C) { ctx.font = '800 9px ' + BODY; const nw = ctx.measureText(C.name).width + 10; ctx.fillStyle = C.color || '#f2a23a'; rrect(bx + 8, by - 8, nw, 14, 4); ctx.fill(); ctx.fillStyle = '#0d0d12'; ctx.textAlign = 'left'; ctx.fillText(C.name, bx + 13, by - 5); }
  ctx.restore();
}
function drawComic() {
  const c = comic; if (!c) return;
  comicPaper();
  ctx.textBaseline = 'middle';
  textOut(c.P.title, 24, 34, '30px ' + DISPLAY, '#ffd23f', OUT, 7, 'left');
  ctx.font = '30px ' + DISPLAY; const tw = ctx.measureText(c.P.title).width;
  if (c.P.sub) { ctx.font = '800 14px ' + BODY; ctx.fillStyle = '#efe6d2'; ctx.textAlign = 'left'; ctx.fillText(c.P.sub, 24 + tw + 16, 36); }
  const R = COMIC_RECTS[c.P.lay];
  c.P.panels.forEach((p, i) => {
    if (i >= c.n) return;
    const [x, y, w, h] = R[i], age = i === c.n - 1 ? c.nT : 9, k = Math.min(1, age / 0.3), e = easeOut(k);
    const img = bgImg(comicFile(c.id, i)), dx = (1 - e) * 60;
    ctx.save(); ctx.globalAlpha = k; ctx.translate(dx, 0);
    ctx.fillStyle = '#000'; ctx.fillRect(x - 5, y - 5, w + 10, h + 10);
    ctx.fillStyle = '#efe6d2'; ctx.fillRect(x - 2, y - 2, w + 4, h + 4);
    if (img) {   // cover the panel, centred
      const s = Math.max(w / img.width, h / img.height), sw = w / s, sh = h / s;
      ctx.imageSmoothingEnabled = true; ctx.drawImage(img, (img.width - sw) / 2, (img.height - sh) / 2, sw, sh, x, y, w, h); ctx.imageSmoothingEnabled = false;
    } else { ctx.fillStyle = '#221a30'; ctx.fillRect(x, y, w, h); }
    // the caption box, top left
    if (p.cap && age > 0.2) {
      ctx.font = '800 13px ' + BODY; const lines = wrapLines(p.cap.toUpperCase(), Math.min(w - 40, 330)), cw = Math.max(...lines.map(l => ctx.measureText(l).width)) + 18;
      ctx.fillStyle = '#000'; ctx.fillRect(x + 8, y + 8, cw + 4, lines.length * 17 + 14);
      ctx.fillStyle = '#ffd23f'; ctx.fillRect(x + 10, y + 10, cw, lines.length * 17 + 10);
      ctx.fillStyle = '#16120c'; ctx.textAlign = 'left'; ctx.textBaseline = 'top';
      const n = Math.floor((age - 0.2) * 60); let left = n;
      lines.forEach((l, j) => { ctx.fillText(l.slice(0, Math.max(0, left)), x + 19, y + 16 + j * 17); left -= l.length; });
    }
    for (const [lad, words, fx, fy] of p.say || []) if (age > 0.7) comicBubbleAt(x + w * fx, y + h * fy, words, lad, Math.min(1, (age - 0.7) / 0.15));
    ctx.restore();
  });
  // skip, and carry on when it's all there
  const S2 = COMIC_SKIP; rrect(S2.x, S2.y, S2.w, S2.h, 8); ctx.fillStyle = 'rgba(15,22,25,0.85)'; ctx.fill(); ctx.strokeStyle = 'rgba(239,230,210,0.5)'; ctx.lineWidth = 2; ctx.stroke();
  ctx.font = '800 12px ' + BODY; ctx.fillStyle = '#efe6d2'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText('SKIP', S2.x + S2.w / 2, S2.y + S2.h / 2 + 1);
  if (c.n >= c.P.panels.length && c.nT > 0.9 && Math.floor(time * 2) % 2) { ctx.font = '800 12px ' + BODY; ctx.fillStyle = '#ffd23f'; ctx.fillText(touchUI ? 'TAP TO CARRY ON' : 'J TO CARRY ON', W / 2, H - 9); }
}

// ------------------------------------------------------------------ endings: one for each lad, collected when you finish
// the campaign as him, kept on this phone (settings.endings), and up on the wall at the Harvest Moon.
// ENDINGS: Tim's words. An empty one shows "To be continued..."
const ENDINGS = {
  tim: '', seb: '', pearcy: '', byron: '', kelly: '', marc: '', sam: '', ash: '', thet: '',
};
const ENDING_LADS = ['tim', 'seb', 'pearcy', 'byron', 'kelly', 'marc', 'sam', 'ash', 'thet'];
function endingsGot() { return (settings.endings || []).filter(id => ENDING_LADS.includes(id)); }
function runStat(k, sub) { if (!run) return; const s = run.st || (run.st = {}); s[k] = (s[k] || 0) + 1; if (sub) s[k + ':' + sub] = (s[k + ':' + sub] || 0) + 1; }
let ending = null;
// after the last group chat: each lad's ending (yours collected), then the damage report, then the win screen
function endingShow(done) {
  const lads = (NET.on ? PL : [player]).filter(Boolean);
  const cards = lads.map(p => { const id = p.def.id, mine = !NET.on || isMine(p), had = endingsGot().includes(id);
    if (mine && !had && ENDING_LADS.includes(id)) { settings.endings = endingsGot().concat(id); saveSettings(); }
    return { id, fresh: mine && !had }; });
  ENDING_LADS.forEach(id => bgImg('ladcard/' + id));
  ending = { cards, i: 0, t: 0, done, report: true, from: 'run' };
  mode = 'ending'; modeT = 0; banner = null; musicSet('title'); sfx('airhorn');
}
function endingView(id, back) { ending = { cards: [{ id, fresh: false }], i: 0, t: 0, done: back, report: false, from: 'wall' }; mode = 'ending'; modeT = 0; sfx('page'); }
function updateEnding(dt) {
  const e = ending; if (!e) return; e.t += dt;
  const go = pressed.has('punch') || pressed.has('start') || pressed.has('jump') || taps.length;
  if ((pressed.has('escape') || pressed.has('back')) && e.from === 'wall') { const d = e.done; ending = null; d && d(); return; }
  if (!go || e.t < 0.8) return;
  sfx('page'); e.t = 0;
  if (e.i < e.cards.length - 1) { e.i++; return; }
  if (e.report && e.i === e.cards.length - 1) { e.i++; return; }   // on to the damage report
  const d = e.done; ending = null; d && d();
}
function drawEndingCard(id, t, fresh) {
  const C = CHAR_BY_ID[id] || CHAR_BY_ID.tim, col = C.color || '#f2a23a';
  comicPaper(col + '33');
  const card = bgImg('ladcard/' + id), k = easeOut(Math.min(1, t / 0.35));
  if (card) { const s = 2.6, w = card.width * s, h = card.height * s;
    ctx.save(); ctx.imageSmoothingEnabled = false; ctx.globalAlpha = k; ctx.drawImage(card, Math.round(40 - (1 - k) * 160), H - h - 10, w, h); ctx.restore(); }
  const x = 420, a = Math.min(1, Math.max(0, (t - 0.25) / 0.3));
  ctx.save(); ctx.globalAlpha = a;
  ctx.font = '800 14px ' + BODY; ctx.fillStyle = '#ffd23f'; ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; ctx.fillText('WHERE ARE THEY NOW?', x, 96);
  textOut(C.name, x, 140, '48px ' + DISPLAY, col, OUT, 8, 'left');
  const line = ENDINGS[id] || 'To be continued...';
  ctx.font = '700 19px ' + BODY; const lines = wrapLines(line, 470), bh = lines.length * 26 + 28;
  ctx.fillStyle = '#000'; ctx.fillRect(x - 4, 180, 494, bh + 8); ctx.fillStyle = '#efe6d2'; ctx.fillRect(x - 2, 182, 490, bh + 4);
  ctx.fillStyle = '#1b1b1b'; ctx.textBaseline = 'top';
  let left = Math.floor(Math.max(0, t - 0.5) * 45); lines.forEach((l, j) => { ctx.fillText(l.slice(0, Math.max(0, left)), x + 12, 198 + j * 26); left -= l.length + 1; });
  ctx.restore();
  if (t > 1.2) {   // the stamp
    const got = endingsGot().length;
    ctx.save(); ctx.translate(x + 330, 210 + bh + 50); ctx.rotate(-0.08); ctx.globalAlpha = Math.min(1, (t - 1.2) / 0.15);
    const s = fresh ? 'ENDING COLLECTED' : 'ENDING', sub = got + ' OF ' + ENDING_LADS.length + ' ON THE WALL AT THE HARVEST MOON';
    ctx.strokeStyle = fresh ? '#e8443a' : '#93a3a1'; ctx.lineWidth = 3; ctx.strokeRect(-150, -26, 300, 52);
    textOut(s, 0, -7, '20px ' + DISPLAY, fresh ? '#e8443a' : '#93a3a1', OUT, 4, 'center');
    ctx.font = '800 9px ' + BODY; ctx.fillStyle = fresh ? '#e8443a' : '#93a3a1'; ctx.textAlign = 'center'; ctx.fillText(sub, 0, 14);
    ctx.restore();
  }
}
function drawDamage(t) {
  comicPaper('rgba(232,68,58,0.14)');
  textOut('THE DAMAGE', W / 2 + 120, 50, '40px ' + DISPLAY, '#ffd23f', OUT, 8, 'center');
  const s = (run && run.st) || {}, mm = Math.floor((run ? run.totalTime : 0) / 60), ss = Math.floor((run ? run.totalTime : 0) % 60);
  const rows = [
    ['KNOCKOUTS', fmtN(run ? run.kills : 0)],
    ['FOOD EATEN', fmtN(s.food || 0) + ((s['food:kebab'] || 0) ? '  (' + s['food:kebab'] + ' KEBAB' + (s['food:kebab'] > 1 ? 'S' : '') + ')' : '')],
    ['SPECIALS FIRED', fmtN(s.specials || 0)],
    ['TIMES ON THE FLOOR', fmtN(s.floored || 0)],
    ['WEAPONS THROWN', fmtN(s.thrown || 0)],
    ['BOSSES BEATEN', fmtN(s.bosses || 0)],
    ['ROUNDS BOUGHT', fmtN(s.rounds || 0)],
    ['LIVES LOST', fmtN(run ? run.livesLost : 0)],
    ['TIME', mm + 'm ' + String(ss).padStart(2, '0') + 's'],
  ];
  if (s['specials:sam']) rows.splice(3, 0, ['TIMES SAM FELL ASLEEP', fmtN(s['specials:sam'])]);
  rows.forEach(([l, v], i) => {
    const at = 0.4 + i * 0.22; if (t < at) return;
    if (!ending['tick' + i]) { ending['tick' + i] = 1; sfx('swing'); }
    const y = 104 + i * 38, x0 = 330, x1 = 920;
    ctx.font = '800 15px ' + BODY; ctx.fillStyle = '#efe6d2'; ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; ctx.fillText(l, x0, y);
    const lw = ctx.measureText(l).width;
    ctx.font = '22px ' + DISPLAY; const vw = ctx.measureText(v).width;
    ctx.fillStyle = 'rgba(239,230,210,0.25)'; for (let d = x0 + lw + 10; d < x1 - vw - 10; d += 8) ctx.fillRect(d, y + 4, 3, 2);
    textOut(v, x1, y, '22px ' + DISPLAY, '#ffd23f', OUT, 4, 'right');
  });
  // Marc, of course
  const keep = modeT, keepC = clearInfo; clearInfo = ending.marc || (ending.marc = {}); modeT = t - 0.6;
  try { drawMarcTally(); } finally { modeT = keep; clearInfo = keepC; }
}
function drawEnding() {
  const e = ending; if (!e) return;
  if (e.i < e.cards.length) drawEndingCard(e.cards[e.i].id, e.t, e.cards[e.i].fresh); else drawDamage(e.t);
  if (e.t > 1.6 && Math.floor(time * 2) % 2) { ctx.font = '800 12px ' + BODY; ctx.fillStyle = '#ffd23f'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(touchUI ? 'TAP TO CARRY ON' : 'J TO CARRY ON', W / 2, H - 12); }
}

// the endings wall at the Harvest Moon: past the trophy cabinet, a frame for every lad; yours have his picture in.
// HIT opens the wall: pick a lad to read his ending
const ENDINGS_X = 2660;
let endWall = { sel: 0 };
function endingsWallDraw(cx) {
  const x0 = Math.round((ENDINGS_X - 150 - cx) / 2) * 2; if (x0 > W + 10 || x0 + 300 < -10) return;
  ctx.fillStyle = '#2a190f'; ctx.fillRect(x0 - 8, 150, 316, 214); ctx.fillStyle = '#5a3a22'; ctx.fillRect(x0 - 4, 154, 308, 206); ctx.fillStyle = '#1a120c'; ctx.fillRect(x0, 158, 300, 198);
  const got = endingsGot();
  ENDING_LADS.forEach((id, i) => {
    const fx = x0 + 12 + (i % 3) * 98, fy = 166 + Math.floor(i / 3) * 62, on = got.includes(id), p = bgImg('portraits/' + id);
    ctx.fillStyle = on ? '#c9a227' : '#4a3a2a'; ctx.fillRect(fx, fy, 82, 56); ctx.fillStyle = '#0d0a08'; ctx.fillRect(fx + 4, fy + 4, 74, 48);
    if (on && p) { ctx.save(); ctx.imageSmoothingEnabled = false; ctx.drawImage(p, 0, 0, p.width, Math.round(p.width * 0.65), fx + 4, fy + 4, 74, 48); ctx.restore(); }
    else { ctx.font = '22px ' + DISPLAY; ctx.fillStyle = '#3a2e24'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText('?', fx + 41, fy + 29); }
  });
}
function endingsWallText(cx) {
  const x = ENDINGS_X - cx; if (x < -170 || x > W + 170) return;
  textOut('WHERE ARE THEY NOW', x, 136, '14px ' + DISPLAY, '#ffd23f', OUT, 4);
}
function endingsOpen() { ENDING_LADS.forEach(id => bgImg('ladcard/' + id)); endWall = { sel: Math.max(0, ENDING_LADS.indexOf(endingsGot()[0] || 'tim')) }; mode = 'endings'; modeT = 0; sfx('page'); }
function endingsClose() { mode = 'pub'; modeT = 0; sfx('page'); }
const endCell = i => ({ x: 90 + (i % 5) * 160, y: 110 + Math.floor(i / 5) * 210, w: 140, h: 190 });
function updateEndings() {
  if (modeT < 0.2) return;
  if (pressed.has('escape') || pressed.has('back') || pressed.has('jump')) { endingsClose(); return; }
  const n = ENDING_LADS.length;
  if (pressed.has('left')) { endWall.sel = (endWall.sel + n - 1) % n; sfx('swing'); }
  if (pressed.has('right')) { endWall.sel = (endWall.sel + 1) % n; sfx('swing'); }
  if (pressed.has('up') || pressed.has('down')) { endWall.sel = (endWall.sel + 5) % n; sfx('swing'); }
  let pick = pressed.has('punch') || pressed.has('start') ? endWall.sel : -1;
  for (const t of taps) { for (let i = 0; i < n; i++) { const c = endCell(i); if (t.x > c.x && t.x < c.x + c.w && t.y > c.y && t.y < c.y + c.h) pick = i; } if (pick < 0 && t.y > H - 50) { endingsClose(); return; } }
  if (pick >= 0) { endWall.sel = pick; const id = ENDING_LADS[pick];
    if (endingsGot().includes(id)) endingView(id, () => { mode = 'endings'; modeT = 0; });
    else { sfx('grab'); endWall.msg = 'Finish the campaign as ' + CHAR_BY_ID[id].name + ' to put him on the wall.'; endWall.msgT = 2.5; } }
  if (endWall.msgT > 0) endWall.msgT -= 1 / 60;
}
function drawEndings() {
  comicPaper();
  textOut('WHERE ARE THEY NOW', W / 2, 44, '34px ' + DISPLAY, '#ffd23f', OUT, 7);
  const got = endingsGot();
  ctx.font = '600 12px ' + BODY; ctx.fillStyle = '#93a3a1'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillText(got.length + ' of ' + ENDING_LADS.length + ' endings. Finish the campaign as a lad to get his.', W / 2, 78);
  ENDING_LADS.forEach((id, i) => {
    const c = endCell(i), on = got.includes(id), C = CHAR_BY_ID[id], card = bgImg('ladcard/' + id), sel = i === endWall.sel;
    ctx.fillStyle = '#000'; ctx.fillRect(c.x - 3, c.y - 3, c.w + 6, c.h + 6);
    ctx.fillStyle = sel ? '#ffd23f' : on ? '#efe6d2' : '#3a3440'; ctx.fillRect(c.x - 1, c.y - 1, c.w + 2, c.h + 2);
    ctx.fillStyle = on ? (C.color || '#444') + '44' : '#17141f'; ctx.fillRect(c.x + 2, c.y + 2, c.w - 4, c.h - 4);
    if (card) { ctx.save(); ctx.imageSmoothingEnabled = false; if (!on) ctx.filter = 'brightness(0)'; ctx.globalAlpha = on ? 1 : 0.55;
      const s = Math.min((c.w - 8) / card.width, (c.h - 30) / card.height); ctx.drawImage(card, c.x + (c.w - card.width * s) / 2, c.y + c.h - 28 - card.height * s, card.width * s, card.height * s); ctx.restore(); }
    ctx.fillStyle = '#0d0a10'; ctx.fillRect(c.x + 2, c.y + c.h - 26, c.w - 4, 24);
    ctx.font = '15px ' + DISPLAY; ctx.fillStyle = on ? (C.color || '#efe6d2') : '#56636a'; ctx.textAlign = 'center'; ctx.fillText(on ? C.name : '???', c.x + c.w / 2, c.y + c.h - 13);
  });
  ctx.font = '600 12px ' + BODY; ctx.fillStyle = endWall.msgT > 0 ? '#ffd23f' : '#93a3a1';
  ctx.fillText(endWall.msgT > 0 ? endWall.msg : (touchUI ? 'Tap a lad to read his ending. Tap here to go back.' : 'Arrows to choose, J to read, K to go back.'), W / 2, H - 22);
}
