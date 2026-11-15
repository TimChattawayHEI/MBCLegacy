// ================================================================== Version 85: the bosses talk
// Each boss intro card has a strip of five cards, web/bg/bosscard/<id>_talk.png: the painted card (mouth shut), then the
// mouth open (a), round (o), teeth (e) and lip-bite (f). PixelLab's mouth tool drew the mouths on a 64px crop of the head;
// only the mouth area was pasted back onto the painted card (tools/v85/bossmouths.py), so the card is otherwise untouched.
// Once the card has slammed in, the mouth follows the letters of the boss's line (the same timing as the lads' faces)
// and the boss lets out their own sound, web/sfx/taunt_<id>.wav (PixelLab sound effects: a cackle, a bellow, a fish
// roar...), in place of the generic boss roar.
const BOSS_TALK = ['alan', 'bros', 'carab', 'denise', 'duo', 'farbank', 'gary', 'gaz', 'inspector', 'jeff', 'jeweller', 'lady',
  'lenny', 'mafioso', 'mc', 'mick', 'nozzer', 'parkie'];
const TAUNT_VOL = /*TAUNT_VOL*/{}/*END*/;   // levelled so each sits with the other voices, a little over the music
setTimeout(() => BOSS_TALK.forEach(k => { bgImg('bosscard/' + k + '_talk'); ASSET_BG.push('bosscard/' + k + '_talk'); }), 0);
const taunt = { bufs: {}, loading: false };
function tauntLoad() {
  if (taunt.loading || !actx || (typeof sfxClassic !== 'undefined' && sfxClassic)) return; taunt.loading = true;
  BOSS_TALK.forEach(k => fetch('sfx/taunt_' + k + '.wav').then(r => r.ok ? r.arrayBuffer() : Promise.reject(r.status))
    .then(b => new Promise((ok, no) => { const p = actx.decodeAudioData(b, ok, no); if (p && p.then) p.then(ok, no); }))
    .then(buf => { taunt.bufs[k] = buf; }).catch(() => {}));
}
// load once the sound is on (checked each second, so the start-up code needn't change)
const tauntWait = setInterval(() => { if (actx) { tauntLoad(); clearInterval(tauntWait); } }, 1000);
const cardTalkId = name => { const k = BOSS_ART[name]; return k && BOSS_TALK.includes(k) ? k : null; };
// the card's picture at the current mouth (null: draw the plain card)
function cardTalkFrame(c, art) {
  const k = cardTalkId(c.name); if (!k) return null;
  const strip = bgImg('bosscard/' + k + '_talk'); if (!strip || strip.width !== art.width * 5) return null;
  const f = c.slammed ? talkFrame(c.line || '', c.t - 0.45) : 0;
  return { strip, sx: f * art.width };
}
// true when the boss on the card about to show (or showing) has its own sound
function cardHasTaunt() { return !!(S && S.card && cardTalkId(S.card.name) && taunt.bufs[cardTalkId(S.card.name)]); }
function tauntPlay(c) {
  const k = cardTalkId(c.name), b = k && taunt.bufs[k];
  if (!b || !actx || !settings.sound) return false;
  const src = actx.createBufferSource(), g = actx.createGain();
  src.buffer = b; g.gain.value = TAUNT_VOL[k] || 0.28; src.connect(g); g.connect(sfxBus); src.start(); return true;
}
// the generic roar, unless the card coming up has the boss's own sound (the card is set just after the boss spawns)
function bossRoar() { setTimeout0(() => { if (!cardHasTaunt()) sfx('roar'); }, 0.05); }
