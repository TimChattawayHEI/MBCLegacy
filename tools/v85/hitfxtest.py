"""Version 85 hit effects check, headless: python3 tools/v85/hitfxtest.py [lad index ...] [--out dir]
Freezes the clock and steps it by hand: a jab on a head (sweat), a combo ender (white then the lad's colour, speed lines),
a weapon hit (the thwack), the body landing (the dust ring) and the special starting (the burst and the dim).
Saves a contact sheet per lad. Fails on any page error."""
import http.server, os, socketserver, sys, threading, time
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw
opt = lambda k, d: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = opt('--out', '/tmp/v85hitfx'); os.makedirs(OUT, exist_ok=True)
LADS = [int(a) for a in sys.argv[1:] if not a.startswith('--') and a != OUT] or [0]
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
os.chdir(os.path.join(ROOT, 'web'))
srv = socketserver.ThreadingTCPServer(('127.0.0.1', 0), Q); srv.daemon_threads = True; port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
errs = []
HIT = "applyHit(p, f, %s, 1)"
SHOTS = [  # label, js after setup, frames to step
    ('jab: sweat', HIT % "{ dmg: 4, kd: false, kb: 90, hs: 0.05 }", 6), ('jab later', HIT % "{ dmg: 4, kd: false, kb: 90, hs: 0.05 }", 10),
    ('ender: white', HIT % "{ dmg: 18, kd: true, kb: 320, hs: 0.09 }", 2), ('ender: colour', HIT % "{ dmg: 18, kd: true, kb: 320, hs: 0.09 }", 9),
    ('ender: lines', HIT % "{ dmg: 18, kd: true, kb: 320, hs: 0.09 }", 13),
    ('landing', HIT % "{ dmg: 18, kd: true, kb: 320, hs: 0.09 }", 30), ('landing later', HIT % "{ dmg: 18, kd: true, kb: 320, hs: 0.09 }", 36),
    ('weapon hit', HIT % "{ dmg: 10, kd: false, kb: 120, hs: 0.05, weapon: true }", 3), ('weapon later', HIT % "{ dmg: 10, kd: false, kb: 120, hs: 0.05, weapon: true }", 6),
    ('special a', "p.meter = 100; startSpecial(p)", 3), ('special b', "p.meter = 100; startSpecial(p)", 7), ('special c', "p.meter = 100; startSpecial(p)", 12),
]
with sync_playwright() as pw:
    br = pw.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--mute-audio'])
    pg = br.new_page(); pg.set_viewport_size({'width': 960, 'height': 540})
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(f'http://127.0.0.1:{port}/index.html?pubtest'); time.sleep(3)
    ev = lambda js: pg.evaluate('s => window.__pub(s)', js)
    for li in LADS:
        ev("window.__freeze = false; if (!window.__realStep) { window.__realStep = step; step = dt => window.__freeze ? false : window.__realStep(dt); }")
        ev(f"settings.thet = true; settings.ash = true; profileSet('TIM', false); newRun({li}, 'frequency'); startStageNow('frequency')"); time.sleep(5)
        lad = ev('player.def.id'); crops = []
        for label, js, n in SHOTS:
            ev("window.__freeze = false"); time.sleep(0.1); ev("window.__freeze = true")
            ok = ev(f"""(() => {{ try {{ parts.length = 0; foes.length = 0; hitstop = 0; shake = 0; v85DimAt = -9; const p = player; p.inv = 99; p.hp = p.maxHp; p.state = 'idle'; p.t = 0;
              p.atk = null; p.weapon = null; p.face = 1; p.x = cam.x + 330; p.y = 450; p.z = 0; p.vx = p.vy = p.vz = 0;
              const f = makeFoe('townie', 0, 0, 'idle'); f.x = cam.x + 400; f.y = 450; f.z = 0; f.face = -1; f.hp = 999; f.state = 'idle'; f._hn = 0; foes.push(f);
              {js}; for (let i = 0; i < {n}; i++) window.__realStep(1 / 60); render(); return 'ok'; }} catch (e) {{ return String(e); }} }})()""")
            box = pg.locator('canvas').first.bounding_box(); s = box['width'] / 960
            path = os.path.join(OUT, 'f.png'); pg.screenshot(path=path); im = Image.open(path)
            cx, cy = box['x'] + 380 * s, box['y'] + 450 * s
            crops.append((label + ('' if ok == 'ok' else ' ERR ' + ok[:30]), im.crop((int(cx - 220 * s), int(cy - 230 * s), int(cx + 260 * s), int(cy + 40 * s)))))
        ev("window.__freeze = false")
        cw, ch = crops[0][1].size; cols = 4; rows = (len(crops) + cols - 1) // cols
        sheet = Image.new('RGB', (cw * cols, (ch + 16) * rows), (20, 22, 28)); d = ImageDraw.Draw(sheet)
        for i, (label, c) in enumerate(crops):
            x, y = (i % cols) * cw, (i // cols) * (ch + 16); sheet.paste(c, (x, y + 16)); d.text((x + 4, y + 2), label, fill=(255, 210, 63))
        sheet.save(os.path.join(OUT, lad + '.png')); print('saved', lad, flush=True)
    br.close()
print('page errors:', errs[:5] if errs else 'none')
sys.exit(1 if errs else 0)
