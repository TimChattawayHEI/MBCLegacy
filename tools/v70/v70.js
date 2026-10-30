// Version 70: more Meshy. The train's and the bus's ceilings and floors, skies that drift slower than the scenery,
// a foreground layer that passes in front of the fighters, and the darts wall.

// the sky on the sunny and sunset stages is its own layer (tools/v64/meshy_bg.py "parasky"), scrolled at this
// fraction of the camera, so the clouds hang back while the ground goes by
const MESHY_SKY = { airport: 0.3, beach: 0.3, divebar: 0.3 };
for (const k in MESHY_SKY) ASSET_BG.push('meshy/' + k + '_sky');
function meshySky(k) {
  const p = MESHY_SKY[k]; if (!p) return; const img = bgImg('meshy/' + k + '_sky'); if (!img) return;
  const w = img.width * 2, h = img.height * 2;
  ctx.save(); ctx.imageSmoothingEnabled = false;
  for (let x = -((cam.x * p % w) + w) % w; x < W; x += w) ctx.drawImage(img, Math.round(x / 2) * 2, 0, w, h);
  ctx.restore();
}

// the foreground: Meshy's station column, street lamp, railings and luggage trolley (tools/v70/cut.py), close to the
// camera, so they slide past faster than the stage (FG_P) and anyone right behind one sees through it
const FG_P = 1.3;
const FG_SET = {
  nl_cx: [['column', 640], ['trolley', 1500], ['column', 2250], ['railing', 3000], ['column', 3700]],
  nl_station: [['lamp', 900], ['railing', 2100], ['column', 3300]],
  frequency: [['lamp', 760], ['railing', 1800], ['lamp', 2900], ['lamp', 3900]],
  nl_alley: [['lamp', 1250], ['railing', 2700]],
};
for (const n of ['column', 'lamp', 'railing', 'trolley']) ASSET_BG.push('fg/' + n);
function drawFG() {
  const L = S && FG_SET[S.key]; if (!L || mode !== 'play' && mode !== 'pause') return;
  const lads = (NET.on ? PL : [player]).filter(Boolean);
  for (const [n, fx] of L) {
    const img = bgImg('fg/' + n); if (!img) continue;
    const w = img.width * 2, h = img.height * 2, x = Math.round((fx - cam.x * FG_P - w / 2) / 2) * 2;
    if (x > W || x + w < 0) continue;
    let a = 1;
    for (const q of lads) { const d = Math.abs(q.x - cam.x - (x + w / 2)) - w / 2; a = Math.min(a, Math.max(0.4, Math.min(1, d / 50))); }
    ctx.save(); ctx.globalAlpha = a; ctx.imageSmoothingEnabled = false; ctx.drawImage(img, x, H + 16 - h, w, h); ctx.restore();
  }
}

// the train and the bus: Meshy's ceiling and floor (tools/v70/cut.py), so there's no black above the carriage wall
// and no plain floor under it. A carriage has three wall sections then its end; the ceiling and floor run under all four
function nlTrainCeilFloor(which) {
  for (let c = Math.max(0, Math.floor(cam.x / TRAIN.car) - 1); c * TRAIN.car < cam.x + W + TRAIN.car; c++)
    for (let k = 0; k < 4; k++) nlPut(which === 'ceil' ? 'tr_ceil' : 'tr_floor', c * TRAIN.car + k * TRAIN.seg, which === 'ceil' ? 92 : H);
}
function nlBusCeilFloor(which) {
  const img = NLX.img(which === 'ceil' ? 'bus_ceil' : 'bus_floor'); if (!img) return false;
  ctx.save(); ctx.imageSmoothingEnabled = false;
  ctx.drawImage(img, 0, which === 'ceil' ? 0 : H - img.height * 2, img.width * 2, img.height * 2);
  ctx.restore(); return true;
}
