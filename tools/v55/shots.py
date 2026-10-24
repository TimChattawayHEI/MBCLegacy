"""Screenshots of the pub and its games in headless Chromium: python3 tools/v55/shots.py [out_dir]

Serves web/ locally, opens the game, jumps straight into the pub and each game through the page's own functions,
presses keys like a player, and saves PNGs. Prints any console errors and in-game glitches.
"""
import http.server, os, socketserver, sys, threading, time
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp/pubshots'
os.makedirs(OUT, exist_ok=True)


class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass


os.chdir(os.path.join(ROOT, 'web'))
srv = socketserver.TCPServer(('127.0.0.1', 0), Q); port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
errs = []
with sync_playwright() as pw:
    b = pw.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
    pg = b.new_page(viewport={'width': 1300, 'height': 900})
    pg.on('response', lambda r: errs.append('404 ' + r.url) if r.status == 404 else None)
    pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
    pg.on('pageerror', lambda e: errs.append('PAGEERROR ' + str(e)))
    pg.goto(f'http://127.0.0.1:{port}/index.html?pubtest'); time.sleep(3)
    ev = lambda js: pg.evaluate('s => window.__pub(s)', js)
    shot = lambda n: pg.locator('#game').screenshot(path=os.path.join(OUT, n + '.png'))
    def key(k, hold=0.08):
        pg.keyboard.down(k); time.sleep(hold); pg.keyboard.up(k); time.sleep(0.05)
    def glitch():
        g = ev('glitchInfo && glitchInfo.msg');
        if g: errs.append('GLITCH ' + g)
    ev("PUB_GAMES.forEach(g => PUB.cabs[g] = true); PUB.wallet = 50000; pubSave(); openPub('menu', null, 'tim')"); time.sleep(1.5)
    shot('pub_0'); glitch()
    for i, x in enumerate([700, 1300, 1700]):
        ev(f"PUB.x = {x}"); time.sleep(0.6); shot(f'pub_{i + 1}'); glitch()
    ev("PUB.x = 1450"); time.sleep(0.3); key('KeyK'); time.sleep(0.5); shot('pub_board'); key('KeyJ'); time.sleep(0.3)
    games = sys.argv[2].split(',') if len(sys.argv) > 2 else ['darts', 'fruit', 'pens', 'golf', 'awake', 'kiss']
    for g in games:
        ev(f"openMini('{g}', 'pub', () => {{ mode = 'pub'; }})"); time.sleep(0.8); shot(f'{g}_intro'); key('KeyJ'); time.sleep(0.6)
        if g == 'darts':
            for i in range(9):
                time.sleep(0.3); key('KeyJ'); time.sleep(0.4)
                if i == 1: shot('darts_1')
                if i % 3 == 2: time.sleep(1.8)
            time.sleep(0.5)
        elif g == 'fruit':
            for i in range(4):
                key('KeyJ'); time.sleep(0.9)
                if i == 0: shot('fruit_spin')
                time.sleep(1.2)
            shot('fruit_1'); key('Escape')
        elif g == 'pens':
            for i in range(5):
                time.sleep(0.4 + i * 0.13); key('KeyJ'); time.sleep(0.5); key('KeyJ')
                if i == 0: time.sleep(0.5); shot('pens_kick'); time.sleep(0.2); shot('pens_kick2')
                time.sleep(2.0)
        elif g == 'golf':
            for i in range(3):
                if i == 0: shot('golf_address')
                key('KeyJ'); time.sleep(0.5)
                if i == 0: shot('golf_back')
                time.sleep(0.35); key('KeyJ'); time.sleep(0.45); key('KeyJ')
                if i == 0: time.sleep(0.08); shot('golf_impact')
                time.sleep(0.6);
                if i == 0: shot('golf_fly')
                time.sleep(4.5)
        elif g == 'awake':
            for i in range(12):
                pg.keyboard.down('ArrowUp' if i % 2 else 'ArrowDown'); time.sleep(0.25); pg.keyboard.up('ArrowUp' if i % 2 else 'ArrowDown'); time.sleep(0.8)
                if i == 3: shot('awake_1')
            ev("MG.s.meter = 20"); time.sleep(0.6); shot('awake_2'); ev("MG.s.meter = 0.1"); time.sleep(3)
        elif g == 'kiss':
            for i in range(10):
                k = ['ArrowLeft', 'ArrowUp', 'ArrowRight', 'ArrowDown'][i % 4]; pg.keyboard.down(k); time.sleep(0.6); pg.keyboard.up(k)
                if i == 3: shot('kiss_1')
            ev("MG.t = 59.5"); time.sleep(1.2); shot('kiss_midnight'); time.sleep(2.5)
        time.sleep(0.5); shot(f'{g}_result'); glitch()
        print(g, ev("mode"), ev("MG ? JSON.stringify({p: MG.phase, sc: MG.score, paid: MG.paid, res: MG.res}) : 'closed'"))
        if ev("mode") == 'name': ev("nameEls.input.value = 'TIM'"); pg.click('#nameForm button[type=submit], #nameForm input[type=submit]') if pg.query_selector('#nameForm button[type=submit]') else ev("submitName(false)"); time.sleep(0.4)
        key('KeyJ'); time.sleep(0.5)
    shot('pub_after'); glitch()
    print('tab', ev('PUB.wallet'), 'pb', ev('JSON.stringify(PUB.pb)'))
    b.close()
print('errors:', errs[:20] if errs else 'none')
