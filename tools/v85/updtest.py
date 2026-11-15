"""Version 85 in-app update card check, headless: python3 tools/v85/updtest.py [--out dir]
Fakes the app's updater (window.MBCNative) and walks it through a download, a download that stops, TRY AGAIN, the
automatic retry a minute later, and UPDATE READY, checking the card's words and buttons on the title screen at each
step, and that nothing shows during a fight. Saves a screenshot of each state. Fails on any page error or wrong card."""
import http.server, os, socketserver, sys, threading, time
from playwright.sync_api import sync_playwright
opt = lambda k, d: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = opt('--out', '/tmp/v85upd'); os.makedirs(OUT, exist_ok=True)
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
os.chdir(os.path.join(ROOT, 'web'))
srv = socketserver.ThreadingTCPServer(('127.0.0.1', 0), Q); srv.daemon_threads = True; port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
FAKE = """
window.__ota = { state: 'idle', mine: 175, latest: 0, done: 0, total: 0, files: 0, of: 0, err: '' };
window.__checks = 0; window.__applied = 0;
window.MBCNative = { otaStatus: () => JSON.stringify(window.__ota), otaCheck: () => { window.__checks++; if (window.__ota.state !== 'ready') window.__ota.state = 'checking'; },
  otaApply: () => { window.__applied++; return true; }, canVoice: () => false, voice: () => {} };
"""
errs, bad = [], []
def check(ok, msg):
    print(('ok   ' if ok else 'FAIL ') + msg)
    if not ok: bad.append(msg)
with sync_playwright() as pw:
    br = pw.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--mute-audio'])
    pg = br.new_page(); pg.set_viewport_size({'width': 960, 'height': 540})
    pg.add_init_script(FAKE); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(f'http://127.0.0.1:{port}/index.html?pubtest'); time.sleep(3)
    ev = lambda js: pg.evaluate('s => window.__pub(s)', js)
    card = lambda: pg.evaluate("() => { const e = document.getElementById('updCard'); if (!e || e.style.display === 'none') return null; const g = e.querySelector('#updGo'); return [e.querySelector('#updWhat').textContent, e.querySelector('#updSub').textContent, g.style.display === 'none' ? '' : g.textContent]; }")
    def state(js, wait=1.0): pg.evaluate("s => Object.assign(window.__ota, JSON.parse(s))", js); time.sleep(wait)
    def shot(n): pg.screenshot(path=os.path.join(OUT, n + '.png'))
    print('mode', ev('mode'), 'checks', pg.evaluate('window.__checks'))
    check(pg.evaluate('window.__checks') >= 1, 'the app is asked to look for an update on the title screen')
    state('{"state":"downloading","latest":181,"done":12582912,"total":49180000,"files":20,"of":87}')
    c = card(); shot('1_downloading')
    check(bool(c) and c[0] == 'DOWNLOADING 1.181' and '20 of 87 files, 12 of 47 MB' in c[1] and c[2] == '', f'downloading: {c}')
    state('{"done":41943040,"files":70}', 1.0); c = card()
    check(bool(c) and '70 of 87 files, 40 of 47 MB' in c[1], f'progress moves on: {c and c[1]}')
    # during a fight: no card
    ev("profileSet('TIM', false); newRun(0, 'garage' in STAGES ? 'garage' : 'frequency'); startStageNow('frequency')"); time.sleep(1.5)
    check(card() is None, f'no card in a fight (mode {ev("mode")})')
    ev("mode = 'title'"); time.sleep(1)
    # the download stops
    n0 = pg.evaluate('window.__checks')
    state('{"state":"error","err":"HTTP 429 for road.mp3"}'); c = card(); shot('2_stopped')
    check(bool(c) and c[0] == 'UPDATE 1.181 STOPPED' and c[1].startswith('HTTP 429 for road.mp3.') and c[2] == 'Try again', f'stopped: {c}')
    pg.click('#updGo'); time.sleep(0.5)
    check(pg.evaluate('window.__checks') == n0 + 1, 'TRY AGAIN asks the app to look again')
    state('{"state":"checking"}', 0.8); c = card()
    check(bool(c) and c[0] == 'DOWNLOADING 1.181' and c[1] == 'Starting...', f'after try again: {c}')
    # retry by itself after a minute
    state('{"state":"error","err":"timeout"}', 0.8)
    n1 = pg.evaluate('window.__checks'); ev('UPD.checkedT -= 61000'); time.sleep(1)
    check(pg.evaluate('window.__checks') == n1 + 1, 'a stopped download is tried again after a minute')
    # ready
    state('{"state":"ready","done":49180000,"files":87}'); c = card(); shot('3_ready')
    check(bool(c) and c[0] == 'UPDATE READY: 1.181' and c[2] == 'Restart', f'ready: {c}')
    pg.click('#updGo'); time.sleep(0.8)
    check(pg.evaluate('window.__applied') == 1, 'RESTART switches it in')
    # up to date: nothing shows
    pg.goto(f'http://127.0.0.1:{port}/index.html?pubtest'); time.sleep(2.5)
    state('{"state":"current","mine":181,"latest":181}'); check(card() is None, 'up to date: no card')
    br.close()
for e in errs: print('page error:', e)
print('PASS' if not bad and not errs else f'{len(bad)} failed, {len(errs)} page errors')
sys.exit(1 if bad or errs else 0)
