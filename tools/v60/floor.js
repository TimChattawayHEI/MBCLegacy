// ------------------------------------------------------------------ Version 60: painted floors
// Each stage's floor, painted down from its own backdrop (tools/v60/floors.py), repeated along the stage at 2x from the
// floor top to the bottom of the screen and anchored to the world so it scrolls with it. Until a picture has loaded the
// stage draws its old flat floor instead.
const FLOOR_NAMES = ['freq_pave', 'freq_under', 'freq_park', 'sz_carpet', 'sz_corr', 'sz_roof', 'air_apron', 'air_rank',
  'bar_in', 'bar_out', 'club_out', 'st_hall', 'st_plat', 'cx', 'alley', 'carpark', 'bank', 'peg', 'ram'];
const FLOOR_IMG = {};
function floorImg(name) {
  let im = FLOOR_IMG[name];
  if (!im) { im = FLOOR_IMG[name] = new Image(); im.src = 'bg/floors/' + name + '.png'; }
  return im.complete && im.naturalWidth ? im : null;
}
FLOOR_NAMES.forEach(floorImg);
// world x0..x1, from y0 (FT) down; camx and wmax for pictures drawn into a cache rather than the screen
function floorTex(name, x0, x1, camx = cam.x, y0 = FT, wmax = W) {
  const im = floorImg(name); if (!im) return false;
  const a = Math.max(0, Math.round((x0 - camx) / 2) * 2), b = Math.min(wmax, Math.round((x1 - camx) / 2) * 2);
  if (b <= a) return true;
  const tw = im.width * 2, th = im.height * 2, sm = ctx.imageSmoothingEnabled;
  ctx.save(); ctx.beginPath(); ctx.rect(a, y0, b - a, H - y0); ctx.clip(); ctx.imageSmoothingEnabled = false;
  for (let wx = Math.floor((camx + a) / tw) * tw; wx < camx + b; wx += tw) ctx.drawImage(im, Math.round((wx - camx) / 2) * 2, y0, tw, Math.max(th, H - y0));
  ctx.restore(); ctx.imageSmoothingEnabled = sm;
  return true;
}
// several zones at once, all or none (so a half-loaded stage never mixes old and new)
function floorAll(parts) {
  if (!parts.every(p => floorImg(p[0]))) return false;
  for (const p of parts) floorTex(p[0], p[1], p[2]);
  return true;
}
