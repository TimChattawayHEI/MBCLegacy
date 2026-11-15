"""Version 85: the bosses talk. python3 tools/v85_bosstalk_build.py (re-runnable; patches web/index.html in place).
Art: tools/v85/bosstalk_src/<id>_talk.png (made by tools/v85/bossmouths.py from PixelLab's talking GIFs, also kept there)
copied to web/bg/bosscard. Sounds: tools/v85/bosstalk_src/taunt_<id>.wav (PixelLab sound effects, trimmed, limited and
at 24 kHz mono) copied to web/sfx; their volumes are taunt_vol.json. Code: tools/v85/bosstalk.js between
`// V85 bosstalk start` and `// V85 bosstalk end`, after the talking portraits."""
import json, os, shutil
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); PAGE = os.path.join(ROOT, 'web', 'index.html')
SRC = os.path.join(ROOT, 'tools', 'v85', 'bosstalk_src')
for f in sorted(os.listdir(SRC)):
    if f.endswith('_talk.png'): shutil.copyfile(os.path.join(SRC, f), os.path.join(ROOT, 'web', 'bg', 'bosscard', f))
    if f.startswith('taunt_') and f.endswith('.wav'): shutil.copyfile(os.path.join(SRC, f), os.path.join(ROOT, 'web', 'sfx', f))
vol = json.load(open(os.path.join(SRC, 'taunt_vol.json')))
s = open(PAGE, encoding='utf-8').read()
start, end = '// V85 bosstalk start', '// V85 bosstalk end'
if start in s: a = s.index(start); b = s.index(end) + len(end) + 1; s = s[:a] + s[b:]
js = open(os.path.join(ROOT, 'tools', 'v85', 'bosstalk.js'), encoding='utf-8').read().replace('/*TAUNT_VOL*/{}/*END*/', json.dumps(vol, separators=(',', ':')))
anchor = '// V85 talk end\n'
assert s.count(anchor) == 1
s = s.replace(anchor, anchor + start + '\n' + js.rstrip('\n') + '\n' + end + '\n')
SWAPS = [
    # the card's mouth
    ("    ctx.imageSmoothingEnabled = false; ctx.drawImage(art, Math.round(230 - w / 2), Math.round(bandY + bandH - h), w, h);",
     "    ctx.imageSmoothingEnabled = false; const tf = cardTalkFrame(c, art);   // Version 85: the boss talks\n"
     "    if (tf) ctx.drawImage(tf.strip, tf.sx, 0, art.width, art.height, Math.round(230 - w / 2), Math.round(bandY + bandH - h), w, h);\n"
     "    else ctx.drawImage(art, Math.round(230 - w / 2), Math.round(bandY + bandH - h), w, h);"),
    # the boss's own sound as the card lands
    ("    if (slam >= 1 && !c.slammed) { c.slammed = true; addShake(8); sfx('thud'); }",
     "    if (slam >= 1 && !c.slammed) { c.slammed = true; addShake(8); sfx('thud'); tauntPlay(c); }"),
    # the generic roar waits to see if the card has the boss's own sound
    ("musicSet(bossMusic()); if (!FOE_FEMALE.has(b.kind)) sfx('roar'); showBanner(d.name",
     "musicSet(bossMusic()); if (!FOE_FEMALE.has(b.kind)) bossRoar(); showBanner(d.name"),
    ("const b = makeHB(w.boss); foes.push(b); S.bosses = [b]; musicSet(bossMusic()); sfx('roar');",
     "const b = makeHB(w.boss); foes.push(b); S.bosses = [b]; musicSet(bossMusic()); bossRoar();"),
]
for old, new in SWAPS:
    if new in s: continue
    assert s.count(old) == 1, old[:80]
    s = s.replace(old, new)
open(PAGE, 'w', encoding='utf-8').write(s); print('v85 bosstalk: patched,', len(vol), 'bosses')
