"""Version 85 smashables check, headless: python3 tools/v85/smashtest.py [stage ...] [--out dir]
For every breakable on each stage: whole, dented after one hit, broken (the pop), the food in the air, and the wreck
left on the floor. Saves a contact sheet per stage. Fails on any page error or a missing sprite."""
import http.server, os, socketserver, sys, threading, time
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw
opt = lambda k, d: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = opt('--out', '/tmp/v85smash'); os.makedirs(OUT, exist_ok=True)
STAGES = [a for a in sys.argv[1:] if not a.startswith('--') and a != OUT] or [
    'frequency', 'soundz', 'arrival', 'social', 'pegnine', 'airport', 'divebar', 'beach', 'club', 'ramsden', 'nl_station', 'nl_train', 'nl_cx', 'nl_alley']
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
os.chdir(os.path.join(ROOT, 'web'))
srv = socketserver.ThreadingTCPServer(('127.0.0.1', 0), Q); srv.daemon_threads = True; port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
errs, bad = [], []
SHOTS = [('whole', 0, 1), ('dented', 1, 2), ('broken', 2, 2), ('pop', 0, 12), ('wreck', 0, 50)]   # label, hits, frames
with sync_playwright() as pw:
    br = pw.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--mute-audio'])
    pg = br.new_page(); pg.set_viewport_size({'width': 960, 'height': 540})
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(f'http://127.0.0.1:{port}/index.html?pubtest'); time.sleep(3)
    ev = lambda js: pg.evaluate('s => window.__pub(s)', js)
    ev("window.__freeze = false; if (!window.__realStep) { window.__realStep = step; step = dt => window.__freeze ? false : window.__realStep(dt); }")
    for st in STAGES:
        ev("window.__freeze = false")
        ev(f"settings.thet = true; settings.ash = true; profileSet('TIM', false); newRun(0, '{st}'); startStageNow('{st}')"); time.sleep(5)
        n = ev("(window.__bs = breakables.filter(b => !b.tx).sort((a, c) => a.x - c.x)).length"); crops = []
        miss = ev("breakables.filter(b => SMASH[b.type]).flatMap(b => [b.type + '_d', b.type + '_w'].concat(SMASH[b.type].isnew ? [b.type] : [])).filter(k => !bgImg('props/' + k))")
        if miss: bad.append((st, miss))
        for bi in range(n):
            ev("window.__freeze = true")
            ev(f"""(() => {{ foes.length = 0; shots.length = 0; const b = window.__bs[{bi}]; window.__b = {{ ...b }}; window.__bo = b;
              const p = player; p.inv = 99; p.state = 'idle'; p.x = b.x - 170; p.y = b.y; p.face = 1; for (let i = 0; i < 120; i++) window.__realStep(1 / 60); render(); }})()"""); ev("window.__freeze = false"); time.sleep(1.5); ev("window.__freeze = true; player.x = window.__b.x - 170; player.y = window.__b.y; foes.length = 0")
            for label, hits, frames in SHOTS:
                ok = ev(f"""(() => {{ try {{ foes.length = 0; for (let i = 0; i < {hits}; i++) hitBreakable(window.__bo); for (let i = 0; i < {frames}; i++) window.__realStep(1 / 60);
                  cam.x = window.__b.x - 480; render(); return [Math.round(window.__b.x - cam.x), Math.round(window.__b.y)]; }} catch (e) {{ return String(e); }} }})()""")
                if isinstance(ok, str): crops.append((label + ' ERR ' + ok[:40], Image.new('RGB', (10, 10)))); continue
                box = pg.locator('canvas').first.bounding_box(); s = box['width'] / 960
                path = os.path.join(OUT, 'f.png'); pg.screenshot(path=path); im = Image.open(path)
                cx, cy = box['x'] + ok[0] * s, box['y'] + ok[1] * s
                crops.append((f"{ev('window.__b.type')} {label}", im.crop((int(cx - 150 * s), int(cy - 230 * s), int(cx + 150 * s), int(cy + 50 * s))).resize((300, 280))))
        ev("window.__freeze = false")
        if not crops: print(st, 'no breakables'); continue
        cw, ch = 300, 280; cols = len(SHOTS); rows = (len(crops) + cols - 1) // cols
        sheet = Image.new('RGB', (cw * cols, (ch + 16) * rows), (20, 22, 28)); d = ImageDraw.Draw(sheet)
        for i, (label, c) in enumerate(crops):
            x, y = (i % cols) * cw, (i // cols) * (ch + 16); sheet.paste(c, (x, y + 16)); d.text((x + 4, y + 2), label, fill=(255, 210, 63))
        sheet.save(os.path.join(OUT, st + '.png')); print('saved', st, n, flush=True)
    br.close()
print('missing sprites:', bad or 'none')
print('page errors:', errs[:5] if errs else 'none')
sys.exit(1 if errs or bad else 0)
