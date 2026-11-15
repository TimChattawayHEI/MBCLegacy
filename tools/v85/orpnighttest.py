"""Version 85 Orpington night check, headless: python3 tools/v85/orpnighttest.py [--out dir]
1. Starting the chapter: the present-day chat, then the March 2001 comic page, then the text-speak Nokia chat.
2. The clock: 20:00 at the bus stop, 20:30 at Ram Ba Ba with COACH 22:30, the pub's pool room 21:20, never past the
   next place's time.
3. The door: the questions and the nerve meter. Answering in the green: SMOOTH and 3,000. Saying nothing: no bonus but
   still in. Either way the comic page and on to the dance floor.
Screenshots: the clock at the bus stop, and the meter. Fails on any page error or a wrong answer."""
import http.server, os, socketserver, sys, threading, time
from playwright.sync_api import sync_playwright
from PIL import Image
opt = lambda k, d: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = opt('--out', '/tmp/v85night'); os.makedirs(OUT, exist_ok=True)
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
os.chdir(os.path.join(ROOT, 'web'))
srv = socketserver.ThreadingTCPServer(('127.0.0.1', 0), Q); srv.daemon_threads = True; port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
errs, bad = [], []
def check(ok, msg):
    print(('ok   ' if ok else 'FAIL ') + msg)
    if not ok: bad.append(msg)
with sync_playwright() as pw:
    br = pw.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--mute-audio'])
    pg = br.new_page(); pg.set_viewport_size({'width': 960, 'height': 540}); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(f'http://127.0.0.1:{port}/index.html?pubtest'); time.sleep(3)
    ev = lambda js: pg.evaluate('s => window.__pub(s)', js)
    shot = lambda n: pg.locator('canvas').first.screenshot(path=os.path.join(OUT, n))
    # 1. the chats
    ev("window.__done = false; profileSet('TIM', false); newRun(0, 'orp_street'); openChat(CHATS.orpIntro, () => { window.__done = true; mode = 'select'; }, null, 2001); 0")
    a = ev("[mode, chat && chat.lines === CHATS.orpNow, chat && chat.era]")
    check(a[0] == 'chat' and a[1] and a[2] is None, f'present-day chat first {a}')
    ev("skipChat(); 0"); time.sleep(0.3)
    b = ev("[mode, comic && comic.id]")
    check(b == ['comic', 'p2001'], f'then the comic page {b}')
    ev("comicEnd(); 0"); time.sleep(0.3)
    c = ev("[mode, chat && chat.lines === CHATS.orpIntro, chat && chat.era, CHATS.orpIntro[1][1]]")
    check(c[0] == 'chat' and c[1] and c[2] == 2001 and 'dnt b l8' in c[3], f'then the Nokia, in text speak {c[:3]}')
    ev("skipChat(); 0"); time.sleep(0.2)
    check(ev("window.__done"), 'and then the stage')
    r = ev("openChat(CHATS.orpIntro, null, 'CARRYING ON', 2001), [mode, !!(chat && chat.lines === CHATS.orpNow)]")
    check(r[1] is False, f'carrying on skips the present day {r}')
    ev("if (comic) comicEnd(); 0"); time.sleep(0.2); ev("if (chat) skipChat(); 0"); time.sleep(0.2)
    # 2. the clock
    ev("profileSet('TIM', false); newRun(0, 'orp_street'); startStageNow('orp_street')"); time.sleep(2.5)
    t0 = ev("S.night"); check(t0 is not None and 1200 <= t0 < 1202, f'bus stop clock {t0}')
    shot('clock.png')
    ev("orpGoScene(2, 1); 0"); time.sleep(0.5)
    t1 = ev("[S.night, S.coachSeen]"); check(1230 <= t1[0] < 1232 and t1[1], f'Ram Ba Ba 20:30 and the coach time {t1}')
    ev("S.ckT = 9999; 0"); time.sleep(0.3)
    check(ev("S.night") == 1233, f'stops a minute before the next place {ev("S.night")}')
    ev("profileSet('TIM', false); newRun(0, 'orp_pub'); startStageNow('orp_pub')"); time.sleep(2)
    ev("orpGoScene(2, 1); 0"); time.sleep(0.4)
    check(1280 <= ev("S.night") < 1282, f'pool room 21:20 {ev("S.night")}')
    # 3. the door
    def door(cool):
        ev("profileSet('TIM', false); newRun(0, 'orp_atlantis'); startStageNow('orp_atlantis')"); time.sleep(2)
        ev("if (S.howto) { const h = S.howto; S.howto = null; h.then && h.then(); } 0"); time.sleep(0.3)
        for _ in range(60):
            st = ev("[!!S.queue, !!S.howto]")
            if st[1]: ev("{ const h = S.howto; S.howto = null; h.then && h.then(); } 0")
            if st[0]: ev("foes.length = 0; S.queue.ahead = 0; 0")
            time.sleep(0.2)
            if ev("!!S.blag || (S.howto && S.howto.title === 'THE DOOR')"): break
        if ev("S.howto && S.howto.title === 'THE DOOR'"): ev("{ const h = S.howto; S.howto = null; h.then && h.then(); } 0")
        time.sleep(0.2)
        check(ev("!!S.blag && S.blag.qs.length === 3"), 'the bouncer asks three questions')
        score0 = ev("run.score")
        if cool: ev("window.__needle = orpBlagNeedle; orpBlagNeedle = () => 0.5; 0")
        shots = 0
        for _ in range(120):
            ph = ev("S.blag ? S.blag.phase : 'done'")
            if ph == 'done': break
            if ph == 'ask':
                if not shots: time.sleep(0.5); shot('blag_cool.png' if cool else 'blag.png'); shots = 1
                if cool: ev("pressed.add('punch'); 0")
            time.sleep(0.15)
        if cool: ev("orpBlagNeedle = window.__needle; 0")
        res = ev("S.blagRes"); gain = ev("run.score") - score0
        if cool: check(res and res['smooth'] and gain >= 3000, f'cool answers: SMOOTH and 3,000 ({res}, +{gain})')
        else: check(res and not res['smooth'] and res['cool'] == 0, f'no answers: no bonus ({res})')
        for _ in range(40):
            time.sleep(0.25)
            if ev("mode") == 'comic': ev("comicEnd(); 0")
            if ev("S.sc") == 1: break
        check(ev("S.sc") == 1, 'through the door to the dance floor')
    door(True); door(False)
    g = ev("glitchInfo ? glitchInfo.msg : ''")
    check(not g, f'no glitches reported ({g})')
    br.close()
for e in errs: print('page error:', e)
print('PASS' if not bad and not errs else f'{len(bad)} failed, {len(errs)} page errors')
sys.exit(1 if bad or errs else 0)
