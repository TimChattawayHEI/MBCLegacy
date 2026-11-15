"""Version 85: music for the moments and the pub. python3 tools/v85_stings_build.py (re-runnable; patches web/index.html).
Code: tools/v85/stings.js between `// V85 stings start` and `// V85 stings end`, at the very end of the game script (after
boardInit), so the mini-games, the Snake cabinet and Kebab Siege exist. Files: web/music/v85/sting_*.mp3 and the eight
loops (pub, pubgames, pens, kiss, awake, golf, snake, kebab), whose loop points are in tools/v85/music.json (built by
tools/v85_music_build.py). Run tools/v85_music_build.py first.
Hooks: a stage clear, the last boss down, game over, ON THE TAB and a chapter's title page play their sting; the pub
plays its own track."""
import os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); PAGE = os.path.join(ROOT, 'web', 'index.html')
subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'v85_music_build.py')], check=True)
s = open(PAGE, encoding='utf-8').read()
start, end = '// V85 stings start', '// V85 stings end'
if start in s: a = s.index(start); b = s.index(end) + len(end) + 1; s = s[:a] + s[b:]
js = open(os.path.join(ROOT, 'tools', 'v85', 'stings.js'), encoding='utf-8').read()
anchor = 'boardInit();\n'
assert s.count(anchor) == 1
s = s.replace(anchor, anchor + start + '\n' + js.rstrip('\n') + '\n' + end + '\n')
SWAPS = [
    # the last boss down
    ("  musicSet(null); sfx('heavy'); sfx('boom');\n  spark(b.x, b.y,",
     "  musicSet(null); sfx('heavy'); sfx('boom'); stingPlay('bossdown');   // Version 85\n  spark(b.x, b.y,"),
    # a stage cleared (not straight over the boss sting)
    ("  musicSet(null); sfx('life');\n  const after = () =>",
     "  musicSet(null); sfx('life'); if (!stingRecent('bossdown', 5)) stingPlay('clear');   // Version 85\n  const after = () =>"),
    # game over
    ("mode = 'over'; modeT = 0; musicSet(null); showBanner('BLANKED'",
     "mode = 'over'; modeT = 0; musicSet(null); stingPlay('gameover'); showBanner('BLANKED'"),
    # on the tab: the sting, then the stage's music once it's done
    ("  sfx('life'); buzz(60);\n  musicSet(CONT.music || ST.music || null, true);\n}",
     "  sfx('life'); buzz(60);\n  const back = CONT.music || ST.music || null; musicSet(null); stingPlay('tab');   // Version 85\n"
     "  setTimeout0(() => { if (mode === 'play' && !mus.key) musicSet(back, true); }, 3.4);\n}"),
    # a chapter's title page
    ("  mode = 'comic'; modeT = 0; banner = null; sfx('page');\n}",
     "  mode = 'comic'; modeT = 0; banner = null; sfx('page');\n  if (/^CHAPTER /.test(P.title || '') || id === 'p2001') { musicSet(null); stingPlay('chapter'); }   // Version 85\n}"),
    # the pub's own music
    ("  cam.x = 0; mode = 'pub'; modeT = 0; banner = null; musicSet('social');",
     "  cam.x = 0; mode = 'pub'; modeT = 0; banner = null; musicSet('pub');   // Version 85: its own track"),
    ("openMini(o.id, 'pub', () => { mode = 'pub'; modeT = 0; musicSet('social'); });",
     "openMini(o.id, 'pub', () => { mode = 'pub'; modeT = 0; musicSet('pub'); });"),
    # load the stings with the sound effects
    ("    sfxLoad();   // Version 85: the recorded sound effects\n",
     "    sfxLoad();   // Version 85: the recorded sound effects\n    stingsPreload();   // and the music stings\n"),
    # a new track stops a sting that's still going
    ("function musicSet(key, keepPos) {\n  if (mus.key === key) return;\n",
     "function musicSet(key, keepPos) {\n  if (mus.key === key) return;\n  if (key) stingStop();   // Version 85\n"),
]
for old, new in SWAPS:
    if new in s: continue
    assert s.count(old) == 1, old[:80]
    s = s.replace(old, new)
open(PAGE, 'w', encoding='utf-8').write(s); print('v85 stings: patched')
