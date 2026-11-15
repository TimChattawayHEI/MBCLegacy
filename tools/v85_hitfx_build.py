"""Version 85: hits that land harder. python3 tools/v85_hitfx_build.py (re-runnable; patches web/index.html in place).
Code: tools/v85/hitfx.js, between `// V85 hitfx start` and `// V85 hitfx end`, after Version 81. Art: tools/v85/hitfx_art.py.
Hooks: applyHit (weapon thwack, sweat, combo enders), physics (the dust ring on a hard landing), startSpecial (the
burst and the dim), drawWorld (the dim under the fighters; the burst and speed lines behind their owner), drawPart
(skips those two), drawLad and sprTint (the white-then-colour flash)."""
import os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); PAGE = os.path.join(ROOT, 'web', 'index.html')
subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'v85', 'hitfx_art.py')], check=True)
s = open(PAGE, encoding='utf-8').read()
start, end = '// V85 hitfx start', '// V85 hitfx end'
if start in s: a = s.index(start); b = s.index(end) + len(end) + 1; s = s[:a] + s[b:]
anchor = '// V81 js end\n'
assert s.count(anchor) == 1
s = s.replace(anchor, anchor + start + '\n' + open(os.path.join(ROOT, 'tools', 'v85', 'hitfx.js'), encoding='utf-8').read().rstrip('\n') + '\n' + end + '\n')
SWAPS = [
    ("  if (!v80Spark(a, t.x - dir * t.half * 0.4, t.y, t.z + hz, big, dir)) spark(t.x - dir * t.half * 0.4, t.y, t.z + hz, big);   // Version 80\n",
     "  if (!v85HitFx(a, t, k, dir, big, hz) && !v80Spark(a, t.x - dir * t.half * 0.4, t.y, t.z + hz, big, dir)) spark(t.x - dir * t.half * 0.4, t.y, t.z + hz, big);   // Version 80, 85\n"),
    ("    if (e.z <= 0) { if (e.vz < -260 && (e.state === 'down'",
     "    if (e.z <= 0) { v85Land(e); if (e.vz < -260 && (e.state === 'down'"),
    ("function startSpecial(p) {\n  runStat('specials', p.def.id);   // Version 71\n",
     "function startSpecial(p) {\n  runStat('specials', p.def.id);   // Version 71\n  v85SpecialStart(p);   // Version 85\n"),
    ("  drawDeniseFloor(); drawBossFloor();\n", "  drawDeniseFloor(); drawBossFloor();\n  v85Dim();   // Version 85\n"),
    ("  ladFxDraw(list);\n", "  ladFxDraw(list);\n  v85FxList(list);   // Version 85\n"),
    ("  if (p.k === 'v81fx' || p.k === 'v81flash') { v81DrawPart(p); return; }   // Version 81\n",
     "  if (p.k === 'v85burst' || p.k === 'v85speed') return;   // Version 85: drawn behind their owner (v85FxList)\n  if (p.k === 'v81fx' || p.k === 'v81flash') { v81DrawPart(p); return; }   // Version 81\n"),
    ("  const tint = e.flash > 0 ? 'white' :",
     "  const tint = e.flash > 0 ? (e.v85col && time - e.v85at > 0.06 && time - e.v85at < 0.24 ? e.v85col : 'white') :   // Version 85: white, then the lad's colour\n   "),
    ("x.globalCompositeOperation = 'source-atop'; x.fillStyle = SPR_TINT[kind];",
     "x.globalCompositeOperation = 'source-atop'; x.fillStyle = SPR_TINT[kind] || kind;"),
]
for old, new in SWAPS:
    if new in s: continue
    assert s.count(old) == 1, old[:60]
    s = s.replace(old, new)
open(PAGE, 'w', encoding='utf-8').write(s); print('v85 hitfx: patched')
