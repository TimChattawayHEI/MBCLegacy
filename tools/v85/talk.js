// Talking portraits (Version 85): each portrait has a strip of five faces, web/bg/portraits/<id>_talk.png: the original
// (mouth shut), then open (a), round (o), teeth (e, and most consonants) and lip-bite (f). PixelLab drew the mouths;
// only the mouth area was pasted onto the original portrait (tools/v85/mouths.py), so the face stays the hand-made one.
// The face follows the letters of the line being said, about 13 letters a second, and shuts at the end.
setTimeout(() => PORTRAIT_IDS.forEach(id => { ASSET_BG.push('portraits/' + id + '_talk'); bgImg('portraits/' + id + '_talk'); }), 0);   // PORTRAIT_IDS is declared further down
const TALK_RATE = 0.075;
function talkFrame(text, t) {
  if (!text || t == null || t < 0) return 0;
  const i = Math.floor(t / TALK_RATE); if (i >= text.length) return 0;
  const c = text[i].toLowerCase();
  if (c === 'a' || c === 'h') return 1;
  if ('ouw'.includes(c)) return 2;
  if ('fv'.includes(c)) return 4;
  if ('mbp .,!?\'-'.includes(c)) return 0;
  return 3;
}
// the speaker of a bubble, if they have a portrait
function talkId(e) {
  if (!e) return null;
  if (e.def && PORTRAIT_IDS.includes(e.def.id)) return e.def.id;
  return PORTRAIT_IDS.includes(e.kind) ? e.kind : null;
}
// a small talking face tucked beside the speech bubble (drawn inside drawBubble, so it pops and fades with it)
function talkBubbleFace(b, bx, by, bw, bh, bs) {
  const id = talkId(b.e); if (!id || !portraitImg(id)) return;
  const s = Math.round(36 * bs / 2) * 2, left = bx - s - 6 >= 4;
  const x = left ? bx - s - 6 : Math.min(W - s - 4, bx + bw + 6), y = by + bh - s;
  drawPortrait(id, Math.round(x), Math.round(y), s, (SPEAKERS[id] || SPEAKERS.sys || {}).color, talkFrame(b.text, b.t - 0.1));
}
