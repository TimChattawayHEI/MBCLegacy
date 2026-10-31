"""Headless checks of the Orpington 2001 chapter: python3 tools/v72/test.py [out_dir]

Starts each stage in Chromium (the page's ?pubtest hook), sweeps it with screenshots, plays the Blacksmiths' getting
served (sneaks to the bar while Sue pours), skips to Mick and lets the fight run, and reports any page errors."""
import http.server, os, socketserver, sys, threading, time
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp/v72test'; os.makedirs(OUT, exist_ok=True)


class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass


os.chdir(os.path.join(ROOT, 'web'))
srv = socketserver.TCPServer(('127.0.0.1', 0), Q); port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
errs = []
with sync_playwright() as pw:
    b = pw.chromium.launch(); ctx = b.new_context(viewport={'width': 1280, 'height': 720}); pg = ctx.new_page()
    pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
    pg.on('pageerror', lambda e: errs.append('PAGEERROR ' + str(e)))
    pg.goto(f'http://127.0.0.1:{port}/index.html?pubtest'); time.sleep(4)
    ev = lambda js: pg.evaluate('s => window.__pub(s)', js)
    shot = lambda n: pg.locator('#game').screenshot(path=os.path.join(OUT, n + '.png'))
    print('route:', ev("ROUTE.slice(0, 6).join(' ')"), '| chapter of orp_pub:', ev("chapterOf('orp_pub')"), '| n:', ev("STAGES.orp_pub.n"))
    for st in ['orp_street', 'orp_pub', 'orp_atlantis']:
        ev(f"profileSet('TIM', false); newRun(0, '{st}'); startStage('{st}')"); time.sleep(6)
        print(st, 'mode', ev('mode'), 'meshy drawn:', ev('MESHY_BG[S.key] && bgReady(meshyFiles(S.key))'), 'len', ev('ST.len'))
        if st == 'orp_pub':
            # getting served: walk in while she pours
            ev("player.x = 200; player.y = FT + 90; cam.x = 0"); time.sleep(1.5); shot('pub_served_start')
            print(' served:', ev("JSON.stringify(S.served && {phase: S.served.phase, watch: S.served.watch})"), 'sue:', ev("!!S.sue"))
            for _ in range(40):
                if ev("S.served && S.served.phase === 'done'"): break
                if not ev("S.served.watch || S.served.warn > 0"): ev("player.x = Math.min(player.x + 60, 1200); player.y = FT + 110; cam.x = clamp(player.x - 400, 0, ST.len - W)")
                time.sleep(0.25)
            print(' after sneaking:', ev("S.served.phase"), 'tries', ev("S.served.tries"), 'score', ev("run.score")); shot('pub_served_end')
            # skip to Mick
            ev("foes.length = 0; S.wave = null; S.waveIdx = ST.waves.length - 1; S.served.phase = 'done'; player.x = ST.len - 200; cam.x = ST.len - W"); time.sleep(4)
            print(' boss:', ev("S.bosses.map(b => b.kind + ':' + b.state + ':' + b.hp).join(',')")); shot('pub_mick')
            for i in range(6): time.sleep(1.5); ev("player.hp = player.maxHp")
            print(' mick states seen:', ev("S.bosses.map(b => b.state).join(',')"), 'sue', ev("S.sue && S.sue.state")); shot('pub_mick2')
            ev("S.bosses.forEach(b => { b.hp = 1; }); S.sueOiT = 0.1"); time.sleep(2); shot('pub_oi')
        else:
            L = ev('ST.len')
            for i, x in enumerate(list(range(0, L - 960, 640)) + [L - 960]):
                ev(f"cam.x = {x}; player.x = {x} + 330; player.y = FT + 60; foes.forEach((f, j) => {{ f.x = {x} + 600 + j * 80; f.y = FT + 20 + (j % 3) * 50; }})")
                time.sleep(0.6); shot(f'{st}_{i}')
            if st == 'orp_atlantis': print(' beat phase:', ev('orpBeatPhase()'), 'npcs', ev('(S.npcs||[]).map(n => n.kind).join(",")'))
    b.close()
print('errors:', [e for e in errs if 'firebase' not in e and 'build.json' not in e and 'Failed to load resource' not in e and 'TUNNEL' not in e][:8])
