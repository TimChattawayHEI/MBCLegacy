"""Version 85 stings and pub music check, headless: python3 tools/v85/stingtest.py
Each sting loads and plays at its moment: the last boss down, a stage cleared (and not straight over the boss sting),
game over, ON THE TAB (then the stage's music comes back), a chapter's title page. The pub and every pub game play their
own track, Kebab Siege too, and ?oldmusic gives them the tracks they had before. Fails on any page error or a wrong answer."""
import http.server, os, socketserver, sys, threading, time
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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
    br = pw.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--mute-audio', '--autoplay-policy=no-user-gesture-required'])
    pg = br.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(f'http://127.0.0.1:{port}/index.html?pubtest'); time.sleep(3)
    ev = lambda js: pg.evaluate('s => window.__pub(s)', js)
    ev("audioInit(); actx.resume(); settings.sound = true; 0"); time.sleep(3)
    check(ev("Object.keys(sting.bufs).sort().join()") == 'bossdown,chapter,clear,gameover,tab', 'all five stings load: ' + ev("Object.keys(sting.bufs).sort().join()"))
    # the mini-games and kebab siege
    got = ev("JSON.stringify(Object.fromEntries(['darts','fruit','pens','kiss','awake','golf','snake'].map(k => [k, MINI_DEF[k].music])))")
    check('"darts":"pubgames"' in got and '"snake":"snake"' in got and '"golf":"golf"' in got, 'pub games have their own tracks: ' + got)
    check(ev("STAGES.kebab.music") == 'kebab' and ev("TRACKS.kebab.src") == 'music/v85/kebab.mp3', 'Kebab Siege has its own track')
    # stage: boss down, then clear straight after: the clear sting doesn't cut it
    ev("profileSet('TIM', false); newRun(0, 'frequency'); startStageNow('frequency')"); time.sleep(3)
    ev("stingPlay('bossdown'); 0"); time.sleep(0.3)
    ev("musicSet(null); if (!stingRecent('bossdown', 5)) stingPlay('clear'); 0"); time.sleep(0.2)
    check(ev("sting.key") == 'bossdown', 'a stage clear just after the boss leaves the boss sting playing')
    ev("sting.at -= 10; musicSet(null); if (!stingRecent('bossdown', 5)) stingPlay('clear'); 0"); time.sleep(0.2)
    check(ev("sting.key") == 'clear' and ev("!!sting.src"), 'a stage clear on its own plays the clear sting')
    # a new track stops a sting
    ev("musicSet('garage'); 0"); time.sleep(0.2)
    check(ev("!sting.src"), 'a new track stops the sting')
    # game over
    ev("musicSet('garage'); gameOver(); 0"); time.sleep(0.3)
    check(ev("sting.key") == 'gameover' and ev("mus.key") is None, 'game over plays its sting over silence')
    # on the tab: sting, then the stage music after 3.4 s of game time
    ev("profileSet('TIM', false); newRun(0, 'frequency'); startStageNow('frequency')"); time.sleep(3)
    ev("PUB.wallet = 1e6; CONT.on = true; CONT.cost = 10000; CONT.music = 'garage'; mode = 'cont'; contYes(); 0"); time.sleep(0.4)
    check(ev("sting.key") == 'tab' and ev("mus.key") is None, 'ON THE TAB plays its sting first')
    time.sleep(4.5)
    check(ev("mus.key") == 'garage', 'then the stage music comes back: ' + str(ev("mus.key")))
    # a chapter page
    ev("comicShow('pelba', () => {}); 0"); time.sleep(0.3)
    check(ev("sting.key") == 'chapter', 'a chapter title page plays the chapter sting')
    ev("comicEnd(); comicShow('p2001', () => {}); sting.key = ''; comicEnd(); comicShow('p2001', () => {}); 0"); time.sleep(0.2)
    check(ev("sting.key") == 'chapter', 'Orpington 2001 title page too')
    ev("comicEnd(); 0")
    # the pub
    ev("openPub('select', null, 'tim'); 0"); time.sleep(0.5)
    check(ev("TRACKS.pub.src") == 'music/v85/pub.mp3' and ev("mus.key") == 'pub', 'the pub plays its own track')
    # ?oldmusic
    pg.goto(f'http://127.0.0.1:{port}/index.html?pubtest&oldmusic'); time.sleep(3)
    old = ev("[TRACKS.pub.src, TRACKS.pubgames.src, TRACKS.pens.src, TRACKS.kebab.src]")
    check(old == ['music/last-orders.mp3', 'music/last-orders.mp3', 'music/bait-and-switch.mp3', 'music/night-bus.mp3'], f'?oldmusic: {old}')
    br.close()
for e in errs: print('page error:', e)
print('PASS' if not bad and not errs else f'{len(bad)} failed, {len(errs)} page errors')
sys.exit(1 if bad or errs else 0)
