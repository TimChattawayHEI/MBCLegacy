"""Build a mouth strip for one portrait: mouths.py gif original.png out.png
Takes the unique frames of a PixelLab talking GIF, finds the box where the mouth frames differ from each other, and pastes
only that box (grown by 1px) from each mouth frame onto the original portrait, so the face stays the original drawing.
Out: a strip [closed (original), mouth 1..n] at 48x48."""
import sys
from PIL import Image
g = Image.open(sys.argv[1]); orig = Image.open(sys.argv[2]).convert('RGBA'); fr = []
try:
    while True: fr.append(g.convert('RGBA').copy()); g.seek(g.tell() + 1)
except EOFError: pass
uniq = []
for f in fr:
    if not any(f.tobytes() == u.tobytes() for u in uniq): uniq.append(f)
W, H = orig.size; px = [u.load() for u in uniq]
def dist(a, b): return sum(abs(a[i] - b[i]) for i in range(3)) + abs(a[3] - b[3])
hot = {(x, y) for y in range(H) for x in range(W) if max(dist(p[x, y], q[x, y]) for p in px for q in px) > 90}
# keep the biggest clump (the mouth): grow by 2px to join it up, then flood
from collections import deque
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
xs = [c[0] for c in best]; ys = [c[1] for c in best]
x0, x1, y0, y1 = max(0, min(xs) - 1), min(W, max(xs) + 2), max(0, min(ys) - 1), min(H, max(ys) + 2)
if len(sys.argv) > 4: x0, y0, x1, y1 = map(int, sys.argv[4].split(","))   # a box by hand
print('mouth box', x0, y0, x1, y1, 'frames', len(uniq))
while len(uniq) < 5: uniq.append(uniq[3])   # no separate f mouth: use the e one
out = Image.new('RGBA', (W * len(uniq), H))
for i, u in enumerate(uniq):
    f = orig.copy()
    if i: f.paste(u.crop((x0, y0, x1, y1)), (x0, y0))
    out.paste(f, (i * W, 0))
out.save(sys.argv[3])
