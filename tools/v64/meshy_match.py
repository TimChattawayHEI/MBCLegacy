"""Pull a carried-on panel's colours into line with the quarter it carried on from: python3 tools/v64/meshy_match.py <stage> <name> [rows]

Meshy keeps the left quarter of a carried-on panel but sometimes paints the rest a shade off (a paler sky, a colder
floor). For each row in 0..rows (default 130: the sky; keep to rows with nothing in front), the painted part's average colour is shifted to
the left quarter's, the shift smoothed over neighbouring rows and faded in over 100 columns past the quarter. The
original is kept as <name>_orig.png; <name>_raw.png becomes the matched panel, so later panels carry on from it."""
import os, sys, shutil
import numpy as np
from PIL import Image
WORK = os.environ.get('MESHY_WORK', '/tmp/meshy_work')
stage, name = sys.argv[1], sys.argv[2]; rows = int(sys.argv[3]) if len(sys.argv) > 3 else 130
D = os.path.join(WORK, stage); src = os.path.join(D, name + '_raw.png'); orig = os.path.join(D, name + '_orig.png')
if not os.path.exists(orig): shutil.copy(src, orig)
p = np.asarray(Image.open(orig).convert('RGB')).astype(np.float32)
L = np.median(p[:rows, 60:330], 1); R = np.median(p[:rows, 444:], 1)
d = L - R; k = np.ones(9) / 9; d = np.stack([np.convolve(np.pad(d[:, i], 4, mode='edge'), k, mode='valid') for i in range(3)], 1)
w = np.clip((np.arange(p.shape[1]) - 344) / 100, 0, 1)
fade = np.clip((rows - np.arange(rows)) / 30, 0, 1)[:, None, None]
p[:rows] += d[:, None, :] * w[None, :, None] * fade
Image.fromarray(np.clip(p, 0, 255).astype(np.uint8)).save(src); print('matched', name)
