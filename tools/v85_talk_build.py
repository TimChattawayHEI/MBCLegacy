"""Version 85: talking portraits. python3 tools/v85_talk_build.py (re-runnable; patches web/index.html in place).
Code: tools/v85/talk.js between `// V85 talk start` and `// V85 talk end`, after the livelier backgrounds. Art: tools/v85/talk_src
(<id>_talk.png, five 48x48 faces) copied to web/bg/portraits; tools/v85/mouths.py made them from PixelLab's talking GIFs.
Hooks: drawPortrait takes a mouth frame; the newest message in the group chat talks; speech bubbles get the speaker's face."""
import os, shutil
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); PAGE = os.path.join(ROOT, 'web', 'index.html')
SRC = os.path.join(ROOT, 'tools', 'v85', 'talk_src')
for f in sorted(os.listdir(SRC)):
    if f.endswith('.png'): shutil.copyfile(os.path.join(SRC, f), os.path.join(ROOT, 'web', 'bg', 'portraits', f))
s = open(PAGE, encoding='utf-8').read()
start, end = '// V85 talk start', '// V85 talk end'
if start in s: a = s.index(start); b = s.index(end) + len(end) + 1; s = s[:a] + s[b:]
anchor = '// V85 alive end\n'
assert s.count(anchor) == 1
s = s.replace(anchor, anchor + start + '\n' + open(os.path.join(ROOT, 'tools', 'v85', 'talk.js'), encoding='utf-8').read().rstrip('\n') + '\n' + end + '\n')
SWAPS = [
    ("function drawPortrait(id, x, y, s, rim) {\n  const img = portraitImg(id); if (!img) return false;",
     "function drawPortrait(id, x, y, s, rim, mouth) {\n  const img = portraitImg(id); if (!img) return false;\n  const strip = mouth ? bgImg('portraits/' + id + '_talk') : null;   // Version 85: a talking mouth"),
    ("  ctx.drawImage(img, x + 2, y + 2, s - 4, s - 4);\n  ctx.restore();\n  return true;",
     "  if (strip) ctx.drawImage(strip, mouth * 48, 0, 48, 48, x + 2, y + 2, s - 4, s - 4); else ctx.drawImage(img, x + 2, y + 2, s - 4, s - 4);\n  ctx.restore();\n  return true;"),
    ("      if (av) drawPortrait(b.who, b.mine ? px + pw - 22 - 44 : px + 22, y, 44, (SPEAKERS[b.who] || SPEAKERS.sys).color);",
     "      if (av) drawPortrait(b.who, b.mine ? px + pw - 22 - 44 : px + 22, y, 44, (SPEAKERS[b.who] || SPEAKERS.sys).color, i === blocks.length - 1 ? talkFrame(b.ls.join(' '), chat.t - 0.1) : 0);   // Version 85: the newest one talks"),
    ("  lines.forEach((l, i) => ctx.fillText(l, bx + 9 * bs, by + (6 + 7.5) * bs + i * 15 * bs));\n  ctx.restore();\n}",
     "  lines.forEach((l, i) => ctx.fillText(l, bx + 9 * bs, by + (6 + 7.5) * bs + i * 15 * bs));\n  talkBubbleFace(b, bx, by, bw, bh, bs);   // Version 85: the speaker's face, talking\n  ctx.restore();\n}"),
]
for old, new in SWAPS:
    if new in s: continue
    assert s.count(old) == 1, old[:60]
    s = s.replace(old, new)
open(PAGE, 'w', encoding='utf-8').write(s); print('v85 talk: patched')
