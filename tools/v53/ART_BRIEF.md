# Nightlife 2006: art brief for PixelLab

Game: a pixel-art side-scrolling beat 'em up set in south London, Friday night in 2006. Every sprite is side view,
facing east (right). Characters are made with PixelLab `create_character` (mode "v3", view "side", size 64; bosses
size 80). Enemy groups are designed by look and attitude, never by race; every group mixes faces. Nothing gory.

## Output layout
For every character and animation, save the PixelLab workbench sheet:
`pixelart_workbench argv=["inspect", "character:<id>:east:<anim>", "--scale", "2"]`. The tool result includes a local
image path like `/root/.claude/projects/-home-claude/<...>/tool-results/mcp-PixelLab-blob-....png`. Copy that file
to `/home/claude/mbclegacy/tools/v53/src/<key>/<anim>.png`. (For the select/pose-free NPCs too.)
Images (backgrounds, props) from `create_image_pixflux` + `get_image`: get_image's result also gives a local
`tool-results/...png` path; copy it to `/home/claude/mbclegacy/tools/v53/img/<name>.png`.
Keep `/home/claude/mbclegacy/tools/v53/pixellab_ids.md` up to date with every character id, and write
`/home/claude/mbclegacy/tools/v53/ART_DONE.md` listing each saved file, frame count, and anything re-rolled or
still weak. The network can't download PixelLab URLs directly (403), so always go through inspect/get_image.

## Animations (all `animate_character` mode "v3", directions ["east"])
Standard enemy set (frame_count in brackets; the stored strip has one extra reference frame at the start):
- idle (6): "fighting stance idle, ..." suited to the character
- walk (8): a walk forward suited to the character
- attack (8): their main strike (described per character below)
- hurt (4): "gets punched in the face, head snaps back, staggers"
- knockdown (16): "knocked off his/her feet backwards, lands flat on the back, lies still, then gets back up"
Quality bar: the character must stay side-on facing right, keep the same clothes and colours, and not hold objects
that aren't asked for. If a strike turns the character to face the camera or invents a weapon, delete that animation
(`delete_animation`) and re-roll once with a clearer description ("side-on, facing right, empty hands").

## Characters already created (wait until each is completed with get_character before animating)
- city "City Boy" 5e070ef3-d2f0-4ed8-befc-e72b479e6eea: attack = "sharp backhand slap with his right hand"; extra
  `throw` (8) = "throws a drink from a glass forward, overarm" (the glass is fine here).
- itgirl "It Girl" 56f4af06-c882-47f4-9779-68ad0fdd27d2: attack = "swings her tiny clutch bag in a wide arc";
  extra `kick` (6) = "quick stiletto heel kick forward".
- burb "Burberry Cap" 64287cb6-c2a1-4e25-8996-6a50c5a09dc5: attack = "wild swinging haymaker punch".
- hoops "Hoops" 77856b57-de05-45bf-9009-708a9c99e2e4: attack = "lunges and slaps forward with long nails";
  extra `pull` (6) = "grabs forward and yanks back with both hands, hair pull".
- snood "Snood" e3d6cc0a-72b1-45af-b003-c533638c396d: attack = "fast jab jab then a straight right".
- puffer "Puffer" 5b3d5191-b2ec-419c-8ff4-d0e615e54e8a: idle/walk/attack/hurt/knockdown ALREADY QUEUED by me (check
  get_character; just save the sheets). Extra `dash` (6) = "darts forward low in a quick shoulder barge".
- inspector "Ticket Inspector" (boss, 80) 68cf9fda-bd30-4b27-90eb-ececf58564d4: idle "stands stiffly, tapping his
  clipboard"; walk "officious march forward"; attack = "swings the ticket machine on its strap in a wide arc";
  `attack2` (8) = "raises his clipboard overhead and slaps it down"; `block` (6) = "holds both arms out wide
  blocking the way"; `shout` (6) = "points forward and shouts, leaning in".
- lenny "Lewisham Lenny" (boss, 80) 2fa20501-1fd3-43c8-be55-1c34c9c5382c: attack = "heavy straight right punch";
  `attack2` (8) = "jumps up and kicks forward with both feet"; `pull` (6) = "reaches up and yanks down hard on a
  handle above his head"; `charge` (8) = "charges forward with his shoulder down".

## Characters to create (v3, side view)
- hood "Hood" (64): "young Black street gang member in 2006, black hooded top with hood up, black snood over his
  nose, black tracksuit, black trainers, wiry". attack = "quick hook punch"; standard set.
- grappler "The Grappler" (64): "huge broad thug in a black leather jacket over a black t-shirt, shaved head, thick
  neck, a smooth watch thief's crew member". attack = "lunges forward with both arms wide in a bear hug grab";
  extra `hold` (6) = "squeezing a bear hug, rocking side to side".
- dipper "The Dipper" (64): "slim slippery pickpocket in a fitted grey suit jacket, open shirt, slicked hair,
  cheeky grin". attack = "quick flicking jab"; `dodge` (6) = "sidesteps backwards nimbly"; `steal` (6) =
  "darts a hand forward and snatches something, then pockets it".
- lookout "The Lookout" (64): "lanky lad in a black bomber jacket and flat cap, hands in pockets". attack =
  "lobs something underarm forward"; `whistle` (6) = "puts two fingers in his mouth and whistles loudly".
- jeweller "The Jeweller" (boss, 80): "flash crime boss in a cream suit and open black shirt, several gold chains,
  rows of gold watches up both forearms, rings, slicked back hair". attack = "whips a heavy gold chain forward";
  `glint` (6) = "raises his wrist and flashes his watches proudly"; `grab` (8) = "lunges and grabs forward with both
  hands"; idle "smug stance admiring his watches".
- stag "The Stag" (64): "drunk groom-to-be in a full-body yellow banana costume, face poking out, red cheeks".
  attack = "wild clumsy swinging punch"; `stagger` (6) = "drunken stagger, wobbling".
- groom "Groomsman" (64): "lad on a stag do in a white t-shirt with big black print, jeans, holding nothing". attack =
  "drunken haymaker punch".
- smiler "Smiler" (64, friendly NPC, not an enemy): "kind-faced older homeless man in a worn green parka, woolly
  beanie, grey beard, sleeping bag rolled over his shoulder". Animations: idle (6) "sits up and stretches, friendly
  wave", throw (8) "lobs something underarm forward to a friend". No fight anims. Depict him with dignity.
- commuter "Commuter" (64, fleeing passenger): "woman in a smart office coat with a handbag". run (8) "running away in
  a panic, arms flailing"; idle (6) "standing nervously".
- oldboy "Old Boy" (64, fleeing passenger): "elderly man in a flat cap and tweed coat holding a newspaper". run (8)
  "hurrying away in a panic, shuffling"; idle (6) "reading his newspaper".

## Images (create_image_pixflux; no_background true for props, false for backgrounds; outline "single color black
outline" for props, "lineless" or default for backgrounds; detail "highly detailed" for backgrounds)
Backgrounds (pixel art, night, flat front-on wall views; no characters in them):
- st_hall 320x152: "front view of the inside wall of a small 1990s British railway station ticket hall at night:
  ticket office windows, a departure board, posters, tiled floor line at the bottom, fluorescent light"
- st_front 320x152: "front view of a 1980s brick and glass British suburban railway station entrance at night,
  orange street lights, taxi rank sign"
- st_platform 400x128: "British railway platform at night seen from the side: a long canopy on green posts, benches,
  a yellow safety line, lamps, dark sky"
- tr_wall 320x144: "inside a British commuter train carriage at night, front-on view of one side wall: a row of
  dark windows, blue patterned 3+2 seats with headrests, yellow grab poles, luggage racks above, grey walls"
- tr_door 64x144 (no_background false): "a pair of closed grey sliding train doors with yellow edges and small
  windows, front view, inside a British commuter train"
- tr_end 64x144: "the end wall of a train carriage with a connecting door with a small window, front view"
- tr_toilet 64x144: "a narrow grey train toilet door with a lock indicator, front view, inside a train"
- toilet_guy 64x80 (no_background true): "cartoon man in a shirt and tie sitting on a train toilet with his trousers
  round his ankles, shocked face, holding a newspaper, comedy, nothing rude showing"
- sc_suburb 400x96: "south London suburbs at night seen from a passing train, rows of houses with lit windows, trees,
  streetlights, dark blue sky", should tile left-right
- sc_platform 400x96: "a British station platform at night seen through a train window: platform edge, lamps,
  benches, people waiting"
- cx_hall 320x160: "front view of the concourse back wall of a big London terminus station at night: big departure
  boards, shop fronts, clock, glass roof above"
- cx_barrier 128x64 (no_background true): "a row of grey automatic ticket barrier gates with yellow paddles, front view"
- trafalgar 400x224: "Trafalgar Square in London at night: Nelson's Column lit up, the bronze lions, fountains, the
  National Gallery behind, red double decker bus, wet reflections", cinematic
- alley 320x160: "front view of a grimy back alley behind a London bar at night: brick wall, a green fire exit door
  propped open with light spilling out, a smoking shelter, wheelie bins, kegs, fairy lights"
- bus_deck 320x144: "inside the top deck of a red London double decker night bus, front-on view of one side: a row
  of windows, red and blue patterned seats, yellow grab poles on the seat backs, bell push, dim lights"
- bus_stairs 64x144: "the top of the stairs on a London double decker bus, yellow poles, front view"
- sc_highst 400x96: "a London high street at night seen from the top deck of a bus: kebab shop, fried chicken shop,
  off licence with glowing signs, bus stop", should tile left-right
Props (no_background true): seat_pole 16x64 "a single yellow grab pole on top of a red bus seat back";
window_hammer 32x32 "a small red emergency window hammer"; luggage 48x32 "a black wheeled suitcase";
alarm 32x32 "a red train passenger alarm handle on a yellow plate"; watch 32x32 "a classic steel wristwatch with a
black face"; bottle (reuse game's), kebab 32x32 "a doner kebab in pitta wrapped in paper".
