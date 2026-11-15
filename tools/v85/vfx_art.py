"""Version 85 hand-drawn small effects: python3 tools/v85/vfx_art.py  (writes web/fx/*.png, prints the FX table lines)

From PixelLab's effects tool (saved in Tim's My effects), in tools/v85/vfx_src:
- puff.png  "Carp Diem smoke puff": cartoon smoke that billows up and breaks into bits (24 px frames)
- lick.png  "Carp Diem flame lick": a single flame tongue that flares and dies (16x22 px frames)
Made here from those: puff_s (the puff halved, keeping its outline), sand and sand_s (both puffs in the old dust's
sandy browns). Drawn here pixel by pixel, being only a few pixels across: twinkle (a four-point star that pops and
shrinks, in the old sparkle's greens), heart, drop and drop_s (water), and zz (a sleep Z in three sizes).
One sheet pixel is 2 game units, as for every effect sheet."""
import os
from collections import Counter
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
SRC, OUT = os.path.join(HERE, 'vfx_src'), os.path.join(ROOT, 'web', 'fx')
hexc = lambda h, a=255: tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) + (a,)
meta = {}

def sheet(frames, cols, name, ax, ay, fps, loop=False):
    fw, fh = frames[0].size; rows = (len(frames) + cols - 1) // cols
    s = Image.new('RGBA', (fw * cols, fh * rows), (0, 0, 0, 0))
    for i, f in enumerate(frames): s.paste(f, ((i % cols) * fw, (i // cols) * fh))
    s.save(os.path.join(OUT, name + '.png')); meta[name] = dict(fw=fw, fh=fh, n=len(frames), cols=cols, ax=ax, ay=ay, fps=fps, loop=loop)

def cut(path, fw, fh, n):
    im = Image.open(path).convert('RGBA'); cols = im.width // fw
    return [im.crop(((i % cols) * fw, (i // cols) * fh, (i % cols + 1) * fw, (i // cols + 1) * fh)) for i in range(n)]

def halve(f):
    """2x2 blocks to one pixel: kept where at least two are solid; an edge block keeps its outline colour."""
    px = f.load(); o = Image.new('RGBA', (f.width // 2, f.height // 2), (0, 0, 0, 0)); op = o.load()
    for y in range(o.height):
        for x in range(o.width):
            cs = [px[2 * x + i, 2 * y + j] for i in (0, 1) for j in (0, 1)]; solid = [c for c in cs if c[3] > 128]
            if len(solid) < 2: continue
            dark = [c for c in solid if sum(c[:3]) < 250]
            op[x, y] = dark[0] if dark and len(solid) < 4 else Counter(solid).most_common(1)[0][0]
    return o

def remap(f, pairs, ref=None):
    """recolour onto another ramp: each source colour, ranked by brightness, takes the same step of the new ramp"""
    px = f.load(); o = f.copy(); op = o.load()
    r = (ref or f).load(); rw, rh = (ref or f).size
    cols = sorted({r[x, y][:3] for y in range(rh) for x in range(rw) if r[x, y][3] >= 128}, key=lambda c: c[0] * 3 + c[1] * 6 + c[2])
    rank = {c: min(len(pairs) - 1, i * len(pairs) // len(cols)) for i, c in enumerate(cols)}
    for y in range(f.height):
        for x in range(f.width):
            c = px[x, y]
            if c[3] >= 128: op[x, y] = hexc(pairs[rank.get(c[:3], len(pairs) - 1)])
    return o

def draw(rows, pal):
    h, w = len(rows), max(len(r) for r in rows); im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); px = im.load()
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch in pal: px[x, y] = hexc(pal[ch])
    return im

# --- the PixelLab two
puff = cut(os.path.join(SRC, 'puff.png'), 24, 24, 8)
sheet(puff, 3, 'puff', 12, 12, 12)
puff_s = [halve(f) for f in puff]
sheet(puff_s, 3, 'puff_s', 6, 6, 12)
SAND = ['#2e2214', '#7a6444', '#a88a5e', '#c8ac7c', '#e8d6ae']
REF = Image.open(os.path.join(SRC, 'puff.png')).convert('RGBA')   # the puff's five colours, ranked once
sheet([remap(f, SAND, REF) for f in puff], 3, 'sand', 12, 12, 12)
sheet([remap(f, SAND, REF) for f in puff_s], 3, 'sand_s', 6, 6, 12)
sheet(cut(os.path.join(SRC, 'lick.png'), 16, 22, 8), 3, 'lick', 8, 15, 12)
# the big puffs: the older poof (purple-grey) in the new puff's greys, so big and small smoke match
POOF = Image.open(os.path.join(OUT, 'poof.png')).convert('RGBA')
sheet([remap(f, ['#211d1e', '#7a7173', '#a8a09d', '#cdc8c3', '#f2eee8'], POOF) for f in cut(os.path.join(OUT, 'poof.png'), 56, 45, 10)], 4, 'poofw', 30, 27, 12)

# --- twinkle: arms grow to a peak with tiny diagonal glints, then shrink to a dot (the old sparkle's greens)
G = {'W': '#ffffff', 'L': '#d4ffbc', 'M': '#8fe36a', 'D': '#4c9a34'}
def star(arm, glint):
    n = 11; c = 5; rows = [['.'] * n for _ in range(n)]
    for d in range(1, arm + 1):
        col = 'L' if d == 1 else ('M' if d < arm else 'D')
        for x, y in ((c + d, c), (c - d, c), (c, c + d), (c, c - d)): rows[y][x] = col
    if glint:
        for x, y in ((c + 2, c + 2), (c - 2, c - 2), (c + 2, c - 2), (c - 2, c + 2)): rows[y][x] = 'D'
        for x, y in ((c + 1, c + 1), (c - 1, c - 1), (c + 1, c - 1), (c - 1, c + 1)): rows[y][x] = 'M'
    rows[c][c] = 'W' if arm > 0 else 'L'
    return draw([''.join(r) for r in rows], G)
sheet([star(1, False), star(3, False), star(5, True), star(4, True), star(2, False), star(1, False), star(0, False)], 4, 'twinkle', 5, 5, 12)

# --- heart, drops
sheet([draw(['.OO...OO.', 'OLWO.OMMO', 'OWLMOMMMO', 'OLMMMMMDO', '.OMMMMDO.', '..OMMDO..', '...ODO...', '....O....'],
            {'O': '#3a0d18', 'W': '#ffffff', 'L': '#ff9fb0', 'M': '#ff4f6d', 'D': '#b0203e'})], 1, 'heart', 4, 4, 1)
DP = {'O': '#2c5a6e', 'W': '#ffffff', 'L': '#d6f2fa', 'M': '#9fd6e8', 'D': '#5fa8c4'}
sheet([draw(['..O..', '.OLO.', 'OLWMO', 'OMMDO', '.OOO.'], DP)], 1, 'drop', 2, 3, 1)
sheet([draw(['.O.', 'OLO', 'OMO', '.O.'], DP)], 1, 'drop_s', 1, 2, 1)

# --- sleep Z in three sizes, outlined, frames padded to one size
def zed(n):
    g = [['.'] * n for _ in range(n)]
    for x in range(n): g[0][x] = g[n - 1][x] = 'F'
    for i in range(1, n - 1): g[i][n - 1 - i] = 'F'
    w = n + 2; rows = [['.'] * w for _ in range(w)]
    for y in range(n):
        for x in range(n):
            if g[y][x] == 'F': rows[y + 1][x + 1] = 'F'
    for y in range(w):
        for x in range(w):
            if rows[y][x] == '.' and any(0 <= y + j < w and 0 <= x + i < w and rows[y + j][x + i] == 'F' for i in (-1, 0, 1) for j in (-1, 0, 1)): rows[y][x] = 'O'
    for x in range(1, n + 1):   # a lighter top edge
        if rows[1][x] == 'F': rows[1][x] = 'L'
    return draw([''.join(r) for r in rows], {'O': '#1a2433', 'F': '#cfe6ff', 'L': '#ffffff'})
zs = [zed(4), zed(5), zed(7)]; S = max(z.width for z in zs)
pad = []
for z in zs:
    f = Image.new('RGBA', (S, S), (0, 0, 0, 0)); f.paste(z, ((S - z.width) // 2, (S - z.height) // 2)); pad.append(f)
sheet(pad, 3, 'zz', S // 2, S // 2, 1)

for k, m in meta.items():
    print("FX.%s = { fw: %d, fh: %d, n: %d, cols: %d, ax: %d, ay: %d, fps: %d, loop: %s };" % (k, m['fw'], m['fh'], m['n'], m['cols'], m['ax'], m['ay'], m['fps'], 'true' if m['loop'] else 'false'))
