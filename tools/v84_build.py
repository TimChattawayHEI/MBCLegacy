"""Version 84: voice chat in online co-op. Run from the repo root after the other builds: python3 tools/v84_build.py.
Safe to run again.

- Voice rides on the lobby's WebRTC link (rtcStart): the host's offer carries an audio slot, the guest answers with
  voice both ways, and the mic is attached later, so switching it on or off never touches the connection.
- The relay server (TURN) comes from web/net.json; the HUD and lobby say DIRECT, RELAY or VIA SERVER.
- Lobby VOICE pill, a mic button by pause, a speaker mark on your mate's face when they talk (tap their panel to mute
  them), M to flip your mic, the music dips while your mate talks. Settings: VOICE VOLUME, MUSIC WHEN TALKING.
- Only where the app says it can (MBCNative.canVoice, the Version 84 APK), or ?netmock for testing.
The game code is tools/v84/voice.js, put in the page between `// V84 voice start` and `// V84 voice end`.
The Android side (the mic permission, the loudspeaker while voice is live) is in android/: it needs a full APK."""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, 'web', 'index.html')
read = lambda p: open(p, encoding='utf-8').read()
s = read(PAGE)


def put(s, start, end, content, anchor):
    full = start + '\n' + content.rstrip('\n') + '\n' + end
    if start in s: return re.sub(re.escape(start) + r'.*?' + re.escape(end), lambda m: full, s, count=1, flags=re.S)
    if s.count(anchor) != 1: sys.exit(f'v84_build: could not find {anchor[:60]!r}')
    return s.replace(anchor, full + '\n' + anchor)


def swap(s, name, old, new):
    if new in s: return s
    if s.count(old) != 1: sys.exit(f'v84_build: {name}: found {s.count(old)} copies of {old[:60]!r}')
    return s.replace(old, new)


s = put(s, '// V84 voice start', '// V84 voice end', read(os.path.join(ROOT, 'tools', 'v84', 'voice.js')),
        '// ================================================================== step & render')

SWAPS = [
    ('relay config and the audio slot',
     "  try { pc = new RTCPeerConnection({ iceServers: [{ urls: ['stun:stun.l.google.com:19302', 'stun:stun1.l.google.com:19302'] }] }); } catch (e) { return; }\n  RTC.pc = pc; const n = ++RTC.n;\n",
     "  try { pc = new RTCPeerConnection(voxIce()); } catch (e) { return; }   // Version 84: the relay server from net.json\n  RTC.pc = pc; const n = ++RTC.n; voxWire(pc, role);   // Version 84: an audio slot for voice\n"),
    ('the host\'s offer',
     "pc.createOffer().then(o => pc.setLocalDescription(o))",
     "pc.createOffer().then(o => pc.setLocalDescription(voxSdp(o)))"),
    ('the guest\'s answer',
     "pc.setRemoteDescription({ type: 'offer', sdp: v.sdp }).then(() => pc.createAnswer()).then(a => pc.setLocalDescription(a))",
     "pc.setRemoteDescription({ type: 'offer', sdp: v.sdp }).then(() => { voxGuestSlot(pc); return pc.createAnswer(); }).then(a => pc.setLocalDescription(voxSdp(a)))"),
    ('HUD link label',
     "(rtcLive() ? 'DIRECT' : 'VIA SERVER')",
     "(rtcLive() ? (RTC.relay ? 'RELAY' : 'DIRECT') : 'VIA SERVER')"),
    ('lobby link label',
     "ctx.fillText(rtcLive() ? 'DIRECT LINK: ON' : 'DIRECT LINK: TRYING (works without it, just slower)', W / 2, 140)",
     "ctx.fillText(rtcLive() ? (RTC.relay ? 'LINK: THROUGH THE RELAY' : 'DIRECT LINK: ON') : 'DIRECT LINK: TRYING (works without it, just slower)', W / 2, 140)"),
    ('settings rows',
     "    { id: 'fx', label: 'EFFECTS', vol: true },\n",
     "    { id: 'fx', label: 'EFFECTS', vol: true },\n"
     "    { id: 'vox', label: 'VOICE VOLUME', vol: true, voice: true },   // Version 84\n"
     "    { id: 'vduck', label: 'MUSIC WHEN TALKING', val: settings.vduck === false ? 'STAYS' : 'DIPS', voice: true },\n"),
    ('settings filter',
     "  ].filter(r => !r.touch || touchUI || (r.id === 'buzz' && canBuzz()));",
     "  ].filter(r => (!r.touch || touchUI || (r.id === 'buzz' && canBuzz())) && (!r.voice || voxCan()));"),
    ('settings spacing',
     "const sp = rows.length > 13 ? 26 :",
     "const sp = rows.length > 15 ? 24 : rows.length > 13 ? 26 :"),
    ('settings panel grows to fit the rows',
     "  rrect(x, 70, 470, 404, 12); ctx.fillStyle = 'rgba(24,36,42,0.95)'; ctx.fill(); ctx.strokeStyle = '#2b3b42'; ctx.lineWidth = 2; ctx.stroke();\n  if (pauseTab === 'scores')",
     "  const ph = pauseTab === 'settings' ? (rl => Math.max(404, rl.y + rl.h + 12 - 70))(setRows().slice(-1)[0]) : 404;   // Version 84: room for the voice rows\n"
     "  rrect(x, 70, 470, ph, 12); ctx.fillStyle = 'rgba(24,36,42,0.95)'; ctx.fill(); ctx.strokeStyle = '#2b3b42'; ctx.lineWidth = 2; ctx.stroke();\n  if (pauseTab === 'scores')"),
]
for name, old, new in SWAPS: s = swap(s, name, old, new)

open(PAGE, 'w', encoding='utf-8').write(s)
print('v84_build: voice chat in')
