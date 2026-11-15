"""Version 85: the run back. python3 tools/v85_runback_build.py (re-runnable; patches web/index.html in place).
Art: python3 tools/v85/runback_art.py (web/bg/orp/run_*.png). Code: tools/v85/runback.js between `// V85 runback start`
and `// V85 runback end`, after the smashables. The stage goes on the route between the Blacksmiths and Atlantis.
Hooks, as the drive has them: start, tick (it moves the lad itself), the street behind, the obstacles and the coach in the
draw list, the clock, the points rows and the rank; and the select screen's line and picture."""
import os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); PAGE = os.path.join(ROOT, 'web', 'index.html')
subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'v85', 'runback_art.py')], check=True)
s = open(PAGE, encoding='utf-8').read()
start, end = '// V85 runback start', '// V85 runback end'
if start in s: a = s.index(start); b = s.index(end) + len(end) + 1; s = s[:a] + s[b:]
js = open(os.path.join(ROOT, 'tools', 'v85', 'runback.js'), encoding='utf-8').read()
anchor = '// V85 smash end\n'
assert s.count(anchor) == 1
s = s.replace(anchor, anchor + start + '\n' + js.rstrip('\n') + '\n' + end + '\n')
SWAPS = [
    ("function drawStageBg() {\n  if (orpBg()) return;",
     "function drawStageBg() {\n  if (ST.run) { runBg(); return; }   // Version 85: the run back\n  if (orpBg()) return;"),
    ("  if (ST.drive) { let own = false; try { own = driveTick(dt); } catch (e) { glitch('drive', e); } if (own) { updateParts(dt); updateBubbles(dt); updateWaves(dt); shake = Math.max(0, shake - dt * 30); return true; } }\n",
     "  if (ST.drive) { let own = false; try { own = driveTick(dt); } catch (e) { glitch('drive', e); } if (own) { updateParts(dt); updateBubbles(dt); updateWaves(dt); shake = Math.max(0, shake - dt * 30); return true; } }\n"
     "  if (ST.run) { let own = false; try { own = runTick(dt); } catch (e) { glitch('run', e); } if (own) { updateParts(dt); updateBubbles(dt); shake = Math.max(0, shake - dt * 30); return true; } }   // Version 85\n"),
    ("  if (ST.drive) driveDraw(list);\n", "  if (ST.drive) driveDraw(list);\n  if (ST.run) runDraw(list);   // Version 85\n"),
    ("if (ST && ST.drive && mode === 'play') drawDriveHud();", "if (ST && ST.drive && mode === 'play') drawDriveHud(); if (ST && ST.run && mode === 'play') runHud();"),
    ("  if (ST.drive) driveStart(); else setTimeout0(", "  if (ST.drive) driveStart(); else if (ST.run) runStart(); else setTimeout0("),
    ("  if (ST.drive) driveRows(add); else {", "  if (ST.drive) driveRows(add); else if (ST.run) runRows(add); else {"),
    ("function updateOrp(dt) {\n  if (!S || !ST || ST.era !== 2001) return;", "function updateOrp(dt) {\n  if (!S || !ST || ST.era !== 2001 || ST.run) return;"),
    ("function orpDrawFore() {\n  if (!ST || ST.era !== 2001 || !S) return;", "function orpDrawFore() {\n  if (!ST || ST.era !== 2001 || !S || ST.run) return;"),
    ("function stageRank() {\n  let p = 0;\n", "function stageRank() {\n  if (ST.run) return runRank();   // Version 85\n  let p = 0;\n"),
    ("orp_pub: 'Jeff, then Mick (and Sue)', orp_atlantis:", "orp_pub: 'Jeff, then Mick (and Sue)', orp_run: 'No boss. Make the coach.', orp_atlantis:"),
    ("orp_pub: 'orp/bar', orp_atlantis: 'orp/floor',", "orp_pub: 'orp/bar', orp_run: 'orp/front', orp_atlantis: 'orp/floor',"),
]
for old, new in SWAPS:
    if new in s: continue
    assert s.count(old) == 1, old[:80]
    s = s.replace(old, new)
open(PAGE, 'w', encoding='utf-8').write(s); print('v85 runback: patched')
