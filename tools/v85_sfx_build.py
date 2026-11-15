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
]
for old, new in SWAPS:
    if new in s: continue
    assert s.count(old) == 1, old[:60]
    s = s.replace(old, new)
open(PAGE, 'w', encoding='utf-8').write(s); print('v85 sfx: patched')
