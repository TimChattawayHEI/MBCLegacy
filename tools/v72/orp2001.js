// ================================================================== ORPINGTON 2001 (Version 72)
// A Saturday night in March 2001, between 1999 and Elba: the Pizza Express bus stop, over the mini roundabout, past Ram Ba Ba,
// the Blacksmiths (getting served under Sue's nose, then Alan, Jeff and Mick), then the Ram Ba Ba coach to Atlantis in
// Croydon. Backdrops: tools/v72/orp_bg.py (Meshy, from Tim's photos). Sprites: tools/v72/foe_sheets.py (PixelLab).
const ORP_KEYS = ['orp_street', 'orp_pub', 'orp_atlantis'];

// ---------------------------------------------------------------- who's in the Blacksmiths
Object.assign(FOES, {
  alan: { name: 'ALAN', hp: 58, speed: 96, dmg: 8, reach: 70, windup: 0.5, score: 320, ai: 'melee', rush: true,
    lines: ["You lot ain't from round 'ere.", 'Wassat? WASSAT?', "I'm fine. I'm FINE.", "Mum! MUM! They're startin'!"] },
  jeff: { name: 'JEFF', hp: 120, speed: 80, dmg: 13, reach: 80, windup: 0.6, score: 600, ai: 'melee', armor: true, kdAttack: true,
    lines: ['Outside. Now.', "You've spilt my pint.", "Dad said I'm allowed.", 'Come \'ere.'] },
  sue: { name: 'SUE', hp: 1, speed: 0, dmg: 0, reach: 0, windup: 1, score: 0, ai: 'melee', lines: ['OI!'] },
  mick: { name: 'MICK', hp: 360, speed: 84, dmg: 13, scale: 1.1, beatenWord: 'BARRED!', beatenLine: "...You're all barred. Same time next week?", sub: 'Landlord. Thirty years behind that bar.',
    intro: ["Right. Who's started it?", 'Not in my pub, son.'], lines: ['Get out of my pub!', "You're barred!", 'SUE! The bat!', "I've had bigger than you in 'ere."], tick: (b, dt, rage) => orpMick(b, dt, rage) },
});
['alan', 'jeff', 'sue', 'mick'].forEach(k => NO_EXTRA.add(k));
BOSS_CARD.jeff = ['JEFF', "Dad! They're starting!", ['jeff']];

// ---------------------------------------------------------------- the stages
Object.assign(STAGES, {
  orp_street: { era: 2001, title: 'THE HIGH STREET', sub: 'Orpington. Saturday, March 2001. 8pm.', bg: 'orp_street', ft: 352, fb: 506, len: 3688,
    music: 'codered', aggro: 2, aa: 0.3, intro: 'orpIntro',
    items: [{ w: 'cone', x: 700, y: 480 }, { w: 'alcopop', x: 1560, y: 450 }],
    breakables: [{ type: 'bin', x: 1180, y: 476, drop: 'chips' }, { type: 'bin', x: 2300, y: 460, drop: 'chips' }],
    waves: [
      // the bus stop: a crew from Petts Wood wants it more than you
      { at: 180, title: 'HOLD THE BUS STOP', groups: [[['townie', 'R'], ['townie', 'L'], ['ladette', 'R']], [['vibez', 'R'], ['townie', 'L']]] },
      // the mini roundabout: the traffic doesn't stop for you
      { at: 560, event: 'crossing' },
      { at: 980, event: 'coachBoard' },
      { at: 1300, groups: [[['vibez', 'R'], ['ladette', 'R'], ['townie', 'L']], [['bouncer', 'R'], ['vibez', 'L']]], food: 'chips' },
      { at: 2100, groups: [[['chunk', 'R'], ['townie', 'L'], ['ladette', 'R']]] },
      { at: 'end', final: true, groups: [[['bouncer', 'R'], ['townie', 'R'], ['vibez', 'L']], [['chunk', 'R'], ['ladette', 'L'], ['townie', 'R']]] },
    ] },
  orp_pub: { era: 2001, title: 'YE OLDE BLACKSMITH', sub: "8:40pm. Mick and Sue's. Don't let her see Byron.", bg: 'orp_pub', ft: 352, fb: 506, len: 2400,
    music: 'heist', aggro: 3, aa: 0.4, intro: 'orpPub',
    items: [{ w: 'cue', x: 1980, y: 470 }, { w: 'alcopop', x: 600, y: 470 }],
    breakables: [{ type: 'keg', x: 1660, y: 484, drop: 'chips' }],
    fruit: { x: 810 },
    waves: [
      { at: 40, event: 'served' },
      { at: 520, title: 'ALAN', groups: [[['alan', 'R'], ['regular', 'R'], ['regular', 'L']]] },
      { at: 1150, mini: true, miniKind: 'jeff', title: 'JEFF', groups: [[['jeff', 'R'], ['regular', 'L']], [['darts', 'R'], ['regular', 'R']]], food: 'chips' },
      { at: 'end', boss: 'mick', title: 'MICK' },
    ] },
  orp_atlantis: { era: 2001, title: 'ATLANTIS', sub: 'Croydon. 11pm. DJ EZ.', bg: 'orp_atlantis', ft: 352, fb: 506, len: 1920,
    music: 'alarmcall', aggro: 3, aa: 0.45, intro: 'orpClub', outro: 'orpHome', beat: 134,
    items: [{ w: 'alcopop', x: 1200, y: 470 }],
    breakables: [{ type: 'keg', x: 1500, y: 484, drop: 'chips' }],
    waves: [
      { at: 300, event: 'door' },
      { at: 1000, groups: [[['vibez', 'R'], ['vibez', 'R'], ['ladette', 'L']], [['townie', 'R'], ['vibez', 'L'], ['ladette', 'R']]] },
      { at: 'end', final: true, title: '2AM', groups: [[['bouncer', 'R'], ['vibez', 'R'], ['vibez', 'L']], [['chunk', 'R'], ['ladette', 'L'], ['vibez', 'R'], ['townie', 'L']]], food: 'chips' },
    ] },
});
// music (the chiptune tracks made for new levels, soundtrack/songs5.py to songs7.py): Code Red down the High Street, Heist while
// you get served, Lockdown when Mick comes for you, Alarm Call at Atlantis
ORP_KEYS.forEach(k => { BOSS_MUSIC[k] = 'boss1999'; });
BOSS_MUSIC.orp_pub = 'lockdown'; BOSS_KEYS.add('lockdown');
// the chapter goes between 1999 and Elba; every stage on the route is numbered in order again
ROUTE.splice(ROUTE.indexOf('airport'), 0, ...ORP_KEYS);
ROUTE.forEach((k, i) => { STAGES[k].n = i + 1; });
Object.assign(MESHY_BG, { orp_street: 4, orp_pub: 3, orp_atlantis: 2 });
for (const k of ORP_KEYS) ASSET_BG.push(...meshyFiles(k));
// the bar sticks out into the room: you stand in front of it, not in it; the pool table's legs
FLOOR_BLOCK.orp_pub = [[996, 1476, 432], [1830, 2196, 428]];

// ---------------------------------------------------------------- the group chats (2001: the Nokia)
Object.assign(CHATS, {
  orpIntro: [
    ['sys', 'March 2001. Saturday.'],
    ['tim', 'Pizza Express bus stop, 8pm. Blacksmiths, then Ram Ba Ba for the coach.'],
    ['seb', 'Get in Ram Ba Ba and nobody checks ID at Atlantis. Tactical.'],
    ['marc', 'DJ EZ!!! DJ EZ IS ON!!!'],
    ['byron', 'Will Sue serve me?'],
    ['kelly', 'no'],
    ['pearcy', 'stand behind me'],
    ['sam', 'Might be a bit late'],
    ['kelly', 'course you will'],
  ],
  orpPub: [
    ['sys', 'The Blacksmiths. 8:40pm.'],
    ['tim', "Sue's on the bar. Byron, keep out of her eyeline."],
    ['byron', 'I look 25'],
    ['kelly', 'you look 12'],
    ['seb', 'The fruit machines. Use them as cover.'],
    ['pearcy', "Alan's in. He's already wavey."],
  ],
  orpClub: [
    ['sys', 'Ram Ba Ba. 10:30pm. The Atlantis coach.'],
    ['tim', 'On the coach. Croydon. Nobody checks ID.'],
    ['kelly', 'the bouncer looked at me funny'],
    ['marc', 'DJ EZ, lads. DJ. EZ.'],
    ['seb', 'Stay together inside.'],
  ],
  orpHome: [
    ['sys', '2am. The coach back to Orpington.'],
    ['tim', 'Head count.'],
    ['byron', 'Kelly?'],
    ['kelly', 'been on this coach since 11'],
    ['kelly', 'the driver told me about his divorce twice'],
    ['marc', 'DJ EZ though'],
    ['kelly', 'I HEARD IT FROM THE CAR PARK'],
  ],
});

// ---------------------------------------------------------------- per frame
function updateOrp(dt) {
  if (!S || !ST || ST.era !== 2001) return;
  if (!S.npcs) S.npcs = [];
  updateNpcs(dt);
  if (S.ann) { S.ann.t += dt; if (S.ann.t > S.ann.life) S.ann = null; }
  if (S.key === 'orp_pub') orpSueTick(dt);
  if (S.key === 'orp_street') orpTraffic(dt);
}
function orpAnnounce(text, life) { S.ann = { text, t: 0, life: life || 3.2 }; sfx('page'); }
function orpEvent(ev) {
  if (!ST || ST.era !== 2001) return false;
  const done = () => { S.wave = null; S.waveIdx++; };
  if (ev === 'crossing') {   // the mini roundabout: cars come round it along the road, so keep to the pavement when one's coming
    S.traffic = { left: 4, t: 1.2 }; orpAnnounce('THE MINI ROUNDABOUT · MIND THE TRAFFIC'); done(); return true;
  }
  if (ev === 'coachBoard') {
    popWord(cam.x + W * 0.55, FT + 20, 150, 'RAM BA BA: ATLANTIS COACH 10.30', true); sfx('clink');
    say(player, pick(['Coach at half ten. Pint first.', "Blacksmiths, then back here.", "Ram Ba Ba. Remember the face, Kelly."]), 2.4, true); done(); return true;
  }
  if (ev === 'served') { orpServedStart(); return true; }
  if (ev === 'door') { orpDoor(); return true; }
  return false;
}

// ================================================================== the High Street: traffic round the roundabout
// a car comes along the road (the bottom of the street), a horn first; the pavement (the back of the floor) is safe
function orpTraffic(dt) {
  const tr = S.traffic; if (!tr || tr.left <= 0) return;
  tr.t -= dt; if (tr.t > 0) return;
  tr.left--; tr.t = rand(2.6, 4);
  hazards.push({ kind: 'moped', phase: 'warn', t: 0, dir: chance(0.5) ? 1 : -1, x: 0, y: rand(FB - 46, FB - 8), hit: new Set() });
  if (tr.left === 3) say(player, 'Wait for the green man!', 1.6, true);
}

// ================================================================== the Blacksmiths: getting served
// Sue pulls pints with her back to the room, then turns and looks it over. Get to the bar while she isn't looking, or stand
// at the fruit machines (they hide you). If she clocks you moving she sends you back to the door. Three goes, then it kicks
// off anyway.
const ORP_BAR = { x0: 1000, x1: 1470, sueX: 1250, top: 258 };
const ORP_HIDE = [[270, 410], [760, 870]];   // in front of the fruit machines, near the wall
function orpHidden(p) { return p.y < FT + 70 && ORP_HIDE.some(([a, b]) => p.x > a && p.x < b); }
function orpServedStart() {
  S.served = { phase: 'sneak', tries: 0, watch: false, t: rand(2.2, 3.2), seen: 0 };
  const sue = makeNpc('sue', ORP_BAR.sueX, 316); sue.face = 1; sue.state = 'idle'; sue.draw = orpDrawSue; sue.hp = 0; S.npcs.push(sue); S.sue = sue;
  orpAnnounce("GET SERVED · DON'T LET SUE SEE YOU MOVE", 4);
}
function orpSueTick(dt) {
  const sv = S.served, sue = S.sue; if (!sue) return;
  // during the fight she shouts from behind the bar now and then; it rings your ears
  if (!sv || sv.phase === 'done') { orpSueOi(dt); return; }
  const p = player;
  sv.t -= dt;
  if (sv.warn > 0) { sv.warn -= dt; if (sv.warn <= 0) { sv.watch = true; sue.face = -1; sue.state = 'idle'; } }
  else if (sv.t <= 0) {
    if (sv.watch) { sv.watch = false; sue.face = 1; sv.t = rand(2.4, 3.8); say(sue, pick(['Pint of Stella, love?', "Mick! Change the barrel!", "Who's next?"]), 1.6, true); }
    else { sv.warn = 0.6; sue.state = 'oiWind'; sue.t = 0; sv.t = rand(1.6, 2.6); popWord(sue.x, sue.y, 190, '!', false); }
  }
  if (sv.watch && canBeHit(p) && !orpHidden(p) && Math.hypot(p.vx || 0, p.vy || 0) > 30 && p.x < ORP_BAR.x1) {
    // clocked
    sv.tries++; sv.watch = false; sue.face = 1; sv.t = rand(2.4, 3.4); sfx('nope');
    say(sue, sv.tries >= 3 ? 'MICK! He\'s TWELVE!' : pick(['OI! How old are YOU?', "I know your mum!", 'Out. Come back with ID.']), 2, true);
    popWord(p.x, p.y, 170, 'CLOCKED!', true);
    if (sv.tries >= 3) { orpServedEnd(false); return; }
    p.x = 120; p.y = clamp(p.y, FT + 20, FB - 20); p.vx = p.vy = 0; cam.x = 0;
    return;
  }
  if (p.x > ORP_BAR.x0 + 30 && p.x < ORP_BAR.x1 && p.y < 482) orpServedEnd(true);   // stood at the bar (it's solid down to 432)
}
function orpServedEnd(ok) {
  const sv = S.served; sv.phase = 'done'; S.sue.face = -1; S.sue.state = 'idle'; S.sueOiT = rand(5, 7);
  if (ok) { popWord(player.x, player.y, 170, 'SERVED!', true); addScore(2000); sfx('jackpot'); say(S.sue, 'Six pints of Stella? Go on then.', 2.4, true); }
  setTimeout0(() => { if (S && S.key === 'orp_pub') { orpAnnounce("ALAN'S SPILT A PINT"); } }, ok ? 2.4 : 1.2);
  S.wave = null; S.waveIdx++;
}
function orpSueOi(dt) {
  const sue = S.sue; if (!S.wave || S.done) return;
  S.sueOiT = (S.sueOiT || 6) - dt;
  if (sue.state === 'oiWind') { if (sue.t > 0.7) { sue.state = 'oi'; sue.t = 0; orpOi(sue); } return; }
  if (sue.state === 'oi') { if (sue.t > 0.6) { sue.state = 'idle'; sue.t = 0; } return; }
  if (S.sueOiT <= 0) { S.sueOiT = rand(6, 9) * (S.bosses && S.bosses.length ? 0.8 : 1.3); sue.state = 'oiWind'; sue.t = 0; sue.face = Math.sign(player.x - sue.x) || -1; popWord(sue.x, sue.y, 190, '!', false); }
}
// "OI!": anyone stood in front of her within earshot is stunned for a moment (jump, or be in the air, and it misses you)
function orpOi(sue) {
  popWord(sue.x, sue.y, 210, 'OI!', true); sfx('airhorn'); addShake(4);
  for (const p of players()) {
    if (!canBeHit(p) || p.z > 20 || p.state === 'down' || p.state === 'getup') continue;
    if (Math.abs(p.x - sue.x) < 620) { p.state = 'hurt'; p.t = -0.6; p.vx = p.vy = 0; p.atk = null; p.running = false; popWord(p.x, p.y, 160, 'EARS RINGING!', false); }
  }
}
// Sue stands behind the bar: only her top half shows over the counter
function orpDrawSue(n) {
  ctx.save(); ctx.beginPath(); ctx.rect(0, 0, W, ORP_BAR.top); ctx.clip(); drawEntity(n); ctx.restore();
  if (S.served && S.served.phase !== 'done') {   // an eye over her head while she's looking
    const x = Math.round((n.x - cam.x) / 2) * 2, y = 150;
    const sv = S.served, tag = sv.watch ? ['WATCHING', '#ff4d4d'] : sv.warn > 0 ? ['TURNING...', '#ffd24d'] : ['POURING', '#d8e6ff'];
    ctx.fillStyle = 'rgba(5,6,14,0.7)'; ctx.fillRect(x - 58, y - 11, 116, 22); pxText(tag[0], x, y, 12, tag[1]);
  }
}

// ================================================================== Mick
// A big slow haymaker (the shared melee), the belly barge down your lane, and once he's angry, the bell: LAST ORDERS
// brings two regulars in off their stools.
function orpMick(b, dt, rage) {
  const p = player, dx = Math.abs(p.x - b.x), dy = Math.abs(p.y - b.y);
  const faceP = () => { if (Math.abs(p.x - b.x) > 8) b.face = Math.sign(p.x - b.x); };
  switch (b.state) {
    case 'idle': case 'walk': {
      if (b.cool > 0 || !playerTargetable()) return false;
      if (rage && !b.rang) { b.rang = true; b.state = 'bellWind'; b.t = 0; b.vx = b.vy = 0; say(b, 'LAST ORDERS!', 1.8, true); return true; }
      if (dy < 30 && dx > 170 && dx < 560 && chance(0.55)) { b.state = 'bellyWind'; b.t = 0; b.vx = b.vy = 0; faceP(); say(b, pick(['Come \'ere!', 'Mind the belly!']), 1.2, true); return true; }
      return false;
    }
    case 'bellyWind': b.vx = b.vy = 0; faceP(); if (b.t > 0.6 * D().wind) { b.state = 'belly'; b.t = 0; b.hitP = false; sfx('brrap'); } return true;
    case 'belly':
      b.vx = b.face * (rage ? 620 : 540); b.vy = 0; b.walk += dt * 14; if (chance(0.5)) dust(b.x - b.face * 20, b.y, 1, 20);
      if (!b.hitP && pHittable(40) && Math.abs(p.x - b.x) < 56 && Math.abs(p.y - b.y) < 28) { b.hitP = true; hitP(b, 14, b.face, true, 460); popWord(p.x, p.y, 150, 'BELLIED!', false); }
      if ((b.face > 0 && b.x > cam.x + W - 60) || (b.face < 0 && b.x < cam.x + 60) || b.t > 1.2) { b.vx = 0; addShake(5); if (b.hitP) { b.state = 'rest'; b.t = 0; } else bDaze(b, 1.3, 'PUFFED OUT!'); }
      return true;
    case 'bellWind': b.vx = b.vy = 0; if (b.t > 0.5) { b.state = 'bell'; b.t = 0; sfx('clink'); setTimeout0(() => sfx('clink'), 0.18); setTimeout0(() => sfx('clink'), 0.36);
      popWord(b.x, b.y, 200, 'DING DING DING!', true); spawnGroup([['regular', 'L'], ['regular', 'R']]); } return true;
    case 'bell': if (b.t > 0.8) { b.state = 'rest'; b.t = 0; } return true;
  }
  return false;
}

// ================================================================== Atlantis: the door, then the beat
function orpDoor() {
  const bx = 780, by = FT + 40;
  const d1 = makeNpc('doorman', bx, by - 26), d2 = makeNpc('doorman', bx + 40, by + 26); d1.face = d2.face = -1; S.npcs.push(d1, d2);
  if (player.def.id === 'kelly') {   // it happened: Kelly upset the bouncers and sat on the coach till 2am
    say(d1, 'Not you, mate. Not tonight.', 2.4, true);
    setTimeout0(() => say(player, "...I'll be on the coach then.", 2.4, true), 2.2);
    setTimeout0(() => { showBanner('KELLY WAITED ON THE COACH', 'Till 2am. The driver told him about his divorce. Twice.', 3.6); sfx('meh'); }, 4.6);
    setTimeout0(() => { if (S && !S.done) { S.done = true; S.endT = 0.1; } }, 8.6);
    S.wave = null; S.waveIdx = ST.waves.length; return;
  }
  say(d1, "In you go, lads. Not him. Not the one with the big head.", 2.6, true);
  setTimeout0(() => popWord(cam.x + 140, FT + 40, 150, "KELLY: BUT I'M WITH THEM!", true), 1.6);
  setTimeout0(() => { d1.remove = d2.remove = true; orpAnnounce('ATLANTIS · HIT ON THE BEAT FOR MORE', 3.6); }, 3.4);
  S.wave = null; S.waveIdx++;
}
// the 2-step beat: hits that land on it do more, and a ring pulses with it
function orpBeatPhase() {
  const bpm = ST && ST.beat; if (!bpm || !S || player.x < 1000) return -1;
  const per = 60 / bpm;
  // locked to Alarm Call itself when it's playing (its loop is exactly 128 beats), else to the stage clock
  if (actx && trk.src && trk.key === mus.key && mus.key === ST.music) {
    const lat = (actx.outputLatency || 0) + (actx.baseLatency || 0), el = actx.currentTime - lat - trk.t0;
    return (((el % per) + per) % per) / per;
  }
  return ((S.time || 0) % per) / per;
}
function orpBeatMult(a, t) {
  if (!ST || !ST.beat || !a || a.kind !== 'player' || t === a) return 1;
  const ph = orpBeatPhase(); if (ph < 0) return 1;
  if (ph < 0.14 || ph > 0.9) { if (!S.beatPop || S.time - S.beatPop > 0.6) { S.beatPop = S.time; popWord(t.x, t.y, 170, 'ON BEAT!', false); } return 1.6; }
  return 1;
}
function orpDrawFore() {
  if (!ST || ST.era !== 2001) return;
  if (S.ann) {   // the announcement plate, as the 2006 stages have
    const a = S.ann, k = Math.min(1, a.t / 0.15, (a.life - a.t) / 0.25), w = Math.max(320, a.text.length * 12 + 60), x = W / 2 - w / 2, y = 112;
    ctx.save(); ctx.globalAlpha = Math.max(0, k);
    ctx.fillStyle = '#0a0c1e'; ctx.fillRect(x, y, w, 30); ctx.fillStyle = '#c9a227'; ctx.fillRect(x, y, w, 2); ctx.fillRect(x, y + 28, w, 2);
    pxText(a.text, W / 2, y + 15, 12, '#ffe08a'); ctx.restore();
  }
  const ph = orpBeatPhase(); if (ph < 0) return;
  // strobe on the bar line, and the beat ring
  if ((S.bar = (S.lastPh > 0.5 && ph < 0.5) ? (S.bar || 0) + 1 : (S.bar || 0)) % 4 === 0 && ph < 0.12) { ctx.fillStyle = 'rgba(235,240,255,0.10)'; ctx.fillRect(0, 0, W, H); }
  S.lastPh = ph;
  const r = 16 + (1 - ph) * 14, on = ph < 0.14 || ph > 0.9;
  ctx.save(); ctx.strokeStyle = on ? '#7cf7ff' : 'rgba(180,140,255,0.6)'; ctx.lineWidth = on ? 4 : 2; ctx.beginPath(); ctx.arc(W / 2, H - 34, r, 0, Math.PI * 2); ctx.stroke();
  ctx.fillStyle = on ? '#7cf7ff' : 'rgba(255,255,255,0.7)'; ctx.font = '800 11px ' + BODY; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText('BEAT', W / 2, H - 34); ctx.restore();
}
