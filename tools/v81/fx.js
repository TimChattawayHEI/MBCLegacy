// ================================================================== Version 81: every lad's own hits, and a signature effect on each mini special
// Builds on Version 80 (Tim's trails and sparks). Each lad gets his own colour on trails and sparks, trail shapes fitted
// to his own fists and feet, and a PixelLab effect on his hold-HIT mini special that only he has.

// One colour per lad, chosen so no two look alike in a crowd. Keep in step with FX_COL in tools/v81/sparks.py
const FX_COL = { tim: '#6aa8e8', seb: '#b0d050', byron: '#4fd8d0', pearcy: '#ffcf3a', kelly: '#b98ce6',
  marc: '#ff6a6a', sam: '#ff7ab8', thet: '#dfe8f8', ash: '#f07a2a' };
for (const id in FX_COL) {
  FX_LADS[id] = true;
  if (id === 'tim') continue;   // Tim's sheets are the Version 80 originals
  FX[id + '_spark'] = Object.assign({}, FX.tim_spark); FX[id + '_spark_big'] = Object.assign({}, FX.tim_spark_big);
  fxImg(id + '_spark'); fxImg(id + '_spark_big');
}

// Trails fitted to each lad: where his fist or foot lands (forward, up, in world units from his feet), how big he is,
// and which shape a move uses (Ash's jab and hook rows are a low kick and a roundhouse). Unlisted moves keep Tim's.
SWOOSH.round = { p: [[-6, 24], [34, 118], [74, 88]], w: 24 };
const SW_FIT = {
  seb: { s: 1.1, hook: [52, 92], kick: [46, 104] },
  byron: { jab: [56, 88], hook: [46, 86], kick: [46, 86] },
  pearcy: { s: 1.1, hook: [68, 86], kick: [52, 95] },
  kelly: { jab: [56, 94], hook: [42, 86], knee: [20, 56] },
  marc: { jab: [58, 86], hook: [55, 86], kick: [42, 86] },
  sam: { jab: [42, 88], hook: [40, 86], swing: [56, 90] },
  thet: { s: 0.5, jab: [18, 46], hook: [18, 46], kick: [22, 32] },
  ash: { use: { jab: 'kick', hook: 'round' }, jab: [70, 85], hook: [74, 88], kick: [64, 80] },
};
function swKey(p) {
  const id = p.def.id, fit = SW_FIT[id], anim = p.comboAnim;
  if (!fit) return anim;
  const key = id + '_' + anim;
  if (!SWOOSH[key]) {
    const base = SWOOSH[(fit.use && fit.use[anim]) || anim]; if (!base) return anim;
    const s = fit.s || 1, end = fit[anim] || base.p[2], last = base.p[2];
    SWOOSH[key] = { p: base.p.map(q => [end[0] + s * (q[0] - last[0]), Math.max(2, end[1] + s * (q[1] - last[1]))]), w: base.w * s };
  }
  return key;
}
v80Swoosh = function (p) {
  if (!fxLad(p) || !p.atk || !SWOOSH[(SW_FIT[p.def.id] && SW_FIT[p.def.id].use && SW_FIT[p.def.id].use[p.comboAnim]) || p.comboAnim]) return;
  const a = p.atk, start = a.t0 * 0.35, sweep = Math.max(0.05, a.t1 - start), fade = p.comboFin ? 0.13 : 0.09;
  parts.push({ k: 'swoosh', who: p, atk: a, shape: swKey(p), big: !!p.comboFin, col: FX_COL[p.def.id] || p.def.color || '#ffffff', face: p.face,
    start, sweep, fade, x: p.x, y: p.y, z: 0, t: 0, life: start + sweep + fade });
};

// ------------------------------------------------------------------ mini specials: one effect each (PixelLab VFX workbench)
// Sheets in tools/v81/src/mini_<lad>.png, copied to web/fx/. ax/ay is the point on the sheet that sits on `at`:
// feet = the lad's feet (where he stood when it started), or [forward, up] world units from his feet.
// when: 'start' plays it when the mini special starts (after `delay` seconds), 'last' on its final hit.
const MINI_FX = {
  tim:    { fw: 146, fh: 93,  n: 12, ax: 73, ay: 32, fps: 20, when: 'start', delay: 0.08, at: [0, 80] },   // a whirl round him at elbow height
  seb:    { fw: 116, fh: 117, n: 10, ax: 58, ay: 59, fps: 16, when: 'last',  at: [44, 112] },             // BONK: burst and cartoon stars at the head
  byron:  { fw: 157, fh: 74,  n: 12, ax: 27, ay: 52, fps: 16, when: 'start', delay: 0.04, at: [0, 0] },    // turf and dust kicked up along the slide
  pearcy: { fw: 152, fh: 99,  n: 11, ax: 76, ay: 52, fps: 16, when: 'last',  at: [26, 100] },             // White Out: a powder cloud with gold glitter
  kelly:  { fw: 193, fh: 62,  n: 12, ax: 95, ay: 38, fps: 18, when: 'start', delay: 0.1, at: [0, 0] },     // tyre tracks and sparks off the wheels
  marc:   { fw: 112, fh: 99,  n: 12, ax: 56, ay: 86, fps: 18, when: 'start', delay: 0.04, at: [0, 0] },    // a red tornado
  sam:    { fw: 141, fh: 100, n: 12, ax: 7,  ay: 50, fps: 16, when: 'start', delay: 0.18, at: [28, 104] },  // a big heart blown forward that bursts into little ones
  thet:   { fw: 148, fh: 56,  n: 12, ax: 36, ay: 39, fps: 18, when: 'start', delay: 0.04, at: [0, 0] },    // snapping teeth at ankle height
  ash:    { fw: 152, fh: 103, n: 12, ax: 65, ay: 90, fps: 18, when: 'start', delay: 0.05, at: [0, 0] },    // fiery spinning kicks, a flame ring and embers
};
for (const id in MINI_FX) { const m = MINI_FX[id]; FX['mini_' + id] = { fw: m.fw, fh: m.fh, n: m.n, cols: 4, ax: m.ax, ay: m.ay, fps: m.fps, loop: false }; fxImg('mini_' + id); }

function miniFxPlay(p, m) {
  const k = 'mini_' + p.def.id, f = FX[k], face = p.miniFace || p.face || 1;
  parts.push({ k: 'v81fx', fx: k, x: p.x + face * m.at[0], y: p.y, z: (p.z || 0) + m.at[1], flip: face, t: -(m.delay || 0), life: f.n / f.fps });
}
// called from startMini
function v81MiniStart(p) {
  const m = p.def && MINI_FX[p.def.id];
  if (!m || !fxLad(p)) return;
  if (m.when === 'start') miniFxPlay(p, m);
}
// called from miniBurst on every hit; the last one gets the flash in his colour
function v81MiniBurst(p, mini, last) {
  const m = p.def && MINI_FX[p.def.id];
  if (!m || !fxLad(p) || !last) return;
  if (m.when === 'last') miniFxPlay(p, m);
  parts.push({ k: 'v81flash', col: FX_COL[p.def.id] || '#ffffff', x: 0, y: 0, z: 0, t: 0, life: 0.2 });
}
function v81DrawPart(p) {
  if (p.k === 'v81fx') {
    if (p.t < 0) return;
    const m = FX[p.fx]; drawFxFrame(p.fx, Math.min(m.n - 1, Math.floor(p.t * m.fps)), p.x - cam.x, p.y - p.z, p.flip);
    return;
  }
  if (p.k === 'v81flash') {   // a quick wash of the lad's colour over the screen, SoR4 style
    if (reduceMotion || settings.shake === 'less') return;
    ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.globalAlpha = 0.28 * (1 - p.t / p.life); ctx.fillStyle = p.col;
    ctx.fillRect(-20, -20, W + 40, H + 40); ctx.restore();
  }
}
