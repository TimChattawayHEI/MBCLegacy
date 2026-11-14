"""Version 85 enemies check, headless: python3 tools/v85/foetest.py townie parkie [--out dir] [--root repo]
Freezes the game, puts each kind on screen in every state that has a row (idle, walk, the wind-ups and hits, a combo's
second punch, the anti-air uppercut, both hurts, falling, flat, getting up, grabbed, dazed, a boss's own moves) and
saves a contact sheet per kind. --root points at another checkout for a before and after. Fails on any page error."""
import http.server, os, socketserver, sys, threading, time
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw
opt = lambda k, d: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
ROOT = opt('--root', os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
OUT = opt('--out', '/tmp/v85foes')
skip = {opt('--root', None), opt('--out', None)}
KINDS = [a for a in sys.argv[1:] if not a.startswith('--') and a not in skip] or ['townie']
os.makedirs(OUT, exist_ok=True)


class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass


os.chdir(os.path.join(ROOT, 'web'))
srv = socketserver.ThreadingTCPServer(('127.0.0.1', 0), Q); srv.daemon_threads = True; port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
errs = []
COMMON = [('idle', "f.state='idle'"), ('walk', "f.state='walk'; f.vx=-90; f.walk=1.7"), ('hurt head', "f._hn=0; f.state='hurt'; f.t=0.08"),
          ('hurt body', "f._hn=1; f.state='hurt'; f.t=0.12"), ('falling', "f.state='down'; f.t=0.14"), ('flat', "f.state='down'; f.t=0.9"),
          ('getting up', "f.state='getup'; f.t=0.22"), ('grabbed', "f.state='grabbed'"), ('dazed', "f.state='stunned'")]
MELEE = [('wind-up', "f.state='windup'; f.t=0.2"), ('punch', "f.state='attack'; f.t=0.05"), ('recover', "f.state='recover'; f.t=0.05"),
         ('2nd wind-up', "f.combo2n=1; f.state='windup'; f.t=0.2"), ('2nd punch', "f.combo2n=1; f.state='attack'; f.t=0.05"),
         ('uppercut wind', "f.uppercut=true; f.state='windup'; f.t=0.1"), ('uppercut', "f.uppercut=true; f.state='attack'; f.t=0.05")]
BOSS = {'parkie': [('picker wind', "f.state='meleeWind'; f.t=0.3"), ('picker jab', "f.state='melee'; f.t=0.05"), ('rest', "f._ps='melee'; f._from='melee'; f.state='rest'; f.t=0.1"),
                   ('snatch wind', "f.state='snatchWind'; f.t=0.3"), ('snatch', "f.state='snatch'; f.t=0.1"), ('ball wind', "f.state='ballWind'; f.t=0.3"),
                   ('whistle wind', "f.state='closeWind'; f.t=0.3"), ('whistle', "f.state='close'; f.t=0.05")]}
with sync_playwright() as pw:
    br = pw.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--autoplay-policy=no-user-gesture-required'])
    pg = br.new_page(); pg.set_viewport_size({'width': 960, 'height': 540})
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(f'http://127.0.0.1:{port}/index.html?pubtest'); time.sleep(3)
    ev = lambda js: pg.evaluate('s => window.__pub(s)', js)
    ev("profileSet('TIM', false); newRun(0, 'frequency'); startStageNow('frequency')"); time.sleep(5)
    ev("window.__realStep = window.__realStep || step; step = dt => false")
    for kind in KINDS:
        boss = kind in BOSS; crops = []
        for label, js in COMMON[:2] + (BOSS[kind] if boss else MELEE) + COMMON[2:]:
            ok = ev(f"""(() => {{ try {{ foes.length = 0; parts.length = 0; const p = player; p.x = cam.x + 140; p.y = 470; p.state = 'idle';
              const f = {"makeHB('" + kind + "')" if boss else "makeFoe('" + kind + "', 0, 0, 'idle')"}; f.x = cam.x + 520; f.y = 470; f.z = 0; f.face = -1; f.vx = f.vy = 0; f.t = 0;
              f.inv = 0; f.flash = 0; f.say = null; f.combo2n = 0; f.uppercut = false; f._ps = null; foes.push(f); {js}; render(); return 'ok'; }} catch (e) {{ return String(e); }} }})()""")
            box = pg.locator('canvas').first.bounding_box(); sx = box['width'] / 960; sy = box['height'] / 540
            path = os.path.join(OUT, 'f.png'); pg.screenshot(path=path)
            im = Image.open(path); cx, cy = box['x'] + (520 + 0) * sx, box['y'] + 470 * sy
            crops.append((label + ('' if ok == 'ok' else ' ERR'), im.crop((int(cx - 130 * sx), int(cy - 190 * sy), int(cx + 110 * sx), int(cy + 30 * sy)))))
            if ok != 'ok': print(kind, label, ok)
        cw, ch = crops[0][1].size; cols = 6; rows = (len(crops) + cols - 1) // cols
        sheet = Image.new('RGB', (cw * cols, (ch + 16) * rows), (20, 22, 28)); d = ImageDraw.Draw(sheet)
        for i, (label, c) in enumerate(crops):
            x, y = (i % cols) * cw, (i // cols) * (ch + 16); sheet.paste(c, (x, y + 16)); d.text((x + 4, y + 2), label, fill=(255, 210, 63))
        sheet.save(os.path.join(OUT, kind + '.png')); print('saved', kind, flush=True)
    br.close()
print('page errors:', errs[:5] if errs else 'none')
sys.exit(1 if errs else 0)
