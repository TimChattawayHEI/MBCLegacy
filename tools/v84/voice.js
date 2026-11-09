// ================================================================== VOICE CHAT (Version 84)
// The two phones in an online game can talk. Voice rides on the same direct link as the button presses (RTC.pc):
// the host puts an audio slot in its offer, the guest turns it on in its answer, and the mic is attached to it
// later (replaceTrack), so switching voice on or off never touches the connection. Voice sits outside the lockstep
// game, like music: it never uses the shared random numbers and nothing in the fight depends on it.
// Only in the app (an APK that has the mic permission says so through MBCNative.canVoice), or ?netmock for testing.
const VOX = { el: null, stream: null, track: null, mic: null, sender: null, pending: false, denied: false, hidden: !!document.hidden,
  mateMuted: false, an: null, myAn: null, buf: null, lvl: 0, myLvl: 0, mateT: 0, meT: 0, duck: null, duckG: 1,
  note: '', noteT: 0, statT: 0, live: false, inBytes: 0, outBytes: 0 };
function voxCan() {
  if (/[?&]novoice/.test(location.search)) return false;   // testing: behave like an old app
  if (typeof RTCPeerConnection === 'undefined' || !navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) return false;
  try { if (window.MBCNative && typeof window.MBCNative.canVoice === 'function') return !!window.MBCNative.canVoice(); } catch (e) { /* old app */ }
  return netMockWanted();
}
function voxNative(on) { try { if (window.MBCNative && typeof window.MBCNative.voice === 'function') window.MBCNative.voice(!!on); } catch (e) { /* old app */ } }
function voxNote(s, secs) { VOX.note = s; VOX.noteT = performance.now() + (secs || 5) * 1000; }

// ------------------------------------------------------------------ the relay server (TURN): web/net.json
// { "iceServers": [ { "urls": ["turn:...:80", "turns:...:443?transport=tcp"], "username": "...", "credential": "..." } ] }
// Lets the phones reach each other when a direct link is blocked (some 4G networks, strict routers). Without it voice
// only works on a direct link, and button presses fall back to Firebase as before. ?relayonly forces the relay (testing).
const NETCFG = { ice: null };
try { fetch('net.json', { cache: 'no-store' }).then(r => r.ok ? r.json() : null).then(j => { if (j && Array.isArray(j.iceServers)) NETCFG.ice = j.iceServers.filter(s => s && s.urls); }).catch(() => {}); } catch (e) { /* no fetch */ }
function voxIce() {
  const base = [{ urls: ['stun:stun.l.google.com:19302', 'stun:stun1.l.google.com:19302'] }];
  return { iceServers: base.concat(NETCFG.ice || []), iceTransportPolicy: /[?&]relayonly/.test(location.search) ? 'relay' : 'all' };
}

// ------------------------------------------------------------------ the audio slot on the connection
function voxWire(pc, role) {
  RTC.atr = null; RTC.relay = false;
  if (!voxCan()) return;
  pc.ontrack = e => { if (RTC.pc === pc && e.track && e.track.kind === 'audio') voxRemote(e.streams && e.streams[0] ? e.streams[0] : new MediaStream([e.track])); };
  if (role === 'h') { try { RTC.atr = pc.addTransceiver('audio', { direction: 'sendrecv' }); } catch (e) { RTC.atr = null; } }
}
// the guest, once it has the host's offer: answer with voice both ways (an old app answers listen-only by itself)
function voxGuestSlot(pc) {
  if (!voxCan()) return;
  try {
    const t = pc.getTransceivers().find(x => x.receiver && x.receiver.track && x.receiver.track.kind === 'audio');
    if (t) { t.direction = 'sendrecv'; RTC.atr = t; }
  } catch (e) { /* no voice */ }
}
// small, mono, and next to nothing while nobody's talking
function voxSdp(d) {
  if (!voxCan() || !d || !d.sdp) return d;
  const m = d.sdp.match(/a=rtpmap:(\d+) opus\/48000/i); if (!m) return d;
  const pt = m[1], re = new RegExp('a=fmtp:' + pt + ' ([^\\r\\n]*)');
  let sdp = d.sdp;
  if (re.test(sdp)) sdp = sdp.replace(re, (all, p) => 'a=fmtp:' + pt + ' ' + p.split(';').filter(x => !/^(usedtx|stereo|sprop-stereo|maxaveragebitrate)=/.test(x.trim())).concat(['usedtx=1', 'stereo=0', 'sprop-stereo=0', 'maxaveragebitrate=24000']).join(';'));
  return { type: d.type, sdp };
}
function voxBitrate(sender) {
  try { const p = sender.getParameters(); if (!p.encodings || !p.encodings.length) p.encodings = [{}]; p.encodings[0].maxBitrate = 24000; sender.setParameters(p).catch(() => {}); } catch (e) { /* defaults are fine */ }
}

// ------------------------------------------------------------------ your mate's voice
function voxRemote(stream) {
  VOX.stream = stream;
  if (!VOX.el) {
    const el = document.createElement('audio'); el.autoplay = true; el.setAttribute('playsinline', ''); el.style.display = 'none';
    document.body.appendChild(el); VOX.el = el;
  }
  VOX.el.srcObject = stream; voxVolume();
  VOX.el.play().catch(() => {});
  // a level meter on it (for the speaker mark and the music dip); it plays through the <audio> element, not this
  audioInit(); VOX.an = null;
  if (actx) { try { const src = actx.createMediaStreamSource(stream), an = actx.createAnalyser(); an.fftSize = 512; src.connect(an); VOX.an = an; } catch (e) { /* no meter */ } }
}
function voxVolume() { if (VOX.el) { VOX.el.volume = clamp((settings.vox ?? 10) / 10, 0, 1); VOX.el.muted = VOX.mateMuted; } }
function voxLevel(an) {
  if (!an) return 0;
  if (!VOX.buf || VOX.buf.length !== an.fftSize) VOX.buf = new Float32Array(an.fftSize);
  an.getFloatTimeDomainData(VOX.buf); let s = 0; for (let i = 0; i < VOX.buf.length; i++) s += VOX.buf[i] * VOX.buf[i];
  return Math.sqrt(s / VOX.buf.length);
}
function voxMateTalking() { return !VOX.mateMuted && performance.now() < VOX.mateT; }
function voxMeTalking() { return !!VOX.track && performance.now() < VOX.meT; }
// the music dips while your mate talks (Settings: MUSIC WHEN TALKING)
function voxDuck(on) {
  if (!actx || !musBus) return;
  if (!VOX.duck) { VOX.duck = actx.createGain(); try { musBus.disconnect(); } catch (e) { /* not connected */ } musBus.connect(VOX.duck); VOX.duck.connect(actx.destination); }
  const g = on && settings.vduck !== false ? 0.4 : 1;
  if (g !== VOX.duckG) { VOX.duckG = g; VOX.duck.gain.setTargetAtTime(g, actx.currentTime, g < 1 ? 0.05 : 0.18); }
}

// ------------------------------------------------------------------ your mic
// On in an online lobby or game when you've switched voice on (it remembers), off when the app is in the background
function voxWant() {
  if (!voxCan() || !settings.vmic || VOX.hidden || VOX.denied || !RTC.pc || !RTC.atr) return false;
  if (NL.them && !NL.them.vx) return false;   // an old app on the other phone can't hear you: keep the mic closed
  return (mode === 'net' && NL.screen === 'lobby') || (NET.on && !NET.solo);
}
async function voxMicStart() {
  VOX.pending = true;
  const atr = RTC.atr;
  try {
    const s = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true, channelCount: 1 }, video: false });
    const t = s.getAudioTracks()[0];
    if (!t || !voxWant() || RTC.atr !== atr) { s.getTracks().forEach(x => x.stop()); return; }
    await atr.sender.replaceTrack(t);
    VOX.track = t; VOX.mic = s; VOX.sender = atr.sender;
    voxBitrate(atr.sender);
    VOX.myAn = null;
    if (actx) { try { const src = actx.createMediaStreamSource(s), an = actx.createAnalyser(); an.fftSize = 512; src.connect(an); VOX.myAn = an; } catch (e) { /* no meter */ } }
    t.addEventListener('ended', () => { if (VOX.track === t) voxMicStop(); });
    voxNative(true); VOX.live = true;
    voxPublish();
  } catch (e) {
    VOX.denied = true;
    voxNote(e && (e.name === 'NotAllowedError' || e.name === 'SecurityError') ? "Mic's off (no permission).\nYou can still hear your mate." : "Couldn't find a mic.\nYou can still hear your mate.", 6);
    voxPublish();
  } finally { VOX.pending = false; }
}
function voxMicStop() {
  const t = VOX.track, s = VOX.mic, snd = VOX.sender;
  VOX.track = null; VOX.mic = null; VOX.sender = null; VOX.myAn = null; VOX.meT = 0;
  try { if (s) s.getTracks().forEach(x => x.stop()); else if (t) t.stop(); } catch (e) { /* gone */ }
  if (snd) snd.replaceTrack(null).catch(() => {});
  if (VOX.live) { VOX.live = false; voxNative(false); }
  voxPublish();
}
// one switch: the lobby's VOICE pill, the mic button in a game and the M key all flip it
function voxToggle() {
  if (!voxCan()) return;
  if (VOX.denied) { VOX.denied = false; settings.vmic = true; }
  else settings.vmic = !settings.vmic;
  if (settings.vmic && !lsGet('mbc.voxseen', false)) { lsSet('mbc.voxseen', true); voxNote('Your phone will ask for the mic.\nYour voice only goes to your mate.', 6); }
  saveSettings(); sfx(settings.vmic ? 'start' : 'page');
  voxPublish(); voxTick();
}
function voxMuteMate() { VOX.mateMuted = !VOX.mateMuted; voxVolume(); sfx('page'); }
// tell your mate whether you've voice (vx: your app can, vm: your mic is on); rides on the lobby entry
function voxPublish() { if (NET.role && NT.kind && NT.code && (mode === 'net' || NET.on)) try { netLobbyPublish(); } catch (e) { /* later */ } }
function voxMate() { const t = NL.them || {}; return { can: !!t.vx, on: !!t.vm }; }

// ------------------------------------------------------------------ the loop (outside the game's frames)
function voxTick() {
  const now = performance.now();
  if (VOX.track && VOX.sender !== (RTC.atr && RTC.atr.sender)) voxMicStop();   // the link was remade
  const want = voxWant();
  if (want && !VOX.track && !VOX.pending) voxMicStart();
  if (!want && VOX.track) voxMicStop();
  if (VOX.an) { VOX.lvl = voxLevel(VOX.an); if (VOX.lvl > 0.012) VOX.mateT = now + 350; }
  if (VOX.myAn) { VOX.myLvl = voxLevel(VOX.myAn); if (VOX.myLvl > 0.02) VOX.meT = now + 300; }
  voxDuck(voxMateTalking() && (NET.on || mode === 'net'));
  // which way the link goes (DIRECT or through the relay) and how much voice is flowing, every couple of seconds
  if (RTC.pc && now - VOX.statT > 2000) {
    VOX.statT = now; const pc = RTC.pc;
    pc.getStats().then(r => {
      if (RTC.pc !== pc) return;
      let pair = null; const by = {};
      r.forEach(s => { by[s.id] = s; });
      r.forEach(s => { if (s.type === 'transport' && s.selectedCandidatePairId) pair = by[s.selectedCandidatePairId]; });
      if (!pair) r.forEach(s => { if (s.type === 'candidate-pair' && s.nominated && s.state === 'succeeded') pair = s; });
      const lc = pair && by[pair.localCandidateId], rc = pair && by[pair.remoteCandidateId];
      RTC.relay = !!((lc && lc.candidateType === 'relay') || (rc && rc.candidateType === 'relay'));
      r.forEach(s => { if (s.kind === 'audio' && s.type === 'inbound-rtp') VOX.inBytes = s.bytesReceived || 0; if (s.kind === 'audio' && s.type === 'outbound-rtp') VOX.outBytes = s.bytesSent || 0; });
    }).catch(() => {});
  }
}
setInterval(() => { try { voxTick(); } catch (e) { /* never stop the game for voice */ } }, 50);
document.addEventListener('visibilitychange', () => { VOX.hidden = document.hidden; voxTick(); });
window.__voicePause = () => { VOX.hidden = true; voxTick(); };
window.__voiceResume = () => { VOX.hidden = document.hidden; if (VOX.track) voxNative(true); voxTick(); };
// M flips your mic in an online lobby or game (it's the sound key everywhere else)
window.addEventListener('keydown', e => {
  if (e.code !== 'KeyM' || !voxCan() || !(NET.on || (mode === 'net' && NL.screen === 'lobby'))) return;
  const tg = e.target && e.target.tagName; if (tg === 'INPUT' || tg === 'TEXTAREA') return;
  e.preventDefault(); e.stopImmediatePropagation(); if (!e.repeat) voxToggle();
}, true);

// ------------------------------------------------------------------ hooks into the lobby, the link and the HUD
const voxRtcStop = rtcStop;
rtcStop = function () {
  if (VOX.track) voxMicStop();
  VOX.stream = null; VOX.an = null; VOX.mateT = 0; if (VOX.el) { try { VOX.el.srcObject = null; } catch (e) { /* gone */ } }
  VOX.denied = false; VOX.mateMuted = false; voxDuck(false);
  RTC.atr = null; RTC.relay = false;
  return voxRtcStop.apply(this, arguments);
};
const voxLobbyPublish = netLobbyPublish;
netLobbyPublish = function () {
  // the same as before plus vx / vm, so an old app on the other phone just ignores them
  const put = NT.put; NT.put = function (path, val) { if (val && typeof val === 'object' && /^lobby_/.test(path)) { val.vx = voxCan() ? 1 : 0; val.vm = voxCan() && settings.vmic && !VOX.denied ? 1 : 0; } return put.apply(this, arguments); };
  try { return voxLobbyPublish.apply(this, arguments); } finally { NT.put = put; }
};
function voxPill() { return { x: W - 170, y: 18, w: 150, h: 40 }; }
function voxInside(t, b) { return t.x > b.x && t.x < b.x + b.w && t.y > b.y && t.y < b.y + b.h; }
const voxUpdateLobby = updateNetLobby;
updateNetLobby = function () {
  if (NL.screen === 'lobby' && voxCan()) {
    const b = voxPill();
    for (let i = taps.length - 1; i >= 0; i--) if (voxInside(taps[i], b)) { taps.splice(i, 1); voxToggle(); }
  }
  return voxUpdateLobby.apply(this, arguments);
};
function voxMicBtn() { const pb = pauseBtn(); return { x: pb.x - 52, y: pb.y, r: 19 }; }
const VOX_MATE_PANEL = { x: 384, y: 12, w: 210, h: 50 };
function voxHudOn() { return voxCan() && NET.on && !NET.solo && PL.length === 2; }
const voxFrameLoop = netFrameLoop;
netFrameLoop = function (realDt) {
  if (mode === 'play' && voxHudOn()) {
    const mb = voxMicBtn();
    for (let i = taps.length - 1; i >= 0; i--) {
      const t = taps[i];
      if (Math.hypot(t.x - mb.x, t.y - mb.y) < mb.r + 8) { taps.splice(i, 1); voxToggle(); }
      else if (voxMate().can && voxInside(t, VOX_MATE_PANEL)) { taps.splice(i, 1); voxMuteMate(); }
    }
  }
  return voxFrameLoop.apply(this, arguments);
};
// a microphone, drawn in code like the rest of the HUD: on (with a ring while you talk), or crossed out
function voxDrawMic(x, y, s, on, talking, col) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  ctx.fillStyle = col; ctx.strokeStyle = col; ctx.lineWidth = 2.4;
  rrect(-4, -10, 8, 13, 4); ctx.fill();
  ctx.beginPath(); ctx.arc(0, -1, 7.5, 0.15 * Math.PI, 0.85 * Math.PI); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(0, 6.5); ctx.lineTo(0, 10); ctx.moveTo(-4.5, 10.5); ctx.lineTo(4.5, 10.5); ctx.stroke();
  if (!on) { ctx.strokeStyle = OUT; ctx.lineWidth = 5; ctx.beginPath(); ctx.moveTo(-10, -11); ctx.lineTo(10, 11); ctx.stroke(); ctx.strokeStyle = '#e5484d'; ctx.lineWidth = 2.6; ctx.stroke(); }
  ctx.restore();
}
// a speaker with sound waves (your mate talking), or crossed out (you've muted them)
function voxDrawSpeaker(x, y, s, muted, t) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.lineCap = 'round';
  ctx.fillStyle = OUT; ctx.beginPath(); ctx.arc(1, 0, 11, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = muted ? '#93a3a1' : '#7fcf5a';
  ctx.beginPath(); ctx.moveTo(-6, -3); ctx.lineTo(-3, -3); ctx.lineTo(2, -7); ctx.lineTo(2, 7); ctx.lineTo(-3, 3); ctx.lineTo(-6, 3); ctx.closePath(); ctx.fill();
  if (muted) { ctx.strokeStyle = '#e5484d'; ctx.lineWidth = 2.2; ctx.beginPath(); ctx.moveTo(4, -4); ctx.lineTo(9, 4); ctx.moveTo(9, -4); ctx.lineTo(4, 4); ctx.stroke(); }
  else { ctx.strokeStyle = '#7fcf5a'; ctx.lineWidth = 1.8; const k = 0.75 + 0.25 * Math.sin(t * 18); ctx.beginPath(); ctx.arc(2, 0, 4.5, -0.9, 0.9); ctx.stroke(); ctx.globalAlpha = k; ctx.beginPath(); ctx.arc(2, 0, 8, -0.9, 0.9); ctx.stroke(); }
  ctx.restore();
}
const voxDrawLobby = drawNetLobby;
drawNetLobby = function () {
  voxDrawLobby.apply(this, arguments);
  if (NL.screen !== 'lobby' || !voxCan()) return;
  const b = voxPill(), on = !!settings.vmic && !VOX.denied, me = voxMeTalking();
  rrect(b.x, b.y, b.w, b.h, 10); ctx.fillStyle = on ? '#22402c' : 'rgba(24,36,42,0.92)'; ctx.fill();
  ctx.strokeStyle = me ? '#7fcf5a' : on ? '#3f8a52' : '#2b3b42'; ctx.lineWidth = me ? 4 : 2; ctx.stroke();
  voxDrawMic(b.x + 24, b.y + b.h / 2, 1, on, me, on ? '#7fcf5a' : '#93a3a1');
  const lab = VOX.denied ? 'MIC BLOCKED' : VOX.pending ? 'ASKING...' : on ? 'VOICE ON' : 'VOICE OFF';
  textOut(lab, b.x + 44, b.y + b.h / 2, '15px ' + DISPLAY, on ? '#efe6d2' : '#93a3a1', OUT, 4, 'left');
  // under each lad: whether they've voice on
  const hostIsMe = NET.role === 'h', mate = voxMate();
  const st = (x, can, mic, talking) => {
    const s = !can ? 'NO VOICE ON THEIR APP' : mic ? (talking ? 'TALKING' : 'VOICE ON') : 'MIC OFF';
    ctx.font = '800 11px ' + BODY; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillStyle = !can ? '#c9a46a' : talking ? '#7fcf5a' : mic ? '#9fd3a8' : '#93a3a1'; ctx.fillText(s, x, 134);
    if (talking) voxDrawSpeaker(x + (s.length * 3.4) + 18, 134, 0.8, false, time);
  };
  const myX = hostIsMe ? W / 2 - 230 : W / 2 + 230, mateX = hostIsMe ? W / 2 + 230 : W / 2 - 230;
  st(myX, true, on, me);
  if (NL.them) st(mateX, mate.can, mate.on, voxMateTalking());
  if (NL.them && !mate.can && performance.now() > VOX.noteT) voxNote("Your mate's app can't do voice.\nThey need the new app.", 0.1);
  if (performance.now() < VOX.noteT && VOX.note) { ctx.font = '700 12px ' + BODY; ctx.fillStyle = '#efe6d2'; ctx.textAlign = 'right'; ctx.textBaseline = 'middle'; VOX.note.split('\n').forEach((l, i) => ctx.fillText(l, b.x + b.w, 74 + i * 16)); }
};
const voxDrawHud = drawNetHud;
drawNetHud = function () {
  voxDrawHud.apply(this, arguments);
  if (mode !== 'play' || cutin || !voxHudOn()) return;
  // your mic button, by pause
  const mb = voxMicBtn(), on = !!settings.vmic && !VOX.denied, me = voxMeTalking();
  ctx.fillStyle = 'rgba(12,16,20,0.72)'; ctx.beginPath(); ctx.arc(mb.x, mb.y, mb.r, 0, Math.PI * 2); ctx.fill();
  ctx.strokeStyle = me ? '#7fcf5a' : on ? '#3f8a52' : '#5d6a6c'; ctx.lineWidth = me ? 4 : 2.5; ctx.stroke();
  voxDrawMic(mb.x, mb.y, 0.95, on, me, on ? '#efe6d2' : '#93a3a1');
  // your mate talking (or muted by you), on their face in the partner panel
  const mate = PL[1 - NET.me];
  if (mate && !mate.gone && voxMate().can) {
    if (VOX.mateMuted) voxDrawSpeaker(576, 26, 0.9, true, time);
    else if (voxMateTalking()) voxDrawSpeaker(576, 26, 0.9, false, time);
  }
  if (performance.now() < VOX.noteT && VOX.note) { ctx.font = '700 12px ' + BODY; ctx.fillStyle = '#efe6d2'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(VOX.note.replace('\n', ' '), W / 2, 96); }
};
// Settings: VOICE VOLUME and MUSIC WHEN TALKING (only on an app that can do voice)
const voxSetAdj = setAdj;
setAdj = function (id, d) {
  if (id === 'vox') { settings.vox = clamp((settings.vox ?? 10) + d, 0, 10); voxVolume(); saveSettings(); sfx('swing'); return; }
  if (id === 'vduck') { settings.vduck = settings.vduck === false; saveSettings(); sfx('swing'); return; }
  return voxSetAdj.apply(this, arguments);
};
