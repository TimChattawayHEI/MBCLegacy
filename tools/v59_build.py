"""Version 59: KEBAB SIEGE.

Patches web/index.html in place (run from the repo root, after tools/v56_build.py):  python3 tools/v59_build.py
Safe to run again; it re-runs v56_build.py first. The code is tools/v59/kebab.js, put in whole between
`// KB js start` and `// KB js end` (just after the pub's block, whose MINI_DEF and cabinet list it joins).

A horde fight on the real fight engine: a fixed screen in the kebab shop at 3am, the 2006 crowd coming in through the
door, wave after wave, one life. Ticket 50, they're on 44; every wave cleared they call the next number, and at yours
your kebab's up (full health and a bonus) and you get a new ticket. Knocked down by the door, they're thrown out.
After The Smoking Area on a run, and the seventh game in the Harvest Moon.
"""
import os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, 'web', 'index.html')
read = lambda p: open(p, encoding='utf-8').read()


def swap(s, old, new, label):
    if new in s:
        return s
    if s.count(old) != 1:
        sys.exit(f'v59_build: could not find the {label} (found {s.count(old)} matches)')
    return s.replace(old, new)


subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'v56_build.py')], check=True)
s = read(PAGE)

start, end = '// KB js start', '// KB js end'
block = start + '\n' + read(os.path.join(ROOT, 'tools', 'v59', 'kebab.js')).rstrip('\n') + '\n' + end + '\n'
if start in s:
    a = s.index(start); b = s.index(end) + len(end) + 1
    s = s[:a] + block + s[b:]
else:
    s = swap(s, "// PUB js end\n", "// PUB js end\n" + block, 'kebab module')

# the shop door: in through it (like the N47's stairs), and out of it if you're knocked down beside it
s = swap(s, "  if (ST.fixed && ST.bus) { f = makeFoe(type,", "  if (ST.fixed && (ST.bus || ST.door)) { f = makeFoe(type,", 'door spawn')
s = swap(s, "if (['leap', 'fly', 'swim', 'dead'].includes(e.state) || (ST.bus && e.state === 'enter')) return;",
         "if (['leap', 'fly', 'swim', 'dead'].includes(e.state) || ((ST.bus || ST.door) && e.state === 'enter')) return;", 'door walk in')
s = swap(s, "(e.x > R + 4 && !ST.bus))", "(e.x > R + 4 && !ST.bus && !ST.door))", 'counter side')
s = swap(s, "function splashOut(f) {\n  if (ST.bus) {", "function splashOut(f) {\n  if (ST.door) { kebabOut(f); return; }   // Version 59\n  if (ST.bus) {", 'thrown out')
# the shop, the ticket and the waves
s = swap(s, "function drawStageBg() {\n", "function drawStageBg() {\n  if (ST.bg === 'kebab') { kebabBg(); return; }   // Version 59\n", 'shop background')
s = swap(s, "if (!cutin) { drawHUD(); drawDeniseHUD(); if (ST && ST.drive && mode === 'play') drawDriveHud(); }",
         "if (!cutin) { drawHUD(); drawDeniseHUD(); if (ST && ST.drive && mode === 'play') drawDriveHud(); kebabHud(); }", 'ticket HUD')
s = swap(s, "(ST.hidden ? 'HIDDEN' : 'STAGE ' + ST.n)", "(ST.door ? 'WAVE ' + (S.waveIdx + 1) : ST.hidden ? 'HIDDEN' : 'STAGE ' + ST.n)", 'wave label')
s = swap(s, "  updateWaves(dt);\n  updateCam(dt);", "  updateWaves(dt);\n  kebabTick(dt);\n  updateCam(dt);", 'endless waves')
# a mini run: no saving over the campaign, its own game over, quit and restart
# (the siege's own game over is in v55_build's gameOver swap, so re-running the chain stays clean)
s = swap(s, "  if (!NET.on && run) { const d = runData();", "  if (!NET.on && run && !run.mini) { const d = runData();", 'no carry-on save')
s = swap(s, "else { pauseConfirm = false; clearSavedRun(); mode = 'select';",
         "else { pauseConfirm = false; if (run && run.mini) { kebabEnd('GAVE UP', true); return; } clearSavedRun(); mode = 'select';", 'pause quit')
s = swap(s, "sfx('start'); restartStage(); }", "sfx('start'); if (run && run.mini) kebabRestart(); else restartStage(); }", 'pause restart')

s = swap(s, "ctx.fillText(run.lives >= MAX_LIVES ? 'LIVES MAXED' : 'EXTRA LIFE AT ' + run.nextLife.toLocaleString('en-GB'), W - 20, 75);",
         "ctx.fillText(run.mini ? 'ONE LIFE' : run.lives >= MAX_LIVES ? 'LIVES MAXED' : 'EXTRA LIFE AT ' + run.nextLife.toLocaleString('en-GB'), W - 20, 75);", 'one life label')

open(PAGE, 'w', encoding='utf-8').write(s)
print('v59_build: web/index.html updated')
