# Things to Do

## New (30 October)

### Combat
- [x] Super recharge is too slow. Either speed up how fast the bar refills, or add pickups that top it up
  - Done (V65): fills about three times as fast per hit, and knockouts and food top it up too
- [x] Back kick is pointless. Drop it and put the special on that button
  - Done (V65): U, V and the touch button where BACK was fire the special. With a weapon and no special ready, it throws the weapon
- [x] Seb's headbutt (mini special): redo the animation as a spring-loaded headbutt. He arches his back first, then snaps forward into it
  - Done (V65): leans back on the coil, then snaps through with a quicker, longer lunge
- [x] Check every other lad's special animations for their supers and fix any that look off
  - Done (V65): all nine fired in game. Fixed Sam's lights out, where foes' speech bubbles floated in the dark. Worth a look on a real phone too

### Art
- [x] Rebuild the health bars in Meshy
  - Done (V65): gunmetal plate, boss bar frame and glass-tube fills; the other HUD panels match
- [x] Pearcy's golf mini-game (The Long Drive): fix what's broken, and give it Meshy graphics
  - Done (V65): the lake at golden hour painted in Meshy. Played through on desktop and phone with no errors; the one thing found broken was the swing meter's words sitting on the yard labels. Tim: if something else was broken for you, say what and I'll fix it

### Bugs
- [x] Hidden characters (Thet, Ash) can be selected before they're unlocked, and the game bugs out. Locked lads must not be pickable anywhere
  - Done (V65): the online lobby, a guest who hadn't picked, the pub and a carried-on run could all hand you a locked lad. One check now covers every route

### Also done 30 October (Tim's chat requests)
- [x] Faint joins on Charing Cross and the Smoking Area smoothed
- [x] Fishery pegs, Jo's rota, Nozzer's chair and the smoker repainted in Meshy
- [x] Every place-to-place join in the stage pictures blended (Arrivals apron to hall, and the rest)
- [x] Boss intro cards with Meshy portraits for every boss
- [x] Seb redrawn from Tim's photos: buzz cut, ginger stubble, no sunglasses, no camo (grey-olive shirt over a white tee, jeans, boots, watch)
  - Done (V68): every move, his select pose, his portrait (also his group chat face) and his title pick card. Same frame counts, so his timings haven't changed. `tools/v68_build.py` patches the page directly like V66 and V67

### Updates
- [x] In-app updates: the app downloads only the changed game files from GitHub and restarts itself, no APK download. A full APK only when the Android side changes
  - Done (V66): the card says UPDATE READY and Restart switches it in (or it goes in next time the app opens). Everyone needs this one APK the old way first; the first real in-app update will be the build after it. Not yet tried on a real phone
- [ ] Online lobby: warn when the two phones are on different versions (they'd drift out of sync), with an update button

### Tidy-ups (30 October evening)
- [x] Select screen: the lad's name (and the stage and difficulty headings) off the comic bursts; the name in the lad's colour
  - Done (V67)
- [x] Select screen: lad tiles, chapter tabs and stage list in the same type as the footer buttons; no cut-off "TAP A LAD..." hint on phones
  - Done (V67)
- [x] The Long Drive: yard markers upgraded
  - Done (V67): the fishery's Meshy peg boards standing in the lake with the yards on them (every 100 in red)

### Joins, blockers and fire (30 October, late)
- [x] Soundz FM roof: the parapet broke into a corner where the Master Control fight is. Now one straight wall and railing; the corridor ends at the ROOF door set in the wall
  - Done (V69), Meshy repaints
- [x] Elba Arrivals: the hard cut from outside to the hall. Now the terminal front ends in a corner, the hall is seen cut away, the full ARRIVI/ARRIVALS sign, and the floor meets the apron along a slanted kerb
  - Done (V69)
- [x] Orpington: the station front and the door out to the platform repainted so nothing cuts or sticks out over the floor; a ghost of the bench removed
  - Done (V69)
- [x] Charing Cross: the floor started over the tracks, so you could stand on the train or the buffers. The floor now starts at the platform edge, the columns, bins and signs block you, and the lines down the floor are smoothed
  - Done (V69)
- [x] Things painted on the floor block the way (the dive bar's end wall by the back door, the pergola post, the stools; the Soundz decks, sofa, door, air con box and mast; the plane and tug; ticket machines, seats, vending machine, open doors and benches; lamp posts, phone box and the underpass pillar; Charing Cross columns; the sandcastle)
  - Done (V69): FLOOR_BLOCK in tools/v69/v69.js, for players, foes and allies. If one feels wrong in play, it's a line in that list
- [x] The train: the carriage end looked stuck on and after the first carriage cut a window in half. Each carriage now draws its own walls and the end wall matches the carriage
  - Done (V69)
- [x] The N47: the grab poles were stubby poles on red blocks. Now floor to ceiling yellow poles with a red STOP button
  - Done (V69)
- [x] Carp Diem car park: two overlapping silver cars and a see-through red car. Now one estate, the smoker, then the red hatchback by the gate
  - Done (V69)
- [x] Faint joins on Ramsden's road and in the night fishery's sky smoothed
  - Done (V69)
- [x] The fire on the burning Espace, Ramsden's wrecks and bins, and the drive's crash: real animated fire (flames lick up and break off, sparks, glow) instead of rows of the small flame sprite; the Espace's smoke no longer a dark ball
  - Done (V69)
- [ ] Have a play through every stage on a phone and say if any block stops you somewhere it shouldn't, or any join still shows

### More Meshy (30 October, night)
- [x] The train and the N47 painted in Meshy: proper ceilings with strip lights and floors, no more black above the carriage
  - Done (V70)
- [x] Foreground layer: station columns, lamps, railings and a trolley slide past in front of the fighters (Charing Cross, Orpington, the Frequency, the alley); they go see-through when a lad is behind one
  - Done (V70), `FG_SET` in tools/v70/v70.js. More stages can be added there
- [x] Parallax skies: Elba airport, the beach and the dive bar's track have their sky as a slower layer
  - Done (V70), "parasky" in stages.json
- [x] Pickups and weapons repainted as one matching sheet (the cone, helmet and net kept, Meshy made them worse); the bus pole weapon matches the new grab poles
  - Done (V70)
- [x] Seb's artillery cut-in: the mortar pit painted in Meshy (flare, sandbags, forest)
- [x] Stage titles, GAME OVER and the win banner on a Meshy caption plate; game over and victory pictures behind them
- [x] Darts on a Meshy pub wall with the cabinet open round the board; the kiss game in the Meshy Soundz flat
- [x] App icon (a fist with a sovereign ring over London at sunset) and a splash screen while it loads
  - Done (V70). Shows on the next APK, not an in-app update
- [ ] Tim: say if any foreground piece gets in the way in a fight; it's one line per piece to move or drop

### Story (30 October, late night)
- [x] Comic pages at the big moments: Seb's loft and the jump to 1999, midnight on the millennium, landing on Elba, the Espace, Orpington station 2006, home to the present, arriving at Denise's, the fireball, and Big Gary at the end
  - Done (V71): painted in Meshy (tools/v71/comics.py); captions and speech are in COMIC_PAGES in tools/v71/v71.js, easy to change
- [x] An ending for every lad: finish the campaign as him to collect his, and they go up on a WHERE ARE THEY NOW wall at the Harvest Moon (past the trophy cabinet), where you can read them again
  - Done (V71)
- [x] The damage report after the endings: knockouts, food (and kebabs), specials, times Sam fell asleep, times on the floor, weapons thrown, bosses, rounds bought, lives lost, time, with Marc on the numbers
  - Done (V71)
- [ ] Tim: write the ending line for each lad (Tim, Seb, Pearcy, Byron, Kelly, Marc, Sam, Ash, Thet). Until then each shows "To be continued...". They go in ENDINGS in tools/v71/v71.js, or send them in chat
- [ ] Check the comic pages and endings in an online game (built for one phone; online they're shown on each phone on its own)

## New (31 October): Orpington 2001

A group night out before the 2006 chapter: meet at the Pizza Express bus stop, over the mini roundabout, past Ram Ba Ba, into the Blacksmiths, back to Ram Ba Ba for the coach, then Atlantis in Croydon. Full design in `tools/v72/ORPINGTON_2001.md`; Tim's photos (cleaned crops) in `tools/v72/ref/`.

Real street order, left to right (the mirror shop is past the Blacksmiths, not before it): Pizza Express corner (bus stop) | mini roundabout | Ram Ba Ba (corner of Church Hill, then the Young's frontage) | car park | Blacksmiths' single storey wing | Ye Olde Blacksmith | the mirror and lamp shop with PRIVATE PROPERTY! NO PARKING on its gable.

### Story and chapter
- [x] Decide where it sits in the campaign: between 1999 and Elba 2002 (it's 2001), with the time travel arc landing the lads there
  - Done (V72): between 1999 and Elba in ROUTE, its own chapter tab (ORPINGTON 2001) on the select screen and the route picker. Stages renumbered (ranks are kept by name, so nothing is lost)
- [ ] Group chat opener in 2001 SMS speak on brick phones ("c u @ pizza xpress 8, dnt b l8"); a present-day chat flashback (the Blacksmiths is now Aksular, Ram Ba Ba became Fiesta Mexicana)
- [ ] Comic pages: Kelly knocked back at the Ram Ba Ba door; the coach to Croydon (replaces a coach fight, since the N47 is already a bus fight); 2am, everyone back on the coach and Kelly asleep on it
- [ ] Tim: confirm the night's details (what time the coach left, any other Blacksmiths or Atlantis stories worth a moment)

### Stages and mechanics (not just left to right)
- [x] 1. Pizza Express bus stop: lads arrive one at a time while you hold the stop against a rival crew
  - First pass (V72): THE HIGH STREET opens with a fight at the bus stop (HOLD THE BUS STOP). The lads arriving one at a time is still to do
- [x] 2. The mini roundabout: a short Frogger-style crossing (zebra, Belisha beacons, Corsas, the red estate, a bus)
  - First pass (V72): cars come round the roundabout along the road (the moped hazard with a horn first); keep to the pavement. A proper Frogger crossing with its own screen is still to do
- [x] 3. Ram Ba Ba, first pass: no fight; a chalkboard by the shutter says ATLANTIS COACH 10.30 and starts the night's clock on screen
  - Done (V72): ATLANTIS COACH 10.30 pops up passing Ram Ba Ba. The on-screen clock is still to do
- [x] 4. The Blacksmiths, getting served: stealth in the L-shaped bar. The bar is in the corner so whoever's serving sees down both arms; keep Byron (looks like a kid) out of Sue's eyeline behind fruit machines and seating while the oldest-looking lad goes up
  - Done (V72): Sue pours with her back turned, turns round with a "!" and TURNING..., then WATCHING. Move in her sight (away from the fruit machines) and she clocks you and sends you back to the door; three strikes and it kicks off anyway; reach the bar for SERVED! and 2,000
- [x] 5. The Blacksmiths, it kicks off: Alan and Jeff start it round the pool table at the top of the L. Throwable horseshoes, pool cues and balls, wagon wheels off the walls rolling as hazards, the fruit machine gives a hold/nudge bonus when hit. Boss: Mick ringing the bell, Sue's "OI!" from behind the bar as a stun
  - First pass (V72): Alan (with regulars), Jeff as a mini-boss with his own card, then Mick: haymaker, belly barge down your lane, and LAST ORDERS (the bell brings two regulars in) when he's angry. Sue shouts "OI!" from behind the bar every few seconds: ears ringing for anyone on the floor (jump it). A cue and the fruit machine are there; horseshoes and rolling wagon wheels still to do
- [ ] 6. The run back: auto-runner up the High Street to make the coach (bollards, bins, people); miss it and restart the run
- [x] 7. Ram Ba Ba door: blag mini-game with a nerve meter, tapping to keep Kelly's Mass Head from inflating. Scripted to fail (it's canon): Kelly is refused and sits on the coach till 2am. Playing as Kelly: Snake on his brick phone, with a board
  - First pass (V72): at the Atlantis door, the bouncers let the lads in and turn Kelly away; playing as Kelly, he sits the night out on the coach and the stage ends. The nerve-meter blag and Kelly's Snake are still to do
- [x] 8. Atlantis: rhythm brawler, hits land harder on the 2-step beat, strobes reveal foes; ends at 2am
  - First pass (V72): inside, a BEAT ring at the bottom of the screen; hits landed on the beat do 1.6x (ON BEAT!), and a strobe flashes every bar. The 2am finale and the coach home chat are in. Needs a garage track at the right tempo (it uses the Elba club music for now)
- [ ] Mini-games 6 and 7 go in the Harvest Moon arcade once met, like the others

### Characters (PixelLab, Tim has topped up credits)
- [ ] Mick (big, fat, bald, old, East End landlord), Sue (2000s older landlady, short blonde going grey), Alan (thin, blonde, unkempt, always half-cut), Jeff (huge, short dark hair, dirty polo shirt). Lightly tweaked names, since the APK gets passed round
  - Done (31 Oct): looks signed off; idle, walk, attack, hurt and knockdown for all four, plus Sue's shout and Mick's belly charge. Sheets in `tools/v72/src/`, notes in `tools/v72/pixellab_ids.md`
- [x] Build the game sheets for Mick, Sue, Alan and Jeff (as `tools/v53/foe_sheets.py` does), skipping the hit-smear frames noted in pixellab_ids.md
  - Done (V72): `tools/v72/foe_sheets.py` -> web/sprites/{mick,jeff,sue,alan}.png; the template falls and get-ups stitched into one knockdown row
- [ ] Atlantis bouncers, Ram Ba Ba door staff, a rival crew at the bus stop, clubbers
- [ ] Brick phone (Kelly's Snake), pool cue, horseshoe, wagon wheel weapon and pickup sprites

### Backdrops (Meshy, kept true to the photos, same style as the other stages)
- [x] Street strip: Pizza Express corner (dormers, white corner bay, blue roundel, TO LET board, barbers) to the roundabout, Ram Ba Ba (Young's fascia, roller shutter, Church Hill sign, X-pattern window rails, the 2nd floor TO LET board, IB 798 bollard), the car park, the Blacksmiths' wing, Ye Olde Blacksmith (black shutters, anvil and smith bracket sign, brass lanterns, barrel planters, chalkboards, flagpole, planted roof on the wing) and the mirror shop's NO PARKING gable
  - Fixed (31 Oct, Tim's notes): the road past Ram Ba Ba ran into a fence and there were flower beds in it. Ram Ba Ba repainted flat on, the Church Hill junction, the car park behind its wall, and the pavement widening smoothly to the pub; the road now runs straight through to the Blacksmiths
  - Done (first pass, 31 Oct): five panels and three bridges, one 5408 px strip with no visible joins, in `tools/v72/img/orp01/` (see LAYOUT.md there). Painted from the photos with `tools/v72/orp_panel.py`; joins with `tools/v72/bridge.py` (MIX=0 when a bridge keeps the cut)
- [x] No St George bunting on the Blacksmiths (that was the 2002 World Cup); a faded "Artichoke Inn" ghost sign as an easter egg
  - Done: no bunting; the ghost sign is on the end wall
- [x] Blacksmiths inside: the L-shaped room, bar in the corner, pool table at the top of the L, blacksmith's tools, wagon wheels and horse brasses on the walls, fruit machines, seating round the edges
  - Done (first pass): bi0, bi1, bi2, a 3440 px strip: door and seating, the bar jutting out of the corner with a bell over it (Mick's), the pool room with a fire exit
- [x] Atlantis outside: gold ATLANTIS on the navy oval with the merman crest, blue NIGHTCLUB, the white wave-shaped canopy, yellow brick with brown bands, blue bollards, DJ EZ posters in the ornate frames, a NO TRAINERS sign
  - Done (first pass): at0. The canopy's wave ribs run off the right edge; paint one more panel if the stage needs to scroll
- [x] Atlantis inside: dance floor, strobes, the DJ booth with a DJ EZ silhouette (posters and silhouette only, not his likeness or voice)
  - Done (first pass): ai0, DJ EZ banner over the booth
- [x] Atlantis inside: the gold crest on the wall came out looking like an elephant, not a merman. Repaint that bit
  - Done: ai1, a gold merman with a crown and trident
- [ ] Tim: check the panels look right to you (anything missing or wrong from real life), before they go in the game
- [ ] Floors: the strip's pavement and road are painted in perspective near the roundabout; cut a flat walkable floor (as V60 did) when the stage goes in
- [x] Wire the panels into stages.json / MESHY_BG once the strip is signed off
  - Done (V72): `tools/v72/orp_bg.py` fits and tiles them into web/bg/meshy/orp_*.png (drawn by the V64 Meshy code). Atlantis outside and inside joined with a cut-away of the club wall (door2.webp)

### Orpington 2001: still to do after V72
- [x] Tim: play the chapter on a phone (THE HIGH STREET, YE OLDE BLACKSMITH, ATLANTIS) and say what feels off
  - Done (31 Oct): the joins didn't blend, the High Street strip didn't work at all, you could walk up the walls, the crossing was over too quickly, the stealth wasn't explained (ran to the bar and nothing happened), Atlantis's outside to inside join was horrible, under 5 minutes for the lot. All reworked in V73, below
- [ ] The run back up the High Street to make the coach (auto-runner), between the Blacksmiths and Atlantis
- [x] A garage track for Atlantis at a steady 2-step tempo
  - Done: Alarm Call, 134 bpm; the BEAT ring follows the song itself (its loop is exactly 128 beats), so ON BEAT! lands with the music
- [x] Comic pages for the chapter (Kelly at the door, the coach, 2am) in tools/v71/comics.py
  - Done (V73): five pages, `tools/v73/comics.py`
- [x] A trophy for finishing the chapter, like the other chapters'
  - Done (V74): UNDERAGE (finish Orpington 2001), and NOKIA ROYALTY (300 in Snake)
- [x] Mick's boss card art (bosscard/) and Jeff's
  - Done (V74): Alan, Jeff and Mick, painted in Meshy from their sprites (`tools/v74/bosscards.py`)
- [ ] Sue: only her top half shows over the bar, clipped by a fixed line; check it sits right on a phone (looked right in the headless phone shot)

### Orpington 2001 rebuilt (V73, from Tim's play-test)
- [x] No more stitched strips: every place is one screen made from one Meshy painting, with a wipe to the next (`tools/v73/scenes.py`, web/bg/orp/). The High Street is four places (the bus stop, the crossing, Ram Ba Ba, outside the Blacksmiths); the Blacksmiths four (the lounge, the bar, the pool room, back to the bar for Mick); Atlantis two (the queue, the dance floor). Walk off the side the GO arrow points to
- [x] Walking up the walls: each place's floor line measured from its own painting, and the bar, the pool table, the lounge seating and the lamp posts block you
- [x] Bus stop: hold it against the Petts Wood lot; after each wave a lad turns up and fights with you (Sam last: "Bus was late"); they go on ahead to the Blacksmiths
- [x] The crossing is a proper Frogger on its own painted screen: four lanes, three crossings (over, back for Sam's phone, over again with the 61 bus), a hit sends you back to the kerb, mopeds can be jumped
- [x] Getting served explained with a how-to card, Sue's gaze drawn on the floor when she's watching, HIDE spots marked, an ID meter over your head that fills (not instant), an ORDER HERE spot, then carry the pints back to the lads' table (walk, don't run, dodge Alan). Six pints in three trips; IDed three times and it kicks off anyway. Byron gets IDed twice as fast
- [x] Atlantis: a queue down the road that moves only when it's calm; queue-jumpers push in and you sort them out; at the door Kelly is turned away (comic page), then a cut inside. The dance floor is packed with dancers on the beat; a few at a time stop (a "!") and come for you, five waves, then 2am lights on and the last lot
- [x] Comic pages: the bus stop (start), the spilt pint (it kicks off), Mick's last orders, the door, 2am (end)
- [x] Every new mechanic opens with a how-to card (HIT to go)
- [ ] Tim: play it again on a phone. Expected length now around 20 minutes for the chapter
- [x] Kelly's Snake: a bonus round after Atlantis (Kelly on the coach, 11pm to 2am, his Nokia, the battery dies after 90 seconds), then a SNAKE cabinet at the far end of the Harvest Moon with its own board (V74)
- [x] Horseshoes and cart wheels in the pub: horseshoes to pick up, swing or throw (CLANG!); cart wheels roll across the pool room and come off the wall when Mick rings the bell, with an arrow first, and flatten whoever they meet, foes too (V74)
- [x] Tim's notes on 1.81 (31 Oct): the lamp posts outside Pizza Express and the Blacksmiths blocked a big strip of the screen; you could walk up the shopfronts at the bus stop, Ram Ba Ba and the Blacksmiths; the Ram Ba Ba bouncer looked out of place; the Atlantis queue went up faster than it came down (past 50)
  - Done (V75): posts block only a small spot at their foot and are drawn over anyone behind them (you can walk round the back); the street places' floor line moved down to where the buildings actually meet the pavement (FT 406); the bouncer is gone; queue-jumpers no longer add to the queue, it only counts down (10 to the door), with four lots of them pushing in along the way
- [ ] Still on the list: the run back up the High Street to make the coach

### Orpington 2001: its own crowd (V76, 31 October)
Tim: build a bunch of new, unique NPCs with different attacks. Done (V76): ten locals drawn and animated in PixelLab (`tools/v76/pixellab_ids.md`), each with a move nobody else in the game has. They play as a group like the 1999/2006 crowds (flanking, piling in when you're held) and replace the reused 1999 lot in the chapter's fights
- [x] KAPPA KID (the bus stop, Ram Ba Ba): pops his trackies off by the poppers and cracks them like a whip from outside punching range (POPPERS!, TRACKIED!)
- [x] RAZOR KID: rides his Razor scooter straight through you along his line (step out of it), or kicks it at you along the floor (jump it), then has to go and fetch it. Knock him off mid-ride: WIPEOUT!
- [x] FROSTED TIPS: a spinning roundhouse that catches both sides, a knee slide along the floor (jump it), and he stops to check his hair the first time you hit him (he takes extra damage while he does)
- [x] SCRUNCHIE: throws her Nokia 3310, which comes back to her hand (hits going and coming); knock her down and it drops (STILL WORKS). Down to her last mates, she rings her brother
- [x] GARAGE MC (street and Atlantis): gets on the mic, three sound waves roll out (they shove you back, the first one dizzies you close up) and his mates speed up. Get behind him
- [x] THE BUILDER (outside the pub, the bar, the pool room, Mick's bell): an unstoppable shoulder barge that skittles his own lot too, and seeing stars if he hits the wall; throws bar stools (a red ring shows where it lands)
- [x] THE OLD BOY: slow and doesn't flinch; hooks you round the neck with his walking stick from across the room, reels you in and gives you a dig (mash to slip it)
- [x] POOL SHARK (the pool room): a cue jab with twice anyone's reach, and the break: three balls along the floor in a spread that flatten his own lot too
- [x] MOSCHINO (the queue, the dance floor, 2am): shakes the champagne and sprays it; caught facing him, you're blinded (held, slowed, the screen fizzes). Turn your back
- [x] RAVER (the dance floor): glowstick flurries, only on the beat on the dance floor; his whistle sets the dancers round him off early (off the floor it rings your ears)
- [x] Props drawn by hand: the scooter, a bar stool, the 3310 (`tools/v76/props.py`)
- [ ] Tim: play the chapter on a phone and say which of them are too much or too little

### Orpington 2001: lighting (V77, 31 October)
Tim asked what Meshy could do with lighting: it has no live lighting, but it can paint a light map of each place, and the game moves it. Tim chose the glow layers and lighting on the fighters
- [x] Glow layers for all nine places: Meshy repaints each backdrop with only its lights left (windows, lamps, signs, neon, the stage lights); the layer takes its colours from the painting itself so it sits exactly on it (`tools/v77/glow.py`, 81 Meshy credits plus one re-roll for Ram Ba Ba, which Meshy had shifted)
- [x] The places dim a little for the time of night and the glow moves: street lamps flicker, the pub glow breathes, the Atlantis neon buzzes now and then, the dance floor pulses on the beat; a car's headlights sweep along the pavement and shop fronts at the bus stop, Ram Ba Ba and outside the Blacksmiths every so often
- [x] Lighting on the fighters (players, the lads, every foe and NPC): night blue on the street, warm in the pub, purple in the club, and the nearest lights fall on them from their side (street lamps, windows, the pool table lamp, the fruit machines changing colour, headlights, the crossing's cars, the club's sweeping beams). Walk under a lamp and you light up
- [ ] Tim: check it on a phone, that it isn't too dark on the street and that the dance floor (14 dancers, all lit) still runs smoothly
- [ ] Next if wanted: painted lit/unlit pairs for the big moments (Atlantis at 2am with the house lights up, last orders dimming the Blacksmiths)

### Snake on a phone (V78, 31 October)
- [x] Tim: the Snake controls don't work well, maybe an up/down/left/right overlay. Done (V78): on a phone, Snake had no stick and only turned by tapping left/right/above/below the middle of the screen. Now there's a D-pad of four big arrows beside the Nokia (on the right, or the left with the stick set to the right in Settings); a tap anywhere on the pad counts by which way it is from the middle, the arrow lights up, and a swipe anywhere on the screen also turns (every 30 px of finger travel is a turn, so you can steer without lifting). Same on the coach and the Harvest Moon cabinet

### Quality of life (V79, 31 October)
Tim asked for quality of life ideas, then for all six
- [x] The "!" warning before a big move now covers the ten Orpington locals too (the Builder's barge, the Old Boy's hook, Moschino's champagne and the rest), lifted clear of each sprite's head
- [x] How-to cards stop the game the first time only; after that a one-line reminder at the top while you play (Settings: HOW-TO CARDS, FIRST TIME ONLY / EVERY TIME)
- [x] An arrow at the edge of the screen for anyone walking in off it, on every stage (red for a boss)
- [x] Auto-turn on a phone: punch with nobody in front and someone right behind, and you turn round to hit them, unless you're pushing the stick the way you face (Settings: AUTO-TURN, ON / OFF)
- [x] Settings: LIGHTING, FULL / LOW (low keeps the glowing backdrops, skips lighting the fighters, for older phones)
- [x] Orpington stages carry on from the place you'd reached (the bar, the pool room, the dance floor) when you carry a run on after the app closed; RESTART STAGE still starts from the top
- [x] Found while testing: a how-to card appearing mid-punch left the punch stuck (a glitch message on screen); fixed
- [ ] Tim: try AUTO-TURN on the phone and say if it turns you when you didn't want it to

### Menus redesign (31 October, mockups)
Tim: the title goes straight into character select, the options along the bottom are cluttered and hard to read, and the level select is messy now Orpington 2001 is in (the chapter tabs wrap onto two lines). Mockups on a claude.ai Design canvas ("MBC Legacies menu redesign"): a start menu, the lad select, two takes on the level select, and a Ready screen
- [x] Mock up: a start menu between the title and the lads (CARRY ON with the saved run, NEW GAME, PLAY ONLINE, THE HARVEST MOON, TROPHIES, SCORES, SETTINGS; the name and sound top right), so the bottom bar goes
- [x] Mock up: lad select with faces in the roster, the steps as 1 LAD / 2 STAGE / 3 GO, PLAY AS TIM on the card, BACK to the menu top left, nothing else along the bottom
- [x] Mock up: level select A (chapters down the side with a picture each, the chapter's stages as picture cards, START HERE) and B (the years as postcards on a timeline, the stages listed under it)
- [x] Mock up: a Ready screen with the difficulty folded in (Language moves to Settings)
- [x] Tim: pick a level select (A or B) and say what to change, then build it into the 3D title's HTML layer (#t3)
  - Done (V80): Tim picked A. Built into the real menus over the 3D street: the start menu (the lads lined up on the road to its right, the logo above it), the header on the select screens (back, the steps that tick off with what you picked, your name), faces in the roster, the chapters down the side with NEW on Orpington 2001 until you've a rank there, the stages as picture cards, START HERE, then 3 GO. SETTINGS on the menu opens the settings panel on its own. Language moves to Settings
- [x] Tim: Byron's roster picture was just his head next to the others' head and shoulders (his card is a smaller, big-headed figure). Done (V80): each lad's face is framed from his own card (`tools/v80/faces.json`), so they all match
- [ ] Tim: try the new menus on the phone (the start menu buttons, the roster faces, the chapter list)

### For whoever builds next
- [ ] Re-running `tools/v64_build.py` adds another copy of the Meshy backdrop line in `drawStageBg` each time (there are ten now; harmless but untidy). `title3d_build.py` undoes V65's locked-lad fixes in the page. V66 to V71 patch the page directly for that reason

### Music (31 October)
- [x] Atlantis: use Alarm Call (key `alarmcall`, or `alarmcall2` for the alarm on every other beat). Whoever builds Atlantis: set the stage's `music` to that key. Tim: say which version
  - Done (V72): Atlantis plays `alarmcall` (alarm on every beat). Tim: say if you'd rather have `alarmcall2`; it's one word in STAGES.orp_atlantis in tools/v72/orp2001.js

#### Music available for new levels
All in `web/music/` and registered in `TRACKS` (index.html, after the main table), so a new stage only needs `music: '<key>'`. Each is a seamless loop of about a minute. Source is in the claude.ai project under `soundtrack/`.

| Key | Track | Style | Source |
|---|---|---|---|
| `alarmcall` | Alarm Call (alarm every beat) | Spy-thriller 2-step garage, 134 bpm, G minor, guitar-style chip riff, blaring alarm on the beat. **Used: Atlantis (V72)** | songs5.py |
| `alarmcall2` | Alarm Call (alarm every other beat) | The same with the alarm on beats 1 and 3 only | songs5.py |
| `codered` | Code Red | 136 bpm, A minor, chugging riff, two-tone police siren on every beat (chase feel). **Used: The High Street, Orpington 2001 (V72)** | songs7.py |
| `lockdown` | Lockdown | 130 bpm, C minor, heavy galloping riff, low buzzer on 2 and 4, half-time breakdown. **Used: Mick's boss fight at the Blacksmiths (V72, BOSS_MUSIC.orp_pub)** | songs7.py |
| `heist` | Heist | 138 bpm, F# minor, stop-start octave riff, rising dive klaxon on every bar. **Used: Ye Olde Blacksmith, getting served and the fight before Mick (V72)** | songs7.py |
| `deepcover` | Deep Cover | Four-channel NES-style chiptune 2-step, 132 bpm, E minor, plucky pulse riff, triangle sub with glides | songs6.py |

- [ ] Still free: `alarmcall2` and `deepcover` (the run back to the coach could take Deep Cover). When a level takes one of these, note it here; when a track is clearly not going to be used, delete its file from `web/music/` and its line in `TRACKS` so the app stays small

## Carried over from the build plan

### Firebase rules (Tim to paste, from the README)
- [ ] One up-to-date rules paste covering everything added since Version 55: shared boards, `players`, `online`, `invites`, `chat`, `saves` and `restore`. Until then scores, presence, chat and cloud saves only half work. Tick this off if it's already done

### Online co-op
- [ ] A proper test with two real phones
- [ ] The pub and the bonus rounds are skipped in an online game
- [ ] Per-player tabs in co-op (competitive totals), whose round it is, and 1v1 darts and penalties

### Real phone checks
- [ ] Friends' scores save to the boards from their own phones
- [ ] The stick dead zone, running and speech bubble sizes feel right on a phone and a tablet
- [ ] Pause menu settings, CARRY ON and chat skip (Version 45) on a phone, and online
- [ ] A full play as Ash on a phone
- [ ] The pub and its mini-games on a phone
