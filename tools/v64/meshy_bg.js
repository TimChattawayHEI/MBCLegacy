// ------------------------------------------------------------------ Version 64: stages painted in Meshy
// A stage listed here is one long picture, sky to floor, cut into 512 pixel tiles (bg/meshy/<stage>_<n>.png, made by
// tools/v64/meshy_bg.py) and drawn edge to edge in place of its old pieced-together backdrop. Things the game does on
// top of the backdrop (the Christmas tree's star, and so on) are still drawn by meshyOver. Until every tile of a stage
// has loaded, the old backdrop is drawn instead.
const MESHY_BG = { frequency: 4, soundz: 4, airport: 4 };
// where the painted pictures put things the game needs to know about
STAGES.soundz.secret.x = 2024;   // the broken lift
const MESHY_TILE = 512;
function meshyFiles(k) { const out = []; for (let i = 0; i < (MESHY_BG[k] || 0); i++) out.push('meshy/' + k + '_' + i); return out; }
for (const k in MESHY_BG) ASSET_BG.push(...meshyFiles(k));
function meshyBg() {
  const k = S && S.key; if (!MESHY_BG[k]) return false;
  const files = meshyFiles(k); if (!bgReady(files)) return false;
  for (let i = 0; i < files.length; i++) bgPut(bgImg(files[i]), i * MESHY_TILE * 2, H);
  meshyOver(k);
  return true;
}
// the drive to the bar: the coast scenery above the road, on a loop, scrolled with the road
ASSET_BG.push('meshy/road_loop');
function meshyRoad() {
  const img = bgImg('meshy/road_loop'); if (!img) return false;
  const w = img.width * 2, h = img.height * 2, s = ((cam.x % w) + w) % w;
  ctx.save(); ctx.imageSmoothingEnabled = false;
  for (let x = -s; x < W; x += w) ctx.drawImage(img, snap2(x), ROAD_TOP - h, w, h);
  ctx.restore(); return true;
}
function meshyOver(k) {
  if (k === 'frequency') { if (S.tree) drawTree(S.tree); }
  if (k === 'soundz') {
    // Vince, asleep on the sofa
    { const x = 1068 - cam.x; if (x > -140 && x < W + 140) { pxText('z', x + 8 + Math.sin(time * 2) * 3, 214 - (time * 10) % 20, 14, '#efe6d2'); pxText('VINCE', x + 104, FT + 14, 12, '#efe6d2', OUT); } }
    // out on the roof: fireworks over the skyline, and the countdown
    const roofX = 2520 - cam.x;
    if (roofX < W) {
      ctx.save(); ctx.beginPath(); ctx.rect(Math.max(0, roofX), 0, W, 210); ctx.clip(); drawFireworks(S.fireworks ? 9 : 4, S.fireworks ? 1 : 0.8); ctx.restore();
      const x = Math.round(Math.max(roofX + 60, W / 2) / 2) * 2;
      if (x < W - 60) { ctx.fillStyle = OUT; ctx.fillRect(x - 52, 38, 104, 38); ctx.fillStyle = '#101014'; ctx.fillRect(x - 50, 40, 100, 34); pxText(S.fireworks ? '00:00' : '23:5' + (Math.floor(time / 6) % 10), x, 57, 26, S.fireworks ? '#7fe07a' : '#ff5a4a'); }
    }
  }
}
