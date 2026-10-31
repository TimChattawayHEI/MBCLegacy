"""Walks the redesigned menus headless with WebGL on: python3 tools/v82/test.py [out_dir]
Title -> start menu -> SETTINGS and back -> NEW GAME -> the lads (Byron picked to check his face) -> where to start
(Orpington 2001) -> 3 GO, a screenshot at each, and checks the steps, the back buttons and that a run starts."""
import http.server, os, socketserver, sys, threading, time
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp/v82test'; os.makedirs(OUT, exist_ok=True)


class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass


os.chdir(os.path.join(ROOT, 'web'))
srv = socketserver.TCPServer(('127.0.0.1', 0), Q); port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
errs = []; ok = lambda n, c: print(('PASS ' if c else 'FAIL ') + n)
with sync_playwright() as pw:
    b = pw.chromium.launch(args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
    pg = b.new_page(viewport={'width': 1280, 'height': 720})
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.add_init_script('window.__mbcTest = {}')   # the 3D select's test hook
    pg.goto(f'http://127.0.0.1:{port}/index.html?pubtest'); time.sleep(3)
    pg.evaluate("s => window.__pub(s)", "profileSet('TWOB', false)"); pg.reload(); time.sleep(7)
    shot = lambda n: pg.locator('#frame').screenshot(path=os.path.join(OUT, n + '.png'))
    view = lambda: pg.evaluate("() => window.__mbcTest && window.__mbcTest.t3 ? window.__mbcTest.t3.state().view : null")
    pg.keyboard.press('Enter'); time.sleep(0.4); pg.keyboard.press('Enter'); time.sleep(2.5)
    ok('title goes to the start menu', view() == 'menu'); shot('1_menu')
    pg.click('#t3-mset'); time.sleep(0.8); shot('2_settings')
    ok('settings opens from the menu', pg.evaluate("s => window.__pub(s)", "mode") == 'pause')
    pg.keyboard.press('Escape'); time.sleep(0.3); pg.keyboard.press('Escape'); time.sleep(1.5)
    ok('settings back to the menu', view() == 'menu' and pg.evaluate("s => window.__pub(s)", "mode") == 'select')
    pg.click('#t3-mnew'); time.sleep(2.5); ok('NEW GAME goes to the lads', view() == 'lad'); shot('3_lads')
    pg.click('#t3-roster button[aria-label="BYRON"]'); time.sleep(1.5); shot('4_byron')
    pg.click('#t3-hback'); time.sleep(1.2); ok('back from the lads to the menu', view() == 'menu')
    pg.click('#t3-mnew'); time.sleep(1.5); pg.click('#t3-pick'); time.sleep(3.5)
    ok('picking goes to where to start', view() == 'stage')
    pg.click('#t3-tabs button[data-c="1"]'); time.sleep(1.5); shot('5_stage_orp')
    pg.click('#t3-tabs button[data-c="2"]'); time.sleep(1.2); shot('6_stage_elba')
    pg.click('#t3-tabs button[data-c="1"]'); time.sleep(0.6); pg.click('#t3-sgrid button[data-f="3"]'); time.sleep(0.8)
    pg.click('#t3-here'); time.sleep(2); ok('START HERE goes to 3 GO', view() == 'diff'); shot('7_go')
    pg.click('#t3-go'); time.sleep(4)
    m = pg.evaluate("s => window.__pub(s)", "mode"); st = pg.evaluate("s => window.__pub(s)", "run && run.route && run.route[0]")
    ok('LET\'S GO starts the run at the stage picked (' + str(m) + ', ' + str(st) + ')', st == 'orp_pub')
    print('errors:', errs[:5] if errs else 'none')
    b.close()
