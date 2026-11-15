"""Version 85 talking bosses check, headless: python3 tools/v85/bosstalktest.py [--out dir]
Every boss card: its talking strip and its sound load; shown with the clock stopped at a few moments of its line, the
mouth is shut before it lands and moves after; the boss's own sound plays as it lands and the generic roar is skipped.
Saves a contact sheet of every card mid-line. Fails on any page error or a wrong answer."""
import http.server, os, socketserver, sys, threading, time
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw
opt = lambda k, d: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = opt('--out', '/tmp/v85bosstalk'); os.makedirs(OUT, exist_ok=True)
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
    pg = br.new_page(); pg.set_viewport_size({'width': 960, 'height': 540}); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(f'http://127.0.0.1:{port}/index.html?pubtest'); time.sleep(3)
    ev = lambda js: pg.evaluate('s => window.__pub(s)', js)
    ev("audioInit(); actx.resume(); settings.sound = true; 0"); time.sleep(3)
    check(ev("Object.keys(taunt.bufs).length") == 18, 'all 18 boss sounds load: ' + str(ev("Object.keys(taunt.bufs).length")))
    names = ev("Object.keys(BOSS_ART).filter(n => cardTalkId(n))")
    check(len(names) == 18, f'{len(names)} boss cards talk')
    ev("profileSet('TIM', false); newRun(0, 'frequency'); startStageNow('frequency')"); time.sleep(4)
    ev("step = dt => false; window.__render = window.__render || render; render = () => {}; foes.length = 0; 0")
    # count the sounds that play
    ev("window.__played = []; const ts = tauntPlay; tauntPlay = c => { window.__played.push(c.name); return ts(c); }; const s0 = sfx; sfx = k => { if (k === 'roar') window.__played.push('roar'); return s0(k); }; 0")
    shots = []
    for n in names:
        ev(f"S.card = {{ t: 0, len: 2.6, name: {n!r}, line: (Object.values(BOSS_CARD).find(c => c[0] === {n!r}) || [0, 'You lot again? Right.'])[1], spr: ['tim'] }}; 0")
        frames = []
        for t in (0.2, 0.6, 0.75, 0.9, 1.05):
            ev(f"S.card.t = {t}; if ({t} > 0.4) {{ const c = S.card; if (!c.slammed) {{ c.slammed = true; tauntPlay(c); }} }} window.__render(); 0")
            frames.append(ev(f"(() => {{ const c = S.card, a = bgImg('bosscard/' + BOSS_ART[c.name]); const f = cardTalkFrame(c, a); return f ? f.sx / a.width : -1; }})()"))
            if t == 0.9:
                p = os.path.join(OUT, 'f.png'); pg.locator('canvas').first.screenshot(path=p); shots.append((n, Image.open(p).convert('RGB').resize((960, 540))))
        check(frames[0] == 0 and any(f > 0 for f in frames[1:]), f'{n}: shut before it lands, then talks {frames}')
    check(sum(1 for p in ev("window.__played") if p != 'roar') == len(names), 'each card plays its own sound once')
    # the roar is skipped when the card has a sound, kept when it hasn't
    ev("window.__played = []; S.card = { t: 0, len: 2.6, name: 'THE PARKIE', line: 'x', spr: ['tim'] }; bossRoar(); 0")
    ev("timers.forEach(tm => { tm.t = -1; }); updateTimers ? 0 : 0");
    pg.evaluate("s => window.__pub(s)", "(() => { for (const tm of timers.splice(0)) tm.fn(); })()")
    check('roar' not in ev("window.__played"), 'no generic roar under a boss with its own sound')
    ev("window.__played = []; S.card = null; bossRoar(); 0")
    pg.evaluate("s => window.__pub(s)", "(() => { for (const tm of timers.splice(0)) tm.fn(); })()")
    check(ev("window.__played") == ['roar'], 'the generic roar still plays otherwise')
    cols = 3; sheet = Image.new('RGB', (480 * cols, 286 * ((len(shots) + cols - 1) // cols)), (20, 22, 28)); d = ImageDraw.Draw(sheet)
    for i, (n, im) in enumerate(shots):
        x, y = (i % cols) * 480, (i // cols) * 286; sheet.paste(im.resize((480, 270)), (x, y + 16)); d.text((x + 4, y + 2), n, fill=(255, 210, 63))
    sheet.save(os.path.join(OUT, 'cards.png'))
    br.close()
for e in errs: print('page error:', e)
print('PASS' if not bad and not errs else f'{len(bad)} failed, {len(errs)} page errors')
sys.exit(1 if bad or errs else 0)
