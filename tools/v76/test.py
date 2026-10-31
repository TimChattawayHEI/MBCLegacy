"""Tries every one of the Orpington 2001 crowd headless: python3 tools/v76/test.py [out_dir] [kind ...]

For each kind: a scene of the High Street (or the pub, or the dance floor, where they live), two of them spawned, the player
kept topped up, each of their own moves started by hand once it's free to, a screenshot at the moment of the move, and a
list of the states each one went through (so a move that never fires shows up). Page errors are printed."""
import http.server, os, socketserver, sys, threading, time
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp/v76test'; os.makedirs(OUT, exist_ok=True)
WHERE = {'kappa': ('orp_street', 0), 'razor': ('orp_street', 0), 'frosted': ('orp_street', 2), 'scrunchie': ('orp_street', 2), 'garagemc': ('orp_street', 3),
         'builder': ('orp_pub', 1), 'codger': ('orp_pub', 1), 'shark': ('orp_pub', 2), 'moschino': ('orp_atlantis', 1), 'raver': ('orp_atlantis', 1)}
# the move each one is made to try, and how far from the player to stand for it
MOVES = {'kappa': [('whipWind', 130)], 'razor': [('rideWind', 320), ('kickWind', 180)], 'frosted': [('spinKickWind', 80), ('kneeSlideWind', 200)],
         'scrunchie': [('throwWind', 220)], 'garagemc': [('barsWind', 140)], 'builder': [('bargeWind', 300), ('throwWind', 300)],
         'codger': [('hookWind', 140)], 'shark': [('breakWind', 260)], 'moschino': [('shakeWind', 110)], 'raver': [('whistleWind', 80), ('flurryWind', 50)]}
KINDS = sys.argv[2:] or list(WHERE)


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
    for k in KINDS:
        st, sc = WHERE[k]
        ev(f"profileSet('TIM', false); newRun(0, '{st}'); startStage('{st}')"); time.sleep(2.5)
        for _ in range(20):
            m = ev('mode')
            if m == 'comic': ev('comicEnd()')
            elif m == 'chat': ev("pressed.add('escape')")
            elif m == 'play': break
            time.sleep(0.4)
        ev(f"orpGoScene({sc}, 1); S.howto = null; S.frog = null; S.served = null; S.queue = null; S.dance = null; ST.waves = []; S.wave = null")
        ev(f"player.x = 300; player.y = FT + 50; for (let i = 0; i < 2; i++) {{ const f = makeFoe('{k}', 560 + i * 140, FT + 40 + i * 20); f.state = 'hover'; foes.push(f); }}")
        ev("window.__seen = {}; window.__tick = setInterval(() => { for (const f of foes) { (window.__seen[f.kind] = window.__seen[f.kind] || new Set()).add(f.state); } player.hp = player.maxHp; }, 30)")
        time.sleep(2.5); shot(f'{k}_0')
        for i, (mv, dist) in enumerate(MOVES[k]):
            ev(f"(() => {{ const f = foes.find(o => o.kind === '{k}' && o.hp > 0); if (!f) return; if (player.state === 'netted' || player.state === 'drowsy') setIdle(player); "
               f"player.x = 300; player.y = FT + 50; f.x = 300 + {dist}; f.y = player.y; f.face = -1; f.state = 'hover'; f.t = 0; f.inv = 0; S.nlSpecT = 0; nlStartSpecial(f, '{mv}'); }})()")
            for j in range(4): time.sleep(0.3); shot(f'{k}_{i + 1}_{mv}_{j}')
            time.sleep(1.5)
        time.sleep(4)
        seen = ev(f"Array.from((window.__seen['{k}'] || new Set()))")
        print(k, 'states:', ', '.join(seen)); ev('clearInterval(window.__tick)')
    print('errors:', errs[:20] if errs else 'none')
    b.close()
