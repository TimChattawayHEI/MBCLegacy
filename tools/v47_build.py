"""Version 47: easier running on a phone.

Patches web/index.html in place (run from the repo root, after tools/v45_build.py):  python3 tools/v47_build.py
Safe to run again.

Before, running on the touch stick needed a double flick (out, back, out again within 0.4s), which was hard to hit
in a fight. Now holding the stick right out to the side breaks into a run after a moment (0.35s), so short pushes
still walk; the double flick still runs straight away. A RUNNING setting in the pause menu can make any full push run. A ring fills round the stick's knob while it builds up, and
the knob turns orange when running (on the portrait pad as well).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, 'web', 'index.html')


def swap(s, old, new, label):
    if new in s:
        return s
    if s.count(old) != 1:
        sys.exit(f'v47_build: could not find the {label} (found {s.count(old)} matches)')
    return s.replace(old, new)


s = open(PAGE, encoding='utf-8').read()

s = swap(s, """const SR = { out: false, backT: -9, dir: 0, on: false, at: -1 };
function stickRun() {
  const v = stickVec(); if (!v) { SR.on = false; SR.out = false; return false; }
  if (SR.at === time) return SR.on; SR.at = time;
  const k = Math.abs(v.dx) / v.R, dir = Math.sign(v.dx) || SR.dir;
  if (k > 0.85 && !SR.out) { if (time - SR.backT < 0.4 && dir === SR.dir) SR.on = true; SR.out = true; SR.dir = dir; }
  else if (k < 0.45 && SR.out) { SR.out = false; SR.backT = time; }
  if (SR.on && (k < 0.55 || dir !== SR.dir)) SR.on = false;
  return SR.on;
}""", """// running on the touch stick: hold it right out to the side and he breaks into a run after a moment (Version 47),
// or flick it out, back and out again for a run straight away
const runHold = () => settings.run === 'push' ? 0.06 : 0.35;
const SR = { out: false, backT: -9, dir: 0, on: false, at: -1, hold: 0, hdir: 0 };
function stickRun() {
  const v = stickVec(); if (!v) { SR.on = false; SR.out = false; SR.hold = 0; return false; }
  if (SR.at === time) return SR.on;
  const dt = SR.at < 0 ? 0 : Math.min(0.1, Math.max(0, time - SR.at)); SR.at = time;
  const k = Math.abs(v.dx) / v.R, mag = Math.hypot(v.dx, v.dy) / v.R, dir = Math.sign(v.dx) || SR.dir;
  if (k > 0.85 && !SR.out) { if (time - SR.backT < 0.4 && dir === SR.dir) SR.on = true; SR.out = true; SR.dir = dir; }
  else if (k < 0.45 && SR.out) { SR.out = false; SR.backT = time; }
  if (mag > 0.78 && k > 0.6) {
    if (dir !== SR.hdir) { SR.hdir = dir; SR.hold = 0; }
    SR.hold += dt;
    if (SR.hold >= runHold() && !SR.on) { SR.on = true; SR.dir = dir; }
  } else SR.hold = 0;
  if (SR.on && (k < 0.55 || dir !== SR.dir)) SR.on = false;
  return SR.on;
}
// how far the hold-to-run has built up, 0 to 1, for the ring round the knob
function stickRunCharge() { return SR.on ? 1 : Math.min(1, SR.hold / runHold()); }""", 'stick run')

s = swap(s, """  ctx.fillStyle = stickRun() ? 'rgba(242,162,58,0.8)' : 'rgba(239,230,210,0.6)'; circle(kx, ky, 28); ctx.fill();""",
         """  ctx.fillStyle = stickRun() ? 'rgba(242,162,58,0.8)' : 'rgba(239,230,210,0.6)'; circle(kx, ky, 28); ctx.fill();
  { const ch = st ? stickRunCharge() : 0; if (ch > 0.05 && ch < 1) { ctx.strokeStyle = 'rgba(242,162,58,0.9)'; ctx.lineWidth = 5; ctx.beginPath(); ctx.arc(kx, ky, 34, -Math.PI / 2, -Math.PI / 2 + ch * Math.PI * 2); ctx.stroke(); } }""",
         'run charge ring')

s = swap(s, """  if (padSpecialEl) padSpecialEl.classList.toggle('ready', mode === 'play' && !!player && player.meter >= 100);""",
         """  if (padSpecialEl) padSpecialEl.classList.toggle('ready', mode === 'play' && !!player && player.meter >= 100);
  if (padKnobEl && padOn()) padKnobEl.classList.toggle('run', mode === 'play' && stickRun());""", 'pad knob run colour')
s = swap(s, """const padSpecialEl = document.getElementById('padSpecial');""",
         """const padSpecialEl = document.getElementById('padSpecial'), padKnobEl = document.getElementById('padKnob');""", 'pad knob element')
s = swap(s, """.knob{position:absolute;left:30%;top:30%;width:40%;height:40%;border-radius:50%;background:var(--ink);box-shadow:0 4px 0 rgba(0,0,0,.35);opacity:.9;pointer-events:none}""",
         """.knob{position:absolute;left:30%;top:30%;width:40%;height:40%;border-radius:50%;background:var(--ink);box-shadow:0 4px 0 rgba(0,0,0,.35);opacity:.9;pointer-events:none}
.knob.run{background:#f2a23a}""", 'pad knob style')

s = swap(s, """<p class="padnote">Flick the stick twice to run.""", """<p class="padnote">Hold the stick right out to run.""", 'pad note')

# a RUNNING choice in the pause settings: hold the stick out (default) or run on any full push (Version 47)
s = swap(s, """    { id: 'lefty', label: 'STICK', val: settings.lefty ? 'ON THE RIGHT' : 'ON THE LEFT', touch: true },""",
         """    { id: 'lefty', label: 'STICK', val: settings.lefty ? 'ON THE RIGHT' : 'ON THE LEFT', touch: true },
    { id: 'run', label: 'RUNNING', val: settings.run === 'push' ? 'ANY FULL PUSH' : 'HOLD THE STICK OUT', touch: true },""", 'run settings row')
s = swap(s, """  else if (id === 'lefty') { settings.lefty = !settings.lefty; applyTouchLayout(); }""",
         """  else if (id === 'lefty') { settings.lefty = !settings.lefty; applyTouchLayout(); }
  else if (id === 'run') settings.run = settings.run === 'push' ? 'hold' : 'push';""", 'run settings toggle')
s = s.replace("rows.forEach((r, i) => { r.x = 452; r.y = 112 + i * 34; r.w = 426; r.h = 30; r.vx = r.x + 196; });",
              "rows.forEach((r, i) => { r.x = 452; r.y = 110 + i * 32; r.w = 426; r.h = 28; r.vx = r.x + 196; });")

open(PAGE, 'w', encoding='utf-8').write(s)
print('v47_build: web/index.html updated')
