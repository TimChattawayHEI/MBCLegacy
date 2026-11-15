// Things to smash (Version 85): every breakable has three looks drawn by PixelLab, whole, damaged and wrecked. One hit
// dents it, the last one breaks it: a white pop, a dust ring, bits flying (glass for the phone box, the vending machine
// and the pub table), the food or the weapon jumping out, and the wreck left lying on the floor for the rest of the stage.
const SMASH = {
  bin:       { col: '#8a9096' },
  keg:       { col: '#a8adb2' },
  coolbox:   { col: '#e9eef0' },
  luggage:   { col: '#6a4630' },
  phonebox:  { col: '#c8242a', sc: 3, half: 34, glass: true, isnew: true },   // drawn at 3 so it stands taller than the lads
  aboard:    { col: '#7a5a3a', half: 26, isnew: true },
  crate:     { col: '#8a6238', half: 26, isnew: true },
  vending:   { col: '#5e5a52', half: 28, glass: true, isnew: true },
  pubtable:  { col: '#5a3a24', half: 24, glass: true, isnew: true },
  trolley:   { col: '#b8c0c8', half: 28, isnew: true },
  deckchair: { col: '#d84a4a', half: 26, isnew: true },
};
let smashWrecks = [];
Object.keys(SMASH).forEach(k => { if (SMASH[k].isnew) bgImg('props/' + k); bgImg('props/' + k + '_d'); bgImg('props/' + k + '_w'); });
function smashHalf(t) { return (SMASH[t] && SMASH[t].half) || 22; }
function smashCol(t) { return (SMASH[t] && SMASH[t].col) || '#8a9096'; }
function smashSprite(x, y, flash, name, sc) {
  const img = bgImg('props/' + name); if (!img) return false;
  ctx.save(); ctx.imageSmoothingEnabled = false;
  if (flash) ctx.filter = 'brightness(2.4)';
  ctx.drawImage(img, Math.round((x - img.width * sc / 2) / 2) * 2, Math.round(y / 2) * 2 - (img.height - 3) * sc, img.width * sc, img.height * sc);
  ctx.restore(); return true;
}
// a breakable still standing: dented once it has been hit
function smashDraw(b, x, y) {
  const m = SMASH[b.type]; if (!m) return false;
  const sc = m.sc || 2;
  if (b.hp < 3 && smashSprite(x, y, b.flash > 0, b.type + '_d', sc)) return true;
  if (m.isnew) return smashSprite(x, y, b.flash > 0, b.type, sc);
  return false;
}
// the last hit: the wreck goes down on the floor and whatever was inside jumps out
function smashBreak(b, n0) {
  const m = SMASH[b.type]; if (!m) return;
  smashWrecks.push({ type: b.type, x: b.x, y: b.y, t: time });
  if (m.glass) debris(b.x, b.y, 40, '#d8eef8', 8);
  if (FX.slam) fxPlay('slam', b.x, b.y, 0, false);
  addShake(m.sc === 3 ? 6 : 3);
  const side = player && player.x > b.x ? 1 : -1;   // it lands on the side you hit it from, not on top of the wreck
  for (let i = n0; i < items.length; i++) { const it = items[i]; it.pop = true; it.t = 0; it.x = itemX(b.x + side * 44); it.y = clamp(b.y + 10, FT + 6, FB - 4); }
}
// wrecks lie on the floor, under the food and under everyone's feet; the two that still stand (the phone box and the
// vending machine) go in with the fighters so they are drawn in front of or behind them by depth
function smashWreck(w) {
  const x = w.x - cam.x; if (x < -140 || x > W + 140) return;
  const m = SMASH[w.type], age = time - w.t, hop = age < 0.14 ? (1 - age / 0.14) * 8 : 0;
  smashSprite(x, w.y - hop, age < 0.08, w.type + '_w', m.sc || 2);
}
const smashTall = w => { const img = bgImg('props/' + w.type + '_w'); return img && img.height > 44; };
function smashWrecksDraw() { for (const w of smashWrecks) if (!smashTall(w)) smashWreck(w); }
function smashWrecksList(list) { for (const w of smashWrecks) if (smashTall(w)) list.push({ y: w.y, f: () => smashWreck(w) }); }
// food or a weapon out of a broken thing jumps up and lands in front of it
function smashItem(it) {
  if (!it.pop || it.t >= 0.5) { drawItem(it); return; }
  ctx.save(); ctx.translate(0, -Math.round(Math.sin(it.t / 0.5 * Math.PI) * 56)); drawItem(it); ctx.restore();
}
for (const k in SMASH) { if (SMASH[k].isnew) ASSET_BG.push('props/' + k); ASSET_BG.push('props/' + k + '_d', 'props/' + k + '_w'); }   // preloaded with the rest of the art
