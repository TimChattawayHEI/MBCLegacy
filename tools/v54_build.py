"""Version 54: Ash, the second unlockable lad.

Patches web/index.html in place (run from the repo root, after tools/v53_build.py):  python3 tools/v54_build.py
Safe to run again. Ash's sheets (web/sprites/ash.png, ashn.png, pose_ash.png) and their layout and frame picks
(tools/v54/ash_meta.json) come from tools/v54/ash_sheet.py. Also edits tools/title3d/title3d.js so the 3D select keeps him.

- Ash: a head taller than everyone (his sheet is drawn on a bigger canvas, about 76px to the lads' 62). Long reach,
  a touch slower. Jab, jab, long front kick.
- Special THE ASHINATOR: he stands bolt upright, a flash, and he's the Ashinator (leather jacket, shades). Nine shots:
  all of them into the boss if there's one on screen, otherwise round the room, whoever's nearest to going down first.
  Then "Ash'll be back." and he marches off the nearest edge of the screen, and walks back in as Ash.
- Mini special GINGER SNAP: a spinning long-legged kick that catches everyone round him.
- Locked until you finish the campaign on Hard: a NEW CHALLENGER moment on the win screen (after Thet's, if both
  unlock at once). Until then he's a silhouette on the select screen. Typing ASH on the select screen, or ASHY as an
  online join code, unlocks him too.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, 'web', 'index.html')
META = json.load(open(os.path.join(ROOT, 'tools', 'v54', 'ash_meta.json')))


def swap(s, old, new, label):
    if new in s:
        return s
    if s.count(old) != 1:
        sys.exit(f'v54_build: could not find the {label} (found {s.count(old)} matches)')
    return s.replace(old, new)


s = open(PAGE, encoding='utf-8').read()

# ---------------------------------------------------------------- who he is
s = swap(s, """      respawn: ['Back in the long grass.'], boss: ['Big lad. Bigger ankles.'] } },
];""", """      respawn: ['Back in the long grass.'], boss: ['Big lad. Bigger ankles.'] } },
  // Ash (Version 54): unlocked by finishing the campaign on Hard. A head taller than everyone, long reach, and he'll be back
  { id: 'ash', name: 'ASH', tag: 'Ginger. Tall. Will be back.', speed: 224, power: 1.06, hp: 122, atkMul: 1, reach: 18, special: 'THE ASHINATOR', sp: 'ashinator', color: '#f07a2a',
    stats: [3, 3, 4], blurb: 'Stands up very straight. Then the Ashinator walks in: leather jacket, shades, nine shots, all of them into the boss if there is one. Then he walks off. He\\u2019ll be back.',
    look: { shirt: '#bfcde6', shirt2: '#e6f0fa', legs: '#c5ab80', skin: '#f8cab2', hair: '#ee791a', hairStyle: 'short', build: 0.9, tall: 1.22 },
    lines: {
      start: ['Mind your heads, lads.', 'Alright down there?', "I'm not lanky. I'm long.", 'Never needed my hands.', 'Kickboxing club, under 11s. Undefeated.'],
      special: ['Hold my coat.', 'One moment, lads.', 'Stand back.'],
      morph: ['Target acquired.', 'Ginger mode. Engaged.', 'Scanning. Nine targets.', 'Systems online.'],
      leave: ["Ash'll be back.", "Ash'll be back.", "Ash'll be back.", "Ash'll be back. Probably."],
      back: ['Told you.', 'Back.', 'Did I miss anything?', 'Told you I would.'],
      ko: ['Long legs, mate.', 'Reach.', 'Saw you coming. From up here.', 'Down you go.', 'Lights out.', 'Feet first.'],
      hurt: ['Oi! Up here!', 'Mind the hair!', 'How did you even reach?', 'That was a cheap shot.'],
      weapon: ['Long reach, longer stick.'], food: ['Growing lad.'],
      respawn: ["Told you I'd be back."], boss: ["Big lad. I'm taller though."] } },
];""", 'Ash in CHARS')
s = swap(s, """const PLAYABLE = ['tim', 'seb', 'byron', 'pearcy', 'kelly', 'marc', 'sam', 'thet'].map(id => CHAR_BY_ID[id]);""",
         """const PLAYABLE = ['tim', 'seb', 'byron', 'pearcy', 'kelly', 'marc', 'sam', 'thet', 'ash'].map(id => CHAR_BY_ID[id]);""", 'PLAYABLE')
s = swap(s, """function ladLocked(c) { return !!c && c.id === 'thet' && !settings.thet; }""",
         """function ladLocked(c) { return !!c && ((c.id === 'thet' && !settings.thet) || (c.id === 'ash' && !settings.ash)); }
// Ash (Version 54) stays a silhouette until the campaign's been finished on Hard (or ASH is typed on the select screen)
function unlockAsh() { if (settings.ash) return false; settings.ash = true; saveSettings(); return true; }
function lockHint(c) { return c && c.id === 'ash' ? 'Someone tall is waiting. Finish the campaign on Hard to find out who.' : 'Someone is hiding in the bushes. Finish the campaign to find out who.'; }""", 'ladLocked')
s = swap(s, """const COMBO_OF = { tim: 'quick', marc: 'quick', byron: 'quick', seb: 'heavy', pearcy: 'heavy', kelly: 'kelly', sam: 'sam', thet: 'quick' };""",
         """const COMBO_OF = { tim: 'quick', marc: 'quick', byron: 'quick', seb: 'heavy', pearcy: 'heavy', kelly: 'kelly', sam: 'sam', thet: 'quick', ash: 'ash' };""", 'Ash combo')
s = swap(s, """  std: [{ a: 'jab', d: 8 }, { a: 'hook', d: 8 }, { a: 'kick', d: 13, fin: true }],
};""", """  std: [{ a: 'jab', d: 8 }, { a: 'hook', d: 8 }, { a: 'kick', d: 13, fin: true }],
  ash: [{ a: 'jab', d: 8 }, { a: 'hook', d: 10 }, { a: 'kick', d: 15, fin: true, kb: 380 }],   // all kicks: his jab and hook rows are a low kick and a roundhouse
};""", 'Ash combo moves')
# long arms: a lad's own reach on top of everyone's
s = swap(s, """reach: [6, (fin ? 80 : 68) + (brute ? 6 : 0)], depth: 24,""", """reach: [6, (fin ? 80 : 68) + (brute ? 6 : 0) + (p.def.reach || 0)], depth: 24,""", 'punch reach')
s = swap(s, """  thet: { name: 'ANKLE BITER', hit: [0.1, 0.2, 0.3, 0.4], end: 0.6, r: 92, slide: 720, dmg: 6, word: 'TRIPPED!' },
};""", """  thet: { name: 'ANKLE BITER', hit: [0.1, 0.2, 0.3, 0.4], end: 0.6, r: 92, slide: 720, dmg: 6, word: 'TRIPPED!' },
  ash: { name: 'GINGER SNAP', hit: [0.3, 0.5], end: 0.72, r: 132, spin: [0.08, 0.42], dmg: 10, word: 'SNAP!' },
};""", 'Ash mini')

# ---------------------------------------------------------------- his sheets
import re
# between markers, so a rebuilt sheet replaces the old entries when this is run again
metas = ''.join('"' + k + '":' + json.dumps(META[k], separators=(',', ':')) + ',' for k in ('ash', 'ashn'))
block = '/* ash meta */' + metas + '/* ash meta end */'
if '/* ash meta */' in s: s = re.sub(r'/\* ash meta \*/.*?/\* ash meta end \*/', lambda m: block, s, flags=re.S)
else: s = swap(s, """const SPRITE_META = {""", """const SPRITE_META = {""" + block, 'Ash sprite meta')
frames = """  // ash frames
  ash: """ + META['frames']['ash'] + """,
  ashn: """ + META['frames']['ashn'] + """,
  // ash frames end"""
if '  // ash frames\n' in s: s = re.sub(r'  // ash frames\n.*?  // ash frames end', lambda m: frames, s, flags=re.S)
else: s = swap(s, """const LAD_FRAMES = {""", """const LAD_FRAMES = {\n""" + frames, 'Ash frames')
# the Ashinator is drawn from his own sheet while the special has him
s = swap(s, """  { const sid = e.def && e.def.id && LAD_FRAMES[e.def.id] ? e.def.id : (e.kind && FOE_FRAMES[e.kind] ? e.kind : null);""",
         """  { const sid = e.spForm && SPRITE_META[e.spForm] ? e.spForm : e.def && e.def.id && LAD_FRAMES[e.def.id] ? e.def.id : (e.kind && FOE_FRAMES[e.kind] ? e.kind : null);""", 'drawHuman sheet')
s = swap(s, """  const m = sh.m, F = isFoe ? FOE_FRAMES[e.kind] : LAD_FRAMES[e.def.id], st = e.state, sp = st === 'special' ? e.def.sp : null;""",
         """  const m = sh.m, F = isFoe ? FOE_FRAMES[e.kind] : LAD_FRAMES[e.spForm || e.def.id], st = e.state, sp = st === 'special' ? e.def.sp : null;""", 'drawLad frames')
s = swap(s, """  if (wk && !worn && !(isFoe && F.ownWeapon) && st !== 'throw'""", """  if (wk && !worn && !e.spForm && !(isFoe && F.ownWeapon) && st !== 'throw'""", 'no weapon in the Ashinator hand')

# ---------------------------------------------------------------- THE ASHINATOR
s = swap(s, """  if (sp === 'ambush') return ambushSp(p, dt, pw);
  return false;
}""", """  if (sp === 'ambush') return ambushSp(p, dt, pw);
  if (sp === 'ashinator') return ashinatorSp(p, dt, pw);
  return false;
}
// THE ASHINATOR (Ash): he stands up straight, a flash, and he's the Ashinator. Nine shots, then he walks off. He'll be back.
const ASHN = { morph: 0.75, first: 1.05, gap: 0.2, n: 9, walk: 330 };
function ashMuzzle(p) {
  const m = SPRITE_META.ashn, F = LAD_FRAMES.ashn, g = (m.gun && m.gun.shoot && m.gun.shoot[F.aim]) || [m.ax + 30, m.ay - 48];
  return { x: p.x + p.face * (g[0] - m.ax) * SPR_K, z: (m.ay - g[1]) * SPR_K };
}
function ashRevert(p) { p.spForm = null; p.spAway = false; p.spBack = false; p.spHide = false; p.spOffT = null; }
function ashinatorSp(p, dt, pw) {
  const t = p.t;
  if (!p.spAway && !p.spBack) { p.vx = 0; p.vy = 0; }
  if (t < ASHN.morph) {
    if (!p.spInf && t > 0.15) { p.spInf = true; sfx('servo'); }
    if (t > 0.25 && chance(dt * 16)) parts.push({ k: 'sparkle', x: p.x + rand(-22, 22), y: p.y, z: rand(10, 160), t: 0, life: 0.35 });
  } else if (!p.spForm && !p.spDone && !p.spBack) {
    p.spForm = 'ashn'; p.spShot = 0; p.spNext = ASHN.first; p.spFireT = null; p.spPlan = null; p.spWaitT = 0;
    flashT = Math.max(flashT, 0.14); addShake(9); sfx('heavy'); sfx('special');
    for (let i = 0; i < 22; i++) parts.push({ k: 'sparkle', x: p.x + rand(-34, 34), y: p.y, z: rand(0, 180), t: 0, life: rand(0.4, 0.8) });
    say(p, pick(p.def.lines.morph), 1.6, true);
  }
  if (p.spForm && !p.spDone && t >= p.spNext) {
    // nine shots: all into the boss if there is one on screen, otherwise round the room, whoever's nearest to going down first
    const i = p.spShot, on = foes.filter(f => canBeHit(f) && !f.npc && f.x > cam.x - 10 && f.x < cam.x + W + 10);
    // the plan is made on the first shot: who gets which bullet, so each of them only goes down on his last one
    if (!p.spPlan) { const boss = on.find(f => f.boss), pool = boss ? [boss] : on.sort((a, b) => a.hp - b.hp); p.spPlan = pool.length ? [...Array(ASHN.n).keys()].map(k => pool[k % pool.length]) : []; }
    let f = p.spPlan[i] || null;
    const floored = f && f.boss && !canBeHit(f) && !f.remove && f.state !== 'dead' && f.state !== 'beaten';
    if (floored && p.spWaitT < 3) {
      // a boss that's gone down: he waits, aimed, until he's up again
      if (!p.spWaitT) say(p, 'Get up.', 1.4, true);
      p.spWaitT += dt; p.spNext = t + 0.04; p.face = Math.sign(f.x - p.x) || p.face;
    } else {
      if (f && !canBeHit(f)) f = on.sort((a, b) => Math.abs(a.x - p.x) - Math.abs(b.x - p.x))[0] || null;   // he's gone: whoever's nearest
      p.spNext = t + ASHN.gap; p.spShot++; p.spFireT = t;
      if (f) p.face = Math.sign(f.x - p.x) || p.face;
      const g = ashMuzzle(p), tx = f ? f.x : p.x + p.face * 900, ty = f ? f.y : p.y, tz = f ? 70 * (f.scale || 1) : g.z;
      (S.tracers = S.tracers || []).push({ x0: g.x, y0: p.y, z0: g.z, x1: tx, y1: ty, z1: tz, t: 0, hit: !!f });
      sfx('bang'); addShake(3);
      parts.push({ k: 'debris', x: p.x + p.face * 12, y: p.y, z: g.z - 6, vx: -p.face * rand(60, 130), vz: rand(160, 260), t: 0, life: 0.6, r: 2, col: '#d9b048', rot: 0, vr: 9 });
      if (f) {
        const last = p.spShot === ASHN.n, his = p.spPlan.lastIndexOf(f) <= i;   // his last bullet (or a stray, retargeted one)
        applyHit(p, f, { sp: true, dmg: (f.boss ? 14 : 16) * pw, kd: f.boss ? last : his, kb: his ? 300 : 0, hs: last ? 0.08 : 0.02 }, p.face);
        if (p.spShot % 3 === 0) popWord(f.x, f.y, 150, pick(['BLAM!', 'BANG!', 'BLAM!']), false);
      }
      if (p.spShot >= ASHN.n) { p.spDone = true; p.spEnd = t + 0.45; }
    }
  }
  // done shooting: "Ash'll be back", and he marches off the nearest edge of the screen
  if (p.spDone && !p.spAway && !p.spBack && t >= p.spEnd) {
    if (ST.fixed) {   // nowhere to walk to on the raft
      if (!p.spWord) { p.spWord = true; say(p, "Ash'll be b... it's a boat, isn't it.", 2.2, true); p.spEnd = t + 1.2; }
      else { ashRevert(p); flashT = Math.max(flashT, 0.1); sfx('page'); endSpecial(p); }
      return true;
    }
    p.spAway = true; p.spOut = p.x - cam.x < W / 2 ? -1 : 1; p.face = p.spOut; p.spOffT = null;
    say(p, pick(p.def.lines.leave), 2.4, true);
  }
  if (p.spAway) {
    p.vy = 0; p.face = p.spOut; p.walk = (p.walk || 0) + dt * 11;
    const gone = p.spOut < 0 ? p.x < cam.x - 70 : p.x > cam.x + W + 70;
    if (gone && p.spOffT == null) { p.spOffT = 0; p.spHide = true; }
    if (p.spOffT == null) p.vx = p.spOut * ASHN.walk;
    else {
      p.vx = 0; p.spOffT += dt;
      if (p.spOffT > 0.55) { p.spAway = false; p.spHide = false; p.spForm = null; p.spBack = true; p.face = -p.spOut; }   // and back he comes, Ash again
    }
  }
  if (p.spBack) {
    p.vx = -p.spOut * 300; p.vy = 0; p.face = -p.spOut; p.walk = (p.walk || 0) + dt * 10;
    const inside = p.spOut < 0 ? p.x > cam.x + 110 : p.x < cam.x + W - 110;
    if (inside) { p.vx = 0; say(p, pick(p.def.lines.back), 1.8, true); ashRevert(p); endSpecial(p); }
  }
  if (t > 12) { ashRevert(p); p.x = clamp(p.x, cam.x + 60, cam.x + W - 60); endSpecial(p); }
  return true;
}""", 'ASHINATOR special')
s = swap(s, """  p.spHide = false; p.spOutT = null; p.spWord = false;""",
         """  p.spHide = false; p.spOutT = null; p.spWord = false;
  p.spForm = null; p.spAway = false; p.spBack = false; p.spOffT = null; p.spShot = 0; p.spFireT = null; p.spPlan = null;""", 'special flags')
s = swap(s, """function endSpecial(p) {
  if (p.def.sp === 'cover')""", """function endSpecial(p) {
  if (p.def.sp === 'ashinator') { p.spForm = null; p.spAway = false; p.spBack = false; p.spHide = false; }
  if (p.def.sp === 'cover')""", 'endSpecial reset')
# a new stage never starts with him hidden off screen or still in the jacket
s = swap(s, """p.meter = 100; meterNopeT = 0; p.rage = false; p.heldBy = null;""",
         """p.meter = 100; meterNopeT = 0; p.rage = false; p.heldBy = null;
  for (const q of players()) { q.spForm = null; q.spAway = false; q.spBack = false; q.spHide = false; }""", 'stage start reset')
# walking off the screen: no edge clamp, and the camera waits for him
s = swap(s, """    if (p.state === 'walkin') p.x = Math.min(p.x, maxX); else p.x = clamp(p.x, minX, maxX);""",
         """    if (p.state === 'walkin') p.x = Math.min(p.x, maxX); else if (!p.spAway && !p.spBack) p.x = clamp(p.x, minX, maxX);""", 'edge clamp')
s = swap(s, """  if (S.wave && !S.wave.event) return;
  const target = clamp(player.x - W * 0.42, 0, ST.len - W);""", """  if (S.wave && !S.wave.event) return;
  if (players().some(q => q.spAway || q.spBack)) return;   // Ash walking off and back on
  const target = clamp(player.x - W * 0.42, 0, ST.len - W);""", 'camera hold')
# his frames: the straighten-up, then the Ashinator's sheet (aim, fire, recoil, the march), then Ash walking back in
s = swap(s, """      // play the lad's own special animation over its wind-up, then hold the last frame""",
         """      // Ash: stands up straight (his sheet), then the Ashinator (his own sheet), then Ash walking back in
      if (sp === 'ashinator') {
        if (e.spForm) {
          const wl = F.walk || [1];
          if (e.spAway) return ['walk', wl[((Math.floor((e.walk || 0) / (Math.PI * 2) * wl.length) % wl.length) + wl.length) % wl.length]];
          if (!e.spShot) return t < ASHN.first - 0.14 ? ['idle', F.idle[0]] : ['shoot', F.raise[Math.min(F.raise.length - 1, Math.floor((t - ASHN.first + 0.14) / 0.07))]];
          const since = t - (e.spFireT == null ? -9 : e.spFireT);
          if (since < 0.05) return ['shoot', F.fire[0]];
          if (since < 0.11) return ['shoot', F.fire[1]];
          if (e.spDone) return ['idle', F.idle[0]];
          return ['shoot', F.aim];
        }
        if (e.spBack) return ['walk', walkIdx()];
        if (F.special) return ['special', F.special[Math.min(F.special.length - 1, Math.floor(t / ASHN.morph * F.special.length))]];
      }
      // play the lad's own special animation over its wind-up, then hold the last frame""", 'Ashinator frames')
# the shots: a bright streak from the muzzle to whoever it hit, gone in a blink
s = swap(s, """  if (S.bushes && S.bushes.length) { for (const b of S.bushes) b.t += dt; S.bushes = S.bushes.filter(b => b.t < b.life); }""",
         """  if (S.bushes && S.bushes.length) { for (const b of S.bushes) b.t += dt; S.bushes = S.bushes.filter(b => b.t < b.life); }
  if (S.tracers && S.tracers.length) { for (const r of S.tracers) r.t += dt; S.tracers = S.tracers.filter(r => r.t < 0.1); }""", 'tracer update')
s = swap(s, """  for (const b of (S.bushes || [])) if (b.t >= 0) list.push({ y: b.y - 3, f: () => drawBush(b) });
}""", """  for (const b of (S.bushes || [])) if (b.t >= 0) list.push({ y: b.y - 3, f: () => drawBush(b) });
  for (const r of (S.tracers || [])) list.push({ y: Math.max(r.y0, r.y1) + 2, f: () => drawTracer(r) });
}
function drawTracer(r) {
  const a = 1 - r.t / 0.1; if (a <= 0) return;
  const x0 = r.x0 - cam.x, y0 = r.y0 - r.z0, x1 = r.x1 - cam.x, y1 = r.y1 - r.z1, n = Math.max(1, Math.ceil(Math.hypot(x1 - x0, y1 - y0) / 4));
  const px = v => Math.round(v / 2) * 2;
  ctx.save(); ctx.globalAlpha = a;
  ctx.fillStyle = 'rgba(255,214,110,0.55)'; for (let i = 0; i <= n; i++) { const k = i / n; ctx.fillRect(px(x0 + (x1 - x0) * k) - 2, px(y0 + (y1 - y0) * k) - 2, 4, 4); }
  ctx.fillStyle = '#fff6c8'; for (let i = 0; i <= n; i++) { const k = i / n; ctx.fillRect(px(x0 + (x1 - x0) * k), px(y0 + (y1 - y0) * k), 2, 2); }
  if (r.hit) { ctx.fillStyle = '#ffffff'; ctx.fillRect(px(x1) - 4, px(y1) - 2, 8, 4); ctx.fillRect(px(x1) - 2, px(y1) - 4, 4, 8); }
  ctx.restore();
}""", 'tracer draw')
# his sounds: the servo whine of the change, and the shots
s = swap(s, """  meh: () => { tn({ f: 330, f1: 250, len: 1.4, type: 'sawtooth', vol: 0.035, vib: 6, vibD: 14 }); },
});""", """  meh: () => { tn({ f: 330, f1: 250, len: 1.4, type: 'sawtooth', vol: 0.035, vib: 6, vibD: 14 }); },
  servo: () => { tn({ f: 90, f1: 420, len: 0.6, type: 'sawtooth', vol: 0.04, vib: 22, vibD: 18 }); nz({ len: 0.5, f: 4000, f1: 1200, type: 'bandpass', q: 3, vol: 0.08 }); },
  bang: () => { nz({ len: 0.2, f: 2600 * pv(), f1: 380, type: 'lowpass', vol: 0.55 }); tn({ f: 160, f1: 45, len: 0.15, type: 'square', vol: 0.1 }); },
});""", 'Ash sounds')

# ---------------------------------------------------------------- locked until the campaign's done on Hard
s = swap(s, """  if (typed.endsWith('THET') && unlockThet()) { typed = ''; sfx('jackpot'); showBanner('THET UNLOCKED', 'He was there the whole time', 2.4); }""",
         """  if (typed.endsWith('THET') && unlockThet()) { typed = ''; sfx('jackpot'); showBanner('THET UNLOCKED', 'He was there the whole time', 2.4); }
  if (typed.endsWith('ASH') && unlockAsh()) { typed = ''; sfx('jackpot'); showBanner('ASH UNLOCKED', "He said he'd be back", 2.4); }""", '2D select unlock code')
# nine tiles on the 2D select
s = swap(s, """const TILE = { w: 100, h: 80, gap: 12, y: 404 };""", """const TILE = { w: 92, h: 80, gap: 10, y: 404 };""", '2D select tile size')
# online: ASHY as a join code unlocks him, and is never handed out as a room code
s = swap(s, """return s === 'THET' ? netRoomCode() : s; }""", """return s === 'THET' || s === 'ASHY' ? netRoomCode() : s; }""", 'room codes')
s = swap(s, """  if (code === 'THET') {""", """  if (code === 'ASHY') { NL.code = ''; if (NL.input) NL.input.value = ''; if (unlockAsh()) { sfx('jackpot'); NL.msg = "ASH UNLOCKED. He said he'd be back."; } else NL.msg = 'Ash is already in. Look up.'; return; }
  if (code === 'THET') {""", 'join code unlock')
# the ending chat and the unlock
s = swap(s, """    if (!settings.thet) lines.push(['sys', 'Thet joined the group'], ['thet', 'been here the whole time lads'], ['thet', 'you just never look down']);""",
         """    if (!settings.thet) lines.push(['sys', 'Thet joined the group'], ['thet', 'been here the whole time lads'], ['thet', 'you just never look down']);
    if (!settings.ash && run.diff === 'hard') lines.push(['sys', 'Ash joined the group'], ['ash', 'sorry im late lads'], ['ash', 'had to duck to get through the door'], ['ash', 'told you id be back']);""", 'ending lines')
s = swap(s, """  if (unlockThet()) { challenger = { t: 0 }; setTimeout(() => { sfx('airhorn'); sfx('incoming'); }, 300); }""",
         """  { const fresh = []; if (unlockThet()) fresh.push('thet'); if (run.diff === 'hard' && unlockAsh()) fresh.push('ash');
    if (fresh.length) { challenger = { ids: fresh }; fresh.forEach((id, i) => setTimeout(() => { sfx('airhorn'); sfx('incoming'); }, 300 + i * CH_LEN * 1000)); } }""", 'unlock on win')
s = swap(s, """  if (modeT > (challenger ? 4.6 : 1.4) && (pressed.has('punch') || pressed.has('start') || taps.length)) { challenger = null; openNameEntry(); }""",
         """  if (modeT > (challenger ? CH_LEN * challenger.ids.length - 0.6 : 1.4) && (pressed.has('punch') || pressed.has('start') || taps.length)) { challenger = null; openNameEntry(); }""", 'win screen wait')
s = swap(s, """function drawChallenger() {
  const t = modeT; if (t > 5.2) { challenger = null; return; }
  const a = Math.min(1, t / 0.25, (5.2 - t) / 0.4);""", """const CH_LEN = 5.2;
function drawChallenger() {
  const ids = challenger.ids || ['thet'], i = Math.floor(modeT / CH_LEN);
  if (i >= ids.length) { challenger = null; return; }
  const id = ids[i], C = CHAR_BY_ID[id], t = modeT - i * CH_LEN;
  const a = Math.min(1, t / 0.25, (CH_LEN - t) / 0.4);""", 'challenger timing')
s = swap(s, """  const sh = ladSprite('thet');
  if (sh && sh.ready) {
    const m = sh.m, row = m.rows.idle[0], k = 5,""", """  const sh = ladSprite(id);
  if (sh && sh.ready) {
    const m = sh.m, row = m.rows.idle[0], k = id === 'thet' ? 5 : 250 / m.h,""", 'challenger sprite')
s = swap(s, """  if (t > 1.3) { textOut('THET', W / 2, 470, '34px ' + DISPLAY, '#efe6d2', OUT, 7, 'center');""",
         """  if (t > 1.3) { textOut(C.name, W / 2, 470, '34px ' + DISPLAY, '#efe6d2', OUT, 7, 'center');""", 'challenger name')

# the HUD face: Thet drawn bigger and Ash smaller, so their heads fill the box like everyone else's
s = swap(s, """p.def.id === 'thet' ? 1.15 * 62 / SPRITE_META.thet.h : 1.15);""",
         """p.def.id === 'thet' || p.def.id === 'ash' ? 1.15 * 62 / SPRITE_META[p.def.id].h : 1.15);""", 'HUD face')

# ---------------------------------------------------------------- portrait and credits
s = swap(s, '"portraits/thet", ', '"portraits/ash", "portraits/thet", ', 'portrait preload')
s = swap(s, """const PORTRAIT_IDS = ['tim', 'seb', 'byron', 'pearcy', 'kelly', 'marc', 'sam', 'thet', 'denise', 'jo', 'nozzer'];""",
         """const PORTRAIT_IDS = ['tim', 'seb', 'byron', 'pearcy', 'kelly', 'marc', 'sam', 'thet', 'ash', 'denise', 'jo', 'nozzer'];""", 'portrait ids')
s = swap(s, """['lad', 'thet', 'THET', 'Pocket-sized. Fully camouflaged.'], ['gap'],""",
         """['lad', 'thet', 'THET', 'Pocket-sized. Fully camouflaged.'], ['lad', 'ash', 'ASH', 'Ginger. Tall. Will be back.'], ['gap'],""", 'credits')

# ---------------------------------------------------------------- the 3D select (also in tools/title3d/title3d.js)
T3 = [
    ("""  const ORDER = ['marc', 'sam', 'seb', 'tim', 'byron', 'pearcy', 'kelly', 'thet'];   // Thet on the end (Version 50), a silhouette until unlocked""",
     """  const ORDER = ['ash', 'marc', 'sam', 'seb', 'tim', 'byron', 'pearcy', 'kelly', 'thet'];   // the tallest and the shortest at either end (Thet, Version 50; Ash, Version 54), silhouettes until unlocked""", '3D order'),
    ("""tx: (i - MID) * 50, tz: 24 - depth * 18,""", """tx: (i - MID) * 44, tz: 24 - depth * 16,""", '3D lineup spacing'),
    ("""  const POSES = { tim: 1, seb: 1, byron: 1, pearcy: 1, kelly: 1, marc: 1, sam: 1, thet: 1 };""",
     """  const POSES = { tim: 1, seb: 1, byron: 1, pearcy: 1, kelly: 1, marc: 1, sam: 1, thet: 1, ash: 1 };""", '3D poses'),
    ("""thet: ['CAN\\u2019T SEE ME!', 'incoming'] };""", """thet: ['CAN\\u2019T SEE ME!', 'incoming'], ash: ['MIND YOUR HEADS!', 'servo'] };""", '3D pick shout'),
    ("""      const spots = [[-124, -40], [124, -60], [-140, -130], [140, -150], [-118, -220], [118, -240], [0, -290]];""",
     """      const spots = [[-124, -40], [124, -60], [-140, -130], [140, -150], [-118, -220], [118, -240], [0, -290], [-60, -330]];""", '3D stage spots'),
    ("""      const spots = [[44, -26], [-40, -38], [88, -56], [-82, -70], [130, -86], [-124, -102], [170, -118]];""",
     """      const spots = [[44, -26], [-40, -38], [88, -56], [-82, -70], [130, -86], [-124, -102], [170, -118], [-166, -134]];""", '3D diff spots'),
    ("""    if (typed.endsWith('THET') && unlockThet()) { typed = ''; sfx('jackpot'); toast('THET UNLOCKED'); if (view === 'lad') renderLad(); }""",
     """    if (typed.endsWith('THET') && unlockThet()) { typed = ''; sfx('jackpot'); toast('THET UNLOCKED'); if (view === 'lad') renderLad(); }
    if (typed.endsWith('ASH') && unlockAsh()) { typed = ''; sfx('jackpot'); toast('ASH UNLOCKED'); if (view === 'lad') renderLad(); }""", '3D unlock code'),
    ("""    q('ltag').textContent = lk ? 'Someone is hiding in the bushes. Finish the campaign to find out who.' : c.tag;""",
     """    q('ltag').textContent = lk ? lockHint(c) : c.tag;""", '3D locked hint'),
]
for o, n, l in T3:
    s = swap(s, o, n, l)

open(PAGE, 'w', encoding='utf-8').write(s)
print('v54_build: web/index.html updated')

# keep the title3d source in step, so tools/title3d_build.py carries the same code
SRC = os.path.join(ROOT, 'tools', 'title3d', 'title3d.js')
j = open(SRC, encoding='utf-8').read()
for o, n, l in T3:
    j = swap(j, o, n, l + ' (title3d.js)')
open(SRC, 'w', encoding='utf-8').write(j)
