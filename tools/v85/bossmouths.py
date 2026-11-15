"""Talking mouths for a boss card: bossmouths.py key gif [x0,y0,x1,y1]
The card's head crop (tools/v85/bosstalk_src/crop_<key>.png, cut at boxes.json) went to PixelLab's vocal animation; its
talking GIF for "m a o e f" holds the shut mouth and the four open ones in that order. As for the lads (mouths.py), only the
box where the mouth frames differ is taken, and it is pasted onto the original card, so the painted card is untouched
apart from the mouth. Out: tools/v85/bosstalk_src/<key>_talk.png, five cards side by side (shut = the original, a, o, e, f).
A box can be given by hand (crop coordinates) when the found one is wrong."""
import json, os, sys
from collections import deque
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); SRC = os.path.join(HERE, 'bosstalk_src'); ROOT = os.path.dirname(os.path.dirname(HERE))
key, gif = sys.argv[1], sys.argv[2]
bx, by, W, H = json.load(open(os.path.join(SRC, 'boxes.json')))[key]
card = Image.open(os.path.join(ROOT, 'web', 'bg', 'bosscard', key + '.png')).convert('RGBA')
g = Image.open(gif); fr = []
try:
    while True: fr.append(g.convert('RGBA').copy()); g.seek(g.tell() + 1)
except EOFError: pass
uniq = []
for f in fr:
    if not any(f.tobytes() == u.tobytes() for u in uniq): uniq.append(f)
px = [u.load() for u in uniq]; S = uniq[0].size[0]
def dist(a, b): return sum(abs(a[i] - b[i]) for i in range(3)) + abs(a[3] - b[3])
hot = {(x, y) for y in range(S) for x in range(S) if max(dist(p[x, y], q[x, y]) for p in px for q in px) > 90}
seen, best = set(), []
for s0 in hot:
    if s0 in seen: continue
    comp, q = [], deque([s0]); seen.add(s0)
    while q:
        cx, cy = q.popleft(); comp.append((cx, cy))
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                n = (cx + dx, cy + dy)
                if n in hot and n not in seen: seen.add(n); q.append(n)
    if len(comp) > len(best): best = comp
xs = [c[0] for c in best] or [0]; ys = [c[1] for c in best] or [0]
x0, x1, y0, y1 = max(0, min(xs) - 1), min(S, max(xs) + 2), max(0, min(ys) - 1), min(S, max(ys) + 2)
if len(sys.argv) > 3: x0, y0, x1, y1 = map(int, sys.argv[3].split(','))
print(key, 'mouth box', x0, y0, x1, y1, 'frames', len(uniq))
while len(uniq) < 5: uniq.append(uniq[-1])
out = Image.new('RGBA', (W * 5, H))
for i, u in enumerate(uniq[:5]):
    f = card.copy()
    if i:
        patch = u.crop((x0, y0, x1, y1)); f.paste(patch, (bx + x0, by + y0), patch)   # only the mouth's solid pixels
        orig = card.crop((bx + x0, by + y0, bx + x1, by + y1))
        # where the new mouth is see-through but the card isn't, keep the card (the crop's cut-out may differ)
    out.paste(f, (i * W, 0))
out.save(os.path.join(SRC, key + '_talk.png'))
