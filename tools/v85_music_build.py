"""Version 85: the new soundtrack. python3 tools/v85_music_build.py (re-runnable; patches web/index.html in place).
Code: tools/v85/music.js between `// V85 music start` and `// V85 music end`, after the talking portraits; NEW_MUSIC is filled
from tools/v85/music.json (per key: loop start, loop end, file length, volume, and for Atlantis the tempo and first beat).
Files: web/music/v85/<key>.mp3 (PixelLab music, made into loops; 128k MP3, cut at the loop end).
Hooks: trackStop and trackStart remember where an intro-then-loop track was in its file; orpBeatPhase uses the track's own
tempo and first beat when it has them."""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); PAGE = os.path.join(ROOT, 'web', 'index.html')
s = open(PAGE, encoding='utf-8').read()
start, end = '// V85 music start', '// V85 music end'
if start in s: a = s.index(start); b = s.index(end) + len(end) + 1; s = s[:a] + s[b:]
data = json.load(open(os.path.join(ROOT, 'tools', 'v85', 'music.json')))
js = open(os.path.join(ROOT, 'tools', 'v85', 'music.js'), encoding='utf-8').read()
js = js.replace('/*NEW_MUSIC*/{}/*END*/', json.dumps({k: v for k, v in data.items() if not k.startswith('_')}, separators=(',', ':')))
anchor = '// V85 talk end\n'
assert s.count(anchor) == 1
s = s.replace(anchor, anchor + start + '\n' + js.rstrip('\n') + '\n' + end + '\n')
SWAPS = [
    ("return r.arrayBuffer(); }).catch(() => { T.failed = true; return null; });",
     "return r.arrayBuffer(); }).catch(() => { if (T.old && TRACKS[key] === T) { TRACKS[key] = T.old; delete trk.bytes[key]; return trackBytes(key); } T.failed = true; return null; });   // Version 85: a new track that won't load falls back to the old one"),
    ("    try { if (trk.len) trk.pos[trk.key] = ((actx.currentTime - trk.t0) % trk.len + trk.len) % trk.len; trk.src.stop(); } catch (e) { /* already stopped */ }",
     "    try { const T = TRACKS[trk.key], fp = T && T.from ? trackFilePos() : null;   // Version 85: an intro-then-loop track remembers its place in the loop\n"
     "      if (T && T.from) trk.pos[trk.key] = fp != null && fp >= T.from ? fp - T.from : 0; else if (trk.len) trk.pos[trk.key] = ((actx.currentTime - trk.t0) % trk.len + trk.len) % trk.len; trk.src.stop(); } catch (e) { /* already stopped */ }"),
    ("    s.start(t, T.from && !trk.pos[key] ? T.lead : ls + off);\n    trk.src = s; trk.key = key; trk.len = len; trk.t0 = t - off;",
     "    s.start(t, T.from && !trk.pos[key] ? T.lead : ls + off);\n    trk.src = s; trk.key = key; trk.len = len; trk.t0 = t - (T.from && trk.pos[key] ? T.from + off : off);"),
    ("  if (actx && trk.src && trk.key === mus.key && mus.key === ST.music) {\n    const lat",
     "  if (actx && trk.src && trk.key === mus.key && mus.key === ST.music && TRACKS[trk.key].bpm) {   // Version 85: the new track's own tempo and first beat\n"
     "    const T = TRACKS[trk.key], fp = trackFilePos(), bp = 60 / T.bpm; if (fp != null) return ((((fp - T.beat0) % bp) + bp) % bp) / bp;\n  }\n"
     "  if (actx && trk.src && trk.key === mus.key && mus.key === ST.music) {\n    const lat"),
]
for old, new in SWAPS:
    if new in s: continue
    assert s.count(old) == 1, old[:70]
    s = s.replace(old, new)
open(PAGE, 'w', encoding='utf-8').write(s); print('v85 music: patched', len(data) - 1, 'tracks')
