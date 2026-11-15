"""Version 85: recorded sound effects. python3 tools/v85_sfx_build.py (re-runnable; patches web/index.html in place).
Code: tools/v85/sfx.js, between `// V85 sfx start` and `// V85 sfx end`, straight after the old sfxOk. The takes live in
web/sfx (24 kHz mono WAV). They were made with PixelLab's create_sound_effect (prompts and ids in tools/v85/sfx_prompts.json),
then trimmed to start on the sound, faded out over 40 ms and levelled to just under full scale; loudness per kind is SFX_VOL.
Hooks: audioInit starts loading the takes, and sfx() tries a take before the synthesised sound."""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); PAGE = os.path.join(ROOT, 'web', 'index.html')
s = open(PAGE, encoding='utf-8').read()
start, end = '// V85 sfx start', '// V85 sfx end'
if start in s: a = s.index(start); b = s.index(end) + len(end) + 1; s = s[:a] + s[b:]
anchor = "  sfxLast[kind] = now; return true;\n}\n"
assert s.count(anchor) == 1
s = s.replace(anchor, anchor + start + '\n' + open(os.path.join(ROOT, 'tools', 'v85', 'sfx.js'), encoding='utf-8').read().rstrip('\n') + '\n' + end + '\n')
SWAPS = [
    ("function sfx(kind) { if (!actx || !settings.sound) return; try { if (sfxOk(kind)) (SFX[kind] || (() => {}))(); } catch (e) { /* audio is optional */ } }",
     "function sfx(kind) { if (!actx || !settings.sound) return; try { if (sfxOk(kind) && !sfxSample(kind)) (SFX[kind] || (() => {}))(); } catch (e) { /* audio is optional */ } }   // Version 85: a recorded take first"),
    ("    applySound();\n  } catch (e) { actx = null; }",
     "    applySound();\n    sfxLoad();   // Version 85: the recorded sound effects\n  } catch (e) { actx = null; }"),
    # batch 2
    ("    knockDown(t, dir, k.kb || 260);\n    addShake(big ? 6 : 3);\n",
     "    knockDown(t, dir, k.kb || 260); foeVoice(t, true);   // Version 85: a cry\n    addShake(big ? 6 : 3);\n"),
    ("  } else { t.state = 'hurt'; t.t = 0; t.vx = dir * (k.kb || 90); t.vy = 0; t.hurtN = (t.hurtN || 0) + 1; }",
     "  } else { t.state = 'hurt'; t.t = 0; t.vx = dir * (k.kb || 90); t.vy = 0; t.hurtN = (t.hurtN || 0) + 1; foeVoice(t, false); }"),
    ("  startAction(p, 'pickup', 0.16, null); sfx('pickup');", "  startAction(p, 'pickup', 0.16, null); sfx('wpick');   // Version 85"),
    ("popWord(p.x, p.y, 140, f.word, false); sfx('pickup');", "popWord(p.x, p.y, 140, f.word, false); sfx('eat');"),
    ("  const after = () => { mode = 'clear'; modeT = 0; };", "  const after = () => { mode = 'clear'; modeT = 0; sfx('cheer'); };   // Version 85: the crowd"),
    ("foes.push(b); S.bosses = [b]; musicSet(bossMusic()); showBanner(d.name", "foes.push(b); S.bosses = [b]; musicSet(bossMusic()); if (!FOE_FEMALE.has(b.kind)) sfx('roar'); showBanner(d.name"),
    ("const b = makeHB(w.boss); foes.push(b); S.bosses = [b]; musicSet(bossMusic());", "const b = makeHB(w.boss); foes.push(b); S.bosses = [b]; musicSet(bossMusic()); sfx('roar');"),
    # the title theme (PixelLab music, made into a loop: the intro plays once, then 39.102 s to 93.373 s repeats)
    ("  deepcover: { src: 'music/deep-cover.mp3', loop: 58.181814, fb: 'garage' },\n});",
     "  deepcover: { src: 'music/deep-cover.mp3', loop: 58.181814, fb: 'garage' },\n  title: { src: 'music/title-theme.mp3', from: 39.102, loop: 54.271, end: 93.6, fb: 'title' },   // Version 85: the title theme\n});"),
    ("    if (T.loop) { if (buf.duration > T.loop + 0.02) ls = MP3_DELAY; len = Math.min(T.loop, buf.duration - ls); }",
     "    if (T.from) { T.lead = buf.duration > T.end + 0.01 ? MP3_DELAY : 0; ls = T.from + T.lead; len = T.loop; }   // Version 85: an intro, then the loop\n    else if (T.loop) { if (buf.duration > T.loop + 0.02) ls = MP3_DELAY; len = Math.min(T.loop, buf.duration - ls); }"),
    ("    s.start(t, ls + off);\n", "    s.start(t, T.from && !trk.pos[key] ? T.lead : ls + off);\n"),
    ("  if (!actx || !mus.key || !settings.sound || actx.state !== 'running') return;",
     "  if (mode === 'title' && !mus.key) musicSet('title');   // Version 85: the title screen has its theme\n  if (!actx || !mus.key || !settings.sound || actx.state !== 'running') return;"),
]
for old, new in SWAPS:
    if new in s: continue
    assert s.count(old) == 1, old[:60]
    s = s.replace(old, new)
open(PAGE, 'w', encoding='utf-8').write(s); print('v85 sfx: patched')
