// ------------------------------------------------------------------ Version 64: stages painted in Meshy
// A stage listed here is one long picture, sky to floor, cut into 512 pixel tiles (bg/meshy/<stage>_<n>.png, made by
// tools/v64/meshy_bg.py) and drawn edge to edge in place of its old pieced-together backdrop. Things the game does on
// top of the backdrop (the Christmas tree's star, and so on) are still drawn by meshyOver. Until every tile of a stage
// has loaded, the old backdrop is drawn instead.
const MESHY_BG = { frequency: 4, soundz: 4, airport: 4, divebar: 4, beach: 4, club: 4, nl_station: 4, nl_cx: 4, nl_alley: 4 };
STAGES.beach.secret.x = 2930;   // the sandcastle
// where the painted pictures put things the game needs to know about
STAGES.soundz.secret.x = 2024;   // the broken lift
const MESHY_TILE = 512;
function meshyFiles(k) { const out = []; for (let i = 0; i < (MESHY_BG[k] || 0); i++) out.push('meshy/' + k + '_' + i); return out; }
for (const k in MESHY_BG) ASSET_BG.push(...meshyFiles(k));
function meshyBg() { return meshyStage(S && S.key); }
function meshyStage(k) {
  if (!MESHY_BG[k]) return false;
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
  if (k === 'divebar') {
    ePut('stool', CARAB_X - 25, FT + 10, 2);   // the Carabiniere's own stool
    // the Espace, burning out on the track (Sam's drive ends here)
    if (!S.drv) { const wx = 2760, img = eImg('mpv'); if (img) { const w = img.width * 2, x = Math.round((wx - cam.x - w / 2) / 2) * 2, b = FT + 2;
      if (x > -w - 100 && x < W + 100) { ePut('mpv', wx - w / 2, b, 2);
        for (let i = 0; i < 5; i++) drawFireSprite(x + 20 + i * (w - 40) / 4, b - img.height * 2 + 18 + (i % 2) * 8, wx + i);
        for (let i = 0; i < 4; i++) { const k2 = (time * 0.35 + i / 4) % 1; pxCircle(x + w / 2 + Math.sin(k2 * 5 + i) * 16, b - img.height * 2 - k2 * 180, Math.round(12 + k2 * 34), 'rgba(40,36,36,' + (0.5 * (1 - k2)).toFixed(2) + ')'); } } } }
  }
  if (k === 'beach' && ST.stuart) {   // Stuart, buried up to his neck
    const x = Math.round((ST.stuart - cam.x) / 2) * 2; if (x > -60 && x < W + 60) { ctx.fillStyle = '#d8c088'; ctx.fillRect(x - 30, FT + 44, 60, 10); ctx.fillRect(x - 20, FT + 40, 40, 4); ePut('stuart', ST.stuart - 20, FT + 48, 2); }
  }
  if (k === 'club' && cam.x < 1950) {
    // the DJ in his booth, and the light rig sweeping the room (inside only)
    ctx.save(); ctx.beginPath(); ctx.rect(0, 0, Math.min(W, 1950 - cam.x), H); ctx.clip();
    { const x = 972 - cam.x; if (x > -80 && x < W + 80) clubDancer(x, FT - 40, 98, true); }
    ePut('djbooth', 860, FT + 2, 2);
    ctx.globalCompositeOperation = 'lighter';
    for (let i = 0; i < 6; i++) { const ox = ((i * 330 - cam.x * 0.9) % (W + 300) + W + 300) % (W + 300) - 150, ang = Math.sin(time * (0.7 + i * 0.13) + i) * 0.6;
      ctx.fillStyle = ['rgba(255,60,180,0.12)', 'rgba(60,200,255,0.12)', 'rgba(255,220,60,0.1)', 'rgba(120,255,120,0.1)'][i % 4];
      ctx.beginPath(); ctx.moveTo(ox, 10); ctx.lineTo(ox + Math.sin(ang) * 600 - 50, H); ctx.lineTo(ox + Math.sin(ang) * 600 + 50, H); ctx.closePath(); ctx.fill(); }
    ctx.restore();
  }
  if (k === 'nl_station') nlGateline(NL_ST_GATE);
  if (k === 'nl_cx') nlGateline(NL_CX_GATE);   // the ticket barriers are people the game runs
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
