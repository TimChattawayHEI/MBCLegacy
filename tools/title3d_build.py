"""Version 42: the 3D title and select screens, and starting a run at any stage.

Patches web/index.html in place (run from the repo root):  python3 tools/title3d_build.py
Safe to run again: each change is skipped if it is already there.

What it does
- Any stage can start a run. routeFrom() takes a stage key ('divebar') as well as a chapter ('elba').
  A stage started directly keeps its place in the difficulty ramp, so stage 5 is as tough as it is
  when you reach it from the start of Elba.
- The 3D title and select (tools/title3d/*) go into the page. The game's step(), render() and the app's
  back button hand over to it while it is live; if three.js or WebGL is missing it never goes live and
  the old 2D title and select carry on.
- three.js comes from web/vendor/three.module.min.js (the app) or jsDelivr (claude.ai, where the vendor file is not published).
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, 'web', 'index.html')
HERE = os.path.join(ROOT, 'tools', 'title3d')
read = lambda p: open(p, encoding='utf-8').read()


def swap(s, old, new, label):
    if new in s:
        return s
    if s.count(old) != 1:
        sys.exit(f'title3d_build: could not find the {label} (found {s.count(old)} matches)')
    return s.replace(old, new)


def block(s, start, end, content, anchor, label, before=True):
    """Put content between start/end markers, replacing an older copy, else insert it at the anchor."""
    full = start + '\n' + content.rstrip('\n') + '\n' + end
    if start in s:
        return re.sub(re.escape(start) + r'.*?' + re.escape(end), lambda m: full, s, count=1, flags=re.S)
    if s.count(anchor) != 1:
        sys.exit(f'title3d_build: could not find where to put the {label}')
    return s.replace(anchor, (full + '\n' + anchor) if before else (anchor + '\n' + full))


s = read(PAGE)

# ---------------------------------------------------------------- start a run at any stage
s = swap(s, """function routeFrom(start) {
  if (start === 'ramsden') return ['ramsden'];""", """// a chapter ('elba') or any stage ('divebar') can start a run (Version 42)
function chapterOf(key) { const i = ROUTE.indexOf(key); return i < 0 ? null : i >= ROUTE.indexOf('arrival') ? 'carpdiem' : i >= ROUTE.indexOf('airport') ? 'elba' : '1999'; }
// how many stages a mid-chapter start skips, so that stage keeps its place in the difficulty ramp
function routeDepth(start) { if (!ROUTE.includes(start)) return 0; const full = routeFrom(chapterOf(start)); return Math.max(0, full.indexOf(start)); }
function startLabel(start) { return ({ elba: 'ELBA 2002', carpdiem: 'CARP DIEM', ramsden: 'RAMSDEN' })[start] || (STAGES[start] && ROUTE.includes(start) ? 'STAGE ' + STAGES[start].n : '1999'); }
function routeFrom(start) {
  if (start === 'ramsden') return ['ramsden'];
  if (ROUTE.includes(start)) { const full = routeFrom(chapterOf(start)); return full.slice(Math.max(0, full.indexOf(start))); }""", 'route builder')

s = swap(s, """  run = { ci, c, route: routeFrom(start), idx: 0,""",
         """  run = { ci, c, route: routeFrom(start), off: routeDepth(start), vroute: ROUTE.includes(start) ? routeFrom(chapterOf(start)) : null, idx: 0,""",
         'run setup')

s = swap(s, """  if (!run || !run.route || run.route.length <= 2) return base;
  const i = run.idx || 0, key = base.label + i + (netCoop() ? 'c' : '');""",
         """  const vr = run && (run.vroute || run.route);
  if (!run || !vr || vr.length <= 2) return base;
  const i = (run.idx || 0) + (run.off || 0), key = base.label + i + vr[0] + (netCoop() ? 'c' : '');""",
         'difficulty ramp')
s = swap(s, """    const ri = run.route.indexOf('road'), deep""", """    const ri = vr.indexOf('road'), deep""", 'difficulty depth')

s = swap(s, """label: ({ elba: 'ELBA 2002', carpdiem: 'CARP DIEM', ramsden: 'RAMSDEN' }[startAt] || '1999'), key: 'R' }""",
         """label: startLabel(startAt), key: 'R' }""", 'select screen start label')
s = swap(s, """sl = { elba: 'ELBA 2002', carpdiem: 'CARP DIEM', ramsden: 'RAMSDEN' }[h.start] || '1999';""",
         """sl = startLabel(h.start);""", 'lobby start label')

# ---------------------------------------------------------------- hand title and select to the 3D screens while they are live
s = swap(s, """  if (mode === 'title') { updateTitle(); return true; }
  if (mode === 'select') { updateSelect(); return true; }""",
         """  if (mode === 'title') { if (T3.live()) T3.input(); else updateTitle(); return true; }
  if (mode === 'select') { if (T3.live()) T3.input(); else updateSelect(); return true; }""", 'step hooks')
s = swap(s, """  if (mode === 'title') { drawTitleScreen(); return; }
  if (mode === 'select') { drawSelect(); drawBanner(); return; }""",
         """  if (mode === 'title') { if (!T3.live()) drawTitleScreen(); return; }
  if (mode === 'select') { if (!T3.live()) { drawSelect(); drawBanner(); } return; }""", 'render hooks')
s = swap(s, """window.__appBack = () => {
  if (NET.on) { netPressed.add('pause'); return true; }""", """window.__appBack = () => {
  if (NET.on) { netPressed.add('pause'); return true; }
  if (mode === 'select' && T3.live()) return T3.back();""", 'app back button')

s = block(s, '/* T3 css start */', '/* T3 css end */', read(os.path.join(HERE, 'title3d.css')),
          """</style>\n\n<div class="wrap">""", 'styles')
s = block(s, '<!-- T3 html start -->', '<!-- T3 html end -->', read(os.path.join(HERE, 'title3d.html')),
          """    <canvas id="game" width="960" height="540" tabindex="0" aria-label="MBC Legacies beat 'em up game"></canvas>""", 'screen layer', before=False)
s = block(s, '// T3 js start', '// T3 js end', read(os.path.join(HERE, 'title3d.js')), """requestAnimationFrame(frame);\n\nconst fsBtn""", 'script')

open(PAGE, 'w', encoding='utf-8').write(s)
print('title3d_build: web/index.html updated')
