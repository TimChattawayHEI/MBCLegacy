"""Version 65: Tim's to-do list of 30 October (ToDo.MD). Patches web/index.html in place (run from the repo root):
python3 tools/v65_build.py. Safe to run again; it re-runs v64_build.py first.

- The super fills about three times as fast: more for each hit, kills and food top it up too.
- No more back kick. Its button (U, V, the BACK touch button) is the special now; with a weapon in hand and the
  special not ready, it throws the weapon instead (J+K still throws too).
- Seb's headbutt is spring-loaded: he arches back, then snaps forward into it.
"""
import os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, 'web', 'index.html')
read = lambda p: open(p, encoding='utf-8').read()


def swap(s, old, new, label):
    if new in s:
        return s
    if s.count(old) != 1:
        sys.exit(f'v65_build: could not find the {label} (found {s.count(old)} matches)')
    return s.replace(old, new)


subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'v64_build.py')], check=True)
s = read(PAGE)

# ---------------------------------------------------------------- the super fills faster
s = swap(s, "const METER = { hit: 0.72, extra: 0.3, knee: 0.65, hurt: 0.5, respawn: 50 };",
         "const METER = { hit: 1.6, extra: 0.45, knee: 1.4, hurt: 1.2, respawn: 50, ko: 4, food: 20 };   // Version 65: about three times as quick", 'meter rates')
s = swap(s, "function noteKO(f) {\n  if (!S) return;\n",
         "function noteKO(f) {\n  if (!S) return;\n  if (player && !f.npc) gainMeter(player, METER.ko);   // Version 65: every knockout tops the super up\n", 'meter on KO')
s = swap(s, "p.hp = Math.min(p.maxHp, p.hp + f.heal); popWord(p.x, p.y, 140, f.word, false);",
         "p.hp = Math.min(p.maxHp, p.hp + f.heal); gainMeter(p, METER.food); popWord(p.x, p.y, 140, f.word, false);", 'meter from food')

# ---------------------------------------------------------------- the back kick goes; its button is the special
s = swap(s, "KeyU: 'back', KeyV: 'back',", "KeyU: 'special', KeyV: 'special',", 'back keys')
s = swap(s, "  { id: 'back', x: 752, y: 392, r: 30, label: 'BACK' },\n  { id: 'special', x: 862, y: 334, r: 34, label: 'SPECIAL' },",
         "  { id: 'special', x: 752, y: 392, r: 34, label: 'SPECIAL' },   // Version 65: where BACK was (the back kick is gone)", 'touch buttons')
s = swap(s, '      <button class="pb back" type="button" data-act="back">BACK</button>\n', '      <!-- Version 65: no BACK button, the special has its place -->\n', 'pad back button')
s = swap(s, ".pb.special{left:27%;top:0;width:34%;height:34%;", ".pb.special{left:0;top:28%;width:34%;height:34%;", 'pad special place')
s = swap(s, "  const chord = pressed.has('back') || (pressed.has('punch') && pressed.has('jump'));",
         "  const chord = pressed.has('punch') && pressed.has('jump');", 'throw chord')
s = swap(s, "      if (chord) { if (p.weapon) throwWeapon(p); else startBack(p); break; }",
         "      if (chord && p.weapon) { throwWeapon(p); break; }   // Version 65: no back kick", 'chord back kick')
s = swap(s, "      if (pressed.has('punch') || pressed.has('back')) { if (p.weapon) throwWeapon(p); else startBack(p); break; }",
         "      if (pressed.has('punch') && p.weapon) { throwWeapon(p); break; }", 'squat back kick')
s = swap(s, "      if (p.combo === 1 && p.t < 0.07 && (pressed.has('jump') || pressed.has('back'))) { startBack(p); break; }\n", "      // Version 65: no back kick off the first jab\n", 'combo back kick')
# special pressed with a weapon and no special ready: throw the weapon instead of the NOT READY buzz
s = swap(s, "  if (pressed.has('special') && p.meter < 100 && p.state !== 'special' && meterNopeT <= 0) { meterNopeT = 0.5; sfx('nope'); }",
         "  if (pressed.has('special') && p.meter < 100 && p.weapon && (p.state === 'idle' || p.state === 'walk' || p.state === 'run')) throwWeapon(p);\n"
         "  else if (pressed.has('special') && p.meter < 100 && p.state !== 'special' && meterNopeT <= 0) { meterNopeT = 0.5; sfx('nope'); }", 'special throws weapon')
s = swap(s, "<div><kbd>J</kbd>+<kbd>K</kbd> back attack, throws your weapon</div>", "<div><kbd>J</kbd>+<kbd>K</kbd> or <kbd>U</kbd> throws your weapon</div>", 'help line')

# ---------------------------------------------------------------- Seb's spring-loaded headbutt
s = swap(s, "  seb: { name: 'HEADBUTT', hit: [0.28], end: 0.62, r: 124, lunge: 110, dmg: 19, word: 'BONK!' },",
         "  seb: { name: 'HEADBUTT', hit: [0.31], end: 0.64, r: 124, lunge: 230, lungeT: [0.24, 0.33], dmg: 19, word: 'BONK!', spring: true },   // Version 65: arch back, then snap", 'seb mini')
s = swap(s, "  if (m.lunge) p.vx = t > 0.16 && t < 0.3 ? p.miniFace * m.lunge : 0;",
         "  if (m.lunge) { const [a, b] = m.lungeT || [0.16, 0.3]; p.vx = t > a && t < b ? p.miniFace * m.lunge : 0; if (m.spring && t >= a && t - dt < a) sfx('swing'); }", 'mini lunge window')
s = swap(s, "      if (fr && rows && rows.mini) return ['mini', fr[Math.min(fr.length - 1, Math.floor(t / ((mm && mm.end) || 0.6) * fr.length))]];",
         "      if (fr && rows && rows.mini && mm && mm.spring) return ['mini', fr[Math.min(fr.length - 1, t < 0.24 ? 1 : t < 0.27 ? 5 : t < 0.4 ? 6 : t < 0.5 ? 4 : 2)]];   // Version 65: coil, snap, recover\n"
         "      if (fr && rows && rows.mini) return ['mini', fr[Math.min(fr.length - 1, Math.floor(t / ((mm && mm.end) || 0.6) * fr.length))]];", 'mini frames')
s = swap(s, "  if (st === 'dash') ctx.rotate(0.12);\n",
         "  if (st === 'dash') ctx.rotate(0.12);\n"
         "  if (st === 'mini' && e.def && MINI[e.def.id] && MINI[e.def.id].spring) {   // Version 65: lean back on the coil, snap the head through\n"
         "    const t = e.t || 0, coil = clamp(t / 0.22, 0, 1), ease = 1 - Math.pow(1 - coil, 2);\n"
         "    const a = t < 0.24 ? -0.44 * ease : t < 0.3 ? lerp(-0.44, 0.3, (t - 0.24) / 0.06) : t < 0.38 ? 0.3 : lerp(0.3, 0, clamp((t - 0.38) / 0.18, 0, 1));\n"
         "    ctx.rotate(a); if (t < 0.24) ctx.scale(1, 1 - 0.05 * ease);\n"
         "  }\n", 'seb lean')

# ---------------------------------------------------------------- the specials check: Sam's lights out hides the foes' chat too
s = swap(s, "  drawCine(); drawLids();\n  if (!pix) for (const b of bubbles) drawBubble(b);",
         "  drawCine(); drawLids();\n  if (!pix && !(S && S.lids > 0.5)) for (const b of bubbles) drawBubble(b);   // Version 65: nothing to see with Sam's eyes shut", 'sleepy bubbles')
s = swap(s, "  for (const b of bubbles) drawBubble(b);\n  ctx.globalAlpha = 1;\n}",
         "  if (!(S && S.lids > 0.5)) for (const b of bubbles) drawBubble(b);   // Version 65\n  ctx.globalAlpha = 1;\n}", 'sleepy bubbles (pixel pass)')


open(PAGE, 'w', encoding='utf-8').write(s)
print('v65_build: web/index.html updated')
