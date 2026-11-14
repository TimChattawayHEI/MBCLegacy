"""Drop floating bits (blood sprays, impact streaks) from source strips: in every frame keep only the
largest connected blob of opaque pixels and anything touching it.
python3 tools/v85/clean.py <kind> <anim> [<anim> ...]   (edits tools/v85/src/<kind>/q_<anim>@<w>.png in place)"""
import sys, os, glob
import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))


def clean_frame(f, keep_min=40):
    lab, n = ndimage.label(f[..., 3] > 0, structure=np.ones((3, 3)))
    if n < 2: return f
    sizes = ndimage.sum(np.ones(lab.shape), lab, range(1, n + 1))
    big = 1 + int(np.argmax(sizes))
    keep = np.zeros(n + 1, bool); keep[big] = True
    for i, s in enumerate(sizes, 1):   # a large second blob (a thrown leg, a dropped bag) stays
        if s >= keep_min and s >= 0.15 * sizes[big - 1]: keep[i] = True
    out = f.copy(); out[~keep[lab]] = 0
    return out


for anim in sys.argv[2:]:
    for p in glob.glob(os.path.join(HERE, 'src', sys.argv[1], 'q_%s@*.png' % anim)):
        w = int(p.rsplit('@', 1)[1][:-4]); im = np.array(Image.open(p).convert('RGBA'))
        frames = [clean_frame(im[:, k * w:(k + 1) * w]) for k in range(im.shape[1] // w)]
        Image.fromarray(np.concatenate(frames, 1), 'RGBA').save(p); print('cleaned', p)
