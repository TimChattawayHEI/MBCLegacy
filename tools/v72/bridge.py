"""Paint over a hard cut in the Orpington 2001 strip before it's in stages.json:
python3 tools/v72/bridge.py <stage> <name@x,name@x,...> <raw x> <name> "<what the join should be>"

Stitches the raw Meshy panels (each starts 1032 px after the last, as meshy_cont/orp_panel paint them), takes the 1376
pixels around raw x, keeps the outer thirds, blurs the middle into a guide and has Meshy (9 credits) repaint the middle.
A panel's own cut sits at raw i*1032+344. Saves MESHY_WORK/<stage>/<name>_raw.png; it covers raw x-688 to x+688."""
import os, subprocess, sys
from PIL import Image, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); V64 = os.path.join(HERE, '..', 'v64')
WORK = os.environ.get('MESHY_WORK', '/tmp/meshy_work')
stage, panels, x, name, what = sys.argv[1], sys.argv[2].split(','), int(sys.argv[3]), sys.argv[4], sys.argv[5]
D = os.path.join(WORK, stage)
items = [(p.split('@')[0], int(p.split('@')[1])) if '@' in p else (p, i * 1032) for i, p in enumerate(panels)]   # pasted in order: later ones cover earlier ones
strip = Image.new('RGB', (max(x0 for _, x0 in items) + 1376, 768))
for p, x0 in items: strip.paste(Image.open(os.path.join(D, p + '_raw.png')).convert('RGB'), (x0, 0))
crop = strip.crop((x - 688, 0, x + 688, 768)); T = 1376 // 3
import numpy as np
a = np.asarray(crop).astype(float); L = a[:, T - 1:T]; R = a[:, 1376 - T:1376 - T + 1]
t = np.linspace(0, 1, 1376 - 2 * T)[None, :, None]; k = float(os.environ.get('MIX', '0.35')); mid = a[:, T:1376 - T] * k + (L * (1 - t) + R * t) * (1 - k)   # crossfade the edges so the guide has no cut
g = a.copy(); g[:, T:1376 - T] = mid; guide = Image.fromarray(g.astype('uint8')).filter(ImageFilter.GaussianBlur(10)); guide.paste(crop.crop((0, 0, T, 768)), (0, 0)); guide.paste(crop.crop((1376 - T, 0, 1376, 768)), (1376 - T, 0))
gp = os.path.join(D, name + '_canvas.png'); guide.save(gp); cp = os.path.join(D, name + '_crop.png'); crop.save(cp)
prompt = ("The first image is a wide pixel art background for a side-scrolling beat 'em up game. Its left third and right third are finished; the blurry middle "
          "third is only a rough guide and must be repainted. Keep the left third and the right third exactly as they are, pixel for pixel, and repaint the middle "
          "so the whole picture is one seamless street scene at night with no visible join, vertical line or change of colour in the sky, buildings or ground, "
          "in exactly the same pixel art style, pixel size, lighting and camera as the finished parts. " + what + " No people, no cars, no text other than signs already there.")
subprocess.run([sys.executable, os.path.join(V64, 'meshy_free.py'), stage, name, prompt, gp + ',' + cp], check=True)
