"""Version 85: the jukebox in the Harvest Moon. python3 tools/v85_jukebox_build.py (re-runnable; patches web/index.html).
Code: tools/v85/jukebox.js between `// V85 jukebox start` and `// V85 jukebox end`, after the lads coming alive.
Art: web/bg/pub/jukebox.png (PixelLab, in the style of the arcade cabinet).
The songs with vocals and the guitar songs live in jukebox/ at the top of the repo, NOT in web/, so the in-app update
never downloads them (34 files, about 80 MB): the jukebox streams them from raw.githubusercontent.com on main.
To add a song: put <key>_1.mp3 and <key>_2.mp3 (128 kbps, about -14.5 LUFS) in jukebox/ and a line in JUKE.pages.
The pub gets 200 px longer at the far end for it."""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); PAGE = os.path.join(ROOT, 'web', 'index.html')
s = open(PAGE, encoding='utf-8').read()
start, end = '// V85 jukebox start', '// V85 jukebox end'
if start in s: a = s.index(start); b = s.index(end) + len(end) + 1; s = s[:a] + s[b:]
js = open(os.path.join(ROOT, 'tools', 'v85', 'jukebox.js'), encoding='utf-8').read()
anchor = '// V85 alive end\n'
assert s.count(anchor) == 1
s = s.replace(anchor, anchor + start + '\n' + js.rstrip('\n') + '\n' + end + '\n')
SWAPS = [
    ("const PUB_W = 3100, PUB_FLOOR = 400;", "const PUB_W = 3300, PUB_FLOOR = 400;   /* Version 85: 3100 until the jukebox */"),
    ("  { id: 'snake', x: 2990 },   // SNAKE (Version 74)\n", "  { id: 'snake', x: 2990 },   // SNAKE (Version 74)\n  { id: 'jukebox', x: 3135 },   // the jukebox (Version 85)\n"),
    ("  if (o.id === 'endings') return 'WHERE ARE THEY NOW · ' + endingsGot().length + ' OF ' + ENDING_LADS.length;   // Version 71\n",
     "  if (o.id === 'endings') return 'WHERE ARE THEY NOW · ' + endingsGot().length + ' OF ' + ENDING_LADS.length;   // Version 71\n"
     "  if (o.id === 'jukebox') return JUKE.now ? 'JUKEBOX · ' + JUKE.now.title.toUpperCase() : 'THE JUKEBOX · PICK A SONG';   // Version 85\n"),
    ("  if (o.id === 'endings') { endingsOpen(); return; }   // Version 71\n",
     "  if (o.id === 'endings') { endingsOpen(); return; }   // Version 71\n  if (o.id === 'jukebox') { jukeOpen(); return; }   // Version 85\n"),
    ("  endingsWallDraw(cx);   // Version 71\n", "  endingsWallDraw(cx);   // Version 71\n  jukeDraw(cx);   // Version 85\n"),
    ("  pubTabHud();\n  hubCountHud();\n", "  pubTabHud();\n  hubCountHud();\n  jukePlate();   // Version 85\n"),
    ("  if (mode === 'endings') { updateEndings(); return true; }\n", "  if (mode === 'endings') { updateEndings(); return true; }\n  if (mode === 'juke') { updateJuke(); return true; }   // Version 85\n"),
    ("  if (mode === 'endings') { drawEndings(); return; }\n", "  if (mode === 'endings') { drawEndings(); return; }\n  if (mode === 'juke') { drawJuke(); return; }   // Version 85\n"),
    ("  if (mode === 'endings') { endingsClose(); return true; }\n", "  if (mode === 'endings') { endingsClose(); return true; }\n  if (mode === 'juke') { jukeClose(); return true; }   // Version 85\n"),
    ("function musicTick() {\n", "function musicTick() {\n  if (typeof jukeTick === 'function') jukeTick();   // Version 85: the jukebox\n"),
]
for old, new in SWAPS:
    if new in s: continue
    assert s.count(old) == 1, old[:90]
    s = s.replace(old, new)
open(PAGE, 'w', encoding='utf-8').write(s); print('v85 jukebox: patched')
