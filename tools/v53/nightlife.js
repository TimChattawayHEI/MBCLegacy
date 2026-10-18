// ================================================================== NIGHTLIFE 2006 (Version 53)
// A Friday night out in London: Orpington station, the train to Charing Cross, Charing Cross, the smoking area, the N47.
// Everything that moves (the train, the stops, the bus lurching) runs inside the shared game so online co-op stays in step.
const NLX = { keys: ['nl_station', 'nl_train', 'nl_cx', 'nl_alley', 'nl_bus'], img: k => bgImg('nightlife/' + k) };
const NL_FILES = ['st_front', 'st_hall', 'tr_wall', 'tr_door', 'tr_end', 'tr_toilet', 'toilet_guy', 'sc_suburb', 'sc_platform', 'cx_hall',
  'cx_barrier', 'trafalgar', 'alley', 'bus_deck', 'bus_stairs', 'sc_highst'].map(k => 'nightlife/' + k);

// ---------------------------------------------------------------- who's out tonight
Object.assign(FOES, {
  city: { name: 'CITY BOY', hp: 50, speed: 104, dmg: 7, reach: 70, windup: 0.42, score: 260, ai: 'melee', combo2: true,
    lines: ['Do you know who my father is?', 'This shirt cost more than your car.', 'Yah. Totally.', 'I work in finance, actually.'] },
  itgirl: { name: 'IT GIRL', hp: 44, speed: 116, dmg: 7, reach: 68, windup: 0.4, score: 240, ai: 'melee', leap: true,
    lines: ['Ew.', 'Like, oh my God.', 'Daddy will hear about this.', 'These shoes are Italian.'] },
  burb: { name: 'CHECK CAP', hp: 56, speed: 112, dmg: 8, reach: 72, windup: 0.4, score: 260, ai: 'melee', rush: true,
    lines: ["What you lookin' at?", 'Wanna go, bruv?', 'Oi! Oi!', 'Mind my trainers.'] },
  hoops: { name: 'HOOPS', hp: 46, speed: 120, dmg: 7, reach: 68, windup: 0.38, score: 240, ai: 'melee', combo2: true,
    lines: ['Are you starting?', "Don't touch my hair!", 'Babes, hold my earrings.', 'Is it?'] },
  snood: { name: 'SNOOD', hp: 62, speed: 118, dmg: 9, reach: 72, windup: 0.38, score: 300, ai: 'melee', combo2: true,
    lines: ['Wrong carriage.', "You're on our train now.", 'Allow it.', 'Say nothing.'] },
  puffer: { name: 'PUFFER', hp: 50, speed: 142, dmg: 8, reach: 70, windup: 0.34, score: 280, ai: 'melee', rush: true,
    lines: ['Next stop, your stop.', 'Allow it.', 'What?', 'Run your pockets.'] },
  hood: { name: 'HOOD', hp: 58, speed: 122, dmg: 9, reach: 72, windup: 0.4, score: 300, ai: 'melee', aa: true,
    lines: ['Wrong train, bruv.', 'Say nothing.', 'Mind the gap.', 'Allow it.'] },
  grappler: { name: 'THE GRAPPLER', hp: 84, speed: 84, dmg: 6, reach: 70, windup: 0.5, score: 360, ai: 'melee', armor: true,
    lines: ['Come here, you.', 'Hug it out.', "Don't struggle."], extra: (f, dt) => nlGrappler(f, dt) },
  dipper: { name: 'THE DIPPER', hp: 44, speed: 156, dmg: 6, reach: 66, windup: 0.32, score: 320, ai: 'melee',
    lines: ['Nice watch.', "What's the time, mate?", 'Lovely.', "Don't mind me."], extra: (f, dt) => nlDipper(f, dt) },
  lookout: { name: 'THE LOOKOUT', hp: 40, speed: 104, dmg: 7, reach: 60, windup: 0.5, score: 300, ai: 'ranged', shot: 'bottle',
    lines: ['Oi! Over here!', 'Lads! LADS!', 'He saw us.'], extra: (f, dt) => nlLookout(f, dt) },
  stag: { name: 'THE STAG', hp: 64, speed: 86, dmg: 9, reach: 74, windup: 0.5, score: 320, ai: 'melee',
    lines: ['Last night of freedom!', 'Who wants a banana?', 'I LOVE YOU, MATE.', 'Is this the bus to Ibiza?'] },
  groom: { name: 'GROOMSMAN', hp: 52, speed: 108, dmg: 8, reach: 70, windup: 0.42, score: 260, ai: 'melee', rush: true,
    lines: ['DAVE! DAVE! DAVE!', "Stag do, mate. Rules don't apply.", 'Shots! SHOTS!', 'Where are we?'] },
  // bosses (the Elba boss engine, each with a tick of its own)
  inspector: { name: 'THE TICKET INSPECTOR', hp: 300, speed: 92, dmg: 11, scale: 1.08, beatenWord: 'VALID!', beatenLine: '...Have a nice evening.', sub: 'Revenue protection. Zero tolerance.',
    intro: ['Tickets, please.', 'Tickets. All of you.'], lines: ['Ticket?', 'No ticket, no travel.', "I've seen your sort."], tick: (b, dt, rage) => nlInspector(b, dt, rage) },
  lenny: { name: 'LEWISHAM LENNY', hp: 380, speed: 104, dmg: 13, scale: 1.12, beatenWord: 'TERMINATED!', beatenLine: '...This is my stop anyway.', sub: 'Runs this carriage. Thinks he runs the line.',
    intro: ['This is my carriage.', "You're on the wrong train."], lines: ['Hold on to something.', 'Mind the doors.', 'Fresh air?'], tick: (b, dt, rage) => nlLenny(b, dt, rage) },
  jeweller: { name: 'THE JEWELLER', hp: 420, speed: 100, dmg: 12, scale: 1.1, beatenWord: 'TIME UP!', beatenLine: '...Keep the watch.', sub: 'Collects watches. Never his own.',
    intro: ['Lovely piece, that.', 'What time is it? Mine.'], lines: ['Tick tock.', 'Shiny, innit?', 'Every watch has a price.'], tick: (b, dt, rage) => nlJeweller(b, dt, rage) },
});
// on the night bus the lads' sheets stand in for the travellers who aren't drawn yet
const NL_NPC = { commuter: { name: 'COMMUTER' }, oldboy: { name: 'OLD BOY' }, smiler: { name: 'SMILER' } };
Object.assign(FOES, NL_NPC);

// ---------------------------------------------------------------- the stages
Object.assign(STAGES, {
  nl_station: { n: 8, era: 2006, title: 'ORPINGTON STATION', sub: 'Friday. 9pm. Train to Charing Cross.', bg: 'nl_station', ft: 352, fb: 506, len: 3300,
    music: 'platform', aggro: 3, aa: 0.4, intro: 'nlIntro',
    items: [{ w: 'alcopop', x: 760, y: 470 }, { w: 'cone', x: 1560, y: 440 }],
    breakables: [{ type: 'bin', x: 1180, y: 476, drop: 'kebab' }, { type: 'bin', x: 2380, y: 450, drop: 'w:alcopop' }],
    waves: [
      { at: 360, groups: [[['townie', 'R'], ['ladette', 'R'], ['townie', 'L']]] },
      { at: 1100, groups: [[['tracksuit', 'R'], ['hoodie', 'R']], [['townie', 'R'], ['ladette', 'L'], ['tracksuit', 'R']]] },
      { at: 1800, groups: [[['chunk', 'R'], ['townie', 'L'], ['ladette', 'R']], [['hoodie', 'R'], ['tracksuit', 'L']]], food: 'kebab' },
      { at: 'end', boss: 'inspector', title: 'THE TICKET INSPECTOR' },
    ] },
  nl_train: { n: 9, era: 2006, title: 'THE 21:12 TO CHARING CROSS', sub: 'Calling at Chislehurst, Hither Green, Lewisham...', bg: 'nl_train', ft: 372, fb: 506, len: 5600,
    music: 'train', aggro: 3, aa: 0.45, train: true,
    items: [{ w: 'alcopop', x: 900, y: 480 }],
    breakables: [{ type: 'luggage', x: 1500, y: 470, drop: 'w:alcopop' }, { type: 'luggage', x: 3100, y: 480, drop: 'sroll' }, { type: 'luggage', x: 4300, y: 460, drop: 'w:alcopop' }],
    waves: [
      { at: 300, groups: [[['townie', 'R'], ['ladette', 'R']]] },
      { at: 1150, stop: 'CHISLEHURST', groups: [[['city', 'R'], ['itgirl', 'R'], ['city', 'R']], [['itgirl', 'R'], ['city', 'L']]] },
      { at: 2700, stop: 'HITHER GREEN', groups: [[['burb', 'R'], ['hoops', 'R'], ['burb', 'R']], [['hoops', 'R'], ['burb', 'L'], ['burb', 'R']]], food: 'sroll' },
      { at: 3800, stop: 'LEWISHAM', groups: [[['snood', 'R'], ['puffer', 'R'], ['hood', 'R']], [['snood', 'R'], ['hood', 'L'], ['puffer', 'R'], ['puffer', 'R']]] },
      { at: 'end', boss: 'lenny', title: 'LEWISHAM LENNY' },
    ] },
  nl_cx: { n: 10, era: 2006, title: 'CHARING CROSS', sub: '21:47. This train terminates here.', bg: 'nl_cx', ft: 356, fb: 506, len: 3200,
    music: 'terminus', aggro: 3, aa: 0.45,
    items: [{ w: 'alcopop', x: 820, y: 470 }],
    breakables: [{ type: 'bin', x: 1300, y: 470, drop: 'chips' }, { type: 'bin', x: 2300, y: 460, drop: 'w:alcopop' }],
    waves: [
      { at: 360, groups: [[['puffer', 'R'], ['snood', 'R'], ['city', 'L']]] },
      { at: 1100, groups: [[['burb', 'R'], ['hoops', 'R']], [['itgirl', 'R'], ['city', 'R'], ['burb', 'L']]], food: 'chips' },
      { at: 1800, groups: [[['hood', 'R'], ['snood', 'R'], ['puffer', 'L']], [['city', 'R'], ['hood', 'R']]] },
      { at: 'end', final: true, groups: [[['snood', 'R'], ['burb', 'R'], ['puffer', 'R'], ['hoops', 'L']]] },
    ] },
  nl_alley: { n: 11, era: 2006, title: 'THE SMOKING AREA', sub: "Round the back. Where's Seb?", bg: 'nl_alley', ft: 356, fb: 506, len: 3200,
    music: 'smoking', aggro: 3, aa: 0.5, intro: 'nlSeb',
    items: [{ w: 'cue', x: 1200, y: 460 }],
    breakables: [{ type: 'keg', x: 980, y: 480, drop: 'kebab' }, { type: 'bin', x: 2100, y: 460, drop: 'w:alcopop' }],
    waves: [
      { at: 300, event: 'sebScene' },
      { at: 420, groups: [[['dipper', 'R'], ['grappler', 'R'], ['lookout', 'R']]] },
      { at: 1300, groups: [[['grappler', 'R'], ['dipper', 'L']], [['dipper', 'R'], ['lookout', 'R'], ['grappler', 'L']]], food: 'kebab' },
      { at: 2000, groups: [[['dipper', 'R'], ['dipper', 'L'], ['grappler', 'R'], ['lookout', 'R']]] },
      { at: 'end', boss: 'jeweller', title: 'THE JEWELLER' },
    ] },
  nl_bus: { n: 12, era: 2006, title: 'THE N47', sub: '01:50. Top deck. Next stop: home.', bg: 'nl_bus', fixed: true, bus: true, ft: 384, fb: 476, raft: [150, 900], len: W,
    music: 'nightbus', aggro: 3, aa: 0.4, intro: 'nlBus', outro: 'nlHome',
    breakables: [{ type: 'pole', x: 380, y: 400, drop: 'w:pole' }, { type: 'pole', x: 640, y: 400, drop: 'w:pole' }, { type: 'pole', x: 820, y: 470, drop: 'w:pole' }],
    waves: [
      { groups: [[['stag', 'L'], ['groom', 'L'], ['groom', 'L']]] },
      { groups: [[['burb', 'L'], ['hoops', 'L']], [['groom', 'L'], ['puffer', 'L']]], food: 'kebab' },
      { event: 'smiler' },
      { groups: [[['snood', 'L'], ['hood', 'L'], ['dipper', 'L']], [['grappler', 'L'], ['lookout', 'L']]] },
      { groups: [[['stag', 'L'], ['groom', 'L'], ['city', 'L'], ['itgirl', 'L']]], food: 'kebab' },
      { event: 'smiler' },
      { final: true, groups: [[['groom', 'L'], ['stag', 'L'], ['groom', 'L']], [['puffer', 'L'], ['burb', 'L'], ['snood', 'L']]] },
    ] },
});
['nl_station', 'nl_train', 'nl_cx', 'nl_alley', 'nl_bus'].forEach(k => { BOSS_MUSIC[k] = 'boss2006'; });
BOSS_KEYS.add('boss2006');
Object.assign(TRACKS, {
  platform: { src: 'music/platform-zero.mp3', loop: 60, fb: 'garage' }, train: { src: 'music/mind-the-gap.mp3', loop: 55.65, fb: 'garage' },
  terminus: { src: 'music/terminus.mp3', loop: 60.95, fb: 'arrival' }, smoking: { src: 'music/smoking-area.mp3', loop: 54.86, fb: 'ramsden' },
  nightbus: { src: 'music/night-bus.mp3', loop: 58.18, fb: 'naval' }, boss2006: { src: 'music/last-orders-boss.mp3', loop: 51.2, fb: 'boss' },
});

// ---------------------------------------------------------------- the group chats (2006: a colour screen, texts not WhatsApp)
Object.assign(CHATS, {
  nlIntro: [
    ['sys', 'October 2006. Friday night.'],
    ['tim', "Right. Orpington station, 9pm. Train's at 21:12. I've done a plan."],
    ['byron', "9pm means 8:55. I'll be under the clock."],
    ['pearcy', 'wearing my good shirt'],
    ['kelly', 'which one'],
    ['pearcy', 'the shiny one'],
    ['seb', 'Pre-drinks at mine. Tactical.'],
    ['marc', "London. Proper London. Let's have it."],
    ['tim', 'Sam?'],
    ['sam', 'Left already. 5 mins.'],
    ['sys', '30 minutes later.'],
    ['byron', 'Sam.'],
    ['sam', 'Literally 5 mins.'],
    ['kelly', "he's not even out of bed is he"],
    ['sam', 'I am OUT of bed.'],
  ],
  nlSeb: [
    ['sys', '23:58. Somewhere off the Strand.'],
    ['tim', 'Good night so far. Anyone seen Seb?'],
    ['kelly', 'he went for a fag about an hour ago'],
    ['pearcy', 'seb doesnt smoke'],
    ['marc', 'Saw him round the back by the smoking area. With some new mates.'],
    ['byron', 'Seb does not have new mates.'],
    ['sam', "I'll go and look."],
    ['tim', 'Everyone go and look.'],
  ],
  nlBus: [
    ['sys', '01:41. Charing Cross.'],
    ['seb', "Watch is back. All good. Lovely lads, actually, until they weren't."],
    ['byron', 'The last train left at 00:38.'],
    ['tim', 'Night bus then. N47. Trafalgar Square, all the way home.'],
    ['marc', "I'm not paying a bus fare. I'll walk."],
    ['kelly', 'its 14 miles mate'],
    ['marc', 'Lovely night for it.'],
    ['pearcy', 'top deck. front seats. called it'],
  ],
  nlHome: [
    ['sys', '03:20. Orpington.'],
    ['sam', 'Home. Bed. Best night ever.'],
    ['seb', 'Still got the watch. Still on Elba time.'],
    ['tim', "Marc? You home?"],
    ['marc', 'Catford.'],
    ['sys', '06:45.'],
    ['marc', 'Bromley.'],
    ['byron', 'Sunrise in Bromley. A man of principle.'],
    ['sys', 'KRSSSHHHHHHHHHH'],
    ['sys', 'Back in the present. For real this time.'],
  ],
});

// ---------------------------------------------------------------- per-frame, every 2006 stage
function updateNightlife(dt) {
  if (!S || !ST || ST.era !== 2006) return;
  if (!S.npcs) S.npcs = [];
  updateNpcs(dt);
  S.cineA = (S.cineA || 0) + ((S.cine ? 1 : 0) - (S.cineA || 0)) * Math.min(1, dt * 5);
  if (S.ann) { S.ann.t += dt; if (S.ann.t > S.ann.life) S.ann = null; }
  if (ST.train) { nlTrainTick(dt); nlWindTick(dt); }
  if (ST.bus) nlBusTick(dt);
  if (ST.bg === 'nl_cx') nlCxTick(dt);
  if (ST.bg === 'nl_alley') nlAlleyTick(dt);
  if (ST.bg === 'nl_station' && !S.saidSam && player.x > 520) { S.saidSam = true; if (player.def.id !== 'sam') setTimeout0(() => popWord(cam.x + W - 80, FT + 30, 120, "SAM: 'NEARLY THERE'", false), 0.2); }
}
function nlAnnounce(text, life) { S.ann = { text, t: 0, life: life || 3.6 }; sfx('page'); }
// a wave can carry a train stop; the event names run their own little scripts
function nlEvent(ev) {
  if (ev === 'sebScene') { nlSebScene(); return true; }
  if (ev === 'smiler') { nlSmiler(); return true; }
  return false;
}
function nlStartWave(w) {
  if (!w.stop) return false;
  nlStop(w);
  return true;
}

// ================================================================== the train
// The carriage is a long repeating interior; the world behind the windows scrolls with the train's speed, not the camera.
const TRAIN = { seg: 640, car: 2048, cruise: 960, doors: [420, 1180], stops: ['PETTS WOOD', 'CHISLEHURST', 'ELMSTEAD WOODS', 'GROVE PARK', 'HITHER GREEN', 'LEWISHAM', 'LONDON BRIDGE'] };
const TRAIN_PASS = [{ x: 700, name: 'PETTS WOOD' }, { x: 2200, name: 'ELMSTEAD WOODS' }, { x: 2480, name: 'GROVE PARK' }, { x: 4700, name: 'LONDON BRIDGE' }];
function trainDoorsNear(x) {
  const out = [];
  for (let c = 0; c * TRAIN.car < ST.len + TRAIN.car; c++) for (const d of TRAIN.doors) out.push(c * TRAIN.car + d);
  return out.filter(d => d > cam.x + 80 && d < cam.x + W - 80).sort((a, b) => Math.abs(a - x) - Math.abs(b - x));
}
function nlTrainTick(dt) {
  if (S.trainV == null) { S.trainV = TRAIN.cruise; S.doorOpen = 0; S.passIdx = 0; S.toilet = 0; nlAnnounce('THIS TRAIN IS FOR CHARING CROSS', 3.4); }
  const st = S.stopSeq;
  if (st) {
    st.t += dt;
    if (st.phase === 'brake') {
      S.trainV = Math.max(0, TRAIN.cruise * (1 - st.t / 2.0));
      if (st.t >= 2.0) { st.phase = 'open'; st.t = 0; S.trainV = 0; sfx('hiss'); nlAnnounce('THIS IS ' + st.name + '. MIND THE GAP.', 3); addShake(4); nlLurch(-220); }
    } else if (st.phase === 'open') {
      S.doorOpen = Math.min(1, st.t / 0.5);
      if (!st.fled && st.t > 0.3) { st.fled = true; nlFleeing(2); }
      if (!st.spawned && st.t > 0.7) {
        st.spawned = true;
        const ds = trainDoorsNear(cam.x + W * 0.72), g = st.wave.groups[0];
        const out = g.map(([t], i) => { const dx = ds[i % ds.length] || cam.x + W - 120; const f = makeFoe(t, dx + rand(-20, 20), FT + 6); f.face = player.x < dx ? -1 : 1; f.vy = 120; return f; });
        for (let n = D().extra; n > 0; n--) if (n >= 1 || chance(n)) { const [t] = pick(g); out.push(makeFoe(t, (ds[0] || cam.x + W - 120) + rand(-30, 30), FT + 6)); }
        foes.push(...out);
        if (st.name === 'LEWISHAM') setTimeout0(() => say(player, pick(["Lewisham. Dangerous place, this.", 'Lewisham. Keep your hands in your pockets, lads.']), 2.4, true), 0.6);
        if (st.name === 'LEWISHAM') setTimeout0(() => say(player, 'Still. Could be worse. Could be Croydon.', 2.6, true), 3.3);
      }
      if (st.t > 2.4) { st.phase = 'close'; st.t = 0; nlAnnounce('MIND THE DOORS', 1.6); sfx('page'); }
    } else if (st.phase === 'close') {
      S.doorOpen = Math.max(0, 1 - st.t / 0.5);
      if (st.t > 0.7) { st.phase = 'depart'; st.t = 0; nlLurch(-260); addShake(5); }
    } else if (st.phase === 'depart') {
      S.trainV = TRAIN.cruise * Math.min(1, st.t / 2.6);
      if (st.t > 2.6) { S.trainV = TRAIN.cruise; S.stopSeq = null; S.hold = false; const nx = TRAIN.stops[TRAIN.stops.indexOf(st.name) + 1]; if (nx) setTimeout0(() => nlAnnounce('THE NEXT STATION IS ' + nx, 3.4), 1.5); }
    }
  }
  if (S.brakeT > 0) { S.brakeT -= dt; S.trainV = Math.max(80, S.trainV - 900 * dt); if (S.brakeT <= 0 && !S.stopSeq) S.reaccel = 1; }
  else if (S.reaccel && !S.stopSeq) { S.trainV = Math.min(TRAIN.cruise, S.trainV + 420 * dt); if (S.trainV >= TRAIN.cruise) S.reaccel = 0; }
  S.scrollX += S.trainV * dt;
  if (S.trainV > 600 && chance(dt * 0.25)) addShake(2.5);   // over the points
  // passing stations: just the announcement
  const pass = TRAIN_PASS[S.passIdx];
  if (pass && player.x > pass.x) { S.passIdx++; nlAnnounce('THE NEXT STATION IS ' + pass.name, 3); }
  // the toilets: out of order, out of order, out of order... and then the one that isn't
  if (!S.toilet && player.x > 1880 && !S.wave) { S.toilet = 1; S.toiletT = 0; }
  if (S.toilet === 1) { S.toiletT += dt; if (S.toiletT > 0.25) { S.toilet = 2; S.toiletT = 0; sfx('page'); say(player, 'Need a wee. Hang on.', 1.6, true); } }
  else if (S.toilet === 2) { S.toiletT += dt; if (S.toiletT > 1.4) { S.toilet = 3; S.toiletT = 0; sfx('hiss'); popWord(nlToiletX() + 30, FT + 40, 150, 'OI! SHUT THE DOOR!', true); addShake(3); setTimeout0(() => say(player, 'Sorry! SORRY!', 1.6, true), 0.7); } }
  else if (S.toilet === 3) { S.toiletT += dt; if (S.toiletT > 2.2) { S.toilet = 4; sfx('thud'); } }
}
function nlToiletX() { return 1960; }
// braking throws everyone towards the front of the train, pulling away throws them back
function nlLurch(v) {
  const all = (NET.on ? PL : [player]).concat(foes.filter(f => !f.boss && canBeHit(f)));
  for (const e of all) if (e.z <= 0 && e.state !== 'cut') { e.vx += v * (e.boss ? 0.2 : 1); if (e !== player && !PL.includes(e) && Math.abs(v) > 500 && chance(0.6)) knockDown(e, Math.sign(v), Math.abs(v) * 0.5); }
}
function nlStop(w) {
  S.hold = true; S.stopSeq = { wave: w, name: w.stop, phase: 'brake', t: 0 };
  nlAnnounce('THE NEXT STATION IS ' + w.stop, 2.2);
  setTimeout0(() => { if (S.stopSeq) { nlLurch(420); addShake(6); sfx('heavy'); } }, 0.9);
}
// passengers leg it the other way
function nlFleeing(n) {
  for (let i = 0; i < n; i++) {
    const kind = i % 2 ? 'oldboy' : 'commuter', x = cam.x + W + 60 + i * 70, y = rand(FT + 20, FB - 20);
    const p = makeNpc(kind, x, y); p.face = -1; p.flee = true;
    p.script = (n2, dt) => { n2.state = 'walk'; n2.walk += dt * 14; n2.x -= (n2.kind === 'oldboy' ? 210 : 300) * dt; if (n2.t > 0.2 && !n2.said) { n2.said = true; if (chance(0.7)) say(n2, pick(['Excuse me! Excuse me!', 'Not again...', 'I want to get off!', 'Every Friday.']), 1.6, true); } if (n2.x < cam.x - 120) n2.remove = true; };
    S.npcs.push(p);
  }
}

// ---------------------------------------------------------------- Lewisham Lenny: the passenger alarm, the doors, the charge
function nlLenny(b, dt, rage) {
  const p = player;
  switch (b.state) {
    case 'idle': case 'walk':
      if (b.cool > 0 || !playerTargetable()) return false;
      { const dx = Math.abs(p.x - b.x), r = Math.random();
        if (!b.alarmUsed || (rage && r < 0.18 && !S.brakeT)) { b.alarmUsed = true; b.state = 'alarmWind'; b.t = 0; say(b, 'Hold on to something.', 1.8, true); return true; }
        if (dx > 160 && dx < 420 && r < 0.3) { b.state = 'kneeWind'; b.t = 0; b.vx = b.vy = 0; return true; }
        if (dx > 200 && r < 0.55) { b.state = 'chargeWind'; b.t = 0; b.vx = b.vy = 0; return true; }
        if (r < 0.7 && !S.windT && (b.hp < b.maxHp * 0.7)) { b.state = 'doorWind'; b.t = 0; b.vx = b.vy = 0; say(b, 'Fresh air?', 1.6, true); return true; }
      }
      return false;
    case 'alarmWind':
      b.vx = b.vy = 0;
      if (b.t > 0.8) { b.state = 'alarm'; b.t = 0; sfx('siren'); flashT = Math.max(flashT, 0.08); S.brakeT = 1.4; nlLurch(760); addShake(12); popWord(b.x, b.y, 200, 'EMERGENCY BRAKE!', true); for (const pl of (NET.on ? PL : [p])) if (pl.z <= 0 && canBeHit(pl) && !(pl.buffT > 0)) { pl.vx += 300; } }
      return true;
    case 'alarm':
      b.vx = b.vy = 0;
      if (b.t > 0.6) { b.state = 'chargeWind'; b.t = 0; }
      return true;
    case 'doorWind':
      b.vx = b.vy = 0;
      if (b.t > 0.7) { b.state = 'doorOpen'; b.t = 0; S.windX = trainDoorsNear(b.x)[0] || b.x; S.windT = 3.6; sfx('gust'); nlAnnounce('PLEASE DO NOT OBSTRUCT THE DOORS', 2.4); }
      return true;
    case 'doorOpen':
      b.vx = b.vy = 0;
      if (b.t > 0.5) { b.state = 'rest'; b.t = 0; }
      return true;
  }
  return false;
}
// an open door at speed: everyone is pulled towards it, and the doorway itself hurts
function nlWindTick(dt) {
  if (!(S.windT > 0)) { S.doorWind = Math.max(0, (S.doorWind || 0) - dt * 3); return; }
  S.windT -= dt; S.doorWind = Math.min(1, (S.doorWind || 0) + dt * 4);
  const pull = e => {
    if (e.z > 0 || e.boss || !canBeHit(e)) return;
    const dx = S.windX - e.x;
    if (Math.abs(dx) < 380) { e.vx += Math.sign(dx) * 520 * dt * 3; e.vy -= 160 * dt; }
    if (Math.abs(dx) < 34 && e.y < FT + 50) {
      if (e === player || PL.includes(e)) { if (pHittable(30) && !(e.windHit > 0)) { e.windHit = 1.2; hitP({ x: S.windX, face: 1, kind: 'door', def: { name: 'DOOR' } }, 10, Math.sign(e.x - S.windX) || 1, true, 380); popWord(e.x, e.y, 150, 'MIND THE GAP!', true); } }
      else if (e.state !== 'down') { knockDown(e, Math.sign(e.x - S.windX) || 1, 260); e.hp -= 10; popWord(e.x, e.y, 120, 'WHOOSH!', false); }
    }
  };
  for (const e of (NET.on ? PL : [player])) { pull(e); if (e.windHit > 0) e.windHit -= dt; }
  for (const f of foes) pull(f);
  if (chance(dt * 30)) parts.push({ k: 'debris', x: S.windX + rand(-200, 200), y: rand(FT, FB), z: rand(20, 120), vx: (Math.random() < 0.5 ? 1 : -1) * 40, vz: 40, t: 0, life: 0.5, r: 2, col: 'rgba(230,240,255,0.7)', rot: 0, vr: 0 });
}

// ================================================================== the station
function nlInspector(b, dt, rage) {
  const p = player, dx = Math.abs(p.x - b.x), dy = Math.abs(p.y - b.y);
  switch (b.state) {
    case 'idle': case 'walk': {
      if (b.cool > 0 || !playerTargetable()) return false;
      const r = Math.random();
      if (dx < 120 && dy < 34 && r < 0.4) { b.state = 'slapWind'; b.t = 0; b.vx = b.vy = 0; return true; }
      if (dx > 140 && dx < 320 && r < 0.4) { b.state = 'fineWind'; b.t = 0; b.vx = b.vy = 0; say(b, 'Ticket!', 1.2, true); return true; }
      if (dx < 260 && r < 0.6 && !b.blockCool) { b.state = 'blockWind'; b.t = 0; b.vx = b.vy = 0; return true; }
      return false;
    }
    case 'slapWind':
      b.vx = b.vy = 0; if (Math.abs(p.x - b.x) > 8) b.face = Math.sign(p.x - b.x);
      if (b.t > 0.55 * D().wind) { b.state = 'slap'; b.t = 0; b.atkT = 0; b.atk = { t0: 0.05, t1: 0.2, reach: [0, 110], depth: 30, dmg: 14, kd: true, kb: 380, hs: 0.1, hit: new Set() }; sfx('swing'); }
      return true;
    case 'slap': if (b.t > 0.4) { b.atk = null; b.state = 'rest'; b.t = 0; } return true;
    case 'fineWind':
      b.vx = b.vy = 0; if (Math.abs(p.x - b.x) > 8) b.face = Math.sign(p.x - b.x);
      if (b.t > 0.75 * D().wind) {
        b.state = 'fine'; b.t = 0; sfx('whistle');
        if (pHittable(60) && Math.abs(p.x - b.x) < 340 && Math.abs(p.y - b.y) < 60 && Math.sign(p.x - b.x) === b.face) {
          popWord(p.x, p.y, 170, 'PENALTY FARE!', true); hitP(b, 7, b.face, false, 160); addScore(-200, true);
        } else popWord(b.x, b.y, 190, 'NO TICKET?', false);
      }
      return true;
    case 'fine': if (b.t > 0.5) { b.state = 'rest'; b.t = 0; } return true;
    case 'blockWind':
      b.vx = b.vy = 0;
      if (b.t > 0.2) { b.state = 'block'; b.t = 0; say(b, 'Not without a ticket.', 1.4, true); }
      return true;
    case 'block':
      b.vx = b.vy = 0; if (Math.abs(p.x - b.x) > 8) b.face = Math.sign(p.x - b.x);
      // blocks anything from the front; go round the back
      b.inv = Math.sign(p.x - b.x) === b.face ? 0.05 : 0;
      if (b.inv && p.atk && p.atkT < 0.05 && Math.abs(p.x - b.x) < 130 && !b.saidBlock) { b.saidBlock = true; popWord(b.x, b.y, 170, 'BLOCKED!', false); sfx('thud'); }
      if (b.t > 1.5) { b.state = 'rest'; b.t = 0; b.inv = 0; b.saidBlock = false; b.blockCool = true; setTimeout0(() => { b.blockCool = false; }, 3); }
      return true;
  }
  return false;
}

// ================================================================== Charing Cross: the barriers, then Trafalgar Square
function nlCxTick(dt) {
  if (S.done && !S.traf) { S.traf = { t: 0 }; S.endT = 99; S.cine = 1; for (const pl of (NET.on ? PL : [player])) if (pl.state !== 'dead') { pl.vx = pl.vy = 0; } }
  if (S.traf) {
    S.traf.t += dt;
    if (S.traf.t > 0.6 && !S.traf.said) { S.traf.said = true; sfx('page'); }
    if (S.traf.t > 6.2) { S.traf = null; S.trafDone = true; S.endT = 0.01; S.cine = 0; }
  }
}
function nlDrawTrafalgar() {
  const tr = S.traf; if (!tr) return;
  const img = NLX.img('trafalgar'); const a = Math.min(1, tr.t / 0.8, (6.2 - tr.t) / 0.6);
  ctx.save(); ctx.globalAlpha = Math.max(0, a); ctx.fillStyle = '#05060c'; ctx.fillRect(0, 0, W, H);
  if (img) {
    // a slow push in and drift across the square
    const k = (W / img.width) * (1.12 + tr.t * 0.02), w = img.width * k, h = img.height * k;
    const x = (W - w) / 2 - (tr.t - 3) * 6, y = (H - h) / 2 + 10;
    ctx.imageSmoothingEnabled = false; ctx.drawImage(img, Math.round(x / 2) * 2, Math.round(y / 2) * 2, Math.round(w / 2) * 2, Math.round(h / 2) * 2);
  }
  ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, 54); ctx.fillRect(0, H - 54, W, 54);
  if (tr.t > 1.2) { const b = Math.min(1, (tr.t - 1.2) / 0.5); ctx.globalAlpha = Math.max(0, a) * b; textOut('LONDON.', W / 2, H - 92, '34px ' + DISPLAY, '#efe6d2', OUT, 7, 'center'); }
  if (tr.t > 2.0) { ctx.font = '700 16px ' + BODY; ctx.fillStyle = '#ffd23f'; ctx.textAlign = 'center'; ctx.fillText('Trafalgar Square, 21:58', W / 2, H - 64); }
  ctx.restore();
}

// ================================================================== the smoking area: Seb, the watch crew
function nlSebScene() {
  S.wave = null; S.waveIdx++;
  const sebPlays = (NET.on ? PL : [player]).some(pl => pl.def.id === 'seb');
  S.cine = 1; S.hold = true; for (const pl of (NET.on ? PL : [player])) { pl.vx = pl.vy = 0; if (pl.z <= 0 && !['down', 'getup', 'dead'].includes(pl.state)) { pl.state = 'cut'; pl.atk = null; } }
  const sx = cam.x + W * 0.62, sy = FT + 30;
  // the crew round him, chatting him up
  const crew = [['dipper', sx + 60, sy + 20], ['grappler', sx + 120, sy + 50], ['lookout', sx + 170, sy + 10]].map(([k, x, y]) => { const n = makeNpc(k, x, y); n.face = -1; n.def = FOES[k]; S.npcs.push(n); return n; });
  if (sebPlays) {
    const pl = (NET.on ? PL : [player]).find(q => q.def.id === 'seb');
    pl.x = sx; pl.y = sy; pl.face = 1; pl.state = 'cut';
    setTimeout0(() => say(crew[0], "Lovely watch. What is it, Swiss?", 2.2, true), 0.6);
    setTimeout0(() => say(pl, "It's Elba time, mate. Long story.", 2.2, true), 2.6);
    setTimeout0(() => { crew[0].state = 'walk'; crew[0].x -= 30; popWord(pl.x, pl.y, 150, 'CLICK.', false); sfx('page'); }, 4.4);
    setTimeout0(() => say(pl, '...Hang on.', 1.6, true), 5.2);
    setTimeout0(() => { say(pl, "THAT'S MY WATCH.", 2, true); pl.rage = true; addShake(10); flashT = 0.2; sfx('special'); popWord(pl.x, pl.y, 210, 'SEB IS RAGING!', true); }, 6.4);
  } else {
    // Seb, sat on the back step, surrounded; you come out of the fire door
    const seb = makeNpc('seb', sx, sy); seb.def = CHAR_BY_ID.seb; seb.look = CHAR_BY_ID.seb.look; seb.face = 1; S.npcs.push(seb);
    setTimeout0(() => say(crew[0], "Lovely watch. What is it, Swiss?", 2.2, true), 0.6);
    setTimeout0(() => say(seb, "It's Elba time, mate. Long story.", 2.2, true), 2.6);
    setTimeout0(() => { crew[0].x -= 30; popWord(seb.x, seb.y, 150, 'CLICK.', false); sfx('page'); }, 4.4);
    setTimeout0(() => say(player, 'SEB! Your watch!', 1.8, true), 5.2);
    setTimeout0(() => { say(seb, '...OI!', 1.6, true); }, 6.2);
    setTimeout0(() => { seb.remove = true; nlSebAlly(seb.x, seb.y); }, 7.0);
  }
  // the crew turn round and it kicks off
  setTimeout0(() => {
    for (const n of crew) { n.remove = true; const f = makeFoe(n.kind, n.x, n.y); f.face = -1; f.state = 'hover'; foes.push(f); }
    S.cine = 0; S.hold = false;
    for (const pl of (NET.on ? PL : [player])) if (pl.state === 'cut') setIdle(pl);
    musicSet(ST.music);
  }, 7.6);
}
function nlSebAlly(x, y) {
  const c = CHAR_BY_ID.seb;
  const a = { kind: 'ally', ally: true, friend: true, def: c, look: c.look, x, y, z: 0, vx: 0, vy: 0, vz: 0, face: 1, state: 'idle', t: 0, life: 9999,
    combo: 0, comboT: 0, atk: null, atkT: 0, flash: 0, walk: 0, half: 20, scale: 1, inv: 99, landed: false, cool: 0.4, sayCool: 0 };
  allies.push(a); S.sebAlly = a;
}
function nlAlleyTick(dt) {
  // Seb's rage lasts the stage; the watch comes back when the Jeweller goes down
  if (S.done && !S.watchBack) {
    S.watchBack = true;
    const seb = (NET.on ? PL : [player]).find(q => q.def.id === 'seb') || S.sebAlly;
    if (seb) { setTimeout0(() => { popWord(seb.x, seb.y, 200, 'WATCH RECOVERED!', true); sfx('jackpot'); nlWatchFx = { who: seb, t: 0 }; say(seb, pick(['Tick tock.', 'Elba time. Back where it belongs.', "That's mine. Thank you."]), 2.4, true); }, 0.6); S.endT = Math.max(S.endT, 3.4); }
  }
}
function nlHeldFree(f) { if (player.state === 'netted' && player.heldBy === f) freePlayer(); }
// the Grappler: a bear hug from behind; mash to get out, and his mates go through your pockets meanwhile
function nlGrappler(f, dt) {
  const p = player;
  if (f.state === 'hug') {
    f.vx = f.vy = 0;
    if (p.state !== 'netted' || p.heldBy !== f) { f.state = 'recover'; f.t = 0; return true; }
    p.x = f.x + f.face * 34; p.y = f.y + 2; p.face = -f.face;
    if (pressed.has('punch') || pressed.has('jump') || pressed.has('left') || pressed.has('right') || taps.length) { f.mash = (f.mash || 0) + 1; p.flash = 0.05; }
    if (p.rage || (f.mash || 0) >= 7 || f.t > 2.6) {
      freePlayer(); f.state = (f.mash >= 7 || p.rage) ? 'hurt' : 'recover'; f.t = 0; f.mash = 0;
      if (p.rage) { popWord(p.x, p.y, 160, 'NOT TODAY!', true); knockDown(f, -f.face, 380); f.hp -= 12; }
      else if (f.state === 'hurt') { popWord(p.x, p.y, 150, 'BROKE FREE!', false); f.vx = -f.face * 200; }
    }
    return true;
  }
  if (f.state === 'attack' && f.atk && !f.hugTry && f.atkT > 0.05) {
    f.hugTry = true;
    if (canBeHit(p) && !(p.buffT > 0) && p.z < 20 && p.state !== 'netted' && Math.abs(p.x - f.x) < 80 && Math.abs(p.y - f.y) < 26) {
      if (p.rage) { popWord(p.x, p.y, 150, 'NOPE!', false); return false; }
      f.atk = null; holdPlayer(f); f.state = 'hug'; f.t = 0; f.mash = 0; say(f, pick(['Got you.', 'Hug it out.', 'Shh shh shh.']), 1.4, true); sfx('grab');
      return true;
    }
  }
  if (f.state !== 'attack') f.hugTry = false;
  if (f.state === 'hurt' || f.state === 'down' || f.state === 'thrown' || f.state === 'dead') nlHeldFree(f);
  return false;
}
// the Dipper: slips your punches and lifts your weapon (or a bit of your score)
function nlDipper(f, dt) {
  const p = player;
  f.dodgeCool = (f.dodgeCool || 0) - dt;
  if (f.state === 'dodge') { f.vx = -f.face * 300 * Math.max(0, 1 - f.t * 2); f.vy = (f.dy || 0) * 160; if (f.t > 0.45) { f.state = 'hover'; f.t = 0; f.inv = 0; } return false; }
  if (p.atk && p.atkT < 0.08 && f.dodgeCool <= 0 && canBeHit(f) && f.state !== 'down' && Math.abs(p.x - f.x) < 120 && Math.abs(p.y - f.y) < 40 && chance(0.45)) {
    f.dodgeCool = 2.2; f.state = 'dodge'; f.t = 0; f.inv = 0.3; f.dy = chance(0.5) ? 1 : -1; f.face = Math.sign(p.x - f.x) || f.face; popWord(f.x, f.y, 140, pick(['SLIPPY!', 'NOPE!', 'TOO SLOW!']), false);
    if (f.token) releaseToken(f, 0.4);
    return false;
  }
  // a hit that lands also lifts something
  if (f.state === 'attack' && f.atk && f.atk.hit && f.atk.hit.has(p) && !f.stole) {
    f.stole = true;
    if (p.weapon) { p.weapon = null; popWord(p.x, p.y, 160, 'NICKED!', true); }
    else { addScore(-150, true); popWord(p.x, p.y, 160, 'DIPPED! -150', false); }
    sfx('pickup');
  }
  if (f.state !== 'attack') f.stole = false;
  // and when someone's holding you, he's straight in your pockets
  if (p.state === 'netted' && p.heldBy && p.heldBy.kind === 'grappler' && canBeHit(f) && Math.abs(p.x - f.x) < 140 && !(f.dipT > 0)) {
    f.dipT = 1.2; addScore(-100, true); popWord(p.x, p.y, 170, 'POCKETS!', false); sfx('pickup');
  }
  if (f.dipT > 0) f.dipT -= dt;
  return false;
}
// the Lookout: hangs back, lobs bottles, whistles more of them in
function nlLookout(f, dt) {
  f.whistleT = (f.whistleT == null ? rand(5, 8) : f.whistleT) - dt;
  if (f.state === 'whistle') { f.vx = f.vy = 0; if (f.t > 0.9) { f.state = 'hover'; f.t = 0; const k = pick(['dipper', 'grappler']); const n = spawnFoe(k, chance(0.5) ? 'R' : 'L'); foes.push(n); } return true; }
  if (f.whistleT <= 0 && canBeHit(f) && foes.filter(o => canBeHit(o) && !o.boss).length < 5 && ['hover', 'idle', 'walk', 'approach'].includes(f.state)) {
    f.whistleT = rand(8, 12); f.state = 'whistle'; f.t = 0; sfx('whistle'); popWord(f.x, f.y, 160, 'PHWEEEET!', false);
    if (f.token) releaseToken(f, 0.4);
    return true;
  }
  return false;
}
// the Jeweller: a chain whip with a long reach, a blinding flash off his watches, a grab and "what time is it?"
function nlJeweller(b, dt, rage) {
  const p = player, dx = Math.abs(p.x - b.x), dy = Math.abs(p.y - b.y);
  if (!b.calls) b.calls = 0;
  if (b.calls < 2 && b.hp < b.maxHp * (b.calls ? 0.35 : 0.65) && b.state !== 'beaten') { b.calls++; say(b, 'Lads! A bit of help.', 1.8, true); setTimeout0(() => { const g = [['dipper', 'R'], ['grappler', 'L']]; foes.push(...g.map(([t, s]) => spawnFoe(t, s))); }, 0.6); }
  switch (b.state) {
    case 'idle': case 'walk': {
      if (b.cool > 0 || !playerTargetable()) return false;
      const r = Math.random();
      if (dx < 200 && dy < 34 && r < 0.45) { b.state = 'whipWind'; b.t = 0; b.vx = b.vy = 0; return true; }
      if (dx < 120 && dy < 30 && r < 0.75) { b.state = 'grabWind'; b.t = 0; b.vx = b.vy = 0; return true; }
      if (dx > 150 && dx < 460 && r < 0.6) { b.state = 'glintWind'; b.t = 0; b.vx = b.vy = 0; say(b, 'Look at this.', 1.2, true); return true; }
      return false;
    }
    case 'whipWind':
      b.vx = b.vy = 0; if (dx > 8) b.face = Math.sign(p.x - b.x);
      if (b.t > 0.5 * D().wind) { b.state = 'whip'; b.t = 0; b.atkT = 0; b.atk = { t0: 0.05, t1: 0.22, reach: [0, 200], depth: 26, dmg: 12, kd: true, kb: 340, hs: 0.08, hit: new Set() }; sfx('swing'); }
      return true;
    case 'whip': if (b.t > 0.42) { b.atk = null; b.state = 'rest'; b.t = 0; } return true;
    case 'glintWind':
      b.vx = b.vy = 0; if (dx > 8) b.face = Math.sign(p.x - b.x);
      if (chance(dt * 20)) parts.push({ k: 'sparkle', x: b.x + b.face * 20, y: b.y, z: 90 + rand(0, 30), t: 0, life: 0.4 });
      if (b.t > 0.85 * D().wind) {
        b.state = 'glint'; b.t = 0; flashT = Math.max(flashT, 0.14); sfx('jackpot');
        // look away (face the other way) or be in the air to dodge it
        const looking = Math.sign(b.x - p.x) === p.face;
        if (looking && pHittable(40) && dx < 520 && !p.rage) { holdPlayer(b); p.blindT = 1.0; popWord(p.x, p.y, 170, 'BLINDED!', true); }
        else popWord(p.x, p.y, 150, p.rage ? 'NOT TODAY!' : 'LOOKED AWAY!', false);
      }
      return true;
    case 'glint':
      if (p.blindT > 0) { p.blindT -= dt; if (p.blindT <= 0 && p.state === 'netted' && p.heldBy === b) freePlayer(); }
      if (b.t > 0.4 && !(p.blindT > 0)) { b.state = 'rest'; b.t = 0; }
      return true;
    case 'grabWind':
      b.vx = b.vy = 0; if (dx > 8) b.face = Math.sign(p.x - b.x);
      if (b.t > 0.55 * D().wind) {
        b.state = 'grabLunge'; b.t = 0; b.vx = b.face * 420; sfx('swing');
      }
      return true;
    case 'grabLunge':
      if (canBeHit(p) && !(p.buffT > 0) && p.z < 20 && p.state !== 'netted' && Math.abs(p.x - b.x) < 70 && Math.abs(p.y - b.y) < 28) {
        b.vx = 0;
        if (p.rage) { popWord(p.x, p.y, 160, 'NOT TODAY!', true); b.state = 'rest'; b.t = 0; bDaze(b, 0.9, 'SHOVED!'); return true; }
        holdPlayer(b); b.state = 'grabHold'; b.t = 0; b.mash = 0; say(b, 'What time is it?', 1.4, true); sfx('grab');
      } else if (b.t > 0.4) { b.vx = 0; b.state = 'rest'; b.t = 0; }
      return true;
    case 'grabHold':
      b.vx = b.vy = 0;
      if (p.state !== 'netted' || p.heldBy !== b) { b.state = 'rest'; b.t = 0; return true; }
      p.x = b.x + b.face * 44; p.y = b.y + 2; p.face = -b.face;
      if (pressed.has('punch') || pressed.has('jump') || pressed.has('left') || pressed.has('right') || taps.length) b.mash++;
      if (b.mash >= 9) { freePlayer(); popWord(p.x, p.y, 150, 'BROKE FREE!', false); bDaze(b, 0.8, 'OI!'); return true; }
      if (b.t > 1.2) { freePlayer(); say(b, 'Time to go.', 1.2, true); hitP(b, 13, b.face, true, 460); b.state = 'rest'; b.t = 0; }
      return true;
  }
  return false;
}

// ================================================================== the N47
function nlBusTick(dt) {
  if (S.busT == null) { S.busT = 0; S.lurchT = rand(9, 13); S.stopN = 0; S.trainV = 520; }
  S.busT += dt; S.scrollX += S.trainV * dt;
  // the bus brakes and swings round corners: a warning, then everyone goes flying one way
  S.lurchT -= dt;
  if (S.lurchT < 1 && !S.lurchWarn) { S.lurchWarn = Math.random() < 0.5 ? 1 : -1; nlAnnounce(S.lurchWarn > 0 ? 'HOLD ON! (BRAKING)' : 'HOLD ON! (CORNER)', 1.2); sfx('honk'); }
  if (S.lurchT <= 0) {
    const dir = S.lurchWarn || 1; S.lurchWarn = 0; S.lurchT = rand(9, 14);
    addShake(9); sfx('heavy');
    for (const e of (NET.on ? PL : [player]).concat(foes.filter(f => !f.boss && canBeHit(f)))) {
      if (e.z > 0) continue;
      const mine = e === player || PL.includes(e);
      e.vx += dir * (mine ? 420 : 640);
      if (!mine && chance(0.5)) knockDown(e, dir, 260);
    }
    if (dir > 0) S.trainV = 160; else S.trainV = 380;
  }
  S.trainV += (520 - S.trainV) * Math.min(1, dt * 0.6);
  // the stops go by at the front, one per wave
  if (S.lastWaveIdx !== S.waveIdx) { S.lastWaveIdx = S.waveIdx; const stops = ['TRAFALGAR SQUARE', 'ELEPHANT & CASTLE', 'NEW CROSS', 'LEWISHAM', 'CATFORD', 'BROMLEY', 'PETTS WOOD', 'ORPINGTON']; S.busStop = stops[Math.min(stops.length - 1, S.waveIdx)]; if (S.waveIdx > 0) nlAnnounce(S.busStop, 2.6); }
}
// Smiler, on the back seat: wakes up, and looks after you
function nlSmiler() {
  S.wave = null; S.waveIdx++; S.waitT = 1.2;
  let sm = S.npcs.find(n => n.kind === 'smiler');
  if (!sm) { sm = makeNpc('smiler', 860, FT + 14); sm.face = -1; sm.def = FOES.smiler; S.npcs.push(sm); }
  sm.wake = 0;
  const lines = [['Here. You need this more than me.', 'Go on, son.'], ['Take it. And mind yourselves.', "They're not worth it. Here."]];
  const which = S.smilerN = (S.smilerN || 0) + 1;
  setTimeout0(() => { say(sm, pick(lines[(which - 1) % 2]), 2.2, true); sm.state = 'throw'; sm.t = 0; }, 0.4);
  setTimeout0(() => {
    const p = player, w = which === 1 ? 'pole' : 'alcopop';
    shots.push({ kind: 'gift', w, x: sm.x - 20, y: sm.y, z: 60, vx: (p.x - sm.x) / 0.8, vy: (p.y - sm.y) / 0.8, vz: 420, t: 0, face: -1, hit: new Set(), dmg: 0 });
    sfx('throw');
  }, 1.0);
  setTimeout0(() => { if (sm) sm.state = 'idle'; say(player, pick(['Cheers, mate!', 'You legend.', 'Thanks, Smiler!']), 1.8, true); }, 1.8);
}
// a thrown gift lands as a weapon at your feet
function nlGiftTick(s, dt) {
  s.t += dt; s.x += s.vx * dt; s.y += s.vy * dt; s.vz -= 1100 * dt; s.z += s.vz * dt;
  if (s.z <= 0) { s.dead = true; dropItemWeapon(s.w, s.x, s.y); sfx('pickup'); popWord(s.x, s.y, 90, 'CATCH!', false); }
  return true;
}

// ================================================================== drawing
const nlSnap = v => Math.round(v / 2) * 2;
function nlPut(k, wx, bottom, flip, k2) { const img = NLX.img(k); if (!img) return null; const s = k2 || 2, w = img.width * s, h = img.height * s, x = nlSnap(wx - cam.x); if (x > W + 20 || x + w < -20) return img; ctx.save(); ctx.imageSmoothingEnabled = false; if (flip) { ctx.translate(x + w, 0); ctx.scale(-1, 1); ctx.drawImage(img, 0, nlSnap(bottom - h), w, h); } else ctx.drawImage(img, x, nlSnap(bottom - h), w, h); ctx.restore(); return img; }
// a strip that repeats forever, scrolled by an offset of its own (scenery past a moving window)
function nlStrip(k, off, bottom, s) { const img = NLX.img(k); if (!img) return; const w = img.width * (s || 2), h = img.height * (s || 2); let x = -(((off % w) + w) % w); ctx.save(); ctx.imageSmoothingEnabled = false; for (; x < W; x += w) ctx.drawImage(img, nlSnap(x), nlSnap(bottom - h), w, h); ctx.restore(); }
function nlDrawStageBg(bg) {
  if (bg === 'nl_station') return nlBgStation();
  if (bg === 'nl_train') return nlBgTrain();
  if (bg === 'nl_cx') return nlBgCx();
  if (bg === 'nl_alley') return nlBgAlley();
  if (bg === 'nl_bus') return nlBgBus();
  return false;
}
function nlBgStation() {
  pxSky(['#0a0d22', '#121636', '#1b1a40', '#26203f', '#33263f', '#41293c'], 0, FT);
  // Station Approach outside, the ticket hall, the barriers, then the platform under the night sky
  for (let wx = -200; wx < 1080; wx += 640) nlPut('st_front', wx, FT + 4);
  for (let wx = 1080; wx < 2600; wx += 640) nlPut('st_hall', wx, FT + 4);
  for (let wx = 2600; wx < ST.len + 800; wx += 800) nlPut('st_platform', wx, FT + 4);
  pxFloor(0, ST.len, '#3b3d44', '#34363c', 40, 80, '#44464d');
  ctx.fillStyle = '#55575f'; ctx.fillRect(0, FT, W, 4);
  // the yellow line on the platform: stand behind it
  { const x = nlSnap(2600 - cam.x); if (x < W) { ctx.fillStyle = '#e8c23a'; ctx.fillRect(Math.max(0, x), FB - 18, W - Math.max(0, x), 4); } }
  // the barrier line the Inspector guards
  nlPut('cx_barrier', 2420, FT + 40);
  return true;
}
function nlBgTrain() {
  const sc = S.scrollX || 0, band = FT - 60;
  ctx.fillStyle = '#060814'; ctx.fillRect(0, 0, W, FT);
  // the world outside: suburbs at speed, a platform when we're stopped
  nlStrip('sc_suburb', sc * 0.9, band + 10);
  if (S.stopSeq || (S.platAt != null && S.platAt > sc - 1400)) {
    if (S.stopSeq && S.stopSeq.phase === 'brake' && S.platAt == null) S.platAt = sc + TRAIN.cruise;
    const pk = NLX.img('sc_platform');
    if (pk && S.platAt != null) {
      const w = pk.width * 2, x0 = nlSnap(S.platAt - sc - w / 2 + W / 2);
      ctx.save(); ctx.imageSmoothingEnabled = false; for (let x = x0 - w; x < x0 + w * 2; x += w) ctx.drawImage(pk, x, nlSnap(band + 10 - pk.height * 2), w, pk.height * 2);
      const name = S.stopSeq ? S.stopSeq.name : S.lastStop;
      if (name) { const nx = x0 + w / 2; ctx.fillStyle = '#123a8c'; ctx.fillRect(nx - 110, band - 150, 220, 34); ctx.fillStyle = '#efe6d2'; ctx.fillRect(nx - 110, band - 150, 220, 3); pxText(name, nx, band - 133, 16, '#ffffff'); }
      ctx.restore();
    }
    if (S.stopSeq) S.lastStop = S.stopSeq.name;
  }
  if (!S.stopSeq && S.platAt != null && S.platAt < sc - 1400) S.platAt = null;
  // the carriage: walls with see-through windows, doors, the end wall and the toilets
  for (let wx = Math.floor(cam.x / TRAIN.seg) * TRAIN.seg - TRAIN.seg; wx < cam.x + W + TRAIN.seg; wx += TRAIN.seg) nlPut('tr_wall', wx, FT + 6);
  for (let c = Math.max(0, Math.floor(cam.x / TRAIN.car) - 1); c * TRAIN.car < cam.x + W + TRAIN.car; c++) {
    for (const d of TRAIN.doors) nlDrawTrainDoor(c * TRAIN.car + d);
    nlPut('tr_end', c * TRAIN.car + TRAIN.car - 128, FT + 6);
  }
  // the toilets, every one out of order... nearly
  for (const [i, tx] of [1700, 1830, nlToiletX()].entries()) {
    const img = nlPut('tr_toilet', tx, FT + 6);
    if (img) { const x = nlSnap(tx - cam.x); const last = i === 2;
      if (last && (S.toilet === 3)) { ctx.fillStyle = '#11131a'; ctx.fillRect(x + 8, FT + 6 - img.height * 2 + 16, img.width * 2 - 16, img.height * 2 - 20); nlPut('toilet_guy', tx + 2, FT + 2); }
      else { ctx.fillStyle = '#efe6d2'; ctx.fillRect(x + 14, FT - 170, img.width * 2 - 28, 22); pxText('OUT OF ORDER', x + img.width, FT - 159, 9, '#b8231a'); } }
  }
  pxFloor(0, ST.len, '#2b2f3a', '#262a33', 36, 64, '#323744');
  ctx.fillStyle = '#c9a227'; ctx.fillRect(0, FT, W, 4);
  return true;
}
function nlDrawTrainDoor(wx) {
  // a doorway in the carriage side: the frame, what's outside, and two leaves that slide apart into the wall
  const fr = NLX.img('tr_doorframe'), img = NLX.img('tr_door'); if (!fr || !img) return;
  const x = nlSnap(wx - cam.x), w = fr.width * 2, h = fr.height * 2, y = nlSnap(FT + 6 - h);
  if (x > W + 10 || x + w < -10) return;
  const open = (S.doorOpen || 0) * 0.95, wind = S.doorWind && Math.abs(S.windX - wx - w / 2) < w ? S.doorWind : 0, o = Math.max(open, wind);
  const ox = x + 6, oy = y + 62, ow = img.width * 2, oh = img.height * 2, stopped = S.trainV < 50 && S.stopSeq;
  ctx.save(); ctx.imageSmoothingEnabled = false;
  ctx.fillStyle = stopped ? '#1a2340' : '#07091a'; ctx.fillRect(ox, oy, ow, oh);
  if (stopped) { ctx.fillStyle = '#56535a'; ctx.fillRect(ox, oy + oh - 46, ow, 46); ctx.fillStyle = '#e8c23a'; ctx.fillRect(ox, oy + oh - 46, ow, 3); }
  else if (o > 0) { ctx.fillStyle = '#0d1226'; for (let i = 0; i < 4; i++) { const sx = ox + ((i * 53 - (S.scrollX || 0) * 1.4) % ow + ow) % ow; ctx.fillRect(sx, oy + 30 + i * 37, 26, 2); } }
  ctx.drawImage(fr, x, y, w, h);
  ctx.beginPath(); ctx.rect(ox, oy, ow, oh); ctx.clip();
  const half = img.width / 2, slide = Math.round(ow / 2 * o / 2) * 2;
  ctx.drawImage(img, 0, 0, half, img.height, ox - slide, oy, ow / 2, oh);
  ctx.drawImage(img, half, 0, half, img.height, ox + ow / 2 + slide, oy, ow / 2, oh);
  ctx.restore();
}
function nlBgCx() {
  pxSky(['#0b0d1e', '#111430', '#181a3a'], 0, FT);
  for (let wx = -100; wx < ST.len + 640; wx += 640) nlPut('cx_hall', wx, FT + 4);
  pxFloor(0, ST.len, '#4a4c55', '#43454d', 48, 96, '#53555e');
  ctx.fillStyle = '#6c6e78'; ctx.fillRect(0, FT, W, 4);
  // the ticket barriers across the end of the concourse, and the way out to the Strand
  nlPut('cx_barrier', ST.len - 560, FT + 40); nlPut('cx_barrier', ST.len - 304, FT + 40);
  return true;
}
function nlBgAlley() {
  pxSky(['#07080f', '#0c0e1a', '#121423'], 0, FT);
  for (let wx = -120; wx < ST.len + 640; wx += 640) nlPut('alley', wx, FT + 4);
  pxFloor(0, ST.len, '#2c2a2c', '#262426', 32, 72, '#353234');
  ctx.fillStyle = '#3d3a3c'; ctx.fillRect(0, FT, W, 4);
  return true;
}
function nlBgBus() {
  const sc = S.scrollX || 0, band = FT - 40;
  ctx.fillStyle = '#05070f'; ctx.fillRect(0, 0, W, FT);
  nlStrip('sc_highst', sc, band);
  // Marc, walking home, now and then
  { const per = 5200, ph = ((sc * 0.6) % per + per) % per; if (ph < 1400 && !(NET.on ? PL : [player]).some(q => q.def.id === 'marc')) { const sh = ladSprite('marc'); if (sh && sh.ready) { const m = sh.m, row = m.rows.walk, f = 1 + Math.floor(time * 10) % (row[1] - 1), x = W + 80 - ph * 0.8; ctx.save(); ctx.imageSmoothingEnabled = false; ctx.translate(nlSnap(x), band - 6); ctx.scale(-1, 1); ctx.drawImage(sh.img, f * m.cell, row[0] * m.cell, m.cell, m.cell, -m.ax, -m.ay, m.cell, m.cell); ctx.restore(); } } }
  for (let wx = -40; wx < W + 640; wx += 640) nlPut('bus_deck', wx, FT + 6);
  nlPut('bus_stairs', 20, FT + 6);
  pxFloor(0, W, '#3a2c2e', '#33272a', 30, 60, '#42343a');
  ctx.fillStyle = '#c9a227'; ctx.fillRect(0, FT, W, 4);
  // the stops strip
  ctx.fillStyle = '#0b0b10'; ctx.fillRect(W / 2 - 170, 70, 340, 26); ctx.fillStyle = '#c9a227'; ctx.fillRect(W / 2 - 170, 94, 340, 2);
  pxText('N47 → ' + (S.busStop || 'TRAFALGAR SQUARE'), W / 2, 83, 12, '#ffb04a');
  return true;
}
let nlWatchFx = null;
function nlDrawFore() {
  if (!ST || ST.era !== 2006) return;
  // grab poles in front of everyone on the train and the bus
  if (ST.train) for (let wx = Math.floor(cam.x / 320) * 320 + 160; wx < cam.x + W + 320; wx += 320) { const x = nlSnap(wx - cam.x); if (wx % TRAIN.car < 1800) { ctx.fillStyle = '#1b1606'; ctx.fillRect(x - 3, 0, 8, H); ctx.fillStyle = '#e8c23a'; ctx.fillRect(x - 2, 0, 5, H); ctx.fillStyle = '#fff2a0'; ctx.fillRect(x - 1, 0, 1, H); } }
  if (S && S.ann) {
    const a = S.ann, k = Math.min(1, a.t / 0.15, (a.life - a.t) / 0.25);
    ctx.save(); ctx.globalAlpha = Math.max(0, k);
    const w = Math.max(320, a.text.length * 12 + 60), x = W / 2 - w / 2, y = 112;
    ctx.fillStyle = '#050505'; ctx.fillRect(x, y, w, 30); ctx.fillStyle = '#2a2a2a'; ctx.fillRect(x, y, w, 2); ctx.fillRect(x, y + 28, w, 2);
    // a dot-matrix scroll if it's long
    pxText(a.text, W / 2, y + 15, 12, '#ff9a1a');
    ctx.restore();
  }
  if (S && S.traf) nlDrawTrafalgar();
  // Seb's watch, back where it belongs: it rises over his head and catches the light
  // (kept out of S: it's only a picture, timed by the screen, so it can't knock online co-op out of step)
  if (nlWatchFx) { const w = nlWatchFx, img = NLX.img('watch'); w.t += 1 / 60;
    if (w.t > 2.6 || !img || !S) nlWatchFx = null;
    else { const k = Math.min(1, w.t / 0.4), x = nlSnap(w.who.x - cam.x - 110), y = nlSnap(w.who.y - 150 - k * 24 + Math.sin(w.t * 5) * 3);
      ctx.save(); ctx.imageSmoothingEnabled = false; ctx.globalAlpha = Math.min(1, (2.6 - w.t) / 0.4); ctx.filter = 'brightness(1.6)'; ctx.drawImage(img, x, y, 64, 64); ctx.filter = 'none';
      if (Math.floor(w.t * 8) % 3 === 0) { ctx.fillStyle = '#ffffff'; ctx.fillRect(x + 40, y + 14, 4, 12); ctx.fillRect(x + 36, y + 18, 12, 4); }
      ctx.restore(); } }
}
