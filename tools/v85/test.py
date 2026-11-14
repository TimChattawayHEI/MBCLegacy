"""Version 85 check, headless: python3 tools/v85/test.py [lad index ...] [--out dir]
Starts The Frequency as each lad, clears the foes, then puts him through every state that has a new row (idle, walk,
run, the jab/cross/kick combo, the jump and the flying kick, the dash, both hurts, dazed, held, knocked down and up, the
special, the mini, the pickup, a throw, the stage won) and saves a contact sheet of crops round him. Fails on any page error."""
import http.server, os, socketserver, sys, threading, time
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
args = [a for a in sys.argv[1:] if not a.startswith('--')]
OUT = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else '/tmp/v85test'
if '--out' in sys.argv: args.remove(OUT)
os.makedirs(OUT, exist_ok=True)
LADS = [int(a) for a in args] or [0]


class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass


os.chdir(os.path.join(ROOT, 'web'))
srv = socketserver.ThreadingTCPServer(('127.0.0.1', 0), Q); srv.daemon_threads = True; port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
errs = []
SHOTS = [
    ('idle', "p.state='idle'"), ('walk', "p.state='walk'; p.walk=(p.walk||0)+1.7"), ('run', "p.state='run'; p.walk=(p.walk||0)+2.2"),
    ('jab', "startPunch(p)", 0.09), ('cross', "p.combo=1; startPunch(p)", 0.16), ('kick', "p.combo=2; startPunch(p)", 0.16),
    ('jump up', "p.state='jump'; p.t=0.03; p.z=40; p.vz=600; p.airAtk=false"), ('jump top', "p.state='jump'; p.t=0.3; p.z=120; p.vz=0; p.airAtk=false"),
    ('jump down', "p.state='jump'; p.t=0.5; p.z=60; p.vz=-500; p.airAtk=false"), ('flying kick', "p.state='jump'; p.t=0.3; p.z=110; p.vz=0; p.airAtk=true; p.atkT=0.15"),
    ('land', "p.state='land'; p.t=0.05"), ('dash', "p.running=true; startDash(p)", 0.14),
    ('hurt head', "p.hurtN=2; p.state='hurt'; p.t=0.06"), ('hurt body', "p.hurtN=1; p.state='hurt'; p.t=0.1"),
    ('dazed', "p.state='stunned'; p.t=0; p.stunDur=3"), ('held', "p.state='netted'; p.heldBy='x'; p.t=0"),
    ('falling', "p.state='down'; p.t=0.12"), ('flat', "p.state='down'; p.t=0.8"), ('getting up', "p.state='getup'; p.t=0.22"),
    ('special', "p.state='special'; p.t=0.5"), ('mini', "p.state='mini'; p.t=0.25; p.miniFace=1; p.miniHits=9"), ('pickup', "p.state='pickup'; p.t=0.1"),
    ('throw', "p.state='throw'; p.t=0.3"), ('victory', "p.state='idle'; S.done=true; S.endT=99", 0.7),
]
with sync_playwright() as pw:
    br = pw.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--autoplay-policy=no-user-gesture-required'])
    pg = br.new_page(); pg.set_viewport_size({'width': 960, 'height': 540})
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(f'http://127.0.0.1:{port}/index.html?pubtest'); time.sleep(3)
    ev = lambda js: pg.evaluate('s => window.__pub(s)', js)
    for li in LADS:
        ev(f"settings.thet = true; settings.ash = true; profileSet('TIM', false); newRun({li}, 'frequency'); startStageNow('frequency')"); time.sleep(5)
        lad = ev('player.def.id'); crops = []
        for shot in SHOTS:
            label, js = shot[0], shot[1]; wait = shot[2] if len(shot) > 2 else 0.12
            ev(f"(() => {{ const p = player; foes.length = 0; p.inv = 99; p.hp = p.maxHp; S.done = false; p.vx = p.vy = 0; p.z = 0; p.vz = 0; p.atk = null; p.airAtk = false; p.weapon = null; p.face = 1; p.x = cam.x + 420; p.y = 470; {js}; }})()")
            time.sleep(wait)
            box = pg.locator('canvas').first.bounding_box(); sx = box['width'] / 960; sy = box['height'] / 540
            px, py, pz = ev('[player.x - cam.x, player.y, player.z]')
            path = os.path.join(OUT, 'f.png'); pg.screenshot(path=path)
            im = Image.open(path)
            cx, cy = box['x'] + px * sx, box['y'] + (py - pz) * sy
            crops.append((label, im.crop((int(cx - 110 * sx), int(cy - 170 * sy), int(cx + 130 * sx), int(cy + 30 * sy)))))
        cw, ch = crops[0][1].size; cols = 6; rows = (len(crops) + cols - 1) // cols
        sheet = Image.new('RGB', (cw * cols, (ch + 16) * rows), (20, 22, 28)); d = ImageDraw.Draw(sheet)
        for i, (label, c) in enumerate(crops):
            x, y = (i % cols) * cw, (i // cols) * (ch + 16); sheet.paste(c, (x, y + 16)); d.text((x + 4, y + 2), label, fill=(255, 210, 63))
        sheet.save(os.path.join(OUT, lad + '.png')); print('saved', lad, flush=True)
    br.close()
print('page errors:', errs[:5] if errs else 'none')
sys.exit(1 if errs else 0)
