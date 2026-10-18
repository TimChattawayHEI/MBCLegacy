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

## Weakest items to revisit
- Hurt anims that lean or step forward instead of recoiling: burb, snood, groom, lenny, jeweller, inspector. Puffer and lookout barely react.
- lenny attack2 (no jump) and lenny pull (doesn't reach overhead).
- hoops idle (drifts) and hoops walk (barely moves).
- lookout attack (no lob), dipper attack and steal, city attack, stag stagger.
- Nothing in the brief is missing. (The bottle prop was not generated: the brief says to reuse the game's.)
