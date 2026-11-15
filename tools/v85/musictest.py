"""Version 85 soundtrack check, headless: python3 tools/v85/musictest.py
For every new track: it loads and decodes, its length matches `end` (so the lead-in check doesn't misfire), and once
playing its loop runs from `from` to the loop end. Then: a track stopped mid-loop (a mini-boss) picks up in the loop, not
the intro; a missing file falls back to the old track; ?oldmusic plays the old tracks; and Atlantis's beat phase follows
Alarm Call's own tempo. Fails on any page error or any wrong number."""
import http.server, json, os, socketserver, sys, threading, time
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = {k: v for k, v in json.load(open(os.path.join(ROOT, 'tools', 'v85', 'music.json'))).items() if not k.startswith('_')}
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
    ev("audioInit(); actx.resume(); settings.sound = true; 0")
    # every track: decodes, length, loop points once playing
    for k, (frm, le, end, vol, *_) in DATA.items():
        r = pg.evaluate("s => window.__pub(s)", f"""(async () => {{ const b = await trackBuffer('{k}'); return b ? b.duration : -1; }})()""")
        check(r > 0 and abs(r - end) < 0.03, f'{k}: decoded {r:.3f}s, end {end}')
        ev(f"musicSet('{k}'); trackStart('{k}'); 0"); time.sleep(0.3)
        s = ev("trk.src ? [trk.key, trk.src.loopStart, trk.src.loopEnd, TRACKS[trk.key].lead, trk.gain.gain.value, TRACKS[trk.key].src] : null")
        ok = s and s[0] == k and abs(s[1] - s[3] - frm) < 0.002 and abs(s[2] - s[3] - le) < 0.002 and s[5] == f'music/v85/{k}.mp3'
        check(bool(ok), f'{k}: loop {s and round(s[1], 3)}..{s and round(s[2], 3)} lead {s and s[3]} gain {s and round(s[4], 3)}')
        ev("musicSet(null); 0")
    # a mini-boss part way into the loop: the stage track comes back inside the loop
    ev("musicSet('garage'); trackStart('garage'); 0"); time.sleep(0.4)
    ev("trk.t0 -= 50; 0")   # pretend 50s have played (intro is 36.5s)
    fp = ev("trackFilePos()")
    ev("musicSet('boss', true); 0"); pos = ev("trk.pos.garage")
    check(abs(pos - (fp - DATA['garage'][0])) < 0.2, f'garage stopped at file {fp:.2f}s, keeps loop offset {pos:.2f}s')
    ev("musicSet('garage', true); trackStart('garage'); 0"); time.sleep(0.4)
    fp2 = ev("trackFilePos()")
    check(abs(fp2 - fp) < 0.8, f'garage resumes at file {fp2:.2f}s (was {fp:.2f}s)')
    # beat phase follows the new tempo
    bp = ev(f"""(() => {{ ST = STAGES.atlantis || Object.values(STAGES).find(s => s.music === 'alarmcall'); musicSet('alarmcall'); return ST.music; }})()""")
    ev("trackStart('alarmcall'); 0"); time.sleep(0.5)
    T = DATA['alarmcall']
    ph = ev("(() => { const fp = trackFilePos(), T = TRACKS.alarmcall, b = 60 / T.bpm; return [fp, ((((fp - T.beat0) % b) + b) % b) / b]; })()")
    check(ph[0] > 0 and 0 <= ph[1] < 1, f'alarmcall plays at file {ph[0]:.2f}s, beat phase {ph[1]:.2f} at {T[4]} bpm')
    ev("musicSet(null); 0")
    # a file that won't load falls back to the old track
    ev("TRACKS.club.src = 'music/v85/nope.mp3'; delete trk.bytes.club; trk.bufs.delete('club'); 0")
    d = pg.evaluate("s => window.__pub(s)", "(async () => { const b = await trackBuffer('club'); return [b && b.duration, TRACKS.club.src]; })()")
    check(d[0] and d[1] == 'music/biggest-club.mp3', f'missing club file falls back to {d[1]} ({d[0] and round(d[0], 1)}s)')
    # ?oldmusic keeps the old tracks
    pg.goto(f'http://127.0.0.1:{port}/index.html?pubtest&oldmusic'); time.sleep(3)
    old = ev("[TRACKS.garage.src, TRACKS.boss.src, TRACKS.title.src]")
    check(old[0] == 'music/bait-and-switch.mp3' and old[1] == 'music/the-big-one.mp3', f'?oldmusic: {old}')
    br.close()
for e in errs: print('page error:', e)
print('PASS' if not bad and not errs else f'{len(bad)} failed, {len(errs)} page errors')
sys.exit(1 if bad or errs else 0)
