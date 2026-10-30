"""Version 70: cut the Meshy pictures in tools/v70/img into game pieces: python3 tools/v70/cut.py

tools/v70/img holds the Meshy results (nano-banana-pro, 9 credits each; prompts in tools/v70/PROMPTS.md):
- train.webp / bus.webp: the train carriage and the N47's top deck, painted full height from a layout of the existing
  (Version 64) walls. Only their ceiling and floor are used (the walls stay the pieces the game moves about):
  web/bg/nightlife/tr_ceil.png and tr_floor.png repeat every 640 units (blended at the ends so they tile);
  bus_ceil.png and bus_floor.png span the screen (the bus doesn't scroll).
- fg.webp: four foreground pieces on magenta (a station column, a street lamp, railings, a luggage trolley), cut out
  to web/bg/fg/*.png at the size they're drawn (2 units a pixel), slightly darkened as they're nearest the camera.
- pit.webp: the night mortar pit behind Seb's artillery cut-in -> web/bg/cutin/pit.png (480x270).
- banner.webp: the caption plate behind stage titles, GAME OVER and the win banner -> web/bg/hud/banner.png.
- over.webp / win.webp: the game over and victory pictures -> web/bg/screens/over.png and win.png (480x270).
- darts.webp: the pub wall and cabinet behind the darts board -> web/bg/mini/darts.png (480x270), shifted so the
  cabinet's round board space sits under the game's board.
- icon.webp: the app icon -> android mipmaps, and the splash picture -> android drawable-nodpi/splash_logo.png.
"""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
IMG = os.path.join(HERE, 'img'); BG = os.path.join(ROOT, 'web', 'bg'); RES = os.path.join(ROOT, 'android', 'app', 'src', 'main', 'res')
load = lambda n: Image.open(os.path.join(IMG, n + '.webp')).convert('RGB')
def save(im, *p):
    path = os.path.join(*p); os.makedirs(os.path.dirname(path), exist_ok=True); im.save(path, optimize=True); print(os.path.relpath(path, ROOT), im.size)

def tile_strip(a, x0, w, k=24):
    """columns x0..x0+w of a, blended at the ends with what follows so the strip repeats with no join"""
    out = a[:, x0:x0 + w].astype(np.float32).copy(); nxt = a[:, x0 + w:x0 + w + k].astype(np.float32)
    t = np.linspace(0, 1, k)[None, :, None]
    out[:, :k] = nxt * (1 - t) + out[:, :k] * t
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))

# the train: the layout had a 320 px wall section at 80..400 of a 480x270 screen, ceiling rows 0..45, floor 189..270
tr = np.asarray(load('train').resize((480, 270), Image.LANCZOS))
save(tile_strip(tr[0:46], 80, 320), BG, 'nightlife', 'tr_ceil.png')
# Meshy put a dark band along the very bottom (rows 248 on); the floor above it is stretched to fill the floor's height
fl = np.asarray(Image.fromarray(tr[188:247]).resize((480, 82), Image.LANCZOS))
save(tile_strip(fl, 80, 320), BG, 'nightlife', 'tr_floor.png')
# the bus: ceiling rows 0..51, floor 195..270, the whole screen
bus = load('bus').resize((480, 270), Image.LANCZOS)
save(bus.crop((0, 0, 480, 52)), BG, 'nightlife', 'bus_ceil.png')
save(bus.crop((0, 194, 480, 270)), BG, 'nightlife', 'bus_floor.png')

# the foreground pieces: magenta keyed out, each piece found as a run of columns with something in it
fg = np.asarray(load('fg')).astype(np.int32)
key = (fg[..., 0] > 200) & (fg[..., 2] > 200) & (fg[..., 1] < 90)
cols = (~key).sum(0) > 6
runs, x = [], 0
while x < len(cols):
    if cols[x]:
        s = x
        while x < len(cols) and cols[x]: x += 1
        if x - s > 20: runs.append((s, x))
    x += 1
NAMES = ['column', 'lamp', 'railing', 'trolley']
HEIGHT = {'column': 300, 'lamp': 290, 'railing': 62, 'trolley': 52}   # art pixels tall in the game (2 units each)
for name, (s, e) in zip(NAMES, runs[:4]):
    m = ~key[:, s:e]; ys = np.where(m.any(1))[0]; y0, y1 = ys.min(), ys.max() + 1
    rgba = np.dstack([fg[y0:y1, s:e] * 0.82, np.where(m[y0:y1], 255, 0)]).astype(np.uint8)   # nearest the camera, so in shadow
    im = Image.fromarray(rgba, 'RGBA'); h = HEIGHT[name]; w = max(1, round(im.width * h / im.height))
    save(im.resize((w, h), Image.LANCZOS), BG, 'fg', name + '.png')

save(load('pit').resize((480, 270), Image.LANCZOS), BG, 'cutin', 'pit.png')
save(load('over').resize((480, 270), Image.LANCZOS), BG, 'screens', 'over.png')
save(load('win').resize((480, 270), Image.LANCZOS), BG, 'screens', 'win.png')

# the banner plate: cut out of the magenta, the plate's own box
b = np.asarray(load('banner')).astype(np.int32); bk = (b[..., 0] > 200) & (b[..., 2] > 200) & (b[..., 1] < 90)
ys, xs = np.where(~bk); y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
plate = np.dstack([b[y0:y1, x0:x1], np.where(bk[y0:y1, x0:x1], 0, 255)]).astype(np.uint8)
save(Image.fromarray(plate, 'RGBA').resize((480, 56), Image.LANCZOS), BG, 'hud', 'banner.png')

# darts: the cabinet's round dark board space (Meshy was given the board's size, and drew it a little smaller) is found,
# and the picture scaled about it and moved so the space sits under the game's board (DBX 480, DBY 262 units: 240, 131
# art pixels) with the board just covering it (pubImg dartboard, drawn 2x)
d = load('darts').resize((480, 270), Image.LANCZOS); da = np.asarray(d).astype(np.float32)
dark = da.mean(-1) < 22
sub = dark[20:230, 130:350]; ys, xs = np.where(sub)
cx0, cy0 = (xs.min() + xs.max()) / 2 + 130, (ys.min() + ys.max()) / 2 + 20
r0 = ((xs.max() - xs.min()) + (ys.max() - ys.min())) / 4
board = Image.open(os.path.join(BG, 'pub', 'dartboard.png')); r1 = board.width / 2 - 2
sc = max(1.0, r1 / r0); print('darts board space', round(cx0), round(cy0), 'radius', round(r0, 1), 'scale', round(sc, 2))
big = d.resize((round(480 * sc), round(270 * sc)), Image.LANCZOS)
ox, oy = round(240 - cx0 * sc), round(131 - cy0 * sc)
out = Image.new('RGB', (480, 270)); out.paste(big, (ox, oy))
o = np.asarray(out).copy()
if ox > 0: o[:, :ox] = o[:, ox:ox + 1]
if oy > 0: o[:oy] = o[oy:oy + 1]
if oy + big.height < 270: o[oy + big.height:] = o[oy + big.height - 1:oy + big.height]
if ox + big.width < 480: o[:, ox + big.width:] = o[:, ox + big.width - 1:ox + big.width]
# Meshy kept faint light and dark bands where the guide's wallpaper repeated: even each column of the wall out to the
# light of the wall around it, measured on the plain wallpaper along the top (only in broad bands, not the detail)
o = o.astype(np.float32); top = o[2:28].mean(axis=(0, 2))
sm = lambda v, k: np.convolve(np.pad(v, k // 2, mode='edge'), np.ones(k) / k, mode='valid')
g = np.clip(sm(sm(top, 81), 9) / np.maximum(sm(top, 15), 1), 0.85, 1.15)
o[:186] *= g[None, :, None]
o = np.clip(o, 0, 255).astype(np.uint8)
save(Image.fromarray(o), BG, 'mini', 'darts.png')

# the app icon: the square inside Meshy's white margin
ic = np.asarray(Image.open(os.path.join(IMG, 'icon.webp')).convert('RGB')).astype(np.int32)
nonwhite = ic.min(-1) < 235; ys, xs = np.where(nonwhite)
icon = Image.fromarray(ic[ys.min():ys.max() + 1, xs.min():xs.max() + 1].astype(np.uint8))
side = min(icon.size); icon = icon.crop(((icon.width - side) // 2, (icon.height - side) // 2, (icon.width - side) // 2 + side, (icon.height - side) // 2 + side))
for d_, px in [('mdpi', 48), ('hdpi', 72), ('xhdpi', 96), ('xxhdpi', 144), ('xxxhdpi', 192)]:
    save(icon.resize((px, px), Image.LANCZOS), RES, 'mipmap-' + d_, 'ic_launcher.png')
save(icon.resize((288, 288), Image.LANCZOS), RES, 'drawable-nodpi', 'splash_logo.png')
