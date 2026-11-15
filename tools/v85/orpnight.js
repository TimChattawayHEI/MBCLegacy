// ================================================================== Version 85: the rest of the Orpington night
// 1. The night's clock: a Nokia screen at the top of every Orpington place, 20:00 at the bus stop to 02:00 at lights up.
//    Each place starts at its own time and the minutes tick on while you're there, never past the next place's time.
//    Once you've passed Ram Ba Ba's chalkboard it also shows COACH 22:30 (orange from ten to ten).
// 2. The blag at the Atlantis door: the bouncer's questions and a nerve meter. HIT when the needle is in the green for a
//    cool answer; miss (or wait) and you stammer, and the next one is harder. Two cool answers of three: SMOOTH, 3,000.
//    The Ram Ba Ba wristband gets you in either way. Kelly is always refused.
// 3. The chats in 2001 text speak on the Nokia, and a present-day chat first (the Blacksmiths is Aksular now).
const ORP_CLOCK = {
  orp_street: { at: [20 * 60, 20 * 60 + 22, 20 * 60 + 30, 20 * 60 + 34], end: 20 * 60 + 40 },
  orp_pub: { at: [20 * 60 + 40, 20 * 60 + 48, 21 * 60 + 20, 21 * 60 + 55], end: 22 * 60 + 24 },
  orp_atlantis: { at: [22 * 60 + 55, 23 * 60 + 40], end: 26 * 60 },
};
const ORP_COACH = 22 * 60 + 30;
function orpClockTick(dt) {
  const C = ORP_CLOCK[S.key]; if (!C) return;
  if (S.ckSc !== S.sc) { S.ckSc = S.sc; S.ckT = 0; }
  S.ckT += dt;
  const i = S.sc || 0, from = C.at[i] != null ? C.at[i] : C.at[C.at.length - 1], to = (C.at[i + 1] != null ? C.at[i + 1] : C.end) - 1;
  let m = from + S.ckT / 4;   // a minute every four seconds
  if (S.dance) m = Math.max(m, from + S.dance.wave * 26);   // the dance floor: the waves carry the night on to 2am
  if (S.lights) m = 26 * 60;
  S.night = Math.min(S.lights ? 26 * 60 : to, m);
  if (S.key !== 'orp_street' || i >= 2) S.coachSeen = true;
}
function orpClockStr(m) { m = Math.floor(m); return String(Math.floor(m / 60) % 24).padStart(2, '0') + ':' + String(m % 60).padStart(2, '0'); }
function orpDrawClock() {
  if (S.night == null || S.frog) return;
  const coach = S.coachSeen && S.key !== 'orp_atlantis', w = 118, h = coach ? 50 : 36, x = W / 2 - w / 2, y = 12;
  ctx.save();
  rrect(x - 4, y - 4, w + 8, h + 8, 8); ctx.fillStyle = '#2c3236'; ctx.fill();
  const g = ctx.createLinearGradient(0, y, 0, y + h); g.addColorStop(0, '#a9c27a'); g.addColorStop(1, '#8fab62');
  ctx.fillStyle = g; ctx.fillRect(x, y, w, h);
  const ink = '#1f2a14';
  for (let i = 0; i < 4; i++) { ctx.fillStyle = ink; ctx.fillRect(x + 5, y + 26 - i * 5, 2 + i, 3); }   // signal bars
  ctx.fillStyle = ink; ctx.font = '700 22px "Courier New", ui-monospace, monospace'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  const blink = Math.floor(time * 2) % 2 ? ':' : ' ', s = orpClockStr(S.night);
  ctx.fillText(s.slice(0, 2) + blink + s.slice(3), x + w / 2 + 4, y + 19);
  if (coach) {
    const late = S.night >= ORP_COACH - 40;
    ctx.fillStyle = late ? '#8a2a0a' : ink; ctx.font = '700 11px "Courier New", ui-monospace, monospace';
    ctx.fillText(late && Math.floor(time * 3) % 2 ? '' : 'COACH 22:30', x + w / 2, y + 40);
  }
  ctx.restore();
}

// ---------------------------------------------------------------- the blag
const BLAG_Q = [
  ['How old are you?', 'Eighteen.', 'Eigh... eighteen. Nearly. Yes.'],
  ['Date of birth?', 'Fourth of March, eighty-two.', 'Nineteen... eighty... the March one.'],
  ['Star sign?', 'Pisces.', 'Is that the crab?'],
  ['Where\'d you get that wristband?', 'Ram Ba Ba, mate.', 'Found it. I mean, Ram Ba Ba.'],
  ['Who\'s on tonight?', 'DJ EZ.', 'Er... the garage one?'],
];
function orpBlagStart(d1, done) {
  orpHowto('THE DOOR', ['The bouncer has a few questions. Keep your nerve.',
    'HIT when the needle is in the green to answer cool. Miss it, or wait too long, and you start to sweat.'], () => {
    const qs = [BLAG_Q[0]].concat(BLAG_Q.slice(1).sort(() => Math.random() - 0.5).slice(0, 2));
    S.blag = { d1, done, qs, q: -1, t: 0, phase: 'gap', nerve: 0, cool: 0, res: [], ph: Math.random() * 6, kelly: player.def.id === 'kelly' };
  });
}
function orpBlagNeedle(B) {
  const w = 2.0 + B.q * 0.6 + B.nerve * 1.6, t = B.t;
  return clamp(0.5 + 0.4 * Math.sin(t * w + B.ph) + 0.08 * Math.sin(t * w * 2.7 + 1) + (B.kelly ? 0.18 * Math.sin(t * 9) : 0), 0.02, 0.98);
}
function orpBlagZone(B) { return B.kelly ? 0.035 : Math.max(0.06, 0.14 - B.q * 0.02 - B.nerve * 0.04); }
function orpBlagTick(dt) {
  const B = S.blag; B.t += dt;
  for (const p of players()) { p.vx = p.vy = 0; if (p.atk || p.state === 'walk' || p.state === 'run' || p.state === 'punch') { p.atk = null; setIdle(p); } }
  if (B.phase === 'gap') {
    if (B.t < 1.0) return;
    B.q++;
    if (B.q >= B.qs.length) { B.phase = 'end'; B.t = 0; return; }
    say(B.d1, B.qs[B.q][0], 2.4, true); B.phase = 'ask'; B.t = 0; B.ph = Math.random() * 6; return;
  }
  if (B.phase === 'ask') {
    const hit = B.t > 0.35 && (pressed.has('punch') || pressed.has('jump') || taps.length);
    if (!hit && B.t < 4.5) return;
    const n = orpBlagNeedle(B), ok = hit && Math.abs(n - 0.5) < orpBlagZone(B);
    B.res.push(ok); B.last = { ok, n, t: 0 };
    if (ok) { B.cool++; sfx('ready'); popWord(player.x, player.y, 170, 'COOL', true); }
    else { B.nerve = Math.min(1, B.nerve + 0.4); sfx('nope'); popWord(player.x, player.y, 170, 'GULP', true); addShake(2); }
    say(player, B.qs[B.q][ok ? 1 : 2], 2, true);
    B.phase = 'gap'; B.t = 0; return;
  }
  if (B.phase === 'end') {
    if (B.t < 0.3) return;
    const smooth = !B.kelly && B.cool >= 2;
    S.blag = null; S.blagRes = { cool: B.cool, smooth };
    if (smooth) { addScore(3000); popWord(player.x, player.y, 200, 'SMOOTH!', true); sfx('cheer'); }
    if (B.done) B.done(smooth, B.kelly);
  }
}
function orpDrawBlag() {
  const B = S.blag; if (!B) return;
  const w = 380, x = W / 2 - w / 2, y = H - 118;
  ctx.save();
  ctx.fillStyle = 'rgba(8,10,24,0.86)'; ctx.fillRect(x - 16, y - 34, w + 32, 100);
  ctx.fillStyle = '#c9a227'; ctx.fillRect(x - 16, y - 34, w + 32, 2);
  pxText('NERVE', x + 26, y - 18, 11, '#ffe08a');
  for (let i = 0; i < B.qs.length; i++) {   // one pip per question
    const r = B.res[i]; circle(x + w - 50 + i * 22, y - 18, 6);
    ctx.fillStyle = r == null ? '#2b3b42' : r ? '#7ad36a' : '#e5533d'; ctx.fill();
  }
  // the meter: red at the ends, amber, a green middle that shrinks as you sweat
  const z = orpBlagZone(B);
  const gr = ctx.createLinearGradient(x, 0, x + w, 0);
  gr.addColorStop(0, '#b0302a'); gr.addColorStop(0.3, '#d68a2a'); gr.addColorStop(0.5, '#d6b42a'); gr.addColorStop(0.7, '#d68a2a'); gr.addColorStop(1, '#b0302a');
  ctx.fillStyle = gr; ctx.fillRect(x, y, w, 18);
  ctx.fillStyle = '#58c45a'; ctx.fillRect(x + w * (0.5 - z), y, w * z * 2, 18);
  ctx.strokeStyle = OUT; ctx.lineWidth = 3; ctx.strokeRect(x, y, w, 18);
  const live = B.phase === 'ask', n = live ? orpBlagNeedle(B) : (B.last ? B.last.n : 0.5), nx = x + w * n;
  ctx.fillStyle = '#ffffff'; ctx.fillRect(nx - 2, y - 6, 4, 30);
  ctx.beginPath(); ctx.moveTo(nx - 7, y - 10); ctx.lineTo(nx + 7, y - 10); ctx.lineTo(nx, y - 2); ctx.closePath(); ctx.fill();
  if (live && Math.floor(time * 3) % 2 === 0) pxText(touchUI ? 'TAP TO ANSWER' : 'HIT TO ANSWER', W / 2, y + 42, 11, '#9fe8ff');
  else if (!live && B.last) pxText(B.last.ok ? 'COOL AS YOU LIKE' : 'SWEATING', W / 2, y + 42, 11, B.last.ok ? '#7ad36a' : '#ff8a8a');
  ctx.restore();
}

// ---------------------------------------------------------------- the chats: 2001 text speak, and now
Object.assign(CHATS, {
  orpNow: [
    ['sys', 'Now.'],
    ['tim', 'Drove down Orpington High Street today. The Blacksmiths is a Turkish place now. Aksular.'],
    ['seb', 'And Ram Ba Ba?'],
    ['tim', 'Fiesta Mexicana.'],
    ['byron', 'Sue never did serve me'],
    ['kelly', "I'm still on that coach"],
    ['marc', 'DJ EZ though'],
    ['tim', 'Remember the texts? March 2001.'],
  ],
  orpIntro: [
    ['sys', 'March 2001. Sat.'],
    ['tim', 'c u @ pizza xpress bus stop 8. blacksmiths then ram ba ba 4 the coach. dnt b l8'],
    ['seb', 'ram ba ba wristband = no ID @ atlantis. tactical'],
    ['marc', 'DJ EZ!!! DJ EZ IS ON!!!'],
    ['byron', 'wil sue serve me?'],
    ['kelly', 'no'],
    ['pearcy', 'stnd behind me'],
    ['sam', 'mite b l8'],
    ['kelly', 'course u wil m8'],
  ],
  orpPub: [
    ['sys', 'The Blacksmiths. 8:40pm.'],
    ['tim', 'sues on the bar. 6 pints. no1 gets IDd'],
    ['byron', 'i look 25'],
    ['kelly', 'u look 12'],
    ['seb', 'move wen her back is turned. freeze wen it isnt'],
    ['pearcy', 'alans in. hes already wavey'],
  ],
  orpClub: [
    ['sys', 'Ram Ba Ba. 10:30pm. The Atlantis coach.'],
    ['tim', 'on the coach. croydon. no1 checks ID'],
    ['kelly', 'the bouncer lookd @ me funny'],
    ['marc', 'DJ EZ lads. DJ. EZ.'],
    ['seb', 'stay 2gether in the q'],
  ],
  orpHome: [
    ['sys', '2am. The coach back to Orpington.'],
    ['tim', 'head count'],
    ['byron', 'kelly?'],
    ['kelly', 'bin on this coach since 11'],
    ['kelly', 'the driver told me bout his divorce twice'],
    ['marc', 'DJ EZ tho'],
    ['kelly', 'I HEARD IT FROM THE CAR PARK'],
  ],
});
// the present-day chat comes first (starting the chapter, not carrying on), then the March 2001 comic page, then the Nokia
function orpNowFirst(lines, next, headline, era) {
  if (lines !== CHATS.orpIntro || headline || (next && next.orpNow)) return false;
  const after = () => { if (next) next(); }; after.orpNow = true;
  openChat(CHATS.orpNow, () => openChat(lines, after, headline, era), 'NOW');
  return true;
}
