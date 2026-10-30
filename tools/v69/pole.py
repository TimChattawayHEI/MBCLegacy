"""Version 69: the N47's grab pole (web/bg/props/pole.png), a breakable on the bus: python3 tools/v69/pole.py

A full height yellow grab pole, floor to ceiling, with its ceiling bracket, a red STOP button at hand height and a
floor flange, instead of the old stubby pole on a red block and stone plinth (Tim: "the poles in the red things look
wrong"). Drawn pixel by pixel; the game draws it at 2 units a pixel with its foot 6 units below the prop's y."""
import os
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
W, H = 14, 150
OUT, Y, YL, YD = (26, 20, 22, 255), (232, 194, 58, 255), (255, 240, 160, 255), (168, 132, 28, 255)
G, GL, GD = (120, 122, 132, 255), (170, 172, 182, 255), (70, 72, 82, 255)
R, RL, RD = (216, 50, 42, 255), (255, 120, 100, 255), (140, 26, 22, 255)
im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); px = im.load()
def rect(x0, y0, x1, y1, c):
    for y in range(y0, y1):
        for x in range(x0, x1): px[x, y] = c
cx = W // 2
# the pole: 4 wide with a highlight and a shade, outlined
rect(cx - 3, 4, cx + 3, H - 3, OUT); rect(cx - 2, 4, cx + 2, H - 3, Y)
rect(cx - 1, 4, cx, H - 3, YL); rect(cx + 1, 4, cx + 2, H - 3, YD)
# the ceiling bracket
rect(cx - 5, 0, cx + 5, 5, OUT); rect(cx - 4, 1, cx + 4, 4, G); rect(cx - 4, 1, cx + 4, 2, GL)
# the floor flange
rect(1, H - 4, W - 1, H, OUT); rect(2, H - 3, W - 2, H - 1, G); rect(2, H - 3, W - 2, H - 2, GL)
# the red STOP button, clamped on at hand height
by = 70
rect(cx - 6, by, cx + 6, by + 12, OUT); rect(cx - 5, by + 1, cx + 5, by + 11, R)
rect(cx - 5, by + 1, cx + 5, by + 2, RL); rect(cx - 5, by + 10, cx + 5, by + 11, RD)
rect(cx - 2, by + 4, cx + 2, by + 8, (250, 244, 230, 255))   # the white push
rect(cx - 1, by + 5, cx + 1, by + 7, RL)
# two dark joint rings
for y in (40, 110): rect(cx - 3, y, cx + 3, y + 2, YD)
im.save(os.path.join(ROOT, 'web', 'bg', 'props', 'pole.png'))
print('pole', im.size)
