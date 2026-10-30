"""Version 64: whole-stage backdrops painted in Meshy -> web/bg/meshy/<stage>_<n>.png.  python3 tools/v64/meshy_bg.py [stage ...]

Each stage was painted as a run of 16:9 Meshy panels (tools/v64/img/<stage>/<panel>.webp, 1376x768, one screen each),
every panel after the first made by giving Meshy the previous panel's right quarter and asking it to carry the scene on
(tools/v64/meshy_free.py for the first, tools/v64/meshy_cont.py for the rest). Here they are laid out a quarter overlapped and cross-faded across the overlap, then fitted
to the game: the line where the buildings meet the ground ("base", a panel pixel row) goes to the stage's FT, the
picture above it (from row "top") fills the screen above FT and the ground below it fills the screen below, at the
game's native scale (1 pixel = 2 units, so 480x270 a screen). The stage's ST.len units across are cut into 512 pixel
wide tiles, which the game draws edge to edge (tools/v64/meshy_bg.js).
"""
import json, os, sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, 'web', 'bg', 'meshy'); os.makedirs(OUT, exist_ok=True)
CFG = json.load(open(os.path.join(HERE, 'stages.json')))
TILE, PW, PH = 512, 1376, 768
Q = PW // 4                       # each panel overlaps the one before by a quarter
FADE = (72, 272)                  # cross-fade from the old panel to the new one between these columns of the overlap


def stitch(stage, panels):
    ims = [np.asarray(Image.open(os.path.join(HERE, 'img', stage, p + '.webp')).convert('RGB').resize((PW, PH))).astype(np.float32) for p in panels]
    out = np.zeros((PH, PW + (PW - Q) * (len(ims) - 1), 3), np.float32)
    out[:, :PW] = ims[0]
    for i, im in enumerate(ims[1:], 1):
        x0 = i * (PW - Q)
        a = np.clip((np.arange(PW) - FADE[0]) / (FADE[1] - FADE[0]), 0, 1)[None, :, None]
        out[:, x0:x0 + PW] = out[:, x0:x0 + PW] * (1 - a) + im * a
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def patch(strip, stage, c):
    """seam repairs: a Meshy redraw of the 1376 pixels around a join (tools/v64/meshy_seam.py), its middle pasted back
    over the stitched picture with the edges faded in"""
    out = np.asarray(strip).astype(np.float32).copy()
    for fix in c.get('fixes', []):
        if fix[0] == 'diag': continue   # done last, after the patches
        # ["tile", sx0, sx1, dx0, dx1, y0, y1]: cover dx0..dx1 (rows y0..y1) with columns sx0..sx1 repeated, edges faded in
        _, sx0, sx1, dx0, dx1, y0, y1 = fix
        src = out[y0:y1, sx0:sx1].copy(); w = dx1 - dx0; reps = np.concatenate([src] * (w // (sx1 - sx0) + 1), axis=1)[:, :w]
        a = np.clip(np.minimum(np.arange(w) + 1, w - np.arange(w)) / 6, 0, 1)[None, :, None]
        out[y0:y1, dx0:dx1] = out[y0:y1, dx0:dx1] * (1 - a) + reps * a
    for fix in c.get('sky', []):
        # [rx0, rx1, dx0, dx1, y0, y1]: repaint rows y0..y1 of dx0..dx1 as flat night sky, each row the median colour of
        # that row over rx0..rx1 (where Meshy painted the sky right), edges faded in over 40 columns
        rx0, rx1, dx0, dx1, y0, y1 = fix
        row = np.median(out[y0:y1, rx0:rx1], axis=1)[:, None, :]; w = dx1 - dx0
        a = np.clip(np.minimum(np.arange(w) + 1, w - np.arange(w)) / 40, 0, 1)[None, :, None]
        out[y0:y1, dx0:dx1] = out[y0:y1, dx0:dx1] * (1 - a) + row * a
    for x, w, *ln in c.get('seams', []):
        if ln:   # a thin line right on the join: rebuild columns x-ln..x+ln from the columns just outside them
            k = ln[0]; a, b = out[:, x - k - 1], out[:, x + k + 1]
            for i in range(-k, k + 1): t = (i + k + 1) / (2 * k + 2); out[:, x + i] = a * (1 - t) + b * t
        # [x, w]: a faint vertical line at column x where Meshy's kept quarter meets what it painted. Row by row (smoothed
        # over 9 rows), the colour step across x is measured from 10 columns either side and spread out over w columns
        # each way, half taken off each side, so the line goes and the picture either side is left as it was.
        L = out[:, x - 12:x - 2].mean(1); R = out[:, x + 2:x + 12].mean(1); d = R - L
        k = np.ones(9) / 9; d = np.stack([np.convolve(np.pad(d[:, i], 4, mode='edge'), k, mode='valid') for i in range(3)], 1)
        t = np.arange(w, dtype=np.float32) / w
        out[:, x - w:x] += d[:, None, :] * (0.5 * t)[None, :, None]          # left side rises to meet the middle
        out[:, x:x + w] -= d[:, None, :] * (0.5 * (1 - t))[None, :, None]    # right side comes down to meet it
    for x, name, *mode in c.get('patches', []):
        im = np.asarray(Image.open(os.path.join(HERE, 'img', stage, name + '.webp')).convert('RGB').resize((PW, PH))).astype(np.float32)
        x0 = x - PW // 2; a = np.clip(1 - np.abs(np.arange(PW) - PW / 2) / (PW * 0.36), 0, 1); a = np.clip(a * 3, 0, 1)[None, :, None]
        if mode and mode[0] == 'left':   # Version 69: a repaint of the stage's start: all of it, fading out over its last 90 columns
            a = np.clip((PW - np.arange(PW)) / 90, 0, 1)[None, :, None]
        lo, hi = max(0, x0), min(out.shape[1], x0 + PW)
        out[:, lo:hi] = out[:, lo:hi] * (1 - a[:, lo - x0:hi - x0]) + im[:, lo - x0:hi - x0] * a[:, lo - x0:hi - x0]
    for fix in c.get('fixes', []):
        if fix[0] != 'diag': continue
        # ["diag", xc, xbot, y0] (Version 69): a floor that changes in a straight line down the picture at column xc, from
        # row y0 down. The floor right of xc is mirrored leftward to a slanted line from (xc, y0) to (xbot, bottom), with
        # a kerb along it, so the two floors meet along a slanted step instead of a cut
        _, xc, xbot, y0 = fix
        for y in range(y0, out.shape[0]):
            bx = round(xc + (xbot - xc) * (y - y0) / (out.shape[0] - 1 - y0))
            if bx < xc: out[y, bx:xc] = out[y, xc + (xc - bx) - 1:xc - 1:-1]
            out[y, max(0, bx - 7):bx] = (206, 200, 186); out[y, max(0, bx - 11):max(0, bx - 7)] = (112, 108, 102)
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def grade(strip, c):
    """"grade": [x0, x1] raw columns whose floor is the right colour. Meshy sometimes paints a stretch of floor colder or
    warmer than the rest; this pulls the floor's colour (not its light and shade) along the whole stage toward that
    stretch's, a column at a time from the colour around it, fading in over 24 rows from the base down."""
    if 'grade' not in c: return strip
    x0, x1 = c['grade']; b = c['base']
    ycc = np.asarray(strip.convert('YCbCr')).astype(np.float32)
    fl = ycc[b + 10:, :, 1:].mean(axis=0)                                   # each column's floor chroma
    k = 400; ker = np.ones(k) / k
    loc = np.stack([np.convolve(np.pad(fl[:, i], (k // 2, k // 2), mode='edge'), ker, mode='same')[k // 2:-k // 2] for i in range(2)], 1)
    tgt = fl[x0:x1].mean(axis=0)
    ramp = np.clip((np.arange(ycc.shape[0]) - b + 4) / 24, 0, 1)[:, None, None]
    ycc[:, :, 1:] += ramp * (tgt - loc)[None, :, :]
    return Image.fromarray(np.clip(ycc, 0, 255).astype(np.uint8), 'YCbCr').convert('RGB')


def skytone(strip, c):
    """"skytone": [x0, x1, rows]: Meshy paints some panels' sky paler than others. Every sky pixel (blue, in rows
    0..rows) along the stage is moved from the colour of the sky around it (a 300 column window) to the colour of the
    sky in columns x0..x1 at that height, so clouds, the sun and the treeline stay as they are."""
    if 'skytone' not in c: return strip
    x0, x1, rows = c['skytone']
    a = np.asarray(strip).astype(np.float32).copy(); s = a[:rows]
    r, g, b = s[..., 0], s[..., 1], s[..., 2]
    sky = (b > r + 25) & (b > g + 5) & (b > 90)
    tgt = np.array([np.median(s[y, x0:x1][sky[y, x0:x1]], 0) if sky[y, x0:x1].any() else s[y, x0:x1].mean(0) for y in range(rows)])
    # the sky's own colour at each height, every 50 columns (300 wide windows), then the shift interpolated between
    step = 50; cs = list(range(0, s.shape[1], step)) + [s.shape[1] - 1]; sh = np.zeros((rows, len(cs), 3), np.float32); ok = np.zeros((rows, len(cs)), bool)
    for j, cx in enumerate(cs):
        lo, hi = max(0, cx - 150), min(s.shape[1], cx + 150)
        for y in range(rows):
            m = sky[y, lo:hi]
            if m.sum() >= 20: sh[y, j] = tgt[y] - np.median(s[y, lo:hi][m], 0); ok[y, j] = True
    xs = np.arange(s.shape[1]); out = s.copy()
    for y in range(rows):
        if not ok[y].any(): continue
        for ch in range(3):
            d = np.interp(xs, np.array(cs)[ok[y]], sh[y, ok[y], ch])
            out[y, :, ch] += np.where(sky[y], d, 0)
    a[:rows] = out
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def skyfill(strip, c):
    """"skyfill": [x0, x1, rx0, rx1, rows]: a plain sky from column x0 on (Meshy painted it hazy there): every pixel above
    the treeline (the first green pixel down each column, within rows) takes the sky colour of columns rx0..rx1 at that
    height, faded in over 60 columns from x0. The game drifts its own clouds across it (meshyOver)."""
    if 'skyfill' not in c: return strip
    x0, x1, rx0, rx1, rows = c['skyfill']
    a = np.asarray(strip).astype(np.float32).copy(); s = a[:rows]
    r, g, b = s[..., 0], s[..., 1], s[..., 2]
    sky = (b > r + 25) & (b > g + 5) & (b > 90)
    tgt = np.zeros((rows, 3), np.float32)
    for y in range(rows):
        m = sky[y, rx0:rx1]; tgt[y] = np.median(s[y, rx0:rx1][m], 0) if m.sum() > 10 else tgt[y - 1]
    green = (g > b + 5) & (g > r) & (np.arange(rows)[:, None] > 40)
    tree = np.where(green.any(0), green.argmax(0), rows)
    tree = np.array([tree[max(0, i - 2):i + 3].min() for i in range(len(tree))]) - 2
    for x in range(x0, min(x1, s.shape[1])):
        k = min(1.0, (x - x0) / 60); t = tree[x]
        a[:t, x] = a[:t, x] * (1 - k) + tgt[:t] * k
        loose = (b[t:, x] > r[t:, x] + 5) & (b[t:, x] >= g[t:, x]) & (b[t:, x] > 120)   # sky showing through the trees
        a[t:rows, x][loose] = a[t:rows, x][loose] * (1 - k) + tgt[t:][loose] * k
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def floormatch(strip, c):
    """"floormatch": [x0, x1]: Meshy paints some panels' ground lighter or darker than the rest. Each panel after the
    first has its ground (below the base) shifted, light and colour, to the average ground of columns x0..x1, the shift
    changing over 200 columns where the panel starts to be its own (just past the quarter it carried on from)."""
    if 'floormatch' not in c: return strip
    x0, x1 = c['floormatch']; b = c['base'] + 8
    ycc = np.asarray(strip.convert('YCbCr')).astype(np.float32); fl = ycc[b:]
    ref = fl[:, x0:x1].reshape(-1, 3).mean(0); n = len(c['panels']); W_ = fl.shape[1]
    shift = np.zeros((W_, 3), np.float32); prev = None
    for i in range(n):
        a = 0 if i == 0 else i * (PW - Q) + Q; e = min(W_, (i + 1) * (PW - Q) + Q) if i < n - 1 else W_
        d = ref - fl[:, a:e].reshape(-1, 3).mean(0)
        shift[a:e] = d
        if prev is not None:
            r0 = max(0, a - 100); r1 = min(W_, a + 100); t = np.linspace(0, 1, r1 - r0)[:, None]
            shift[r0:r1] = prev * (1 - t) + d * t
        prev = d
    ramp = np.clip((np.arange(fl.shape[0]) + 1) / 24, 0, 1)[:, None, None]
    ycc[b:] += ramp * shift[None]
    return Image.fromarray(np.clip(ycc, 0, 255).astype(np.uint8), 'YCbCr').convert('RGB')


def fit(strip, c):
    w = round(strip.width * 480 / PW); ft = c['ft'] // 2
    top = strip.crop((0, c['top'], strip.width, c['base'])).resize((w, ft), Image.LANCZOS)
    bot = strip.crop((0, c['base'], strip.width, c.get('bottom', PH))).resize((w, 270 - ft), Image.LANCZOS)
    out = Image.new('RGB', (w, 270)); out.paste(top, (0, 0)); out.paste(bot, (0, ft))
    return out.crop((0, 0, c['len'] // 2, 270))


def parasky(full, stage, c):
    """"parasky": [x0, x1, rows, (colour tolerance, default 34)] (Version 70; finished picture pixels): the sky becomes its own layer that the game scrolls
    slower than the scenery, so clouds and stars drift behind. Each column's sky runs down from the top to the first
    pixel that is neither sky colour (each row's own colour, from columns x0..x1), clear blue, nor a pale cloud; that part of
    the picture is made see-through, and <stage>_sky.png is the sky of columns x0..x1, with the gaps filled in with each
    row's sky colour and the two ends blended so it repeats."""
    if 'parasky' not in c: return full, None
    x0, x1, rows, *tol = c['parasky']; tol = tol[0] if tol else 34
    a = np.asarray(full.convert('RGB')).astype(np.float32); H_, W_ = a.shape[:2]
    ref = np.median(a[:rows, x0:x1], axis=1)                                 # each row's sky colour
    d = np.abs(a[:rows] - ref[:, None, :]).sum(-1)
    lum = a[:rows].mean(-1); sat = a[:rows].max(-1) - a[:rows].min(-1)
    r_, g_, b_ = a[:rows, :, 0], a[:rows, :, 1], a[:rows, :, 2]
    skyish = (d < tol) | (lum > 228) | ((b_ > r_ + 25) & (b_ > g_ - 5)) | ((r_ > 165) & (g_ > 165) & (b_ > 165) & (sat < 80) & (b_ >= r_ - 8))   # sky, blue sky, or a pale cloud
    h = np.zeros(W_, int)
    for x in range(W_):
        col = skyish[:, x]; h[x] = rows if col.all() else int(np.argmin(col))
    h = np.array([int(np.median(h[max(0, i - 2):i + 3])) for i in range(W_)])   # a star or speck one or two columns wide doesn't stop it
    h = np.array([h[max(0, i - 1):i + 2].min() for i in range(W_)])          # and a hair inside the edges of what does
    h = np.minimum(h, [int(np.median(h[max(0, i - 6):i + 7])) for i in range(W_)])   # no narrow slits cut down into hills of a sky-like colour
    h[:max(0, x0 - 40)] = 0; h[min(W_, x1 + 40):] = 0                       # only where the stage has sky
    rgba = np.dstack([a, np.full((H_, W_), 255, np.float32)])
    for x in range(W_):
        if h[x] > 1: rgba[:h[x] - 1, x, 3] = 0; rgba[h[x] - 1, x, 3] = 128
    sky = a[:rows, x0:x1].copy()
    for x in range(x1 - x0):
        hx = h[x0 + x]; sky[hx:, x] = ref[hx:]
    k = 40; w = sky.shape[1] - k                                             # blend the ends so it tiles
    t = np.linspace(0, 1, k)[None, :, None]
    sky2 = sky[:, :w].copy(); sky2[:, :k] = sky[:, w:] * (1 - t) + sky[:, :k] * t
    return Image.fromarray(np.clip(rgba, 0, 255).astype(np.uint8), 'RGBA'), Image.fromarray(np.clip(sky2, 0, 255).astype(np.uint8))


def loop(stage, c):
    """scenery that repeats forever (the drive): the panels stitched, then the same again mirrored, so the loop runs on
    with no join at either end (Meshy will not paint a panel that leads back into the first one)"""
    s = np.asarray(stitch(stage, c['loop']))
    s = Image.fromarray(np.concatenate([s, s[:, ::-1]], axis=1))
    top = c.get('top', 0); k = c['ground'] / 2 / (c['base'] - top)
    out = s.crop((0, top, s.width, c['base'])).resize((round(s.width * k), round(c['ground'] / 2)), Image.LANCZOS)
    out.save(os.path.join(OUT, stage + '_loop.png'), optimize=True); print(stage, 'loop', out.size)

for stage in ([] if sys.argv[1:] == ['--none'] else sys.argv[1:] or list(CFG)):
    c = CFG[stage]
    if 'loop' in c: loop(stage, c); continue
    full = fit(floormatch(skyfill(skytone(grade(patch(stitch(stage, c['panels']), stage, c), c), c), c), c), c)
    full, sky = parasky(full, stage, c)
    for f in os.listdir(OUT):
        if f.startswith(stage + '_') and (f[len(stage) + 1:-4].isdigit() or f == stage + '_sky.png'): os.remove(os.path.join(OUT, f))
    if sky: sky.save(os.path.join(OUT, stage + '_sky.png'), optimize=True)
    n = 0
    for x in range(0, full.width, TILE):
        full.crop((x, 0, min(full.width, x + TILE), 270)).save(os.path.join(OUT, f'{stage}_{n}.png'), optimize=True); n += 1
    print(stage, full.size, n, 'tiles')
