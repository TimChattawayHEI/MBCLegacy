// Livelier backgrounds (Version 85): small things that move on top of the Meshy paintings, drawn behind the fighters.
// The paintings are untouched. Each stage lists what it has in ALIVE (world x, screen y, as the painting puts it):
//   neon   [x0, x1, y0, y1, colour, stutters]  a sign's glow breathing; a sign that stutters drops out for a blink now and then
//   bulbs  [x, y, colour]                      fairy lights twinkling (found in the painting by tools/v85/bulbs.py)
//   lamps  [x, y]                              a lamp's glow breathing, with moths round it
//   tubes  [x0, x1, y]                         a strip light that flickers
//   drips  [x, y, rx]                          rings spreading on a puddle
//   anims  { k, x, y, fps, sc, flip }          a looping PixelLab animation in place (web/bg/alive/<k>.png, a strip)
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
    const [x, y] = A.lamps[i], sx = x - cam.x; if (sx < -80 || sx > W + 80) continue;
    const g = ctx.createRadialGradient(sx, y, 2, sx, y, 46);
    g.addColorStop(0, 'rgba(255,214,140,' + (0.16 + 0.05 * Math.sin(time * 2.2 + i)).toFixed(3) + ')'); g.addColorStop(1, 'rgba(255,214,140,0)');
    ctx.globalAlpha = 1; ctx.fillStyle = g; ctx.fillRect(sx - 46, y - 46, 92, 92);
    ctx.globalCompositeOperation = 'source-over'; ctx.fillStyle = '#f4ead0';
    for (let m = 0; m < 3; m++) {
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
  for (const a of A.anims || []) aliveFrame(a.k, Math.floor(time * (a.fps || 8)), a.x, a.y, a.sc || 2, a.flip, null, A.dim);
  for (let i = 0; i < (A.walks || []).length; i++) {
    const w = A.walks[i], ev = Math.floor((time + i * 7) / w.every), ph = (time + i * 7) % w.every; if (ph > w.dur) continue;
    const rev = w.back && ev % 2 === 1, f = ph / w.dur, x = rev ? w.x1 + (w.x0 - w.x1) * f : w.x0 + (w.x1 - w.x0) * f;
    aliveFrame(w.k, Math.floor(time * (w.fps || 10)), x, w.y + (w.bob ? Math.round(Math.sin(f * Math.PI * w.dur * 1.5) * w.bob) : 0), w.sc || 2, rev !== !!w.flip, null, A.dim);
  }
}

// ---- the stages
['fox_trot', 'cat', 'pigeon_peck', 'pigeon', 'gull_fly', 'rat', 'duck', 'flag'].forEach(k => aliveSheet(k, 8));
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
