"""Plays Orpington 2001 through headless: python3 tools/v73/test.py [out_dir] [stage ...]

Drives each stage scene by scene the quick way (reads each how-to card, clears each fight, walks to the exit, crosses the road,
carries the pints, waits out the queue, clears the dance floor), screenshots every place and every mechanic once, and reports
the scenes it passed through, how long each took in game time, and any page errors."""
import http.server, os, socketserver, sys, threading, time
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp/v73test'; os.makedirs(OUT, exist_ok=True)
STAGES = sys.argv[2:] or ['orp_street', 'orp_pub', 'orp_atlantis']


class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass


os.chdir(os.path.join(ROOT, 'web'))
srv = socketserver.TCPServer(('127.0.0.1', 0), Q); port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
errs = []
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_context(viewport={'width': 1280, 'height': 720}).new_page()
    pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
    pg.on('pageerror', lambda e: errs.append('PAGEERROR ' + str(e)))
    pg.goto(f'http://127.0.0.1:{port}/index.html?pubtest'); time.sleep(4)
    ev = lambda js: pg.evaluate('s => window.__pub(s)', js)
    shot = lambda n: pg.locator('#game').screenshot(path=os.path.join(OUT, n + '.png'))
    for st in STAGES:
        ev(f"profileSet('TIM', false); newRun(0, '{st}'); startStage('{st}')"); time.sleep(3)
        seen, shots_done, t0 = [], set(), time.time()
        while time.time() - t0 < 240:
            m = ev('mode')
            if m == 'clear': print(st, 'CLEARED in', round(ev('S.time')), 's of game time'); shot(st + '_clear'); break
            if m == 'comic':
                if ('comic', ev('comic && comic.id')) not in shots_done: time.sleep(4); shot(st + '_comic_' + ev('comic.id')); shots_done.add(('comic', ev('comic && comic.id')))
                ev('comicEnd()'); time.sleep(0.4); continue
            if m == 'chat': ev("pressed.add('escape')"); time.sleep(0.3); continue
            if m != 'play': time.sleep(0.5); continue
            sc = ev('S.sc'); bg = ev('S.scBg')
            if (sc, bg) not in [(a, c) for a, c, _ in seen]: seen.append((sc, bg, round(ev('S.time')))); time.sleep(1.2); shot(f'{st}_{sc}_{bg}')
            if ev('!!S.wipe'): time.sleep(0.4); continue
            if ev('!!S.howto'):
                k = ('howto', sc, ev('S.howto.title'))
                if k not in shots_done: shot(f'{st}_{sc}_howto'); shots_done.add(k)
                ev('S.howto.t = 13'); time.sleep(0.3); continue
            ev('player.hp = player.maxHp')
            if ev('!!S.frog'):
                if ('frog', ev('S.frog.round')) not in shots_done: time.sleep(2.5); shot(f'{st}_frog{ev("S.frog.round")}'); shots_done.add(('frog', ev('S.frog.round')))
                ev("if (S.frog && !S.frog.reset) { player.y = S.frog.goal === 'top' ? FT + 20 : FB - 6; }"); time.sleep(0.5); continue
            if ev('!!S.served'):
                ph = ev('S.served.phase')
                if ('served', ph) not in shots_done: time.sleep(1); shot(f'{st}_served_{ph}'); shots_done.add(('served', ph))
                if ph == 'go': ev('player.x = 520; player.y = 460; player.vx = player.vy = 0')
                elif ph == 'carry': ev('if (S.alanNpc) { S.alanNpc.x = 800; S.alanNpc.tx = 800; } player.x = 120; player.y = FT + 40; player.running = false')
                time.sleep(0.6); continue
            if ev('!!S.queue'):
                if 'queue' not in shots_done: time.sleep(5); shot(f'{st}_queue'); shots_done.add('queue')
                ev('foes.forEach(f => f.remove = true); if (S.queue) S.queue.t = 0'); time.sleep(0.4); continue
            if ev('!!S.dance'):
                if 'dance' not in shots_done: time.sleep(4); shot(f'{st}_dance'); shots_done.add('dance')
                ev('foes.forEach(f => f.remove = true); if (S.dance) S.dance.t = 0'); time.sleep(1.2); continue
            nf = ev("foes.filter(f => f.state !== 'dead' && !f.remove && f.state !== 'beaten').length")
            if nf:
                if ('fight', sc) not in shots_done: time.sleep(2); shot(f'{st}_{sc}_fight'); shots_done.add(('fight', sc))
                ev("foes.forEach(f => { f.remove = true; })"); time.sleep(0.4); continue
            if ev('!!S.exitReady'):
                if ('exit', sc) not in shots_done: shot(f'{st}_{sc}_exit'); shots_done.add(('exit', sc))
                ev('player.x = S.exitReady.dir > 0 ? W - 30 : 30'); time.sleep(0.4); continue
            time.sleep(0.4)
        else: print(st, 'DID NOT FINISH; stuck at scene', ev('S.sc'), ev('S.scBg'), 'wave', ev('S.waveIdx'), ev('JSON.stringify(S.wave)'))
        print(st, 'scenes:', seen)
    b.close()
print('errors:', [e for e in errs if 'firebase' not in e and 'build.json' not in e and 'Failed to load resource' not in e and 'TUNNEL' not in e][:8])
