"""Version 52: the last shapes drawn in code become PixelLab art.

Patches web/index.html in place (run from the repo root, after tools/v51_build.py):  python3 tools/v52_build.py
Safe to run again. Images in web/bg/fx (made with PixelLab, kept in its Creator gallery):
  transmitter  Master Control's pirate radio box (the frequency bar shows on its display, the light blinks)
  picker       the Parkie's litter picker (the pole stretches to his reach, handle and jaws keep their shape)
  spod, boilie, float   the far bank's bait rocket, bait balls and the float on their line
  wave, firewave        Big Gary's splash waves and Big Gaz's fire waves
  moon, cloud, firework the Stage 1 moon, daytime clouds and the fireworks when Master Control goes down
Big Gaz's small head flames use the PixelLab fire effect the floor fires already use, drawn smaller.
Each keeps the old code drawing as a fallback while its image loads.
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, 'web', 'index.html')


def swap(s, old, new, label):
    if new in s:
        return s
    if s.count(old) != 1:
        sys.exit(f'v52_build: could not find the {label} (found {s.count(old)} matches)')
    return s.replace(old, new)


s = open(PAGE, encoding='utf-8').read()

# ---------------------------------------------------------------- Master Control's transmitter
s = swap(s, """function drawTransmitter(b) {
  const x = Math.round((b.x - cam.x + (b.flash > 0 ? rand(-3, 3) : 0)) / 2) * 2, y = Math.round(b.y / 2) * 2;
  shadow(x, y, 34, 0);""", """function drawTransmitter(b) {
  const x = Math.round((b.x - cam.x + (b.flash > 0 ? rand(-3, 3) : 0)) / 2) * 2, y = Math.round(b.y / 2) * 2;
  shadow(x, y, 34, 0);
  { const img = bgImg('fx/transmitter');   // the PixelLab box (Version 52): the bar on its display is what's left of it
    if (img) {
      const L = x - img.width, T = y - img.height * 2 + 2;
      ctx.save(); ctx.imageSmoothingEnabled = false; ctx.drawImage(img, L, T, img.width * 2, img.height * 2);
      if (b.flash > 0) { ctx.globalCompositeOperation = 'lighter'; ctx.drawImage(img, L, T, img.width * 2, img.height * 2); }
      ctx.restore();
      ctx.fillStyle = '#10261a'; ctx.fillRect(L + 14, T + 114, 38, 14);
      ctx.fillStyle = '#7fe07a'; ctx.fillRect(L + 16, T + 116, Math.round((34 * b.hp / 7) / 2) * 2, 10);
      if (Math.floor(time * 4) % 2) { ctx.fillStyle = '#4a1210'; ctx.fillRect(L + 20, T + 80, 8, 6); }
      return;
    } }""", 'transmitter')

# ---------------------------------------------------------------- the Parkie's litter picker
s = swap(s, """      const reach = Math.min(1, b.t / 0.12) * 250; ctx.fillStyle = OUT;""",
         """      const reach = Math.min(1, b.t / 0.12) * 250, pk = bgImg('fx/picker');
      if (pk) {   // handle at his hand, jaws at the end, the pole stretched between (Version 52)
        const H2 = pk.height * 2, y0 = Math.round((sy - 86 - pk.height) / 2) * 2, hw = 12, jw = 16, pole = Math.max(0, reach - hw - jw);
        ctx.save(); ctx.imageSmoothingEnabled = false; ctx.translate(Math.round(sx / 2) * 2, y0); ctx.scale(b.face, 1);
        ctx.drawImage(pk, 0, 0, 6, pk.height, 0, 0, hw, H2);
        ctx.drawImage(pk, 6, 0, pk.width - 14, pk.height, hw, 0, pole, H2);
        ctx.drawImage(pk, pk.width - 8, 0, 8, pk.height, hw + pole, 0, jw, H2);
        ctx.restore();
      } else { ctx.fillStyle = OUT;""", 'picker')
s = swap(s, """      ctx.fillStyle = '#9aa1a7'; ctx.fillRect(Math.round((sx + b.face * reach) / 2) * 2 - 6, Math.round((sy - 92) / 2) * 2, 12, 14);
    }""", """      ctx.fillStyle = '#9aa1a7'; ctx.fillRect(Math.round((sx + b.face * reach) / 2) * 2 - 6, Math.round((sy - 92) / 2) * 2, 12, 14); }
    }""", 'picker fallback close')

# ---------------------------------------------------------------- the far bank: float, spods and boilies
s = swap(s, """      ctx.fillStyle = '#ff5a4a'; ctx.fillRect(Math.round(tx / 2) * 2 - 4, Math.round(ty / 2) * 2 - 4, 8, 8);""",
         """      { const fl = bgImg('fx/float'); if (fl) drawSpr(fl, tx, ty, 0, 1); else { ctx.fillStyle = '#ff5a4a'; ctx.fillRect(Math.round(tx / 2) * 2 - 4, Math.round(ty / 2) * 2 - 4, 8, 8); } }""", 'float')
s = swap(s, """      if (s.k === 'spod') { ctx.fillStyle = OUT;""",
         """      const bimg = bgImg('fx/' + s.k);
      if (bimg) drawSpr(bimg, x, y, s.k === 'spod' ? (k < 0.5 ? 0 : Math.PI) : Math.round(s.t * 12) / 2, 1);   // the spod tips over at the top
      else if (s.k === 'spod') { ctx.fillStyle = OUT;""", 'spod and boilie')

# ---------------------------------------------------------------- Big Gary's and Big Gaz's waves
s = swap(s, """function drawWavePixel(h) {
  const x = Math.round((h.x - cam.x) / 2) * 2, y = Math.round(h.y / 2) * 2, d = Math.sign(h.vx) || 1;""",
         """function drawWavePixel(h) {
  const x = Math.round((h.x - cam.x) / 2) * 2, y = Math.round(h.y / 2) * 2, d = Math.sign(h.vx) || 1;
  { const img = bgImg(h.kind === 'wave' ? 'fx/wave' : 'fx/firewave');   // PixelLab waves (Version 52), a little bob as they roll
    if (img) {
      const bob = Math.round(Math.sin(time * 14 + h.x * 0.05) * 1) * 2;
      ctx.save(); ctx.imageSmoothingEnabled = false; ctx.translate(x, y + bob); ctx.scale(d, 1);
      ctx.drawImage(img, -img.width, -img.height * 2 + 4, img.width * 2, img.height * 2); ctx.restore(); return true;
    } }""", 'waves')

# ---------------------------------------------------------------- Big Gaz's head flames: the PixelLab fire, smaller
s = swap(s, """  if (sz >= 12 && drawFireSprite(x, y + 2, seed)) return;""",
         """  if (sz >= 12 && drawFireSprite(x, y + 2, seed)) return;
  { const m = FX.fire, img = fxImg('fire');   // small ones too (Version 52): the same flame, scaled to the size asked for
    if (m && img) {
      const f = (Math.floor(time * m.fps) + Math.abs(Math.floor(seed * 7))) % m.n, k = sz / 22;
      ctx.save(); ctx.imageSmoothingEnabled = false; ctx.translate(Math.round(x / 2) * 2, Math.round(y / 2) * 2);
      ctx.drawImage(img, (f % m.cols) * m.fw, ((f / m.cols) | 0) * m.fh, m.fw, m.fh, -m.ax * 2 * k, -m.ay * 2 * k, m.fw * 2 * k, m.fh * 2 * k);
      ctx.restore(); return;
    } }""", 'small flames')

# ---------------------------------------------------------------- the sky: moon, clouds, fireworks
s = swap(s, """  ctx.fillStyle = '#efe6c8'; circle(820, 60, 18); ctx.fill(); ctx.fillStyle = '#d8ccaa'; ctx.fillRect(812, 52, 6, 4); ctx.fillRect(824, 64, 4, 4);""",
         """  { const mo = bgImg('fx/moon'); if (mo) { ctx.save(); ctx.imageSmoothingEnabled = false; ctx.drawImage(mo, 820 - mo.width, 60 - mo.height, mo.width * 2, mo.height * 2); ctx.restore(); }
    else { ctx.fillStyle = '#efe6c8'; circle(820, 60, 18); ctx.fill(); ctx.fillStyle = '#d8ccaa'; ctx.fillRect(812, 52, 6, 4); ctx.fillRect(824, 64, 4, 4); } }""", 'moon')
s = swap(s, """function pxCloud(x, y, s) {
  ctx.fillStyle = 'rgba(255,255,255,0.85)';""", """function pxCloud(x, y, s) {
  { const cl = bgImg('fx/cloud'); if (cl) { const w = Math.round(cl.width * 2 * s / 2) * 2, h = Math.round(cl.height * 2 * s / 2) * 2; ctx.save(); ctx.imageSmoothingEnabled = false; ctx.globalAlpha *= 0.92; ctx.drawImage(cl, x - w / 2, y - h + 10, w, h); ctx.restore(); return; } }
  ctx.fillStyle = 'rgba(255,255,255,0.85)';""", 'clouds')
s = swap(s, """    if (ph < 0.15) { ctx.fillStyle = 'rgba(255,240,200,0.8)'; ctx.fillRect(x - 1, y + 80 * (1 - ph / 0.15), 2, 10); continue; }
    const al = inten * Math.min(1, (1 - ph) * 1.6);""", """    if (ph < 0.15) { ctx.fillStyle = 'rgba(255,240,200,0.8)'; ctx.fillRect(x - 1, y + 80 * (1 - ph / 0.15), 2, 10); continue; }
    const al = inten * Math.min(1, (1 - ph) * 1.6);
    { const fw = bgImg('fx/firework');   // the PixelLab burst (Version 52), grown and faded, a different colour each time
      if (fw) {
        const k = Math.min(1, 0.35 + ph * 1.1), w = Math.round(fw.width * 2 * k / 2) * 2, hh = Math.round(fw.height * 2 * k / 2) * 2, dy = ph * ph * 30;
        ctx.save(); ctx.imageSmoothingEnabled = false; ctx.globalAlpha = al; ctx.filter = 'hue-rotate(' + [0, 60, 180, 100, 270][seed % 5] + 'deg)';
        ctx.drawImage(fw, Math.round((x - w / 2) / 2) * 2, Math.round((y + dy - hh / 2) / 2) * 2, w, hh); ctx.restore(); continue;
      } }""", 'fireworks')

# preload with the rest of the art
s = swap(s, '"fx/bush", "fx/koala", ', '"fx/boilie", "fx/bush", "fx/cloud", "fx/firewave", "fx/firework", "fx/float", "fx/koala", "fx/moon", "fx/picker", "fx/spod", "fx/transmitter", "fx/wave", ', 'preload list')

open(PAGE, 'w', encoding='utf-8').write(s)
print('v52_build: web/index.html updated')
