"""Checks the Version 80 hits headless: python3 tools/v80/test.py [out_dir]
Tim's combo facing right and left (swoosh trails and his own sparks, screenshots), and Seb unchanged (old spark, no trail)."""
import http.server, os, socketserver, sys, threading, time
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp/v80test'; os.makedirs(OUT, exist_ok=True)


class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass


os.chdir(os.path.join(ROOT, 'web'))
srv = socketserver.TCPServer(('127.0.0.1', 0), Q); port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
errs = []; ok = lambda name, c: print(('PASS ' if c else 'FAIL ') + name)
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_context(viewport={'width': 960, 'height': 540}).new_page()
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(f'http://127.0.0.1:{port}/index.html?pubtest'); time.sleep(4)
    ev = lambda js: pg.evaluate('s => window.__pub(s)', js)
    shot = lambda n: pg.locator('#game').screenshot(path=os.path.join(OUT, n + '.png'))
    def play(lad):
        ev(f"profileSet('TIM', false); newRun({lad}, 'frequency'); startStage('frequency')"); time.sleep(2.5)
        for _ in range(25):
            m = ev('mode')
            if m == 'comic': ev('comicEnd()')
            elif m == 'chat': ev("pressed.add('escape')")
            elif m == 'play': break
            time.sleep(0.4)
    def setup(face):
        ev(f"foes.length = 0; ST.waves = []; S.wave = null; player.hp = 999; player.x = cam.x + 480; player.y = FT + 60; player.face = {face}; setIdle(player)")
        ev(f"const f = makeFoe('kappa', player.x + {face} * 62, player.y); f.state = 'hover'; f.hp = 999; f.maxHp = 999; foes.push(f)")
    def combo(name, n):
        for i in range(n):
            ev("startPunch(player)"); time.sleep(0.06); shot(f'{name}_{i}_swing'); time.sleep(0.05); shot(f'{name}_{i}_hit'); time.sleep(0.15)

    play(0)
    ok('playing as Tim', ev('player.def.id') == 'tim')
    setup(1); ev("startPunch(player)")
    ok('a jab queues a swoosh', ev("parts.some(p => p.k === 'swoosh' && p.shape === 'jab')"))
    time.sleep(0.15)
    ok("Tim's hit plays his spark", ev("parts.some(p => p.k === 'fx' && p.fx === 'tim_spark')"))
    time.sleep(0.4); setup(1); combo('right', 4)
    ok('the swooshes drew (frames cached)', ev("Object.keys(swCache).length") >= 3)
    time.sleep(0.4); setup(-1); ev("startPunch(player)"); time.sleep(0.15)
    ok('facing left, the spark is flipped', ev("parts.some(p => p.k === 'fx' && p.fx === 'tim_spark' && p.flip === -1)"))
    time.sleep(0.4); setup(-1); combo('left', 4)

    play(1)
    ok('playing as someone else', ev('player.def.id') != 'tim')
    setup(1); ev("startPunch(player)"); time.sleep(0.15)
    if ev("Object.keys(FX_LADS).length > 1"): print('SKIP other lads unchanged: Version 81 switched every lad on (tools/v81/test.py checks them)')
    else:
        ok('no swoosh for lads not switched on yet', ev("!parts.some(p => p.k === 'swoosh')"))
        ok('they keep the old spark', ev("parts.some(p => p.k === 'fx' && (p.fx === 'hit' || p.fx === 'hitbig'))"))
    shot('other_lad')
    print('errors:', errs[:5] if errs else 'none')
    b.close()
