"""Version 50: Thet, the unlockable eighth lad.

Patches web/index.html in place (run from the repo root, after tools/v49_build.py):  python3 tools/v50_build.py
Safe to run again. Thet's sheet layout (cell, anchor, rows, hand points) and frame picks live in tools/v50/thet_meta.json,
written by tools/v50/thet_sheet.py when web/sprites/thet.png is built.

- Thet: pocket-sized, quick, small target. A head shorter than everyone (his sheet is drawn at two thirds the size).
- Special AMBUSH: dives into the undergrowth; bushes pop up across the screen and he springs out of each one in turn,
  taking legs out. Mini special ANKLE BITER: darts low through the crowd tripping everyone.
- Locked until you finish the campaign on any difficulty: a NEW CHALLENGER moment on the win screen. Until then he's a
  black silhouette on the select screen. (Typing THET on the select screen unlocks him too.)
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, 'web', 'index.html')
META = json.load(open(os.path.join(ROOT, 'tools', 'v50', 'thet_meta.json')))


def swap(s, old, new, label):
    if new in s:
        return s
    if s.count(old) != 1:
        sys.exit(f'v50_build: could not find the {label} (found {s.count(old)} matches)')
    return s.replace(old, new)


s = open(PAGE, encoding='utf-8').read()

# ---------------------------------------------------------------- who he is
s = swap(s, """      respawn: ['Pivoting.'], boss: ["I'll handle the big account."] } },
];""", """      respawn: ['Pivoting.'], boss: ["I'll handle the big account."] } },
  // Thet (Version 50): unlocked by finishing the campaign. Small, quick, and nobody ever sees him coming
  { id: 'thet', name: 'THET', tag: 'Pocket-sized. Fully camouflaged.', speed: 268, power: 0.88, hp: 104, atkMul: 0.8, special: 'AMBUSH', sp: 'ambush', color: '#e0483a',
    stats: [5, 2, 3], blurb: 'Dives into the undergrowth. Bushes pop up everywhere and he comes out of every one of them going for the ankles.',
    look: { shirt: '#4f6130', shirt2: '#2c391a', legs: '#384d26', skin: '#eaa87b', hair: '#161619', hairStyle: 'short', build: 0.8, tall: 0.7, camo: true },
    lines: {
      start: ["Nobody saw me coming. Nobody ever does.", "I'm not short. I'm low profile.", 'Lads. Down here.', 'Smaller target, mate.'],
      special: ['AMBUSH!', 'Into the bushes!', "You can't hit what you can't see.", 'Tactical crouch!'],
      ko: ['Ankles. Always the ankles.', 'The bigger they are...', 'Never look down, mate.', 'Should have looked down.', 'Tactical.'],
      hurt: ['Pick on someone your own size. Actually, don\\u2019t.', 'Oi! Down here!', 'Felt that in my shins.', 'That was a cheap shot. Literally, I\\u2019m cheap to reach.'],
      weapon: ["It's bigger than me. Perfect."], food: ["Don't say kids' menu. Don't say it."],
      respawn: ['Back in the long grass.'], boss: ['Big lad. Bigger ankles.'] } },
];""", 'Thet in CHARS')
s = swap(s, """const PLAYABLE = ['tim', 'seb', 'byron', 'pearcy', 'kelly', 'marc', 'sam'].map(id => CHAR_BY_ID[id]);""",
         """const PLAYABLE = ['tim', 'seb', 'byron', 'pearcy', 'kelly', 'marc', 'sam', 'thet'].map(id => CHAR_BY_ID[id]);
// Thet stays a silhouette until the campaign's been finished once (or THET is typed on the select screen)
function ladLocked(c) { return !!c && c.id === 'thet' && !settings.thet; }
function unlockThet() { if (settings.thet) return false; settings.thet = true; saveSettings(); return true; }""", 'PLAYABLE')
# a smaller target
s = swap(s, """half: c.look.build > 1.2 ? 26 : 20, flash: 0,""", """half: c.id === 'thet' ? 15 : c.look.build > 1.2 ? 26 : 20, flash: 0,""", 'Thet hitbox')
s = swap(s, """const COMBO_OF = { tim: 'quick', marc: 'quick', byron: 'quick', seb: 'heavy', pearcy: 'heavy', kelly: 'kelly', sam: 'sam' };""",
         """const COMBO_OF = { tim: 'quick', marc: 'quick', byron: 'quick', seb: 'heavy', pearcy: 'heavy', kelly: 'kelly', sam: 'sam', thet: 'quick' };""", 'Thet combo')
s = swap(s, """  sam: { name: 'BLOWS A KISS', hit: [0.36], end: 0.74, r: 132, dmg: 17, word: 'MWAH!', hearts: true },
};""", """  sam: { name: 'BLOWS A KISS', hit: [0.36], end: 0.74, r: 132, dmg: 17, word: 'MWAH!', hearts: true },
  thet: { name: 'ANKLE BITER', hit: [0.1, 0.2, 0.3, 0.4], end: 0.6, r: 92, slide: 720, dmg: 6, word: 'TRIPPED!' },
};""", 'Thet mini')

# ---------------------------------------------------------------- his sheet
meta = json.dumps(META['meta'], separators=(',', ':'))
s = swap(s, """const SPRITE_META = {""", """const SPRITE_META = {"thet":""" + meta + """,""", 'Thet sprite meta')
s = swap(s, """const LAD_FRAMES = {""", """const LAD_FRAMES = {
  thet: """ + META['frames'] + """,""", 'Thet frames')

# ---------------------------------------------------------------- AMBUSH
s = swap(s, """  if (sp === 'sleepy') return sleepySam(p, dt, pw);
  return false;
}""", """  if (sp === 'sleepy') return sleepySam(p, dt, pw);
  if (sp === 'ambush') return ambushSp(p, dt, pw);
  return false;
}
// AMBUSH (Thet): into the undergrowth, bushes pop up across the screen, and he comes out of each one in turn
function ambushSp(p, dt, pw) {
  p.vx = 0; p.vy = 0;
  if (!p.spDove && p.t > 0.32) {
    p.spDove = true; p.spHide = true; sfx('swing'); dust(p.x, p.y, 6, 60);
    // a bush by each of the nearest foes on screen, topped up to four with a few anywhere
    const tg = foes.filter(f => canBeHit(f) && f.x > cam.x + 20 && f.x < cam.x + W - 20).sort((a, b) => Math.abs(a.x - p.x) - Math.abs(b.x - p.x)).slice(0, 5);
    const spots = tg.map(f => ({ x: clamp(f.x + (f.x > p.x ? -46 : 46), cam.x + 50, cam.x + W - 50), y: clamp(f.y + 4, FT + 6, FB - 4) }));
    while (spots.length < 4) spots.push({ x: cam.x + rand(90, W - 90), y: rand(FT + 16, FB - 12) });
    spots.sort((a, b) => Math.abs(a.x - p.x) - Math.abs(b.x - p.x));
    S.bushes = (S.bushes || []).concat(spots.map((b, i) => ({ x: b.x, y: b.y, t: -0.08 * i, at: 0.3 + i * 0.36, out: false, life: 0.3 + i * 0.36 + 1.6, own: p })));
    p.spBushes = spots.length;
  }
  if (p.spDove) {
    const mine = (S.bushes || []).filter(b => b.own === p);
    for (const b of mine) {
      if (b.out || p.t - 0.32 < b.at) continue;
      // out he comes: legs taken out round the bush
      b.out = true; b.shake = 0;
      const tg = foes.filter(f => canBeHit(f)).sort((a, c) => Math.abs(a.x - b.x) - Math.abs(c.x - b.x))[0];
      p.x = b.x; p.y = b.y; p.face = tg ? (Math.sign(tg.x - b.x) || 1) : p.face; p.spHide = false; p.spOutT = 0;
      sfx('hit'); sfx('heavy'); addShake(5); dust(b.x, b.y, 8, 70);
      for (let i = 0; i < 6; i++) parts.push({ k: 'debris', x: b.x + rand(-18, 18), y: b.y, z: rand(10, 40), vx: rand(-120, 120), vz: rand(120, 260), t: 0, life: 0.6, r: 3, col: pick(['#3f6b2a', '#5d8c34', '#2c4a1e']), rot: 0, vr: 6 });
      radialHit(p, b.x + p.face * 26, b.y, 96, { sp: true, dmg: 15 * pw, kd: true, kb: 320, hs: 0.05 });
      if (!p.spWord) { p.spWord = true; popWord(b.x, b.y, 150, 'GOTCHA!', false); }
    }
    if (p.spOutT != null) {
      p.spOutT += dt;
      const left = mine.some(b => !b.out);
      if (left && p.spOutT > 0.3) { p.spHide = true; p.spOutT = null; }
    }
    if (mine.length && mine.every(b => b.out) && p.spOutT != null && p.spOutT > 0.42) { p.spHide = false; p.spOutT = null; endSpecial(p); }
  }
  if (p.t > 4) { p.spHide = false; p.spOutT = null; endSpecial(p); }
  return true;
}""", 'AMBUSH special')
s = swap(s, """  p.spWhistle = false; p.spDove = false; p.spGhost = p.spInf = p.spYawn = p.spZ = p.spSnore = p.spWake = false; p.headK = 1;""",
         """  p.spWhistle = false; p.spDove = false; p.spGhost = p.spInf = p.spYawn = p.spZ = p.spSnore = p.spWake = false; p.headK = 1;
  p.spHide = false; p.spOutT = null; p.spWord = false;""", 'special flags')
# the bushes: pop up, rustle, then shrink away
s = swap(s, """function updateLadFx(dt) {
  if (!S) return;""", """function updateLadFx(dt) {
  if (!S) return;
  if (S.bushes && S.bushes.length) { for (const b of S.bushes) b.t += dt; S.bushes = S.bushes.filter(b => b.t < b.life); }""", 'bush update')
s = swap(s, """  for (const k of (S.koalas || [])) if (k.t >= 0) list.push({ y: k.y + 2, f: () => drawKoala(k) });
}""", """  for (const k of (S.koalas || [])) if (k.t >= 0) list.push({ y: k.y + 2, f: () => drawKoala(k) });
  for (const b of (S.bushes || [])) if (b.t >= 0) list.push({ y: b.y - 3, f: () => drawBush(b) });
}
function drawBush(b) {
  const img = bgImg('fx/bush'); if (!img) return;
  const pop = Math.min(1, b.t / 0.16), gone = clamp((b.life - b.t) / 0.3, 0, 1), k = 2 * (pop < 1 ? 0.4 + 0.75 * pop : 1) * gone;
  const near = !b.out && b.t > b.at - 0.3, wob = near ? Math.sin(time * 60) * 3 : 0;
  const sx = Math.round((b.x - cam.x + wob) / 2) * 2, sy = Math.round(b.y / 2) * 2;
  ctx.save(); ctx.imageSmoothingEnabled = false;
  ctx.drawImage(img, sx - img.width * k / 2, sy - img.height * k + 6, img.width * k, img.height * k * (b.out && b.t < b.at + 0.5 ? 0.9 : 1));
  ctx.restore();
}""", 'bush draw')
s = swap(s, """function drawEntity(e) {
  if (e.car) { drawEspace(e); return; }""", """function drawEntity(e) {
  if (e.car) { drawEspace(e); return; }
  if (e.spHide) return;   // Thet in the bushes""", 'hide in bushes')
s = swap(s, """      // play the lad's own special animation over its wind-up, then hold the last frame""",
         """      // Thet: the dive, then the spring out of each bush
      if (sp === 'ambush' && F.special) {
        const n = F.special.length, half = Math.floor(n / 2);
        if (e.spOutT != null) return ['special', F.special[Math.min(n - 1, half + Math.floor(e.spOutT / 0.3 * (n - half)))]];
        return ['special', F.special[Math.min(half - 1, Math.floor(t / 0.32 * half))]];
      }
      // play the lad's own special animation over its wind-up, then hold the last frame""", 'ambush frames')

# ---------------------------------------------------------------- locked until the campaign's done
# Tim's helpers never include a lad you haven't unlocked
s = swap(s, """  const pool = PLAYABLE.filter(c => c.id !== p.def.id), two = [];""",
         """  const pool = PLAYABLE.filter(c => c.id !== p.def.id && !ladLocked(c)), two = [];""", 'allies pool')
# 2D select (the fallback when there's no 3D)
s = swap(s, """  if (pressed.has('left')) { sel = (sel + n - 1) % n; sfx('swing'); }
  if (pressed.has('right')) { sel = (sel + 1) % n; sfx('swing'); }""", """  const stepSel = d => { do { sel = (sel + d + n) % n; } while (ladLocked(PLAYABLE[sel])); sfx('swing'); };
  if (pressed.has('left')) stepSel(-1);
  if (pressed.has('right')) stepSel(1);
  if (typed.endsWith('THET') && unlockThet()) { typed = ''; sfx('jackpot'); showBanner('THET UNLOCKED', 'He was there the whole time', 2.4); }""", '2D select stepping')
s = swap(s, """    PLAYABLE.forEach((c, i) => { const x = tileX(i); if (t.x > x && t.x < x + TILE.w && t.y > TILE.y - 8 && t.y < TILE.y + TILE.h) { used = true; if (sel === i) go = true; else { sel = i; sfx('swing'); } } });""",
         """    PLAYABLE.forEach((c, i) => { const x = tileX(i); if (t.x > x && t.x < x + TILE.w && t.y > TILE.y - 8 && t.y < TILE.y + TILE.h) { used = true; if (ladLocked(c)) sfx('nope'); else if (sel === i) go = true; else { sel = i; sfx('swing'); } } });""", '2D select taps')
s = swap(s, """    { const pi = portraitImg(ch.id); if (pi) { ctx.imageSmoothingEnabled = false; ctx.drawImage(pi, x + TILE.w / 2 - 36, y - 6, 72, 72); }""",
         """    if (ladLocked(ch)) { ctx.font = '40px ' + DISPLAY; ctx.fillStyle = '#3b4f58'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText('?', x + TILE.w / 2, y + 30); }
    else { const pi = portraitImg(ch.id); if (pi) { ctx.imageSmoothingEnabled = false; ctx.drawImage(pi, x + TILE.w / 2 - 36, y - 6, 72, 72); }""", '2D select locked tile')
s = swap(s, """    ctx.fillText(ch.name, x + TILE.w / 2, y + TILE.h - 11);
  });""", """    ctx.fillText(ladLocked(ch) ? '???' : ch.name, x + TILE.w / 2, y + TILE.h - 11);
  });""", '2D select locked name')
# the online lobby: a locked lad can't be picked
s = swap(s, """for (let k = 0; k < n; k++) { i = (i + d + n) % n; if (!netLadTaken(i)) break; }""",
         """for (let k = 0; k < n; k++) { i = (i + d + n) % n; if (!netLadTaken(i) && !ladLocked(PLAYABLE[i])) break; }""", 'lobby stepping')
s = swap(s, """t.y > TILE.y - 8 && t.y < TILE.y + TILE.h && !netLadTaken(i)) { NL.lad = i;""",
         """t.y > TILE.y - 8 && t.y < TILE.y + TILE.h && !netLadTaken(i) && !ladLocked(c)) { NL.lad = i;""", 'lobby taps')
s = swap(s, """      const pi = portraitImg(ch.id); if (pi) { ctx.globalAlpha = taken ? 0.3 : 1;""",
         """      const pi = ladLocked(ch) ? null : portraitImg(ch.id); if (pi) { ctx.globalAlpha = taken ? 0.3 : 1;""", 'lobby locked tile')

# ---------------------------------------------------------------- the unlock: finish the campaign
s = swap(s, """    if (!settings.unlocked) lines.push(['sys', 'One stage is still hidden. The fruit machine at the Social looks lucky.']);
    openChat(lines, winGame);""", """    if (!settings.unlocked) lines.push(['sys', 'One stage is still hidden. The fruit machine at the Social looks lucky.']);
    if (!settings.thet) lines.push(['sys', 'Thet joined the group'], ['thet', 'been here the whole time lads'], ['thet', 'you just never look down']);
    openChat(lines, winGame);""", 'ending lines')
s = swap(s, """function winGame() {
  if (!NET.on) clearSavedRun();""", """let challenger = null;
function winGame() {
  if (!NET.on) clearSavedRun();
  if (unlockThet()) { challenger = { t: 0 }; setTimeout(() => { sfx('airhorn'); sfx('incoming'); }, 300); }""", 'unlock on win')
s = swap(s, """  if (modeT > 1.4 && (pressed.has('punch') || pressed.has('start') || taps.length)) openNameEntry();""",
         """  if (modeT > (challenger ? 4.6 : 1.4) && (pressed.has('punch') || pressed.has('start') || taps.length)) { challenger = null; openNameEntry(); }""", 'win screen wait')
s = swap(s, """  if (mode !== 'pause') drawBanner();""", """  if (mode !== 'pause') drawBanner();
  if (mode === 'win' && challenger) drawChallenger();""", 'challenger render')
s = swap(s, """function resultLabel() {""", """// A NEW CHALLENGER HAS ARRIVED: Thet slides in over the win screen the first time the campaign's finished
function drawChallenger() {
  const t = modeT; if (t > 5.2) { challenger = null; return; }
  const a = Math.min(1, t / 0.25, (5.2 - t) / 0.4);
  ctx.save(); ctx.globalAlpha = a;
  ctx.fillStyle = 'rgba(6,4,14,0.97)'; ctx.fillRect(0, 0, W, H);
  if (Math.floor(t * 6) % 2 || t > 1.4) textOut('A NEW CHALLENGER', W / 2, 96, '42px ' + DISPLAY, '#ff5a3c', OUT, 8, 'center');
  if (t > 0.5) textOut('HAS ARRIVED', W / 2, 146, '30px ' + DISPLAY, '#ffd23f', OUT, 7, 'center');
  const sh = ladSprite('thet');
  if (sh && sh.ready) {
    const m = sh.m, row = m.rows.idle[0], k = 5, slide = easeOut(clamp((t - 0.6) / 0.5, 0, 1)), x = W + 120 - (W / 2 + 120) * slide, f = 1 + Math.floor(t * 7) % (m.rows.idle[1] - 1);
    ctx.fillStyle = 'rgba(0,0,0,0.4)'; ctx.fillRect(x - 70, 418, 140, 10);
    ctx.imageSmoothingEnabled = false; ctx.drawImage(sh.img, f * m.cell, row * m.cell, m.cell, m.cell, x - m.ax * k, 424 - m.ay * k, m.cell * k, m.cell * k);
  }
  if (t > 1.3) { textOut('THET', W / 2, 470, '34px ' + DISPLAY, '#efe6d2', OUT, 7, 'center'); ctx.font = '600 15px ' + BODY; ctx.fillStyle = '#93a3a1'; ctx.textAlign = 'center'; ctx.fillText('Now playable. Pick him on the select screen.', W / 2, 505); }
  ctx.restore();
}
function resultLabel() {""", 'challenger draw')

# the HUD face: Thet drawn bigger so his head fills the box like everyone else's
s = swap(s, """  drawHuman({ look: p.look, def: p.def, face: 1, state: 'idle', t: 0, z: 0, walk: 0, vx: 0, vy: 0, flash: 0 }, 46, 170, 1.15);""",
         """  drawHuman({ look: p.look, def: p.def, face: 1, state: 'idle', t: 0, z: 0, walk: 0, vx: 0, vy: 0, flash: 0 }, 46, 170, p.def.id === 'thet' ? 1.15 * 62 / SPRITE_META.thet.h : 1.15);""", 'HUD face')

# ---------------------------------------------------------------- portrait and credits
s = swap(s, '"fx/koala", ', '"fx/bush", "fx/koala", ', 'bush preload')
s = swap(s, '"portraits/tim"', '"portraits/thet", "portraits/tim"', 'portrait preload')
s = swap(s, """const PORTRAIT_IDS = ['tim', 'seb', 'byron', 'pearcy', 'kelly', 'marc', 'sam', 'denise', 'jo', 'nozzer'];""",
         """const PORTRAIT_IDS = ['tim', 'seb', 'byron', 'pearcy', 'kelly', 'marc', 'sam', 'thet', 'denise', 'jo', 'nozzer'];""", 'portrait ids')
s = swap(s, """['lad', 'sam', 'SAM', 'Sells AI. Does ice baths.'], ['gap'],""",
         """['lad', 'sam', 'SAM', 'Sells AI. Does ice baths.'], ['lad', 'thet', 'THET', 'Pocket-sized. Fully camouflaged.'], ['gap'],""", 'credits')

# ---------------------------------------------------------------- the 3D select (also in tools/title3d/title3d.js)
T3 = [
    ("""  const ORDER = ['marc', 'sam', 'seb', 'tim', 'byron', 'pearcy', 'kelly'];""",
     """  const ORDER = ['marc', 'sam', 'seb', 'tim', 'byron', 'pearcy', 'kelly', 'thet'];   // Thet on the end (Version 50), a silhouette until unlocked
  const MID = (ORDER.length - 1) / 2;""", '3D order'),
    ("""  const POSES = { tim: 1, seb: 1, byron: 1, pearcy: 1, kelly: 1, marc: 1, sam: 1 };""",
     """  const POSES = { tim: 1, seb: 1, byron: 1, pearcy: 1, kelly: 1, marc: 1, sam: 1, thet: 1 };""", '3D poses'),
    ("""marc: ['G\\u2019DAY, LADS!', 'cooee'], sam: ['I\\u2019M UP, I\\u2019M UP!', 'yawn'] };""",
     """marc: ['G\\u2019DAY, LADS!', 'cooee'], sam: ['I\\u2019M UP, I\\u2019M UP!', 'yawn'], thet: ['CAN\\u2019T SEE ME!', 'incoming'] };""", '3D pick shout'),
    ("""      const a = ladAtlas(id, img['lad_' + id], img['pose_' + id]), depth = Math.abs(i - 3);""",
     """      const a = ladAtlas(id, img['lad_' + id], img['pose_' + id]), depth = Math.abs(i - MID);""", '3D lineup depth'),
    ("""tx: (i - 3) * 50, tz: 24 - depth * 18, delay: (6 - i) * 0.13,""",
     """tx: (i - MID) * 50, tz: 24 - depth * 18, delay: (ORDER.length - 1 - i) * 0.13,""", '3D lineup spacing'),
    ("""      const spots = [[-124, -40], [124, -60], [-140, -130], [140, -150], [-118, -220], [118, -240]];""",
     """      const spots = [[-124, -40], [124, -60], [-140, -130], [140, -150], [-118, -220], [118, -240], [0, -290]];""", '3D stage spots'),
    ("""      const spots = [[44, -26], [-40, -38], [88, -56], [-82, -70], [130, -86], [-124, -102]];""",
     """      const spots = [[44, -26], [-40, -38], [88, -56], [-82, -70], [130, -86], [-124, -102], [170, -118]];""", '3D diff spots'),
    ("""    const L = chosen(), id = L.id, P = PICK[id] || ['', 'start'];""",
     """    const L = chosen(), id = L.id, P = PICK[id] || ['', 'start'];
    if (ladLocked(CHAR_BY_ID[id])) { sfx('nope'); toast('LOCKED'); return; }""", '3D pick locked'),
    ("""    if (view === 'lad' && !picking) { if (P('left')) chooseLad((li + 6) % 7); if (P('right')) chooseLad((li + 1) % 7); }""",
     """    if (view === 'lad' && !picking) { const n = ORDER.length; if (P('left')) chooseLad((li + n - 1) % n); if (P('right')) chooseLad((li + 1) % n); }""", '3D lad stepping'),
    ("""      settings.unlocked = true; saveSettings(); typed = ''; sfx('jackpot'); toast('RAMSDEN UNLOCKED');
      if (view === 'stage') renderStage();
    }""", """      settings.unlocked = true; saveSettings(); typed = ''; sfx('jackpot'); toast('RAMSDEN UNLOCKED');
      if (view === 'stage') renderStage();
    }
    if (typed.endsWith('THET') && unlockThet()) { typed = ''; sfx('jackpot'); toast('THET UNLOCKED'); if (view === 'lad') renderLad(); }""", '3D unlock code'),
    ("""    const c = CHAR_BY_ID[chosen().id], mm = MINI[c.id];
    q('name').textContent = c.name; q('name').style.color = c.color;
    q('ltag').textContent = c.tag;""", """    const c = CHAR_BY_ID[chosen().id], mm = MINI[c.id], lk = ladLocked(c);
    q('name').textContent = lk ? '???' : c.name; q('name').style.color = lk ? 'var(--t3grey)' : c.color;
    q('ltag').textContent = lk ? 'Someone is hiding in the bushes. Finish the campaign to find out who.' : c.tag;""", '3D locked name'),
    ("""<b class="${k < c.stats[j] ? 'f' : ''}"></b>""", """<b class="${k < (lk ? 0 : c.stats[j]) ? 'f' : ''}"></b>""", '3D locked stats'),
    ("""    q('special').textContent = c.special; q('blurb').textContent = c.blurb;
    q('mini').textContent = mm ? mm.name : '';""", """    q('special').textContent = lk ? '???' : c.special; q('blurb').textContent = lk ? '' : c.blurb;
    q('mini').textContent = lk ? '???' : mm ? mm.name : '';""", '3D locked moves'),
    ("""    q('pick').textContent = 'PICK ' + c.name; q('pick').disabled = false;
    q('roster').innerHTML = ORDER.map((id, i) => `<button type="button" data-i="${i}" aria-pressed="${i === li}" style="--c:${CHAR_BY_ID[id].color}">${CHAR_BY_ID[id].name}</button>`).join('');""",
     """    q('pick').textContent = lk ? 'LOCKED' : 'PICK ' + c.name; q('pick').disabled = lk;
    q('roster').innerHTML = ORDER.map((id, i) => `<button type="button" data-i="${i}" aria-pressed="${i === li}" style="--c:${ladLocked(CHAR_BY_ID[id]) ? '#5a6068' : CHAR_BY_ID[id].color}">${ladLocked(CHAR_BY_ID[id]) ? '???' : CHAR_BY_ID[id].name}</button>`).join('');""", '3D locked roster'),
    ("""      L.tint.lerp(V3(...tt), damp(L.act && L.act.kind === 'pick' ? 3 : 5, dt)); L.m.material.uniforms.tint.value.copy(L.tint);""",
     """      if (ladLocked(CHAR_BY_ID[L.id])) tt.fill(0.04);   // a black silhouette until he's unlocked
      L.tint.lerp(V3(...tt), damp(L.act && L.act.kind === 'pick' ? 3 : 5, dt)); L.m.material.uniforms.tint.value.copy(L.tint);""", '3D silhouette'),
]
for o, n, l in T3:
    s = swap(s, o, n, l)

open(PAGE, 'w', encoding='utf-8').write(s)
print('v50_build: web/index.html updated')

# keep the title3d source in step, so tools/title3d_build.py carries the same code
SRC = os.path.join(ROOT, 'tools', 'title3d', 'title3d.js')
j = open(SRC, encoding='utf-8').read()
for o, n, l in T3:
    j = swap(j, o, n, l + ' (title3d.js)')
open(SRC, 'w', encoding='utf-8').write(j)
