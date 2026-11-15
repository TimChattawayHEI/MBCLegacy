// ================================================================== Version 85: music for the moments and the pub
// Tim, 15 November: more music, in the Smoking Area's style (dark half-time grime, 140 bpm, sparse heavy drums, sub bass
// slides, dry low stabs, no lead). All from PixelLab music; prompts and ids in tools/v85/music_prompts.json.
// - Stings, played once over silence: a stage cleared, the last boss down, game over, ON THE TAB, and a chapter's title
//   page. Each is cut from the start of a PixelLab take on the downbeat, two bars (three for game over) with a fade.
// - The pub and its games get their own loops (they borrowed stage tracks before; Kebab Siege had the N47's):
//   the pub, darts and the fruit machine, penalties, kiss chase, stay awake, the long drive, Snake and Kebab Siege.
//   These go in through NEW_MUSIC like the rest of the new soundtrack. With ?oldmusic they play the tracks they had.
const STING_VOL = { clear: 1.12, bossdown: 1.0, tab: 1.3, chapter: 1.46, gameover: 1.68 };   // matched to the soundtrack's loudness
var sting = { bufs: {}, loading: {}, src: null, gain: null, at: -99, key: '' };   // var: the hooks may run before this line
function stingLoad(k) {
  if (!sting || !actx || sting.bufs[k] || sting.loading[k]) return; sting.loading[k] = true;
  fetch('music/v85/sting_' + k + '.mp3').then(r => r.ok ? r.arrayBuffer() : Promise.reject(r.status))
    .then(b => new Promise((ok, no) => { const p = actx.decodeAudioData(b, ok, no); if (p && p.then) p.then(ok, no); }))
    .then(buf => { sting.bufs[k] = buf; }).catch(() => {});
}
function stingStop() { if (sting && sting.src) { try { sting.src.stop(); sting.src.disconnect(); } catch (e) { /* done */ } sting.src = null; } }
function stingPlay(k) {
  if (!sting || !actx || !settings.sound) return;
  const b = sting.bufs[k]; if (!b) { stingLoad(k); return; }   // not loaded yet: silence, as before
  stingStop();
  if (!sting.gain) { sting.gain = actx.createGain(); sting.gain.connect(musBus); }
  sting.gain.gain.value = TRACK_GAIN * (STING_VOL[k] || 1);
  const s = actx.createBufferSource(); s.buffer = b; s.connect(sting.gain); s.start(actx.currentTime + 0.02);
  s.onended = () => { if (sting.src === s) sting.src = null; };
  sting.src = s; sting.at = actx.currentTime; sting.key = k;
}
// true when sting k started under s seconds ago
function stingRecent(k, s) { return !!(sting && actx && sting.key === k && actx.currentTime - sting.at < s); }
function stingsPreload() { for (const k in STING_VOL) stingLoad(k); }

// the pub's and the games' own tracks, with the tracks they used before for ?oldmusic and as a fallback
const PUB_MUSIC_WAS = { pub: 'social', pubgames: 'social', pens: 'garage', kiss: 'soundz', awake: 'road', golf: 'naval', snake: 'nightbus', kebab: 'nightbus' };
for (const k in PUB_MUSIC_WAS) {
  const was = TRACKS[PUB_MUSIC_WAS[k]];
  if (!TRACKS[k]) TRACKS[k] = was;   // ?oldmusic
  else if (TRACKS[k] !== was) { TRACKS[k].old = was && (was.old || was); TRACKS[k].fb = (was && was.fb) || 'garage'; }
}
// after the Snake cabinet is added (it is set up on a timer at start-up)
setTimeout(() => {
  const set = { darts: 'pubgames', fruit: 'pubgames', pens: 'pens', kiss: 'kiss', awake: 'awake', golf: 'golf', snake: 'snake' };
  for (const id in set) if (MINI_DEF[id]) MINI_DEF[id].music = set[id];
  if (STAGES.kebab) STAGES.kebab.music = 'kebab';
}, 30);
