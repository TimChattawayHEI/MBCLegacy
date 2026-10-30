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
