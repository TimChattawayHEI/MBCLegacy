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


# ---------------------------------------------------------------- locked lads can't be picked anywhere (Thet, Ash)
# one rule used everywhere a lad gets chosen: a locked lad becomes the next unlocked one along
s = swap(s, "function ladLocked(c) { return !!c && ((c.id === 'thet' && !settings.thet) || (c.id === 'ash' && !settings.ash)); }",
         "function ladLocked(c) { return !!c && ((c.id === 'thet' && !settings.thet) || (c.id === 'ash' && !settings.ash)); }\n"
         "function freeLad(i) { const n = PLAYABLE.length; i = ((i | 0) % n + n) % n; for (let k = 0; k < n; k++) { if (!ladLocked(PLAYABLE[(i + k) % n])) return (i + k) % n; } return 0; }   // Version 65", 'free lad helper')
s = swap(s, "function newRun(ci, start) {\n  const c = PLAYABLE[ci];",
         "function newRun(ci, start) {\n  if (!NET.on) ci = freeLad(ci);   // Version 65: never a locked lad (online, the other phone may have him)\n  const c = PLAYABLE[ci];", 'new run guard')
s = swap(s, "NL.ready = false; NL.them = null; NL.go = null; NL.lad = sel;", "NL.ready = false; NL.them = null; NL.go = null; NL.lad = freeLad(sel);", 'lobby start lad')
s = swap(s, "    if (netLadTaken(NL.lad) && !NL.ready) step(1);", "    if ((netLadTaken(NL.lad) || ladLocked(PLAYABLE[NL.lad])) && !NL.ready) step(1);", 'lobby locked lad')
s = swap(s, "lads: [NL.lad, gi < 0 ? (NL.lad + 1) % n : gi]", "lads: [NL.lad, gi < 0 ? freeLad(NL.lad + 1) : gi]", 'guest default lad')
s = swap(s, "  openNetLobby(); NL.lad = Math.max(0, PLAYABLE.findIndex(c => c.id === PUB.lad));", "  openNetLobby(); NL.lad = freeLad(Math.max(0, PLAYABLE.findIndex(c => c.id === PUB.lad)));", 'pub lobby lad')
s = swap(s, "  openNetLobby(); NL.lad = Math.max(0, PLAYABLE.findIndex(c => c.id === lad));", "  openNetLobby(); NL.lad = freeLad(Math.max(0, PLAYABLE.findIndex(c => c.id === lad)));", 'invite lobby lad')
s = swap(s, "  PUB.from = from; PUB.next = next || null; PUB.lad = lad || PUB.lad || 'tim';",
         "  PUB.from = from; PUB.next = next || null; PUB.lad = lad || PUB.lad || 'tim';\n  if (ladLocked(CHAR_BY_ID[PUB.lad])) PUB.lad = 'tim';   // Version 65", 'pub lad guard')
s = swap(s, "    sel = Math.max(0, PLAYABLE.findIndex(c => c.id === id));\n", "    sel = freeLad(Math.max(0, PLAYABLE.findIndex(c => c.id === id)));\n", 'select commit')
s = swap(s, "      if (sr) { li = Math.max(0, ORDER.indexOf(PLAYABLE[sr.ci].id)); setView('cont'); } else setView('lad');",
         "      if (sr && !ladLocked(PLAYABLE[sr.ci])) { li = Math.max(0, ORDER.indexOf(PLAYABLE[sr.ci].id)); setView('cont'); } else setView('lad');", 'carry on locked')


# ---------------------------------------------------------------- the health bars, painted in Meshy (tools/v65/hud.py)
s = swap(s, "function drawHUD() {\n",
         "// Version 65: Meshy's gunmetal plate and glass-tube bars. A fill is one painted tile, repeated along the bar and cut off\n"
         "// where the bar ends; until the pictures load the old code bars are drawn instead.\n"
         "const HUD_FILES = ['plate', 'boss', 'fill_hp', 'fill_sp', 'fill_boss', 'fill_foe'].map(n => 'hud/' + n); HUD_FILES.forEach(f => bgImg(f)); ASSET_BG.push(...HUD_FILES);\n"
         "function hudFill(name, x, y, w, h, frac, trough, flash) {\n"
         "  const img = bgImg('hud/' + name); if (!img) return false;\n"
         "  x = PX(x); y = PX(y); w = PX(w); h = PX(h);\n"
         "  if (trough) { ctx.fillStyle = OUT; ctx.fillRect(x - 2, y - 2, w + 4, h + 4); }\n"
         "  ctx.fillStyle = '#141018'; ctx.fillRect(x, y, w, h);\n"
         "  const fw = PX(w * clamp(frac, 0, 1)); if (fw <= 0) return true;\n"
         "  ctx.save(); ctx.beginPath(); ctx.rect(x, y, fw, h); ctx.clip(); ctx.imageSmoothingEnabled = false;\n"
         "  const tw = img.width * 2; for (let tx = x; tx < x + fw; tx += tw) ctx.drawImage(img, tx, y, tw, h);\n"
         "  if (flash) { ctx.fillStyle = 'rgba(255,250,220,0.35)'; ctx.fillRect(x, y, fw, h); }\n"
         "  ctx.restore(); return true;\n"
         "}\n"
         "function hudFrame(name, x, y) { const img = bgImg('hud/' + name); if (!img) return false; ctx.save(); ctx.imageSmoothingEnabled = false; ctx.drawImage(img, PX(x), PX(y), img.width * 2, img.height * 2); ctx.restore(); return true; }\n"
         "function drawHUD() {\n", 'hud helpers')
s = swap(s, "  const p = player;\n  pxPanel(12, 12, 362, 84);\n",
         "  const p = player;\n  const plate = bgReady(HUD_FILES); if (!plate) pxPanel(12, 12, 362, 84);\n", 'hud plate fallback')
s = swap(s, "  ctx.fillStyle = OUT; ctx.fillRect(18, 18, 60, 2); ctx.fillRect(18, 88, 60, 2); ctx.fillRect(18, 20, 2, 68); ctx.fillRect(76, 20, 2, 68);\n",
         "  if (plate) hudFrame('plate', 12, 12); else { ctx.fillStyle = OUT; ctx.fillRect(18, 18, 60, 2); ctx.fillRect(18, 88, 60, 2); ctx.fillRect(18, 20, 2, 68); ctx.fillRect(76, 20, 2, 68); }\n", 'hud plate')
s = swap(s, "  bar(88, 46, 272, 14, p.hp / p.maxHp, p.hp / p.maxHp < 0.3 ? '#e5484d' : '#7fcf5a');\n",
         "  if (!(plate && hudFill(p.hp / p.maxHp < 0.3 ? 'fill_foe' : 'fill_hp', 88, 46, 274, 14, p.hp / p.maxHp, false, p.hp / p.maxHp < 0.3 && Math.floor(time * 4) % 2)))\n"
         "    bar(88, 46, 272, 14, p.hp / p.maxHp, p.hp / p.maxHp < 0.3 ? '#e5484d' : '#7fcf5a');\n", 'hud health')
s = swap(s, "    bar(88, 72, 150, 8, p.buffT / BUFF_TIME, Math.floor(time * 8) % 2 ? '#ff6a4a' : '#e2471c', '#2a1c1a');\n",
         "    if (!(plate && hudFill('fill_foe', 88, 72, 152, 10, p.buffT / BUFF_TIME, false, Math.floor(time * 8) % 2))) bar(88, 72, 150, 8, p.buffT / BUFF_TIME, Math.floor(time * 8) % 2 ? '#ff6a4a' : '#e2471c', '#2a1c1a');\n", 'hud buff')
s = swap(s, "    bar(88, 72, 150, 8, p.meter / 100, ready ? (Math.floor(time * 6) % 2 ? '#ffd23f' : '#f2a23a') : '#c98a2e', '#2c2a22');\n",
         "    if (!(plate && hudFill('fill_sp', 88, 72, 152, 10, p.meter / 100, false, ready && Math.floor(time * 6) % 2))) bar(88, 72, 150, 8, p.meter / 100, ready ? (Math.floor(time * 6) % 2 ? '#ffd23f' : '#f2a23a') : '#c98a2e', '#2c2a22');\n", 'hud special')
s = swap(s, "    bar(22, ny + 20, 196, 7, lastFoe.hp / lastFoe.maxHp, '#e5484d');\n",
         "    if (!hudFill('fill_foe', 22, ny + 20, 196, 8, lastFoe.hp / lastFoe.maxHp, true)) bar(22, ny + 20, 196, 7, lastFoe.hp / lastFoe.maxHp, '#e5484d');\n", 'hud foe')
s = swap(s, "    bar(W / 2 - 200, 124, 400, 12, hp / max, '#f2a23a', '#3a2a14');\n",
         "    if (!(bgReady(HUD_FILES) && hudFrame('boss', W / 2 - 216, 116) && hudFill('fill_boss', W / 2 - 200, 124, 400, 12, hp / max))) bar(W / 2 - 200, 124, 400, 12, hp / max, '#f2a23a', '#3a2a14');\n", 'hud boss')

# the other HUD panels (score, weapon, the last foe, pause) in the same gunmetal, nine-sliced from the plate's edges
s = swap(s, "function bar(x, y, w, h, frac, col, back) {\n",
         "function hudPanel(x, y, w, h) {\n"
         "  const img = bgImg('hud/plate'); if (!img || !bgReady(HUD_FILES)) { pxPanel(x, y, w, h); return; }\n"
         "  x = PX(x); y = PX(y); w = PX(w); h = PX(h); const c = 6, C = c * 2, mw = 50, mh = 10, sx = 120, sy = 26;   // corner (native), and a plain patch of the plate\n"
         "  ctx.save(); ctx.imageSmoothingEnabled = false; const d = (a, b, cw, ch, X, Y, Wd, Hd) => ctx.drawImage(img, a, b, cw, ch, X, Y, Wd, Hd);\n"
         "  d(sx, sy, mw, mh, x + C, y + C, w - 2 * C, h - 2 * C);\n"
         "  d(120, 0, img.width - 126, c, x + C, y, w - 2 * C, C); d(120, img.height - c, img.width - 126, c, x + C, y + h - C, w - 2 * C, C);   // top and bottom from clear of the holes\n"
         "  d(img.width - c, c, c, img.height - 2 * c, x + w - C, y + C, C, h - 2 * C);\n"
         "  ctx.save(); ctx.translate(x + C, 0); ctx.scale(-1, 1); d(img.width - c, c, c, img.height - 2 * c, 0, y + C, C, h - 2 * C); d(img.width - c, 0, c, c, 0, y, C, C); d(img.width - c, img.height - c, c, c, 0, y + h - C, C, C); ctx.restore();   // the plate's left edge has the portrait window in it: mirror its right edge\n"
         "  d(img.width - c, 0, c, c, x + w - C, y, C, C); d(img.width - c, img.height - c, c, c, x + w - C, y + h - C, C, C);\n"
         "  ctx.restore();\n"
         "}\n"
         "function bar(x, y, w, h, frac, col, back) {\n", 'hud panel')
for a in ["    pxPanel(12, ny, 220, 30);\n", "    pxPanel(12, ny, 220, 34);\n", "  pxPanel(W - 12 - plateW, 12, plateW, 74);\n",
          "  { const pb = pauseBtn(plateW); pxPanel(pb.x - pb.r, pb.y - pb.r, pb.r * 2, pb.r * 2);"]:
    s = swap(s, a, a.replace('pxPanel(', 'hudPanel('), 'hud panel ' + a.strip()[:30])


# ---------------------------------------------------------------- boss intro cards: Meshy portraits (tools/v65/bosscards.py)
s = swap(s, "function bossCardFor(w) {\n",
         "const BOSS_ART = { 'THE PARKIE': 'parkie', 'MASTER CONTROL': 'mc', 'DENISE': 'denise', 'LADY ADDICT': 'lady', 'BIG GARY': 'gary', 'BIG GAZ': 'gaz', 'DON VITO': 'mafioso',\n"
         "  'BIG TONY AND LITTLE NICKY': 'duo', 'IL CARABINIERE': 'carab', 'I FRATELLI': 'bros', 'THE TICKET INSPECTOR': 'inspector', 'LEWISHAM LENNY': 'lenny', 'THE JEWELLER': 'jeweller',\n"
         "  'THE FAR BANK': 'farbank', 'NOZZER': 'nozzer' };   // Version 65\n"
         "setTimeout(() => { for (const k in BOSS_ART) { bgImg('bosscard/' + BOSS_ART[k]); ASSET_BG.push('bosscard/' + BOSS_ART[k]); } }, 0);   // ASSET_BG is declared further down\n"
         "function bossCardFor(w) {\n", 'boss art map')
s = swap(s, "  c.spr.forEach((id, i) => drawCardSprite(id, 230 + (i - (n - 1) / 2) * gap, bandY + bandH - 12, sk));\n",
         "  const art = BOSS_ART[c.name] && bgImg('bosscard/' + BOSS_ART[c.name]);\n"
         "  if (art) {   // Version 65: the boss's painted portrait slams in, bursting up out of the band, with a flash as it lands\n"
         "    const slam = clamp((t - 0.12) / 0.2, 0, 1), k = 2 * (1.35 - 0.35 * easeOut(slam)), w = art.width * k, h = art.height * k;\n"
         "    ctx.save(); ctx.globalAlpha = Math.min(1, slam * 3); ctx.fillStyle = 'rgba(242,162,58,0.18)';\n"
         "    for (let i = 0; i < 9; i++) { const a = -Math.PI / 2 + (i - 4) * 0.28 + Math.sin(t * 3 + i) * 0.04; ctx.beginPath(); ctx.moveTo(230, bandY + bandH); ctx.lineTo(230 + Math.cos(a - 0.06) * 420, bandY + bandH + Math.sin(a - 0.06) * 420); ctx.lineTo(230 + Math.cos(a + 0.06) * 420, bandY + bandH + Math.sin(a + 0.06) * 420); ctx.fill(); }\n"
         "    ctx.imageSmoothingEnabled = false; ctx.drawImage(art, Math.round(230 - w / 2), Math.round(bandY + bandH - h), w, h);\n"
         "    if (slam >= 1 && t < 0.42) { ctx.globalAlpha = (0.42 - t) / 0.1; ctx.fillStyle = '#fff6dc'; ctx.fillRect(0, bandY, W, bandH); }\n"
         "    ctx.restore();\n"
         "    if (slam >= 1 && !c.slammed) { c.slammed = true; addShake(8); sfx('thud'); }\n"
         "  } else c.spr.forEach((id, i) => drawCardSprite(id, 230 + (i - (n - 1) / 2) * gap, bandY + bandH - 12, sk));\n", 'boss card art')


# ---------------------------------------------------------------- The Long Drive: the lake painted in Meshy (stages.json "golf")
s = swap(s, "const GOLF_TEE = 300, GOLF_YD = 4;",
         "const GOLF_BG = ['meshy/golf_0', 'meshy/golf_1', 'meshy/golf_2'];   // Version 65: the lake at golden hour, Pearcy's platform on the left\n"
         "setTimeout(() => { GOLF_BG.forEach(f => bgImg(f)); ASSET_BG.push(...GOLF_BG); }, 0);\n"
         "const GOLF_TEE = 300, GOLF_YD = 4;", 'golf files')
s = swap(s, "    const s = M.s, cx = s.camX;\n    pxSky(['#2a5a9a',",
         "    const s = M.s, cx = s.camX, mz = bgReady(GOLF_BG);\n"
         "    if (mz) { ctx.save(); ctx.imageSmoothingEnabled = false; GOLF_BG.forEach((f, i) => { const img = bgImg(f), x = snap2(i * 1024 - cx); if (x < W && x + img.width * 2 > 0) ctx.drawImage(img, x, 0, img.width * 2, img.height * 2); }); ctx.restore(); }\n"
         "    if (!mz) {\n    pxSky(['#2a5a9a',", 'golf painted lake')
s = swap(s, "    // distance markers: buoys every 50 yards, labelled in the HUD pass\n",
         "    }\n    ctx.save(); if (mz) ctx.translate(0, 20);   // on the painted lake Pearcy's platform, the water line and the buoys sit 20 lower\n"
         "    // distance markers: buoys every 50 yards, labelled in the HUD pass\n", 'golf old lake end')
s = swap(s, "    ctx.fillStyle = '#4a7a3a'; ctx.fillRect(snap2(-cx - 40), 430, 470, 120); ctx.fillStyle = '#5a8a46'; ctx.fillRect(snap2(-cx - 40), 430, 470, 6);\n    ctx.fillStyle = '#3a2a1a'; ctx.fillRect(snap2(-cx + 420), 430, 10, 120);\n",
         "    if (!mz) { ctx.fillStyle = '#4a7a3a'; ctx.fillRect(snap2(-cx - 40), 430, 470, 120); ctx.fillStyle = '#5a8a46'; ctx.fillRect(snap2(-cx - 40), 430, 470, 6);\n    ctx.fillStyle = '#3a2a1a'; ctx.fillRect(snap2(-cx + 420), 430, 10, 120); }\n", 'golf old bank')
s = swap(s, "ctx.fillRect(snap2(x + 4 + k * 20), 424 - k * 20, 6, 20 * (1 - k) + 4); }\n  },\n",
         "ctx.fillRect(snap2(x + 4 + k * 20), 424 - k * 20, 6, 20 * (1 - k) + 4); }\n    ctx.restore();\n  },\n", 'golf restore')
s = swap(s, "    for (let yd = 50; yd <= 500; yd += 50) { const x = GOLF_TEE + yd * GOLF_YD - cx; if (x > -20 && x < W + 20) { ctx.fillStyle = 'rgba(10,14,16,0.55)'; ctx.fillRect(x - 22, 392, 44, 18); ctx.fillStyle = '#efe6d2'; ctx.fillText(yd + ' yd', x, 401); } }",
         "    const gdy = bgReady(GOLF_BG) ? 20 : 0;\n"
         "    for (let yd = 50; yd <= 500; yd += 50) { const x = GOLF_TEE + yd * GOLF_YD - cx; if (x > -20 && x < W + 20) { ctx.fillStyle = 'rgba(10,14,16,0.55)'; ctx.fillRect(x - 22, 392 + gdy, 44, 18); ctx.fillStyle = '#efe6d2'; ctx.fillText(yd + ' yd', x, 401 + gdy); } }", 'golf yard labels')

# the swing meter's instruction sat on the yard labels: it goes inside the meter's panel, under the bar
s = swap(s, "      pubPanel(mx - 14, my - 18, mw + 28, 50);\n", "      pubPanel(mx - 14, my - 18, mw + 28, 62);   // Version 65: room for the words under the bar\n", 'golf meter panel')
s = swap(s, "'HIT ON THE WHITE LINE', W / 2, my - 34);", "'HIT ON THE WHITE LINE', W / 2, my + 30);", 'golf meter words')


open(PAGE, 'w', encoding='utf-8').write(s)
print('v65_build: web/index.html updated')
