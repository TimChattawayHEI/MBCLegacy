"""Version 67: calmer select screens and golf yard boards (Tim, 30 October). Patches web/index.html and the title3d sources in place
(run from the repo root): python3 tools/v67_build.py. Safe to run again. It doesn't re-run the earlier build scripts
(title3d_build.py would undo Version 65's locked-lad fixes in the page).

- The lad's name, the stage title, the difficulty heading and the carry-on stage no longer sit on Meshy's comic
  bursts. They're plain pixel-font headings again, the lad's name in his own colour.
- The lad tiles along the bottom use the footer buttons' look (same font, size, spacing and capitals).
- The chapter tabs and the stage list use the same type.
- The Long Drive's yard markers are the fishery's Meshy peg boards standing in the lake, with the distance painted on
  the board (every 100 yards in red), instead of little code-drawn floats under grey labels.
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
    ('golf markers',
     "    // distance markers: buoys every 50 yards, labelled in the HUD pass\n"
     "    for (let yd = 50; yd <= 500; yd += 50) { const x = snap2(GOLF_TEE + yd * GOLF_YD - cx); if (x < -20 || x > W + 20) continue; ctx.fillStyle = OUT; ctx.fillRect(x - 6, 418, 12, 18); ctx.fillStyle = yd % 100 ? '#efe6d2' : '#d84a3a'; ctx.fillRect(x - 4, 420, 8, 14); ctx.fillStyle = '#d84a3a'; ctx.fillRect(x - 4, 420, 8, 4); }\n",
     "    // distance markers every 50 yards (Version 67): the fishery's peg board standing in the lake, its post going into the\n"
     "    // water with a ripple; the distance is written on the board in the HUD pass (sharp text)\n"
     "    const golfPeg = bgImg('set/peg');\n"
     "    for (let yd = 50; yd <= 500; yd += 50) {\n"
     "      const x = snap2(GOLF_TEE + yd * GOLF_YD - cx); if (x < -40 || x > W + 40) continue;\n"
     "      if (golfPeg) { ctx.save(); ctx.imageSmoothingEnabled = false; ctx.drawImage(golfPeg, 0, 0, 24, 37, x - 24, GOLF_PEG_Y - 74, 48, 74); ctx.restore(); }\n"
     "      else { ctx.fillStyle = OUT; ctx.fillRect(x - 6, 418, 12, 18); ctx.fillStyle = '#efe6d2'; ctx.fillRect(x - 4, 420, 8, 14); }\n"
     "      const rw = 22 + Math.round(Math.sin(time * 2 + yd) * 3) * 2;\n"
     "      ctx.fillStyle = 'rgba(255,240,205,0.6)'; ctx.fillRect(x - rw / 2, GOLF_PEG_Y - 2, rw, 2); ctx.fillStyle = 'rgba(60,36,18,0.28)'; ctx.fillRect(x - 6, GOLF_PEG_Y, 12, 8);\n"
     "    }\n", 'page'),
    ('golf marker labels',
     "    for (let yd = 50; yd <= 500; yd += 50) { const x = GOLF_TEE + yd * GOLF_YD - cx; if (x > -20 && x < W + 20) { ctx.fillStyle = 'rgba(10,14,16,0.55)'; ctx.fillRect(x - 22, 392 + gdy, 44, 18); ctx.fillStyle = '#efe6d2'; ctx.fillText(yd + ' yd', x, 401 + gdy); } }",
     "    // Version 67: the distance on each peg board (the board is 40 units square, its middle 48 above the waterline)\n"
     "    for (let yd = 50; yd <= 500; yd += 50) { const x = snap2(GOLF_TEE + yd * GOLF_YD - cx); if (x > -40 && x < W + 40 && bgImg('set/peg')) {\n"
     "      const by = GOLF_PEG_Y - 48 + gdy; ctx.font = '17px ' + DISPLAY; ctx.fillStyle = yd % 100 ? '#1f2c3c' : '#b8322a'; ctx.fillText(String(yd), x, by - 3);\n"
     "      ctx.font = '800 8px ' + BODY; ctx.fillStyle = '#4a5462'; ctx.fillText('YARDS', x, by + 11); } }", 'page'),
    ('golf peg height',
     "const GOLF_TEE = 300, GOLF_YD = 4;",
     "const GOLF_TEE = 300, GOLF_YD = 4, GOLF_PEG_Y = 440;   // Version 67: the waterline the yard boards stand in", 'page'),
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
patch(PAGE, {'css', 'js', 'page'})
print('v67_build: web/index.html and tools/title3d updated')
