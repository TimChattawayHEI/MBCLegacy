"""Version 85 small effects check, headless: python3 tools/v85/vfxtest.py [--out dir] [--root repo]
Puts one of each small effect (puffs in three sizes, dust in two, a flame, a sparkle, drops, a heart, a Z, debris and
glass) on a stage with the clock stopped, and shoots them at four moments of their life (10, 30, 55 and 80 per cent).
--root points at another checkout (the old drawing) for a before and after. Fails on any page error."""
import http.server, os, socketserver, sys, threading, time
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw
opt = lambda k, d: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
ROOT = opt('--root', os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
OUT = opt('--out', '/tmp/v85vfx'); os.makedirs(OUT, exist_ok=True)
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
os.chdir(os.path.join(ROOT, 'web'))
srv = socketserver.ThreadingTCPServer(('127.0.0.1', 0), Q); srv.daemon_threads = True; port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
# label, particle (x is a column, the rest as the game makes them)
SET = [
    ('puff small', "{ k: 'puff', vx: 20, vy: 0, vz: 0, r: 4 }"),
    ('puff', "{ k: 'puff', vx: 20, vy: 0, vz: 0, r: 8 }"),
    ('puff big', "{ k: 'puff', vx: 20, vy: 0, vz: 0, r: 24 }"),
    ('dust', "{ k: 'dust', vx: 20, vz: 0, r: 7 }"),
    ('dust big', "{ k: 'dust', vx: 20, vz: 0, r: 11 }"),
    ('flame', "{ k: 'flame', vx: 10, vz: 0, r: 12 }"),
    ('sparkle', "{ k: 'sparkle' }"),
    ('drop', "{ k: 'drop', vx: 0, vz: 0, r: 5 }"),
    ('drop small', "{ k: 'drop', vx: 0, vz: 0, r: 3 }"),
    ('heart', "{ k: 'heart' }"),
    ('z', "{ k: 'z' }"),
    ('debris', "{ k: 'debris', vx: 0, vz: 0, r: 7, col: '#d9b048', rot: 0.3, vr: 0 }"),
    ('debris green', "{ k: 'debris', vx: 0, vz: 0, r: 4, col: '#5aa04a', rot: 2.0, vr: 0 }"),
    ('glass', "{ k: 'debris', vx: 0, vz: 0, r: 3, col: '#bfe6ff', rot: 4.0, vr: 0 }"),
]
KS = [0.1, 0.3, 0.55, 0.8]
errs = []
with sync_playwright() as pw:
    br = pw.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--mute-audio'])
    pg = br.new_page(); pg.set_viewport_size({'width': 960, 'height': 540})
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(f'http://127.0.0.1:{port}/index.html?pubtest'); time.sleep(3)
    ev = lambda js: pg.evaluate('s => window.__pub(s)', js)
    ev("profileSet('TIM', false); newRun(0, 'frequency'); startStageNow('frequency')"); time.sleep(4)
    ev("step = dt => false; window.__render = window.__render || render; render = () => {}; 0")
    cell = 64; shots = []
    for kk in KS:
        js = "foes.length = 0; player.x = -9999; cam.x = 0; parts.length = 0; const P = [" + ','.join(p for _, p in SET) + "];"
        js += f"P.forEach((p, i) => {{ Object.assign(p, {{ x: 40 + i * {cell}, y: 470, z: 60, t: {kk} * 1, life: 1 }}); parts.push(p); }}); window.__render(); 0"
        ev(js); time.sleep(0.15)
        p = os.path.join(OUT, 'f.png'); pg.locator('canvas').first.screenshot(path=p)
        im = Image.open(p).convert('RGB').resize((960, 540)); shots.append(im.crop((0, 340, 960, 460)))
    sheet = Image.new('RGB', (960 * 2, 130 * len(KS) + 24), (20, 22, 28)); d = ImageDraw.Draw(sheet)
    for i, (label, _) in enumerate(SET): d.text((8 + (40 + i * cell - 26) * 2, 4), label, fill=(255, 210, 63))
    for r, im in enumerate(shots):
        sheet.paste(im.resize((1920, 240)).crop((0, 0, 1920, 130)) if False else im.resize((1920, 240)).crop((0, 50, 1920, 180)), (0, 20 + r * 130))
        d.text((4, 24 + r * 130), f'{int(KS[r] * 100)}%', fill=(140, 220, 255))
    sheet.save(os.path.join(OUT, 'vfx.png'))
    br.close()
for e in errs: print('page error:', e)
print('saved', os.path.join(OUT, 'vfx.png'), '| PASS' if not errs else f'| {len(errs)} page errors')
sys.exit(1 if errs else 0)
