// Recorded sound effects (Version 85): made with PixelLab's sound effects (prompts in tools/v85/sfx_prompts.json), trimmed,
// faded and levelled into web/sfx at 24 kHz mono. sfx(kind) plays one of the kind's takes, a touch faster or slower each time,
// and falls back to the old synthesised sound for any kind with no take or while the files are still loading.
// ?classicsfx in the address plays the old synthesised sounds only, to compare.
const SFX_TAKES = {
  hit: ['hit_1', 'hit_2', 'hit_3'], heavy: ['heavy_1', 'heavy_2'], swing: ['swing_1', 'swing_2'], fall: ['fall_1', 'fall_2'], ouch: ['ouch_1', 'ouch_2'],
  ko: ['ko'], smash: ['smash'], break: ['break'], grab: ['grab'], throw: ['throw'], land: ['land'], splash: ['splash'], boom: ['boom'],
  airhorn: ['airhorn'], scratch: ['scratch'], clink: ['clink'], dart: ['dart'], thunk: ['thunk'], whistle: ['whistle'], special: ['special'],
  door: ['door'], engine: ['engine'], honk: ['honk'], bang: ['bang'], snore: ['snore'], fire: ['fire'], hiss: ['hiss'],
  // batch 2: enemy voices, eating, picking up a weapon, jumping, the crowd at a stage clear, a boss arriving
  grunt: ['grunt_m1', 'grunt_m2', 'grunt_m3'], gruntf: ['grunt_f1', 'grunt_f2'], cry: ['cry_m1', 'cry_m2'], cryf: ['cry_f1', 'cry_f2'],
  eat: ['eat'], wpick: ['wpick'], jump: ['jump'], cheer: ['cheer'], roar: ['roar'],
};
const SFX_VOL = { hit: 0.55, heavy: 0.7, swing: 0.3, fall: 0.6, ouch: 0.45, ko: 0.8, smash: 0.6, break: 0.6, grab: 0.55, throw: 0.5, land: 0.4,
  splash: 0.6, boom: 0.7, airhorn: 0.55, scratch: 0.5, clink: 0.5, dart: 0.6, thunk: 0.6, whistle: 0.4, special: 0.7, door: 0.6, engine: 0.5,
  honk: 0.5, bang: 0.6, snore: 0.5, fire: 0.5, hiss: 0.4, grunt: 0.42, gruntf: 0.42, cry: 0.5, cryf: 0.5, eat: 0.6, wpick: 0.5,
  jump: 0.28, cheer: 0.5, roar: 0.6 };
const SFX_STEADY = new Set(['airhorn', 'whistle', 'honk', 'scratch']);   // these keep their pitch
const sfxBufs = {};
let sfxLoading = false;
const sfxClassic = /[?&]classicsfx\b/.test(location.search);
function sfxLoad() {
  if (sfxLoading || !actx || sfxClassic) return; sfxLoading = true;
  const names = [...new Set(Object.values(SFX_TAKES).flat())];
  names.forEach(n => fetch('sfx/' + n + '.wav').then(r => r.ok ? r.arrayBuffer() : Promise.reject(r.status))
    .then(b => new Promise((ok, no) => { const p = actx.decodeAudioData(b, ok, no); if (p && p.then) p.then(ok, no); }))
    .then(buf => { sfxBufs[n] = buf; }).catch(() => {}));
}
function sfxSample(kind) {
  const takes = (SFX_TAKES[kind] || []).filter(n => sfxBufs[n]); if (!takes.length) return false;
  const src = actx.createBufferSource(), g = actx.createGain();
  src.buffer = sfxBufs[takes[Math.floor(Math.random() * takes.length)]];
  if (!SFX_STEADY.has(kind)) src.playbackRate.value = rand(0.93, 1.07);
  g.gain.value = SFX_VOL[kind] || 0.6; src.connect(g); g.connect(sfxBus); src.start(); return true;
}
// enemies have voices: a grunt now and then when hit, a cry when knocked down; one voice at a time so a crowd doesn't babble
const FOE_FEMALE = new Set(['ladette', 'lady', 'ragazza', 'beachf', 'clubf', 'itgirl', 'denise', 'sue', 'scrunchie', 'hoops', 'commuter']);
const FOE_MUTE = new Set(['goose', 'swan', 'gary', 'gaz', 'koala']);
let foeVoiceT = 0;
function foeVoice(t, down) {
  if (!t || t.car || t.fish || FOE_MUTE.has(t.kind) || !actx) return;
  if (actx.currentTime < foeVoiceT || (!down && Math.random() > 0.35)) return;
  const f = FOE_FEMALE.has(t.kind); foeVoiceT = actx.currentTime + (down ? 0.55 : 0.3);
  sfx(down ? (f ? 'cryf' : 'cry') : (f ? 'gruntf' : 'grunt'));
}
