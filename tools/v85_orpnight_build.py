"""Version 85: the rest of the Orpington night. python3 tools/v85_orpnight_build.py (re-runnable; patches web/index.html).
Code: tools/v85/orpnight.js between `// V85 orpnight start` and `// V85 orpnight end`, after the lads coming alive (its own anchor, so it merges with the run back).
Hooks: the clock ticks and draws in the Orpington per-frame code; the blag takes over the Atlantis door; the present-day
chat goes in front of the first Orpington chat."""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); PAGE = os.path.join(ROOT, 'web', 'index.html')
s = open(PAGE, encoding='utf-8').read()
start, end = '// V85 orpnight start', '// V85 orpnight end'
if start in s: a = s.index(start); b = s.index(end) + len(end) + 1; s = s[:a] + s[b:]
js = open(os.path.join(ROOT, 'tools', 'v85', 'orpnight.js'), encoding='utf-8').read()
anchor = '// V85 alive end\n'
assert s.count(anchor) == 1
s = s.replace(anchor, anchor + start + '\n' + js.rstrip('\n') + '\n' + end + '\n')
SWAPS = [
    # the clock runs under everything, and the blag stops the floor like a how-to card
    ("  if (S.howto) { orpHowtoTick(dt); return; }\n  if (S.exitReady) {",
     "  orpClockTick(dt);   // Version 85: the night's clock\n  if (S.howto) { orpHowtoTick(dt); return; }\n  if (S.blag) { orpBlagTick(dt); return; }   // Version 85: the blag\n  if (S.exitReady) {"),
    ("  // the way on: an arrow to the side you leave by\n",
     "  orpDrawClock(); orpDrawBlag();   // Version 85: the night's clock and the blag\n  // the way on: an arrow to the side you leave by\n"),
    # the door: questions first, then everyone in but Kelly
    ("  say(d1, 'Wristbands. In you go. Not him.', 2.4, true);\n  setTimeout0(() => { if (kel) say(kel, \"But I'm WITH them!\", 2, true); else say(player, \"But I'm WITH them!\", 2, true); }, 1.6);\n  setTimeout0(() => orpComic('pdoor', () => {\n    if (player.def.id === 'kelly') showBanner('1AM', 'Kelly talked his way in through the fire exit', 2.6);\n    orpWipe(1, 1, 'INSIDE ATLANTIS'); S.wave = null; S.waveIdx++;\n  }), 3.4);\n",
     "  say(d1, 'Wristbands. Hang on. Few questions.', 2.2, true);   // Version 85: the blag\n  setTimeout0(() => orpBlagStart(d1, (smooth, asKelly) => {\n  say(d1, asKelly ? 'Not you, mate.' : smooth ? 'Go on then. In you go. Not him.' : 'Wristband. Fine. In. Not him.', 2.4, true);\n  setTimeout0(() => { if (kel) say(kel, \"But I'm WITH them!\", 2, true); else say(player, \"But I'm WITH them!\", 2, true); }, 1.6);\n  setTimeout0(() => orpComic('pdoor', () => {\n    if (player.def.id === 'kelly') showBanner('1AM', 'Kelly talked his way in through the fire exit', 2.6);\n    orpWipe(1, 1, 'INSIDE ATLANTIS'); S.wave = null; S.waveIdx++;\n  }), 3.4);\n  }), 1.8);\n"),
    ("  S.frog = null; S.served = null; S.queue = null; S.dance = null; S.sue = null; S.howto = null;",
     "  S.frog = null; S.served = null; S.queue = null; S.dance = null; S.sue = null; S.howto = null; S.blag = null;"),
    ("function openChat(lines, next, headline, era) {\n",
     "function openChat(lines, next, headline, era) {\n  if (typeof orpNowFirst === 'function' && orpNowFirst(lines, next, headline, era)) return;   // Version 85: the present day first\n"),
]
for old, new in SWAPS:
    if new in s: continue
    assert s.count(old) == 1, old[:90]
    s = s.replace(old, new)
open(PAGE, 'w', encoding='utf-8').write(s); print('v85 orpnight: patched')
