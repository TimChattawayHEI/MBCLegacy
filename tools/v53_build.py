"""Version 53: Nightlife 2006, a new chapter between Elba 2002 and Carp Diem.

Patches web/index.html in place (run from the repo root, after tools/v52_build.py):  python3 tools/v53_build.py
Safe to run again (the module is replaced between its markers; every other change is a swap that skips when done).

- tools/v53/nightlife.js: the chapter itself (stages, enemies, bosses, chats, the train, the bus, Seb's night), injected
  whole between `// NL js start` and `// NL js end`.
- tools/v53/sheets.json (from tools/v53/foe_sheets.py): sprite sheet layout and frame picks for every new character.
  A character without a sheet yet borrows an existing one (SPRITE_ALIAS) so the game always runs.
- This script: the hooks into the game (route, chapter labels, waves, events, the boss engine, drawing, rage, the
  bus rules, the 2006 phone, the 3D stage list).
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, 'web', 'index.html')
V53 = os.path.join(ROOT, 'tools', 'v53')


def swap(s, old, new, label, count=1):
    if new in s:
        return s
    if s.count(old) != count:
        sys.exit(f'v53_build: could not find the {label} (found {s.count(old)} matches)')
    return s.replace(old, new)


s = open(PAGE, encoding='utf-8').read()

# ---------------------------------------------------------------- the module
mod = open(os.path.join(V53, 'nightlife.js'), encoding='utf-8').read()
block = '// NL js start\n' + mod.rstrip() + '\n// NL js end\n'
if '// NL js start' in s:
    s = re.sub(r'// NL js start\n.*?// NL js end\n', lambda m: block, s, flags=re.S)
else:
    s = swap(s, """// ================================================================== state
let mode = 'title',""", block + """// ================================================================== state
let mode = 'title',""", 'module anchor')

# ---------------------------------------------------------------- the route and chapter labels
s = swap(s, """const ROUTE = ['frequency', 'soundz', 'airport', 'road', 'divebar', 'beach', 'club', 'arrival', 'naval', 'social', 'pegnine'];""",
         """const ROUTE = ['frequency', 'soundz', 'airport', 'road', 'divebar', 'beach', 'club', 'nl_station', 'nl_train', 'nl_cx', 'nl_alley', 'nl_bus', 'arrival', 'naval', 'social', 'pegnine'];""", 'ROUTE')
s = swap(s, """i >= ROUTE.indexOf('arrival') ? 'carpdiem' : i >= ROUTE.indexOf('airport') ? 'elba' : '1999'; }""",
         """i >= ROUTE.indexOf('arrival') ? 'carpdiem' : i >= ROUTE.indexOf('nl_station') ? 'nightlife' : i >= ROUTE.indexOf('airport') ? 'elba' : '1999'; }""", 'chapterOf')
s = swap(s, """({ elba: 'ELBA 2002', carpdiem: 'CARP DIEM', ramsden: 'RAMSDEN' })[start]""",
         """({ elba: 'ELBA 2002', nightlife: 'NIGHTLIFE 2006', carpdiem: 'CARP DIEM', ramsden: 'RAMSDEN' })[start]""", 'startLabel')
s = swap(s, """const at = { elba: 'airport', carpdiem: 'arrival', fishery: 'arrival' }[start];""",
         """const at = { elba: 'airport', nightlife: 'nl_station', carpdiem: 'arrival', fishery: 'arrival' }[start];""", 'routeFrom')
s = swap(s, """settings.unlocked ? ['1999', 'elba', 'carpdiem', 'ramsden'] : ['1999', 'elba', 'carpdiem']""",
         """settings.unlocked ? ['1999', 'elba', 'nightlife', 'carpdiem', 'ramsden'] : ['1999', 'elba', 'nightlife', 'carpdiem']""", 'start options', count=2)
# Carp Diem moves to stages 13 to 16
for k, a, b in [('arrival', "word: 'LOOSE PLANK!' }, n: 8,", "word: 'LOOSE PLANK!' }, n: 13,"), ('naval', "  naval: { n: 9,", "  naval: { n: 14,"),
                ('social', "  social: { n: 10,", "  social: { n: 15,"), ('pegnine', "word: 'PEG NINE PROVIDES' }, n: 11,", "word: 'PEG NINE PROVIDES' }, n: 16,")]:
    s = swap(s, a, b, k + ' number')
# the extra chapter mustn't make Carp Diem much harder in a full run: the depth bonus stops growing at nine stages
s = swap(s, """const ri = vr.indexOf('road'), deep = Math.max(0, i - 2 - (ri >= 0 && ri < i ? 1 : 0));""",
         """const ri = vr.indexOf('road'), deep = Math.min(9, Math.max(0, i - 2 - (ri >= 0 && ri < i ? 1 : 0)));""", 'depth cap')
# Elba now hands over to 2006, and 2006 brings them home
s = swap(s, """    ['seb', 'Retuning to 104.1. Home time.'],
    ['sys', 'KRSSSHHHHHHHHHH'],
    ['sys', 'Back in the present. For real this time.'],""", """    ['seb', 'Retuning to 104.1. Home time.'],
    ['sys', 'KRSSSHHHHHHHHHH'],
    ['sys', 'Nearly the present. One more night out first.'],""", 'club outro')

# ---------------------------------------------------------------- waves, events, bosses
s = swap(s, """  try { updateElba(dt); } catch (e) { glitch('elba', e); }""",
         """  try { updateElba(dt); } catch (e) { glitch('elba', e); }
  try { updateNightlife(dt); } catch (e) { glitch('nightlife', e); }""", 'update hook')
s = swap(s, """  if (S.cut || S.carabSeq) return;""", """  if (S.cut || S.carabSeq || S.hold) return;""", 'wave hold')
s = swap(s, """  if (w.event) { runEvent(w.event); return; }
  if (w.raid)""", """  if (w.event) { runEvent(w.event); return; }
  if (nlStartWave(w)) return;
  if (w.boss === 'inspector' || w.boss === 'lenny' || w.boss === 'jeweller') {   // Nightlife 2006 bosses (Version 53)
    const d = FOES[w.boss], b = makeEBoss(w.boss, cam.x + W + 80, laneY(1), d.hp, { group: w.boss, hx: cam.x + W * 0.68, half: 28, poise: 70, poiseMax: 70 });
    foes.push(b); S.bosses = [b]; musicSet(bossMusic()); showBanner(d.name, d.sub || '', 2.4); setTimeout0(() => ladSay('boss', 1, true), 3); return;
  }
  if (w.raid)""", 'boss start')
s = swap(s, """  if (elbaEvent(ev)) return;""", """  if (elbaEvent(ev) || nlEvent(ev)) return;""", 'events')
s = swap(s, """  'IL CARABINIERE': ['carab'], 'I FRATELLI': ['gianni', 'marco', 'luca', 'paolo'],
};""", """  'IL CARABINIERE': ['carab'], 'I FRATELLI': ['gianni', 'marco', 'luca', 'paolo'],
  'THE TICKET INSPECTOR': ['inspector'], 'LEWISHAM LENNY': ['lenny'], 'THE JEWELLER': ['jeweller'],
};""", 'boss cards')
# the boss engine: a kind can run its own moves first
s = swap(s, """  updateEFx(b, dt);
""", """  updateEFx(b, dt);
  if (d.tick && b.state !== 'beaten' && d.tick(b, dt, rage)) { physics(b, dt); b.x = clamp(b.x, cam.x + 40, cam.x + W - 40); if (b.atk) resolveAttack(b, [player]); return; }
""", 'boss tick')
# ordinary foes too
s = swap(s, """  if (f.kind === 'nozzer' && nozzerExtra(f, dt)) return;""",
         """  if (f.kind === 'nozzer' && nozzerExtra(f, dt)) return;
  if (f.def.extra && f.def.extra(f, dt)) return;""", 'foe extra')
# Smiler's gift: an arcing throw that lands as a weapon
s = swap(s, """    if (s.kind === 'boomerang') {""", """    if (s.kind === 'gift') { nlGiftTick(s, dt); continue; }
    if (s.kind === 'boomerang') {""", 'gift update')
s = swap(s, """  if (drawShotPixel(sh)) return;""", """  if (sh.kind === 'gift') { shadow(sh.x - cam.x, sh.y, 10, sh.z); drawWeaponFloor(sh.w, sh.x - cam.x, sh.y - sh.z); return; }
  if (drawShotPixel(sh)) return;""", 'gift draw')

# ---------------------------------------------------------------- the naval-only bits stay on the lake
s = swap(s, """  if (!ST.fixed || S.fire > 0.8) return;""", """  if (!ST.fixed || ST.bg !== 'naval' || S.fire > 0.8) return;""", 'bbq hazard')
s = swap(s, """  if (ST.fixed) { S.scrollX += dt * (S.tow ? 300 : 40); updateNaval(dt); }""",
         """  if (ST.fixed && ST.bg === 'naval') { S.scrollX += dt * (S.tow ? 300 : 40); updateNaval(dt); }""", 'naval update')
s = swap(s, """  if (ST.fixed) ctx.translate(0, Math.sin(time * 2) * 2 + (S.tow ? Math.sin(time * 9) * 1.5 : 0));""",
         """  if (ST.fixed && ST.bg === 'naval') ctx.translate(0, Math.sin(time * 2) * 2 + (S.tow ? Math.sin(time * 9) * 1.5 : 0));
  else if ((ST.train || ST.bus) && !reduceMotion) ctx.translate(0, Math.round(Math.sin(time * 17) * ((S.trainV || 0) > 300 ? 1 : 0.4)) * 2);   // the rumble""", 'rumble')
s = swap(s, """  if (ST.fixed) list.push({ y: BBQ.y, f: drawBBQ });""", """  if (ST.fixed && ST.bg === 'naval') list.push({ y: BBQ.y, f: drawBBQ });""", 'bbq draw')
# on the bus, they come up the stairs; knocked off the end, they go back down them
s = swap(s, """  if (ST.fixed) {
    const [L, R] = ST.raft;""", """  if (ST.fixed && ST.bus) { f = makeFoe(type, 70 + rand(0, 50), FT + rand(8, 40)); f.vx = 140; }
  else if (ST.fixed) {
    const [L, R] = ST.raft;""", 'bus spawns')
s = swap(s, """function splashOut(f) {
  f.state = 'dead'; f.t = 0; f.remove = true; f.hp = 0;""", """function splashOut(f) {
  if (ST.bus) { f.state = 'dead'; f.t = 0; f.remove = true; f.hp = 0; sfx('thud'); popWord(f.x, f.y, 90, 'DOWN THE STAIRS!', true); addScore(300 + f.def.score); run.kills++; noteKO(f); if (f.token) releaseToken(f, 0); ladSay('ko', 0.4); return; }
  f.state = 'dead'; f.t = 0; f.remove = true; f.hp = 0;""", 'bus knockout')

# ---------------------------------------------------------------- drawing
s = swap(s, """function drawStageBg() {
  if (ST.bg === 'fishery') bgFisheryPixel();""", """function drawStageBg() {
  if (ST.era === 2006 && nlDrawStageBg(ST.bg)) return;
  if (ST.bg === 'fishery') bgFisheryPixel();""", 'bg hook')
s = swap(s, """  else if (ST.bg === 'ramsden') { if (bgReady(RAM_FILES)) drawRamsdenForePixel(); }
}""", """  else if (ST.bg === 'ramsden') { if (bgReady(RAM_FILES)) drawRamsdenForePixel(); }
  nlDrawFore();
}""", 'fore hook')

# ---------------------------------------------------------------- Seb's rage, Seb at your side, the holds
s = swap(s, """function pwr(p) { return p.def.power * (p.buffT > 0 ? 1.5 : 1); }""",
         """function pwr(p) { return p.def.power * (p.buffT > 0 ? 1.5 : 1) * (p.rage ? 1.35 : 1); }""", 'rage power')
s = swap(s, """  const crazed = e.buffT > 0;""", """  const crazed = e.buffT > 0 || e.rage;""", 'rage look')
s = swap(s, """  if (e === player && e.buffT > 0) {
    const pulse = 0.5 + Math.sin(time * 10) * 0.2, fade = Math.min(1, e.buffT / 1.5);""", """  if (e === player && (e.buffT > 0 || e.rage)) {
    const pulse = 0.5 + Math.sin(time * 10) * 0.2, fade = e.rage ? 0.8 : Math.min(1, e.buffT / 1.5);""", 'rage aura')
s = swap(s, """  if (e.ally) { ctx.save(); ctx.scale(1 / dir, 1);""", """  if (e.ally && !e.friend) { ctx.save(); ctx.scale(1 / dir, 1);""", 'friend ring')
s = swap(s, """const tint = e.flash > 0 ? 'white' : (e.ally || (crazed && Math.floor(time * 10) % 2)) ? 'red' : null;""",
         """const tint = e.flash > 0 ? 'white' : ((e.ally && !e.friend) || (crazed && Math.floor(time * 10) % 2)) ? 'red' : null;""", 'friend tint')
s = swap(s, """  if (e === player && e.state === 'netted' && e.heldBy !== 'lady') {""",
         """  if (e === player && e.state === 'netted' && e.heldBy !== 'lady' && !(e.heldBy && e.heldBy.kind)) {""", 'held overlay')
# stage start clears the night's state on the lads
s = swap(s, """p.buffT = 0; p.crashT = 0; p.scale = 1; p.meter = 100; meterNopeT = 0;""",
         """p.buffT = 0; p.crashT = 0; p.scale = 1; p.meter = 100; meterNopeT = 0; p.rage = false; p.heldBy = null;""", 'reset rage')

# ---------------------------------------------------------------- 2006 phones: a colour screen, mixed case
s = swap(s, """  if (chat.era == 1999 || chat.era == 2002) { drawNokia(); return; }""",
         """  if (chat.era == 1999 || chat.era == 2002 || chat.era == 2006) { drawNokia(); return; }""", 'phone era')
s = swap(s, """  ctx.fillStyle = '#c9ccd0'; ctx.font = '800 13px ' + BODY; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText('N O K I A', W / 2, by + 40);""",
         """  const v6 = chat.era == 2006;   // 2006: a slim silver flip phone with a colour screen (Version 53)
  ctx.fillStyle = '#c9ccd0'; ctx.font = '800 13px ' + BODY; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(v6 ? '' : 'N O K I A', W / 2, by + 40);""", 'phone brand')
s = swap(s, """  const g = ctx.createLinearGradient(0, sy, 0, sy + sh); g.addColorStop(0, '#a9c27a'); g.addColorStop(1, '#8fab62');""",
         """  const g = ctx.createLinearGradient(0, sy, 0, sy + sh); g.addColorStop(0, v6 ? '#1e4a8e' : '#a9c27a'); g.addColorStop(1, v6 ? '#0d2350' : '#8fab62');""", 'phone screen')
s = swap(s, """  const ink = '#1f2a14';""", """  const ink = v6 ? '#eaf2ff' : '#1f2a14';""", 'phone ink')
s = swap(s, """    const [who, raw] = chat.lines[i]; const text = clean(raw).toUpperCase();""",
         """    const [who, raw] = chat.lines[i]; const text = v6 ? clean(raw) : clean(raw).toUpperCase();""", 'phone case')

# ---------------------------------------------------------------- a new weapon: the bus pole
s = swap(s, """  cone: { name: 'TRAFFIC CONE',""", """  pole: { name: 'BUS POLE', reach: 92, dmg: 12, kd: false, dur: 6, speed: 0.28, t0: 0.07, t1: 0.16, len: 64, col: '#e8c23a', throwDmg: 15, word: 'DING DING!' },
  cone: { name: 'TRAFFIC CONE',""", 'pole weapon')
s = swap(s, """  ball: { grip: [0, 0], ang: 0, round: true },""", """  ball: { grip: [0, 0], ang: 0, round: true },
  pole: { grip: [3, 2], ang: 0 },""", 'pole grip')

# ---------------------------------------------------------------- sprites: real sheets where they exist, borrowed ones otherwise
sheets = json.load(open(os.path.join(V53, 'sheets.json'))) if os.path.exists(os.path.join(V53, 'sheets.json')) else {}
BORROW = {'city': 'clubm', 'itgirl': 'clubf', 'burb': 'tracksuit', 'hoops': 'ladette', 'snood': 'hoodie', 'puffer': 'hoodie', 'hood': 'hoodie',
          'grappler': 'bouncer', 'dipper': 'clubm', 'lookout': 'townie', 'stag': 'chunk', 'groom': 'townie', 'inspector': 'sec', 'lenny': 'beast',
          'jeweller': 'mafioso', 'commuter': 'clubf', 'oldboy': 'regular', 'smiler': 'regular'}
metas, frames, aliases = [], [], []
for k, src in BORROW.items():
    if k in sheets:
        metas.append(f'"{k}":' + json.dumps(sheets[k]['meta'], separators=(',', ':')))
        frames.append(f'  {k}: {sheets[k]["frames"]},')
    else:
        aliases.append((k, src))
s = re.sub(r'/\* NL meta \*/.*?/\* NL meta end \*/', '', s)
s = re.sub(r'  // NL frames\n.*?  // NL frames end\n', '', s, flags=re.S)
s = re.sub(r'// NL alias\n.*?// NL alias end\n', '', s, flags=re.S)
if metas:
    s = s.replace('const SPRITE_META = {', 'const SPRITE_META = {/* NL meta */' + ','.join(metas) + ',/* NL meta end */', 1)
if frames:
    s = s.replace('const FOE_FRAMES = {\n', 'const FOE_FRAMES = {\n  // NL frames\n' + '\n'.join(frames) + '\n  // NL frames end\n', 1)
al = ''.join(f"SPRITE_ALIAS.{k} = '{v}'; FOE_FRAMES.{k} = FOE_FRAMES['{v}'] || FOE_FRAMES.townie;\n" for k, v in aliases)
anchor = "const SPRITE_ALIAS = { biglad: 'chunk', doorman: 'bouncer', rider: 'clubm', biker: 'clubm' };\n"
if s.count(anchor) != 1:
    sys.exit('v53_build: no SPRITE_ALIAS anchor')
s = s.replace(anchor, anchor + '// NL alias\n' + al + '// NL alias end\n')

# preload the new art with the rest
newbg = sorted('nightlife/' + f[:-4] for f in os.listdir(os.path.join(ROOT, 'web', 'bg', 'nightlife')) if f.endswith('.png')) if os.path.isdir(os.path.join(ROOT, 'web', 'bg', 'nightlife')) else []
newbg += [p for p in ('props/luggage', 'props/pole', 'weapons/pole') if os.path.exists(os.path.join(ROOT, 'web', 'bg', p + '.png'))]
m = re.search(r'const ASSET_BG = (\[.*?\]);', s)
lst = json.loads(m.group(1))
lst = sorted(set(lst) | set(newbg))
s = s[:m.start(1)] + json.dumps(lst).replace('","', '", "') + s[m.end(1):]

# ---------------------------------------------------------------- the 3D stage list (also in tools/title3d/)
T3 = [
    ("""naval: 'No boss. Survive the night.', social: 'Nozzer, then Denise', pegnine: 'Big Gary', ramsden: 'Big Gaz, then Lady Addict' };""",
     """naval: 'No boss. Survive the night.', social: 'Nozzer, then Denise', pegnine: 'Big Gary', ramsden: 'Big Gaz, then Lady Addict',
    nl_station: 'The Ticket Inspector', nl_train: 'Lewisham Lenny', nl_cx: 'No boss. Make the barriers.', nl_alley: 'The Jeweller', nl_bus: 'No boss. Hold the top deck.' };""", '3D bosses'),
    ("""  const iE = ROUTE.indexOf('airport'), iC = ROUTE.indexOf('arrival');""", """  const iE = ROUTE.indexOf('airport'), iN = ROUTE.indexOf('nl_station'), iC = ROUTE.indexOf('arrival');""", '3D indexes'),
    ("""    { id: 'elba', name: 'ELBA 2002', keys: ROUTE.slice(iE, iC),""", """    { id: 'elba', name: 'ELBA 2002', keys: ROUTE.slice(iE, iN),""", '3D elba keys'),
    ("""    { id: 'carpdiem', name: 'CARP DIEM',""", """    { id: 'nightlife', name: 'NIGHTLIFE 2006', keys: ROUTE.slice(iN, iC), mood: { world: [0.82, 0.86, 1.18], sky: [0.7, 0.78, 1.25], fog: 0x0a0a3a, light: [1.15, 0.85, 1.05] } },
    { id: 'carpdiem', name: 'CARP DIEM',""", '3D chapter'),
]
for o, n, l in T3:
    s = swap(s, o, n, l)
s = swap(s, """#t3-tabs{display:grid;grid-template-columns:repeat(4,auto);""", """#t3-tabs{display:grid;grid-template-columns:repeat(5,auto);""", '3D tabs css')

open(PAGE, 'w', encoding='utf-8').write(s)
print('v53_build: web/index.html updated', f'({len(metas)} sheets, {len(aliases)} borrowed)')

SRC = os.path.join(ROOT, 'tools', 'title3d', 'title3d.js')
j = open(SRC, encoding='utf-8').read()
for o, n, l in T3:
    j = swap(j, o, n, l + ' (title3d.js)')
open(SRC, 'w', encoding='utf-8').write(j)
CSS = os.path.join(ROOT, 'tools', 'title3d', 'title3d.css')
c = open(CSS, encoding='utf-8').read()
c = swap(c, """#t3-tabs{display:grid;grid-template-columns:repeat(4,auto);""", """#t3-tabs{display:grid;grid-template-columns:repeat(5,auto);""", '3D tabs (title3d.css)')
open(CSS, 'w', encoding='utf-8').write(c)
