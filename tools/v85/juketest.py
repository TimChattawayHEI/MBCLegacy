"""Version 85 jukebox check, headless: python3 tools/v85/juketest.py [--out dir]
Serves the repo root (so jukebox/ is reachable as it is from GitHub) and opens the game in the Harvest Moon.
1. The jukebox is at the far end and HIT by it opens it; the three pages are there with every song.
2. SOUNDTRACK: a game track plays through the music player.
3. SONGS: the A side and the B side stream (the <audio> reaches 'playing' and moves), the pub track stops under it,
   the plate says what's playing; STOP brings the pub track back.
4. Every song file the list names exists in jukebox/ (both sides).
5. A file that can't be reached says it needs signal. Leaving the pub stops the jukebox.
Fails on any page error or a wrong answer."""
import http.server, os, socketserver, sys, threading, time, re
from playwright.sync_api import sync_playwright
opt = lambda k, d: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = opt('--out', '/tmp/v85juke'); os.makedirs(OUT, exist_ok=True)
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
os.chdir(ROOT)
srv = socketserver.ThreadingTCPServer(('127.0.0.1', 0), Q); srv.daemon_threads = True; port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
errs, bad = [], []
def check(ok, msg):
    print(('ok   ' if ok else 'FAIL ') + msg)
    if not ok: bad.append(msg)
with sync_playwright() as pw:
    br = pw.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--mute-audio', '--autoplay-policy=no-user-gesture-required'])
    pg = br.new_page(); pg.set_viewport_size({'width': 960, 'height': 540}); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(f'http://127.0.0.1:{port}/web/index.html?pubtest'); time.sleep(3)
    ev = lambda js: pg.evaluate('s => window.__pub(s)', js)
    shot = lambda n: pg.locator('canvas').first.screenshot(path=os.path.join(OUT, n))
    ev("JUKE_RAW = '/jukebox/'; settings.sound = true; profileSet('TIM', false); openPub('menu'); 0"); time.sleep(0.6)
    # 4. the files
    keys = ev("JUKE.pages.slice(0, 2).flatMap(p => p.list.map(r => r[0]))")
    missing = [k + '_' + s for k in keys for s in '12' if not os.path.exists(os.path.join(ROOT, 'jukebox', k + '_' + s + '.mp3'))]
    check(not missing, f'{len(keys)} streamed songs, both sides in jukebox/ {missing}')
    gl = ev("JUKE.pages[2].list.length"); check(gl >= 25, f'{gl} soundtrack tracks, all real')
    # 1. walk there, HIT
    ev("PUB.x = 3135; PUB.y = 470; 0"); time.sleep(0.3)
    check(ev("PUB.near && PUB.near.id") == 'jukebox', 'stood at the jukebox')
    shot('pub.png')
    ev("pressed.add('punch'); 0"); time.sleep(0.4)
    check(ev("mode") == 'juke', 'HIT opens it')
    ev("pressed.add('right'); 0"); time.sleep(0.2); ev("pressed.add('right'); 0"); time.sleep(0.2)
    check(ev("JUKE.page") == 1, f'right flips the side then the page ({ev("JUKE.page")})')
    ev("JUKE.page = 2; JUKE.sel = 0; 0"); time.sleep(0.2)
    # 2. soundtrack
    ev("pressed.add('punch'); 0"); time.sleep(0.5)
    check(ev("mus.key") == 'title' and ev("JUKE.now && !JUKE.now.stream"), f'soundtrack plays through the music player ({ev("mus.key")})')
    # 3. a stream
    ev("JUKE.page = 0; JUKE.sel = 5; JUKE.side = 1; 0"); time.sleep(0.2)
    ev("pressed.add('punch'); 0")
    for _ in range(40):
        time.sleep(0.25)
        if ev("JUKE.state") == 'playing': break
    time.sleep(1.2)
    st = ev("[JUKE.state, JUKE.el && JUKE.el.currentTime, JUKE.el && JUKE.el.src.slice(-24), mus.key, JUKE.now.title]")
    check(st[0] == 'playing' and st[1] > 0.3 and st[3] is None, f'A side streams and the pub track stops {st}')
    shot('juke.png')
    ev("JUKE.side = 2; pressed.add('punch'); 0")
    for _ in range(40):
        time.sleep(0.25)
        if ev("JUKE.state") == 'playing' and ev("JUKE.el.src.endsWith('_2.mp3')"): break
    check(ev("JUKE.el.src.endsWith('vocal_atlantis_2.mp3') && JUKE.state === 'playing'"), 'B side streams')
    ev("pressed.add('jump'); 0"); time.sleep(0.4)
    check(ev("mode") == 'pub' and ev("JUKE.now !== null"), 'closing the jukebox keeps the song on in the pub')
    shot('plate.png')
    ev("jukeOpen(); 0"); time.sleep(0.3); ev("pressed.add('grab'); 0"); time.sleep(0.4)
    check(ev("JUKE.now") is None and ev("mus.key") == 'pub' and ev("JUKE.el.paused"), 'STOP: the pub track comes back')
    # 5. no signal, and leaving
    ev("JUKE_RAW = '/nowhere/'; jukePlay(0, 0, 1); 0")
    for _ in range(20):
        time.sleep(0.25)
        if ev("JUKE.state") == 'error': break
    check(ev("JUKE.state") == 'error', 'unreachable says so')
    shot('error.png')
    ev("JUKE_RAW = '/jukebox/'; jukePlay(0, 1, 1); 0"); time.sleep(1.5)
    ev("jukeClose(); pubLeave(); 0"); time.sleep(0.5)
    check(ev("JUKE.now") is None and ev("JUKE.el.paused") and ev("mode") == 'select', 'leaving the pub stops it')
    g = ev("glitchInfo ? glitchInfo.msg : ''"); check(not g, f'no glitches ({g})')
    br.close()
for e in errs: print('page error:', e)
print('PASS' if not bad and not errs else f'{len(bad)} failed, {len(errs)} page errors')
sys.exit(1 if bad or errs else 0)
