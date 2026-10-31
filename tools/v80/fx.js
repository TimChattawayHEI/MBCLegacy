// ================================================================== Version 80: Streets of Rage 4 style hits (Tim first)
// Swoosh trails follow the fist or foot on every combo hit, in the lad's own colour, glowing ('lighter' blending), and
// his hits throw a spark that sprays the way the punch travels (PixelLab VFX workbench, light and heavy).
// To roll it out to another lad: add his id to FX_LADS. Sparks for him need fx/<id>_spark(.big).png and an FX entry,
// otherwise he keeps the old star spark and still gets the swooshes.
const FX_LADS = { tim: true };
FX.tim_spark = { fw: 64, fh: 55, n: 7, cols: 3, ax: 19, ay: 21, fps: 16, loop: false };
FX.tim_spark_big = { fw: 89, fh: 75, n: 8, cols: 3, ax: 25, ay: 27, fps: 16, loop: false };
fxImg('tim_spark'); fxImg('tim_spark_big');

function fxLad(a) { return !!(a && a.def && !a.ally && FX_LADS[a.def.id] && (a === player || (typeof PL !== 'undefined' && PL.includes(a)))); }

// Each swoosh is a curve in world units, from the lad's feet, facing right: start, bend, end (x forward, z up).
// Worked out from Tim's frames: the fist lands about 50 forward and 79 up, the kick about 66 forward and 75 up.
const SWOOSH = {
  jab:   { p: [[4, 82], [36, 81], [68, 80]], w: 16 },
  hook:  { p: [[-6, 70], [34, 104], [64, 80]], w: 20 },
  kick:  { p: [[2, 10], [70, 6], [60, 72]], w: 26 },
  knee:  { p: [[8, 18], [56, 28], [52, 74]], w: 22 },
  swing: { p: [[-20, 100], [44, 132], [72, 60]], w: 24 },
};
const SW_SWEEP = 6, SW_FADE = 4;   // cached frames: the edge racing round, then the tail catching up and thinning
const swCache = {};

function hexRgb(h) { const n = parseInt(h.slice(1), 16); return [(n >> 16) & 255, (n >> 8) & 255, n & 255]; }
function swPt(P, u) { const a = 1 - u; return [a * a * P[0][0] + 2 * a * u * P[1][0] + u * u * P[2][0], a * a * P[0][1] + 2 * a * u * P[1][1] + u * u * P[2][1]]; }

// one frame of a swoosh, drawn at art-pixel size (half a world unit) and snapped to three colours
function swFrame(shape, col, big, f) {
  const S = SWOOSH[shape], P = S.p, pad = 10;
  const xs = P.map(q => q[0]), zs = P.map(q => q[1]);
  const x0 = Math.min(...xs) - S.w - pad, x1 = Math.max(...xs) + S.w + pad, z0 = Math.min(...zs) - S.w - pad, z1 = Math.max(...zs) + S.w + pad;
  const k = 1, wb = big ? 1.25 : 1, cw = Math.ceil((x1 - x0) * k / 2), ch = Math.ceil((z1 - z0) * k / 2);
  const cv = document.createElement('canvas'); cv.width = cw; cv.height = ch;
  const c = cv.getContext('2d');
  const toPx = q => [(q[0] - x0) * k / 2, (z1 - q[1]) * k / 2];
  // where the edge and the tail are along the curve
  let head, tail, wk = 1;
  if (f < SW_SWEEP) { const q = (f + 1) / SW_SWEEP, e = 1 - Math.pow(1 - q, 2); head = 0.2 + 0.8 * e; tail = Math.max(0, head - 0.8); }
  else { const r = (f - SW_SWEEP + 1) / SW_FADE; head = 1; tail = 0.2 + 0.72 * r; wk = 1 - 0.55 * r; }
  // the hollow side of the curve: the crescent grows inward from its outer rim
  const mid = [(P[0][0] + P[2][0]) / 2, (P[0][1] + P[2][1]) / 2], bend = [mid[0] - P[1][0], mid[1] - P[1][1]];
  const N = 28, outer = [], norms = [], width = [];
  for (let i = 0; i <= N; i++) {
    const u = tail + (head - tail) * i / N, a = swPt(P, u), b = swPt(P, Math.min(1, u + 0.01)), c0 = swPt(P, Math.max(0, u - 0.01));
    let tx = b[0] - c0[0], tz = b[1] - c0[1]; const l = Math.hypot(tx, tz) || 1; tx /= l; tz /= l;
    let nx = -tz, nz = tx; if (nx * bend[0] + nz * bend[1] < 0) { nx = -nx; nz = -nz; }
    if (Math.abs(bend[0]) + Math.abs(bend[1]) < 1) { nx = 0; nz = -1; }   // a straight jab: thicken downwards
    const s = i / N, grow = Math.pow(s, 0.8), tip = s > 0.9 ? (1 - s) / 0.1 : 1;
    outer.push(a); norms.push([nx, nz]); width.push(S.w * wb * wk * grow * (0.35 + 0.65 * tip));
  }
  const band = (frac, fill) => {
    c.beginPath();
    outer.forEach((q, i) => { const p = toPx(q); i ? c.lineTo(p[0], p[1]) : c.moveTo(p[0], p[1]); });
    for (let i = outer.length - 1; i >= 0; i--) { const q = outer[i], n = norms[i], w = width[i] * frac; const p = toPx([q[0] + n[0] * w, q[1] + n[1] * w]); c.lineTo(p[0], p[1]); }
    c.closePath(); c.fillStyle = fill; c.fill();
  };
  const rgb = hexRgb(col), tint = rgb.map(v => Math.round(v + (255 - v) * 0.55));
  band(1, col); band(0.55, `rgb(${tint})`); band(0.22, '#ffffff');
  // snap to three colours and hard alpha, so it sits with the pixel art
  const im = c.getImageData(0, 0, cw, ch), d = im.data, pal = [rgb, tint, [255, 255, 255]];
  for (let i = 0; i < d.length; i += 4) {
    if (d[i + 3] < 90) { d[i + 3] = 0; continue; }
    let best = 0, bd = 1e9;
    for (let j = 0; j < 3; j++) { const e = (d[i] - pal[j][0]) ** 2 + (d[i + 1] - pal[j][1]) ** 2 + (d[i + 2] - pal[j][2]) ** 2; if (e < bd) { bd = e; best = j; } }
    d[i] = pal[best][0]; d[i + 1] = pal[best][1]; d[i + 2] = pal[best][2]; d[i + 3] = 255;
  }
  c.putImageData(im, 0, 0);
  return { cv, ox: x0 * k, oz: z1 * k };   // world offset of the canvas's top left, from the feet
}
function swFrames(shape, col, big) {
  const key = shape + col + (big ? 'B' : '');
  if (!swCache[key]) { swCache[key] = []; for (let f = 0; f < SW_SWEEP + SW_FADE; f++) swCache[key].push(swFrame(shape, col, big, f)); }
  return swCache[key];
}

// called from startPunch: queue the trail for this hit
function v80Swoosh(p) {
  if (!fxLad(p) || !p.atk || !SWOOSH[p.comboAnim]) return;
  const a = p.atk, start = a.t0 * 0.35, sweep = Math.max(0.05, a.t1 - start), fade = p.comboFin ? 0.13 : 0.09;
  parts.push({ k: 'swoosh', who: p, atk: a, shape: p.comboAnim, big: !!p.comboFin, col: p.def.color || '#ffffff', face: p.face,
    start, sweep, fade, x: p.x, y: p.y, z: 0, t: 0, life: start + sweep + fade });
}
function v80DrawSwoosh(s) {
  const w = s.who;
  if (w && w.atk === s.atk && w.state === 'punch') { s.x = w.x; s.y = w.y; s.z = w.z || 0; }
  else if (s.t < s.start + s.sweep) s.t = s.start + s.sweep;   // the punch was cut short: let the trail fade out now
  if (s.t < s.start) return;
  let f, alpha = 1;
  if (s.t < s.start + s.sweep) f = Math.min(SW_SWEEP - 1, Math.floor((s.t - s.start) / s.sweep * SW_SWEEP));
  else { const r = Math.min(0.999, (s.t - s.start - s.sweep) / s.fade); f = SW_SWEEP + Math.floor(r * SW_FADE); alpha = 1 - r * 0.6; }
  const fr = swFrames(s.shape, s.col, s.big)[f];
  const sx = Math.round((s.x - cam.x) / 2) * 2, sy = Math.round((s.y - s.z) / 2) * 2;
  ctx.save();
  ctx.imageSmoothingEnabled = false; ctx.globalCompositeOperation = 'lighter'; ctx.globalAlpha = alpha * 0.92;
  ctx.translate(sx, sy); ctx.scale(s.face < 0 ? -1 : 1, 1);
  ctx.drawImage(fr.cv, fr.ox, -fr.oz, fr.cv.width * 2, fr.cv.height * 2);
  ctx.restore();
}

// called from applyHit: the lad's own directional spark; false leaves the old one to play
function v80Spark(a, x, y, z, big, dir) {
  if (!fxLad(a)) return false;
  const k = a.def.id + (big ? '_spark_big' : '_spark');
  if (!FX[k]) return false;
  fxPlay(k, x, y, z, dir < 0 ? -1 : 1);
  return true;
}
