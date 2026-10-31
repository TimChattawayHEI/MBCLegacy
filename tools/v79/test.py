"""Checks the Version 79 quality-of-life changes headless: python3 tools/v79/test.py [out_dir]
The "!" over a winding-up Builder, an edge arrow for someone off screen, auto-turn on a punch, a how-to card skipped
the second time, an Orpington stage carried on from the pool room, and the settings list on a phone (screenshots)."""
import http.server, json, os, socketserver, sys, threading, time
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp/v79test'; os.makedirs(OUT, exist_ok=True)


class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass


os.chdir(os.path.join(ROOT, 'web'))
srv = socketserver.TCPServer(('127.0.0.1', 0), Q); port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
errs = []; ok = lambda name, c: print(('PASS ' if c else 'FAIL ') + name)
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_context(viewport={'width': 960, 'height': 540}, has_touch=True).new_page()
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(f'http://127.0.0.1:{port}/index.html?pubtest'); time.sleep(4)
    ev = lambda js: pg.evaluate('s => window.__pub(s)', js)
    shot = lambda n: pg.locator('#game').screenshot(path=os.path.join(OUT, n + '.png'))
    def play(st):
        ev(f"profileSet('TIM', false); newRun(0, '{st}'); startStage('{st}')"); time.sleep(2.5)
        for _ in range(20):
            m = ev('mode')
            if m == 'comic': ev('comicEnd()')
            elif m == 'chat': ev("pressed.add('escape')")
            elif m == 'play': break
            time.sleep(0.4)
    play('orp_street')
    ev("orpGoScene(3, 1); S.howto = null; ST.waves = []; S.wave = null; player.x = 300; player.y = FT + 50")
    # 1: the tell
    ev("const f = makeFoe('builder', 640, player.y); f.state = 'hover'; foes.push(f); S.nlSpecT = 0; nlStartSpecial(f, 'bargeWind')"); time.sleep(0.2); shot('1_tell')
    ok('builder winding up shows as a tell', ev("NL_TELL.has(foes[0].state)"))
    # 3: edge arrow
    ev("foes.length = 0; const g = makeFoe('kappa', -120, FT + 60); g.state = 'enter'; foes.push(g)"); time.sleep(0.15); shot('3_edge_arrow')
    # 4: auto-turn
    ev("foes.length = 0; touchUI = true; settings.aim = true; const h = makeFoe('codger', player.x - 70, player.y); h.state = 'hover'; foes.push(h); player.face = 1; setIdle(player); startPunch(player)")
    ok('punch turns round to the foe behind', ev("player.face") == -1)
    ev("foes.length = 0; const h = makeFoe('codger', player.x - 70, player.y); h.state = 'hover'; foes.push(h); player.face = 1; setIdle(player); settings.aim = false; startPunch(player)")
    ok('auto-turn off leaves you facing', ev("player.face") == 1); ev("settings.aim = true")
    # 2: how-to card skipped the second time
    ev("localStorage.removeItem('carpdiem.howto'); window.__ran = 0; orpHowto('THE QUEUE', ['x'], () => window.__ran++)")
    ok('first time: the card shows', ev("!!S.howto"))
    ev("pressed.add('punch')"); time.sleep(0.9); ev("pressed.add('punch')"); time.sleep(0.3)
    ok('dismissing it marks it read', ev("!!(lsGet('carpdiem.howto', {}) || {})['THE QUEUE']"))
    ev("S.howto = null; window.__ran = 0; orpHowto('THE QUEUE', ['x'], () => window.__ran++)")
    ok('second time: no card, a reminder, carries straight on', ev("!S.howto && !!S.ann && window.__ran === 1"))
    shot('2_reminder')
    # 6: carry on from the pool room
    play('orp_pub'); ev("S.howto = null; orpGoScene(2, 1)")
    ok('the pool room is saved with the run', ev("(lsGet(RUN_SAVE, null) || {}).orpAt && lsGet(RUN_SAVE, null).orpAt.i") == 2)
    ev("mode = 'select'; continueRun()"); time.sleep(1.5)
    for _ in range(20):
        m = ev('mode')
        if m == 'comic': ev('comicEnd()')
        elif m == 'chat': ev("pressed.add('escape')")
        elif m == 'play' and ev('S.sc') is not None: break
        time.sleep(0.4)
    ok('carrying the run on starts in the pool room', ev('S.sc') == 2 and ev("S.scBg") == 'pool'); shot('6_carry_on')
    ok('restart stage would start from the top', ev("!(stageSnap && stageSnap.run && stageSnap.run.orpAt)"))
    # 5 and the settings list on a phone
    ev("settings.light = 'low'"); time.sleep(0.3); shot('5_light_low'); ev("settings.light = 'full'")
    ev("mode = 'pause'; pauseTab = 'settings'; pauseFocus = 'right'"); time.sleep(0.4); shot('settings_phone')
    ok('settings rows fit on the screen', ev("setRows().every(r => r.y + r.h <= H - 4)"))
    print('errors:', errs[:5] if errs else 'none')
    b.close()
