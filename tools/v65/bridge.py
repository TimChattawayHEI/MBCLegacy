"""Paint over a hard cut in a stage picture: python3 tools/v65/bridge.py <stage> <native x> <name> "<what the join should be>"

native x is a column of the finished stage picture (web/bg/meshy, 1 pixel = 2 game units). Takes the 1376 raw pixels
around it from the stitched Meshy panels (tools/v64/meshy_bg.py), keeps the outer thirds, blurs the middle into a rough
guide, and asks Meshy (9 credits) to repaint the middle as a natural way from one place into the other (a doorway, an
entrance, a kerb) with the floor changing along it, not in a straight line down the picture. Saves
tools/v64/img/<stage>/<name>.webp; add [raw x, "<name>"] (printed) to the stage's "patches" in stages.json.
"""
import importlib.util, os, subprocess, sys
from PIL import Image, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); V64 = os.path.join(ROOT, 'tools', 'v64')
WORK = os.environ.get('MESHY_WORK', '/tmp/meshy_work')
stage, nx, name, what = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
spec = importlib.util.spec_from_file_location('mb', os.path.join(V64, 'meshy_bg.py')); mb = importlib.util.module_from_spec(spec)
sys.argv = [sys.argv[0], '--none']; spec.loader.exec_module(mb)
c = mb.CFG[stage]; strip = mb.patch(mb.stitch(stage, c['panels']), stage, c)
x = round(nx * mb.PW / 480); x = max(688, min(strip.width - 688, x))
crop = strip.crop((x - 688, 0, x + 688, 768)); T = 1376 // 3
guide = crop.filter(ImageFilter.GaussianBlur(16)); guide.paste(crop.crop((0, 0, T, 768)), (0, 0)); guide.paste(crop.crop((1376 - T, 0, 1376, 768)), (1376 - T, 0))
D = os.path.join(WORK, stage); os.makedirs(D, exist_ok=True); gp = os.path.join(D, name + '_canvas.png'); guide.save(gp)
first = os.path.join(V64, 'img', stage, c['panels'][0] + '.webp')
prompt = ("The first image is a wide pixel art background for a side-scrolling beat 'em up game. Its left third and right third are finished and show two "
          "different places; the blurry middle third is only a rough guide and must be repainted. Keep the left third and the right third exactly as they are, "
          "pixel for pixel, and repaint the middle so the picture reads as one continuous place with a natural way through from the left place into the right one, "
          "in exactly the same pixel art style, pixel size, lighting and flat side-on camera as the finished parts and the second image. " + what +
          " There must be no straight vertical line where one floor or wall simply stops and the other starts: the floor on the left meets the floor on the right "
          "along the edge of a step, a threshold, a kerb or a doormat, or they blend gradually. The line where the walls meet the ground stays at the same height, and "
          "the bottom third stays flat, wide, empty walkable ground. No people, no text other than signs already there.")
subprocess.run([sys.executable, os.path.join(V64, 'meshy_free.py'), stage, name, prompt, gp + ',' + first], check=True)
Image.open(os.path.join(D, name + '_raw.png')).save(os.path.join(V64, 'img', stage, name + '.webp'), quality=94, method=6)
print('patch', [x, name])
