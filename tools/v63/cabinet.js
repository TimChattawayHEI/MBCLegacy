// ================================================================== Version 63: the trophy cabinet
// At the far end of the Harvest Moon, past the arcade: an open-fronted cabinet whose shelves fill up as you win
// trophies (16 on the shelves for the 29 trophies, a share matching yours; all of them when you've got the lot).
// The count is on the drawer. HIT opens the trophy room. Art: tools/v63/trophy_art.py; TROPHY_CAB comes from its json.
const TROPHY_X = 2420;   // the cabinet's middle, in the pub's world
function trophyShown() {
  const n = achCount(), t = ACH_LIST.length, k = TROPHY_CAB.items.length;
  return n <= 0 ? 0 : n >= t ? k : Math.min(k - 1, Math.max(1, Math.round(n / t * k)));
}
function trophyCabDraw(cx) {
  const img = pubImg('trophy_cab'); if (!img) return;
  const L = TROPHY_X - img.width, T = 414 - img.height * 2, x0 = Math.round((L - cx) / 2) * 2;
  if (x0 > W + 4 || x0 + img.width * 2 < -4) return;
  bgPut(img, L, 414);
  const it = pubImg('trophy_items'); if (!it) return;
  ctx.save(); ctx.imageSmoothingEnabled = false;
  TROPHY_CAB.items.slice(0, trophyShown()).forEach(([sx, sy, w, h, ix, iy]) => ctx.drawImage(it, sx, sy, w, h, x0 + ix * 2, T + iy * 2, w * 2, h * 2));
  // the newest one catches the light now and then
  const k = trophyShown(); if (k) { const [, , w, h, ix, iy] = TROPHY_CAB.items[k - 1], ph = (time * 0.6) % 3; if (ph < 0.5) { ctx.fillStyle = 'rgba(255,250,220,0.75)'; ctx.fillRect(x0 + (ix + Math.floor(ph / 0.5 * w)) * 2, T + (iy + 1) * 2, 2, 2); } }
  ctx.restore();
}
// sharp text over the room: a sign above, the count on the drawer
function trophyCabText(cx) {
  const x = TROPHY_X - cx; if (x < -120 || x > W + 120) return;
  textOut('TROPHIES', x, 168, '15px ' + DISPLAY, '#ffd23f', OUT, 4);
  ctx.font = '10px ' + DISPLAY; ctx.fillStyle = '#ffd23f'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillText(achCount() + ' / ' + ACH_LIST.length, x, 414 - (TROPHY_CAB.h - 104) * 2);
}
