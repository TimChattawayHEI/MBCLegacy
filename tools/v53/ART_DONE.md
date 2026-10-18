# Nightlife 2006: art delivery (PixelLab)

All work from ART_BRIEF.md is saved. Character ids are in `pixellab_ids.md`.
PixelLab generations used: about 223 for this pass (balance went from 860 used to 1081 used; that figure may include the 5 Puffer jobs that were already queued).

## Format notes (read before slicing)
- `src/<key>/<anim>.png` is the `pixelart_workbench inspect ... --scale 2` sheet: frames are laid out in a grid at 2x, each with a "frame Fn 2x" label, on a dark slate background (not transparent). Frame 1 is the reference pose (the stored strip has one extra frame), so an anim requested at N frames has N+1 cells.
- Native frame canvas: 84-92 px for the 64 px characters, 108 px (Inspector, Lenny) and 112 px (Jeweller) for the 80 px bosses.
- If clean transparent strips are needed, the PixelLab spritesheet endpoint per character (`/mcp/characters/<id>/spritesheet`) has them, but it can't be downloaded from this shell. Re-export from a machine that can reach PixelLab.
- `img/*.png` are the raw get_image outputs at native size. Backgrounds are opaque, props are transparent.

## Prompt fixes found along the way (useful for any re-rolls)
- Knockdown: "knocked off his feet backwards..." made v3 fall FORWARD onto the front. This prompt fixed it: "hit hard, flies backwards to the left, falls onto his back face up looking at the sky, lies still on his back, then sits up and stands back up, side-on facing right". The brief's prompt was used for city/puffer/grappler at first, then all three were re-rolled with this one.
- Hurt: "gets punched in the face" adds a white fist/swoosh effect. I switched to "stays in side profile facing right, recoils/head jerks backwards..., no effects". Even so, many hurt anims lean FORWARD instead of snapping back (see weak list). This is the weakest category overall.
- Idle: "fighting stance idle" often turns the character to face the camera. Starting with "stays in side profile facing right" fixed it.
- The word "stag" in a character description gives the character a tail.

## Characters and animations (frames requested / cells stored)
Standard set: idle 6/7, walk 8/9, attack 8/9, hurt 4/5, knockdown 16/17.

| key | saved anims | notes |
|---|---|---|
| city | idle, walk, attack, hurt, knockdown, throw (8/9) | attack is weak: arms spread, the slap reads soft. hurt re-rolled (1st had a punch-swoosh effect), 2nd is subtle. knockdown re-rolled (1st fell on his front), 2nd is good. throw re-rolled (1st turned to face left); in the 2nd he sips the drink before throwing and the glass vanishes at release. |
| itgirl | idle, walk, attack, hurt, knockdown, kick (6/7) | idle re-rolled (1st faced camera). attack ok (green clutch). hurt ok-ish (one frame faces camera). kick ok-ish (skirt picks up a green tint). knockdown good. |
| burb | idle, walk, attack, hurt, knockdown | idle re-rolled (1st faced camera flexing). attack reads more jab than haymaker. hurt re-rolled and still weak: leans forward. knockdown good. |
| hoops | idle, walk, attack, hurt, knockdown, pull (6/7) | idle weak: drifts into a forward step, so it will pop when looped. walk weak: very little leg movement. pull re-rolled (1st pulled her own ponytail), 2nd ok-ish. knockdown good. |
| snood | idle, walk, attack, hurt, knockdown | attack re-rolled (1st spun to face camera); 2nd ok-ish: 3/4 stance, a single straight punch rather than jab-jab-cross. hurt weak (forward lean). knockdown good. Looks very close to `hood` (both are hooded black tracksuits). |
| puffer | idle, walk, attack, hurt, knockdown, dash (6/7) | Base sprite has stray debris pixels around the feet in early frames of most anims. hurt weak (barely reacts). knockdown re-rolled (1st fell on front), 2nd is good. dash re-rolled (1st was just a punch), 2nd ok (low lunge). |
| inspector (80) | idle, walk, attack, attack2, block, shout (6/7 each), hurt, knockdown | idle ok (a clipboard appears). attack re-rolled (1st faced camera with no machine); 2nd ok-ish: swings a small device on a strap, hard to read. attack2 good. block re-rolled: both takes turn 3/4 to camera with arms wide, which looks forced by the pose; usable. shout re-rolled (1st invented a hammer), 2nd ok. hurt weak (turns into fists-up). knockdown good. |
| lenny (80) | idle, walk, attack, attack2, pull (6/7), charge, hurt, knockdown | attack ok-ish (last frame turns away). attack2 weak: a grounded one-leg front kick, not a two-footed jump kick. pull re-rolled (1st scratched his head); 2nd still weak: fist only reaches head height. charge re-rolled (1st was a walk); 2nd ok, leaning sprint. hurt weak (hunches forward). knockdown good. |
| hood | idle, walk, attack, hurt, knockdown | attack reads more jab than hook. hurt ok-ish. knockdown good. I dropped "Black" from the brief's description, because the brief's own rule says groups are designed "by look and attitude, never by race". The sprite came out with a mid-tone face mostly hidden by the snood. |
| grappler | idle, walk, attack, hurt, knockdown, hold (6/7) | attack re-rolled (1st lost the t-shirt); 2nd ok, turns 3/4 mid-grab. hurt re-rolled (1st had a big white flash); 2nd ok-ish, hunches forward a little. knockdown re-rolled (1st fell on front); 2nd ok: half-reclined slump with small dizzy stars, then gets up. hold ok-ish. |
| dipper | idle, walk, attack, hurt, knockdown, dodge (6/7), steal (6/7) | idle ok, walk ok. attack weak (tiny jab). hurt re-rolled (1st faced camera); 2nd ok. knockdown good. dodge ok (quick step back). steal weak (small hand motion, turns 3/4). |
| lookout | idle, walk, attack, hurt, knockdown, whistle (6/7) | Base sprite wears a baseball cap, not a flat cap. attack weak: small forward push, no visible underarm lob. hurt weak (tiny head dip). whistle re-rolled (1st did nothing), 2nd ok. knockdown good. |
| jeweller (80) | idle, walk, attack, hurt, knockdown, glint (6/7), grab (8/9) | idle ok (checks his watch). attack ok-ish: the chain swirls behind him like a lasso and only lashes forward at the end. glint ok-ish (no sparkle). grab good. hurt weak (lunges forward). knockdown good. |
| stag | idle, walk, attack, hurt, knockdown, stagger (6/7) | Base sprite reads as a half-peeled banana with legs. attack re-rolled (1st lost the costume); 2nd ok. hurt ok-ish. knockdown ok-ish (lands sitting). stagger weak (mild wobble). |
| groom | idle, walk, attack, hurt, knockdown | Uses Groomsman v3 49977129. Two earlier creations (98618ac5, 15a94c10) drew a tail and were abandoned. attack ok-ish (stiff straight punch). hurt weak (forward run pose). knockdown good. |
| smiler | idle (6/7), throw (8/9) | idle: a friendly wave while standing, no sit-up or stretch. throw: gentle underarm toss with nothing visible in the hand. Dignified look: green parka, beanie, grey beard, bedroll. |
| commuter | idle (6/7), run (8/9) | The base sprite came out all greyscale. In run the handbag is mostly lost and the arms don't really flail. |
| oldboy | idle (6/7), run (8/9) | Good: flat cap, tweed coat, newspaper. |


## Images (img/)
| file | size | notes |
|---|---|---|
| st_hall | 320x152 | ok, garbled sign text |
| st_front | 320x152 | ok |
| st_platform | 400x128 | good |
| tr_wall | 320x144 | ok: windows and blue seats, but no yellow poles or luggage racks |
| tr_door | 64x144 | good |
| tr_end | 64x144 | ok, dark |
| tr_toilet | 64x144 | good (red seat edges at the sides) |
| toilet_guy | 64x80 | ok: shirt and tie, newspaper, nothing rude; the shocked face is hard to read |
| sc_suburb | 400x96 | re-rolled (1st was a top-down sprawl); 2nd is a good flat terrace row; edges not guaranteed seamless |
| sc_platform | 400x96 | good (waiting people, as asked) |
| cx_hall | 320x160 | good |
| cx_barrier | 128x64 | ok, transparent |
| trafalgar | 400x224 | ok, cinematic; loose geography |
| alley | 320x160 | ok-ish: the door is closed rather than propped open; no wheelie bins |
| bus_deck | 320x144 | re-rolled (1st looked down the aisle); 2nd is a good side-on wall |
| bus_stairs | 64x144 | good |
| sc_highst | 400x96 | good: tiny figures in the shop windows; edges not guaranteed seamless |
| seat_pole | 16x64 | good |
| window_hammer | 32x32 | ok (reads a bit like a pick) |
| luggage | 48x32 | ok |
| alarm | 32x32 | ok |
| watch | 32x32 | ok-ish: dark, the steel barely reads |
| kebab | 32x32 | ok (could pass for a hot dog) |
| bottle | | not generated: the brief says to reuse the game's |

## Weakest items to revisit (first pass; most fixed in the re-roll pass below)
- Hurt anims that lean or step forward instead of recoiling: burb, snood, groom, lenny, jeweller, inspector. Puffer and lookout barely react.
- lenny attack2 (no jump) and lenny pull (doesn't reach overhead).
- hoops idle (drifts) and hoops walk (barely moves).
- lookout attack (no lob), dipper attack and steal, city attack, stag stagger.
- Nothing in the brief is missing. (The bottle prop was not generated: the brief says to reuse the game's.)

## Re-roll pass (requested by Tim: no weak animations kept)
About 52 PixelLab generations for this pass, from a ~150 budget. The account balance moved more than that (1081 to 1255 used) because another session was running jobs on the same account at the same time. Every replaced sheet keeps its predecessor as `<anim>_v1.png` beside it. PixelLab animation names are `<anim>_r2`, `_r3` and `_r4` (take 1 is the original).

### How the hurts were fixed (read this if you re-roll more)
- The v3 engine can't do a sharp hurt. It eases out of the reference pose, so cells 2-3 always look almost identical to the standing frame. All ten v3 hurt re-takes (r2) failed for this reason.
- The **pixminimax** engine (`mode: "pixminimax"`, still 4 frames, so 5 cells) produces a real backward snap in cells 2-3. However, it always adds speed lines or swoosh arcs, and sometimes the attacker's fist, whatever the prompt says.
- Wording that worked: "stays in side profile facing right; from the very first frame he is already thrown back by a blow: head tipped back to the left, torso bent far backward, arms trailing; next frame still bent back; then slowly straightens. Feet planted. Single character only, nothing else drawn, no fists, no motion lines". It stops the fist being drawn into cell 2, but speed lines still appear.
- **For every pixminimax hurt I kept, I erased the effect pixels with `pixelart_workbench edit`.** These were region- or colour-masked erases, clear of the body, and I checked each one at 2x. The saved PNGs are therefore cleaned versions; the clips stored on PixelLab under `hurt_rN` still have the lines.

### Item by item
| item | takes | kept | what the kept one does / anything still off |
|---|---|---|---|
| burb hurt | r2 v3, r3 pmx, r4 pmx | r4 (cleaned) | Cells 2-3: cap and chest thrown back, arms flung; cells 4-5 recover. r3 had a disembodied fist in cell 2. |
| snood hurt | r2 v3, r3 pmx | r3 (cleaned) | Cells 2-4 bent far back. His face turns a touch toward 3/4 in cell 3. |
| groom hurt | r2 v3, r3 pmx | r3 (cleaned) | Cells 2-3 head and chest thrown far back, then he straightens. |
| lenny hurt | r2 v3, r3 pmx | r3 (cleaned) | Cells 2-4 big backward lean with fists at his waist; cell 5 eases up. |
| jeweller hurt | r2 v3, r3 pmx, r4 pmx | r4 (cleaned) | Cells 2-5 head snapped back, shoulders hunched, arms dangling. He stays dazed rather than fully recovering. r3 had an impact blob at his face. |
| inspector hurt | r2 v3, r3 pmx | r3 (cleaned) | Cells 2-4 cap and head thrown back, chest arched; cell 5 recovering. |
| puffer hurt | r2 v3, r3 pmx, r4 pmx | r4 (cleaned), best of 4 | Cell 2 is a clear backward recoil. In cell 3 his head is still back, but his torso starts to hunch forward. The cleanup slightly trimmed the front edge of his snood in cell 2. The base sprite's floating debris pixels around the feet remain (they're in his reference pose). Still not perfect. |
| lookout hurt | r2 v3, r3 pmx, r4 pmx | r4 (cleaned) | Cells 2-4 thrown back, cell 5 recovering. r3 had a yellow fist or projectile in cell 2. |
| city hurt | r2 v3, r3 pmx, r4 pmx | r4 (cleaned) | Cells 2-5 head and chest thrown far back; a pink swoosh arc was erased. r3 drew an attacker's arm in cell 2. |
| itgirl hurt | r2 pmx | r2 (cleaned) | Cells 2-4 arched far back. Her skirt picks up a checked pattern in the hurt frames. |
| lenny attack2 | r2 v3 | r2 | 8/9: crouch, leaps, horizontal in the air with both boots thrust right, lands. Frames 3-4 turn slightly toward 3/4. |
| lenny pull | r2 v3, r3 pmx, r4 pmx | r4 | A red alarm handle appears overhead. His fist goes well above his head, grabs it and hauls the cord down to his chest. **8 frames = 9 cells (was 6/7)**, because pixminimax only does multiples of 4. |
| inspector attack | r2 v3, r3 pmx, r4 v3 | r4 | 8/9: side-on lunge with his right arm thrust fully out at head height, a hard shove or slap that reads clearly. No ticket book in his hand (every take with a book either turned to the camera or smeared). |
| inspector block | r3 pmx (one take) | r3 | Side-on: steps in and thrusts both arms straight forward, palms out like a traffic stop, then holds. **8 frames = 9 cells (was 6/7).** |
| hoops idle | r2 v3 | r2 | 6/7: stays planted, settles into a fists-up guard and bobs, with no drift. As with every v3 idle, cell 1 is the relaxed reference pose. |
| hoops walk | r2 v3 | r2 | 8/9: clear alternating strides, arms swinging. |
| lookout attack | r2 v3 | r2 | 8/9: a green bottle appears in his hand. He swings back, lobs it forward underarm, and his hand is empty after release. |
| dipper attack | r2 v3 | r2 | 8/9: guard up, then a full-extension jab, then pulls back. |
| dipper steal | r2 v3, r3 v3 | r3 | 6/7: his hand shoots out, clamps on a visible black wallet, pulls it in and stuffs it into his jacket. Slight 3/4 during the tuck. |
| city attack | r2 v3 | r2 | 8/9: wind-up, then steps in with a long open-hand slap or shove held at face height. |
| stag stagger | r2 v3, r3 v3 | r3 | 6/7: lurches with arms flailing, pitches far forward on one leg nearly falling, then rights himself. He tips forward more than backward. |
| commuter (new sprite) | create v2; idle r1 v3, r2 v3; run r1 v3, r2 pmx | idle r2, run r2 | New colour character **a303c518-acb5-40cd-bef8-bb7c4a1aea9c**: beige trench coat, dark hair, brown handbag (pixellab_ids.md updated). The new idle (6/7) stays side-on, hugging her bag with a small nervous fidget; its take 1 turned to face the camera. The run (8/9) is a panicked sprint with both arms thrown up above her head and the coat flying. `idle_v1.png`/`run_v1.png` are the old greyscale sprite. |
| lookout cap | | | Left as a baseball cap, as instructed. |

### Still not right
- puffer hurt: cell 3 starts hunching forward (best of 4 takes).
- Frame-count changes the game must handle: `lenny/pull.png` and `inspector/block.png` now have 9 cells instead of 7.

## Backgrounds pass (no more hard cuts, gatelines that make sense)
Tim: "transitions just cut to a new background image", the ticket hall repeated, and the barriers sat next to the track.
- Every stage that scrolls through scenery is now one row of pieces joined by inpainted joins (`tools/v53/seams.py`):
  - Orpington: st_front | st_j1 | st_hall | st_jh | st_hall2 | st_j2 | st_platform (nothing repeats; 3680 px of 3300).
  - Charing Cross: cx_platform | cx_j1 | cx_hall | cx_j2 | cx_shops | cx_j3 | cx_exit (off the train, through the gates, across the concourse, out to the Strand; the stage is now 3400 long so the way out shows).
  - Smoking area: alley | al_j1 | alley2 | al_j2 | alley3 | al_j3 | alley.
- How a join is made: a 256 px canvas with A's last 48 px and B's first 48 px, the middle masked; the canvas goes up on the throwaway `art-staging` branch so PixelLab can read it from raw.githubusercontent.com (the workspace can't upload to PixelLab), then mcp__PixelLab__inpaint_image fills the middle. bg_process.py pastes A's and B's exact edge pixels back, so the game overlaps them with no seam.
- New pieces (pixflux, 1 generation each): cx_platform (re-rolled once: the first was a flat high-speed train with platform 29/33), cx_shops and alley2/alley3 (img2img from cx_hall/alley so the style matches), cx_exit, st_hall2 (ticket machines, footbridge stairs, "TRAINS TO LONDON CHARING CROSS"). Garbled signs repainted: PLAT 4, NEWS, TOILETS, SANDWICHES, FIRE EXIT, the departures sign; the ticket machine headers blanked.
- Re-rolls: cx_j1 (the first came out in perspective with a Tube train), st_j2 (twice: PixelLab kept painting a darker sky than the platform's, so the part past the doorway is the platform's own first columns mirrored, `seams.MIRROR`). st_j3 and the first st_j2 were dropped when st_hall2 went in.
- Bottoms cropped (`bg_process.CROP`): st_hall, st_platform, cx_*, alley* all ended in a dark band that read as a platform edge or kerb behind the fight. Tops padded or cut so a stage's pieces share a height.
- Gatelines: `gate.png` (pixflux, a side-on gate cabinet; two earlier takes were too tall or three-quarter on) -> gate_open / gate_shut (green or red light). Five cabinets in a column across the walkway, depth-sorted with the fighters: Orpington at the doorway from the ticket hall to the platform (the Inspector's fight is right there), Charing Cross where the platforms end. Red while a fight is on screen, green when clear. On the Orpington platform the yellow line, the edge and the track are drawn in front of the walkway, nearest the camera. cx_barrier.png is no longer used.
- Generations: about 140 (13 inpaints at 10 each, 10 pixflux).
