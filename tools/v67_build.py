"""Version 67: calmer select screens (Tim, 30 October). Patches web/index.html and the title3d sources in place
(run from the repo root): python3 tools/v67_build.py. Safe to run again. It doesn't re-run the earlier build scripts
(title3d_build.py would undo Version 65's locked-lad fixes in the page).

- The lad's name, the stage title, the difficulty heading and the carry-on stage no longer sit on Meshy's comic
  bursts. They're plain pixel-font headings again, the lad's name in his own colour.
- The lad tiles along the bottom use the footer buttons' look (same font, size, spacing and capitals).
- The chapter tabs and the stage list use the same type.
- On a touch screen the footer hint is left out (it was cut off as "TAP A LAD. ..." and tapping is obvious); the
  keyboard hints on the stage and difficulty steps are shorter so they fit.
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, 'web', 'index.html')
CSS = os.path.join(ROOT, 'tools', 'title3d', 'title3d.css')
JS = os.path.join(ROOT, 'tools', 'title3d', 'title3d.js')
read = lambda p: open(p, encoding='utf-8').read()

SWAPS = [
    ('burst headings',
     "#t3-name,#t3-stitle,#t3-diff>.t3h,#t3-cstage{display:inline-block;justify-self:start;padding:calc(var(--t3u) * 5) calc(var(--t3u) * 14) calc(var(--t3u) * 4);margin-left:calc(var(--t3u) * -6);background:url(bg/comic/burst_o1.png) center/100% 100% no-repeat;image-rendering:pixelated;color:#fff6dc!important}\n"
     "#t3-stitle,#t3-diff>.t3h{background-image:url(bg/comic/burst_y1.png)}\n",
     "/* Version 67: plain headings again (Tim: the bursts were too busy) */\n#t3-name{font-size:calc(var(--t3u) * 18)}\n", 'css'),
    ('lad tiles',
     "#t3-roster button{font:700 max(calc(var(--t3m) * 8px),calc(var(--t3u) * 5)) var(--t3disp);letter-spacing:.04em;background:rgba(13,8,38,.7);border:1px solid transparent;padding:calc(var(--t3u) * 2) calc(var(--t3u) * 3);color:var(--t3grey)}",
     "#t3-roster button{font:800 max(calc(var(--t3m) * 8px),calc(var(--t3u) * 4.8)) var(--t3body)!important;letter-spacing:.12em;text-transform:uppercase;background:rgba(13,8,38,.7);border:1px solid var(--t3rule);padding:calc(var(--t3u) * 2.5) calc(var(--t3u) * 5);color:var(--t3cream)}   /* Version 67: the footer buttons' look */", 'css'),
    ('chapter tabs',
     "#t3-tabs button[aria-selected=\"true\"]{color:var(--t3gold);border-color:var(--t3gold)}\n",
     "#t3-tabs button[aria-selected=\"true\"]{color:var(--t3gold);border-color:var(--t3gold)}\n"
     "/* Version 67: chapter tabs and the stage list in the footer buttons' type, like the lad tiles */\n"
     "#t3-tabs button{font:800 max(calc(var(--t3m) * 8px),calc(var(--t3u) * 4.8)) var(--t3body)!important;letter-spacing:.12em;text-transform:uppercase}\n"
     "#t3-list button{font:800 max(calc(var(--t3m) * 9px),calc(var(--t3u) * 5.6)) var(--t3body)!important;letter-spacing:.1em;text-transform:uppercase}\n"
     "#t3-list button .n{font-size:max(calc(var(--t3m) * 8px),calc(var(--t3u) * 4.8))!important}\n", 'css'),
    ('empty hint',
     "#t3-hint{flex:1 1 auto;",
     "#t3-hint:empty{display:none}\n#t3-hint{flex:1 1 auto;", 'css'),
    ('touch hint',
     "      lad: pad ? 'Stick to choose · HIT to pick · BACK' : tch ? 'Tap a lad. Tap again to pick.' : '← → choose · J pick · Esc back',\n"
     "      stage: pad ? 'Stick for chapter · HIT to start here' : tch ? 'Tap a chapter, then a stage.' : '← → chapter · ↑ ↓ stage · J start here',\n"
     "      diff: pad ? 'Stick for difficulty · HIT to go' : tch ? 'Pick a difficulty, then go.' : '← → difficulty · F language · J go',\n"
     "      cont: pad ? 'HIT to carry on · JUMP for a new run' : tch ? 'Carry on, or start a new run.' : 'J carry on · K new run · Esc back',\n",
     "      // Version 67: no hint on a touch screen (the footer is full and it was cut off; tapping is obvious)\n"
     "      lad: pad ? 'Stick to choose · HIT to pick · BACK' : tch ? '' : '← → choose · J pick · Esc back',\n"
     "      stage: pad ? 'Stick for chapter · HIT to start here' : tch ? '' : '← → ↑ ↓ choose · J start',\n"
     "      diff: pad ? 'Stick for difficulty · HIT to go' : tch ? '' : '← → choose · J go · F language',\n"
     "      cont: pad ? 'HIT to carry on · JUMP for a new run' : tch ? '' : 'J carry on · K new run · Esc back',\n", 'js'),
]


def patch(path, kinds):
    s = read(path)
    for label, old, new, kind in SWAPS:
        if kind not in kinds or new in s:
            continue
        if s.count(old) != 1:
            sys.exit(f'v67_build: could not find the {label} in {os.path.relpath(path, ROOT)} (found {s.count(old)})')
        s = s.replace(old, new)
    open(path, 'w', encoding='utf-8').write(s)


patch(CSS, {'css'})
patch(JS, {'js'})
patch(PAGE, {'css', 'js'})
print('v67_build: web/index.html and tools/title3d updated')
