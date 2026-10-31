"""Orpington 2001 backdrop panels in Meshy, painted from Tim's photos (tools/v72/ref).

First panel:  python3 tools/v72/orp_panel.py <stage> <name> - <photo> "<what it shows>"
Next panel:   python3 tools/v72/orp_panel.py <stage> <name> <prev> <photo> "<what it shows>"

A next panel's canvas keeps the previous panel's right quarter and fills the rest with the photo, softened, as a guide.
The sharp photo also goes in as a reference for the real details, plus the Orpington station panel and Tim's street
scene for the look. Uses tools/v64/meshy_free.py (nano-banana-pro, 16:9, 9 credits); output in MESHY_WORK/<stage>/."""
import os, subprocess, sys
from PIL import Image, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); V64 = os.path.join(HERE, '..', 'v64')
WORK = os.environ.get('MESHY_WORK', '/tmp/meshy_work')
stage, name, prev, photo, what = sys.argv[1:6]
D = os.path.join(WORK, stage); os.makedirs(D, exist_ok=True)
ph = os.path.join(HERE, 'ref', photo)
look = os.path.join(V64, 'img', 'nl_station', 'p0.webp')
street = os.path.join(V64, 'img', 'style', 'street.webp')
STYLE = ("in exactly the art style of the night-time pixel art street backgrounds given: chunky 16-bit pixel art, crisp dark outlines, "
         "warm lamplight and lit windows against a deep blue night sky. Strict flat side view, straight on, no perspective, no vanishing point: "
         "the building fronts face the camera square on in one straight row, as in a side-scrolling beat 'em up. "
         "The building fronts take the top two thirds; the bottom third is a wide, flat, empty pavement and road edge the fighters walk on, "
         "the same height all the way across. Set in 2001 in Orpington, south east London. No people, no cars, no text other than signs named here.")
if prev == '-':
    prompt = ("A wide pixel art background for a side-scrolling beat 'em up game. Paint the real buildings in the first image (a photo) as faithfully "
              "as the style allows, keeping their shape, materials, windows, roofs and signs, " + STYLE + " " + what)
    refs = ','.join([ph, look, street])
else:
    pv = Image.open(os.path.join(D, prev + '_raw.png')).convert('RGB'); w, h = pv.size; q = w // 4
    g = Image.open(ph).convert('RGB'); s = h / g.height; g = g.resize((max(w, int(g.width * s)), h), Image.BILINEAR)
    cv = Image.new('RGB', (w, h)); cv.paste(g.crop((0, 0, w - q, h)).filter(ImageFilter.GaussianBlur(10)), (q, 0)); cv.paste(pv.crop((w - q, 0, w, h)), (0, 0))
    cp = os.path.join(D, name + '_canvas.png'); cv.save(cp)
    prompt = ("The first image is a pixel art background for a side-scrolling beat 'em up game: its left quarter is finished, and the rest is a blurry photo "
              "that is only a guide to what goes there. Keep the painted left quarter exactly as it is, pixel for pixel, and repaint the whole of the rest, "
              "edge to edge, carrying the same street on to the right seamlessly, with the same lighting, colours, pixel size and the same line where the "
              "buildings meet the pavement. The second image is the real photo of the next building: paint it faithfully, keeping its shape, materials, "
              "windows, roof and signs, " + STYLE + " " + what)
    refs = ','.join([cp, ph, os.path.join(D, prev + '_raw.png'), look])
subprocess.run([sys.executable, os.path.join(V64, 'meshy_free.py'), stage, name, prompt, refs], check=True)
