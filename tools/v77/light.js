// ================================================================== ORPINGTON 2001: LIGHTING (Version 77)
// Two halves.
// 1. The places: each backdrop is dimmed a touch for the time of night, then its glow layer (web/bg/orp/<scene>_glow.png, painted
//    by Meshy as a light map, tools/v77/glow.py) is added back over it and moves: street lamps flicker, the pub breathes, the
//    Atlantis neon buzzes, the dance floor pulses on the beat. Now and then a car's headlights sweep along the High Street.
// 2. The people: every fighter is lit by the place they're stood in. Night blue on the street, warm in the pub, purple in the
//    club; light from the lamps, windows, the pool table lamp, the fruit machines, passing headlights and the club's beams falls
//    on whoever is near it, from its side. Walk under a street lamp and you light up.
const ORP_GLOW = ['busstop', 'cross', 'rambaba', 'front', 'lounge', 'bar', 'pool', 'queue', 'floor'];
setTimeout(() => { ORP_GLOW.forEach(k => bgImg('orp/' + k + '_glow')); ASSET_BG.push(...ORP_GLOW.map(k => 'orp/' + k + '_glow')); }, 0);
const ORP_NIGHT = '#14204c', ORP_LAMP = '#ffc870', ORP_WIN = '#ffdc96';
// per place: the dimming over the backdrop (multiply), the colour the people take on (amb, how much), and the lights.
// Light: x, y (where it falls on the floor, game units), r (reach), col, a (strength); fl: 'lamp' flickers, 'fruit' cycles colours,
// 'neon' buzzes. Positions read off the paintings (tools/v73/scenes.py fits them to the 960x540 screen).
const ORP_LIGHT = {
  busstop: { dim: '#c2c9ea', amb: [ORP_NIGHT, 0.3], glow: 'street', head: true,
    lights: [{ x: 390, y: 440, r: 190, col: ORP_LAMP, a: 0.5, fl: 'lamp' }, { x: 610, y: 420, r: 240, col: ORP_WIN, a: 0.3 }, { x: 160, y: 420, r: 170, col: ORP_WIN, a: 0.18 }] },
  cross: { dim: '#c2c9ea', amb: [ORP_NIGHT, 0.32], glow: 'street', cars: true,
    lights: [{ x: 140, y: 250, r: 170, col: ORP_LAMP, a: 0.45, fl: 'lamp' }, { x: 330, y: 250, r: 170, col: ORP_LAMP, a: 0.45, fl: 'lamp' }, { x: 320, y: 400, r: 140, col: '#ff9a40', a: 0.3 },
      { x: 620, y: 230, r: 230, col: ORP_WIN, a: 0.2 }] },
  rambaba: { dim: '#c2c9ea', amb: [ORP_NIGHT, 0.32], glow: 'street', head: true,
    lights: [{ x: 120, y: 470, r: 190, col: ORP_LAMP, a: 0.5, fl: 'lamp' }, { x: 470, y: 420, r: 270, col: ORP_WIN, a: 0.28 }, { x: 900, y: 440, r: 150, col: ORP_LAMP, a: 0.25, fl: 'lamp' }] },
  front: { dim: '#c2c9ea', amb: [ORP_NIGHT, 0.3], glow: 'street', head: true,
    lights: [{ x: 780, y: 470, r: 210, col: ORP_LAMP, a: 0.55, fl: 'lamp' }, { x: 520, y: 430, r: 300, col: ORP_WIN, a: 0.28 }, { x: 180, y: 430, r: 140, col: ORP_WIN, a: 0.16 }] },
  lounge: { dim: '#efe0c8', amb: ['#3a1c06', 0.14], glow: 'pub',
    lights: [{ x: 410, y: 420, r: 230, col: '#ffbe6a', a: 0.3 }, { x: 800, y: 420, r: 230, col: '#ffbe6a', a: 0.3 }, { x: 260, y: 430, r: 120, col: '#ff50c0', a: 0.28, fl: 'fruit' },
      { x: 790, y: 440, r: 120, col: '#50e0ff', a: 0.22, fl: 'fruit' }] },
  bar: { dim: '#efe0c8', amb: ['#3a1c06', 0.14], glow: 'pub',
    lights: [{ x: 520, y: 450, r: 320, col: '#ffcc80', a: 0.32 }, { x: 100, y: 430, r: 170, col: '#ffbe6a', a: 0.22 }, { x: 860, y: 430, r: 170, col: '#ffbe6a', a: 0.22 }] },
  pool: { dim: '#efe0c8', amb: ['#2a1606', 0.16], glow: 'pub',
    lights: [{ x: 560, y: 450, r: 280, col: '#eaffc8', a: 0.38 }, { x: 690, y: 420, r: 170, col: '#ffbe6a', a: 0.25 }, { x: 770, y: 440, r: 120, col: '#50e0ff', a: 0.25, fl: 'fruit' },
      { x: 80, y: 430, r: 160, col: '#ffbe6a', a: 0.2 }] },
  queue: { dim: '#b8b6e6', amb: ['#120f40', 0.3], glow: 'neon',
    lights: [{ x: 810, y: 430, r: 220, col: '#a060ff', a: 0.45, fl: 'neon' }, { x: 270, y: 440, r: 280, col: '#8ab4ff', a: 0.24 }, { x: 600, y: 440, r: 140, col: '#ffd48a', a: 0.18 }] },
  floor: { dim: '#b4a6dc', amb: ['#1a0636', 0.3], glow: 'beat', beams: true,
    lights: [{ x: 600, y: 420, r: 300, col: '#c080ff', a: 0.3, fl: 'beat' }, { x: 100, y: 430, r: 220, col: '#40e0ff', a: 0.3 }] },
};
const orpLightCfg = () => (ST && ST.era === 2001 && S && S.scBg) ? ORP_LIGHT[S.scBg] : null;

// ---------------------------------------------------------------- 1. the places
function orpGlowAlpha(c) {
  if (S.lights) return 0.15;   // 2am, the house lights are on
  if (c.glow === 'street') return 0.62 + Math.sin(time * 9.3) * 0.03 + Math.sin(time * 2.1) * 0.03;
  if (c.glow === 'pub') return 0.62 + Math.sin(time * 1.3) * 0.07;
  if (c.glow === 'neon') return (Math.floor(time * 10) % 37 === 0 || Math.floor(time * 10) % 53 === 0) ? 0.35 : 0.8;   // the odd buzz
  if (c.glow === 'beat') { const ph = orpBeatPhase(); return ph < 0 ? 0.6 : 0.3 + 0.7 * Math.pow(1 - ph, 3); }
  return 0.7;
}
function orpGlowBg() {
  const c = orpLightCfg(); if (!c) return;
  ctx.save();
  if (!S.lights) { ctx.globalCompositeOperation = 'multiply'; ctx.fillStyle = c.dim; ctx.fillRect(0, 0, W, H); }
  const g = bgImg('orp/' + S.scBg + '_glow');
  if (g) { ctx.globalCompositeOperation = 'lighter'; ctx.globalAlpha = orpGlowAlpha(c); ctx.imageSmoothingEnabled = true; ctx.drawImage(g, 0, 0, W, H); }
  ctx.restore();
  // a car going past at the end of the High Street: its headlights sweep along the pavement and the shop fronts
  if (c.head) {
    const h = S.orpHead;
    if (h) {
      {
        ctx.save(); ctx.globalCompositeOperation = 'lighter';
        const gr = ctx.createRadialGradient(h.x, FB - 10, 4, h.x, FB - 10, 260); gr.addColorStop(0, 'rgba(255,244,214,0.42)'); gr.addColorStop(1, 'rgba(255,244,214,0)');
        ctx.fillStyle = gr; ctx.save(); ctx.translate(h.x, FB - 10); ctx.scale(1, 0.22); ctx.translate(-h.x, -(FB - 10)); ctx.fillRect(h.x - 260, FB - 270, 520, 520); ctx.restore();
        const wall = ctx.createLinearGradient(h.x - 180, 0, h.x + 180, 0); wall.addColorStop(0, 'rgba(255,240,210,0)'); wall.addColorStop(0.5, 'rgba(255,240,210,0.13)'); wall.addColorStop(1, 'rgba(255,240,210,0)');
        ctx.fillStyle = wall; ctx.fillRect(h.x - 180, FT - 200, 360, 200 + (FB - FT));
        ctx.restore();
      }
    }
  }
}

function orpLightTick(dt) {
  const c = orpLightCfg(); if (!c || !c.head) { S.orpHead = null; return; }
  if (!S.orpHead && !S.wipe && chance(dt / 9)) { const d = chance(0.5) ? 1 : -1; S.orpHead = { x: d > 0 ? -260 : W + 260, d }; }
  const h = S.orpHead; if (h) { h.x += h.d * 760 * dt; if (h.x < -300 || h.x > W + 300) S.orpHead = null; }
}

// ---------------------------------------------------------------- 2. the people
// every light touching a point on the floor: [colour, strength, x it comes from]
function orpLightsAt(x, y) {
  const c = orpLightCfg(); if (!c || S.lights) return null;
  const out = [];
  const add = (L, k) => {
    const d = Math.hypot(x - L.x, (y - L.y) * 1.8); if (d >= L.r) return;
    let a = L.a * k * Math.pow(1 - d / L.r, 1.4), col = L.col;
    if (L.fl === 'lamp') a *= 0.92 + Math.sin(time * 13 + L.x) * 0.08;
    else if (L.fl === 'fruit') col = ['#ff50c0', '#50e0ff', '#ffe050'][(Math.floor(time * 3 + L.x) % 3 + 3) % 3];
    else if (L.fl === 'neon') a *= orpGlowAlpha(c) / 0.8;
    else if (L.fl === 'beat') { const ph = orpBeatPhase(); if (ph >= 0) a *= 0.5 + Math.pow(1 - ph, 2); }
    if (a > 0.02) out.push([col, Math.min(0.8, a), L.x]);
  };
  for (const L of c.lights) add(L, 1);
  if (S.orpHead) add({ x: S.orpHead.x, y: FB - 10, r: 260, col: '#fff2d6', a: 0.6 }, 1);
  if (c.cars) for (const n of (S.npcs || [])) if (n.orpCar && Math.abs(n.vxC || 0) > 0) add({ x: n.x + Math.sign(n.vxC) * (n.w || 120) * 0.5, y: n.y, r: 200, col: '#fff2d6', a: 0.55 }, 1);
  if (c.beams) {
    // the club's sweeping beams (orpClubLights draws them): whoever stands in one takes its colour
    const ph = orpBeatPhase(), pulse = ph < 0 ? 0.8 : 0.55 + 0.6 * Math.pow(1 - ph, 2);
    for (let i = 0; i < 5; i++) {
      const ox = 120 + i * 180 + Math.sin(time * (0.6 + i * 0.17) + i) * 120, hw = 90 * (y - 30) / (H - 30), dx = Math.abs(x - ox);
      if (dx < hw) out.push([['#ff3cc8', '#3cc8ff', '#a05aff'][i % 3], 0.42 * (1 - dx / hw) * pulse, ox]);
    }
  }
  return out.sort((a, b) => b[1] - a[1]).slice(0, 3);
}
const ORP_LCV = document.createElement('canvas'), ORP_LCX = ORP_LCV.getContext('2d');
// called from drawLad straight after the sprite is drawn, inside its transform (dir: which way it's drawn)
function orpLightSprite(e, sh, sx, sy, cell, dx, dy, dw, dh, dir) {
  const c = orpLightCfg(); if (!c || S.lights || e.post) return;
  const ls = orpLightsAt(e.x - cam.x, e.y) || [];
  if (ORP_LCV.width < cell || ORP_LCV.height < cell) { ORP_LCV.width = Math.max(ORP_LCV.width, cell); ORP_LCV.height = Math.max(ORP_LCV.height, cell); }
  const x = ORP_LCX, lit = ls.reduce((s, l) => s + l[1], 0);
  const paint = fill => { x.globalCompositeOperation = 'source-over'; x.clearRect(0, 0, cell, cell); x.drawImage(sh.img, sx, sy, cell, cell, 0, 0, cell, cell); x.globalCompositeOperation = 'source-atop'; x.fillStyle = fill; x.fillRect(0, 0, cell, cell); x.globalCompositeOperation = 'source-over'; };
  const smooth = ctx.imageSmoothingEnabled; ctx.imageSmoothingEnabled = false;
  // the colour of the night (less of it where a light's on you)
  const amb = c.amb[1] * Math.max(0.25, 1 - lit * 1.3);
  if (amb > 0.02) { paint(c.amb[0]); ctx.save(); ctx.globalAlpha = amb; ctx.drawImage(ORP_LCV, 0, 0, cell, cell, dx, dy, dw, dh); ctx.restore(); }
  // each light, brightest on the side it comes from
  for (const [col, a, lx] of ls) {
    const side = Math.sign((lx - (e.x - cam.x)) * dir) || 1;
    const gr = x.createLinearGradient(side > 0 ? 0 : cell, 0, side > 0 ? cell : 0, 0);
    gr.addColorStop(0, 'rgba(0,0,0,0)'); gr.addColorStop(0.45, col); gr.addColorStop(1, col);
    paint(gr);
    ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.globalAlpha = a * 0.6; ctx.drawImage(ORP_LCV, 0, 0, cell, cell, dx, dy, dw, dh); ctx.restore();
  }
  ctx.imageSmoothingEnabled = smooth;
}
