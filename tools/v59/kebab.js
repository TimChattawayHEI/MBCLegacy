// ================================================================== Version 59: KEBAB SIEGE
// A horde fight on the real fight engine: a fixed screen in the kebab shop at 3am, the 2006 crowd pouring in through
// the door, wave after wave, one life. You're ticket 50; every wave you clear they serve the next number. At 50 your
// kebab's up (full health, a bonus), you get a new ticket and it goes on. Knock someone down by the door and they're
// thrown out. Played once on a run (after The Smoking Area) and as a cabinet in the Harvest Moon.
STAGES.kebab = { n: 'K', era: 2006, title: 'KEBAB SIEGE', sub: '3am. Hold your place in the queue.', bg: 'kebab', fixed: true, door: true,
  ft: 404, fb: 520, raft: [40, 920], len: W, music: 'nightbus', aggro: 3, aa: 0.45, waves: [],
  breakables: [{ type: 'bin', x: 300, y: 492, drop: 'w:alcopop' }, { type: 'keg', x: 880, y: 430, drop: 'chips' }] };
const KB_TIERS = [
  ['burb', 'shellsuit', 'hoops', 'city', 'itgirl', 'stag', 'groom'],
  ['puffer', 'hood', 'snood', 'denim', 'tuba'],
  ['leathers', 'shades', 'noface', 'grappler', 'dipper', 'lookout'],
];
function kebabWave(n) {
  const pool = KB_TIERS[0].concat(n >= 3 ? KB_TIERS[1] : [], n >= 6 ? KB_TIERS[2] : []);
  const size = Math.min(6, 2 + Math.ceil(n / 2)), groups = n < 3 ? 1 : n < 8 ? 2 : 3, out = [];
  for (let g = 0; g < groups; g++) { const grp = []; for (let i = 0; i < size; i++) grp.push([pick(pool), 'L']); out.push(grp); }
  return { groups: out, food: n % 3 === 0 ? 'kebab' : null, kb: n };
}
const KB = { saved: null, lastIdx: 0, ticket: 50, serving: 45, upT: 0, kebabs: 0, endReq: null };
// swap the campaign (if there is one) out, and a one-life run for the shop in
function kebabStart(M) {
  KB.saved = { run, player, snap: typeof stageSnap !== 'undefined' ? stageSnap : null };
  const c = CHAR_BY_ID[M.lad] || CHAR_BY_ID.tim;
  run = { ci: Math.max(0, PLAYABLE.indexOf(c)), c, route: ['kebab'], off: 0, vroute: null, idx: 0, score: 0, lives: 1, diff: 'normal', livesLost: 0, totalTime: 0,
    jackpot: false, nextLife: 1e12, kills: 0, reached: 0, cleared: false, ramsdenCleared: false, flawless: false, entryId: null, secrets: 0, winBonus: 0, mini: true, banked: 0 };
  player = makePlayer(c);
  STAGES.kebab.waves = [kebabWave(1), kebabWave(2)];
  KB.lastIdx = 0; KB.ticket = 50; KB.serving = 45; KB.upT = 0; KB.kebabs = 0; KB.endReq = null;
  startStageNow('kebab');
  S.waitT = 2.2;
  showBanner('KEBAB SIEGE', "Ticket 50. They're on 45. Hold your place.", 2.4);
}
function kebabRestart() { if (!MG) return; const keep = KB.saved; run = keep.run; player = keep.player; kebabStart(MG); }
function kebabTick(dt) {
  if (!ST || ST.bg !== 'kebab' || !S) return;
  while (ST.waves.length <= S.waveIdx + 1) ST.waves.push(kebabWave(ST.waves.length + 1));
  if (KB.upT > 0) KB.upT -= dt;
  if (S.waveIdx > KB.lastIdx) {
    // a wave cleared: a bonus, the next number called, and a breather
    const n = S.waveIdx; KB.lastIdx = n; addScore(400 * n, true); KB.serving++; S.waitT = 2.4; sfx('pickup');
    if (KB.serving >= KB.ticket) {
      KB.kebabs++; KB.upT = 2.6; addScore(5000, true); player.hp = player.maxHp; sfx('life'); sfx('airhorn');
      showBanner('NUMBER ' + KB.ticket + '! KEBAB\u2019S UP', 'Full health. Back in the queue for seconds.', 2.6); popWord(player.x, player.y, 170, 'KEBAB!', true);
      KB.ticket += 6;
    } else showBanner('NUMBER ' + KB.serving + '!', 'Wave ' + (n + 1) + ' coming in.  You\u2019re ' + KB.ticket + '.', 1.8);
  }
}
// thrown out of the door, on the left
function kebabOut(f) {
  f.state = 'dead'; f.t = 0; f.remove = true; f.hp = 0; sfx('thud'); popWord(f.x, f.y, 90, 'OUT YOU GO!', true);
  addScore(300 + f.def.score); run.kills++; noteKO(f); if (f.token) releaseToken(f, 0); ladSay('ko', 0.4);
}
// back to the mini-game screen with the score, and the campaign (if any) back in place
function kebabEnd(reason, forfeit, now) {
  if (!now) { if (!KB.endReq) KB.endReq = [reason, forfeit]; return; }   // finished at the top of the next frame, once the fight's update is done
  const sc = run ? run.score : 0, waves = S ? S.waveIdx : 0, kills = run ? run.kills : 0;
  if (KB.saved) { run = KB.saved.run; player = KB.saved.player; if (typeof stageSnap !== 'undefined') stageSnap = KB.saved.snap; KB.saved = null; }
  foes = []; shots = []; hazards = []; items = []; bubbles = []; banner = null; held.clear(); pointers.clear(); pressed.clear();
  if (!MG) { mode = 'select'; modeT = 0; return; }
  MG.score = sc; MG.forfeit = !!forfeit; MG.s = { waves, kills, kebabs: KB.kebabs };
  mode = 'mini'; modeT = 0; MG.phase = 'play'; miniEnd(reason);
}
function kebabBg() {
  // the whole shop, wall and floor, is one PixelLab picture (Version 59.2: the floor was painted on to match the wall)
  ctx.fillStyle = '#0c0a0a'; ctx.fillRect(0, 0, W, H);
  const img = pubImg('kebab_scene') || pubImg('kebab_wall');
  if (img) { ctx.save(); ctx.imageSmoothingEnabled = false; ctx.drawImage(img, 0, 0, img.width * 2, img.height * 2); ctx.restore(); }
  // the order display over the counter
  const x = 600, y = 8;
  ctx.fillStyle = OUT; ctx.fillRect(x - 92, y - 2, 184, 34); ctx.fillStyle = '#120808'; ctx.fillRect(x - 90, y, 180, 30);
  pxText('NOW SERVING ' + KB.serving, x, y + 15, 14, KB.upT > 0 && Math.floor(time * 8) % 2 ? '#ffe680' : '#ff3a2a');
  return true;
}
function kebabHud() {
  if (!ST || ST.bg !== 'kebab' || mode !== 'play') return;
  pubPanel(W / 2 - 110, 60, 220, 40);
  ctx.font = '800 11px ' + BODY; ctx.textBaseline = 'middle'; ctx.textAlign = 'left'; ctx.fillStyle = '#93a3a1'; ctx.fillText('YOUR TICKET', W / 2 - 96, 80);
  textOut(String(KB.ticket), W / 2 - 4, 80, '20px ' + DISPLAY, '#ffd23f', OUT, 4, 'left');
  ctx.fillStyle = '#93a3a1'; ctx.textAlign = 'right'; ctx.fillText((KB.ticket - KB.serving) + ' TO GO', W / 2 + 96, 80);
}
// the mini-game shell: the intro card and the result screen are the usual ones; the fight is a real stage
MGAME.kebab = {
  init(M) { M.s = {}; },
  update(M) { if (!M.s.started) { M.s.started = true; kebabStart(M); } },
  draw(M) {
    ctx.fillStyle = '#0c0a0a'; ctx.fillRect(0, 0, W, H);
    const img = pubImg('kebab_scene'); if (img) { ctx.save(); ctx.imageSmoothingEnabled = false; ctx.drawImage(img, 0, 0, img.width * 2, img.height * 2); ctx.restore(); }
  },
  hud(M) {
    if (M.phase !== 'result' || !M.s) return;
  },
};
