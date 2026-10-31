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
- [ ] Decide where it sits in the campaign: between 1999 and Elba 2002 (it's 2001), with the time travel arc landing the lads there
- [ ] Group chat opener in 2001 SMS speak on brick phones ("c u @ pizza xpress 8, dnt b l8"); a present-day chat flashback (the Blacksmiths is now Aksular, Ram Ba Ba became Fiesta Mexicana)
- [ ] Comic pages: Kelly knocked back at the Ram Ba Ba door; the coach to Croydon (replaces a coach fight, since the N47 is already a bus fight); 2am, everyone back on the coach and Kelly asleep on it
- [ ] Tim: confirm the night's details (what time the coach left, any other Blacksmiths or Atlantis stories worth a moment)

### Stages and mechanics (not just left to right)
- [ ] 1. Pizza Express bus stop: lads arrive one at a time while you hold the stop against a rival crew
- [ ] 2. The mini roundabout: a short Frogger-style crossing (zebra, Belisha beacons, Corsas, the red estate, a bus)
- [ ] 3. Ram Ba Ba, first pass: no fight; a chalkboard by the shutter says ATLANTIS COACH 10.30 and starts the night's clock on screen
- [ ] 4. The Blacksmiths, getting served: stealth in the L-shaped bar. The bar is in the corner so whoever's serving sees down both arms; keep Byron (looks like a kid) out of Sue's eyeline behind fruit machines and seating while the oldest-looking lad goes up
- [ ] 5. The Blacksmiths, it kicks off: Alan and Jeff start it round the pool table at the top of the L. Throwable horseshoes, pool cues and balls, wagon wheels off the walls rolling as hazards, the fruit machine gives a hold/nudge bonus when hit. Boss: Mick ringing the bell, Sue's "OI!" from behind the bar as a stun
- [ ] 6. The run back: auto-runner up the High Street to make the coach (bollards, bins, people); miss it and restart the run
- [ ] 7. Ram Ba Ba door: blag mini-game with a nerve meter, tapping to keep Kelly's Mass Head from inflating. Scripted to fail (it's canon): Kelly is refused and sits on the coach till 2am. Playing as Kelly: Snake on his brick phone, with a board
- [ ] 8. Atlantis: rhythm brawler, hits land harder on the 2-step beat, strobes reveal foes; ends at 2am
- [ ] Mini-games 6 and 7 go in the Harvest Moon arcade once met, like the others

### Characters (PixelLab, Tim has topped up credits)
- [ ] Mick (big, fat, bald, old, East End landlord), Sue (2000s older landlady, short blonde going grey), Alan (thin, blonde, unkempt, always half-cut), Jeff (huge, short dark hair, dirty polo shirt). Lightly tweaked names, since the APK gets passed round
  - Done (31 Oct): looks signed off; idle, walk, attack, hurt and knockdown for all four, plus Sue's shout and Mick's belly charge. Sheets in `tools/v72/src/`, notes in `tools/v72/pixellab_ids.md`
- [ ] Build the game sheets for Mick, Sue, Alan and Jeff (as `tools/v53/foe_sheets.py` does), skipping the hit-smear frames noted in pixellab_ids.md
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
- [ ] Wire the panels into stages.json / MESHY_BG once the strip is signed off

### For whoever builds next
- [ ] Re-running `tools/v64_build.py` adds another copy of the Meshy backdrop line in `drawStageBg` each time (there are ten now; harmless but untidy). `title3d_build.py` undoes V65's locked-lad fixes in the page. V66 to V71 patch the page directly for that reason

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
