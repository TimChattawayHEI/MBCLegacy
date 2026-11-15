// ================================================================== Version 85: THE RUN BACK (Orpington 2001)
// After Mick, the lads have to make the 10.30 Atlantis coach outside Ram Ba Ba. An auto-runner up the High Street, right to
// left, from Ye Olde Blacksmith past the car park to Ram Ba Ba. The lad runs by himself: up and down change lane, JUMP
// clears the low stuff (bollards, bins, kegs), A-boards and people have to be gone round, forward sprints and back eases
// off. Each knock costs a stumble. The clock runs down to 10.30; miss the coach and the run starts again (no life lost).
// Art: web/bg/orp/run_*.png (tools/v85/runback_art.py): the street (the two Meshy paintings with the gap between them
// painted by PixelLab) scrolls slowly behind; the pavement repeats under the runner at full speed.
const RUN = { D: 11000, base: 400, fast: 500, slow: 300, PX: 640, lanes: [414, 437, 460], g: 1700, jump: 560 };
const RUN_OBS = {
  bollard: { img: 'orp/run_bollard', sc: 2, half: 10, h: 44, jump: true },
  bin:     { img: 'props/bin', sc: 2, half: 22, h: 66, jump: true },
  keg:     { img: 'props/keg', sc: 2, half: 20, h: 62, jump: true },
  aboard:  { img: 'props/aboard', sc: 2, half: 44, h: 96 },
  ped:     { half: 18, h: 130, ped: true },
};
const RUN_PEDS = ['regular', 'codger', 'townie', 'scrunchie', 'kappa', 'builder'];
const RUN_OI = ['OI!', 'WATCH IT!', 'MIND OUT!', 'OW!', 'STEADY ON!'];
const RUN_LINES = { start: ['COACH! RUN!', "It's gone half ten!", 'Leg it!'], made: ['MADE IT!', "Budge up!", 'Get in!'] };
['orp/run_street', 'orp/run_ground', 'orp/run_bollard', 'orp/run_coach'].forEach(k => { bgImg(k); });
setTimeout(() => ASSET_BG.push('orp/run_street', 'orp/run_ground', 'orp/run_bollard', 'orp/run_coach'), 0);
STAGES.orp_run = { era: 2001, title: 'THE RUN BACK', sub: '10.26pm. The Atlantis coach goes at half ten.', bg: 'orp_run', ft: 404, fb: 470, len: W,
  music: 'codered', aggro: 0, aa: 0, intro: 'orpRun', run: true, fixed: true, waves: [] };
ROUTE.splice(ROUTE.indexOf('orp_atlantis'), 0, 'orp_run');
ROUTE.forEach((k, i) => { STAGES[k].n = i + 1; });
BOSS_MUSIC.orp_run = 'boss1999';
CHATS.orpRun = [
  ['sys', 'The Blacksmiths. 10:26pm.'],
  ['seb', 'COACH GOES @ HALF 10'],
  ['marc', 'ATLANTIS LADS!!!'],
  ['byron', 'is mick still cumin?'],
  ['tim', 'dnt look back. just run'],
];
function runLimit() { return ({ easy: 36, normal: 31, hard: 28 })[(run && run.diff) || 'normal'] || 31; }
function runStart() {
  S.rb = { phase: 'intro', t: 0, d: 0, speed: 0, y: RUN.lanes[1], z: 0, vz: 0, stumble: 0, inv: 0, hits: 0, clean: 0, jumps: 0,
    left: runLimit(), obs: [], next: 700, tries: (S.rb && S.rb.tries) || 0, walk: 0 };
  cam.x = 0; ST.len = W;
  for (const q of players()) { q.x = -9999; q.state = 'idle'; q.vx = q.vy = 0; }
}
// a beat of obstacles: one, a pair in two lanes, or a person walking down the middle
function runSpawn(r) {
  const at = r.next, L = RUN.lanes, roll = Math.random(), progress = r.d / RUN.D;
  const add = (kind, lane, extra) => r.obs.push(Object.assign({ kind, x: at + rand(-20, 20), y: L[lane], hit: false, passed: false }, extra || {}));
  const low = () => pick(['bollard', 'bollard', 'bin', 'keg']);
  if (roll < 0.3) add(low(), Math.floor(Math.random() * 3));
  else if (roll < 0.55) { const a = Math.floor(Math.random() * 3); add('aboard', a); if (progress > 0.25) add(low(), (a + 1 + Math.floor(Math.random() * 2)) % 3); }
  else if (roll < 0.8) add('ped', Math.floor(Math.random() * 3), { who: pick(RUN_PEDS), walk: Math.random() * 6, vx: rand(50, 90) });
  else { const gap = Math.floor(Math.random() * 3); for (let i = 0; i < 3; i++) if (i !== gap) add(i === (gap + 1) % 3 ? low() : 'bollard', i); }
  r.next += rand(420, 640) - progress * 120;
}
function runOver(r, o) {
  const m = RUN_OBS[o.kind]; o.hit = true;
  r.hits++; r.stumble = 0.75; r.inv = 1.3; r.speed = 90; addShake(5); sfx('thud'); sfx('ouch');
  popWord(RUN.PX - 20, r.y, 150, m.ped ? pick(RUN_OI) : 'OOF!', false);
  if (m.ped) o.annoyed = 1;
}
function runTick(dt) {
  const r = S.rb; if (!r) return false;
  r.t += dt;
  const p = player, inp = readInput();
  for (const q of players()) if (q !== p) { q.x = -9999; q.vx = q.vy = 0; }
  if (r.phase === 'intro') {
    r.speed = Math.min(RUN.base, r.speed + 600 * dt);
    if (r.t > 0.2 && !r.said) { r.said = true; say(p, pick(RUN_LINES.start), 1.8, true); }
    if (r.t > 1.6) { r.phase = 'run'; r.t = 0; showBanner('RUN!', 'Up and down to change lanes. JUMP the low stuff. Forward to sprint.', 2.6); }
  } else if (r.phase === 'run') {
    r.left -= dt;
    const want = r.stumble > 0 ? 90 : inp.ix < 0 ? RUN.fast : inp.ix > 0 ? RUN.slow : RUN.base;
    r.speed += (want - r.speed) * Math.min(1, dt * (r.stumble > 0 ? 10 : 3));
    if (r.stumble <= 0) r.y = clamp(r.y + inp.iy * 300 * dt, RUN.lanes[0] - 6, RUN.lanes[2] + 6);
    if ((pressed.has('jump') || pressed.has('punch')) && r.z <= 0 && r.stumble <= 0) { r.vz = RUN.jump; r.jumps++; sfx('jump'); }
    if (r.d + 1400 > r.next && r.next < RUN.D - 500) runSpawn(r);
    if (r.d >= RUN.D) { r.phase = 'made'; r.t = 0; say(p, pick(RUN_LINES.made), 2, true); sfx('cheer'); showBanner('MADE IT!', 'Ram Ba Ba, ' + runClock(r) + '. The coach is waiting.', 2.4); }
    else if (r.left <= 0) { r.phase = 'missed'; r.t = 0; musicSet(null); sfx('honk'); showBanner('MISSED IT', 'The coach has gone. Run it again.', 2.4); }
  } else if (r.phase === 'made') {
    r.speed = Math.max(0, r.speed - 500 * dt);
    if (r.t > 2.2 && !r.done) { r.done = true; S.done = true; finishStage(); }
  } else if (r.phase === 'missed') {
    r.speed = Math.max(0, r.speed - 400 * dt); r.coachGo = (r.coachGo || 0) + dt;
    if (r.t > 2.6) { const tries = r.tries + 1; runStart(); S.rb.tries = tries; musicSet(ST.music); }
  }
  if (r.stumble > 0) r.stumble -= dt; if (r.inv > 0) r.inv -= dt;
  r.d = Math.min(RUN.D + 400, r.d + r.speed * dt);
  r.vz -= RUN.g * dt; r.z = Math.max(0, r.z + r.vz * dt); if (r.z <= 0) { if (r.vz < -200) sfx('land'); r.vz = 0; }
  r.walk += dt * r.speed / 20;
  // the obstacles: in reach when level with the runner (they stand still; people walk towards him)
  for (const o of r.obs) {
    const m = RUN_OBS[o.kind];
    if (m.ped) { o.x -= o.vx * dt; o.walk += dt * 6; if (o.annoyed) o.annoyed = Math.max(0, o.annoyed - dt); }
    const dx = Math.abs(o.x - r.d);
    if (!o.hit && !o.passed && dx < m.half + 14 && Math.abs(o.y - r.y) < 15 && r.inv <= 0 && r.phase === 'run') {
      if (m.jump && r.z > m.h * 0.55) { o.cleared = true; } else runOver(r, o);
    }
    if (!o.passed && o.x < r.d - m.half - 20) { o.passed = true; if (!o.hit) r.clean++; }
  }
  r.obs = r.obs.filter(o => o.x > r.d - 900);
  // the runner, drawn as the player
  p.x = RUN.PX; p.y = r.y; p.z = r.z; p.face = -1; p.vx = -r.speed; p.vy = 0; p.walk = r.walk; p.vz = r.vz;
  if (r.stumble > 0) { if (p.state !== 'hurt') { p.state = 'hurt'; p.t = 0; } p.t += dt; }
  else p.state = r.z > 0 ? 'jump' : r.speed > 40 ? 'run' : 'idle';
  if (p.state !== 'hurt') p.t = (p.t || 0) + dt;
  p.inv = r.inv > 0 && r.phase === 'run' ? r.inv : 0;
  return true;
}
function runClock(r) {   // 10:26:00 to 10:30:00 over the time allowed
  const g = clamp((runLimit() - r.left) / runLimit(), 0, 1) * 240, m = 26 + Math.floor(g / 60), sec = Math.floor(g % 60);
  return '10:' + String(Math.min(30, m)).padStart(2, '0') + ':' + String(m >= 30 ? 0 : sec).padStart(2, '0');
}
// the street behind, the pavement under, the coach at the end
function runBg() {
  const r = S.rb; if (!r) { ctx.fillStyle = '#0b0c1a'; ctx.fillRect(0, 0, W, H); return; }
  const st = bgImg('orp/run_street'), gr = bgImg('orp/run_ground');
  ctx.save(); ctx.imageSmoothingEnabled = false;
  ctx.fillStyle = '#0d1430'; ctx.fillRect(0, 0, W, H);
  if (st) { const k = clamp(r.d / RUN.D, 0, 1), sx = (st.width * 2 - W) * (1 - k); ctx.drawImage(st, Math.round(-sx / 2) * 2, 0, st.width * 2, st.height * 2); }
  if (gr) { const tw = gr.width * 2, off = ((r.d % tw) + tw) % tw; for (let x = off - tw; x < W; x += tw) ctx.drawImage(gr, Math.round(x / 2) * 2, 402, tw, gr.height * 2); }
  ctx.restore();
}
function runDraw(list) {
  const r = S.rb; if (!r) return;
  const sx = o => RUN.PX - (o - r.d);
  for (const o of r.obs) {
    const m = RUN_OBS[o.kind], x = sx(o.x); if (x < -120 || x > W + 120) continue;
    if (m.ped) list.push({ y: o.y, f: () => { pubFoe(o.who, x, o.y, 'walk', 1, o.walk); } });
    else list.push({ y: o.y, f: () => { const img = bgImg(m.img); if (!img) return; ctx.save(); ctx.imageSmoothingEnabled = false;
      ctx.fillStyle = 'rgba(0,0,0,0.28)'; ctx.beginPath(); ctx.ellipse(x, o.y + 2, m.half + 4, 5, 0, 0, Math.PI * 2); ctx.fill();
      ctx.drawImage(img, Math.round((x - img.width * m.sc / 2) / 2) * 2, Math.round(o.y / 2) * 2 - (img.height - 2) * m.sc, img.width * m.sc, img.height * m.sc); ctx.restore(); } });
  }
  // the coach, waiting on the road outside Ram Ba Ba (pulls away if he's missed it)
  const c = bgImg('orp/run_coach'), cx = sx(RUN.D + 260) - (r.coachGo ? r.coachGo * r.coachGo * 180 : 0);
  if (c && cx > -500 && cx < W + 500) list.push({ y: 530, f: () => { ctx.save(); ctx.imageSmoothingEnabled = false; ctx.drawImage(c, Math.round((cx - c.width) / 2) * 2, 530 - c.height * 2, c.width * 2, c.height * 2); ctx.restore(); } });
}
function runHud() {
  const r = S.rb; if (!r) return;
  ctx.save();
  const x0 = 330, x1 = 630, y = 104, p = clamp(r.d / RUN.D, 0, 1);
  ctx.fillStyle = 'rgba(12,16,20,0.6)'; ctx.fillRect(x0 - 12, y - 6, x1 - x0 + 24, 40);
  ctx.fillStyle = '#2b3b42'; ctx.fillRect(x0, y, x1 - x0, 8); ctx.fillStyle = '#f2a23a'; ctx.fillRect(x1 - (x1 - x0) * p, y, (x1 - x0) * p, 8);
  ctx.font = '800 11px ' + BODY; ctx.textAlign = 'left'; ctx.fillStyle = '#93a3a1'; ctx.fillText('RAM BA BA', x0, y + 26);
  ctx.textAlign = 'right'; ctx.fillText('BLACKSMITHS', x1, y + 26);
  const low = r.left < 8 && r.phase === 'run';
  textOut(runClock(r), W / 2, 62, '40px ' + DISPLAY, low && Math.floor(time * 4) % 2 ? '#ff6a4a' : '#ffd23f', OUT, 7, 'center');
  ctx.font = '800 12px ' + BODY; ctx.fillStyle = '#efe6d2'; ctx.textAlign = 'center'; ctx.fillText('COACH AT 10.30' + (r.tries ? '   ·   TRY ' + (r.tries + 1) : ''), W / 2, 90);
  ctx.restore();
}
function runRows(add) {
  const r = S.rb; if (!r) return;
  add('Made the coach', 4000);
  add('Time to spare', Math.max(0, Math.round(r.left)) * 250);
  add('Clean run (no knocks)', r.hits === 0 ? 5000 : 0);
  add('Dodged x' + r.clean, r.clean * 100);
}
function runRank() {
  const r = S.rb || {}; let p = 0;
  p += r.hits === 0 ? 3 : r.hits <= 2 ? 2 : r.hits <= 5 ? 1 : 0;
  p += r.left >= 6 ? 2 : r.left >= 3 ? 1 : 0;
  p += r.tries ? 0 : 1;
  return p >= 6 ? 'S' : p >= 5 ? 'A' : p >= 3 ? 'B' : p >= 2 ? 'C' : 'D';
}
