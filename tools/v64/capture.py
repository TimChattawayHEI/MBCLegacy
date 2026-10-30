"""The current backdrop of a stage as one long picture, as Meshy's layout reference: python3 tools/v64/capture.py <stage> [out.png]

Serves web/, starts the stage, and for each screen across the stage clears the canvas and calls drawStageBg() only
(no lads, foes, items or HUD), then stitches the screens into one image the full length of the stage (ST.len units),
at the game's native scale (1 pixel = 2 units). Hide things the game draws itself over the backdrop with HIDE.
"""
import base64, http.server, io, os, socketserver, sys, threading, time
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
stage = sys.argv[1]; out = sys.argv[2] if len(sys.argv) > 2 else f'/tmp/{stage}_ref.png'
HIDE = {'frequency': 'S.tree = null;', 'arrival': "S.props = S.props.filter(p => p.k !== 'peg');", 'pegnine': "S.props = S.props.filter(p => !['peg', 'rota', 'smoker', 'chair'].includes(p.k));", 'social': 'S.fruit = null;'}


class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass


os.chdir(os.path.join(ROOT, 'web'))
srv = socketserver.TCPServer(('127.0.0.1', 0), Q); port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_page(viewport={'width': 960, 'height': 540})
    pg.goto(f'http://127.0.0.1:{port}/index.html?pubtest'); time.sleep(4)
    ev = lambda js: pg.evaluate('s => window.__pub(s)', js)
    ev(f"profileSet('TIM', false); newRun(0, '{stage}'); startStageNow('{stage}')"); time.sleep(6)
    L = ev('ST.len'); ev(HIDE.get(stage, ''))
    shots = []
    for x in list(range(0, L - 960, 960)) + [L - 960]:
        url = ev(f"""(() => {{ mode = 'capture'; cam.x = {x}; const c = ctx.canvas; ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.clearRect(0, 0, c.width, c.height); ctx.restore();
          ctx.save(); const k = c.width / W; ctx.setTransform(k, 0, 0, k, 0, 0); drawStageBg(); ctx.restore(); return c.toDataURL(); }})()""")
        im = Image.open(io.BytesIO(base64.b64decode(url.split(',')[1]))).convert('RGB')
        shots.append((x, im.resize((480, 270), Image.NEAREST)))
    strip = Image.new('RGB', (L // 2, 270))
    for x, im in shots: strip.paste(im, (x // 2, 0))
    strip.save(out); print(out, strip.size, 'FT', ev('FT'), 'FB', ev('FB'))
    b.close()
