// ================================================================== Version 62: your own button layout
// Pause > Settings > BUTTON LAYOUT (on a touch screen). Drag the stick and each button where your thumbs sit, tap one
// and use - / + to size it, MIRROR swaps sides, RESET puts them back. Kept on this phone (settings.tl): positions as
// you left them, with the button size and side they were made at, so the BUTTON SIZE and STICK settings still work on
// top (bigger or smaller round the same spots, or mirrored). The stick still works anywhere on its half of the screen;
// this is where it sits.
// called by applyTouchLayout (hoisted, so it's there at start-up): true if your layout was used
function tlApply() {
  const t = settings.tl; if (!t || !t.stick) return false;
  const kNow = { s: 0.85, m: 1, l: 1.18 }[settings.pad] || 1, f = kNow / (t.k || 1), mir = !!settings.lefty !== !!t.L;
  const put = (o, v) => { if (!v) return; o.x = clamp(mir ? W - v.x : v.x, 20, W - 20); o.y = clamp(v.y, 60, H - 20); o.r = v.r * f; };
  put(STICK, t.stick); BTN.forEach(b => put(b, t[b.id]));
  return true;
}
const TLE = { sel: 'punch', drag: null, back: 'pause', dirty: false };
const tleCtl = () => [Object.assign(STICK, { id: 'stick', label: 'STICK' })].concat(BTN);
const tleR0 = id => id === 'stick' ? STICK0.r : (BTN0.find(b => b.id === id) || { r: 40 }).r;
function tleBar() {
  const items = [{ id: 'minus', label: '−', w: 56 }, { id: 'plus', label: '+', w: 56 }, { id: 'mirror', label: 'MIRROR', w: 112 }, { id: 'reset', label: 'RESET', w: 112 }, { id: 'done', label: 'DONE', w: 112 }];
  let x = W / 2 - (items.reduce((t, b) => t + b.w, 0) + 12 * (items.length - 1)) / 2;
  for (const b of items) { b.x = x; b.y = 86; b.h = 44; x += b.w + 12; }
  return items;
}
function tleOpen() {
  if (mode !== 'pause') return;
  TLE.back = 'pause'; TLE.sel = 'punch'; TLE.drag = null; TLE.dirty = false;
  mode = 'tledit'; modeT = 0; held.clear(); pointers.clear(); sfx('page');
}
function tleSave() {
  const k = { s: 0.85, m: 1, l: 1.18 }[settings.pad] || 1, t = { k, L: !!settings.lefty, stick: { x: STICK.x, y: STICK.y, r: STICK.r } };
  BTN.forEach(b => { t[b.id] = { x: b.x, y: b.y, r: b.r }; });
  settings.tl = t; saveSettings();
}
function tleClose() { if (TLE.dirty) tleSave(); mode = 'pause'; modeT = 0; pauseTab = 'settings'; pauseFocus = 'right'; pointers.clear(); sfx('page'); }
function tleAct(id) {
  const c = tleCtl().find(o => o.id === TLE.sel);
  if (id === 'minus' || id === 'plus') { if (!c) return; const r0 = tleR0(c.id); c.r = clamp(c.r * (id === 'plus' ? 1.12 : 1 / 1.12), r0 * 0.6, r0 * 1.8); TLE.dirty = true; sfx('swing'); }
  else if (id === 'mirror') { for (const o of tleCtl()) o.x = W - o.x; settings.lefty = !settings.lefty; TLE.dirty = true; saveSettings(); sfx('swing'); }
  else if (id === 'reset') { delete settings.tl; saveSettings(); TLE.dirty = false; applyTouchLayout(); sfx('page'); }
  else if (id === 'done') tleClose();
}
function tleKeep(o) { o.x = clamp(o.x, o.r + 4, W - o.r - 4); o.y = clamp(o.y, 140 + o.r, H - o.r - 4); }
canvas.addEventListener('pointerdown', e => {
  if (mode !== 'tledit' || modeT < 0.15) return;
  const p = toLogical(e);
  for (const b of tleBar()) if (p.x > b.x && p.x < b.x + b.w && p.y > b.y && p.y < b.y + b.h) { tleAct(b.id); return; }
  let best = null, bd = 1e9;
  for (const o of tleCtl()) { const d = Math.hypot(p.x - o.x, p.y - o.y); if (d < o.r + 18 && d < bd) { best = o; bd = d; } }
  if (best) { TLE.sel = best.id; TLE.drag = { id: e.pointerId, o: best, dx: best.x - p.x, dy: best.y - p.y }; sfx('swing'); }
});
canvas.addEventListener('pointermove', e => {
  if (mode !== 'tledit' || !TLE.drag || TLE.drag.id !== e.pointerId) return;
  const p = toLogical(e), o = TLE.drag.o; o.x = p.x + TLE.drag.dx; o.y = p.y + TLE.drag.dy; tleKeep(o); TLE.dirty = true;
});
['pointerup', 'pointercancel'].forEach(t => canvas.addEventListener(t, e => { if (TLE.drag && TLE.drag.id === e.pointerId) TLE.drag = null; }));
function tleUpdate() {
  if (modeT < 0.15) return;
  if (pressed.has('escape') || pressed.has('pause')) { tleClose(); return; }
  // keys too, for testing on a computer: Tab picks, arrows move, - and = size
  const ids = tleCtl().map(o => o.id), c = tleCtl().find(o => o.id === TLE.sel);
  if (pressed.has('punch')) { TLE.sel = ids[(ids.indexOf(TLE.sel) + 1) % ids.length]; sfx('swing'); }
  if (c) { const mv = (dx, dy) => { c.x += dx; c.y += dy; tleKeep(c); TLE.dirty = true; };
    if (held.has('left')) mv(-6, 0); if (held.has('right')) mv(6, 0); if (held.has('up')) mv(0, -6); if (held.has('down')) mv(0, 6); }
}
function tleDraw() {
  ctx.setTransform(scale, 0, 0, scale, 0, 0); ctx.globalAlpha = 1;
  ctx.fillStyle = 'rgba(10,14,16,0.72)'; ctx.fillRect(0, 0, W, H);
  ctx.textBaseline = 'middle'; ctx.textAlign = 'center';
  textOut('BUTTON LAYOUT', W / 2, 30, '30px ' + DISPLAY, '#f2a23a', OUT, 6, 'center');
  ctx.font = '600 13px ' + BODY; ctx.fillStyle = '#e9dcc0';
  ctx.fillText('Drag them where your thumbs sit. Tap one, then − / + for its size.', W / 2, 62);
  tleBar().forEach(b => {
    const dis = (b.id === 'minus' || b.id === 'plus') && !TLE.sel;
    rrect(b.x, b.y, b.w, b.h, 10); ctx.fillStyle = b.id === 'done' ? '#7fe07a' : 'rgba(24,36,42,0.95)'; ctx.fill();
    ctx.strokeStyle = b.id === 'done' ? '#7fe07a' : '#f2a23a'; ctx.lineWidth = 2; ctx.stroke();
    ctx.font = (b.w < 60 ? 26 : 16) + 'px ' + DISPLAY; ctx.fillStyle = b.id === 'done' ? '#10200f' : dis ? '#56636a' : '#efe6d2'; ctx.fillText(b.label, b.x + b.w / 2, b.y + b.h / 2 + 1);
  });
  // the stick's half of the screen, faintly
  ctx.fillStyle = 'rgba(242,162,58,0.05)'; if (STICK.x < W / 2) ctx.fillRect(0, 140, W / 2, H - 140); else ctx.fillRect(W / 2, 140, W / 2, H - 140);
  ctx.font = '600 11px ' + BODY; ctx.fillStyle = '#93a3a1'; ctx.fillText('The stick works anywhere on this half. This is where it sits.', STICK.x < W / 2 ? W / 4 : W * 3 / 4, 156);
  for (const o of tleCtl()) {
    const on = o.id === TLE.sel;
    ctx.fillStyle = o.id === 'stick' ? 'rgba(15,22,25,0.55)' : 'rgba(15,22,25,0.7)'; circle(o.x, o.y, o.r); ctx.fill();
    ctx.strokeStyle = on ? '#ffd23f' : 'rgba(239,230,210,0.6)'; ctx.lineWidth = on ? 4 : 3; ctx.stroke();
    if (o.id === 'stick') { ctx.fillStyle = 'rgba(239,230,210,0.6)'; circle(o.x, o.y, 28 * o.r / STICK0.r); ctx.fill(); }
    ctx.fillStyle = '#efe6d2'; ctx.font = (o.id === 'punch' ? 18 : o.id === 'stick' ? 11 : 10) + 'px ' + DISPLAY; ctx.fillText(o.id === 'stick' ? 'MOVE' : o.label, o.x, o.id === 'stick' ? o.y + o.r + 12 : o.y + 1);
  }
}
