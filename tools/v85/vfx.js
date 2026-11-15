// ================================================================== Version 85: hand-drawn small effects
// The little things the code used to draw as plain circles and polygons are pixel art now, on the same 2-unit grid as
// every other effect sheet (art by tools/v85/vfx_art.py; the puff and the flame from PixelLab's effects tool, in Tim's
// My effects as "Carp Diem smoke puff" and "Carp Diem flame lick"):
// - smoke puffs (exhausts, plaster dust, the powder, steam): a cartoon puff that billows and breaks up, in two sizes;
//   the biggest use the poof recoloured to the same greys; all drawn a little see-through, as the old ones were
// - kicked-up dust: the same puff in sandy browns
// - flames: a flame tongue that flares and dies
// - sparkles: a four-point star that pops and shrinks
// - hearts, water drops and the sleep Zs
// - debris and glass: chunky outlined bits in their own colour that tumble a quarter turn at a time
// Everything still moves as before (the particle code is unchanged); only the drawing is new. Until a sheet has
// loaded, the old drawing stands in.
/*FX_LINES*/
for (const k of ['puff', 'puff_s', 'poofw', 'sand', 'sand_s', 'lick', 'twinkle', 'heart', 'drop', 'drop_s', 'zz']) fxImg(k);

// a frame of sheet k picked by how far through its life the particle is (0..1); the last frame is left out when it's blank
function v85Frame(k, kk, x, y, flip, last) {
  const m = FX[k]; if (!m) return false;
  const n = last || m.n; return drawFxFrame(k, Math.min(n - 1, Math.max(0, Math.floor(kk * n))), x, y, flip || 1);
}

// debris: a chunk s sheet pixels long in colour col, four tumbling poses, lit on top and outlined; cached per colour
const v85Chunks = new Map();
function v85Chunk(col, s) {
  const key = col + '|' + s; let c = v85Chunks.get(key); if (c) return c;
  if (v85Chunks.size > 160) v85Chunks.clear();
  const h = Math.max(2, Math.round(s * 0.6)), cell = s + 2;
  c = document.createElement('canvas'); c.width = cell * 4; c.height = cell; const g = c.getContext('2d');
  const shapes = [[s, h, 0], [h, s, 0], [s, h, 1], [Math.max(2, Math.round(s * 0.8)), Math.max(2, Math.round(s * 0.8)), 1]];   // w, h, cut corners
  shapes.forEach(([w, hh, cut], i) => {
    const ox = i * cell + ((cell - w) >> 1), oy = (cell - hh) >> 1;
    const body = (x0, y0, w0, h0) => { g.fillRect(x0, y0, w0, h0); };
    const shape = (pad) => {   // the chunk grown by pad pixels, with its corners cut when asked
      for (let y = -pad; y < hh + pad; y++) for (let x = -pad; x < w + pad; x++) {
        const cx = x < 0 || x >= w, cy = y < 0 || y >= hh;
        if (cx && cy) continue;
        if (cut && w > 2 && hh > 2 && (x <= 0 || x >= w - 1) && (y <= 0 || y >= hh - 1) && !(pad && (cx || cy))) continue;
        body(ox + x, oy + y, 1, 1);
      }
    };
    g.fillStyle = OUT; shape(1);
    g.fillStyle = col; shape(0);
    g.globalCompositeOperation = 'source-atop';
    g.fillStyle = 'rgba(255,255,255,0.38)'; g.fillRect(ox, oy, w, 1);   // lit top
    g.fillStyle = 'rgba(0,0,0,0.3)'; g.fillRect(ox, oy + hh - 1, w, 1); g.fillRect(ox + w - 1, oy, 1, hh);   // shade
    g.globalCompositeOperation = 'source-over';
  });
  c.cell = cell; v85Chunks.set(key, c); return c;
}

// draws particle p at screen point (x, y), k = 0..1 through its life; true when it did
function v85Part(p, x, y, k) {
  switch (p.k) {
    case 'puff': case 'dust': {   // see-through as the old ones were (the big ones most), so a cloud of them doesn't hide the fight
      const sh = p.k === 'dust' ? (p.r >= 9 ? 'sand' : 'sand_s') : p.r >= 20 ? 'poofw' : p.r >= 7 ? 'puff' : 'puff_s';
      if (!fxImg(sh)) return false;
      ctx.globalAlpha = p.k === 'puff' && p.r >= 9 ? 0.5 : 0.8; const ok = v85Frame(sh, k, x, y, p.vx < 0 ? -1 : 1, sh === 'poofw' ? 9 : 7); ctx.globalAlpha = 1; return ok;
    }
    case 'flame': return v85Frame('lick', k, x, y, p.vx < 0 ? -1 : 1, 7);
    case 'sparkle': return v85Frame('twinkle', k, x, y, 1);
    case 'drop': return drawFxFrame(p.r >= 4.5 ? 'drop' : 'drop_s', 0, x, y, 1);
    case 'heart': { if (!fxImg('heart')) return false; ctx.globalAlpha = Math.max(0, 1 - k); const ok = drawFxFrame('heart', 0, x, y, 1); ctx.globalAlpha = 1; return ok; }
    case 'z': { if (!fxImg('zz')) return false; ctx.globalAlpha = Math.max(0, 1 - k); const ok = drawFxFrame('zz', Math.min(2, Math.floor(k * 3)), x, y, 1); ctx.globalAlpha = 1; return ok; }
    case 'debris': {
      if (/^rgba/.test(p.col || '')) return false;   // see-through flecks (the wind) keep their old look
      const s = Math.max(2, Math.min(10, Math.round(p.r))), c = v85Chunk(p.col || '#888888', s);
      const f = ((Math.floor((p.rot || 0) / (Math.PI / 2)) % 4) + 4) % 4, cell = c.cell;
      ctx.save(); ctx.imageSmoothingEnabled = false; ctx.globalAlpha = 1 - Math.max(0, k - 0.7) / 0.3;
      ctx.drawImage(c, f * cell, 0, cell, cell, Math.round(x / 2) * 2 - cell, Math.round(y / 2) * 2 - cell, cell * 2, cell * 2);
      ctx.restore(); return true;
    }
  }
  return false;
}
