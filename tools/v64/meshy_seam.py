"""Repair a visible join: python3 tools/v64/meshy_seam.py <stage> <x> <name> ["what is there"]

x is a pixel column of the stitched raw picture (panel k starts at k * 1032; a panel's own join is 344 in from its
start). Sends Meshy the 1376 pixels around x and asks it to make the join invisible, changing nothing else, then saves
it as tools/v64/img/<stage>/<name>.webp. Add [x, "<name>"] to the stage's "patches" in stages.json and re-run meshy_bg.py."""
import os, subprocess, sys
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); WORK = os.environ.get('MESHY_WORK', '/tmp/meshy_work')
sys.path.insert(0, HERE)
stage, x, name = sys.argv[1], int(sys.argv[2]), sys.argv[3]; what = sys.argv[4] if len(sys.argv) > 4 else ''
import importlib.util
spec = importlib.util.spec_from_file_location('mb', os.path.join(HERE, 'meshy_bg.py')); mb = importlib.util.module_from_spec(spec)
sys.argv = [sys.argv[0], '--none']; spec.loader.exec_module(mb)
c = mb.CFG[stage]; strip = mb.patch(mb.stitch(stage, c['panels']), stage, c)
crop = strip.crop((x - 688, 0, x + 688, 768)); D = os.path.join(WORK, stage); os.makedirs(D, exist_ok=True)
cp = os.path.join(D, name + '_crop.png'); crop.save(cp)
prompt = ("This pixel art game background has a visible vertical join or break running down the middle of the picture, where two halves were painted separately. "
          "Repaint just the middle of the picture so the two halves join up seamlessly and naturally, with every wall, door, line, light and floor pattern continuing correctly across. "
          "Keep the left and right thirds exactly as they are, pixel for pixel, and keep the same pixel art style, pixel size, lighting and camera. " + what + " No people, no new text.")
subprocess.run([sys.executable, os.path.join(HERE, 'meshy_free.py'), stage, name, prompt, cp], check=True)
Image.open(os.path.join(D, name + '_raw.png')).save(os.path.join(HERE, 'img', stage, name + '.webp'), quality=94, method=6)
