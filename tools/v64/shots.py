"""Screenshots of a stage across its length, with the lad, foes and breakables in shot: python3 tools/v64/shots.py <stage> [out_dir] [phone]"""
import http.server, os, socketserver, sys, threading, time
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
stage = sys.argv[1]; OUT = sys.argv[2] if len(sys.argv) > 2 else '/tmp/v64shots'; phone = len(sys.argv) > 3
os.makedirs(OUT, exist_ok=True)


class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass


os.chdir(os.path.join(ROOT, 'web'))
srv = socketserver.TCPServer(('127.0.0.1', 0), Q); port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
errs = []
with sync_playwright() as pw:
    b = pw.chromium.launch()
    ctx = b.new_context(viewport={'width': 844, 'height': 390}, has_touch=True, is_mobile=True) if phone else b.new_context(viewport={'width': 1280, 'height': 720})
    pg = ctx.new_page()
    pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
    pg.on('pageerror', lambda e: errs.append('PAGEERROR ' + str(e)))
    pg.goto(f'http://127.0.0.1:{port}/index.html?pubtest'); time.sleep(4)
    ev = lambda js: pg.evaluate('s => window.__pub(s)', js)
    ev(f"profileSet('TIM', false); newRun(0, '{stage}'); startStage('{stage}')"); time.sleep(7)
    L = ev('ST.len'); tag = 'phone' if phone else 'desk'
    for i, x in enumerate(list(range(0, L - 960, 640)) + [L - 960]):
        ev(f"cam.x = {x}; player.x = {x} + 330; player.y = FT + 60; foes.forEach((f, j) => {{ f.x = {x} + 600 + j * 80; f.y = FT + 20 + (j % 3) * 50; }}); breakables.forEach((o, j) => {{ o.x = {x} + 470 + j * 260; }})")
        time.sleep(0.5); pg.locator('#game').screenshot(path=os.path.join(OUT, f'{stage}_{tag}_{i}.png'))
    print('meshy drawn:', ev('MESHY_BG[S.key] && bgReady(meshyFiles(S.key))'))
    b.close()
print('errors:', [e for e in errs if 'firebase' not in e and 'build.json' not in e and 'Failed to load resource' not in e and 'TUNNEL' not in e][:5])
