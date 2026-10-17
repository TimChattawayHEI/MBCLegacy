"""Version 49: polish for the big moments.

Patches web/index.html in place (run from the repo root, after tools/v47_build.py):  python3 tools/v49_build.py
Safe to run again.

- Boss finish: the hit that drops a stage's last boss freezes on impact, flashes, the music cuts to silence, the
  camera punches in on him and the game runs in slow motion for a moment before the stage clears.
- Boss intro cards: when a boss arrives, the fight pauses and a card slides across with the boss drawn big, his name
  and his line (the words of the banner he used to get). The far bank pair and Nozzer get one as their wave starts.
  Skippable offline after half a second.
- Stage ranks: S, A, B, C or D on the points screen, from time, hits taken, health left and best chain (on the road,
  from dents and the Espace). The best rank for each stage is kept and shown on the stage list.
Everything that changes the game's timing (slow motion, the card's pause) runs inside the shared game, so online
co-op stays in step; the zoom, the music cut and the saved ranks are local.
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, 'web', 'index.html')


def swap(s, old, new, label):
    if new in s:
        return s
    if s.count(old) != 1:
        sys.exit(f'v49_build: could not find the {label} (found {s.count(old)} matches)')
    return s.replace(old, new)


s = open(PAGE, encoding='utf-8').read()

# ---------------------------------------------------------------- shared helpers
s = swap(s, """function bossDefeated(b) {""", """// ================================================================== Version 49: boss finishes, boss cards, stage ranks
let slowT = 0, finishFX = null;
// the stage's last boss going down: freeze on the hit, flash, silence, slow motion and a punch-in
function isFinalBoss(b) {
  if (!S || !ST || S.waveIdx < ST.waves.length - 1) return false;
  return !S.bosses.some(o => o !== b && !(o.state === 'dead' || o.remove || o.state === 'beaten'));
}
function bossFinish(b) {
  if (!isFinalBoss(b)) return;
  hitstop = Math.max(hitstop, 0.12); slowT = 1.9; flashT = Math.max(flashT, 0.2); addShake(14);
  musicSet(null); sfx('heavy'); sfx('boom');
  spark(b.x, b.y, (b.z || 0) + 80, true); spark(b.x + 20, b.y, (b.z || 0) + 110, true);
  finishFX = { t: 0, x: b.x, y: b.y - (b.z || 0) - (b.fish ? 70 : 80) };
}
// boss intro cards. Bosses who already announce themselves with a banner get the card in its place, with the same
// words, at the moment they arrive; the far bank pair and Nozzer, who had no banner, get one as their wave starts
const BOSS_CARD = {
  farbank: ['THE FAR BANK', "That's our swim, lads.", ['farbank', 'farbank']],
  nozzer: ['NOZZER', 'Did I ever tell you about Lanzarote?', ['nozzer']],
};
const BOSS_BANNER = {
  'THE PARKIE': ['parkie'], 'MASTER CONTROL': ['mc'], 'DENISE': ['denise'], 'LADY ADDICT': ['lady'],
  'BIG GARY': ['fish/gary'], 'BIG GAZ': ['fish/gaz'], 'DON VITO': ['mafioso'], 'BIG TONY AND LITTLE NICKY': ['beast', 'quick'],
  'IL CARABINIERE': ['carab'], 'I FRATELLI': ['gianni', 'marco', 'luca', 'paolo'],
};
function bossCardFor(w) {
  const key = w.boss || (w.mini && !w.fish ? 'nozzer' : null), c = key && BOSS_CARD[key];
  return c ? { t: 0, len: 2.6, name: c[0], line: c[1], spr: c[2] } : null;
}
function bossBannerCard(text, sub) {
  if (mode !== 'play' || !S || !BOSS_BANNER[text]) return false;
  S.card = { t: 0, len: 2.6, name: text, line: sub, spr: BOSS_BANNER[text] };
  return true;
}
function updateBossCard(dt) {
  const c = S.card; c.t += dt;
  if (!c.sfx) { c.sfx = true; sfx('heavy'); sfx('scratch'); }
  const skip = !NET.on && c.t > 0.5 && (pressed.has('punch') || pressed.has('start') || pressed.has('jump') || taps.length);
  if (c.t >= c.len || skip) S.card = null;
}
function drawCardSprite(id, x, base, k) {
  ctx.save(); ctx.imageSmoothingEnabled = false;
  if (id.includes('/')) {
    const img = bgImg(id); if (img) { const kk = k * 0.85; ctx.drawImage(img, x - img.width * kk / 2, base - img.height * kk, img.width * kk, img.height * kk); }
  } else {
    const sh = ladSprite(id);
    if (sh && sh.ready) { const m = sh.m, row = (m.rows.idle || [0])[0], c = m.cell; ctx.drawImage(sh.img, 0, row * c, c, c, x - m.ax * k, base - m.ay * k, c * k, c * k); }
  }
  ctx.restore();
}
function drawBossCard() {
  const c = S.card; if (!c) return;
  const t = c.t, inK = easeOut(clamp(t / 0.32, 0, 1)), outK = clamp((t - (c.len - 0.3)) / 0.3, 0, 1);
  ctx.save();
  ctx.fillStyle = 'rgba(8,6,20,' + (0.55 * (1 - outK)).toFixed(3) + ')'; ctx.fillRect(0, 0, W, H);
  const bandY = 168, bandH = 204;
  ctx.translate((1 - inK) * W - outK * W, 0);
  ctx.fillStyle = 'rgba(16,10,40,0.95)'; ctx.fillRect(0, bandY, W, bandH);
  ctx.fillStyle = '#f2a23a'; ctx.fillRect(0, bandY - 5, W, 5); ctx.fillRect(0, bandY + bandH, W, 5);
  ctx.fillStyle = 'rgba(242,162,58,0.12)'; for (let i = 0; i < 14; i++) ctx.fillRect(((i * 90 + t * 260) % (W + 120)) - 60, bandY, 18, bandH);
  const n = c.spr.length, sk = c.spr[0].includes('/') ? 2.2 : 2.6;
  const gap = n > 1 ? Math.min(130, 330 / (n - 1)) : 0;
  c.spr.forEach((id, i) => drawCardSprite(id, 230 + (i - (n - 1) / 2) * gap, bandY + bandH - 12, sk));
  ctx.font = '800 13px ' + BODY; ctx.fillStyle = '#f2a23a'; ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; ctx.fillText('BOSS', 470, bandY + 50);
  textOut(c.name, 470, bandY + 98, (c.name.length > 20 ? '24px ' : c.name.length > 14 ? '30px ' : '40px ') + DISPLAY, '#ffd23f', OUT, 7, 'left');
  ctx.font = '600 17px ' + BODY; ctx.fillStyle = '#efe6d2'; ctx.textAlign = 'left'; ctx.fillText('\\u201C' + clean(c.line) + '\\u201D', 470, bandY + 146);
  ctx.restore();
}
// stage ranks: points for time, hits taken, health and chain (or dents and the Espace on the road)
const RANKS = 'SABCD';
function stageRanks() { return lsGet('carpdiem.ranks', {}) || {}; }
function stageRank() {
  let p = 0;
  if (ST.drive) {
    const d = S.drv || {}; const dents = d.dents || 0;
    p += dents === 0 ? 4 : dents <= 3 ? 3 : dents <= 7 ? 2 : dents <= 12 ? 1 : 0;
    if (d.wreck) p += 2; if ((d.near || 0) >= 5) p += 1;
    return p >= 6 ? 'S' : p >= 5 ? 'A' : p >= 3 ? 'B' : p >= 2 ? 'C' : 'D';
  }
  const par = ST.fixed ? 110 : 150, hp = player.hp / player.maxHp;
  p += S.time <= par * 0.7 ? 3 : S.time <= par ? 2 : S.time <= par * 1.4 ? 1 : 0;
  p += S.hitsTaken === 0 ? 3 : S.hitsTaken <= 3 ? 2 : S.hitsTaken <= 8 ? 1 : 0;
  p += hp >= 0.7 ? 1 : 0;
  p += S.bestChain >= 20 ? 2 : S.bestChain >= 10 ? 1 : 0;
  return p >= 8 ? 'S' : p >= 6 ? 'A' : p >= 4 ? 'B' : p >= 2 ? 'C' : 'D';
}
function noteRank(key, r) {
  const all = stageRanks(), old = all[key];
  const best = !old || RANKS.indexOf(r) < RANKS.indexOf(old);
  if (best) { all[key] = r; lsSet('carpdiem.ranks', all); }
  return best && !!old;
}
function drawRankStamp() {
  const r = clearInfo && clearInfo.rank; if (!r) return;
  const t = modeT - (0.75 + clearInfo.rows.length * 0.25); if (t < 0) return;
  if (!clearInfo.stamped) { clearInfo.stamped = true; sfx('thud'); sfx(r === 'S' ? 'jackpot' : 'heavy'); }
  const k = t < 0.16 ? 2.4 - 1.4 * (t / 0.16) : 1, x = W - 150, y = 290;
  const col = { S: '#ffd23f', A: '#7fe07a', B: '#6ec3ff', C: '#efe6d2', D: '#93a3a1' }[r];
  ctx.save(); ctx.translate(x, y); ctx.rotate(-0.12); ctx.scale(k, k); ctx.globalAlpha = Math.min(1, t / 0.08);
  rrect(-62, -72, 124, 144, 14); ctx.fillStyle = 'rgba(12,16,20,0.92)'; ctx.fill(); ctx.strokeStyle = col; ctx.lineWidth = 5; ctx.stroke();
  ctx.font = '800 12px ' + BODY; ctx.fillStyle = '#93a3a1'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText('RANK', 0, -50);
  textOut(r, 0, 14, '88px ' + DISPLAY, col, OUT, 8, 'center');
  ctx.restore();
  if (clearInfo.newBest && t > 0.35) textOut('NEW BEST!', x, y + 100, '17px ' + DISPLAY, '#7fe07a', OUT, 4, 'center');
}
function bossDefeated(b) {""", 'v49 helpers')

# ---------------------------------------------------------------- hooks
s = swap(s, """function showBanner(text, sub, life) { banner = { text, sub, t: 0, life }; }""",
         """function showBanner(text, sub, life) { if (bossBannerCard(text, sub)) return; banner = { text, sub, t: 0, life }; }""", 'boss banner card')
s = swap(s, """function step(dt) {
  time += dt; modeT += dt;""", """function step(dt) {
  if (finishFX) { finishFX.t += dt; if (finishFX.t > 1.9) finishFX = null; }
  if (slowT > 0 && mode === 'play') { slowT -= dt; dt *= 0.3; }   // a boss finish plays out in slow motion (Version 49)
  time += dt; modeT += dt;""", 'slow motion')
s = swap(s, """  addScore(b.def.score);
  for (const f of foes) if (f !== b && !f.boss""", """  bossFinish(b);
  addScore(b.def.score);
  for (const f of foes) if (f !== b && !f.boss""", 'boss finish call')
s = swap(s, """    startWave(w);
    if (!S.wave) return;""", """    startWave(w);
    { const card = bossCardFor(w); if (card) S.card = card; }
    if (!S.wave) return;""", 'boss card trigger')
s = swap(s, """  if (cutin) { if (NET.on) player = cutin.own || PL[0];""", """  if (S && S.card) { updateBossCard(dt); return true; }
  if (cutin) { if (NET.on) player = cutin.own || PL[0];""", 'boss card step')
s = swap(s, """  if (!cutin) { drawHUD(); drawDeniseHUD(); if (ST && ST.drive && mode === 'play') drawDriveHud(); }""",
         """  if (!cutin) { drawHUD(); drawDeniseHUD(); if (ST && ST.drive && mode === 'play') drawDriveHud(); }
  if (S && S.card && (mode === 'play' || mode === 'pause')) drawBossCard();""", 'boss card render')
s = swap(s, """  ctx.drawImage(midCv, 0, 0, canvas.width, canvas.height);""", """  // a boss finish punches the camera in on him, then eases back out (Version 49)
  const fz = finishFX && !reduceMotion && settings.shake !== 'less' ? finishFX : null;
  if (fz) {
    const a = fz.t < 0.1 ? fz.t / 0.1 : fz.t < 1 ? 1 : Math.max(0, 1 - (fz.t - 1) / 0.85), z = 1 + 0.26 * a * a * (3 - 2 * a);
    const mw = midCv.width, mh = midCv.height, cw = mw / z, ch = mh / z;
    const cx = clamp((fz.x - cam.x) / W * mw - cw / 2, 0, mw - cw), cy = clamp(fz.y / H * mh - ch / 2, 0, mh - ch);
    ctx.drawImage(midCv, cx, cy, cw, ch, 0, 0, canvas.width, canvas.height);
  } else ctx.drawImage(midCv, 0, 0, canvas.width, canvas.height);""", 'finish zoom')
s = swap(s, """  clearInfo = { title: ST.title, n: ST.n, hidden: ST.hidden, rows, total, base: run.score, mult: m, livesBefore: run.lives };""",
         """  clearInfo = { title: ST.title, n: ST.n, hidden: ST.hidden, rows, total, base: run.score, mult: m, livesBefore: run.lives };
  clearInfo.rank = stageRank(); clearInfo.newBest = noteRank(S.key, clearInfo.rank);""", 'rank on clear')
s = swap(s, """  drawMarcTally();
}
function updateEnd() {""", """  drawRankStamp();
  drawMarcTally();
}
function updateEnd() {""", 'rank stamp draw')
# a new stage clears any leftover finish
s = swap(s, """  time = 0; cam.x = 0; hitstop = 0; flashT = 0; shake = 0; banner = null; cutin = null;""", """  time = 0; cam.x = 0; hitstop = 0; flashT = 0; shake = 0; banner = null; cutin = null; slowT = 0; finishFX = null;""", 'reset finish online')
s = swap(s, """function startStageNow(key) {""", """function startStageNow(key) {
  slowT = 0; finishFX = null;""", 'reset finish on stage start')

# ---------------------------------------------------------------- best ranks on the 3D stage list (also in tools/title3d/)
s = swap(s, "    q('list').innerHTML = ch.keys.map(k => {", "    const RK = typeof stageRanks === 'function' ? stageRanks() : {};   // best rank per stage (Version 49)\n    q('list').innerHTML = ch.keys.map(k => {", 'stage list ranks')
s = swap(s, "${locked ? 'LOCKED' : s.title}</button></li>`;\n    }).join('');", '${locked ? \'LOCKED\' : s.title}${!locked && RK[k] ? `<span class="rk r${RK[k]}" aria-label="Best rank ${RK[k]}">${RK[k]}</span>` : \'\'}</button></li>`;\n    }).join(\'\');', 'stage list rank badge')
s = swap(s, '#t3-list button:disabled{color:var(--t3grey);cursor:default}', '#t3-list button:disabled{color:var(--t3grey);cursor:default}\n#t3-list button{grid-template-columns:calc(var(--t3u) * 14) 1fr auto}\n#t3-list .rk{font:800 max(calc(var(--t3m) * 8px),calc(var(--t3u) * 5)) var(--t3disp);color:var(--t3grey);padding-left:calc(var(--t3u) * 2)}\n#t3-list .rk.rS{color:#ffd23f}#t3-list .rk.rA{color:#7fe07a}#t3-list .rk.rB{color:#6ec3ff}', 'rank badge style')

open(PAGE, 'w', encoding='utf-8').write(s)
print('v49_build: web/index.html updated')
