"""Checks the Version 81 hits headless: python3 tools/v81/test.py [out_dir]
Every lad (Thet and Ash unlocked for the test): his combo leaves trails in his own colour and his hits throw his own
sparks; his mini special plays his own effect and the colour flash. Screenshots of each lad's combo and mini special."""
import http.server, os, socketserver, sys, threading, time
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp/v81test'; os.makedirs(OUT, exist_ok=True)
LADS = ['tim', 'seb', 'byron', 'pearcy', 'kelly', 'marc', 'sam', 'thet', 'ash']


class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass


os.chdir(os.path.join(ROOT, 'web'))
srv = socketserver.TCPServer(('127.0.0.1', 0), Q); port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
errs = []; fails = []
def ok(name, c):
    print(('PASS ' if c else 'FAIL ') + name)
    if not c: fails.append(name)
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_context(viewport={'width': 1280, 'height': 720}).new_page()
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(f'http://127.0.0.1:{port}/index.html?pubtest'); time.sleep(4)
    ev = lambda js: pg.evaluate('s => window.__pub(s)', js)
    shot = lambda n: pg.locator('#game').screenshot(path=os.path.join(OUT, n + '.png'))
    ev("settings.thet = true; settings.ash = true")
    for ci, lad in enumerate(LADS):
        ev(f"profileSet('TIM', false); newRun({ci}, 'frequency'); startStage('frequency')"); time.sleep(2.5)
        for _ in range(25):
            m = ev('mode')
            if m == 'comic': ev('comicEnd()')
            elif m == 'chat': ev("pressed.add('escape')")
            elif m == 'play': break
            time.sleep(0.4)
        ok(f'{lad}: playing as him', ev('player.def.id') == lad)
        def setup(n=1):
            ev("foes.length = 0; ST.waves = []; S.wave = null; player.hp = 999; player.maxHp = 999; player.x = cam.x + 420; player.y = FT + 60; player.face = 1; setIdle(player); parts.length = 0")
            for i in range(n):
                ev(f"const f = makeFoe('kappa', player.x + {62 + i * 30}, player.y + {(i % 2) * 10}); f.state = 'hover'; f.hp = 999; f.maxHp = 999; foes.push(f)")
        setup()
        n = ev("comboOf(player).length")
        for i in range(n):
            ev("startPunch(player)")
            if i == 0: ok(f'{lad}: a trail in his colour', ev(f"parts.some(p => p.k === 'swoosh' && p.col === FX_COL['{lad}'])"))
            time.sleep(0.09); shot(f'{lad}_combo_{i}')
            if i == 0: ok(f'{lad}: his own spark', ev(f"parts.some(p => p.k === 'fx' && p.fx.indexOf('{lad}_spark') === 0)"))
            time.sleep(0.2)
        time.sleep(0.4); setup(2)
        ev("window.__fl = 0; if (!window.__wrapped) { window.__wrapped = 1; const o = v81MiniBurst; v81MiniBurst = function (p, m, l) { o(p, m, l); if (l && parts.some(q => q.k === 'v81flash')) window.__fl++; }; }")
        ev("startMini(player)")
        seen_fx = False
        for j, dt in enumerate([0.15, 0.2, 0.2, 0.25]):
            for _ in range(4):
                time.sleep(dt / 4)
                seen_fx = seen_fx or ev(f"parts.some(p => p.k === 'v81fx' && p.fx === 'mini_{lad}' && p.t >= 0)")
            shot(f'{lad}_mini_{j}')
        ok(f'{lad}: his mini special effect played', seen_fx)
        ok(f'{lad}: the flash in his colour on the last hit', ev('window.__fl') > 0)
    print('errors:', errs[:5] if errs else 'none')
    print('failed:', fails if fails else 'none')
    b.close()
