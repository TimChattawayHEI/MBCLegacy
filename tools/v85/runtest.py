"""Version 85 run back check, headless: python3 tools/v85/runtest.py [--out dir]
1. The stage is on the route between the Blacksmiths and Atlantis, numbered, with its chat.
2. A bot runs it: it jumps the low things ahead in its lane and changes lane for A-boards and people. It must make the
   coach in time, the points screen must come up, and the rank must be set. Screenshots along the way.
3. Standing still (no input, never jumping) it misses the coach, the run restarts (TRY 2) and no life is lost.
Fails on any page error or a wrong answer."""
import http.server, os, socketserver, sys, threading, time
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw
opt = lambda k, d: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = opt('--out', '/tmp/v85run'); os.makedirs(OUT, exist_ok=True)
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
os.chdir(os.path.join(ROOT, 'web'))
srv = socketserver.ThreadingTCPServer(('127.0.0.1', 0), Q); srv.daemon_threads = True; port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
errs, bad = [], []
def check(ok, msg):
    print(('ok   ' if ok else 'FAIL ') + msg)
    if not ok: bad.append(msg)
BOT = """(() => {
  const r = S.rb; if (!r || r.phase !== 'run') { held.clear(); return; }
  held.clear(); held.add('left');
  const ahead = r.obs.filter(o => o.x > r.d && o.x - r.d < 260 && !o.hit);
  const inLane = y => ahead.filter(o => Math.abs(o.y - y) < 16);
  const mine = inLane(r.y).sort((a, b) => a.x - b.x)[0];
  if (mine) {
    const m = RUN_OBS[mine.kind];
    if (m.jump && mine.x - r.d < 120 && r.z <= 0) pressed.add('jump');
    else if (!m.jump) { const best = RUN.lanes.filter(y => !inLane(y).some(o => !RUN_OBS[o.kind].jump)).sort((a, b) => Math.abs(a - r.y) - Math.abs(b - r.y))[0];
      if (best != null) held.add(best < r.y ? 'up' : 'down'); }
  } else { const c = RUN.lanes.reduce((a, y) => Math.abs(y - r.y) < Math.abs(a - r.y) ? y : a); if (Math.abs(c - r.y) > 3) held.add(c < r.y ? 'up' : 'down'); }
})()"""
with sync_playwright() as pw:
    br = pw.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--mute-audio'])
    pg = br.new_page(); pg.set_viewport_size({'width': 960, 'height': 540}); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(f'http://127.0.0.1:{port}/index.html?pubtest'); time.sleep(3)
    ev = lambda js: pg.evaluate('s => window.__pub(s)', js)
    route = ev("ROUTE.slice(ROUTE.indexOf('orp_street'), ROUTE.indexOf('airport'))")
    check(route == ['orp_street', 'orp_pub', 'orp_run', 'orp_atlantis'], f'route: {route}')
    check(ev("STAGES.orp_run.n") == ev("STAGES.orp_pub.n") + 1 and ev("!!CHATS.orpRun"), 'numbered after the Blacksmiths, with its chat')
    ev("profileSet('TIM', false); newRun(0, 'orp_run'); startStageNow('orp_run')"); time.sleep(1)
    lives0 = ev("run.lives")
    shots, last = [], -1
    t0 = time.time()
    while time.time() - t0 < 70:
        ev(BOT); time.sleep(0.05)
        st = ev("[mode, S.rb ? S.rb.phase : '', S.rb ? Math.round(S.rb.d) : 0, S.rb ? +S.rb.left.toFixed(1) : 0, S.rb ? S.rb.hits : 0]")
        k = int(st[2] / 2200)
        if st[0] == 'play' and k != last and len(shots) < 6:
            last = k; p = os.path.join(OUT, 'f.png'); pg.locator('canvas').first.screenshot(path=p)
            shots.append((f'd {st[2]}  left {st[3]}s  knocks {st[4]}', Image.open(p).convert('RGB').resize((960, 540))))
        if st[0] != 'play': break
    fin = ev("[mode, S.rb && S.rb.phase, S.rb && S.rb.hits, S.rb && +S.rb.left.toFixed(1), S.rb && S.rb.tries, clearInfo && clearInfo.rank, clearInfo && clearInfo.rows.map(r => r[0]).join(' | ')]")
    print('end:', fin)
    check(fin[1] == 'made' and fin[4] == 0, f'the bot made the coach first time (knocks {fin[2]}, {fin[3]}s to spare)')
    check(fin[0] in ('clear', 'chat') and fin[5] in list('SABCD'), f'points screen and rank {fin[5]}')
    # standing still misses it
    ev("held.clear(); profileSet('TIM', false); newRun(0, 'orp_run'); startStageNow('orp_run')"); time.sleep(1)
    ev("S.rb.left = 1.5; 0")
    for _ in range(40):
        time.sleep(0.5)
        if ev("S.rb.tries") == 1: break
    m = ev("[S.rb.phase, S.rb.tries, run.lives, mode]")
    check(m[1] == 1 and m[2] == lives0 and m[3] == 'play', f'missed: run again, try 2, no life lost {m}')
    p = os.path.join(OUT, 'f.png'); pg.locator('canvas').first.screenshot(path=p); shots.append(('after missing it', Image.open(p).convert('RGB').resize((960, 540))))
    cols = 2; sheet = Image.new('RGB', (480 * cols, 286 * ((len(shots) + 1) // 2)), (20, 22, 28)); d = ImageDraw.Draw(sheet)
    for i, (n, im) in enumerate(shots):
        x, y = (i % cols) * 480, (i // cols) * 286; sheet.paste(im.resize((480, 270)), (x, y + 16)); d.text((x + 4, y + 2), n, fill=(255, 210, 63))
    sheet.save(os.path.join(OUT, 'run.png'))
    br.close()
for e in errs: print('page error:', e)
print('PASS' if not bad and not errs else f'{len(bad)} failed, {len(errs)} page errors')
sys.exit(1 if bad or errs else 0)
