// ================================================================== ORPINGTON 2001 (Version 72, rebuilt in Version 73)
// A Saturday night in March 2001, between 1999 and Elba. Every place is one screen, one Meshy painting (tools/v73/scenes.py),
// with a wipe between them, so nothing is stitched: the Pizza Express bus stop, the crossing, Ram Ba Ba, outside the
// Blacksmiths; inside the Blacksmiths (the lounge, the bar, the pool room, the bar again for Mick); the Atlantis queue and
// the dance floor. Each place has its own job, explained on screen when you get there. Sprites: tools/v72/foe_sheets.py.
const ORP_KEYS = ['orp_street', 'orp_pub', 'orp_atlantis'];
const ORP_LADS = ['tim', 'seb', 'pearcy', 'byron', 'kelly', 'marc', 'sam'];

// ---------------------------------------------------------------- who's out
Object.assign(FOES, {
  alan: { name: 'ALAN', hp: 70, speed: 96, dmg: 8, reach: 70, windup: 0.5, score: 400, ai: 'melee', rush: true,
    lines: ["You lot ain't from round 'ere.", 'Wassat? WASSAT?', "I'm fine. I'm FINE.", "Mum! MUM! They're startin'!"] },
  jeff: { name: 'JEFF', hp: 150, speed: 80, dmg: 13, reach: 80, windup: 0.6, score: 800, ai: 'melee', armor: true, kdAttack: true,
    lines: ['Outside. Now.', "You've spilt my pint.", "Dad said I'm allowed.", "Come 'ere."] },
  sue: { name: 'SUE', hp: 1, speed: 0, dmg: 0, reach: 0, windup: 1, score: 0, ai: 'melee', lines: ['OI!'] },
  mick: { name: 'MICK', hp: 420, speed: 84, dmg: 13, scale: 1.1, beatenWord: 'BARRED!', beatenLine: "...You're all barred. Same time next week?", sub: 'Landlord. Thirty years behind that bar.',
    intro: ["Right. Who's started it?", 'Not in my pub, son.'], lines: ['Get out of my pub!', "You're barred!", 'SUE! The bat!', "I've had bigger than you in 'ere."], tick: (b, dt, rage) => orpMick(b, dt, rage) },
});
['alan', 'jeff', 'sue', 'mick'].forEach(k => NO_EXTRA.add(k));
BOSS_CARD.jeff = ['JEFF', "Dad! They're starting!", ['jeff']];
BOSS_CARD.alan = ['ALAN', "Wassat? WASSAT?", ['alan']];

// ---------------------------------------------------------------- the places (FT per scene: tools/v73/scenes.py)
// waves run as usual inside a scene; an { event: 'exit' } opens the way to the next one (walk off that side of the screen)
const orpG = (...a) => a;
const ORP_SCENES = {
  orp_street: [
    { bg: 'busstop', ft: 380, fb: 506, label: 'THE BUS STOP', block: [[340, 362, 452], [384, 404, 458]],
      items: [{ w: 'cone', x: 640, y: 470 }], breakables: [{ type: 'bin', x: 520, y: 476, drop: 'chips' }],
      waves: [{ event: 'busstopHow' },
        { at: 0, groups: [orpG(['townie', 'R'], ['townie', 'L'], ['ladette', 'R']), orpG(['vibez', 'R'], ['townie', 'L'])] }, { event: 'lad' },
        { at: 0, groups: [orpG(['vibez', 'R'], ['ladette', 'L'], ['townie', 'R']), orpG(['bouncer', 'R'], ['townie', 'L'])], food: 'chips' }, { event: 'lad' },
        { at: 0, groups: [orpG(['chunk', 'R'], ['townie', 'L'], ['vibez', 'R']), orpG(['townie', 'R'], ['ladette', 'L'], ['vibez', 'L'], ['townie', 'R'])] }, { event: 'lad' },
        { event: 'ladsGo' }, { event: 'exit', dir: 1, to: 1, label: 'THE CROSSING' }] },
    { bg: 'cross', ft: 209, fb: 522, label: 'THE CROSSING', frog: true,
      waves: [{ event: 'frog' }, { event: 'exit', dir: 1, to: 2, label: 'RAM BA BA' }] },
    { bg: 'rambaba', ft: 380, fb: 506, label: 'RAM BA BA',
      items: [{ w: 'alcopop', x: 520, y: 470 }], breakables: [{ type: 'bin', x: 760, y: 480, drop: 'w:alcopop' }],
      waves: [{ event: 'rambaba' },
        { at: 0, groups: [orpG(['townie', 'R'], ['vibez', 'R'], ['ladette', 'L']), orpG(['townie', 'R'], ['vibez', 'L'])] },
        { at: 0, groups: [orpG(['chunk', 'R'], ['ladette', 'L'], ['vibez', 'R']), orpG(['townie', 'L'], ['townie', 'R'], ['vibez', 'R'])], food: 'chips' },
        { at: 0, mini: true, miniKind: 'chunk', title: 'THE PETTS WOOD MASSIVE', groups: [orpG(['chunk', 'R'], ['chunk', 'L']), orpG(['vibez', 'R'], ['ladette', 'L'], ['townie', 'R'])] },
        { event: 'exit', dir: 1, to: 3, label: 'YE OLDE BLACKSMITH' }] },
    { bg: 'front', ft: 380, fb: 506, label: 'YE OLDE BLACKSMITH', block: [[772, 792, 470]],
      items: [{ w: 'guinness', x: 300, y: 470 }], breakables: [{ type: 'keg', x: 640, y: 484, drop: 'chips' }],
      waves: [{ event: 'smokers' },
        { at: 0, groups: [orpG(['regular', 'R'], ['regular', 'L'], ['darts', 'R']), orpG(['regular', 'R'], ['townie', 'L'])] },
        { at: 0, final: true, groups: [orpG(['regular', 'R'], ['chunk', 'L'], ['regular', 'R'], ['darts', 'L']), orpG(['darts', 'R'], ['regular', 'L'], ['bouncer', 'R'])], food: 'chips' }] },
  ],
  orp_pub: [
    { bg: 'lounge', ft: 380, fb: 506, label: 'THE LOUNGE', block: [[140, 900, 404]],
      waves: [{ event: 'lounge' }, { event: 'exit', dir: 1, to: 1, label: 'THE BAR' }] },
    { bg: 'bar', ft: 380, fb: 506, label: 'THE BAR', sue: true, block: [[250, 772, 448]],
      waves: [{ event: 'served' }, { event: 'kickoff' },
        { at: 0, mini: true, miniKind: 'alan', title: 'ALAN', groups: [orpG(['alan', 'R'], ['regular', 'L'], ['regular', 'R']), orpG(['regular', 'R'], ['darts', 'L'])] },
        { at: 0, groups: [orpG(['regular', 'L'], ['regular', 'R'], ['darts', 'R']), orpG(['regular', 'L'], ['chunk', 'R'])], food: 'chips' },
        { event: 'exit', dir: 1, to: 2, label: 'THE POOL ROOM' }] },
    { bg: 'pool', ft: 380, fb: 506, label: 'THE POOL ROOM', block: [[380, 772, 436]], fruit: 860,
      items: [{ w: 'cue', x: 260, y: 470 }, { w: 'cue', x: 840, y: 480 }], breakables: [{ type: 'keg', x: 140, y: 484, drop: 'chips' }],
      waves: [{ at: 0, groups: [orpG(['darts', 'R'], ['regular', 'L'], ['darts', 'R']), orpG(['regular', 'R'], ['regular', 'L'])] },
        { at: 0, mini: true, miniKind: 'jeff', title: 'JEFF', groups: [orpG(['jeff', 'R'], ['regular', 'L']), orpG(['darts', 'R'], ['regular', 'R'], ['regular', 'L'])], food: 'chips' },
        { event: 'mickComing' }, { event: 'exit', dir: -1, to: 3, label: 'THE BAR' }] },
    { bg: 'bar', ft: 380, fb: 506, label: 'THE BAR', sue: true, block: [[250, 772, 448]], items: [{ w: 'cue', x: 160, y: 480 }],
      waves: [{ event: 'mickPage' }, { at: 0, boss: 'mick', title: 'MICK' }] },
  ],
  orp_atlantis: [
    { bg: 'queue', ft: 400, fb: 506, label: 'ATLANTIS',
      waves: [{ event: 'queue' }, { event: 'door' }] },
    { bg: 'floor', ft: 380, fb: 506, label: 'THE DANCE FLOOR', beat: true,
      waves: [{ event: 'dance' }, { event: 'lightsUp' },
        { at: 0, final: true, title: '2AM', groups: [orpG(['bouncer', 'R'], ['vibez', 'R'], ['clubm', 'L']), orpG(['bouncer', 'L'], ['chunk', 'R'], ['ladette', 'L'], ['clubf', 'R'])], food: 'chips' }] },
  ],
};
Object.assign(STAGES, {
  orp_street: { era: 2001, title: 'THE HIGH STREET', sub: 'Orpington. Saturday, March 2001. 8pm.', bg: 'orp_street', ft: 380, fb: 506, len: W,
    music: 'codered', aggro: 2, aa: 0.3, intro: 'orpIntro', waves: [] },
  orp_pub: { era: 2001, title: 'YE OLDE BLACKSMITH', sub: "8:40pm. Mick and Sue's.", bg: 'orp_pub', ft: 380, fb: 506, len: W,
    music: 'heist', aggro: 3, aa: 0.4, intro: 'orpPub', waves: [] },
  orp_atlantis: { era: 2001, title: 'ATLANTIS', sub: 'Croydon. 11pm. DJ EZ.', bg: 'orp_atlantis', ft: 400, fb: 506, len: W,
    music: 'alarmcall', aggro: 3, aa: 0.45, intro: 'orpClub', outro: 'orpHome', beat: 134, waves: [] },
});
// music: Code Red down the High Street, Heist in the Blacksmiths, Lockdown for Mick, Alarm Call at Atlantis
ORP_KEYS.forEach(k => { BOSS_MUSIC[k] = 'boss1999'; });
BOSS_MUSIC.orp_pub = 'lockdown'; BOSS_KEYS.add('lockdown');
// the chapter goes between 1999 and Elba; every stage on the route is numbered in order again
ROUTE.splice(ROUTE.indexOf('airport'), 0, ...ORP_KEYS);
ROUTE.forEach((k, i) => { STAGES[k].n = i + 1; });
const ORP_ART = ['busstop', 'cross', 'rambaba', 'front', 'lounge', 'bar', 'pool', 'queue', 'floor', 'bus'].map(k => 'orp/' + k);
ASSET_BG.push(...ORP_ART);
const ORP_CARS = ['fishery/car_beige', 'fishery/car_blue', 'fishery/car_red', 'road/mpv_d1', 'ramsden/moped', 'orp/bus'];

// ---------------------------------------------------------------- the group chats and the comic pages
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
    ['tim', "Sue's on the bar. Six pints. Nobody gets IDed."],
    ['byron', 'I look 25'],
    ['kelly', 'you look 12'],
    ['seb', 'Move when her back is turned. Freeze when it isn\'t.'],
    ['pearcy', "Alan's in. He's already wavey."],
  ],
  orpClub: [
    ['sys', 'Ram Ba Ba. 10:30pm. The Atlantis coach.'],
    ['tim', 'On the coach. Croydon. Nobody checks ID.'],
    ['kelly', 'the bouncer looked at me funny'],
    ['marc', 'DJ EZ, lads. DJ. EZ.'],
    ['seb', 'Stay together in the queue.'],
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
Object.assign(COMIC_PAGES, {
  p2001: { lay: 'L2', title: 'ORPINGTON', sub: 'MARCH 2001', panels: [
    { cap: 'Orpington High Street. Saturday night.' },
    { cap: '8pm. The Pizza Express bus stop.', say: [['byron', 'Will Sue serve me?', 0.3, 0.1], ['kelly', 'no', 0.78, 0.1]] } ] },
  pspill: { lay: 'L2', title: 'NINE O\'CLOCK', sub: 'YE OLDE BLACKSMITH', panels: [
    { cap: 'Six pints of Stella. Nobody got IDed.', say: [['sue', "Who's next?", 0.6, 0.1]] },
    { cap: 'Then Alan turned round.', say: [['jeff', 'ALAN!', 0.72, 0.1]] } ] },
  pmick: { lay: 'L1', title: 'LAST ORDERS', sub: 'MICK', panels: [
    { cap: "Thirty years behind that bar. He's seen your sort.", say: [['mick', "RIGHT. WHO STARTED IT?", 0.32, 0.08]] } ] },
  pdoor: { lay: 'L2', title: 'THE DOOR', sub: 'ATLANTIS, CROYDON', panels: [
    { cap: 'Ram Ba Ba wristbands. No ID checks. Nearly everyone got in.', say: [['bouncer', 'Not you, mate.', 0.66, 0.1]] },
    { cap: 'Kelly waited on the coach. Till 2am.', say: [['kelly', '...', 0.4, 0.12]] } ] },
  p2am: { lay: 'L1', title: '2AM', sub: 'CROYDON', panels: [
    { cap: 'DJ EZ. Everyone agreed. Nearly everyone.', say: [['marc', 'BEST. NIGHT. EVER.', 0.3, 0.1]] } ] },
});
COMIC_BEFORE.orpIntro = 'p2001';
COMIC_AFTER.orpHome = 'p2am';

// ================================================================== scenes
function orpScenes() { return S && ORP_SCENES[S.key]; }
function orpSc() { const L = orpScenes(); return L && L[S.sc || 0]; }
function orpGoScene(i, fromDir) {
  const L = orpScenes(), sc = L[i]; S.sc = i; S.scBg = sc.bg;
  FT = ST.ft = sc.ft; FB = ST.fb = sc.fb || 506;
  ST.waves = sc.waves; S.waveIdx = 0; S.wave = null; S.g = 0; S.exitReady = null; S.goT = 0; S.bosses = [];
  foes.length = 0; shots.length = 0; hazards.length = 0; items.length = 0; breakables.length = 0; S.npcs = [];
  for (const a of allies) a.remove = true; allies = allies.filter(a => !a.remove);
  (sc.items || []).forEach(it => dropItemWeapon(it.w, it.x, it.y));
  (sc.breakables || []).forEach(b => breakables.push({ ...b, hp: 3, flash: 0, half: 22 }));
  FLOOR_BLOCK[S.key] = sc.block || [];
  S.fruit = sc.fruit ? { x: sc.fruit, hits: 0, spin: 0, paid: false, flash: 0 } : null;
  S.frog = null; S.served = null; S.queue = null; S.dance = null; S.sue = null; S.howto = null; S.carry = 0;
  if (sc.sue) orpMakeSue();
  const dir = fromDir || 1;
  for (const p of players()) {
    p.x = dir > 0 ? 70 : W - 70; p.y = sc.frog ? FB - 10 : clamp(p.y, FT + 30, FB - 20); p.face = dir; p.vx = p.vy = 0; p.z = 0;
    if (p.state !== 'dead' && p.state !== 'walkin') setIdle(p);
  }
  cam.x = 0;
}
function orpExitOpen(w) { S.exitReady = { dir: w.dir || 1, to: w.to, label: w.label }; S.goT = 0; S.wave = null; S.waveIdx++; sfx('ready'); }
function orpWipe(to, dir, label) { if (S.wipe) return; S.wipe = { t: 0, to, dir, label, swapped: false }; sfx('swing'); }

// ---------------------------------------------------------------- per frame
function updateOrp(dt) {
  if (!S || !ST || ST.era !== 2001) return;
  if (!S.npcs) S.npcs = [];
  if (S.sc == null) orpGoScene(0);
  updateNpcs(dt);
  if (S.ann) { S.ann.t += dt; if (S.ann.t > S.ann.life) S.ann = null; }
  if (S.wipe) {
    const w = S.wipe; w.t += dt;
    for (const p of players()) { p.vx = p.vy = 0; }
    if (!w.swapped && w.t >= 0.4) { w.swapped = true; orpGoScene(w.to, w.dir); }
    if (w.t >= 1.1) S.wipe = null;
    return;
  }
  if (S.howto) { orpHowtoTick(dt); return; }
  if (S.exitReady) {
    const e = S.exitReady, p = player;
    if ((e.dir > 0 && p.x > W - 44) || (e.dir < 0 && p.x < 44)) orpWipe(e.to, e.dir, e.label);
  }
  if (S.lads) orpLadsTick(dt);
  if (S.frog) orpFrogTick(dt);
  if (S.served) orpServedTick(dt);
  if (S.sue) orpSueTick(dt);
  if (S.queue) orpQueueTick(dt);
  if (S.dance) orpDanceTick(dt);
}
function orpAnnounce(text, life) { S.ann = { text, t: 0, life: life || 3.2 }; sfx('page'); }
function orpComic(id, then) {   // a comic page in the middle of a stage, then straight back to the fight
  comicShow(id, () => { mode = 'play'; modeT = 0; if (then) then(); });
}
// how-to cards: the game waits until you've read it (HIT, JUMP or a tap; it goes by itself after 12 seconds)
function orpHowto(title, lines, then) { S.howto = { title, lines, then, t: 0 }; sfx('page'); }
function orpHowtoTick(dt) {
  const h = S.howto; h.t += dt;
  for (const p of players()) { p.vx = p.vy = 0; p.atk = null; if (p.state === 'walk' || p.state === 'run') setIdle(p); }
  const go = h.t > 0.6 && (pressed.has('punch') || pressed.has('jump') || pressed.has('start') || taps.length);
  if (go || h.t > 12) { S.howto = null; sfx('ready'); if (h.then) h.then(); }
}
function orpEvent(ev) {
  if (!ST || ST.era !== 2001) return false;
  const w = S.wave, next = () => { S.wave = null; S.waveIdx++; };
  switch (ev) {
    case 'exit': orpExitOpen(w); return true;
    case 'busstopHow': orpHowto('HOLD THE BUS STOP', ['The Petts Wood lot want the bus stop.', "The lads are on their way: each time you clear a wave, one more turns up and fights with you."], next); return true;
    case 'lad': orpLadArrives(); next(); return true;
    case 'ladsGo': orpLadsGo(); next(); return true;
    case 'frog': orpFrogStart(); return true;
    case 'rambaba': orpRamBaBa(); next(); return true;
    case 'smokers': say(player, pick(['Smokers. Course there are.', "One pint. Then Ram Ba Ba."]), 2, true); orpAnnounce('THE SMOKERS OUTSIDE THE BLACKSMITHS'); next(); return true;
    case 'lounge': orpLounge(); next(); return true;
    case 'served': orpServedStart(); return true;
    case 'kickoff': orpComic('pspill', () => { orpAnnounce("ALAN'S SPILT JEFF'S PINT"); if (S.sue) S.sueOiT = 6; next(); }); return true;
    case 'mickComing': say(player, 'Is that... a bell?', 2, true); popWord(W - 60, FT + 20, 200, 'DING DING DING!', true); sfx('clink'); orpAnnounce('MICK WANTS A WORD · BACK TO THE BAR'); next(); return true;
    case 'mickPage': orpComic('pmick', next); return true;
    case 'queue': orpQueueStart(); return true;
    case 'door': orpDoor(); return true;
    case 'dance': orpDanceStart(); return true;
    case 'lightsUp': orpLightsUp(); return true;
  }
  return false;
}

// ================================================================== the bus stop: the lads turn up one at a time
function orpLadQueue() {
  if (!S.ladQ) { const others = ORP_LADS.filter(id => id !== player.def.id && id !== 'sam'); for (let i = others.length - 1; i > 0; i--) { const j = (Math.random() * (i + 1)) | 0; [others[i], others[j]] = [others[j], others[i]]; } S.ladQ = others.slice(0, 2).concat(player.def.id === 'sam' ? others.slice(2, 3) : ['sam']); }
  return S.ladQ;
}
const ORP_ARRIVE = { sam: ['Sorry lads. Bus was late.', 'What did I miss?'], byron: ['8pm means 7:55. I was early. I went round the block.'], kelly: ['Who are this lot?'],
  pearcy: ['Wearing my good shirt. Mind the shirt.'], seb: ['Right. Formation.'], marc: ['DJ EZ, lads! Oh. Hello.'], tim: ["I've done a plan."] };
function orpLadArrives() {
  const q = orpLadQueue(), id = q.shift(); if (!id) return; const c = CHAR_BY_ID[id]; if (!c) return;
  const side = chance(0.5) ? -1 : 1;
  const a = { kind: 'ally', ally: true, friend: true, def: c, look: lookFor(c, ST.era), x: side < 0 ? -50 : W + 50, y: rand(FT + 30, FB - 20), z: 0, vx: 0, vy: 0, vz: 0, face: -side, state: 'walk', t: 0, life: 9999,
    combo: 0, comboT: 0, atk: null, atkT: 0, flash: 0, walk: 0, half: 20, scale: 1, inv: 99, landed: false, cool: 0.6, sayCool: 0 };
  allies.push(a); popWord(W / 2, FT + 40, 200, c.name + ' IS HERE!', true); sfx('start');
  setTimeout0(() => say(a, pick(ORP_ARRIVE[id] || ['Alright?']), 2.4, true), 0.6);
}
function orpLadsGo() {   // the lads head on ahead to the Blacksmiths
  for (const a of allies) { a.life = 0; }
  if (allies[0]) say(allies[0], 'See you at the Blacksmiths. Get the first round in.', 2.6, true);
}
function orpLadsTick() {}

// ================================================================== the crossing: a proper Frogger
// Four lanes of traffic between you and the far pavement. Three crossings: over to Ram Ba Ba, back for Sam's phone, over
// again with the 61 bus in the mix. A hit knocks you down and sends you back to the kerb you started from.
const ORP_LANES = [292, 346, 400, 454];
function orpFrogStart() {
  orpHowto('THE CROSSING', ['Get across the High Street to Ram Ba Ba. Nobody stops for the zebra in Orpington.',
    'Move up and down to cross the lanes. A car sends you back to the kerb. Mopeds can be jumped; buses can\'t.'], () => orpFrogRound(1));
}
function orpFrogRound(n) {
  const up = n % 2 === 1;
  S.frog = { round: n, goal: up ? 'top' : 'bottom', hits: 0, t: 0, reset: 0, lanes: ORP_LANES.map((y, i) => ({ y, dir: i < 2 ? -1 : 1, next: rand(0, 1.2) })) };
  for (const p of players()) { p.y = up ? FB - 10 : FT + 30; p.x = 240; p.face = 1; setIdle(p); }
  const what = ['', 'GET TO RAM BA BA', "SAM'S LEFT HIS PHONE AT THE BUS STOP · GO BACK", 'OVER AGAIN · HERE COMES THE 61'][n];
  showBanner('CROSSING ' + n + ' OF 3', what, 2.2);
  if (n === 2) say(player, pick(["SAM.", "Course he has."]), 2, true);
}
function orpFrogTick(dt) {
  const F = S.frog, p = player; F.t += dt;
  const sp = [0, 1, 1.25, 1.5][F.round] * (1 + 0.15 * (D().aggro || 0));
  for (const L of F.lanes) {
    L.next -= dt;
    if (L.next <= 0) {
      const busOut = S.npcs.some(c => c.orpCar === 'orp/bus' && c.x > -300 && c.x < W + 300);
      const big = F.round === 3 && !busOut && chance(0.3), kind = big ? 'orp/bus' : chance(F.round > 1 ? 0.22 : 0) ? 'ramsden/moped' : pick(ORP_CARS.slice(0, 4));
      const v = (kind === 'orp/bus' ? 150 : kind === 'ramsden/moped' ? 320 : rand(190, 270)) * sp;
      const img = bgImg(kind), w = img ? img.width * 2 : 200;
      const car = makeNpc('car', L.dir > 0 ? -w / 2 - 20 : W + w / 2 + 20, L.y); car.orpCar = kind; car.w = w; car.h = img ? img.height * 2 : 96; car.vxC = L.dir * v; car.face = L.dir; car.hp = 0;
      car.draw = orpDrawCar; car.script = (n, dt2) => { n.x += n.vxC * dt2; if (n.x < -400 || n.x > W + 400) n.remove = true; };
      S.npcs.push(car); if (kind === 'orp/bus') { sfx('engine'); popWord(L.dir > 0 ? 80 : W - 80, L.y, 150, 'BUS!', false); } else if (kind === 'ramsden/moped') sfx('brrap');
      L.next = (w + rand(160, 420)) / v + rand(0.2, 0.9) / sp;
    }
  }
  if (F.reset > 0) { F.reset -= dt; if (F.reset <= 0) { const up = F.goal === 'top'; for (const q of players()) { q.y = up ? FB - 10 : FT + 30; q.x = 240; setIdle(q); q.inv = 1.2; } popWord(240, FB - 10, 160, 'BACK TO THE KERB', false); } return; }
  // hit by something
  if (canBeHit(p) && !(p.inv > 0) && p.state !== 'down' && p.state !== 'getup') {
    for (const c of S.npcs) {
      if (!c.orpCar || Math.abs(p.y - c.y) > 18 || Math.abs(p.x - c.x) > c.w / 2 + 4) continue;
      if (c.orpCar === 'ramsden/moped' && p.z > 26) continue;   // jumped it
      hitP(c, 6, Math.sign(c.vxC), true, 360); sfx('heavy'); popWord(p.x, p.y, 170, pick(['BEEEEP!', 'OI! LOOK WHERE YOU\'RE GOING!', 'HONK!', 'WATCH IT!']), true);
      F.hits++; F.reset = 1.4; addScore(-150, true); break;
    }
  }
  // made it
  const there = F.goal === 'top' ? p.y < FT + 46 : p.y > FB - 16;
  if (there && p.state !== 'down') {
    const bonus = Math.max(300, 2000 - F.hits * 400 - Math.round(F.t) * 20);
    popWord(p.x, p.y, 180, F.hits === 0 ? 'NOT A SCRATCH!' : 'MADE IT!', true); addScore(bonus); sfx('jackpot');
    if (F.round === 2) say(p, "Got it. It was in the bin.", 2, true);
    if (F.round < 3) { const n = F.round + 1; S.frog = null; setTimeout0(() => { if (S && S.key === 'orp_street' && S.sc === 1) orpFrogRound(n); }, 1.6); }
    else { S.frog = null; for (const c of S.npcs) if (c.orpCar) c.vxC *= 1.6; setTimeout0(() => { if (S && S.npcs) S.npcs = S.npcs.filter(n => !n.orpCar); }, 3); S.wave = null; S.waveIdx++; }
  }
}
function orpDrawCar(n) {
  const img = bgImg(n.orpCar); if (!img) return;
  const w = img.width * 2, h = img.height * 2, x = Math.round((n.x - cam.x - w / 2) / 2) * 2, y = Math.round((n.y + 6 - h) / 2) * 2;
  ctx.save(); ctx.imageSmoothingEnabled = false;
  ctx.fillStyle = 'rgba(0,0,0,0.3)'; ctx.fillRect(x + 10, n.y + 2, w - 20, 8);
  if (n.vxC < 0) { ctx.translate(x + w, y); ctx.scale(-1, 1); ctx.drawImage(img, 0, 0, w, h); } else ctx.drawImage(img, x, y, w, h);
  ctx.restore();
  // headlights
  ctx.fillStyle = 'rgba(255,240,170,0.18)'; const hx = n.vxC > 0 ? x + w : x - 90; ctx.fillRect(hx, n.y - 26, 90, 18);
}

// ================================================================== Ram Ba Ba and the Blacksmiths' front
function orpRamBaBa() {
  const d = makeNpc('bouncer', 268, FT + 16); d.face = 1; d.state = 'idle'; d.hp = 0; S.npcs.push(d);
  orpAnnounce('RAM BA BA · ATLANTIS COACH 10.30 · WRISTBANDS AT THE DOOR', 4);
  setTimeout0(() => say(d, 'Coach at half ten, lads. Wristbands on. No wristband, no coach.', 2.8, true), 0.6);
  setTimeout0(() => say(player, 'Petts Wood lot are following us.', 2, true), 3.4);
}
function orpLounge() {
  orpAnnounce('THE BLACKSMITHS · THE LADS ARE AT A TABLE BY THE BAR', 3.4);
  const alan = makeNpc('alan', 620, FT + 70); alan.face = -1; alan.hp = 0; S.npcs.push(alan);
  alan.script = (n, dt) => { n.t2 = (n.t2 || 0) + dt; n.state = 'idle'; n.z = 0; n.x += Math.sin(n.t2 * 1.7) * 12 * dt; if (n.t2 > 0.8 && !n.said) { n.said = 1; say(n, "Wassat? Who are you lot?", 2.4, true); } };
}

// ================================================================== the Blacksmiths: getting served
// The lads are at the table by the fruit machine. Get to the bar, order two pints, carry them back: three trips for six.
// Sue pours with her back to the room, then turns round and watches. Moving where she can see you fills your ID meter; stood
// still you're just another punter, and behind the fruit machine or the post she can't see you at all. Full meter: thrown
// out to the door. Carrying pints: walk, don't run (or fight), and keep out of Alan's way, or you'll spill them.
const ORP_BAR = { x0: 300, x1: 730, sueX: 520, top: 297, order: [420, 640] };
const ORP_HIDE = [[0, 150], [228, 272]];
const ORP_TABLE = [40, 210];
function orpHidden(p) { return p.y < FT + 74 && ORP_HIDE.some(([a, b]) => p.x > a && p.x < b); }
function orpMakeSue() {
  S.tableLads = [];
  const sue = makeNpc('sue', ORP_BAR.sueX, 336); sue.face = 1; sue.state = 'idle'; sue.draw = orpDrawSue; sue.hp = 0; S.npcs.push(sue); S.sue = sue; S.sueOiT = 99;
  // two of the lads at their table
  const q = ORP_LADS.filter(id => id !== player.def.id); const two = ['byron', 'pearcy'].filter(id => q.includes(id)); while (two.length < 2) two.push(q.find(id => !two.includes(id)));
  two.forEach((id, i) => { const c = CHAR_BY_ID[id], n = makeNpc('lad_' + id, 70 + i * 70, FT + 26 + i * 8, lookFor(c, ST.era)); n.def = c; n.face = 1; n.state = 'idle'; n.hp = 0; S.npcs.push(n); S.tableLads.push(n); });
}
function orpServedStart() {
  orpHowto('GET THE ROUND IN', ['Six pints. Sue mustn\'t clock how young you are.',
    'When she turns round (!), FREEZE, or get behind the fruit machine or the post. Moving while she\'s WATCHING fills your ID meter.',
    'Get to the ORDER spot at the bar, then carry the pints back to the lads\' table: walk, don\'t run, and dodge Alan. Three trips.'], () => {
    S.served = { phase: 'go', pints: 0, id: 0, strikes: 0, watch: false, warn: 0, t: rand(2.4, 3.2), pourT: 0 };
    const alan = makeNpc('alan', 600, FT + 90); alan.face = -1; alan.hp = 0; alan.tx = 300; alan.ty = FT + 90; S.npcs.push(alan); S.alanNpc = alan;
    alan.script = (n, dt) => { if (!S.served) return; if (Math.hypot(n.x - n.tx, n.y - n.ty) < 10) { n.tx = rand(230, 760); n.ty = rand(FT + 76, FB - 14); if (chance(0.3)) say(n, pick(['Wassat?', "I'm FINE.", 'Mum! MUM!', 'Who moved the floor?']), 1.6); }
      npcWalkTo(n, n.tx, n.ty, 46 + (S.served.pints >= 4 ? 30 : 0), dt); };
  });
}
function orpServedTick(dt) {
  const sv = S.served, sue = S.sue, p = player; if (!sue) return;
  const byron = p.def.id === 'byron';
  // Sue: pour (back turned), then a "!" and she turns round, then she watches
  sv.t -= dt;
  if (sv.warn > 0) { sv.warn -= dt; if (sv.warn <= 0) { sv.watch = true; sue.face = -1; sv.t = rand(1.8, 2.8) + sv.pints * 0.15; } }
  else if (sv.t <= 0) {
    if (sv.watch) { sv.watch = false; sue.face = 1; sv.t = rand(2.2, 3.4) - sv.pints * 0.2; if (chance(0.5)) say(sue, pick(['Pint of Stella, love?', 'Mick! Change the barrel!', "Who's next?", 'Ice? We\'ve got no ice.']), 1.6, true); }
    else { sv.warn = 0.75; sv.t = 9; popWord(sue.x, sue.y, 200, '!', true); sfx('nope'); }
  }
  // the ID meter
  const moving = Math.hypot(p.vx || 0, p.vy || 0) > 25 || p.atk;
  if (sv.watch && moving && !orpHidden(p) && !(p.x < ORP_TABLE[1] && sv.phase === 'go')) {
    sv.id = Math.min(1, sv.id + dt * (byron ? 1.1 : 0.62));
    if (!sv.saidLook) { sv.saidLook = true; say(sue, pick(['Oi. How old are you?', 'You. Yes, YOU.', "I know your mum."]), 1.8, true); }
    if (sv.id >= 1) { orpCaught(); return; }
  } else { sv.id = Math.max(0, sv.id - dt * 0.12); if (!sv.watch) sv.saidLook = false; }
  // ordering
  if (sv.phase === 'go' && p.x > ORP_BAR.order[0] && p.x < ORP_BAR.order[1] && p.y < 482 && canBeHit(p)) {
    sv.phase = 'pour'; sv.pourT = 1.6; say(sue, pick(['Two Stella? Go on then.', 'Two pints. Anything else, love?', "That's four-forty."]), 1.8, true); sfx('clink');
  }
  if (sv.phase === 'pour') {
    p.vx = p.vy = 0; sv.pourT -= dt;
    if (sv.pourT <= 0) { sv.phase = 'carry'; S.carry = 2; popWord(p.x, p.y, 190, '+2 PINTS', true); sfx('pickup'); orpAnnounce('CARRY THEM BACK TO THE TABLE · WALK, DON\'T RUN', 2.6); }
  }
  if (sv.phase === 'carry') {
    const alan = S.alanNpc;
    if (p.running || p.atk || p.state === 'jump' || (alan && Math.hypot(alan.x - p.x, (alan.y - p.y) * 2) < 40)) { orpSpill(alan && Math.hypot(alan.x - p.x, (alan.y - p.y) * 2) < 40); return; }
    if (p.x < ORP_TABLE[1] - 20) {
      sv.pints += 2; S.carry = 0; sv.phase = 'go'; addScore(800); sfx('jackpot'); popWord(p.x, p.y, 190, sv.pints + ' OF 6', true);
      if (S.tableLads && S.tableLads[0]) say(S.tableLads[sv.pints === 6 ? 1 : 0], pick(['Get in.', 'Legend.', 'Cheers, mate.', "Didn't even look at you."]), 1.8, true);
      if (sv.pints >= 6) orpServedEnd(true);
    }
  }
}
function orpSpill(alan) {
  const sv = S.served; S.carry = 0; sv.phase = 'go'; sfx('splash'); droplets(player.x, player.y, 14);
  popWord(player.x, player.y, 190, 'SPILT!', true);
  if (alan && S.alanNpc) say(S.alanNpc, 'Oi! Watch it! That\'s... that\'s your pint.', 2, true);
  else say(player, pick(['Walk. WALK.', 'Two pints, gone.', "That's four-forty on the carpet."]), 1.8, true);
}
function orpCaught() {
  const sv = S.served; sv.strikes++; sv.id = 0; S.carry = 0; sv.phase = 'go'; sv.watch = false; S.sue.face = 1; sv.t = rand(2.6, 3.4);
  sfx('nope'); popWord(player.x, player.y, 180, 'IDED!', true);
  say(S.sue, sv.strikes >= 3 ? "MICK! THIS ONE'S TWELVE!" : pick(['Out. Come back with ID.', "Nice try. Door's that way.", "I know your mum, Byron."]), 2.2, true);
  if (sv.strikes >= 3) { orpServedEnd(false); return; }
  for (const p of players()) { p.x = 50; p.y = clamp(p.y, FT + 30, FB - 20); p.vx = p.vy = 0; setIdle(p); p.inv = 1; }
}
function orpServedEnd(ok) {
  S.served = null; S.carry = 0; if (S.sue) S.sue.face = -1;
  if (S.alanNpc) S.alanNpc.remove = true;
  for (const n of (S.tableLads || [])) n.remove = true; S.tableLads = null;
  if (ok) { popWord(player.x, player.y, 200, 'ROUND\'S IN!', true); addScore(3000); for (const p of players()) { p.hp = p.maxHp; p.meter = 100; } showBanner("THE ROUND'S IN", 'Full health. Special ready.', 2); }
  else showBanner('IDED THREE TIMES', 'It kicks off anyway', 2);
  S.wave = null; S.waveIdx++;
}

// Sue in the fight: "OI!" from behind the bar every few seconds: ears ringing for anyone on the floor (jump it)
function orpSueTick(dt) {
  const sue = S.sue; if (S.served || !S.wave || S.wave.event || S.done) return;
  S.sueOiT = (S.sueOiT == null || S.sueOiT > 50 ? 6 : S.sueOiT) - dt;
  if (sue.state === 'oiWind') { if (sue.t > 0.75) { sue.state = 'oi'; sue.t = 0; orpOi(sue); } return; }
  if (sue.state === 'oi') { if (sue.t > 0.6) { sue.state = 'idle'; sue.t = 0; } return; }
  if (S.sueOiT <= 0) { S.sueOiT = rand(6, 9) * (S.bosses && S.bosses.length ? 0.8 : 1.3); sue.state = 'oiWind'; sue.t = 0; sue.face = -1; popWord(sue.x, sue.y, 200, '! JUMP !', true); }
}
function orpOi(sue) {
  popWord(sue.x, sue.y, 220, 'OI!', true); sfx('airhorn'); addShake(4);
  for (const p of players()) {
    if (!canBeHit(p) || p.z > 20 || p.state === 'down' || p.state === 'getup') continue;
    p.state = 'hurt'; p.t = -0.6; p.vx = p.vy = 0; p.atk = null; p.running = false; popWord(p.x, p.y, 160, 'EARS RINGING!', false);
  }
}
// Sue is behind the bar: only her top half shows over the counter; while you're getting served, a tag over her head
function orpDrawSue(n) {
  ctx.save(); ctx.beginPath(); ctx.rect(0, 0, W, ORP_BAR.top); ctx.clip(); drawEntity(n); ctx.restore();
  const sv = S.served; if (!sv) return;
  const x = Math.round((n.x - cam.x) / 2) * 2, y = 150;
  const tag = sv.watch ? ['WATCHING', '#ff4d4d'] : sv.warn > 0 ? ['TURNING!', '#ffd24d'] : ['POURING', '#bfe6a8'];
  ctx.fillStyle = 'rgba(5,6,14,0.78)'; ctx.fillRect(x - 64, y - 13, 128, 26); pxText(tag[0], x, y, 12, tag[1]);
}
// the stealth layer: her gaze across the floor, the hiding places, the order spot, the table, your ID meter, the pints
function orpDrawServed() {
  const sv = S.served; if (!sv) return;
  ctx.save();
  if (sv.watch || sv.warn > 0) {   // her line of sight: the whole floor in front of the bar
    ctx.globalAlpha = sv.watch ? 0.16 + 0.04 * Math.sin(time * 8) : 0.08; ctx.fillStyle = '#ff3030';
    ctx.beginPath(); ctx.moveTo(ORP_BAR.sueX - 10, 260); ctx.lineTo(0, FT); ctx.lineTo(0, H); ctx.lineTo(W, H); ctx.lineTo(W, FT); ctx.closePath(); ctx.fill();
  }
  ctx.globalAlpha = 1;
  for (const [a, b] of ORP_HIDE) { ctx.fillStyle = 'rgba(80,255,140,' + (sv.watch ? 0.32 : 0.16) + ')'; ctx.fillRect(a, FT + 4, b - a, 68); pxText('HIDE', (a + b) / 2, FT + 84, 10, '#7dffb0'); }
  const [o0, o1] = ORP_BAR.order;
  if (sv.phase === 'go') { ctx.fillStyle = 'rgba(255,214,90,' + (0.25 + 0.15 * Math.sin(time * 5)) + ')'; ctx.fillRect(o0, 450, o1 - o0, 28); pxText('ORDER HERE', (o0 + o1) / 2, 464, 12, '#ffe08a'); }
  if (sv.phase === 'carry') { ctx.fillStyle = 'rgba(120,200,255,' + (0.25 + 0.15 * Math.sin(time * 5)) + ')'; ctx.fillRect(ORP_TABLE[0], FT + 6, ORP_TABLE[1] - ORP_TABLE[0], 70); pxText('THE LADS', (ORP_TABLE[0] + ORP_TABLE[1]) / 2, FT + 90, 12, '#a8dcff'); }
  // the ID meter over your head, the pints count at the top
  const p = player, px = Math.round(p.x - cam.x), py = Math.round(p.y - 190);
  if (sv.id > 0.01) { ctx.fillStyle = 'rgba(0,0,0,0.7)'; ctx.fillRect(px - 32, py, 64, 10); ctx.fillStyle = sv.id > 0.66 ? '#ff4040' : '#ffc040'; ctx.fillRect(px - 30, py + 2, 60 * sv.id, 6); pxText('ID?', px, py - 9, 10, '#ffffff'); }
  if (S.carry) for (let i = 0; i < 2; i++) { const gx = px + p.face * (18 + i * 12), gy = Math.round(p.y - 104 - p.z); ctx.fillStyle = '#e8a93a'; ctx.fillRect(gx - 4, gy, 9, 16); ctx.fillStyle = '#fff6e0'; ctx.fillRect(gx - 4, gy - 3, 9, 4); }
  ctx.fillStyle = 'rgba(8,10,24,0.82)'; ctx.fillRect(W / 2 - 150, H - 62, 300, 30); pxText('PINTS ' + sv.pints + ' OF 6   ·   IDED ' + sv.strikes + ' OF 3', W / 2, H - 47, 12, '#ffe08a');
  ctx.restore();
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
      if (b.hp < b.maxHp * 0.7 && !b.rang1) { b.rang1 = true; b.state = 'bellWind'; b.t = 0; b.vx = b.vy = 0; say(b, 'SUE! Get the regulars!', 1.8, true); return true; }
      if (dy < 30 && dx > 170 && dx < 560 && chance(0.55)) { b.state = 'bellyWind'; b.t = 0; b.vx = b.vy = 0; faceP(); say(b, pick(["Come 'ere!", 'Mind the belly!']), 1.2, true); return true; }
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

// ================================================================== Atlantis: the queue
// The queue runs along the wall from the door. Every few seconds the bouncers let the front one in and everyone shuffles
// up, but only while it's calm: queue-jumpers push in, and nothing moves until you've sorted them out.
const ORP_DOOR_X = 760;
function orpQueueStart() {
  orpHowto('THE QUEUE', ['It goes right down the road. Ram Ba Ba wristbands on, nobody checks ID.',
    'Every few seconds the bouncers let one more in, but only when it\'s calm. Queue-jumpers push in: sort them out and the queue moves again.'], () => {
    const n = 12;
    S.queue = { ahead: n, t: 3.2, jumpT: 4, jumpers: 0, waves: 0 };
    const kinds = ['clubm', 'clubf', 'vibez', 'ladette', 'townie'];
    S.qNpcs = [];
    for (let i = 0; i < 9; i++) { const k = kinds[i % kinds.length], q = makeNpc(k, ORP_DOOR_X - 60 - i * 58, FT + 22 + (i % 2) * 6); q.face = 1; q.state = 'idle'; q.hp = 0; q.slot = i; S.npcs.push(q); S.qNpcs.push(q); }
    const bz = [makeNpc('bouncer', ORP_DOOR_X + 20, FT + 14), makeNpc('bouncer', ORP_DOOR_X + 90, FT + 30)]; bz.forEach(b => { b.face = -1; b.state = 'idle'; b.hp = 0; S.npcs.push(b); }); S.qBouncers = bz;
    // the lads in the queue with you
    const mates = ['kelly', 'marc'].filter(id => id !== player.def.id).concat(player.def.id === 'kelly' || player.def.id === 'marc' ? ['seb'] : []);
    S.qMates = mates.map((id, i) => { const c = CHAR_BY_ID[id], m = makeNpc('lad_' + id, 120 + i * 60, FT + 50 + i * 20, lookFor(c, ST.era)); m.def = c; m.face = 1; m.state = 'idle'; m.hp = 0; S.npcs.push(m); return m; });
    for (const p of players()) { p.x = 240; p.y = FT + 60; }
  });
}
function orpQueueTick(dt) {
  const Q = S.queue;
  const alive = foes.filter(f => f.state !== 'dead' && !f.remove && f.state !== 'beaten').length;
  // queue-jumpers: groups that walk in from the door end and push in
  Q.jumpT -= dt;
  if (Q.jumpT <= 0 && alive === 0 && Q.ahead > 1) {
    Q.waves++; Q.jumpT = rand(7, 10);
    const grp = [orpG(['vibez', 'R'], ['townie', 'R']), orpG(['clubm', 'R'], ['ladette', 'R'], ['townie', 'L']), orpG(['chunk', 'R'], ['vibez', 'R'], ['clubf', 'L']), orpG(['clubm', 'R'], ['clubm', 'R'], ['vibez', 'L'], ['ladette', 'R'])][Math.min(3, Q.waves - 1)];
    const out = spawnGroup(grp); Q.ahead += out.length; popWord(ORP_DOOR_X - 100, FT + 30, 190, 'PUSHING IN!', true); sfx('incoming');
    for (const f of out) if (f.def.lines && chance(0.5)) f.sayIn = rand(0.2, 1);
    setTimeout0(() => { if (S.qMates && S.qMates[0]) say(S.qMates[0], pick(['Oi! There\'s a queue!', 'They just pushed in!', 'Back of the queue, mate!']), 2, true); }, 0.8);
  }
  // the queue moves while it's calm
  if (alive === 0) {
    Q.t -= dt;
    if (Q.t <= 0 && Q.ahead > 0) {
      Q.ahead--; Q.t = 2.6; sfx('clink');
      const front = S.qNpcs.shift(); if (front) { front.script = (n, dt2) => { npcWalkTo(n, ORP_DOOR_X + 60, FT + 6, 120, dt2); if (n.x > ORP_DOOR_X + 40) n.remove = true; }; }
      for (const n of S.qNpcs) { n.slot--; const tx = ORP_DOOR_X - 60 - n.slot * 58; n.script = (m, dt2) => { if (Math.abs(m.x - tx) > 3) npcWalkTo(m, tx, m.y, 90, dt2); else { m.state = 'idle'; m.face = 1; } }; }
      if (Q.ahead > 0 && S.qNpcs.length < Math.min(9, Q.ahead)) { const k = pick(['clubm', 'clubf', 'vibez', 'ladette']), q = makeNpc(k, -40, FT + 22); q.face = 1; q.slot = S.qNpcs.length; q.hp = 0; S.npcs.push(q); S.qNpcs.push(q); const tx = ORP_DOOR_X - 60 - q.slot * 58; q.script = (m, dt2) => { if (Math.abs(m.x - tx) > 3) npcWalkTo(m, tx, m.y, 90, dt2); else { m.state = 'idle'; m.face = 1; } }; }
    }
  }
  if (Q.ahead <= 0 && alive === 0) { S.queue = null; S.wave = null; S.waveIdx++; orpAnnounce("YOU'RE AT THE FRONT", 2); }
}
function orpDrawQueue() {
  const Q = S.queue; if (!Q) return;
  ctx.fillStyle = 'rgba(8,10,24,0.82)'; ctx.fillRect(W / 2 - 170, H - 62, 340, 30);
  const calm = !foes.some(f => f.state !== 'dead' && !f.remove && f.state !== 'beaten');
  pxText((Q.ahead > 0 ? Q.ahead + ' AHEAD OF YOU' : 'NEXT IN') + (calm ? '   ·   QUEUE MOVING' : '   ·   QUEUE STOPPED'), W / 2, H - 47, 12, calm ? '#9fe8ff' : '#ff8a8a');
}
// at the door: everyone in except Kelly (if you're playing as Kelly, he talks his way in through the fire exit at one)
function orpDoor() {
  const bz = S.qBouncers || [], kel = (S.qMates || []).find(m => m.def.id === 'kelly');
  const d1 = bz[0] || makeNpc('bouncer', ORP_DOOR_X, FT + 14);
  for (const p of players()) { p.vx = p.vy = 0; }
  say(d1, 'Wristbands. In you go. Not him.', 2.4, true);
  setTimeout0(() => { if (kel) say(kel, "But I'm WITH them!", 2, true); else say(player, "But I'm WITH them!", 2, true); }, 1.6);
  setTimeout0(() => orpComic('pdoor', () => {
    if (player.def.id === 'kelly') showBanner('1AM', 'Kelly talked his way in through the fire exit', 2.6);
    orpWipe(1, 1, 'INSIDE ATLANTIS'); S.wave = null; S.waveIdx++;
  }), 3.4);
}

// ================================================================== Atlantis: the dance floor
// The floor is full of dancers on the beat. A few at a time stop dancing (a "!" over their heads) and come for you;
// the rest carry on. Hits on the beat do more (the BEAT ring at the bottom follows Alarm Call itself).
const ORP_DANCE = ['clubm', 'clubf', 'vibez', 'ladette', 'townie', 'clubm', 'clubf'];
function orpDanceStart() {
  orpHowto('THE DANCE FLOOR', ['DJ EZ is on. The floor is packed, and some of them want trouble.',
    'Watch for a dancer who stops and points (!): that one\'s coming for you. Hit on the beat (the ring at the bottom) for more damage.'], () => {
    S.dance = { wave: 0, sizes: [2, 3, 3, 4, 5], t: 2.5 };
    S.dancers = [];
    for (let i = 0; i < 14; i++) orpAddDancer(rand(60, W - 60), rand(FT + 12, FB - 10));
  });
}
function orpAddDancer(x, y) {
  const n = makeNpc(pick(ORP_DANCE), x, y); n.hp = 0; n.dancer = true; n.ph = Math.random() * 2; n.face = chance(0.5) ? 1 : -1;
  n.script = (m) => { const ph = orpBeatPhase(); const b = ph < 0 ? (time * 2.2 + m.ph) % 1 : (ph + m.ph) % 1; m.z = Math.round(Math.abs(Math.sin(b * Math.PI)) * 8); m.state = 'idle'; if (b < 0.04 && chance(0.3)) m.face = -m.face; };
  S.npcs.push(n); S.dancers.push(n); return n;
}
function orpDanceTick(dt) {
  const D_ = S.dance, alive = foes.filter(f => f.state !== 'dead' && !f.remove && f.state !== 'beaten').length;
  S.dancers = S.dancers.filter(n => !n.remove);
  if (alive > 0) return;
  D_.t -= dt;
  if (D_.t > 0) return;
  if (D_.wave >= D_.sizes.length) { S.dance = null; S.wave = null; S.waveIdx++; return; }
  // the next lot stop dancing: a "!" first, then they come for you
  const k = D_.sizes[D_.wave++], pickN = S.dancers.slice().sort(() => Math.random() - 0.5).slice(0, k);
  for (const n of pickN) { n.script = null; n.z = 0; n.face = Math.sign(player.x - n.x) || 1; popWord(n.x, n.y, 160, '!', true); }
  sfx('incoming'); D_.t = 2.4;
  if (D_.wave === 3) orpAnnounce('THE FLOOR TURNS NASTY', 2);
  setTimeout0(() => {
    for (const n of pickN) { if (n.remove) continue; n.remove = true; const f = makeFoe(n.kind, n.x, n.y); f.face = Math.sign(player.x - n.x) || 1; f.state = 'hover'; foes.push(f); if (chance(0.35)) f.sayIn = rand(0.1, 0.8); }
    // the gaps fill back up from the sides
    for (let i = 0; i < k - 1; i++) { const n = orpAddDancer(chance(0.5) ? -30 : W + 30, rand(FT + 12, FB - 10)); const tx = rand(80, W - 80); const sc0 = n.script; n.script = (m, dt2) => { if (Math.abs(m.x - tx) > 6) npcWalkTo(m, tx, m.y, 70, dt2); else { m.script = sc0; } }; }
  }, 0.7);
}
function orpLightsUp() {
  S.lights = 0.001; musicSet(null); sfx('scratch'); showBanner('2AM', 'LIGHTS ON. EVERYBODY OUT.', 2.6);
  for (const n of (S.dancers || [])) { n.script = (m, dt2) => { npcWalkTo(m, m.x < W / 2 ? -60 : W + 60, m.y, 110, dt2); if (m.x < -40 || m.x > W + 40) m.remove = true; }; }
  setTimeout0(() => { musicSet(ST.music); S.wave = null; S.waveIdx++; }, 2.6);
}

// the 2-step beat: hits that land on it do more, and a ring pulses with it
function orpBeatPhase() {
  const bpm = ST && ST.beat, sc = S && orpSc(); if (!bpm || !sc || !sc.beat) return -1;
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

// ================================================================== drawing
// the scene's painting, in place of the stage backdrop
function orpBg() {
  if (!ST || ST.era !== 2001 || !S) return false;
  const img = bgImg('orp/' + (S.scBg || (orpScenes() && orpScenes()[0].bg)));
  if (!img) { ctx.fillStyle = '#0b0c1a'; ctx.fillRect(0, 0, W, H); return true; }
  ctx.save(); ctx.imageSmoothingEnabled = false; ctx.drawImage(img, 0, 0, W, H); ctx.restore();
  if (S.scBg === 'floor') orpClubLights();
  return true;
}
function orpClubLights() {
  if (S.lights) return;
  ctx.save(); ctx.globalCompositeOperation = 'lighter';
  for (let i = 0; i < 5; i++) { const ox = 120 + i * 180 + Math.sin(time * (0.6 + i * 0.17) + i) * 120;
    ctx.fillStyle = ['rgba(255,60,200,0.10)', 'rgba(60,200,255,0.10)', 'rgba(160,90,255,0.10)'][i % 3];
    ctx.beginPath(); ctx.moveTo(ox, 30); ctx.lineTo(ox - 90, H); ctx.lineTo(ox + 90, H); ctx.closePath(); ctx.fill(); }
  ctx.restore();
}
function orpDrawFore() {
  if (!ST || ST.era !== 2001 || !S) return;
  orpDrawServed(); orpDrawQueue();
  if (S.ann) {   // the announcement plate, as the 2006 stages have
    const a = S.ann, k = Math.min(1, a.t / 0.15, (a.life - a.t) / 0.25), w = Math.max(320, a.text.length * 12 + 60), x = W / 2 - w / 2, y = 152;
    ctx.save(); ctx.globalAlpha = Math.max(0, k);
    ctx.fillStyle = '#0a0c1e'; ctx.fillRect(x, y, w, 30); ctx.fillStyle = '#c9a227'; ctx.fillRect(x, y, w, 2); ctx.fillRect(x, y + 28, w, 2);
    pxText(a.text, W / 2, y + 15, 12, '#ffe08a'); ctx.restore();
  }
  // the way on: an arrow to the side you leave by
  if (S.exitReady && !S.wipe && Math.floor(time * 3) % 2 === 0) {
    const e = S.exitReady, x = e.dir > 0 ? W - 70 : 70;
    ctx.fillStyle = 'rgba(8,10,24,0.8)'; ctx.fillRect(x - 70, H / 2 - 40, 140, 54);
    pxText(e.dir > 0 ? 'GO →' : '← GO', x, H / 2 - 22, 18, '#ffe08a'); pxText(e.label, x, H / 2 + 2, 10, '#ffffff');
  }
  // the beat ring and the strobe
  const ph = orpBeatPhase();
  if (ph >= 0 && !S.lights) {
    S.bar = (S.lastPh > 0.5 && ph < 0.5) ? (S.bar || 0) + 1 : (S.bar || 0); S.lastPh = ph;
    if (S.bar % 4 === 0 && ph < 0.12) { ctx.fillStyle = 'rgba(235,240,255,0.10)'; ctx.fillRect(0, 0, W, H); }
    const r = 16 + (1 - ph) * 14, on = ph < 0.14 || ph > 0.9;
    ctx.save(); ctx.strokeStyle = on ? '#7cf7ff' : 'rgba(180,140,255,0.6)'; ctx.lineWidth = on ? 4 : 2; ctx.beginPath(); ctx.arc(W / 2, H - 34, r, 0, Math.PI * 2); ctx.stroke();
    ctx.fillStyle = on ? '#7cf7ff' : 'rgba(255,255,255,0.7)'; ctx.font = '800 11px ' + BODY; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText('BEAT', W / 2, H - 34); ctx.restore();
  }
  if (S.lights) { S.lights = Math.min(1, S.lights + 0.02); ctx.fillStyle = 'rgba(255,250,230,' + (0.22 * S.lights) + ')'; ctx.fillRect(0, 0, W, H); }
  // how-to card
  if (S.howto) {
    const h = S.howto, k = Math.min(1, h.t * 5), bw = 640, x = W / 2 - bw / 2;
    ctx.save(); ctx.globalAlpha = k; ctx.fillStyle = 'rgba(0,0,0,0.45)'; ctx.fillRect(0, 0, W, H);
    ctx.font = '600 16px ' + BODY; const lines = h.lines.flatMap(l => wrapLines(l, bw - 60)); const bh = 92 + lines.length * 24;
    const y = H / 2 - bh / 2;
    ctx.fillStyle = '#0d1022'; ctx.fillRect(x, y, bw, bh); ctx.fillStyle = '#c9a227'; ctx.fillRect(x, y, bw, 4); ctx.fillRect(x, y + bh - 4, bw, 4);
    pxText(h.title, W / 2, y + 28, 20, '#ffe08a');
    ctx.font = '600 16px ' + BODY; ctx.fillStyle = '#f2ecdc'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    lines.forEach((l, i) => ctx.fillText(l, W / 2, y + 62 + i * 24));
    if (h.t > 0.6 && Math.floor(time * 2.5) % 2 === 0) pxText('HIT TO GO', W / 2, y + bh - 20, 11, '#9fe8ff');
    ctx.restore();
  }
  // the wipe between places: black closes in from the side you're heading, the next place's name, then it opens
  if (S.wipe) {
    const w = S.wipe, k = w.t < 0.4 ? w.t / 0.4 : w.t < 0.7 ? 1 : Math.max(0, 1 - (w.t - 0.7) / 0.4);
    ctx.fillStyle = '#05060c';
    if (w.dir > 0) ctx.fillRect(W - W * k, 0, W * k + 1, H); else ctx.fillRect(0, 0, W * k, H);
    if (k > 0.9) pxText(w.label || '', W / 2, H / 2, 22, '#ffe08a');
  }
}
