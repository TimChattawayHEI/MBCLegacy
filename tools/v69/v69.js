// Version 69: things painted standing on the floor block the way, and real fire on the burning wrecks.
//
// FLOOR_BLOCK: for each stage, [x0, x1, y1] in game units: between x0 and x1 the floor from the back (FT) down to y1 is
// taken up by something painted there (a wall end, a door standing open, a pillar, a bench, a bin), so nobody can walk
// into it. Coming at it from the side stops you at its edge; coming up from the front stops you at its front.
const FLOOR_BLOCK = {
  divebar: [[0, 1870, 364], [1860, 2005, 396], [2096, 2136, 384]],              // the bar stools, the end wall by the back door, the pergola post
  soundz: [[280, 1200, 390], [1190, 1320, 376], [1380, 1475, 404], [2790, 2890, 404], [3320, 3400, 384]],   // the decks and sofa, the armchair, the flat's door, the air con box and the mast
  airport: [[90, 560, 384], [1100, 1320, 370]],                                 // the plane's wheels and steps, the baggage tug and carts
  nl_station: [[1790, 2400, 388], [2430, 2500, 392], [2584, 2645, 392], [2690, 2995, 384]],   // ticket machines, seats and vending machine, the open doors, the canopy posts, bin and bench
  frequency: [[6, 34, 380], [310, 338, 380], [728, 756, 380], [1132, 1160, 380], [1236, 1316, 372], [1306, 1338, 380], [1456, 1488, 380], [1690, 1745, 386], [1984, 2076, 410]],   // lamp posts, the phone box, the underpass ramp and pillar
  nl_cx: [[0, 1940, 394], [740, 890, 422], [1460, 1620, 420], [1860, 1910, 420], [2100, 2290, 420], [2660, 2770, 414], [3020, 3120, 404], [3110, 3410, 414]],   // the tracks along the platform edge, the columns with their bins and signs, the arches' railings and pillar
  beach: [[2800, 2940, 384]],                                                   // the sandcastle
};
function floorBlock(e, px, py) {
  const B = S && FLOOR_BLOCK[S.key]; if (!B) return;
  for (const b of B) {
    const x0 = b[0], x1 = b[1], y1 = b[2];
    if (e.x <= x0 || e.x >= x1 || e.y >= y1) continue;
    if (px <= x0) e.x = x0; else if (px >= x1) e.x = x1; else e.y = y1;
    // a foe stopped at the side slides forward round it rather than walking on the spot
    if (e.kind !== 'player' && e.y < y1 && (e.x === x0 || e.x === x1)) e.y = Math.min(y1, e.y + 3);
  }
}

// Fire: each burning thing has its own small fire field, a pixel per pixel of the art (drawn at 2 units a pixel). Heat
// is fed in along the bottom row (hottest in the middle, flaring and dropping at random), and every frame each pixel's
// heat moves up a row, drifting a pixel left or right and cooling a little at random, so tongues of flame lick up and
// break off. Heat picks a colour from a 37 step palette, dark red at the edges to yellow-white at the seat.
const FIRE_RGB = [[0, 0, 0], [31, 7, 7], [47, 15, 7], [71, 15, 7], [87, 23, 7], [103, 31, 7], [119, 31, 7], [143, 39, 7], [159, 47, 7], [175, 63, 7], [191, 71, 7], [199, 71, 7], [223, 79, 7], [223, 87, 7], [223, 87, 7], [215, 95, 7], [215, 95, 7], [215, 103, 15], [207, 111, 15], [207, 119, 15], [207, 127, 15], [207, 135, 23], [199, 135, 23], [199, 143, 23], [199, 151, 31], [191, 159, 31], [191, 159, 31], [191, 167, 39], [191, 167, 39], [191, 175, 47], [183, 175, 47], [183, 183, 47], [183, 183, 55], [207, 207, 111], [223, 223, 159], [239, 239, 199], [255, 255, 255]];
const FIRE_PAL = new Uint32Array(37);
for (let i = 0; i < 37; i++) { const c = FIRE_RGB[i], a = i === 0 ? 0 : i < 7 ? 40 + i * 30 : 255; FIRE_PAL[i] = ((a << 24) | (c[2] << 16) | (c[1] << 8) | c[0]) >>> 0; }
const FIRES = {}; let FIRE_N = 0;
function fireTick(f) {
  const w = f.w, h = f.h, p = f.p, base = (h - 1) * w; f.n++;
  for (let x = 0; x < w; x++) {
    const edge = Math.min(1, Math.min(x + 1, w - x) / (w * 0.22));
    const flick = 0.55 + 0.45 * Math.abs(Math.sin(x * 0.37 + f.n * 0.21 + Math.sin(x * 1.3 + f.n * 0.05) * 2));
    p[base + x] = Math.random() < 0.06 ? 0 : Math.min(36, Math.round(36 * f.k * edge * flick + Math.random() * 3));
  }
  for (let y = 1; y < h; y++) {
    const row = y * w;
    for (let x = 0; x < w; x++) {
      const v = p[row + x];
      if (!v) { p[row - w + x] = 0; continue; }
      const nx = Math.min(w - 1, Math.max(0, x + ((Math.random() * 3) | 0) - 1));
      const cool = (Math.random() < f.cool ? 1 : 0) + (Math.random() < 0.35 ? 1 : 0);
      p[row - w + nx] = v > cool ? v - cool : 0;
    }
  }
}
// realFire(id, x, y, w, h, k): a fire w x h art pixels whose seat (bottom row) is centred under x + w (units) at height y;
// k is how fierce (1 is full)
function realFire(id, x, y, w, h, k) {
  let f = FIRES[id];
  if (!f) {
    const cv = document.createElement('canvas'); cv.width = w; cv.height = h; const c2 = cv.getContext('2d'), img = c2.createImageData(w, h);
    f = FIRES[id] = { w, h, k: k || 1, cool: 0.2 + 12 / h, p: new Uint8Array(w * h), cv, c2, img, u32: new Uint32Array(img.data.buffer), t: time, n: 0 };
    for (let i = 0; i < h; i++) fireTick(f);
  }
  let steps = Math.floor((time - f.t) * 30);
  if (steps < 0 || steps > 30) { f.t = time; steps = 1; }
  if (steps > 0) {
    for (let i = 0; i < Math.min(steps, 3); i++) fireTick(f);
    f.t += steps / 30;
    for (let i = 0; i < f.p.length; i++) f.u32[i] = FIRE_PAL[f.p[i]];
    f.c2.putImageData(f.img, 0, 0);
  }
  const X = Math.round(x / 2) * 2, Y = Math.round(y / 2) * 2, fl = 0.8 + 0.2 * Math.sin(time * 13 + w) * Math.sin(time * 7.3 + h);
  ctx.save();
  // the glow it throws on everything round it
  ctx.globalCompositeOperation = 'lighter';
  const g = ctx.createRadialGradient(X + w, Y - h * 0.4, 4, X + w, Y - h * 0.4, w * 2.4);
  g.addColorStop(0, 'rgba(255,140,40,' + (0.26 * fl * f.k).toFixed(3) + ')'); g.addColorStop(1, 'rgba(255,90,20,0)');
  ctx.fillStyle = g; ctx.fillRect(X - w * 1.4, Y - h * 2 - w, w * 4.8, h * 2 + w * 2.2);
  ctx.globalCompositeOperation = 'source-over';
  ctx.imageSmoothingEnabled = false;
  ctx.drawImage(f.cv, X, Y - h * 2, w * 2, h * 2);
  // sparks going up off it
  for (let i = 0; i < 5; i++) {
    const ph = (time * (0.5 + i * 0.07) + i / 5 + w * 0.013) % 1, sx = X + w + Math.sin(i * 7.1 + time * 1.7) * w * 0.7 + ph * 20 * Math.sin(i);
    ctx.fillStyle = ph < 0.5 ? '#ffe08a' : '#ff8a30'; ctx.globalAlpha = 1 - ph;
    ctx.fillRect(Math.round(sx / 2) * 2, Math.round((Y - h * 1.2 - ph * 150) / 2) * 2, 2, 2);
  }
  ctx.restore();
}
// Ramsden's painted wrecks: [centre offset, fire width, seat height above FT (units, negative is up), fierceness]
const RAMS_FIRE = { 560: [-6, 50, -86, 0.8], 1610: [20, 48, -84, 0.75], 2324: [0, 60, -82, 1], 2714: [-6, 44, -84, 0.7], 3440: [10, 66, -92, 0.9] };
