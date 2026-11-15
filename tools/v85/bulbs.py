"""Find small bright light bulbs in a band of a Meshy stage painting.
Usage: bulbs.py stage y0 y1 [minbright]   (y in screen px, the painting is drawn at 2x)
Prints [worldx, screeny, '#rrggbb'] for each blob, the painting tiles laid end to end."""
import sys, json, os
from PIL import Image
from collections import deque
k, y0, y1 = sys.argv[1], int(sys.argv[2]) // 2, int(sys.argv[3]) // 2
mb = int(sys.argv[4]) if len(sys.argv) > 4 else 200
import glob
tiles = sorted(glob.glob(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'web', 'bg', 'meshy', k + '_[0-9].png')))
ims = [Image.open(t).convert('RGB') for t in tiles]
W = sum(i.width for i in ims); im = Image.new('RGB', (W, ims[0].height)); x = 0
for i in ims: im.paste(i, (x, 0)); x += i.width
px = im.load(); seen = set(); out = []
for y in range(y0, y1):
    for x in range(W):
        if (x, y) in seen: continue
        p = px[x, y]
        if max(p) < mb or max(p) - min(p) < 40: continue
        comp = []; q = deque([(x, y)]); seen.add((x, y))
        while q:
            cx, cy = q.popleft(); comp.append((cx, cy))
            for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
                n = (cx+dx, cy+dy)
                if 0 <= n[0] < W and y0 <= n[1] < y1 and n not in seen:
                    pp = px[n]
                    if max(pp) >= mb - 40 and max(pp) - min(pp) >= 40: seen.add(n); q.append(n)
        if 1 <= len(comp) <= 6:
            ax = sum(c[0] for c in comp) / len(comp); ay = sum(c[1] for c in comp) / len(comp)
            r, g, b = max((px[c] for c in comp), key=sum)
            out.append([round(ax * 2), round(ay * 2), '#%02x%02x%02x' % (r, g, b)])
print(len(out)); print(json.dumps(out))
