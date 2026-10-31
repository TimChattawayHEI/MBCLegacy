"""Version 72: the Orpington 2001 chapter (Tim, 31 October). Patches web/index.html (and tools/title3d/title3d.js, the
3D select's source) in place, run from the repo root: python3 tools/v72_build.py. Safe to run again; like V66 to V71 it
doesn't re-run the earlier build scripts.

- tools/v72/orp2001.js goes in between `// V72 js start` and `// V72 js end`, after the V71 block: the stages, Mick, Sue,
  Alan and Jeff, getting served at the Blacksmiths, the roundabout traffic, the Atlantis door and the beat.
- Their sprite sheets (web/sprites/<key>.png, tools/v72/foe_sheets.py) go into SPRITE_META and FOE_FRAMES from
  tools/v72/sheets.json, between `/* ORP meta */` markers.
- The backdrops are web/bg/meshy/orp_*.png (tools/v72/orp_bg.py), drawn by the V64 Meshy code.
- The chapter sits between 1999 and Elba: ROUTE, chapterOf, the start labels, the route picker, the 3D chapter tabs.
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, 'web', 'index.html'); T3 = os.path.join(ROOT, 'tools', 'title3d', 'title3d.js')
read = lambda p: open(p, encoding='utf-8').read()

SWAPS = [
    ('per-frame hook', "  try { updateNightlife(dt); } catch (e) { glitch('nightlife', e); }\n",
     "  try { updateNightlife(dt); } catch (e) { glitch('nightlife', e); }\n  try { updateOrp(dt); } catch (e) { glitch('orp2001', e); }   // Version 72\n"),
    ('events', "  if (elbaEvent(ev) || nlEvent(ev)) return;", "  if (elbaEvent(ev) || nlEvent(ev) || orpEvent(ev)) return;   // Version 72: orpEvent"),
    ('mick', "  if (w.boss === 'inspector' || w.boss === 'lenny' || w.boss === 'jeweller') {",
     "  if (w.boss === 'inspector' || w.boss === 'lenny' || w.boss === 'jeweller' || w.boss === 'mick') {   // Version 72: Mick"),
    ('mini kind', "S.bosses = out.filter(f => f.kind === (w.boss || 'nozzer'));", "S.bosses = out.filter(f => f.kind === (w.boss || w.miniKind || 'nozzer'));"),
    ('mini card', "const key = w.boss || (w.mini && !w.fish ? 'nozzer' : null)", "const key = w.boss || (w.mini && !w.fish ? (w.miniKind || 'nozzer') : null)"),
    ('fore draw', "  nlDrawFore();\n  drawFG();", "  nlDrawFore();\n  orpDrawFore();   // Version 72\n  drawFG();"),
    ('beat damage', "const dmg = Math.max(1, k.dmg * (t === player ? D().dmg : 1)", "const dmg = Math.max(1, k.dmg * orpBeatMult(a, t) * (t === player ? D().dmg : 1)"),
    ('food', "ST.era === 1999 ? 'chips' : 'bacon'", "(ST.era === 1999 || ST.era === 2001) ? 'chips' : 'bacon'"),
    ('looks', "function lookFor(c, era) { return (era === 1999 || era === 2002)", "function lookFor(c, era) { return (era === 1999 || era === 2001 || era === 2002)"),
    ('chat phone', "  if (chat.era == 1999 || chat.era == 2002 || chat.era == 2006) { drawNokia(); return; }",
     "  if (chat.era == 1999 || chat.era == 2001 || chat.era == 2002 || chat.era == 2006) { drawNokia(); return; }"),
    ('chapterOf', ": i >= ROUTE.indexOf('airport') ? 'elba' : '1999'; }",
     ": i >= ROUTE.indexOf('airport') ? 'elba' : ROUTE.includes('orp_street') && i >= ROUTE.indexOf('orp_street') ? 'orp2001' : '1999'; }"),
    ('label', "function startLabel(start) { return ({ elba: 'ELBA 2002',", "function startLabel(start) { return ({ orp2001: 'ORPINGTON 2001', elba: 'ELBA 2002',"),
    ('route start', "  const at = { elba: 'airport', nightlife: 'nl_station',", "  const at = { orp2001: 'orp_street', elba: 'airport', nightlife: 'nl_station',"),
]
ROUTE_OPTS = ("['1999', 'elba', 'nightlife', 'carpdiem', 'ramsden'] : ['1999', 'elba', 'nightlife', 'carpdiem']",
              "['1999', 'orp2001', 'elba', 'nightlife', 'carpdiem', 'ramsden'] : ['1999', 'orp2001', 'elba', 'nightlife', 'carpdiem']")
T3_SWAPS = [
    ('3D bosses', "nl_alley: 'The Jeweller', nl_bus: 'No boss. Hold the top deck.' };",
     "nl_alley: 'The Jeweller', nl_bus: 'No boss. Hold the top deck.',\n    orp_street: 'No boss. Hold the bus stop.', orp_pub: 'Jeff, then Mick (and Sue)', orp_atlantis: 'No boss. Last one standing at 2am.' };"),
    ('3D indexes', "  const iE = ROUTE.indexOf('airport'), iN = ROUTE.indexOf('nl_station'), iC = ROUTE.indexOf('arrival');",
     "  const iO = ROUTE.indexOf('orp_street'), iE = ROUTE.indexOf('airport'), iN = ROUTE.indexOf('nl_station'), iC = ROUTE.indexOf('arrival');"),
    ('3D 1999', "    { id: '1999', name: '1999', keys: ROUTE.slice(0, iE),",
     "    { id: '1999', name: '1999', keys: ROUTE.slice(0, iO),"),
    ('3D chapter', "    { id: 'elba', name: 'ELBA 2002', keys: ROUTE.slice(iE, iN),",
     "    { id: 'orp2001', name: 'ORPINGTON 2001', keys: ROUTE.slice(iO, iE), mood: { world: [1.04, 0.94, 1.02], sky: [0.86, 0.84, 1.12], fog: 0x1c0d4a, light: [1.15, 0.95, 0.8] } },\n"
     "    { id: 'elba', name: 'ELBA 2002', keys: ROUTE.slice(iE, iN),"),
]


def swap(s, label, old, new, where):
    if new in s: return s
    if s.count(old) != 1: sys.exit(f'v72_build: could not find the {label} in {where} (found {s.count(old)})')
    return s.replace(old, new)


s = read(PAGE)
for label, old, new in SWAPS: s = swap(s, label, old, new, 'the page')
if ROUTE_OPTS[1] not in s:
    if s.count(ROUTE_OPTS[0]) != 2: sys.exit('v72_build: route picker lists not found')
    s = s.replace(ROUTE_OPTS[0], ROUTE_OPTS[1])
for label, old, new in T3_SWAPS: s = swap(s, label, old, new, 'the page')

# the sheets
sheets = json.load(open(os.path.join(ROOT, 'tools', 'v72', 'sheets.json')))
s = re.sub(r'/\* ORP meta \*/.*?/\* ORP meta end \*/', '', s)
s = re.sub(r'  // ORP frames\n.*?  // ORP frames end\n', '', s, flags=re.S)
metas = ','.join(f'"{k}":' + json.dumps(v['meta'], separators=(',', ':')) for k, v in sheets.items())
frames = '\n'.join(f'  {k}: {v["frames"]},' for k, v in sheets.items())
s = s.replace('const SPRITE_META = {', 'const SPRITE_META = {/* ORP meta */' + metas + ',/* ORP meta end */', 1)
s = s.replace('const FOE_FRAMES = {\n', 'const FOE_FRAMES = {\n  // ORP frames\n' + frames + '\n  // ORP frames end\n', 1)

# the chapter's code
start, end = '// V72 js start', '// V72 js end'
block = start + '\n' + read(os.path.join(ROOT, 'tools', 'v72', 'orp2001.js')).rstrip('\n') + '\n' + end + '\n'
if start in s: a = s.index(start); b = s.index(end) + len(end) + 1; s = s[:a] + block + s[b:]
else: k = s.index('// V71 js end\n') + len('// V71 js end\n'); s = s[:k] + block + s[k:]
open(PAGE, 'w', encoding='utf-8').write(s)

t = read(T3)
for label, old, new in T3_SWAPS: t = swap(t, label, old, new, 'title3d.js')
open(T3, 'w', encoding='utf-8').write(t)
print('v72_build: web/index.html and tools/title3d/title3d.js updated')
