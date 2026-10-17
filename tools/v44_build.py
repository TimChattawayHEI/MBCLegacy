"""Version 44: the optimisation pass.

Patches web/index.html in place (run from the repo root, after tools/title3d_build.py):  python3 tools/v44_build.py
Safe to run again: each change is skipped if it is already there. Run it again after rebuilding the page from claude.ai.

What it does
- Memory: sprite sheets no longer get two full-size copies each (a white one for the hit flash, a red one for the
  Carp Diem rage and Duck and Cover backup). That was about 370 MB of canvases on a phone. The one frame being drawn
  is tinted on a small scratch canvas instead.
- Speed: the dithered sky bands and the fishery car park were redrawn a few thousand rectangles at a time, every
  frame. Both are drawn once into an image and reused.
- Loading: all the background art is fetched just after the title appears, and a stage waits (LOADING) until its
  art is in, so nothing is ever drawn half loaded. The next stage's music is fetched while its group chat plays.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, 'web', 'index.html')
read = lambda p: open(p, encoding='utf-8').read()


def swap(s, old, new, label):
    if new in s:
        return s
    if s.count(old) != 1:
        sys.exit(f'v44_build: could not find the {label} (found {s.count(old)} matches)')
    return s.replace(old, new)


s = read(PAGE)

# ---------------------------------------------------------------- memory: tint one cell at a time, no full-sheet copies
s = swap(s, """    sh = ladSheets[id] = { m, img: new Image(), ready: false, white: null };
    sh.img.onload = () => {
      sh.ready = true;
      // a pale copy for the white flash when a lad takes a hit
      try {
        const c = document.createElement('canvas'); c.width = sh.img.width; c.height = sh.img.height;
        const x = c.getContext('2d'); x.drawImage(sh.img, 0, 0);
        x.globalCompositeOperation = 'source-atop'; x.fillStyle = 'rgba(255,243,220,0.6)'; x.fillRect(0, 0, c.width, c.height);
        sh.white = c;
        // and a red one for Pearcy's Carp Diem rage
        const r = document.createElement('canvas'); r.width = c.width; r.height = c.height;
        const y = r.getContext('2d'); y.drawImage(sh.img, 0, 0);
        y.globalCompositeOperation = 'source-atop'; y.fillStyle = 'rgba(255,40,20,0.38)'; y.fillRect(0, 0, r.width, r.height);
        sh.red = r;
      } catch (e) { sh.white = null; sh.red = null; }
    };""", """    sh = ladSheets[id] = { m, img: new Image(), ready: false };
    // the white hit flash and the red rage are tinted one cell at a time by sprTint (Version 44), not kept as full copies
    sh.img.onload = () => { sh.ready = true; };""", 'sprite sheet loader')

s = swap(s, """Object.keys(SPRITE_META).forEach(ladSprite);""", """Object.keys(SPRITE_META).forEach(ladSprite);
// one cell of a sheet, tinted white (hit flash) or red (rage, backup lads), on a small reusable canvas (Version 44)
const SPR_TINT = { white: 'rgba(255,243,220,0.6)', red: 'rgba(255,40,20,0.38)' };
const sprTintCv = document.createElement('canvas'), sprTintCtx = sprTintCv.getContext('2d');
function sprTint(sh, sx, sy, cell, kind) {
  if (sprTintCv.width < cell || sprTintCv.height < cell) { sprTintCv.width = Math.max(sprTintCv.width, cell); sprTintCv.height = Math.max(sprTintCv.height, cell); }
  const x = sprTintCtx;
  x.globalCompositeOperation = 'source-over'; x.clearRect(0, 0, cell, cell);
  x.drawImage(sh.img, sx, sy, cell, cell, 0, 0, cell, cell);
  x.globalCompositeOperation = 'source-atop'; x.fillStyle = SPR_TINT[kind]; x.fillRect(0, 0, cell, cell);
  x.globalCompositeOperation = 'source-over';
  return sprTintCv;
}
function drawSprCell(sh, sx, sy, cell, kind, dx, dy, dw, dh) {
  if (kind) ctx.drawImage(sprTint(sh, sx, sy, cell, kind), 0, 0, cell, cell, dx, dy, dw, dh);
  else ctx.drawImage(sh.img, sx, sy, cell, cell, dx, dy, dw, dh);
}""", 'sprite tint helper')

s = swap(s, """  const src = e.flash > 0 && sh.white ? sh.white : (e.ally || (crazed && Math.floor(time * 10) % 2)) && sh.red ? sh.red : sh.img;
  ctx.drawImage(src, idx * m.cell, row[0] * m.cell, m.cell, m.cell, -m.ax * k, -m.ay * k, m.cell * k, m.cell * k);""",
         """  const tint = e.flash > 0 ? 'white' : (e.ally || (crazed && Math.floor(time * 10) % 2)) ? 'red' : null;
  drawSprCell(sh, idx * m.cell, row[0] * m.cell, m.cell, tint, -m.ax * k, -m.ay * k, m.cell * k, m.cell * k);""", 'lad draw tint')

s = swap(s, """  ctx.drawImage(sh.white || sh.img, idx * m.cell, row[0] * m.cell, m.cell, m.cell, -m.ax * K, -m.ay * K, m.cell * K, m.cell * K);""",
         """  drawSprCell(sh, idx * m.cell, row[0] * m.cell, m.cell, 'white', -m.ax * K, -m.ay * K, m.cell * K, m.cell * K);""", 'ghost glow tint')

# ---------------------------------------------------------------- speed: skies drawn once, then reused
s = swap(s, """function pxSky(cols, y0, y1) {
  const n = cols.length, bh = Math.floor((y1 - y0) / n / 2) * 2;
  for (let i = 0; i < n; i++) {
    const top = y0 + i * bh;
    ctx.fillStyle = cols[i]; ctx.fillRect(0, top, W, i === n - 1 ? y1 - top : bh);
    if (i) { ctx.fillStyle = cols[i - 1]; for (let x = 0; x < W; x += 4) { ctx.fillRect(x, top, 2, 2); ctx.fillRect(x + 2, top + 2, 2, 2); } }
  }
}""", """// a dithered sky, drawn once per set of colours at world-pixel size and reused every frame (Version 44)
const pxSkyCache = new Map();
function pxSky(cols, y0, y1) {
  const key = cols.join() + '|' + y0 + '|' + y1;
  let c = pxSkyCache.get(key);
  if (!c) {
    c = document.createElement('canvas'); c.width = W / 2; c.height = Math.max(1, Math.ceil((y1 - y0) / 2));
    const x = c.getContext('2d'), n = cols.length, bh = Math.floor((y1 - y0) / n / 2) * 2;
    x.scale(0.5, 0.5); x.translate(0, -y0);
    for (let i = 0; i < n; i++) {
      const top = y0 + i * bh;
      x.fillStyle = cols[i]; x.fillRect(0, top, W, i === n - 1 ? y1 - top : bh);
      if (i) { x.fillStyle = cols[i - 1]; for (let xx = 0; xx < W; xx += 4) { x.fillRect(xx, top, 2, 2); x.fillRect(xx + 2, top + 2, 2, 2); } }
    }
    pxSkyCache.set(key, c);
  }
  const sm = ctx.imageSmoothingEnabled; ctx.imageSmoothingEnabled = false;
  ctx.drawImage(c, 0, y0, W, c.height * 2); ctx.imageSmoothingEnabled = sm;
}""", 'sky')

# the fishery car park: the same drawing, done once into a strip, then slid along with the camera
CP_OLD = re.search(r"function fshCarPark\(\) \{\n.*?\n\}\n", s, re.S)
if 'function fshCarParkRaw(' not in s:
    if not CP_OLD:
        sys.exit('v44_build: could not find the fishery car park')
    raw = CP_OLD.group(0).replace('function fshCarPark() {', 'function fshCarParkRaw(camx, wmax) {')
    raw = raw.replace('cam.x', 'camx').replace('Math.min(W,', 'Math.min(wmax,')
    if 'cam.x' in raw or 'Math.min(wmax,' not in raw:
        sys.exit('v44_build: the fishery car park has changed shape')
    cached = raw + """// drawn once into a strip of world pixels (8 units of margin each side for the end posts) and reused (Version 44)
let fshCarParkCv = null;
function fshCarPark() {
  if (Math.round((1000 - cam.x) / 2) * 2 <= 0) return;
  if (!fshCarParkCv) {
    const c = document.createElement('canvas'); c.width = 508; c.height = Math.ceil((H - 248) / 2);
    const main = ctx; ctx = c.getContext('2d'); ctx.scale(0.5, 0.5); ctx.translate(0, -248);
    try { fshCarParkRaw(-8, 1016); } finally { ctx = main; }
    fshCarParkCv = c;
  }
  const sm = ctx.imageSmoothingEnabled; ctx.imageSmoothingEnabled = false;
  ctx.drawImage(fshCarParkCv, Math.round(-cam.x / 2) * 2 - 8, 248, fshCarParkCv.width * 2, fshCarParkCv.height * 2);
  ctx.imageSmoothingEnabled = sm;
}
"""
    s = s.replace(CP_OLD.group(0), cached)

# ---------------------------------------------------------------- loading: fetch the art early, and hold a stage until it is in
assets = []
for dp, _, fs in os.walk(os.path.join(ROOT, 'web', 'bg')):
    for f in sorted(fs):
        if f.endswith('.png'):
            assets.append(os.path.relpath(os.path.join(dp, f), os.path.join(ROOT, 'web', 'bg'))[:-4].replace(os.sep, '/'))
assets.sort()
ASSET_LINE = 'const ASSET_BG = ' + repr(assets).replace("'", '"') + ';   // every background image, listed by tools/v44_build.py'
s = re.sub(r'const ASSET_BG = \[.*?\];   // every background image, listed by tools/v44_build.py', lambda m: ASSET_LINE, s)
s = swap(s, """function startStage(key) {""", ASSET_LINE + """
// all the background art is fetched just after the title appears, so a stage never draws half loaded (Version 44)
function preloadArt() { for (const p of ASSET_BG) bgImg(p); }
setTimeout(preloadArt, 700);
function artPending() {
  for (const k in bgImgs) { const b = bgImgs[k]; if (!b.ready && !b.failed) return true; }
  for (const k in ladSheets) { const b = ladSheets[k]; if (!b.ready && !b.failed) return true; }
  return false;
}
let loadKey = null, loadT = 0;
function startStage(key) {
  // offline only: an online game must run the same frames on both phones, and its lobby leaves plenty of time to load
  if (!NET.on && artPending()) { preloadArt(); loadKey = key; loadT = 0; mode = 'loading'; modeT = 0; return; }
  startStageNow(key);
}
function updateLoading(dt) {
  loadT += dt;
  if (!artPending() || loadT > 10) { const k = loadKey; loadKey = null; startStageNow(k); }
}
function drawLoading() {
  ctx.fillStyle = '#0c1014'; ctx.fillRect(0, 0, W, H);
  if (modeT < 0.25) return;
  const dots = '...'.slice(0, 1 + Math.floor(modeT * 3) % 3);
  textOut('LOADING' + dots, W / 2 - 70, H / 2, '26px ' + DISPLAY, '#f2a23a', OUT, 5, 'left');
}
// the next stage's music is fetched (and decoded, once sound is on) while its group chat plays
function prefetchStageMusic(key) {
  const t = STAGES[key] && STAGES[key].music;
  if (!t || !TRACKS[t]) return;
  trackBytes(t);
  if (actx) trackBuffer(t);
}
function startStageNow(key) {""", 'stage start gate')

s = swap(s, """  if (mode === 'chat') { updateChat(dt); return true; }""",
         """  if (mode === 'chat') { updateChat(dt); return true; }
  if (mode === 'loading') { updateLoading(dt); return true; }""", 'loading step')
s = swap(s, """  if (mode === 'chat') { drawChat(); drawStatic(); return; }""",
         """  if (mode === 'chat') { drawChat(); drawStatic(); return; }
  if (mode === 'loading') { drawLoading(); return; }""", 'loading render')
s = swap(s, """  if (mode === 'select' && T3.live()) return T3.back();""",
         """  if (mode === 'select' && T3.live()) return T3.back();
  if (mode === 'loading') return true;   // the phone's back button never closes the app mid-load""", 'back button while loading')
s = swap(s, """  const go = () => openChat(CHATS[STAGES[first].intro], () => startStage(first), null, STAGES[first].era);""",
         """  prefetchStageMusic(first);
  const go = () => openChat(CHATS[STAGES[first].intro], () => startStage(first), null, STAGES[first].era);""", 'first stage music prefetch')
s = swap(s, """    openChat(CHATS[STAGES[nk].intro], () => startStage(nk),""",
         """    prefetchStageMusic(nk);
    openChat(CHATS[STAGES[nk].intro], () => startStage(nk),""", 'next stage music prefetch')

# ---------------------------------------------------------------- the old vector art goes
# Everything is PixelLab art now, and with the art preloaded these fallbacks never draw. Checked by a bot playing
# every stage with each fallback counted: only the moped warning arrow (kept, it is a UI cue) and Big Gaz's small
# head flames (now stepped pixels) ever ran.
class _M:
    def __init__(self, text): self.text = text
    def group(self, i=0): return self.text


def _prev(s, i):
    j = i - 1
    while j >= 0 and s[j] in ' \t\n': j -= 1
    return s[j] if j >= 0 else '('


def fn(s, name):
    """A top-level function's whole source, from 'function name(' to its closing brace and newline."""
    m = re.search(r'^function ' + name + r'\(', s, re.M)
    if not m:
        return None
    i, depth, q = s.index('{', m.end()), 0, None
    while i < len(s):
        c = s[i]
        if q:
            if c == '\\': i += 1
            elif c == q: q = None
        elif c in '\'"`': q = c
        elif c == '/' and s[i + 1] == '/': i = s.index('\n', i) - 1
        elif c == '/' and s[i + 1] == '*': i = s.index('*/', i) + 1
        elif c == '/' and _prev(s, i) in '(,=:[!&|?{};':   # a regex literal: skip to its closing slash
            i += 1; cls = False
            while s[i] != '/' or cls:
                if s[i] == '\\': i += 1
                elif s[i] == '[': cls = True
                elif s[i] == ']': cls = False
                i += 1
        elif c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                end = i + 1 + (1 if s[i + 1:i + 2] == '\n' else 0)
                return _M(s[m.start():end])
        i += 1
    sys.exit(f'v44_build: unbalanced function {name}')


def set_fn(s, name, new):
    m = fn(s, name)
    if not m:
        sys.exit(f'v44_build: could not find function {name}')
    return s if m.group(0) == new else s.replace(m.group(0), new)


for name in ['bgFishery', 'drawCarPark', 'drawCar', 'drawSmoker', 'drawProp', 'drawFisheryFore', 'bgNaval', 'drawRaft',
             'drawNavalFore', 'bgSocial', 'drawFruit', 'bgRamsden', 'drawRamsdenFore', 'drawShop', 'bgOrpington', 'bgSoundz',
             'drawBird', 'punchExt']:
    m = fn(s, name)
    if m:
        s = s.replace(m.group(0), '')

s = re.sub(r"\{ if \(!(bg\w+Pixel)\(\)\) bg\w+\(\); \}", r"\1();", s)
s = s.replace("else { if (!bgRamsdenPixel()) bgRamsden(); }", "else bgRamsdenPixel();")
for fore, files in [('Fishery', 'FSH_FILES'), ('Naval', 'NAV_FILES'), ('Ramsden', 'RAM_FILES')]:
    s = s.replace(f"{{ if (bgReady({files})) draw{fore}ForePixel(); else draw{fore}Fore(); }}", f"{{ if (bgReady({files})) draw{fore}ForePixel(); }}")
s = s.replace("if (!drawBirdSprite(e, sx, e.y)) drawBird(e, sx, e.y);", "drawBirdSprite(e, sx, e.y);")
s = s.replace("const img = bgImg(SOC + 'fruit'); if (!img) return drawFruit(fm);", "const img = bgImg(SOC + 'fruit'); if (!img) return;")

m = fn(s, 'drawHuman')
first = m.group(0).split('\n')[:2]
if not first[1].strip().startswith('{ const sid ='):
    sys.exit('v44_build: drawHuman has changed shape')
s = set_fn(s, 'drawHuman', first[0] + '\n' + first[1] + '\n}\n')

m = fn(s, 'drawFish')
if '  const by = -58;' in m.group(0):
    s = set_fn(s, 'drawFish', m.group(0).split('  const by = -58;')[0] + '  ctx.restore();\n}\n')

s = set_fn(s, 'drawShot', """function drawShot(sh) {
  if (drawShotPixel(sh)) return;
  if (sh.kind !== 'wthrow') return;
  const x = sh.x - cam.x, y = sh.y - sh.z;
  shadow(x, sh.y, 10, sh.z);
  ctx.save(); ctx.translate(x, y); ctx.rotate(sh.t * 18 * sh.face); drawWeapon(sh.w, -WEAPONS[sh.w].len / 2, 0, 0, 1); ctx.restore();
}
""")
# a kicked football flies as the football sprite
s = swap(s, "const SHOT_SPR = { dart: 1,", "const SHOT_SPR = { ball: 1, dart: 1,", 'shot sprite list')
s = swap(s, "  const img = bgImg('shots/' + sh.kind); if (!img) return false;\n  const x = sh.x - cam.x, y = sh.y - sh.z;",
         "  const img = bgImg(sh.kind === 'ball' ? 'weapons/ball' : 'shots/' + sh.kind); if (!img) return false;\n  const x = sh.x - cam.x, y = sh.y - sh.z;", 'football shot image')
s = swap(s, "  if (sh.kind === 'vinyl') rot = Math.round((sh.t * 16 + (sh.spin || 0)) * 2) / 2;",
         "  if (sh.kind === 'ball') rot = Math.round((sh.spin || 0) * 2) / 2;\n  else if (sh.kind === 'vinyl') rot = Math.round((sh.t * 16 + (sh.spin || 0)) * 2) / 2;", 'football spin')

m = fn(s, 'drawMoped')
if 'drawHuman(rider' in m.group(0):
    head, rest = m.group(0).split('  shadow(x, y, 46, 0);', 1)
    s = set_fn(s, 'drawMoped', head.rstrip('\n') + '\n}\n')

s = set_fn(s, 'drawTree', "function drawTree(tr) { drawTreePixel(tr); }\n")
s = s.replace("if (tr.star) { const x = tr.x - cam.x; circle(x + 20, FT - 250, 10); fillOut('#f8f8f4', 2); ctx.fillStyle = OUT; circle(x + 20, FT - 250, 3); ctx.fill();",
              "if (tr.star) { const x = tr.x - cam.x; { const bi = bgImg('weapons/ball'); if (bi) drawSpr(bi, x + 20, FT - 250, 0, 1); }")
s = set_fn(s, 'drawFalling', "function drawFalling(h) { drawFallingPixel(h); }\n")
s = set_fn(s, 'drawBBQ', "function drawBBQ() { drawBBQPixel(); }\n")
s = set_fn(s, 'drawWeapon', """function drawWeapon(k, x, y, ang, sc) {
  const w = WEAPONS[k]; if (!w) return;
  ctx.save(); ctx.translate(x, y); ctx.rotate(ang); ctx.scale(sc || 1, sc || 1);
  drawWeaponSprite(k);
  ctx.restore();
}
""")
# a weapon with no sprite of its own (the Parkie's litter picker is part of his art) never lands on the floor
s = swap(s, "  if (f.weapon) { dropItemWeapon(f.weapon, f.x, f.y); return; }",
         "  if (f.weapon) { if (WSPR[f.weapon]) dropItemWeapon(f.weapon, f.x, f.y); return; }", 'foe weapon drop')

m = fn(s, 'drawItem')
src = m.group(0)
src = re.sub(r"    if \(!drawItemSprite\('oneup', x, by \+ 20\)\) \{\n.*?\n    \}\n", "    drawItemSprite('oneup', x, by + 20);\n", src, flags=re.S)
src = re.sub(r"  if \(drawItemSprite\(it\.f, x, yy \+ 10\)\) return;\n  switch \(it\.f\) \{\n.*?\n  \}\n\}\n", "  drawItemSprite(it.f, x, yy + 10);\n}\n", src, flags=re.S)
s = set_fn(s, 'drawItem', src)
if 'switch (it.f)' in fn(s, 'drawItem').group(0):
    sys.exit('v44_build: drawItem has changed shape')

s = set_fn(s, 'drawBreakable', """function drawBreakable(b) {
  if (b.tx) { drawTransmitter(b); return; }
  const x = b.x - cam.x + (b.flash > 0 ? rand(-2, 2) : 0), y = b.y;
  if (x < -60 || x > W + 60) return;
  shadow(x, y, 26, 0);
  drawBinSprite(x, y, b.flash > 0, b.type === 'bin' ? null : b.type);
  if (b.type === 'bin' && ST && ST.bg === 'ramsden') drawFlame(x, y - 70, 16, b.x);
}
""")

s = set_fn(s, 'drawFlame', """function drawFlame(x, y, sz, seed) {
  if (sz >= 12 && drawFireSprite(x, y + 2, seed)) return;
  // small flames (Big Gaz's head) as stepped tongues on the pixel grid (Version 44)
  for (let i = 0; i < 3; i++) {
    const h = sz * (1.4 + Math.sin(time * 9 + seed + i * 2) * 0.35), w = sz * (0.7 - i * 0.15), tip = Math.sin(time * 7 + seed) * 3;
    ctx.fillStyle = ['#e2471c', '#f28a1c', '#ffd04a'][i];
    for (let r = 0; r < h; r += 2) {
      const u = r / h, hw = w * Math.pow(1 - u, 0.8), cx = x + tip * u;
      const a = Math.round((cx - hw) / 2) * 2, b = Math.round((cx + hw) / 2) * 2;
      if (b > a) ctx.fillRect(a, Math.round((y - r) / 2) * 2 - 2, b - a, 2);
    }
  }
}
""")

# the old fishery palette only fed the vector background
m = re.search(r"^const PAL = \{\n(?:  \w+: \{.*\},?\n)+\};\n", s, re.M)
if m and len(re.findall(r'(?<![\w.])PAL\b', s)) == 1:
    s = s.replace(m.group(0), '')

# nothing left may still call a removed function
for name in ['bgFishery', 'drawCarPark', 'drawCar', 'drawSmoker', 'drawProp', 'drawFisheryFore', 'bgNaval', 'drawRaft',
             'drawNavalFore', 'bgSocial', 'drawFruit', 'bgRamsden', 'drawRamsdenFore', 'drawShop', 'bgOrpington', 'bgSoundz',
             'drawBird', 'punchExt']:
    if re.search(r'(?<![\w.])' + name + r'\(', s):
        sys.exit(f'v44_build: {name} is gone but still called')

open(PAGE, 'w', encoding='utf-8').write(s)
print('v44_build: web/index.html updated')
