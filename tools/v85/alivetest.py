"""Version 85 livelier backgrounds check, headless: python3 tools/v85/alivetest.py stage [--out dir] [--at x,x,...] [--t s,s,...]
Puts the camera at each x (default: every 900px along the stage), with no fighters, and shoots the screen at a few
clock times, so the flicker, the drips and the critters can be compared frame to frame. Fails on any page error."""
import http.server, os, socketserver, sys, threading, time
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw
opt = lambda k, d: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = opt('--out', '/tmp/v85alive'); os.makedirs(OUT, exist_ok=True)
skip = {opt('--out', None), opt('--at', None), opt('--t', None)}
STAGES = [a for a in sys.argv[1:] if not a.startswith('--') and a not in skip]
TS = [float(v) for v in opt('--t', '0.1,0.25,3.4,8.1').split(',')]
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
os.chdir(os.path.join(ROOT, 'web'))
srv = socketserver.ThreadingTCPServer(('127.0.0.1', 0), Q); srv.daemon_threads = True; port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
errs = []
with sync_playwright() as pw:
    br = pw.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--mute-audio'])
    pg = br.new_page(); pg.set_viewport_size({'width': 960, 'height': 540})
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(f'http://127.0.0.1:{port}/index.html?pubtest'); time.sleep(3)
    ev = lambda js: pg.evaluate('s => window.__pub(s)', js)
    for st in STAGES:
        ev(f"profileSet('TIM', false); newRun(0, '{st}'); startStageNow('{st}')"); time.sleep(4)
        ev("step = dt => false; window.__render = window.__render || render; render = () => {}")
        ln = ev("ST.len || 3400")
        xs = [int(v) for v in opt('--at', '').split(',') if v] or list(range(0, max(1, ln - 960) + 1, 900))
        shots = []
        for x in xs:
            for t in TS:
                ev(f"foes.length = 0; player.x = -9999; cam.x = {x}; time = {t}; window.__render()")
                p = os.path.join(OUT, 'f.png'); pg.locator('canvas').first.screenshot(path=p)
                shots.append((f'{st} x{x} t{t}', Image.open(p).convert('RGB').resize((960, 540))))
        cols = len(TS); rows = len(xs)
        sheet = Image.new('RGB', (480 * cols, 286 * rows), (20, 22, 28)); d = ImageDraw.Draw(sheet)
        for i, (label, im) in enumerate(shots):
            x, y = (i % cols) * 480, (i // cols) * 286; sheet.paste(im.resize((480, 270)), (x, y + 16)); d.text((x + 4, y + 2), label, fill=(255, 210, 63))
        sheet.save(os.path.join(OUT, st + '.png'))
        for i, (label, im) in enumerate(shots): im.save(os.path.join(OUT, f'{st}_{i}.png'))
        if '--gif' in sys.argv:   # a short clip at the first x, for showing the movement
            fr = []
            for i in range(60):
                ev(f"cam.x = {xs[0]}; time = {TS[0]} + {i} * 0.1; window.__render()")
                p = os.path.join(OUT, 'f.png'); pg.locator('canvas').first.screenshot(path=p); fr.append(Image.open(p).convert('RGB').resize((640, 360)))
            fr[0].save(os.path.join(OUT, st + '.gif'), save_all=True, append_images=fr[1:], duration=100, loop=0)
        print('saved', st, len(shots), flush=True)
    br.close()
print('page errors:', errs[:5] if errs else 'none')
sys.exit(1 if errs else 0)
