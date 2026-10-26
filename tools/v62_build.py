"""Version 62: trophies and your own button layout.

Patches web/index.html in place (run from the repo root, after tools/v61_build.py):  python3 tools/v62_build.py
Safe to run again; it re-runs v61_build.py first (after adding a Trophies button to tools/title3d, which that chain
copies in). The code is tools/v62/ach.js and tools/v62/layout.js, put in whole between `// V62 js start` and
`// V62 js end` (after the quality of life block). Hooks for the trophies are also in tools/v55/pub.js (pubFlash,
miniEnd) and tools/v61/qol.js (the tick and the cloud save).

1. Trophies: 29 achievements; each one puts a bonus on your tab with a card at the top of the screen. A Trophies
   button on the select screen opens the list. Kept on the phone and in the cloud save.
2. Button layout: Pause > Settings > BUTTON LAYOUT on a touch screen. Drag the stick and buttons, size each one,
   mirror, reset. The floating stick's half of the screen follows wherever you put it.
"""
import os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, 'web', 'index.html')
T3 = os.path.join(ROOT, 'tools', 'title3d')
read = lambda p: open(p, encoding='utf-8').read()


def swap(s, old, new, label):
    if new in s:
        return s
    if s.count(old) != 1:
        sys.exit(f'v62_build: could not find the {label} (found {s.count(old)} matches)')
    return s.replace(old, new)


# ---------------------------------------------------------------- the 3D select screen: a Trophies button
h = read(os.path.join(T3, 'title3d.html'))
h = swap(h, """          <button class="t3ghost" id="t3-online" type="button" hidden>Play online</button>""",
         """          <button class="t3ghost" id="t3-trophy" type="button">Trophies</button>
          <button class="t3ghost" id="t3-online" type="button" hidden>Play online</button>""", '3D trophies button')
open(os.path.join(T3, 'title3d.html'), 'w', encoding='utf-8').write(h)
j = read(os.path.join(T3, 'title3d.js'))
j = swap(j, """  click('online', () => { if (netAvailable()) { sfx('page'); openNetLobby(); } });""",
         """  click('trophy', () => trophyOpen('select'));   // Version 62
  click('online', () => { if (netAvailable()) { sfx('page'); openNetLobby(); } });""", '3D trophies click')
open(os.path.join(T3, 'title3d.js'), 'w', encoding='utf-8').write(j)

subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'v61_build.py')], check=True)
s = read(PAGE)

start, end = '// V62 js start', '// V62 js end'
code = read(os.path.join(ROOT, 'tools', 'v62', 'ach.js')).rstrip('\n') + '\n' + read(os.path.join(ROOT, 'tools', 'v62', 'layout.js')).rstrip('\n')
block = start + '\n' + code + '\n' + end + '\n'
if start in s:
    a = s.index(start); b = s.index(end) + len(end) + 1
    s = s[:a] + block + s[b:]
else:
    s = swap(s, "// QOL js end\n", "// QOL js end\n" + block, 'version 62 module')

# ---------------------------------------------------------------- the button layout
s = swap(s, "function applyTouchLayout() {\n",
         "function applyTouchLayout() {\n  if (settings.tl && tlApply()) return;   // your own layout (Version 62)\n", 'custom layout')
s = swap(s, "if (!role && (settings.lefty ? p.x > W * 0.5 : p.x < W * 0.5) && p.y > 120) role = 'stick';",
         "if (!role && (STICK.x > W * 0.5 ? p.x > W * 0.5 : p.x < W * 0.5) && p.y > 120) role = 'stick';   // the stick's half follows the stick (Version 62)", 'stick half')
s = swap(s, "    { id: 'run', label: 'RUNNING',",
         "    { id: 'layout', label: 'BUTTON LAYOUT', val: settings.tl ? 'YOURS \\u00b7 EDIT' : 'EDIT', touch: true },   // Version 62\n    { id: 'run', label: 'RUNNING',", 'layout row')
s = swap(s, "rows.forEach((r, i) => { r.x = 452; r.y = 110 + i * 32;",
         "rows.forEach((r, i) => { r.x = 452; r.y = 110 + i * (rows.length > 11 ? 30 : 32);", 'settings spacing')
s = swap(s, "  else if (id === 'run') settings.run =",
         "  else if (id === 'layout') { tleOpen(); return; }   // Version 62\n  else if (id === 'run') settings.run =", 'layout open')
# ---------------------------------------------------------------- the trophies
s = swap(s, "function showBanner(text, sub, life) { ",
         "function showBanner(text, sub, life) { if (typeof achBanner === 'function') achBanner(text);   // Version 62\n  ", 'banner hook')
# ---------------------------------------------------------------- the two new screens (added after Version 61's lines, so theirs stay whole)
s = swap(s, "  if (mode === 'cont') { contUpdate(dt); return true; }   // Version 61",
         "  if (mode === 'cont') { contUpdate(dt); return true; }   // Version 61\n  if (mode === 'tledit') { tleUpdate(dt); return true; }   // Version 62\n  if (mode === 'trophies') { updateTrophies(); return true; }", 'new screens step')
s = swap(s, "  if (mode === 'cont') contDraw();   // Version 61",
         "  if (mode === 'cont') contDraw();   // Version 61\n  if (mode === 'tledit') tleDraw();   // Version 62", 'layout screen')
s = swap(s, "  if (mode === 'board') { drawBoard(); return; }",
         "  if (mode === 'trophies') { drawTrophies(); return; }   // Version 62\n  if (mode === 'board') { drawBoard(); return; }", 'trophies screen')
s = swap(s, "  if (mode === 'cont') { contNo(); return true; }   // Version 61\n",
         "  if (mode === 'tledit') { tleClose(); return true; }   // Version 62\n  if (mode === 'trophies') { trophyClose(); return true; }\n  if (mode === 'cont') { contNo(); return true; }   // Version 61\n", 'back button')

open(PAGE, 'w', encoding='utf-8').write(s)
print('v62_build: web/index.html updated')
