// ================================================================== ORPINGTON 2001: THE CROWD (Version 76)
// Ten locals with sprites of their own (PixelLab: tools/v76/pixellab_ids.md; sheets: tools/v76/foe_sheets.py), each with a
// move nobody else in the game has. They play in a group the way the 1999 and 2006 crowds do (nlStyle: flanking, piling in
// when you're held, one big move at a time so each one can be read), then add their own on top (orpCrowd, below).
//   street:    KAPPA KID, RAZOR KID, FROSTED TIPS, SCRUNCHIE, GARAGE MC (the Petts Wood lot)
//   the pub:   THE BUILDER, THE OLD BOY, POOL SHARK
//   Atlantis:  MOSCHINO, RAVER (and the MC again)
Object.assign(FOES, {
  kappa: { name: 'KAPPA KID', hp: 40, speed: 146, dmg: 6, reach: 62, windup: 0.3, score: 220, ai: 'melee', grab: true, aa: true, combo2: true,
    lines: ['Poppers, innit.', 'Petts Wood, bruv!', "What you sayin'?", 'These are brand new, these.'] },
  razor: { name: 'RAZOR KID', hp: 30, speed: 150, dmg: 5, reach: 56, windup: 0.3, score: 220, ai: 'melee', grab: true, aa: true,
    lines: ['Mind out!', 'Got it for Christmas.', "My mum's gonna kill me.", 'Coming through!'] },
  frosted: { name: 'FROSTED TIPS', hp: 46, speed: 132, dmg: 7, reach: 64, windup: 0.36, score: 260, ai: 'melee', grab: true, aa: true,
    lines: ['Mind the hair!', 'I nearly got on Popstars, me.', 'Took an hour, this.', 'Boyband, mate. Boyband.'] },
  scrunchie: { name: 'SCRUNCHIE', hp: 32, speed: 156, dmg: 6, reach: 60, windup: 0.28, score: 240, ai: 'melee', grab: true, aa: true, combo2: true,
    lines: ['Are you starting?', "I'll ring my brother.", 'Whatever.', 'Talk to the hand.'] },
  garagemc: { name: 'GARAGE MC', hp: 46, speed: 112, dmg: 6, reach: 62, windup: 0.4, score: 300, ai: 'melee', grab: true,
    lines: ['Big up Petts Wood!', 'Rewind!', 'Bo! Bo! Bo!', 'Hold tight the Orpington massive.'] },
  builder: { name: 'THE BUILDER', hp: 96, speed: 88, dmg: 12, reach: 76, windup: 0.55, score: 380, ai: 'melee', armor: true, grab: true,
    lines: ["'Ave it!", 'Cash in hand, mate.', "I've been on the tools since six.", 'Mind the van.'] },
  codger: { name: 'THE OLD BOY', hp: 40, speed: 70, dmg: 8, reach: 62, windup: 0.5, score: 340, ai: 'melee', armor: true, grab: true,
    lines: ['In my day we fought fair.', "I've been drinking here since 1962.", 'Mind my pint!', 'Young people.'] },
  shark: { name: 'POOL SHARK', hp: 46, speed: 116, dmg: 8, reach: 110, windup: 0.42, score: 320, ai: 'melee', grab: true,
    lines: ['Winner stays on.', 'Fiver a frame?', 'Chalk.', 'Off the black.'] },
  moschino: { name: 'MOSCHINO', hp: 54, speed: 120, dmg: 8, reach: 68, windup: 0.42, score: 340, ai: 'melee', grab: true,
    lines: ['Bottle service, innit.', 'Do you know who I am?', 'VIP, bruv.', 'Pop the cork!'] },
  raver: { name: 'RAVER', hp: 34, speed: 172, dmg: 5, reach: 60, windup: 0.26, score: 260, ai: 'melee', grab: true, aa: true,
    lines: ['PHWEEEEP!', 'Tune!', 'Have it!', "Lovin' it, lovin' it."] },
});
const ORP_CROWD = ['kappa', 'razor', 'frosted', 'scrunchie', 'garagemc', 'builder', 'codger', 'shark', 'moschino', 'raver'];
for (const k of ORP_CROWD) FOES[k].extra = (f, dt) => nlStyle(f, dt) || orpCrowd(f, dt);
ASSET_BG.push('orp/scooter', 'orp/stool', 'orp/n3310'); ['orp/scooter', 'orp/stool', 'orp/n3310'].forEach(k => bgImg(k));

// a foe's moves start from here: stood off, nothing else big going on, the player there to be hit
const ocFree = f => nlFree(f) && playerTargetable() && nlSpecialOk();
const ocBusy = f => ['down', 'getup', 'dead', 'thrown', 'grabbed', 'beaten', 'hurt', 'stunned'].includes(f.state);
const ocFx = () => (S.ocFx = S.ocFx || []);
// the rest of the room as targets for the moves that hit everyone (the barge, the balls): players and the other foes
const ocAll = f => players().concat(foes.filter(o => o !== f && !o.boss && canBeHit(o)));

function orpCrowd(f, dt) {
  const p = player, d = f.def, dx = Math.abs(p.x - f.x), dy = Math.abs(p.y - f.y);
  if (f.dazedT > 0) f.dazedT -= dt;
  switch (f.kind) {
    case 'kappa': {
      // KAPPA KID: pops his trackies off by the poppers and cracks them like a whip, from well outside punching range
      if (f.state === 'whipWind') { f.vx = f.vy = 0; if (f.t > 0.45) { f.state = 'whip'; f.t = 0; nlStrike(f, 150, d.dmg + 5, true, 320, 0.22); } return nlOwn(f, dt); }
      if (f.state === 'whip') {
        if (!f.cracked && f.t > 0.1) { f.cracked = true; sfx('dart'); popWord(f.x + f.face * 120, f.y, 140, 'CRACK!', false); }
        if (nlHits(f) && !f.trackied) { f.trackied = true; popWord(p.x, p.y, 160, 'TRACKIED!', true); }
        if (f.t > 0.42) { f.atk = null; f.state = 'recover'; f.t = 0; f.cracked = f.trackied = false; }
        return nlOwn(f, dt);
      }
      f.whipCool = (f.whipCool == null ? 1.5 : f.whipCool) - dt;
      if (ocFree(f) && f.whipCool <= 0 && dx > 90 && dx < 170 && dy < 24 && chance(dt * 2.2)) {
        f.whipCool = rand(3.5, 5.5); nlStartSpecial(f, 'whipWind'); popWord(f.x, f.y, 150, 'POPPERS!', true); sfx('break'); return nlOwn(f, dt);
      }
      return false;
    }
    case 'razor': return orpRazor(f, dt, p, d, dx, dy);
    case 'frosted': {
      // FROSTED TIPS: a spinning roundhouse that catches both sides, a knee slide along the floor (jump it), and he stops
      // to check his hair the first time you catch him in the face: hit him then, it does half as much again
      if (f.state === 'spinKickWind') { f.vx = f.vy = 0; if (f.t > 0.28) { f.state = 'spinKick'; f.t = 0; f.atkT = 0; f.atk = { t0: 0.06, t1: 0.34, reach: [-74, 98], depth: 26, dmg: d.dmg + 3, kd: true, kb: 300, hs: 0.07, hit: new Set(), zMax: 90 }; sfx('swing'); } return nlOwn(f, dt); }
      if (f.state === 'spinKick') { if (f.t > 0.5) { f.atk = null; f.state = 'recover'; f.t = 0; } return nlOwn(f, dt); }
      if (f.state === 'kneeSlideWind') { f.vx = f.vy = 0; if (f.t > 0.3) { f.state = 'kneeSlide'; f.t = 0; f.vx = f.face * 520; f.atkT = 0; f.atk = { t0: 0, t1: 0.55, reach: [-6, 58], depth: 20, dmg: d.dmg, kd: true, kb: 220, hs: 0.06, hit: new Set(), zMax: 16 }; sfx('swing'); dust(f.x, f.y, 3, 30); } return nlOwn(f, dt); }
      if (f.state === 'kneeSlide') { if (chance(0.5)) dust(f.x - f.face * 16, f.y, 1, 16); friction(f, dt, 0.3); if (f.t > 0.55 || nlHits(f)) { f.atk = null; f.state = 'pose'; f.t = 0; f.vx = 0; popWord(f.x, f.y, 150, pick(['KEY CHANGE!', 'BOYBAND!', 'WOOO!']), false); } return nlOwn(f, dt); }
      if (f.state === 'pose' || f.state === 'preen') { f.vx = f.vy = 0; if (f.t > (f.state === 'pose' ? 0.7 : 1.1)) { f.state = 'hover'; f.t = 0; f.dazedT = 0; } return nlOwn(f, dt); }
      // the hair
      if (f.state === 'hurt' && f._was !== 'hurt' && !f.preened && f.hp > f.maxHp * 0.3) {
        f.preened = true; f.state = 'preen'; f.t = 0; f.dazedT = 1.1; f.vx = 0; say(f, pick(['MY HAIR!', 'Not the tips!', 'Do you know how long this took?']), 1.3, true); f._was = 'preen'; return nlOwn(f, dt);
      }
      f._was = f.state;
      if (ocFree(f) && dy < 22) {
        if (dx < 120 && chance(dt * 1.4)) { nlStartSpecial(f, 'spinKickWind'); return nlOwn(f, dt); }
        if (dx > 130 && dx < 280 && chance(dt * 1.0)) { nlStartSpecial(f, 'kneeSlideWind'); return nlOwn(f, dt); }
      }
      return false;
    }
    case 'scrunchie': return orpScrunchie(f, dt, p, d, dx, dy);
    case 'garagemc': {
      // GARAGE MC: gets on the mic. Three waves of sound roll out in front of him: they shove you back across the floor,
      // and the first one dizzies you if you're close. Every time he spits, his mates go faster. Get behind him.
      if (f.state === 'barsWind') { f.vx = f.vy = 0; if (f.t > 0.55) { f.state = 'bars'; f.t = 0; f.rings = 0; sfx('airhorn'); orpHype(f); } return nlOwn(f, dt); }
      if (f.state === 'bars') {
        f.vx = f.vy = 0;
        if (f.t > f.rings * 0.4 && f.rings < 3) { f.rings++; ocFx().push({ k: 'ring', x: f.x + f.face * 30, y: f.y, face: f.face, r: 0, t: 0, n: f.rings, from: f, hit: new Set() }); if (f.rings === 1) popWord(f.x, f.y, 170, pick(['BO! BO!', 'REWIND!', 'BIG UP!']), true); }
        if (f.t > 1.4) { f.state = 'recover'; f.t = 0; }
        return nlOwn(f, dt);
      }
      f.barsCool = (f.barsCool == null ? 2 : f.barsCool) - dt;
      if (ocFree(f) && f.barsCool <= 0 && dx < 300 && dy < 46 && chance(dt * 1.2)) { f.barsCool = rand(5, 7); nlStartSpecial(f, 'barsWind'); say(f, pick(d.lines), 1.2, true); return nlOwn(f, dt); }
      return false;
    }
    case 'builder': return orpBuilder(f, dt, p, d, dx, dy);
    case 'codger': {
      // THE OLD BOY: slow, hard as nails (punches don't stop him), and that walking stick reaches. He hooks you round the
      // neck from across the room, reels you in and gives you a dig. Mash to get out of the crook.
      if (f.state === 'hookWind') { f.vx = f.vy = 0; if (f.t > 0.5) { f.state = 'hookOut'; f.t = 0; sfx('swing'); } return nlOwn(f, dt); }
      if (f.state === 'hookOut') {
        if (f.t > 0.06 && !f.hooked) {
          const ahead = (p.x - f.x) * f.face; f.hooked = true;
          if (ahead > 30 && ahead < 220 && dy < 24 && pHittable(30) && !p.rage) { holdPlayer(f); f.state = 'crook'; f.t = 0; f.mash = 0; sfx('grab'); popWord(p.x, p.y, 160, 'HOOKED!', true); say(f, pick(["Come 'ere, you.", 'Gotcha.', 'Not so fast, sonny.']), 1.3, true); S.nlGangT = 1.6; return nlOwn(f, dt); }
        }
        if (f.t > 0.4) { f.state = 'recover'; f.t = 0; f.hooked = false; }
        return nlOwn(f, dt);
      }
      if (f.state === 'crook') {
        f.vx = f.vy = 0;
        if (p.state !== 'netted' || p.heldBy !== f) { f.state = 'recover'; f.t = 0; f.hooked = false; return nlOwn(f, dt); }
        const tx = f.x + f.face * 44; p.x += (tx - p.x) * Math.min(1, dt * 7); p.y += (f.y - p.y) * Math.min(1, dt * 7); p.face = -f.face;
        if (pressed.has('punch') || pressed.has('jump') || pressed.has('left') || pressed.has('right') || taps.length) { f.mash = (f.mash || 0) + 1; p.flash = 0.05; }
        if (f.mash >= 5) { freePlayer(); f.state = 'recover'; f.t = 0; f.hooked = false; popWord(p.x, p.y, 150, 'SLIPPED IT!', false); return nlOwn(f, dt); }
        if (f.t > 0.6) { freePlayer(); f.hooked = false; f.state = 'dig'; f.t = 0; nlStrike(f, d.reach + 10, d.dmg + 4, true, 300); popWord(p.x, p.y, 160, 'A DIG!', true); }
        return nlOwn(f, dt);
      }
      if (f.state === 'dig') { if (f.t > 0.35) { f.atk = null; f.state = 'recover'; f.t = 0; } return nlOwn(f, dt); }
      if (ocBusy(f)) nlHeldFree(f);
      f.hookCool = (f.hookCool == null ? 1.5 : f.hookCool) - dt;
      if (ocFree(f) && f.hookCool <= 0 && dx > 70 && dx < 210 && dy < 22 && chance(dt * 1.6)) { f.hookCool = rand(4, 6); nlStartSpecial(f, 'hookWind'); return nlOwn(f, dt); }
      return false;
    }
    case 'shark': {
      // POOL SHARK: a cue jab with twice anyone's reach, and the break: three balls along the floor in a spread. Jump them or
      // step between them. They flatten his own lot as well.
      if (f.state === 'breakWind') { f.vx = f.vy = 0; if (f.t < 0.3 && chance(dt * 10)) parts.push({ k: 'puff', x: f.x + f.face * 40, y: f.y, z: 60, vx: 0, vy: 0, vz: 10, t: 0, life: 0.4, r: 4 }); if (f.t > 0.62) { f.state = 'breakShot'; f.t = 0; orpBreak(f); } return nlOwn(f, dt); }
      if (f.state === 'breakShot') { if (f.t > 0.45) { f.state = 'recover'; f.t = 0; } return nlOwn(f, dt); }
      f.breakCool = (f.breakCool == null ? 2.5 : f.breakCool) - dt;
      if (ocFree(f) && f.breakCool <= 0 && dx > 160 && dx < 460 && dy < 60 && chance(dt * 1.2)) { f.breakCool = rand(5, 7); nlStartSpecial(f, 'breakWind'); say(f, pick(['Chalk.', 'Rack em up.', 'Break.']), 1, true); return nlOwn(f, dt); }
      return false;
    }
    case 'moschino': {
      // MOSCHINO: shakes the champagne (the fizz is the warning) and sprays it in your face. Caught facing him, you're
      // blinded: held a moment, slowed, and the screen fizzes. Turn your back on him, or get out of line.
      if (f.state === 'shakeWind') {
        f.vx = f.vy = 0; if (Math.abs(p.x - f.x) > 6) f.face = Math.sign(p.x - f.x);
        if (chance(dt * 18)) parts.push({ k: 'puff', x: f.x + f.face * 22 + rand(-6, 6), y: f.y, z: 78 + rand(-6, 10), vx: rand(-20, 20), vy: 0, vz: rand(30, 80), t: 0, life: 0.35, r: 3 });
        if (f.t > 0.85) { f.state = 'spray'; f.t = 0; sfx('hiss'); f.sprayed = false; }
        return nlOwn(f, dt);
      }
      if (f.state === 'spray') {
        f.vx = f.vy = 0;
        if (chance(0.9)) ocFx().push({ k: 'foam', x: f.x + f.face * 34, y: f.y, z: 74, vx: f.face * rand(380, 560), vy: rand(-50, 50), vz: rand(-40, 90), t: 0, life: rand(0.3, 0.45) });
        if (!f.sprayed && f.t > 0.1) {
          f.sprayed = true;
          const ahead = (p.x - f.x) * f.face, looking = p.face === -f.face;
          if (ahead > 0 && ahead < 190 && dy < 34 && looking && pHittable(40) && !p.rage) { holdPlayer(f); p.slowT = 2.6; S.ocFizz = 2.4; f.blinded = 0.8; popWord(p.x, p.y, 170, "MOËT'D!", true); }
          else popWord(p.x, p.y, 150, ahead > 0 && ahead < 190 && dy < 34 ? 'LOOKED AWAY!' : 'MISSED!', false);
        }
        if (f.blinded > 0) { f.blinded -= dt; if (f.blinded <= 0 && p.state === 'netted' && p.heldBy === f) freePlayer(); }
        if (f.t > 0.75 && !(f.blinded > 0)) { f.state = 'recover'; f.t = 0; }
        return nlOwn(f, dt);
      }
      if (ocBusy(f)) { f.blinded = 0; nlHeldFree(f); }
      f.sprayCool = (f.sprayCool == null ? 2 : f.sprayCool) - dt;
      if (ocFree(f) && f.sprayCool <= 0 && dx > 70 && dx < 170 && dy < 26 && chance(dt * 1.6)) { f.sprayCool = rand(5, 7); nlStartSpecial(f, 'shakeWind'); say(f, pick(['Pop the cork!', 'Celebrate, innit!', 'On me!']), 1.2, true); return nlOwn(f, dt); }
      return false;
    }
    case 'raver': {
      // RAVER: a flurry of glowstick punches; on the dance floor he only throws them on the beat. His whistle sets the
      // dancers round him off early, and off the floor it rings your ears if you're close.
      const ph = orpBeatPhase();
      if (f.state === 'windup' && ph >= 0 && f.t > d.windup && ph > 0.12 && ph < 0.88) { f.t = d.windup - 0.01; }   // hold it for the beat
      if (f.state === 'windup' && !f.flurryTried) { f.flurryTried = true; if (chance(0.55)) { nlStartSpecial(f, 'flurryWind', 0.5); return nlOwn(f, dt); } }
      if (f.state !== 'windup') f.flurryTried = false;
      if (f.state === 'flurryWind') { f.vx = f.vy = 0; if (f.t > 0.22 && (ph < 0 || ph < 0.12 || ph > 0.88)) { f.state = 'flurry'; f.t = 0; f.n = 0; nlStrike(f, d.reach, d.dmg - 1, false, 70); } return nlOwn(f, dt); }
      if (f.state === 'flurry') {
        const step = Math.floor(f.t / 0.14);
        if (step > f.n && step < 4) { f.n = step; f.vx = f.face * 70; nlStrike(f, d.reach + 6, step === 3 ? d.dmg + 3 : d.dmg - 1, step === 3, step === 3 ? 300 : 70); }
        friction(f, dt, 0.01);
        if (f.t > 0.7) { f.atk = null; f.state = 'recover'; f.t = 0; }
        return nlOwn(f, dt);
      }
      if (f.state === 'whistleWind') { f.vx = f.vy = 0; if (f.t > 0.4) { f.state = 'whistle'; f.t = 0; orpWhistle(f); } return nlOwn(f, dt); }
      if (f.state === 'whistle') { f.vx = f.vy = 0; if (f.t > 0.6) { f.state = 'recover'; f.t = 0; } return nlOwn(f, dt); }
      f.whistleCool = (f.whistleCool == null ? rand(3, 5) : f.whistleCool) - dt;
      if (nlFree(f) && nlSpecialOk() && f.whistleCool <= 0 && (S.dance || dx < 110) && chance(dt * 1.0)) { f.whistleCool = rand(7, 10); nlStartSpecial(f, 'whistleWind', 0.5); return nlOwn(f, dt); }
      return false;
    }
  }
  return false;
}

// ---------------------------------------------------------------- the Razor Kid and his scooter
// Far off, he rides it straight through you along his line (step out of it). Middling distance, he kicks it at you along the
// floor (jump it), then has to go and fetch it. Knock him off it and it's a wipeout.
function orpScooterFor(f) {
  if (f.scooter && !f.scooter.remove) return f.scooter;
  const n = makeNpc('scooter', f.x, f.y + 1); n.hp = 0; n.mode = 'held'; n.owner = f; n.draw = orpDrawScooter; n.face = f.face;
  n.script = orpScooterTick; S.npcs.push(n); f.scooter = n; return n;
}
function orpRazor(f, dt, p, d, dx, dy) {
  if (f.scooter === undefined) orpScooterFor(f);
  const sc = f.scooter;
  // knocked off it mid-ride
  if (f.riding && ocBusy(f) && sc) {
    f.riding = false; sc.mode = 'slide'; sc.vx = f.face * 380; sc.hit = new Set(); sc.owner = null; f.scooter = null; f.lost = sc;
    popWord(f.x, f.y, 160, 'WIPEOUT!', true); f.hp -= 6; sfx('break');
  }
  if (f.state === 'rideWind') { f.vx = f.vy = 0; if (f.t > 0.4) { f.state = 'ride'; f.t = 0; f.riding = true; sfx('brrap'); f.atkT = 0; f.atk = { t0: 0, t1: 1.3, reach: [-8, 52], depth: 20, dmg: d.dmg + 5, kd: true, kb: 360, hs: 0.07, hit: new Set(), zMax: 30 }; } return nlOwn(f, dt); }
  if (f.state === 'ride') {
    f.vx = f.face * 560; f.vy = 0; if (chance(0.3)) dust(f.x - f.face * 20, f.y, 1, 14);
    const past = (f.x - p.x) * f.face > 170, edge = f.x < cam.x + 30 || f.x > cam.x + W - 30;
    if (f.t > 1.3 || past || edge || nlHits(f)) { f.atk = null; f.riding = false; f.state = 'recover'; f.t = 0; f.vx *= 0.25; if (nlHits(f)) popWord(p.x, p.y, 160, 'RUN OVER!', true); }
    return nlOwn(f, dt);
  }
  if (f.state === 'kickWind') { f.vx = f.vy = 0; if (f.t > 0.38 && sc) { f.state = 'kick'; f.t = 0; sfx('swing'); sc.mode = 'slide'; sc.owner = null; sc.vx = f.face * 640; sc.x = f.x + f.face * 30; sc.y = f.y; sc.hit = new Set(); f.scooter = null; f.lost = sc; } return nlOwn(f, dt); }
  if (f.state === 'kick') { if (f.t > 0.3) { f.state = 'fetch'; f.t = 0; } return nlOwn(f, dt); }
  if (f.state === 'fetch') {
    // off to get it back; you can hit him on the way, and he'll stop to fight if you're on top of him
    const s = f.lost;
    if (!s || s.remove) { f.state = 'hover'; f.t = 0; f.lost = null; return nlOwn(f, dt); }
    if (s.mode !== 'rest') { f.vx = f.vy = 0; return nlOwn(f, dt); }
    if (moveToward(f, s.x, s.y, d.speed, dt) || (Math.abs(f.x - s.x) < 14 && Math.abs(f.y - s.y) < 10)) { s.mode = 'held'; s.owner = f; f.scooter = s; f.lost = null; f.state = 'hover'; f.t = 0; f.rideCool = 1.5; }
    else if (Math.abs(f.vx) > 4) f.face = Math.sign(f.vx);
    if (f.t > 4) { f.state = 'hover'; f.t = 0; f.lost = null; }
    return nlOwn(f, dt);
  }
  if (f.lost && !f.scooter && f.state === 'hover') { f.state = 'fetch'; f.t = 0; return nlOwn(f, dt); }   // after a wipeout
  if (!f.scooter && !f.lost && f.state === 'hover' && f.t > 0.5) f.scooter = orpScooterFor(f);   // a new one (it rolled off)
  f.rideCool = (f.rideCool == null ? 1.2 : f.rideCool) - dt;
  if (f.scooter && ocFree(f) && f.rideCool <= 0) {
    if (dx > 240 && dx < 560 && dy < 16 && chance(dt * 2.2)) { f.rideCool = rand(3, 4.5); nlStartSpecial(f, 'rideWind'); popWord(f.x, f.y, 140, 'RAZOR!', false); return nlOwn(f, dt); }
    if (dx > 120 && dx < 260 && dy < 20 && chance(dt * 1.2)) { f.rideCool = rand(4, 6); nlStartSpecial(f, 'kickWind'); return nlOwn(f, dt); }
    // line up for a run
    if (f.state === 'hover' && dx > 240 && dy >= 16 && chance(dt * 2)) { f.hoverY = p.y; f.retarget = 1.2; }
  }
  return false;
}
function orpScooterTick(n, dt) {
  if (n.mode === 'held') {
    const f = n.owner; if (!f || f.remove || f.state === 'dead' || !foes.includes(f)) { n.mode = 'slide'; n.vx = (n.face || 1) * 120; n.owner = null; n.hit = new Set(); return; }
    n.face = f.face;
    if (f.riding || f.state === 'rideWind') { n.x = f.x + f.face * 4; n.y = f.y + 0.5; n.ride = true; }
    else { n.x = f.x - f.face * 18; n.y = f.y - 0.5; n.ride = false; }   // stood next to him, behind
    return;
  }
  if (n.mode === 'slide') {
    n.ride = false; n.x += n.vx * dt; n.vx *= Math.pow(0.35, dt); n.rot = (n.rot || 0) + dt;
    if (Math.abs(n.vx) > 160) for (const e of ocAll(null)) {
      if (n.hit.has(e) || e.z > 18 || e.kind === 'razor') continue;
      if (Math.abs(e.x - n.x) < 30 + (e.half || 20) * 0.5 && Math.abs(e.y - n.y) < 18) { n.hit.add(e); applyHit(n, e, { dmg: players().includes(e) ? 9 : 18, kd: true, kb: 300, hs: 0.06 }, Math.sign(n.vx) || 1); popWord(e.x, e.y, 140, players().includes(e) ? 'SCOOTERED!' : 'TAKEN OUT!', false); if (!players().includes(e)) addScore(200); }
    }
    if (n.x < cam.x - 60 || n.x > cam.x + W + 60) { n.remove = true; return; }
    if (Math.abs(n.vx) < 30) { n.mode = 'rest'; n.vx = 0; sfx('thud'); }
  }
}
function orpDrawScooter(n) {
  const img = bgImg('orp/scooter'); if (!img) return;
  const x = Math.round((n.x - cam.x) / 2) * 2, y = Math.round(n.y / 2) * 2;
  ctx.save(); ctx.imageSmoothingEnabled = false; ctx.translate(x, y); ctx.scale(n.face || 1, 1);
  if (n.mode === 'rest') ctx.rotate(-0.5);   // on its side
  ctx.drawImage(img, -img.width, -img.height * 2 + 2, img.width * 2, img.height * 2); ctx.restore();
}

// ---------------------------------------------------------------- Scrunchie's 3310
// Out in a straight line and back to her hand: it hits going and coming. Knock her down while it's out and it drops
// (the 3310 survives, obviously). Down to her last mates, she rings her brother. Once.
function orpScrunchie(f, dt, p, d, dx, dy) {
  if (f.state === 'throwWind') { f.vx = f.vy = 0; if (f.t > 0.42) { f.state = 'throwing'; f.t = 0; orpPhoneOut(f); } return nlOwn(f, dt); }
  if (f.state === 'throwing') { if (f.t > 0.3) { f.state = 'hover'; f.t = 0; f.cool = 0.5; } return nlOwn(f, dt); }
  if (f.state === 'callWind') {
    f.vx = f.vy = 0;
    if (f.t > 1.3) { f.state = 'hover'; f.t = 0; const b = spawnFoe(pick(['kappa', 'frosted']), chance(0.5) ? 'L' : 'R'); b.def = Object.assign({}, b.def, { name: 'HER BROTHER' }); foes.push(b); say(b, pick(['Who touched my sister?', 'Where is he?']), 1.8, true); sfx('incoming'); }
    return nlOwn(f, dt);
  }
  if (ocBusy(f) && f.phone && !f.phone.remove && f.phone.mode !== 'floor') { f.phone.mode = 'drop'; }
  f.throwCool = (f.throwCool == null ? 1.5 : f.throwCool) - dt;
  const phoneOut = f.phone && !f.phone.remove;
  if (!phoneOut && !f.called && nlFree(f) && foes.filter(o => canBeHit(o) && !o.boss && o.state !== 'dead').length <= 2 && chance(dt * 0.6)) {
    f.called = true; f.state = 'callWind'; f.t = 0; f.vx = f.vy = 0; say(f, pick(["I'm ringing my brother.", "Wait 'til my brother gets here."]), 1.6, true); sfx('page'); return nlOwn(f, dt);
  }
  if (!phoneOut && ocFree(f) && f.throwCool <= 0 && dx > 140 && dx < 380 && dy < 26 && chance(dt * 1.6)) { f.throwCool = rand(3.5, 5); nlStartSpecial(f, 'throwWind'); return nlOwn(f, dt); }
  return false;
}
function orpPhoneOut(f) {
  const n = makeNpc('n3310', f.x + f.face * 26, f.y + 0.5); n.hp = 0; n.mode = 'out'; n.owner = f; n.z = 78; n.vx = f.face * 600; n.x0 = n.x; n.hit = new Set(); n.rot = 0;
  n.draw = orpDrawPhone; n.script = orpPhoneTick; S.npcs.push(n); f.phone = n; sfx('throw');
}
function orpPhoneTick(n, dt) {
  const f = n.owner; n.rot += dt * 18;
  if (n.mode === 'out' || n.mode === 'back') {
    if (n.mode === 'out') { n.x += n.vx * dt; if (Math.abs(n.x - n.x0) > 300 || n.x < cam.x + 10 || n.x > cam.x + W - 10) { n.mode = 'back'; n.hit = new Set(); } }
    else {
      if (!f || !foes.includes(f) || ocBusy(f)) { n.mode = 'drop'; return; }
      const ddx = f.x + f.face * 20 - n.x, ddy = f.y - n.y, dd = Math.hypot(ddx, ddy) || 1;
      n.x += ddx / dd * 640 * dt; n.y += ddy / dd * 640 * dt;
      if (dd < 22) { n.remove = true; f.phone = null; return; }   // caught
    }
    for (const q of players()) {
      if (n.hit.has(q) || !canBeHit(q) || q.z > 60 || q.state === 'netted') continue;
      if (Math.abs(q.x - n.x) < q.half + 8 && Math.abs(q.y - n.y) < 22) { n.hit.add(q); applyHit(f || n, q, { dmg: 7, kd: false, kb: 120, hs: 0.05 }, Math.sign(q.x - n.x) || 1); popWord(q.x, q.y, 150, n.mode === 'back' ? 'AND BACK!' : "3310'D!", false); sfx('thud'); }
    }
    return;
  }
  if (n.mode === 'drop') { n.z = Math.max(0, n.z - dt * 300); if (n.z <= 0) { n.mode = 'floor'; n.t = 0; sfx('thud'); popWord(n.x, n.y, 90, 'STILL WORKS', false); } return; }
  if (n.mode === 'floor' && n.t > 6) n.remove = true;
}
function orpDrawPhone(n) {
  const img = bgImg('orp/n3310'); if (!img) return;
  const x = Math.round((n.x - cam.x) / 2) * 2, y = n.y;
  shadow(x, y, 8, n.z);
  ctx.save(); ctx.imageSmoothingEnabled = false; ctx.translate(x, Math.round((y - n.z) / 2) * 2);
  ctx.rotate(n.mode === 'floor' ? 1.57 : Math.round(n.rot * 2) / 2); ctx.drawImage(img, -img.width, -img.height, img.width * 2, img.height * 2); ctx.restore();
}

// ---------------------------------------------------------------- the Builder
// Head down and a shoulder barge across the room: nothing stops him once he's going, and he skittles his own lot too. If
// he barges into the wall he's seeing stars for a second or two (hit him then). From range he throws a bar stool.
function orpBuilder(f, dt, p, d, dx, dy) {
  // can't be stopped mid-barge: a hit that isn't the last one puts him straight back into it
  if (f.barging && f.hp > 0 && (f.state === 'hurt' || f.state === 'down')) { f.state = 'barge'; f.z = 0; f.vz = 0; f.vx = f.face * 560; popWord(f.x, f.y, 140, 'UNSTOPPABLE!', false); }
  if (f.barging && f.state !== 'barge') f.barging = false;
  if (f.flash > 0.1 && chance(0.4)) parts.push({ k: 'puff', x: f.x + rand(-12, 12), y: f.y, z: 70 + rand(0, 30), vx: rand(-40, 40), vy: 0, vz: rand(10, 40), t: 0, life: 0.5, r: 5 });   // plaster dust
  if (f.state === 'bargeWind') { f.vx = f.vy = 0; if (Math.abs(p.x - f.x) > 6 && f.t < 0.3) f.face = Math.sign(p.x - f.x); if (chance(dt * 6)) dust(f.x - f.face * 14, f.y, 1, 12); if (f.t > 0.6) { f.state = 'barge'; f.t = 0; f.barging = true; sfx('heavy'); f.atkT = 0; f.atk = { t0: 0, t1: 1.0, reach: [-6, 62], depth: 24, dmg: d.dmg + 4, kd: true, kb: 440, hs: 0.08, hit: new Set(), zMax: 40 }; } return nlOwn(f, dt); }
  if (f.state === 'barge') {
    f.vx = f.face * 560; f.vy = 0; if (chance(0.5)) dust(f.x - f.face * 22, f.y, 1, 18);
    if (f.atk) resolveAttack(f, foes.filter(o => o !== f && !o.boss));   // skittles his own lot too
    const wall = (f.face < 0 && f.x < cam.x + 40) || (f.face > 0 && f.x > cam.x + W - 40);
    if (wall) { f.barging = false; f.atk = null; f.state = 'stars'; f.t = 0; f.vx = -f.face * 120; f.dazedT = 1.6; addShake(8); sfx('thud'); popWord(f.x, f.y, 170, 'BONK!', true); return nlOwn(f, dt); }
    if (f.t > 1.0) { f.barging = false; f.atk = null; f.state = 'recover'; f.t = 0; f.vx *= 0.2; }
    return nlOwn(f, dt);
  }
  if (f.state === 'stars') { friction(f, dt, 0.01); if (chance(dt * 4)) parts.push({ k: 'z', x: f.x + 10, y: f.y, z: 150, t: 0, life: 0.8 }); if (f.t > 1.6) { f.state = 'hover'; f.t = 0; } return nlOwn(f, dt); }
  if (f.state === 'throwWind') { f.vx = f.vy = 0; if (f.t > 0.5) { f.state = 'throwStool'; f.t = 0; orpStool(f); } return nlOwn(f, dt); }
  if (f.state === 'throwStool') { if (f.t > 0.4) { f.state = 'hover'; f.t = 0; f.cool = 0.8; } return nlOwn(f, dt); }
  f.bargeCool = (f.bargeCool == null ? 2 : f.bargeCool) - dt; f.stoolCool = (f.stoolCool == null ? 3 : f.stoolCool) - dt;
  if (ocFree(f)) {
    if (f.bargeCool <= 0 && dx > 150 && dx < 520 && dy < 20 && chance(dt * 1.6)) { f.bargeCool = rand(4.5, 6.5); nlStartSpecial(f, 'bargeWind'); say(f, pick(["'AVE IT!", 'Out the way!', 'Coming through!']), 1.2, true); return nlOwn(f, dt); }
    if (f.stoolCool <= 0 && dx > 200 && dx < 460 && chance(dt * 0.9)) { f.stoolCool = rand(5, 7); nlStartSpecial(f, 'throwWind'); return nlOwn(f, dt); }
    if (f.state === 'hover' && f.bargeCool <= 0 && dx > 150 && dy >= 20 && chance(dt * 2)) { f.hoverY = p.y; f.retarget = 1.2; }
  }
  return false;
}
function orpStool(f) {
  const p = player, T = 0.7, z0 = 100, tx = clamp(p.x + p.vx * 0.3, cam.x + 20, cam.x + W - 20), ty = clamp(p.y + p.vy * 0.3, FT + 4, FB - 4);
  const n = makeNpc('stool', f.x + f.face * 20, f.y); n.hp = 0; n.z = z0; n.vx = (tx - n.x) / T; n.vy = (ty - n.y) / T; n.vz = (GRAV * T * T / 2 - z0) / T; n.rot = 0; n.from = f;
  n.tx = tx; n.ty = ty; n.draw = orpDrawStool; S.npcs.push(n); sfx('throw');
  n.script = (m, dt) => {
    m.vz -= GRAV * dt; m.z += m.vz * dt; m.x += m.vx * dt; m.y += m.vy * dt; m.rot += dt * 9;
    if (m.z <= 0) {
      m.remove = true; sfx('break'); debris(m.x, m.y, 10, '#80502a', 7); addShake(4);
      for (const q of players()) if (canBeHit(q) && q.z < 30 && Math.abs(q.x - m.x) < 40 && Math.abs(q.y - m.y) < 24) { applyHit(m.from || m, q, { dmg: 11, kd: true, kb: 260, hs: 0.06 }, Math.sign(q.x - m.x) || 1); popWord(q.x, q.y, 150, 'STOOLED!', true); }
    }
  };
}
function orpDrawStool(n) {
  const img = bgImg('orp/stool'); if (!img) return;
  const x = Math.round((n.x - cam.x) / 2) * 2;
  // where it'll land, so you can step off it
  ctx.strokeStyle = 'rgba(255,90,60,' + (0.4 + Math.sin(time * 20) * 0.2).toFixed(2) + ')'; ctx.lineWidth = 2; ctx.beginPath(); ctx.ellipse(n.tx - cam.x, n.ty, 34, 10, 0, 0, Math.PI * 2); ctx.stroke();
  shadow(x, n.y, 16, n.z);
  ctx.save(); ctx.imageSmoothingEnabled = false; ctx.translate(x, Math.round((n.y - n.z - img.height) / 2) * 2); ctx.rotate(Math.round(n.rot * 2) / 2);
  ctx.drawImage(img, -img.width, -img.height, img.width * 2, img.height * 2); ctx.restore();
}

// ---------------------------------------------------------------- the Pool Shark's break
const ORP_BALLS = [['#c8202a', '#ff6a5a'], ['#e8c21e', '#fff07a'], ['#141418', '#5a5a66']];
function orpBreak(f) {
  sfx('hit'); popWord(f.x + f.face * 60, f.y, 120, 'BREAK!', false);
  const p = player, ang0 = Math.atan2((p.y - f.y) * 1.2, Math.abs(p.x - f.x) || 1);
  [-0.32, 0, 0.32].forEach((da, i) => {
    const a = clamp(ang0 + da, -0.8, 0.8), n = makeNpc('poolball', f.x + f.face * 40, f.y + (i - 1) * 6); n.hp = 0; n.col = ORP_BALLS[i];
    n.vx = f.face * Math.cos(a) * 560; n.vy = Math.sin(a) * 300; n.hit = new Set([f]); n.draw = orpDrawBall; n.rot = 0; S.npcs.push(n);
    n.script = (m, dt) => {
      m.x += m.vx * dt; m.y += m.vy * dt; m.vx *= Math.pow(0.5, dt); m.vy *= Math.pow(0.5, dt); m.rot += m.vx * dt * 0.1;
      if (m.y < FT + 2 || m.y > FB - 2) { m.vy = -m.vy; m.y = clamp(m.y, FT + 2, FB - 2); sfx('thunk'); }   // off the cushion
      if (Math.abs(m.vx) > 140) for (const e of ocAll(null)) {
        if (m.hit.has(e) || e.z > 16) continue;
        if (Math.abs(e.x - m.x) < (e.half || 20) * 0.6 + 8 && Math.abs(e.y - m.y) < 14) { m.hit.add(e); const pl = players().includes(e); applyHit(f, e, { dmg: pl ? 7 : 14, kd: true, kb: 220, hs: 0.05 }, Math.sign(m.vx) || 1); popWord(e.x, e.y, 120, pl ? 'POTTED!' : 'IN OFF!', false); if (!pl) addScore(150); }
      }
      if (m.x < cam.x - 40 || m.x > cam.x + W + 40 || m.t > 4) m.remove = true;
    };
  });
}
function orpDrawBall(n) {
  const x = Math.round((n.x - cam.x) / 2) * 2, y = Math.round(n.y / 2) * 2 - 6;
  shadow(x, n.y, 7, 0);
  ctx.fillStyle = OUT; ctx.fillRect(x - 6, y - 4, 12, 8); ctx.fillRect(x - 4, y - 6, 8, 12);
  ctx.fillStyle = n.col[0]; ctx.fillRect(x - 4, y - 4, 8, 8);
  ctx.fillStyle = n.col[1]; ctx.fillRect(x - 2 + (Math.floor(n.rot) % 2) * 2, y - 4, 2, 2);
}

// ---------------------------------------------------------------- the MC's hype, the Raver's whistle
function orpHype(f) {
  let n = 0;
  for (const o of foes) if (o !== f && canBeHit(o) && !o.boss && Math.abs(o.x - f.x) < 460) { o.rallyT = 5; o.buffT = 5; n++; }
  if (n) popWord(f.x, f.y, 190, 'HYPED!', false);
}
function orpWhistle(f) {
  sfx('whistle'); popWord(f.x, f.y, 170, 'PHWEEEEP!', true);
  if (S.dance && S.dancers && S.dancers.length) {
    // the dancers nearest him stop and turn on you, there and then
    const near = S.dancers.filter(n => !n.remove && n.script).sort((a, b) => Math.abs(a.x - f.x) - Math.abs(b.x - f.x)).slice(0, 2);
    for (const n of near) { n.script = null; n.z = 0; popWord(n.x, n.y, 160, '!', true); }
    setTimeout0(() => { for (const n of near) { if (n.remove) continue; n.remove = true; const g = makeFoe(n.kind, n.x, n.y); g.face = Math.sign(player.x - n.x) || 1; g.state = 'hover'; foes.push(g); } }, 0.5);
    return;
  }
  for (const q of players()) if (pHittable(30) && Math.abs(q.x - f.x) < 120 && Math.abs(q.y - f.y) < 30) { q.state = 'drowsy'; q.t = 0; q.drowsy = 0.7; q.vx = q.vy = 0; q.atk = null; q.running = false; popWord(q.x, q.y, 160, 'MY EARS!', false); }
}

// ---------------------------------------------------------------- per frame: the MC's sound waves, the champagne, the fizz
function orpCrowdTick(dt) {
  if (S.ocFizz > 0) S.ocFizz -= dt;
  if (!S.ocFx) return;
  for (const e of S.ocFx) {
    e.t += dt;
    if (e.k === 'ring') {
      e.r += 420 * dt; if (e.r > 280 || e.t > 0.8) e.dead = true;
      for (const q of players()) {
        if (e.hit.has(q)) continue;
        const ahead = (q.x - e.x) * e.face;
        if (ahead < 0 || Math.abs(ahead - e.r) > 26 || Math.abs(q.y - e.y) > 44 || q.z > 50 || !canBeHit(q)) continue;
        e.hit.add(q);
        if (q.buffT > 0 || q.rage) continue;
        if (e.n === 1 && ahead < 150 && pHittable(40)) { applyHit(e.from, q, { dmg: 4, kd: false, kb: 360, hs: 0.04 }, e.face); if (q.state === 'hurt') { q.state = 'drowsy'; q.t = 0; q.drowsy = 0.9; q.vx = e.face * 200; } popWord(q.x, q.y, 160, 'BO!', true); }
        else { q.vx += e.face * 520; popWord(q.x, q.y, 140, pick(['BOOM!', 'BASS!', 'WHOA!']), false); }
      }
    } else if (e.k === 'foam') { e.x += e.vx * dt; e.y += e.vy * dt; e.z += e.vz * dt; e.vz -= 400 * dt; if (e.t > e.life || e.z < 0) e.dead = true; }
  }
  S.ocFx = S.ocFx.filter(e => !e.dead);
}
function orpCrowdFore() {
  if (S.ocFx) for (const e of S.ocFx) {
    if (e.k === 'ring') {   // the wave front rolling away from the mic: a bright arc and two fainter ones behind it
      const a = Math.max(0, 1 - e.t / 0.8), fx = e.x - cam.x + e.face * e.r, cy = e.y - 66, ry = 46 + e.r * 0.1;
      const a0 = e.face > 0 ? -1.05 : Math.PI - 1.05, a1 = e.face > 0 ? 1.05 : Math.PI + 1.05;
      ctx.save();
      [[0, 7, '120,230,255', 0.9], [-16, 4, '200,250,255', 0.55], [-30, 3, '255,255,255', 0.3]].forEach(([off, lw, col, k]) => {
        ctx.strokeStyle = 'rgba(' + col + ',' + (a * k).toFixed(2) + ')'; ctx.lineWidth = lw; ctx.beginPath();
        ctx.ellipse(fx + e.face * (off - 34), cy, 34, ry, 0, a0, a1); ctx.stroke();
      });
      ctx.restore();
    } else if (e.k === 'foam') {
      const x = Math.round((e.x - cam.x) / 2) * 2, y = Math.round((e.y - e.z) / 2) * 2;
      ctx.fillStyle = e.t < 0.1 ? '#fff8d8' : 'rgba(255,248,216,0.8)'; ctx.fillRect(x - 2, y - 2, 4, 4); ctx.fillStyle = '#f0d070'; ctx.fillRect(x, y, 2, 2);
    }
  }
  // blinded by champagne: fizz closes in round the edges of the screen
  if (S.ocFizz > 0) {
    const a = Math.min(1, S.ocFizz / 0.8);
    ctx.save(); ctx.globalAlpha = a;
    for (let i = 0; i < 90; i++) {
      const ang = (i * 2.399) % (Math.PI * 2), rr = 0.62 + ((i * 0.37 + time * 0.6) % 0.5), x = W / 2 + Math.cos(ang) * W * rr * 0.62, y = H / 2 + Math.sin(ang) * H * rr * 0.7;
      const s = 6 + (i % 4) * 4; ctx.fillStyle = i % 3 ? 'rgba(255,250,225,0.85)' : 'rgba(240,210,120,0.8)'; ctx.fillRect(Math.round(x / 2) * 2, Math.round((y - (time * 40 + i * 13) % 30) / 2) * 2, s, s);
    }
    ctx.fillStyle = 'rgba(255,248,220,' + (0.25 * a).toFixed(2) + ')'; ctx.fillRect(0, 0, W, H); ctx.restore();
  }
}
