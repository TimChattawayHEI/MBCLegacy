// ------------------------------------------------------------------ Version 64: stages painted in Meshy
// A stage listed here is one long picture, sky to floor, cut into 512 pixel tiles (bg/meshy/<stage>_<n>.png, made by
// tools/v64/meshy_bg.py) and drawn edge to edge in place of its old pieced-together backdrop. Things the game does on
// top of the backdrop (the Christmas tree's star, and so on) are still drawn by meshyOver. Until every tile of a stage
// has loaded, the old backdrop is drawn instead.
const MESHY_BG = { frequency: 4 };
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
function meshyOver(k) {
  if (k === 'frequency') { if (S.tree) drawTree(S.tree); }
}
