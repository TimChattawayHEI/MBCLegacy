"""Carry a stage on to the right: python3 tools/v64/meshy_cont.py <stage> <prev_name> <name> "<what comes next>" [style,...]
Builds a canvas whose left quarter is the right quarter of the previous panel (raw Meshy output) and the rest flat grey,
and asks Meshy to keep the left quarter and paint the rest as the same street carrying on."""
import os, subprocess, sys
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); WORK = os.environ.get('MESHY_WORK', '/tmp/meshy_work')
stage, prev, name, nxt = sys.argv[1:5]
styles = sys.argv[5] if len(sys.argv) > 5 else 'street,alley'
D = os.path.join(WORK, stage)
pv = Image.open(os.path.join(D, prev + '_raw.png')).convert('RGB'); w, h = pv.size; q = w // 4
cv = Image.new('RGB', (w, h), (128, 128, 128))
X0 = os.environ.get('X0')   # native x of this panel in the stage: fill the unpainted part with the old backdrop, blurred, as a rough guide
if X0 is not None:
    from PIL import ImageFilter
    ref = Image.open(os.path.join(D, 'ref.png')).convert('RGB'); x0 = int(X0)   # ref.png: tools/v64/capture.py <stage> <work>/<stage>/ref.png
    g = Image.new('RGB', (480, 270), (20, 22, 34)); g.paste(ref.crop((x0, 0, min(ref.width, x0 + 480), 270)), (0, 0))
    cv = g.resize((w, h), Image.BILINEAR).filter(ImageFilter.GaussianBlur(14))
cv.paste(pv.crop((w - q, 0, w, h)), (0, 0))
cp = os.path.join(D, name + '_canvas.png'); cv.save(cp)
prompt = ("The first image is the left edge of a pixel art background for a side-scrolling beat 'em up game, and the rest of it (blurry or flat grey) is still to be painted, edge to edge, top to bottom. "
          "Keep the painted left quarter exactly as it is, pixel for pixel, and repaint the whole of the rest (the blurry or grey part, which is only a rough guide to what goes where) by carrying the same scene on to the right, seamlessly, "
          "in exactly the same art style, pixel size, lighting, colours and camera as the painted part and as the second image. "
          "The line where the buildings meet the ground stays at the same height all the way across, and the bottom of the picture stays the same flat, wide, empty walkable ground. "
          + nxt + " No people, no cars, no text other than signs named here.")
first = os.path.join(D, prev + '_raw.png') if os.environ.get('FIRST') is None else os.environ['FIRST']
refs = cp + ',' + os.path.join(D, os.environ.get('STYLE_PANEL', 'p0c') + '_raw.png') + (',' + ','.join(os.path.join(HERE, 'img', 'style', s + '.webp') for s in styles.split(',')) if styles else '')
subprocess.run([sys.executable, os.path.join(HERE, 'meshy_free.py'), stage, name, prompt, refs], check=True)
