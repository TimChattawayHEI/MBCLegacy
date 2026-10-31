"""Screenshots every Orpington 2001 place with its lighting: python3 tools/v77/test.py [out_dir] [scene ...]

The player and three of the locals are stood about each place (one under its brightest light), the waves held off, and a
shot taken; on the High Street places a car's headlights are sent past for a second shot. Page errors are printed."""
import http.server, os, socketserver, sys, threading, time
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp/v77test'; os.makedirs(OUT, exist_ok=True)
WHERE = {'busstop': ('orp_street', 0, 'kappa'), 'cross': ('orp_street', 1, 'razor'), 'rambaba': ('orp_street', 2, 'frosted'), 'front': ('orp_street', 3, 'codger'),
         'lounge': ('orp_pub', 0, 'builder'), 'bar': ('orp_pub', 1, 'codger'), 'pool': ('orp_pub', 2, 'shark'), 'queue': ('orp_atlantis', 0, 'moschino'), 'floor': ('orp_atlantis', 1, 'raver')}
SC = sys.argv[2:] or list(WHERE)


class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass


os.chdir(os.path.join(ROOT, 'web'))
srv = socketserver.TCPServer(('127.0.0.1', 0), Q); port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
errs = []
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_context(viewport={'width': 1280, 'height': 720}).new_page()
    pg.on('pageerror', lambda e: errs.append('PAGEERROR ' + str(e)))
    pg.goto(f'http://127.0.0.1:{port}/index.html?pubtest'); time.sleep(4)
    ev = lambda js: pg.evaluate('s => window.__pub(s)', js)
    for name in SC:
        st, sc, k = WHERE[name]
        ev(f"profileSet('TIM', false); newRun(0, '{st}'); startStage('{st}')"); time.sleep(2.5)
        for _ in range(20):
            m = ev('mode')
            if m == 'comic': ev('comicEnd()')
            elif m == 'chat': ev("pressed.add('escape')")
            elif m == 'play': break
            time.sleep(0.4)
        ev(f"orpGoScene({sc}, 1); S.howto = null; S.frog = null; S.served = null; S.queue = null; S.dance = null; S.sue = S.sue; ST.waves = []; S.wave = null")
        # the player under the place's brightest light, three locals spread across the floor, all stood still
        ev(f"""(() => {{ const c = ORP_LIGHT['{name}'], L = c.lights.slice().sort((a, b) => b.a - a.a)[0];
            player.x = L.x; player.y = clamp(L.y, FT + 10, FB - 10);
            [150, 480, 820].forEach((x, i) => {{ const f = makeFoe('{k}', x, clamp(FT + 30 + i * 25, FT + 10, FB - 10)); f.state = 'idle'; f.cool = 99; f.face = Math.sign(player.x - x) || 1; f.extra0 = 1; foes.push(f); }});
            window.__hold = setInterval(() => {{ for (const f of foes) {{ f.vx = f.vy = 0; f.state = 'idle'; f.atk = null; f.cool = 99; }} player.hp = player.maxHp; }}, 16); }})()""")
        time.sleep(1.5); pg.locator('#game').screenshot(path=os.path.join(OUT, name + '.png'))
        if ev(f"!!ORP_LIGHT['{name}'].head"):
            ev("S.orpHead = { x: 200, d: 1 }"); time.sleep(0.45); pg.locator('#game').screenshot(path=os.path.join(OUT, name + '_head.png'))
        ev('clearInterval(window.__hold)')
        print(name, 'shot')
    print('errors:', errs[:10] if errs else 'none')
    b.close()
