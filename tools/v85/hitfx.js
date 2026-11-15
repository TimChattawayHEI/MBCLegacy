// ================================================================== Version 85: hits that land harder
// Art from PixelLab's VFX workbench (in Tim's My effects as "Carp Diem ground slam", "Carp Diem sweat spray",
// "Carp Diem weapon thwack" and "Tim special burst"; the burst is recoloured for every lad by tools/v85/hitfx_art.py).
// - a weapon hit throws a chunky orange thwack with grit instead of the lad's spark
// - a head shot flicks sweat off the way the hit travels
// - a combo ender: the victim flashes white then the lad's colour, a short sharp shake, speed lines behind the knockback
// - a body hitting the floor hard: a dust ring and puffs rolling out both sides
// - a special: a burst in the lad's colour behind him, and the stage dims for a moment so he stands out
FX.slam = { fw: 124, fh: 44, n: 8, cols: 3, ax: 62, ay: 32, fps: 16, loop: false };
FX.sweat = { fw: 56, fh: 44, n: 5, cols: 3, ax: 10, ay: 24, fps: 16, loop: false };
FX.thwack = { fw: 80, fh: 72, n: 5, cols: 3, ax: 30, ay: 36, fps: 16, loop: false };
for (const k of ['slam', 'sweat', 'thwack']) fxImg(k);
for (const id in FX_COL) { FX[id + '_burst'] = { fw: 128, fh: 128, n: 10, cols: 4, ax: 64, ay: 64, fps: 16, loop: false }; fxImg(id + '_burst'); }

const V85_NOBODY = { goose: 1, swan: 1, espace: 1 };   // no sweat or dust ring for birds and cars
let v85DimAt = -9;
function v85Rgba(h, a) { const c = hexRgb(h); return 'rgba(' + c[0] + ',' + c[1] + ',' + c[2] + ',' + a + ')'; }

// called from applyHit before the spark; true when it drew the hit itself (a weapon's thwack)
function v85HitFx(a, t, k, dir, big, hz) {
  if (!t || t.car || t.fish || V85_NOBODY[t.kind]) return false;
  const hx = t.x - dir * t.half * 0.4, f = dir < 0 ? -1 : 1;
  // a head shot (the next hurt row is the head one): sweat flies off the way the hit goes
  const n = t === player || (t.def && t.def.id && typeof LAD_FRAMES !== 'undefined' && LAD_FRAMES[t.def.id]) ? (t.hurtN || 0) % 2 === 1 : ((t.boss ? t._bh : t._hn) || 0) % 2 === 0;
  if ((n && !k.kd) || big) fxPlay('sweat', t.x + dir * 8, t.y + 1, t.z + hz + 30, f);   // off the back of the head
  // a combo ender, knockdown or finisher from a lad: white, then his colour; a sharp shake; speed lines behind
  if (big && fxLad(a) && t !== player) {
    t.v85col = v85Rgba(FX_COL[a.def.id] || '#ffffff', 0.62); t.v85at = time; t.flash = Math.max(t.flash || 0, 0.22);
    if (!reduceMotion && settings.shake !== 'less') shake = Math.max(shake, 7);
    parts.push({ k: 'v85speed', who: t, dir: f, col: FX_COL[a.def.id] || '#ffffff', x: t.x, y: t.y, z: 0, t: 0, life: 0.3 });
  }
  if (k.weapon) { fxPlay('thwack', hx, t.y, t.z + hz, f); return true; }
  return false;
}
// called from physics the frame something lands, before its fall speed is cleared
function v85Land(e) {
  if (e.vz > -260 || !(e.state === 'down' || e.state === 'thrown' || e.state === 'dead')) return;
  if (e.car || e.fish || V85_NOBODY[e.kind]) return;
  fxPlay('slam', e.x, e.y + 1, 0, e.vx < 0 ? -1 : 1);
  if (e.boss || (e.def && e.def.scale > 1.15)) addShake(3);
}
// called from startSpecial: a burst in his colour behind him, and the stage dims
function v85SpecialStart(p) {
  if (!fxLad(p) || !FX[p.def.id + '_burst']) return;
  parts.push({ k: 'v85burst', fx: p.def.id + '_burst', who: p, x: p.x, y: p.y, z: 0, t: 0, life: FX[p.def.id + '_burst'].n / 16 });
  v85DimAt = time;
}
// after the floor and before anyone stands on it: the dim, so the fighters stay bright
function v85Dim() {
  const t = time - v85DimAt; if (t < 0 || t > 0.85) return;
  const a = t < 0.08 ? t / 0.08 : t < 0.45 ? 1 : 1 - (t - 0.45) / 0.4;
  ctx.save(); ctx.fillStyle = 'rgba(6,8,18,' + (0.42 * a).toFixed(3) + ')'; ctx.fillRect(-20, -20, W + 40, H + 40); ctx.restore();
}
// the burst and the speed lines sit just behind their owner in the depth sort
function v85FxList(list) {
  for (const p of parts) {
    if (p.k !== 'v85burst' && p.k !== 'v85speed') continue;
    const o = p.who || p; list.push({ y: o.y - 0.5, f: () => v85DrawOwned(p) });
  }
}
function v85DrawOwned(p) {
  const o = p.who || p;
  if (p.k === 'v85burst') {
    const m = FX[p.fx]; drawFxFrame(p.fx, Math.min(m.n - 1, Math.floor(p.t * m.fps)), o.x - cam.x, o.y - (o.z || 0) - 62, 1);
    return;
  }
  // speed lines: streaks trailing behind the body as it flies, white near it, his colour further back
  if (reduceMotion) return;
  const k = p.t / p.life, back = -Math.sign(o.vx || p.dir) || -p.dir, x0 = o.x - cam.x + back * 26, y0 = o.y - (o.z || 0);
  ctx.save(); ctx.globalAlpha = 1 - k;
  for (let i = 0; i < 5; i++) {
    const h = 26 + i * 18 + ((i * 7) % 5) * 2, len = 34 + ((i * 13) % 4) * 14 + k * 30;
    const xa = Math.round((x0 + back * (i % 2) * 6) / 2) * 2, ya = Math.round((y0 - h) / 2) * 2;
    ctx.fillStyle = '#ffffff'; ctx.fillRect(back > 0 ? xa : xa - len * 0.4, ya, len * 0.4, 2);
    ctx.fillStyle = p.col; ctx.fillRect(back > 0 ? xa + len * 0.4 : xa - len, ya, len * 0.6, 2);
  }
  ctx.restore();
}
