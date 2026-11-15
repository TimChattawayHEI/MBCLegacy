// Livelier backgrounds (Version 85): small things that move on top of the Meshy paintings, drawn behind the fighters.
// The paintings are untouched. Each stage lists what it has in ALIVE (world x, screen y, as the painting puts it):
//   neon   [x0, x1, y0, y1, colour, stutters]  a sign's glow breathing; a sign that stutters drops out for a blink now and then
//   bulbs  [x, y, colour]                      fairy lights twinkling (found in the painting by tools/v85/bulbs.py)
//   lamps  [x, y]                              a lamp's glow breathing, with moths round it
//   tubes  [x0, x1, y]                         a strip light that flickers
//   drips  [x, y, rx]                          rings spreading on a puddle
//   lamps  [x, y, moths]                       moths defaults to 3 (0 indoors)
//   spin   [x, y, rx, ry, turns a second]      a fan or a record: a highlight going round
//   prop   [x, y, r]                           an aircraft propeller turning, seen side on
//   blink  [x, y, colour, period]              a beacon or a standby light
//   city   [x0, x1, y0, y1, n, colour]         far windows going on and off
//   glint  [x0, x1, y0, y1, n]                 sun on water
//   foam   [x0, x1, y]                         the edge of the sea running up and back
//   board  [x0, x1, y0, y1, rows]              a departures board, a row flipping now and then
//   tv     [x0, x1, y0, y1]                    a telly's light jumping
//   belt   [x0, x1, y, speed]                  a baggage belt's slats going round
//   steam  [x, y, colour]                      puffs rising (smoker, coffee machine, a vent)
//   mist   [y0, y1, alpha]                     mist drifting over water
//   flies  [x0, x1, y0, y1, n]                 fireflies
//   patch  [x0, x1, y0, y1, top, bottom]       paint out something an animation replaces
//   anims  { k, x, y, fps, sc, flip, every, dur }  a looping PixelLab animation in place (web/bg/alive/<k>.png, a strip);
//                                              with every/dur it only shows for dur seconds every so often (a carp jumping)
//   wander { k, x, y, rx, ry, sc, fps }       one that hovers about a spot (a dragonfly)
//   walks  { k, x0, x1, y, fps, sc, every, dur, back }  one that crosses now and then (back: it comes back the other way next time)
const ALIVE = {};
const ALIVE_SHEETS = {};   // k: frames in the strip, filled in by aliveSheet
function aliveSheet(k, n) { ALIVE_SHEETS[k] = n; ASSET_BG.push('alive/' + k); bgImg('alive/' + k); }
const aliveRnd = i => { const s = Math.sin(i * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); };
function aliveFrame(k, f, x, bottom, sc, flip, alpha, dim) {
  const img = bgImg('alive/' + k), n = ALIVE_SHEETS[k]; if (!img || !n) return;
  const fw = img.width / n, w = fw * sc, h = img.height * sc, sx = Math.round((x - cam.x - w / 2) / 2) * 2;
  if (sx > W + 8 || sx + w < -8) return;
  ctx.save(); ctx.imageSmoothingEnabled = false; if (alpha != null) ctx.globalAlpha = alpha; if (dim) ctx.filter = 'brightness(' + dim + ')';
  if (flip) { ctx.translate(sx + w, 0); ctx.scale(-1, 1); ctx.drawImage(img, (f % n) * fw, 0, fw, img.height, 0, Math.round(bottom - h), w, h); }
  else ctx.drawImage(img, (f % n) * fw, 0, fw, img.height, sx, Math.round(bottom - h), w, h);
  ctx.restore();
}
function aliveDraw(k) {
  const A = ALIVE[k]; if (!A) return;
  const vis = (x0, x1) => x1 - cam.x > -60 && x0 - cam.x < W + 60;
  ctx.save();
  // patches: paint out a painted thing that an animation replaces (a sky gradient, top colour to bottom)
  for (const [x0, x1, y0, y1, c0, c1] of A.patch || []) { if (!vis(x0, x1)) continue;
    const g = ctx.createLinearGradient(0, y0, 0, y1); g.addColorStop(0, c0); g.addColorStop(1, c1); ctx.fillStyle = g; ctx.fillRect(Math.round((x0 - cam.x) / 2) * 2, y0, x1 - x0, y1 - y0); }
  // signs: the glow breathes; one that stutters blinks out, its pool on the pavement with it
  for (let i = 0; i < (A.neon || []).length; i++) {
    const [x0, x1, y0, y1, col, stut] = A.neon[i]; if (!vis(x0, x1)) continue;
    const X0 = x0 - cam.x, X1 = x1 - cam.x;
    const t = (time + i * 1.7) % 9, off = stut && (t < 0.12 || (t > 0.24 && t < 0.3) || (t > 0.42 && t < 0.9));
    if (off) {
      ctx.globalCompositeOperation = 'source-over'; ctx.fillStyle = 'rgba(10,8,18,0.62)'; ctx.fillRect(X0 + 3, y0 + 3, X1 - X0 - 6, y1 - y0 - 6);
      ctx.fillStyle = 'rgba(10,8,18,0.28)'; ctx.fillRect(X0 - 10, y1 + 70, X1 - X0 + 20, 70);
    } else {
      ctx.globalCompositeOperation = 'lighter'; ctx.fillStyle = col;
      const a = 0.05 + 0.03 * Math.sin(time * 3.1 + i * 2) + 0.015 * Math.sin(time * 17 + i);
      for (const [g, k] of [[16, 0.35], [9, 0.6], [3, 1]]) { ctx.globalAlpha = a * k; ctx.fillRect(X0 - g, y0 - g, X1 - X0 + g * 2, y1 - y0 + g * 2); }
      ctx.globalAlpha = 1;
    }
  }
  // fairy lights: each bulb fades up and down on its own beat
  ctx.globalCompositeOperation = 'lighter';
  for (let i = 0; i < (A.bulbs || []).length; i++) {
    const [x, y, col] = A.bulbs[i], sx = x - cam.x; if (sx < -10 || sx > W + 10) continue;
    const a = Math.sin(time * (1.3 + aliveRnd(i) * 1.6) + aliveRnd(i + 50) * 6.3); if (a < 0.2) continue;
    ctx.globalAlpha = a * 0.9; ctx.fillStyle = col; ctx.fillRect(Math.round(sx / 2) * 2 - 1, Math.round(y / 2) * 2 - 1, 3, 3);
    ctx.globalAlpha = a * 0.25; ctx.fillRect(Math.round(sx / 2) * 2 - 3, Math.round(y / 2) * 2 - 3, 7, 7);
  }
  // lamps: the glow breathes and moths circle the head
  for (let i = 0; i < (A.lamps || []).length; i++) {
    const [x, y, nm] = A.lamps[i], sx = x - cam.x; if (sx < -80 || sx > W + 80) continue;
    const g = ctx.createRadialGradient(sx, y, 2, sx, y, 46);
    g.addColorStop(0, 'rgba(255,214,140,' + (0.16 + 0.05 * Math.sin(time * 2.2 + i)).toFixed(3) + ')'); g.addColorStop(1, 'rgba(255,214,140,0)');
    ctx.globalAlpha = 1; ctx.fillStyle = g; ctx.fillRect(sx - 46, y - 46, 92, 92);
    ctx.globalCompositeOperation = 'source-over'; ctx.fillStyle = '#f4ead0';
    for (let m = 0; m < (nm == null ? 3 : nm); m++) {
      const r = 9 + aliveRnd(i * 3 + m) * 10, sp = (1.8 + aliveRnd(i * 7 + m) * 2.2) * (m % 2 ? 1 : -1), a = time * sp + m * 2.1;
      const mx = sx + Math.cos(a) * r + Math.sin(time * 9 + m) * 2, my = y + Math.sin(a * 1.3) * r * 0.7 + Math.cos(time * 11 + m) * 2;
      ctx.fillRect(Math.round(mx / 2) * 2, Math.round(my / 2) * 2, 2, 2);
    }
    ctx.globalCompositeOperation = 'lighter';
  }
  // strip lights: mostly steady, now and then a stutter
  for (let i = 0; i < (A.tubes || []).length; i++) {
    const [x0, x1, y] = A.tubes[i]; if (!vis(x0, x1)) continue;
    const t = (time + i * 3.3) % (5 + i * 2), off = t < 0.1 || (t > 0.18 && t < 0.24) || (t > 0.3 && t < 0.62);
    if (!off) continue;
    ctx.globalCompositeOperation = 'source-over'; ctx.globalAlpha = 1; ctx.fillStyle = 'rgba(14,16,22,0.6)';
    ctx.fillRect(x0 - cam.x - 2, y - 4, x1 - x0 + 4, 8);
    ctx.fillStyle = 'rgba(8,10,16,0.22)'; ctx.fillRect(x0 - cam.x - 30, y + 4, x1 - x0 + 60, 90);
  }
  // spinning things: a bright notch going round an ellipse
  ctx.globalCompositeOperation = 'source-over';
  for (const [x, y, rx, ry, sp] of A.spin || []) {
    const sx = x - cam.x; if (sx < -60 || sx > W + 60) continue;
    for (let j = 0; j < 2; j++) { const a = time * sp * Math.PI * 2 + j * Math.PI;
      ctx.globalAlpha = 0.55; ctx.fillStyle = j ? '#1a1a20' : '#f0f0f0'; ctx.fillRect(Math.round((sx + Math.cos(a) * rx) / 2) * 2 - 1, Math.round((y + Math.sin(a) * ry) / 2) * 2 - 1, 3, 3); }
  }
  for (const [x, y, r] of A.prop || []) {
    const sx = x - cam.x; if (sx < -60 || sx > W + 60) continue;
    ctx.globalAlpha = 0.28; ctx.fillStyle = '#dfe6ee'; ctx.beginPath(); ctx.ellipse(sx, y, 4, r, 0, 0, Math.PI * 2); ctx.fill();
    const l = Math.cos(time * 37) * r; ctx.globalAlpha = 0.85; ctx.fillStyle = '#2a2e36'; ctx.fillRect(Math.round(sx) - 2, Math.round(y - Math.abs(l)), 4, Math.max(2, Math.round(Math.abs(l) * 2)));
  }
  for (const [x, y, col, per] of A.blink || []) {
    const sx = x - cam.x; if (sx < -20 || sx > W + 20 || (time % (per || 1.6)) > (per || 1.6) * 0.4) continue;
    ctx.globalCompositeOperation = 'lighter'; ctx.fillStyle = col;
    ctx.globalAlpha = 1; ctx.fillRect(Math.round(sx / 2) * 2 - 2, Math.round(y / 2) * 2 - 2, 4, 4);
    ctx.globalAlpha = 0.3; ctx.fillRect(Math.round(sx / 2) * 2 - 6, Math.round(y / 2) * 2 - 6, 12, 12);
    ctx.globalAlpha = 0.12; ctx.fillRect(Math.round(sx / 2) * 2 - 12, Math.round(y / 2) * 2 - 12, 24, 24);
    ctx.globalCompositeOperation = 'source-over';
  }
  for (let c = 0; c < (A.city || []).length; c++) {
    const [x0, x1, y0, y1, n, col] = A.city[c];
    for (let i = 0; i < n; i++) {
      const slot = Math.floor(time / (3 + aliveRnd(i + c * 100) * 5) + aliveRnd(i * 3 + c)), r1 = aliveRnd(i * 31 + slot * 7 + c), r2 = aliveRnd(i * 17 + slot * 3 + c);
      if (aliveRnd(i + slot * 11 + c) < 0.45) continue;
      const sx = x0 + r1 * (x1 - x0) - cam.x; if (sx < -4 || sx > W + 4) continue;
      ctx.globalAlpha = 0.85; ctx.fillStyle = col || '#ffd890'; ctx.fillRect(Math.round(sx / 2) * 2, Math.round((y0 + r2 * (y1 - y0)) / 2) * 2, 2, 4);
    }
  }
  ctx.globalCompositeOperation = 'lighter';
  for (let c = 0; c < (A.glint || []).length; c++) {
    const [x0, x1, y0, y1, n] = A.glint[c];
    for (let i = 0; i < n; i++) {
      const per = 0.9 + aliveRnd(i + c * 50) * 1.4, ph = (time + aliveRnd(i * 7) * per) / per, slot = Math.floor(ph), f = ph - slot;
      const sx = x0 + aliveRnd(i * 13 + slot * 5) * (x1 - x0) - cam.x; if (sx < -6 || sx > W + 6) continue;
      const y = y0 + aliveRnd(i * 29 + slot * 3) * (y1 - y0), a = Math.sin(f * Math.PI);
      ctx.globalAlpha = a * 0.8; ctx.fillStyle = '#ffffff'; ctx.fillRect(Math.round(sx / 2) * 2 - (a > 0.6 ? 3 : 1), Math.round(y / 2) * 2, a > 0.6 ? 8 : 4, 2);
    }
  }
  ctx.globalCompositeOperation = 'source-over';
  for (const [x0, x1, y] of A.foam || []) {
    for (let x = Math.max(x0, Math.floor(cam.x / 8) * 8 - 8); x < Math.min(x1, cam.x + W + 8); x += 8) {
      const run = Math.sin(time * 0.9 + x * 0.004) * 5 + Math.sin(time * 1.7 + x * 0.013) * 2, a = 0.5 + 0.3 * Math.sin(time * 0.9 + x * 0.004);
      if (aliveRnd(x * 0.37 + Math.floor(time * 0.7 + aliveRnd(x) * 3)) < 0.45) continue;
      ctx.globalAlpha = a * 0.7; ctx.fillStyle = '#f4fbff'; ctx.fillRect(Math.round((x - cam.x) / 2) * 2, Math.round((y + run) / 2) * 2, 8, 2);
      if (aliveRnd(x) > 0.6) { ctx.globalAlpha = a * 0.6; ctx.fillRect(Math.round((x - cam.x) / 2) * 2 + 2, Math.round((y + run) / 2) * 2 - 2, 4, 2); }
    }
  }
  for (const [x0, x1, y0, y1, rows] of A.board || []) {
    if (!vis(x0, x1)) continue; const rh = (y1 - y0) / rows, r = Math.floor(time / 2.3) % rows, f = (time / 2.3) % 1;
    if (f > 0.35) continue;
    ctx.globalAlpha = 0.8; ctx.fillStyle = '#121218'; ctx.fillRect(x0 - cam.x, y0 + r * rh, x1 - x0, rh);
    ctx.fillStyle = '#ffc040'; for (let k = 0; k < (x1 - x0) / 6; k++) if (aliveRnd(k + Math.floor(time * 12)) > 0.55) ctx.fillRect(Math.round((x0 - cam.x + 2 + k * 6) / 2) * 2, Math.round((y0 + r * rh + rh / 2 - 1) / 2) * 2, 4, 2);
  }
  for (const [x0, x1, y0, y1] of A.tv || []) {
    if (!vis(x0, x1)) continue;
    ctx.globalAlpha = 0.12 + 0.12 * aliveRnd(Math.floor(time * 8)); ctx.fillStyle = aliveRnd(Math.floor(time * 2)) > 0.5 ? '#c8e8ff' : '#80ff90';
    ctx.globalCompositeOperation = 'lighter'; ctx.fillRect(x0 - cam.x - 14, y0 - 10, x1 - x0 + 28, y1 - y0 + 26);
    ctx.globalCompositeOperation = 'source-over'; ctx.globalAlpha = 0.9; ctx.fillStyle = '#ffffff';
    ctx.fillRect(Math.round((x0 - cam.x + (x1 - x0) * (0.5 + 0.4 * Math.sin(time * 1.3))) / 2) * 2, Math.round((y0 + (y1 - y0) * (0.5 + 0.3 * Math.sin(time * 2.1))) / 2) * 2, 2, 2);
  }
  for (const [x0, x1, y, sp] of A.belt || []) {
    if (!vis(x0, x1)) continue; ctx.globalAlpha = 0.45; ctx.fillStyle = '#20242c';
    for (let x = x0 + ((time * sp) % 14); x < x1; x += 14) ctx.fillRect(Math.round((x - cam.x) / 2) * 2, y, 2, 6);
  }
  for (let i = 0; i < (A.steam || []).length; i++) {
    const [x, y, col] = A.steam[i], sx = x - cam.x; if (sx < -80 || sx > W + 80) continue;
    for (let j = 0; j < 6; j++) { const k = (time * 0.35 + j / 6 + i * 0.13) % 1;
      ctx.globalAlpha = (1 - k) * 0.35; ctx.fillStyle = col || '#e8e8e8';
      pxCircle(Math.round((sx + Math.sin(k * 5 + j) * 6 + k * 18) / 2) * 2, Math.round((y - k * 80) / 2) * 2, Math.round(3 + k * 9), col || '#e8e8e8'); }
  }
  for (const [y0, y1, al] of A.mist || []) {
    for (let j = 0; j < 4; j++) { const w = 700, x = ((time * (8 + j * 3) - cam.x * 0.9 + j * 410) % (W + w) + W + w) % (W + w) - w;
      const g = ctx.createLinearGradient(x, 0, x + w, 0); g.addColorStop(0, 'rgba(235,235,245,0)'); g.addColorStop(0.5, 'rgba(235,235,245,1)'); g.addColorStop(1, 'rgba(235,235,245,0)');
      ctx.globalAlpha = al * (0.6 + 0.4 * Math.sin(time * 0.3 + j)); ctx.fillStyle = g; ctx.fillRect(x, y0 + j * (y1 - y0) / 6, w, (y1 - y0) / 2); }
  }
  ctx.globalCompositeOperation = 'lighter';
  for (let c = 0; c < (A.flies || []).length; c++) {
    const [x0, x1, y0, y1, n] = A.flies[c];
    for (let i = 0; i < n; i++) {
      const bx = x0 + aliveRnd(i + c * 70) * (x1 - x0), by = y0 + aliveRnd(i * 3 + c) * (y1 - y0), t = time * 0.5 + i;
      const sx = bx + Math.sin(t) * 30 + Math.sin(t * 2.3) * 10 - cam.x, sy = by + Math.sin(t * 1.7) * 14; if (sx < -10 || sx > W + 10) continue;
      const a = Math.max(0, Math.sin(time * (1.5 + aliveRnd(i) * 2) + i * 2)); if (a < 0.1) continue;
      ctx.globalAlpha = a; ctx.fillStyle = '#e8ff70'; ctx.fillRect(Math.round(sx / 2) * 2, Math.round(sy / 2) * 2, 2, 2);
      ctx.globalAlpha = a * 0.3; ctx.fillRect(Math.round(sx / 2) * 2 - 3, Math.round(sy / 2) * 2 - 3, 8, 8);
    }
  }
  // puddles: a drop lands and a ring spreads
  ctx.globalCompositeOperation = 'source-over';
  for (let i = 0; i < (A.drips || []).length; i++) {
    const [x, y, rx] = A.drips[i], sx = x - cam.x; if (sx < -60 || sx > W + 60) continue;
    for (let j = 0; j < 2; j++) {
      const per = 2.2 + aliveRnd(i * 5 + j) * 2.4, t = ((time + aliveRnd(i * 9 + j) * per) % per) / 1.1; if (t > 1) continue;
      const ox = (aliveRnd(i * 13 + j + Math.floor((time + aliveRnd(i * 9 + j) * per) / per)) - 0.5) * rx;
      ctx.globalAlpha = (1 - t) * 0.7; ctx.strokeStyle = '#d8e8f4'; ctx.lineWidth = 2;
      ctx.beginPath(); ctx.ellipse(Math.round((sx + ox) / 2) * 2, y, 2 + t * rx * 0.45, 1 + t * rx * 0.13, 0, 0, Math.PI * 2); ctx.stroke();
    }
  }
  ctx.restore();
  // PixelLab critters
  for (let i = 0; i < (A.anims || []).length; i++) {
    const a = A.anims[i];
    if (a.every) { const ph = (time + i * 3.7) % a.every; if (ph > a.dur) continue; aliveFrame(a.k, Math.min(ALIVE_SHEETS[a.k] - 1, Math.floor(ph / a.dur * ALIVE_SHEETS[a.k])), a.x, a.y, a.sc || 2, a.flip, null, A.dim); continue; }
    aliveFrame(a.k, Math.floor(time * (a.fps || 8) + i * 3), a.x, a.y, a.sc || 2, a.flip, null, A.dim);
  }
  for (let i = 0; i < (A.wander || []).length; i++) {
    const w = A.wander[i], t = time * 0.6 + i * 5, x = w.x + Math.sin(t) * w.rx + Math.sin(t * 2.7) * w.rx * 0.3, y = w.y + Math.sin(t * 1.9) * w.ry;
    aliveFrame(w.k, Math.floor(time * (w.fps || 16)), x, y, w.sc || 1, Math.cos(t) < 0, null, A.dim);
  }
  for (let i = 0; i < (A.walks || []).length; i++) {
    const w = A.walks[i], ev = Math.floor((time + i * 7) / w.every), ph = (time + i * 7) % w.every; if (ph > w.dur) continue;
    const rev = w.back && ev % 2 === 1, f = ph / w.dur, x = rev ? w.x1 + (w.x0 - w.x1) * f : w.x0 + (w.x1 - w.x0) * f;
    aliveFrame(w.k, Math.floor(time * (w.fps || 10)), x, w.y + (w.bob ? Math.round(Math.sin(f * Math.PI * w.dur * 1.5) * w.bob) : 0), w.sc || 2, rev !== !!w.flip, null, A.dim);
  }
}

// ---- the stages
['fox_trot', 'cat', 'pigeon_peck', 'pigeon', 'gull_fly', 'rat', 'duck', 'flag', 'fish', 'heron', 'boat', 'pigeon_fly', 'gull'].forEach(k => aliveSheet(k, 8));
aliveSheet('dragonfly', 4);
ALIVE.frequency = {   // the high street at night and the park behind the underpass
  dim: 0.8,
  neon: [[347, 523, 198, 229, '#ff4a5a'], [550, 724, 198, 229, '#5ac8ff'], [751, 916, 198, 229, '#3ee08a'], [943, 1130, 198, 229, '#c060ff', true], [1155, 1326, 198, 229, '#ffe040']],
  bulbs: [[699, 177, "#8d7c62"], [515, 185, "#a5926e"], [426, 187, "#be9f76"], [431, 185, "#a66c56"], [436, 186, "#ac9e7c"], [631, 185, "#c7b18d"], [636, 185, "#9d8d6d"], [832, 186, "#b9a686"], [1418, 187, "#978568"], [376, 189, "#c5aa75"], [405, 189, "#caad84"], [464, 189, "#ad9e7c"], [493, 189, "#ad7161"], [521, 188, "#9f8863"], [569, 188, "#9f936f"], [581, 188, "#d4c29a"], [609, 188, "#ccc193"], [665, 188, "#ae996f"], [775, 189, "#b19872"], [803, 188, "#b8a17b"], [860, 188, "#c0b794"], [895, 188, "#ad9e81"], [1398, 188, "#ab9a7d"], [1454, 188, "#a99572"], [415, 191, "#b06e64"], [445, 190, "#9b8466"], [511, 191, "#bc7f62"], [560, 191, "#cfb37f"], [619, 191, "#d1927d"], [646, 190, "#a6996e"], [813, 191, "#a65e52"], [841, 190, "#ada475"], [903, 190, "#916a5b"], [1099, 190, "#9b8056"], [1435, 191, "#b6a47e"], [1593, 191, "#9b8462"], [368, 193, "#d4c188"], [383, 193, "#b77668"], [396, 193, "#b8a584"], [456, 191, "#dac9a0"], [471, 193, "#a47563"], [484, 191, "#bba67d"], [498, 192, "#c2ad82"], [574, 192, "#c3b78d"], [589, 193, "#a9696a"], [602, 192, "#c5c08e"], [657, 191, "#bd816b"], [672, 193, "#b97f74"], [684, 193, "#b5a777"], [796, 193, "#aaa375"], [851, 192, "#a5705c"], [1447, 191, "#a87766"], [1461, 193, "#917a58"], [94, 196, "#8e8864"], [181, 196, "#a69772"], [268, 196, "#9b926a"]],
  lamps: [[22, 165], [325, 165], [744, 165], [1147, 165], [1525, 165], [1672, 165], [2668, 136], [3130, 136]],
  tubes: [[1893, 1932, 136], [2005, 2087, 146], [2150, 2192, 156]],
  drips: [[165, 440, 30], [418, 421, 34], [803, 440, 40], [1298, 416, 36], [1441, 440, 40], [649, 484, 34], [319, 517, 36], [1727, 500, 30], [1958, 385, 40]],
  anims: [{ k: 'cat', x: 2847, y: 210, fps: 5, sc: 0.5 }],
  walks: [{ k: 'fox_trot', x0: 2330, x1: 3440, y: 334, fps: 12, sc: 1, every: 26, dur: 9, back: true }],
};

// the Social: a string of coloured bulbs every 80 along the beam, red, yellow, blue, green
const SOCIAL_BULBS = []; for (let x = 20, i = 0; x < 2900; x += 80, i++) SOCIAL_BULBS.push([x, 55, ['#ff5050', '#ffd040', '#50b8ff', '#60e070'][i % 4]]);
ALIVE.soundz = {   // the pirate station flat, the corridor, the roof
  neon: [[487, 567, 78, 115, '#ff3030']],
  lamps: [[343, 85, 0], [1050, 85, 0]],
  spin: [[465, 247, 16, 3, 0.55], [597, 247, 16, 3, 0.55], [3040, 362, 12, 4, 3]],
  city: [[0, 95, 110, 240, 6], [872, 960, 110, 250, 6], [2770, 3600, 165, 300, 40]],
  tubes: [[1585, 1615, 55], [1670, 1700, 55], [1805, 1835, 55], [2010, 2040, 55], [2190, 2220, 55]],
  blink: [[3362, 42, '#ff2020', 1.8]],
};
ALIVE.airport = {   // the strip, then Arrivals
  prop: [[165, 296, 26], [312, 290, 26]],
  blink: [[757, 188, '#ff3030', 1.4], [1997, 188, '#40ff60', 2.2]],
  belt: [[2350, 2710, 296, 30]],
  board: [[2675, 2750, 122, 162, 4]],
  walks: [{ k: 'gull_fly', x0: -100, x1: 1400, y: 150, fps: 9, sc: 0.5, every: 21, dur: 14, back: true, bob: 6 },
          { k: 'gull_fly', x0: 3000, x1: 3700, y: 110, fps: 9, sc: 0.45, every: 17, dur: 8, back: true, bob: 4 }],
};
ALIVE.divebar = {   // the bar, then the hills at sunset
  lamps: [[100, 82, 0], [340, 82, 0], [600, 82, 0], [1063, 82, 0], [1320, 82, 0], [1573, 82, 0], [1775, 82, 0]],
  tv: [[768, 822, 85, 115]],
  steam: [[668, 168, '#f0e8e0'], [1388, 168, '#f0e8e0']],
  blink: [[1630, 125, '#ff6040', 2.6]],
  flies: [[2000, 3600, 190, 330, 26]],
  walks: [{ k: 'pigeon_fly', x0: 2100, x1: 3700, y: 95, fps: 10, sc: 0.35, every: 23, dur: 15, back: true, bob: 4 }],
};
ALIVE.beach = {
  patch: [[1466, 1502, 84, 126, '#16a5f9', '#2eb0f9']],   // the painted lifeguard flag, replaced by the flapping one
  glint: [[0, 3600, 196, 300, 70]],
  anims: [{ k: 'flag', x: 1477, y: 128, fps: 9, sc: 0.62 }, { k: 'gull', x: 2560, y: 362, fps: 4, sc: 0.55 }],
  walks: [{ k: 'boat', x0: -200, x1: 3800, y: 196, fps: 3, sc: 0.55, every: 160, dur: 150, back: true },
          { k: 'gull_fly', x0: -100, x1: 1900, y: 120, fps: 9, sc: 0.5, every: 15, dur: 11, back: true, bob: 8 },
          { k: 'gull_fly', x0: 1700, x1: 3700, y: 80, fps: 8, sc: 0.4, every: 19, dur: 12, back: true, bob: 6 }],
};
ALIVE.club = {   // outside: the strip along the wall
  neon: [[2140, 2350, 235, 305, '#ff40b0', true], [1980, 2090, 180, 345, '#ff50c8']],
  lamps: [[2770, 185], [3077, 185], [3490, 185]],
  city: [[2350, 3600, 180, 196, 14, '#ffc070']],
  anims: [{ k: 'cat', x: 3240, y: 212, fps: 5, sc: 0.45 }],
};
ALIVE.social = { bulbs: SOCIAL_BULBS, lamps: [[590, 135, 0], [905, 130, 0]] };
ALIVE.nl_station = {   // Orpington station at night
  dim: 0.8,
  lamps: [[240, 180], [512, 180], [740, 180], [2540, 100], [3050, 225], [3250, 225]],
  drips: [[230, 435, 50], [380, 470, 40], [740, 430, 40], [600, 470, 30], [250, 500, 30]],
  board: [[1378, 1495, 140, 185, 6]],
  tubes: [[1150, 1280, 38], [1535, 1650, 75], [1870, 1985, 75], [2320, 2460, 38]],
  neon: [[1803, 1840, 255, 280, '#40d0ff'], [1886, 1923, 255, 280, '#40d0ff'], [1968, 2005, 255, 280, '#40d0ff'], [2052, 2089, 255, 280, '#40d0ff'], [2300, 2405, 222, 325, '#d0f0ff']],
  walks: [{ k: 'fox_trot', x0: 2800, x1: 3400, y: 302, fps: 12, sc: 0.6, every: 31, dur: 7, back: true }],
};
ALIVE.nl_cx = {   // Charing Cross
  dim: 0.85,
  lamps: [[712, 190], [997, 190], [1432, 190], [487, 222], [1717, 190], [2152, 190], [2935, 190], [3037, 170], [3360, 205]],
  board: [[1075, 1355, 180, 250, 6]],
  city: [[1900, 2500, 190, 270, 14], [2900, 3600, 100, 260, 10]],
  blink: [[420, 326, '#fff4c0', 3]],
  anims: [{ k: 'pigeon_peck', x: 1100, y: 422, fps: 6, sc: 0.45 }, { k: 'pigeon', x: 1160, y: 430, fps: 5, sc: 0.45, flip: true }, { k: 'pigeon_peck', x: 2240, y: 380, fps: 7, sc: 0.42, flip: true }],
  walks: [{ k: 'pigeon', x0: 1500, x1: 2100, y: 418, fps: 10, sc: 0.45, every: 24, dur: 14, back: true },
          { k: 'pigeon_fly', x0: 300, x1: 3000, y: 110, fps: 12, sc: 0.45, every: 13, dur: 8, back: true, bob: 6 }],
};
ALIVE.nl_alley = {   // the smoking area round the back
  dim: 0.8,
  lamps: [[320, 120], [825, 130], [1440, 130], [1915, 130], [2118, 125], [2895, 180], [3185, 125]],
  neon: [[1385, 1470, 170, 330, '#40ff80']],
  spin: [[2715, 137, 16, 16, 3]],
  drips: [[300, 385, 50], [900, 380, 50], [1360, 385, 40], [2200, 385, 50], [2800, 380, 40]],
  steam: [[1030, 150, '#c8ccd4']],
  anims: [{ k: 'cat', x: 2390, y: 334, fps: 5, sc: 0.45 }],
  walks: [{ k: 'rat', x0: 380, x1: 1600, y: 342, fps: 16, sc: 0.42, every: 17, dur: 5 }, { k: 'rat', x0: 3200, x1: 2000, y: 340, fps: 16, sc: 0.4, every: 23, dur: 6, flip: true }],
};
ALIVE.arrival = {   // Denise's fishery, by day
  steam: [[445, 120, '#d8d8d8']],
  glint: [[1270, 3400, 232, 330, 26]],
  anims: [{ k: 'fish', x: 2250, y: 312, sc: 0.5, every: 11, dur: 1.1 }, { k: 'fish', x: 2720, y: 300, sc: 0.45, every: 14, dur: 1.1 }, { k: 'fish', x: 3220, y: 306, sc: 0.5, every: 17, dur: 1.1 },
          { k: 'heron', x: 2460, y: 332, fps: 3, sc: 0.8 }],
  wander: [{ k: 'dragonfly', x: 2240, y: 275, rx: 60, ry: 16, sc: 0.4 }, { k: 'dragonfly', x: 3060, y: 285, rx: 50, ry: 14, sc: 0.4 }],
  walks: [{ k: 'duck', x0: 1450, x1: 3450, y: 304, fps: 4, sc: 0.45, every: 70, dur: 65, back: true }, { k: 'duck', x0: 1600, x1: 3450, y: 296, fps: 4, sc: 0.4, every: 90, dur: 80, back: true }],
};
ALIVE.pegnine = {   // Peg Nine at dawn
  mist: [[195, 255, 0.22]],
  glint: [[0, 3200, 255, 325, 14]],
  blink: [[672, 306, '#ff2020', 4]],
  anims: [{ k: 'fish', x: 1150, y: 322, sc: 0.5, every: 13, dur: 1.1 }, { k: 'fish', x: 2300, y: 318, sc: 0.45, every: 19, dur: 1.1 }, { k: 'heron', x: 1720, y: 336, fps: 3, sc: 0.8, flip: true }],
  walks: [{ k: 'duck', x0: 100, x1: 3200, y: 318, fps: 4, sc: 0.45, every: 95, dur: 90, back: true }],
};
ALIVE.ramsden = {   // the estate on fire: the tower windows going on and off
  city: [[0, 3600, 20, 220, 40, '#ffb060']],
};
