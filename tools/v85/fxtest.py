"""Version 85 effects check, headless: python3 tools/v85/fxtest.py [lad index ...] [--out dir] [--root repo]
Freezes the game clock and steps it by hand, so every shot lands on the same moment: each lad holding a weapon (idle,
walk, run, the swing on the way up, at the hit and after, the dash, a jump), his combo swooshes mid-sweep and at the
end, his mini special's effect and his special. Saves a contact sheet per lad. --root points at another checkout
(the old art) for a before and after. Fails on any page error."""
import http.server, os, socketserver, sys, threading, time
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw
opt = lambda k, d: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
ROOT = opt('--root', os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
OUT = opt('--out', '/tmp/v85fx')
skip = {opt('--root', None), opt('--out', None)}
LADS = [int(a) for a in sys.argv[1:] if not a.startswith('--') and a not in skip] or [0]
os.makedirs(OUT, exist_ok=True)


class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass


os.chdir(os.path.join(ROOT, 'web'))
srv = socketserver.ThreadingTCPServer(('127.0.0.1', 0), Q); srv.daemon_threads = True; port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
errs = []
W = "p.weapon = { k: '%s', dur: 8, n: 8 };"
# label, setup js, steps of 1/60 s to run before the shot
SHOTS = [
    ('stick idle', W % 'stick' + "p.state='idle'", 6), ('stick walk', W % 'stick' + "p.state='walk'; p.walk=1.7", 1),
    ('stick run', W % 'stick' + "p.state='run'; p.running=true; p.walk=2.2", 1),
    ('swing up', W % 'stick' + "startSwing(p)", 3), ('swing hit', W % 'stick' + "startSwing(p)", 9), ('swing after', W % 'stick' + "startSwing(p)", 16),
    ('stick dash', W % 'stick' + "p.running=true; startDash(p)", 6), ('stick jump', W % 'stick' + "p.state='jump'; p.t=0.3; p.z=110; p.vz=0; p.airAtk=false", 1),
    ('net idle', W % 'net' + "p.state='idle'", 6), ('net swing', W % 'net' + "startSwing(p)", 14),
    ('helmet swing', W % 'helmet' + "startSwing(p)", 9), ('pickup', "p.state='pickup'; p.t=0.1", 1),
    ('jab mid', "startPunch(p)", 4), ('jab end', "startPunch(p)", 8),
    ('cross mid', "p.combo=1; p.comboT=0.3; p.state='punch'; startPunch(p)", 5), ('cross end', "p.combo=1; p.comboT=0.3; p.state='punch'; startPunch(p)", 9),
    ('kick mid', "p.combo=2; p.comboT=0.3; p.state='punch'; startPunch(p)", 5), ('kick end', "p.combo=2; p.comboT=0.3; p.state='punch'; startPunch(p)", 10),
    ('mini a', "p.sp = 99; startMini(p)", 8), ('mini b', "p.sp = 99; startMini(p)", 18),
    ('special a', "p.sp = 999; p.spCharge = 999; startSpecial(p)", 20), ('special b', "p.sp = 999; p.spCharge = 999; startSpecial(p)", 50),
    ('special c', "p.sp = 999; p.spCharge = 999; startSpecial(p)", 90), ('victory', "p.state='idle'; S.done=true; S.endT=99", 40),
]
with sync_playwright() as pw:
    br = pw.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--autoplay-policy=no-user-gesture-required'])
    pg = br.new_page(); pg.set_viewport_size({'width': 960, 'height': 540})
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(f'http://127.0.0.1:{port}/index.html?pubtest'); time.sleep(3)
    ev = lambda js: pg.evaluate('s => window.__pub(s)', js)
    for li in LADS:
        ev("window.__freeze = false; if (!window.__realStep) { window.__realStep = step; step = dt => window.__freeze ? false : window.__realStep(dt); }")
        ev(f"settings.thet = true; settings.ash = true; profileSet('TIM', false); newRun({li}, 'frequency'); startStageNow('frequency')"); time.sleep(5)
        lad = ev('player.def.id'); crops = []
        for label, js, n in SHOTS:
            ev("window.__freeze = false"); time.sleep(0.15)
            ev("window.__freeze = true; for (const q of parts.slice()) if (q.k === 'swoosh' || q.k === 'v81fx' || q.k === 'v81flash') parts.splice(parts.indexOf(q), 1)")
            ok = ev(f"""(() => {{ try {{ const p = player; foes.length = 0; p.inv = 99; p.hp = p.maxHp; S.done = false; p.vx = p.vy = 0; p.z = 0; p.vz = 0;
              p.atk = null; p.airAtk = false; p.weapon = null; p.face = 1; p.x = cam.x + 420; p.y = 470; p.state = 'idle'; p.t = 0; p.comboT = 0; p.combo = 0;
              p.spForm = null; p.headK = 1; {js}; for (let i = 0; i < {n}; i++) window.__realStep(1 / 60); render(); return 'ok'; }} catch (e) {{ return String(e); }} }})()""")
            box = pg.locator('canvas').first.bounding_box(); sx = box['width'] / 960; sy = box['height'] / 540
            px, py, pz = ev('[player.x - cam.x, player.y, player.z]')
            if px != px: px, py, pz = 420, 470, 0
            path = os.path.join(OUT, 'f.png'); pg.screenshot(path=path)
            im = Image.open(path); cx, cy = box['x'] + px * sx, box['y'] + (py - pz) * sy
            crops.append((label + ('' if ok == 'ok' else ' ERR'), im.crop((int(cx - 140 * sx), int(cy - 190 * sy), int(cx + 170 * sx), int(cy + 30 * sy)))))
            if ok != 'ok': print(lad, label, ok)
        ev("window.__freeze = false")
        cw, ch = crops[0][1].size; cols = 6; rows = (len(crops) + cols - 1) // cols
        sheet = Image.new('RGB', (cw * cols, (ch + 16) * rows), (20, 22, 28)); d = ImageDraw.Draw(sheet)
        for i, (label, c) in enumerate(crops):
            x, y = (i % cols) * cw, (i // cols) * (ch + 16); sheet.paste(c, (x, y + 16)); d.text((x + 4, y + 2), label, fill=(255, 210, 63))
        sheet.save(os.path.join(OUT, lad + '.png')); print('saved', lad, flush=True)
    br.close()
print('page errors:', errs[:5] if errs else 'none')
sys.exit(1 if errs else 0)
