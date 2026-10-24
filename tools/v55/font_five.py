"""Version 55.2: a flat-topped 5 in the pixel font: python3 tools/v55/font_five.py

Pixelify Sans draws its 5 almost exactly like its S, so on scores and timers it reads as a backwards 2. This redraws the
'five' glyph on the font's own pixel grid with a flat top and a square left shoulder, and drops its weight variation
(the game's HUD uses the regular weight). Safe to run again.
"""
import os
from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, 'web', 'fonts', 'pixelify.ttf')
f = TTFont(P)
glyf = f['glyf']
# the outline, on the same grid the other digits use (columns 60/151/161/423/433/525, rows -12/78/88/179/270/359/540/631)
PTS = [(151, -12), (433, -12), (433, 78), (525, 78), (525, 270), (433, 270), (433, 359), (161, 359), (161, 540), (525, 540),
       (525, 631), (60, 631), (60, 270), (423, 270), (423, 88), (161, 88), (161, 179), (60, 179), (60, 78), (151, 78)]
area = lambda pts: sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))
ref = glyf['S'].getCoordinates(glyf)[0]; ref = [tuple(p) for p in ref[:glyf['S'].endPtsOfContours[0] + 1]]
if (area(PTS) > 0) != (area(ref) > 0): PTS = PTS[::-1]   # same winding as the font's own outer contours
pen = TTGlyphPen(None); pen.moveTo(PTS[0])
for p in PTS[1:]: pen.lineTo(p)
pen.closePath()
g = pen.glyph(); g.recalcBounds(glyf); glyf['five'] = g
if 'gvar' in f and 'five' in f['gvar'].variations: del f['gvar'].variations['five']
f.save(P)
print('font_five: 5 redrawn with a flat top')
