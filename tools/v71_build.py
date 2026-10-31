"""Version 71: the story in comic pages, the lads' endings and the damage report (Tim, 30 October). Patches
web/index.html in place (run from the repo root): python3 tools/v71_build.py. Safe to run again; like V66 to V70 it
doesn't re-run the earlier build scripts. The panels are painted by tools/v71/comics.py.

- tools/v71/v71.js goes in between `// V71 js start` and `// V71 js end`, after the V70 block.
- openChat shows a comic page before a chapter's first group chat (and before the millennium and the fireball), or
  after one (the loft, home to the present): COMIC_BEFORE and COMIC_AFTER in v71.js.
- The campaign ends: the last chat, the Big Gary page, then each lad's ending (yours goes on the wall at the Harvest
  Moon), then the damage report with Marc, then the win screen as before.
- The run counts food, specials, knockdowns, throws, bosses and rounds bought for the damage report.
- The Harvest Moon is longer: the endings wall is past the trophy cabinet.
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, 'web', 'index.html')
read = lambda p: open(p, encoding='utf-8').read()

SWAPS = [
    ('openChat', "function openChat(lines, next, headline, era) {\n",
     "function openChat(lines, next, headline, era) {\n  next = comicWrap(lines, next, headline, era); if (next === COMIC_STOP) return;   // Version 71: comic pages\n"),
    ('the end', "    openChat(lines, winGame);\n",
     "    comicPreload('pend'); openChat(lines, () => comicShow('pend', () => endingShow(winGame)));   // Version 71: Big Gary, the endings, the damage\n"),
    ('update modes', "  if (mode === 'trophies') { updateTrophies(); return true; }\n",
     "  if (mode === 'trophies') { updateTrophies(); return true; }\n"
     "  if (mode === 'comic') { updateComic(dt); return true; }   // Version 71\n"
     "  if (mode === 'ending') { updateEnding(dt); return true; }\n"
     "  if (mode === 'endings') { updateEndings(); return true; }\n"),
    ('draw modes', "  if (mode === 'trophies') { drawTrophies(); return; }   // Version 62\n",
     "  if (mode === 'trophies') { drawTrophies(); return; }   // Version 62\n"
     "  if (mode === 'comic') { drawComic(); return; }   // Version 71\n"
     "  if (mode === 'ending') { drawEnding(); return; }\n"
     "  if (mode === 'endings') { drawEndings(); return; }\n"),
    ('back button', "  if (mode === 'trophies') { trophyClose(); return true; }\n",
     "  if (mode === 'trophies') { trophyClose(); return true; }\n"
     "  if (mode === 'comic') { comicEnd(); return true; }   // Version 71\n"
     "  if (mode === 'ending') { pressed.add(ending && ending.from === 'wall' ? 'escape' : 'punch'); return true; }\n"
     "  if (mode === 'endings') { endingsClose(); return true; }\n"),
    ('food count', "    const f = FOODS[it.f];\n", "    const f = FOODS[it.f]; runStat('food', it.f);   // Version 71\n"),
    ('special count', "function startSpecial(p) {\n", "function startSpecial(p) {\n  runStat('specials', p.def.id);   // Version 71\n"),
    ('throw count', "function throwWeapon(p) {\n", "function throwWeapon(p) {\n  runStat('thrown');   // Version 71\n"),
    ('floor count', "function knockDown(t, dir, kb) { t.state = 'down';", "function knockDown(t, dir, kb) { if (t.kind === 'player') runStat('floored'); t.state = 'down';"),
    ('boss count', "function bossDefeated(b) {\n  b.atk = null;\n", "function bossDefeated(b) {\n  b.atk = null; runStat('bosses');   // Version 71\n"),
    ('round count', "PUB.round = true; if (run) run.lives++;", "PUB.round = true; runStat('rounds'); if (run) run.lives++;"),
    ('pub length', "const PUB_W = 2540, PUB_FLOOR = 400;", "const PUB_W = 2840, PUB_FLOOR = 400;   /* Version 71: 2540 until the endings wall */"),
    ('pub object', "  { id: 'trophy', x: 2420 },   // the trophy cabinet (Version 63)\n",
     "  { id: 'trophy', x: 2420 },   // the trophy cabinet (Version 63)\n  { id: 'endings', x: ENDINGS_X },   // the endings wall (Version 71)\n"),
    ('pub reach', "o.id === 'door' ? 90 : 62)", "o.id === 'door' ? 90 : o.id === 'endings' ? 150 : 62)"),
    ('pub prompt', "  if (o.id === 'trophy') return typeof achCount",
     "  if (o.id === 'endings') return 'WHERE ARE THEY NOW · ' + endingsGot().length + ' OF ' + ENDING_LADS.length;   // Version 71\n  if (o.id === 'trophy') return typeof achCount"),
    ('pub act', "  if (o.id === 'trophy') { if (typeof trophyOpen",
     "  if (o.id === 'endings') { endingsOpen(); return; }   // Version 71\n  if (o.id === 'trophy') { if (typeof trophyOpen"),
    ('pub wall', "  if (typeof trophyCabDraw === 'function') trophyCabDraw(cx);   // Version 63\n",
     "  if (typeof trophyCabDraw === 'function') trophyCabDraw(cx);   // Version 63\n  endingsWallDraw(cx);   // Version 71\n"),
    ('pub wall text', "  if (typeof trophyCabText === 'function') trophyCabText(cx);   // Version 63\n",
     "  if (typeof trophyCabText === 'function') trophyCabText(cx);   // Version 63\n  endingsWallText(cx);   // Version 71\n"),
]

s = read(PAGE)
for label, old, new in SWAPS:
    if new in s: continue
    if s.count(old) != 1: sys.exit(f'v71_build: could not find the {label} (found {s.count(old)})')
    s = s.replace(old, new)
start, end = '// V71 js start', '// V71 js end'
block = start + '\n' + read(os.path.join(ROOT, 'tools', 'v71', 'v71.js')).rstrip('\n') + '\n' + end + '\n'
if start in s: a = s.index(start); b = s.index(end) + len(end) + 1; s = s[:a] + block + s[b:]
else: k = s.index('// V70 js end\n') + len('// V70 js end\n'); s = s[:k] + block + s[k:]
open(PAGE, 'w', encoding='utf-8').write(s)
print('v71_build: web/index.html updated')
