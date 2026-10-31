// ================================================================== QUALITY OF LIFE (Version 79)
// 1. The Orpington crowd's big moves get the "!" warning the 2006 crowd have (drawn by orpCrowdFore in Orpington).
// 2. How-to cards stop the game the first time only; after that, a one-line reminder at the top while you play
//    (Settings: HOW-TO CARDS, FIRST TIME ONLY / EVERY TIME).
// 3. An arrow at the edge of the screen for anyone walking in off it (every stage).
// 4. On a phone, a punch with nobody in front of you and someone right behind turns you round to hit them, unless you're
//    pushing the stick the way you're facing (Settings: AUTO-TURN, ON / OFF).
// 5. Settings: LIGHTING, FULL / LOW. Low keeps Orpington's glowing backdrops but doesn't light the fighters.
// 6. An Orpington stage carries on from the place you'd reached (the bar, the pool room, the dance floor) when you carry
//    a run on after the app closed; RESTART STAGE still starts it from the top.

// ---- 1
['whipWind', 'rideWind', 'kickWind', 'spinKickWind', 'kneeSlideWind', 'barsWind', 'bargeWind', 'hookWind', 'breakWind', 'shakeWind', 'whistleWind'].forEach(s => NL_TELL.add(s));
function qolTells() {
  for (const f of foes) if (NL_TELL.has(f.state) && !f.boss) {
    const sx = f.x - cam.x, m = SPRITE_META[f.kind], top = m ? m.h * SPR_K * (f.scale || 1) + 40 : 150;   // clear of the head, whatever the sprite's height
    if (sx > -40 && sx < W + 40) textOut('!', sx, f.y - f.z - top + Math.sin(time * 14) * 3, '34px ' + DISPLAY, '#ffd23f', OUT, 6);
  }
}

// ---- 2
const ORP_HOW_SHORT = {
  'HOLD THE BUS STOP': 'Hold the bus stop till the lads turn up',
  'THE CROSSING': 'Cross three times · jump the mopeds',
  'GET THE ROUND IN': 'Hide when Sue looks · walk the pints back',
  'THE QUEUE': 'Sort out the queue-jumpers',
  'THE DANCE FLOOR': 'Watch for the ! · hit on the beat',
};
function qolHowSeen(title) { return settings.howto !== 'always' && !!(lsGet('carpdiem.howto', {}) || {})[title]; }
function qolHowRead(title) { const m = lsGet('carpdiem.howto', {}) || {}; m[title] = 1; lsSet('carpdiem.howto', m); }

// ---- 3
function qolEdgeArrows() {
  if (!S || mode !== 'play') return;
  for (const f of foes) {
    if (f.car || f.remove || f.state === 'dead' || f.state === 'beaten' || f.npc) continue;
    const sx = f.x - cam.x; if (sx > -6 && sx < W + 6) continue;
    const off = sx < 0 ? -sx : sx - W; if (off > 420) continue;
    const L = sx < 0, x = L ? 16 : W - 16, y = clamp(f.y - f.z - 60, 90, H - 70), a = clamp(1 - off / 420, 0.35, 1) * (0.7 + 0.3 * Math.sin(time * 9));
    ctx.save(); ctx.globalAlpha = a; ctx.fillStyle = f.boss ? '#ff5a3a' : '#ffd23f'; ctx.strokeStyle = OUT; ctx.lineWidth = 3;
    ctx.beginPath(); ctx.moveTo(x + (L ? -10 : 10), y); ctx.lineTo(x + (L ? 10 : -10), y - 14); ctx.lineTo(x + (L ? 10 : -10), y + 14); ctx.closePath(); ctx.stroke(); ctx.fill();
    ctx.restore();
  }
}

// ---- 4
function qolAutoFace(p) {
  if (!touchUI || settings.aim === false || !p || p.grab || p.z > 0) return;
  const inp = readInput(); if (inp.ix === p.face) return;   // pushing the way you face: you meant it
  let front = false, back = null, bd = 1e9;
  for (const f of foes) {
    if (!canBeHit(f) || f.car || Math.abs(f.y - p.y) > 30) continue;
    const ahead = (f.x - p.x) * p.face;
    if (ahead > -10 && ahead < 130) { front = true; break; }
    if (ahead <= -10 && ahead > -130 && -ahead < bd) { bd = -ahead; back = f; }
  }
  if (!front && back) p.face = -p.face;
}

// ---- 5 is a check in orpLightSprite (settings.light === 'low')

// ---- 6
function qolOrpSaveScene(i) {
  if (NET.on || !run || run.mini || !S) return;
  const r = lsGet(RUN_SAVE, null);
  if (r && r.key === S.key) { r.orpAt = { key: S.key, i }; lsSet(RUN_SAVE, r); }
}
function qolOrpStartScene() {
  const at = run && run.orpAt; let i = 0;
  if (at && at.key === S.key && orpScenes()[at.i]) i = at.i;
  if (run) delete run.orpAt;
  if (stageSnap && stageSnap.run) delete stageSnap.run.orpAt;   // RESTART STAGE starts from the top
  orpGoScene(i);
  if (i > 0) orpAnnounce('CARRYING ON · ' + (orpScenes()[i].label || ''), 3);
}
