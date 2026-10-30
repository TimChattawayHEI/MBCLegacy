"""Version 70: the bus grab pole as a weapon (web/bg/weapons/pole.png, 38x10, held and thrown): python3 tools/v70/pole_weapon.py

Matches the bus's new grab pole (tools/v69/pole.py): a yellow pole with its grey bracket at one end, the floor flange at
the other and the red STOP button clamped on, lying flat."""
import os
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
W, H = 38, 10
OUT, Y, YL, YD = (26, 20, 22, 255), (232, 194, 58, 255), (255, 240, 160, 255), (168, 132, 28, 255)
G, GL = (120, 122, 132, 255), (170, 172, 182, 255)
R, RL, RD = (216, 50, 42, 255), (255, 120, 100, 255), (140, 26, 22, 255)
im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); px = im.load()
def rect(x0, y0, x1, y1, c):
    for y in range(y0, y1):
        for x in range(x0, x1): px[x, y] = c
cy = H // 2
rect(2, cy - 2, W - 2, cy + 2, OUT); rect(2, cy - 1, W - 2, cy + 1, Y); rect(2, cy - 1, W - 2, cy, YL); rect(2, cy, W - 2, cy + 1, YD)
rect(0, cy - 4, 3, cy + 4, OUT); rect(1, cy - 3, 2, cy + 3, G)                 # the ceiling bracket
rect(W - 3, cy - 4, W, cy + 4, OUT); rect(W - 2, cy - 3, W - 1, cy + 3, GL)    # the floor flange
rect(19, cy - 5, 26, cy + 5, OUT); rect(20, cy - 4, 25, cy + 4, R); rect(20, cy - 4, 25, cy - 3, RL); rect(20, cy + 3, 25, cy + 4, RD)
rect(21, cy - 1, 24, cy + 1, (250, 244, 230, 255))
im.save(os.path.join(ROOT, 'web', 'bg', 'weapons', 'pole.png')); print('pole weapon', im.size)
