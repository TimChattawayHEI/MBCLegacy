// The new soundtrack (Version 85): every stage and boss theme made again with PixelLab's music, in the style of the title
// theme Tim rated best by a lot. Each file plays its intro once, then loops from `from` for `loop` seconds; `end` is the
// file's length (to spot a browser that kept the MP3 lead-in). The Mega Drive tracks they replace stay in web/music and
// play again with ?oldmusic in the address, and still stand in if a new file fails to load.
// bpm/beat0 (the tempo and the first beat in the file, found by tools/v85/beats.py) keep Atlantis's BEAT ring on the beat.
const NEW_MUSIC = /*NEW_MUSIC*/{}/*END*/;
if (!/[?&]oldmusic\b/.test(location.search)) for (const k in NEW_MUSIC) {
  const [from, le, end, vol, bpm, beat0] = NEW_MUSIC[k];
  TRACKS[k] = { src: 'music/v85/' + k + '.mp3', from, loop: le - from, end, vol, bpm, beat0, fb: (TRACKS[k] && TRACKS[k].fb) || 'garage', old: TRACKS[k] };
}
// where the playing track is in its own file, seconds (the intro once, then round the loop)
function trackFilePos() {
  const T = TRACKS[trk.key]; if (!T || !actx || !trk.src) return null;
  const lat = (actx.outputLatency || 0) + (actx.baseLatency || 0), el = actx.currentTime - lat - trk.t0;
  if (!T.from) return ((el % trk.len) + trk.len) % trk.len;
  return el < T.from ? el : T.from + (el - T.from) % T.loop;
}
