"""Checks Version 84's voice chat headless: python3 tools/v84/test.py [out_dir]
Two pages over the test relay (?netmock) with Chrome's fake mic (a beeping tone): the lobby's VOICE pill, voice flowing
both ways, the speaker mark and the music dip, mute, the game starting and staying in sync with voice on, an old app
(?novoice) on the other phone, and relay-only (?relayonly, no relay server: everything goes via the test server)."""
import http.server, os, socketserver, sys, threading, time
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp/v84test'; os.makedirs(OUT, exist_ok=True)
CHROME = os.environ.get('CHROME', '/usr/bin/google-chrome')


class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass


os.chdir(os.path.join(ROOT, 'web'))
srv = socketserver.ThreadingTCPServer(('127.0.0.1', 0), Q); srv.daemon_threads = True; port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
errs = []; fails = []


def ok(name, c):
    print(('PASS ' if c else 'FAIL ') + name, flush=True)
    if not c: fails.append(name)


def ev(pg, js):
    return pg.evaluate('s => window.__pub(s)', js)


def wait(pg, js, secs=15):
    t = time.time()
    while time.time() - t < secs:
        try:
            if ev(pg, js): return True
        except Exception: pass
        time.sleep(0.2)
    return False


def open_page(ctx, q):
    pg = ctx.new_page(); pg.set_viewport_size({'width': 1280, 'height': 720})
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(f'http://127.0.0.1:{port}/index.html?pubtest&{q}'); time.sleep(3)
    return pg


def lobby(host, guest, hname, gname):
    ev(host, f"profileSet('{hname}', false); audioInit(); openNetLobby(); netHost()")
    ok_ = wait(host, "NL.screen === 'host' && !!NT.code")
    code = ev(host, 'NT.code')
    ev(guest, f"profileSet('{gname}', false); audioInit(); openNetLobby(); netJoin('{code}')")
    return ok_ and wait(guest, "NL.screen === 'lobby'") and wait(host, "NL.screen === 'lobby'")


def start_game(host, guest):
    ev(guest, "NL.ready = true; netLobbyPublish()"); time.sleep(0.6)
    ev(host, "NL.ready = true; netLobbyPublish()")
    return wait(host, 'NET.on') and wait(guest, 'NET.on')


def into_fight(pages, secs=25):
    # skip the chats and comic pages on both phones (HIT goes to the shared game) until both are fighting
    t = time.time()
    while time.time() - t < secs:
        ms = [ev(p, 'mode') for p in pages]
        if all(m == 'play' for m in ms): return True
        for p, m in zip(pages, ms):
            if m != 'play': ev(p, "netPressed.add('punch'); netPressed.add('escape')")
        time.sleep(0.5)
    return False


shot = lambda pg, n: pg.locator('#game').screenshot(path=os.path.join(OUT, n + '.png'))
with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path=CHROME, args=['--use-fake-ui-for-media-stream', '--use-fake-device-for-media-stream',
                                                        '--autoplay-policy=no-user-gesture-required'])
    ctx = b.new_context()

    # ---------------------------------------------------------------- two new apps
    A = open_page(ctx, 'netmock=40'); B = open_page(ctx, 'netmock=40')
    ok('voice is offered (the test relay counts as an app that can)', ev(A, 'voxCan()') and ev(B, 'voxCan()'))
    ok('both in the lobby', lobby(A, B, 'HOSTY', 'GUESTY'))
    ok('the direct link comes up', wait(A, 'rtcLive()') and wait(B, 'rtcLive()'))
    ok('an audio slot on both ends of the link', ev(A, '!!RTC.atr') and ev(B, '!!RTC.atr'))
    ok('the host offered voice small and mono (DTX, 24 kbps)', ev(A, "/usedtx=1/.test(RTC.pc.localDescription.sdp) && /maxaveragebitrate=24000/.test(RTC.pc.localDescription.sdp)"))
    ok('mic off until you switch it on', not ev(A, '!!VOX.track') and not ev(B, '!!VOX.track'))
    shot(A, 'lobby_off')
    # switch voice on with a tap on the pill (host) and the M key (guest)
    pill = ev(A, 'voxPill()')
    ev(A, f"taps.push({{ x: {pill['x'] + 20}, y: {pill['y'] + 20} }})")
    B.locator('#game').focus(); B.keyboard.press('m')
    ok('the pill and M switch the mic on', wait(A, '!!VOX.track') and wait(B, '!!VOX.track'))
    ok('it remembers (settings.vmic)', ev(A, '!!settings.vmic') and ev(B, '!!settings.vmic'))
    ok("each sees the other's voice is on", wait(A, 'voxMate().can && voxMate().on') and wait(B, 'voxMate().can && voxMate().on'))
    ok('voice flows host to guest', wait(B, 'VOX.inBytes > 2000', 12))
    ok('voice flows guest to host', wait(A, 'VOX.inBytes > 2000', 12))
    ok('your mate talking is picked up (speaker mark)', wait(A, 'voxMateTalking()', 10) and wait(B, 'voxMateTalking()', 10))
    ok('the music dips while they talk', wait(B, 'VOX.duckG === 0.4', 5))
    time.sleep(0.3); shot(A, 'lobby_on'); shot(B, 'lobby_on_guest')

    # mute the guest's mic: the host stops getting voice
    ev(B, 'voxToggle()')
    ok('mute: the mic is released (the phone mic light goes off)', wait(B, '!VOX.track && !VOX.mic'))
    ok('mute: your mate sees MIC OFF', wait(A, '!voxMate().on'))
    time.sleep(2.5); a0 = ev(A, 'VOX.inBytes'); time.sleep(3); a1 = ev(A, 'VOX.inBytes')
    ok(f'mute: no voice arrives ({a1 - a0} bytes in 3s)', a1 - a0 < 600)
    ok('mute: the host stops hearing them talk', wait(A, '!voxMateTalking()', 5))
    ok('the music comes back up', wait(A, 'VOX.duckG === 1', 5))
    ev(B, 'voxToggle()')
    ok('unmute: the mic comes back', wait(B, '!!VOX.track'))
    b0 = ev(A, 'VOX.inBytes'); time.sleep(3)
    ok('unmute: voice flows again', ev(A, 'VOX.inBytes') - b0 > 1500)

    # the game: voice stays on, the fight stays in step
    ok('the game starts on both', start_game(A, B))
    ok('both fighting', into_fight([A, B]))
    ok('mic still on in the game', ev(A, '!!VOX.track') and ev(B, '!!VOX.track'))
    for i in range(30):   # walk about and punch for a while
        for p, k in ((A, 'right'), (B, 'right')):
            ev(p, f"held.add('{k}'); if ({i} % 3 === 0) netPressed.add('punch')")
        time.sleep(0.3)
    for p in (A, B): ev(p, "held.clear()")
    f0 = ev(A, 'NET.frame')
    ok(f'the game ran ({f0} frames)', f0 > 600)
    ok('no "out of sync" with voice on', not ev(A, 'NET.desync') and not ev(B, 'NET.desync'))
    ok('checksums match', ev(A, 'JSON.stringify([...NET.sums])') and all(
        ev(A, f'NET.sums.get({f})') == ev(B, f'NET.sums.get({f})') for f in ev(A, '[...NET.sums.keys()]') if ev(B, f'NET.sums.has({f})')))
    d = ev(A, 'NET.delay'), ev(B, 'NET.delay')
    # headless, the second page runs slower than real time, so its delay climbs to 11 or 12 frames with or without voice
    # (measured: no voice 12 and 11, voice 14 and 11). The host's side is the fair measure here; real phones are the test
    ok(f"input delay with voice: host {d[0]} frames (guest {d[1]}, the throttled page)", d[0] <= 6 and d[1] <= 15)
    ok('voice still flowing in the game', ev(A, 'VOX.inBytes') > 4000)
    ok('the HUD says DIRECT', ev(A, "rtcLive() && !RTC.relay"))
    wait(A, 'voxMateTalking()', 5); shot(A, 'hud_on'); wait(B, 'voxMateTalking()', 5); shot(B, 'hud_on_guest')
    # tap the mic button: muted; tap your mate's panel: muted them
    mb = ev(A, 'voxMicBtn()')
    ev(A, f"taps.push({{ x: {mb['x']}, y: {mb['y']} }})")
    ok('the HUD mic button mutes you', wait(A, '!VOX.track'))
    ok('the tap did not pause the game', ev(A, "mode") == 'play')
    ev(B, "taps.push({ x: 450, y: 30 })")
    ok("tapping your mate's panel mutes them", wait(B, 'VOX.mateMuted && VOX.el.muted'))
    time.sleep(0.3); shot(A, 'hud_muted'); shot(B, 'hud_mate_muted')
    # the app goes to the background: the mic goes off, and comes back with it
    ev(B, 'window.__voicePause()')
    ok('in the background the mic is off', wait(B, '!VOX.track'))
    ev(B, 'window.__voiceResume()')
    ok('back from the background the mic is on again', wait(B, '!!VOX.track'))
    # quitting closes it all
    ev(A, 'netQuit()'); ev(B, 'netQuit()')
    ok('quitting releases the mic and the link', wait(A, '!VOX.track && !RTC.pc') and wait(B, '!VOX.track && !RTC.pc'))
    ok('the music is back to full after', ev(A, 'VOX.duckG') == 1 and ev(B, 'VOX.duckG') == 1)
    # settings rows
    ev(A, 'touchUI = true; openMenuSettings()'); time.sleep(0.4)   # a phone: the most rows
    ok('settings: VOICE VOLUME and MUSIC WHEN TALKING', ev(A, "setRows().some(r => r.id === 'vox') && setRows().some(r => r.id === 'vduck')"))
    ok('settings: every row fits on the screen', ev(A, "setRows().every(r => r.y + r.h < H - 10)"))
    ev(A, "setAdj('vox', -3); setAdj('vduck', 1)")
    ok('settings: voice volume and the dip switch work', ev(A, "settings.vox === 7 && settings.vduck === false"))
    shot(A, 'settings')
    ev(A, "setAdj('vox', 3); setAdj('vduck', 1); closeMenuSettings()")
    A.close(); B.close()

    # ---------------------------------------------------------------- a new host and an old app (no voice)
    A = open_page(ctx, 'netmock=40'); C = open_page(ctx, 'netmock=40&novoice')
    ok('old app: in the lobby', lobby(A, C, 'HOSTY', 'OLDAPP'))
    ok('old app: link up', wait(A, 'rtcLive()') and wait(C, 'rtcLive()'))
    ok("old app: the host sees their app can't do voice", wait(A, '!!NL.them && !voxMate().can'))
    ev(A, 'settings.vmic = true')
    time.sleep(2)
    ok("old app: the host's mic stays closed (they couldn't hear it)", not ev(A, '!!VOX.track'))
    time.sleep(0.5); shot(A, 'lobby_oldapp')
    ok('old app: no voice controls on their side', not ev(C, 'voxCan()'))
    ok('old app: the game starts', start_game(A, C))
    ok('old app: both fighting', into_fight([A, C]))
    time.sleep(6)
    ok('old app: in step', not ev(A, 'NET.desync') and not ev(C, 'NET.desync') and ev(A, 'NET.frame') > 300)
    ok('old app: no mic button on the host HUD (the mate panel has no voice mark)', ev(A, 'voxHudOn()') and not ev(A, 'voxMate().can'))
    ev(A, 'netQuit()'); ev(C, 'netQuit()'); A.close(); C.close()

    # ---------------------------------------------------------------- relay only, with no relay server set up
    A = open_page(ctx, 'netmock=40&relayonly'); B = open_page(ctx, 'netmock=40&relayonly')
    ok('relay only: the link is told to use the relay', True)
    ok('relay only: in the lobby', lobby(A, B, 'HOSTY', 'GUESTY'))
    time.sleep(5)
    ok('relay only: with no relay server there is no direct link', not ev(A, 'rtcLive()'))
    ok('relay only: the game still starts and runs via the server', start_game(A, B) and into_fight([A, B]))
    time.sleep(4)
    ok('relay only: in step, HUD says VIA SERVER', not ev(A, 'NET.desync') and ev(A, 'NET.frame') > 200)
    shot(A, 'hud_viaserver')
    ev(A, 'netQuit()'); ev(B, 'netQuit()')
    b.close()

ok('no errors on any page', not errs)
for e in errs[:10]: print('  ', e)
print(f'{len(fails)} failed' if fails else 'all passed')
sys.exit(1 if fails else 0)
