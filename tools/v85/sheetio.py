"""Read PixelLab workbench 'inspect --scale 2' sheets back into 1x RGBA frames, finding the canvas size by itself."""
import numpy as np
from PIL import Image
S, LAB = 2, 18
def _bg(im): return im[2, 2, :3]
def detect(im):
    H, W = im.shape[:2]; bg = _bg(im); best = None
    for cols in (3, 4, 5, 6):
        if W % (cols * S): continue
        w = W // (cols * S)
        if not 40 <= w <= 200: continue
        # labels: each column's 'frame Fn' text starts 3px in from the cell's left edge
        ok = all((im[2:16, c * w * S + 3: c * w * S + 12, :3] != bg).any() for c in range(cols))
        if not ok: continue
        for rows in range(1, 10):
            if H % rows: continue
            ch = H // rows
            if (ch - LAB) % S: continue
            h = (ch - LAB) // S
            if not 40 <= h <= 200: continue
            ok2 = all((im[r * ch + 2: r * ch + 16, 3:12, :3] != bg).any() for r in range(rows))
            if ok2: best = (w, h, cols, rows)
    if not best: raise ValueError('no grid')
    return best
def frames(path):
    import glob, os
    if not os.path.exists(path):   # a 1x strip cut from a workbench 'join --as rows' sheet: q_<anim>@<w>.png
        alt = glob.glob(path[:-4] + '@*.png')
        if alt: return strip(alt[0])
    im = np.array(Image.open(path).convert('RGBA')); w, h, cols, rows = detect(im)
    ch = h * S + LAB; bg = _bg(im); out = []
    for r in range(rows):
        for c in range(cols):
            blk = im[r * ch + LAB: r * ch + LAB + h * S, c * w * S: (c + 1) * w * S]
            f = blk[::S, ::S].copy(); key = (f[..., :3] == bg).all(-1)
            if key.all(): continue
            f[key] = 0; out.append(f)
    return out, (w, h)
def bbox(f):
    ys, xs = np.where(f[..., 3] > 0); return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())


def strip(path):
    w = int(path.rsplit('@', 1)[1][:-4]); im = np.array(Image.open(path).convert('RGBA')); h = im.shape[0]
    out = [im[:, k * w:(k + 1) * w].copy() for k in range(im.shape[1] // w)]
    return [f for f in out if f[..., 3].any()], (w, h)


def split_join(path, w, h, names, dest):
    """a 'join --as rows' sheet (1x, an 18px label on top, one animation per row) into q_<name>@<w>.png strips"""
    import os
    im = np.array(Image.open(path).convert('RGBA')); top = im.shape[0] - h * len(names); bg = im[2, 2, :3]
    for r, name in enumerate(names):
        row = im[top + r * h: top + (r + 1) * h].copy(); key = (row[..., :3] == bg).all(-1); row[key] = 0
        n = row.shape[1] // w; keep = [k for k in range(n) if row[:, k * w:(k + 1) * w, 3].any()]
        out = np.concatenate([row[:, k * w:(k + 1) * w] for k in keep], 1)
        Image.fromarray(out, 'RGBA').save(os.path.join(dest, 'q_%s@%d.png' % (name, w)))


def split_grid(path, w, h, cols, rows, name, dest):
    """one animation laid out by 'join <anim> --as sheet --columns n' (1x, label on top) into q_<name>@<w>.png"""
    import os
    im = np.array(Image.open(path).convert('RGBA')); top = im.shape[0] - h * rows; bg = im[2, 2, :3]
    fr = []
    for r in range(rows):
        for c in range(cols):
            f = im[top + r * h: top + (r + 1) * h, c * w:(c + 1) * w].copy(); key = (f[..., :3] == bg).all(-1); f[key] = 0
            if f[..., 3].any(): fr.append(f)
    Image.fromarray(np.concatenate(fr, 1), 'RGBA').save(os.path.join(dest, 'q_%s@%d.png' % (name, w)))


def split_multi(path, w, h, cols, rows, parts, dest):
    """several animations laid end to end by 'join a b --as sheet --columns n' into q_<name>@<w>.png strips;
    parts is [(name, frame count), ...] in order"""
    import os
    im = np.array(Image.open(path).convert('RGBA')); top = im.shape[0] - h * rows; bg = im[2, 2, :3]
    cells = []
    for r in range(rows):
        for c in range(cols):
            f = im[top + r * h: top + (r + 1) * h, c * w:(c + 1) * w].copy(); key = (f[..., :3] == bg).all(-1); f[key] = 0; cells.append(f)
    k = 0
    for name, n in parts:
        Image.fromarray(np.concatenate(cells[k:k + n], 1), 'RGBA').save(os.path.join(dest, 'q_%s@%d.png' % (name, w))); k += n
