"""Version 69: the train's carriage end (web/bg/nightlife/tr_end.png): python3 tools/v69/tr_end.py

The old end piece (kept as tools/v69/tr_end_old.png) was a darker, bluer gangway door with a plain dark top, so every
carriage end read as a different picture stuck on. This keeps its door and recolours it into the carriage wall's own
grey (tr_wall.png), and gives it the wall's ceiling light strip and sign band with the coach letter in the middle, so the
end wall is part of the same carriage."""
import os
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
wall = np.asarray(Image.open(os.path.join(ROOT, 'web', 'bg', 'nightlife', 'tr_wall.png')).convert('RGBA')).astype(np.float32)
end = np.asarray(Image.open(os.path.join(HERE, 'tr_end_old.png')).convert('RGBA')).astype(np.float32)
H, W = end.shape[:2]
lum = lambda a: a[..., 0] * 0.3 + a[..., 1] * 0.59 + a[..., 2] * 0.11
# the wall's panel colour: its plain grey between the windows (rows 30..80, columns 160..190 sit on the pier by the W 5 sign)
pier = wall[30:80, 160:190, :3].reshape(-1, 3); pier = pier[lum(pier) > 90]
tint = pier.mean(0) / lum(pier.mean(0)[None])[0]
out = end.copy()
L = lum(end[..., :3])
# brighten the door's dark blue-grey up to the wall's light, then colour it the wall's grey
k = np.clip(L * 1.45, 0, 255)
out[..., :3] = np.clip(k[..., None] * tint[None, None, :], 0, 255)
# keep the little red and green lights their own colours
sat = end[..., :3].max(-1) - end[..., :3].min(-1)
out[sat > 60, :3] = end[sat > 60, :3]
# the top: the wall's ceiling and its sign band, with the "W 5" coach plate in the middle
TOP = 22
band = np.repeat(wall[:TOP, 139:140], W, axis=1).copy()      # the plain band between two signs, stretched
band[:5] = wall[:5, 100:100 + W]                              # the ceiling with a light tube in it
plate = wall[5:TOP, 143:179]; x0 = (W - plate.shape[1]) // 2
band[5:TOP, x0:x0 + plate.shape[1]] = plate
out[:TOP] = band
# a dark edge each side, like the wall's own vestibule frames
out[TOP:, :1, :3] = 20; out[TOP:, -1:, :3] = 20
Image.fromarray(out.astype(np.uint8)).save(os.path.join(ROOT, 'web', 'bg', 'nightlife', 'tr_end.png'))
print('tr_end', W, H)
