# Orpington 2001 crowd (Version 76): PixelLab ids (v3, side view, east only)
Street (the Petts Wood lot)
- kappa: KAPPA KID 91ca982f-ad53-4866-8a31-01d34a081d67 (64) - rips his trousers off by the poppers and whips you with them
- razor: RAZOR KID b2ad5e57-b521-4dad-923c-1fae6feaeb70 (64) - rides his Razor scooter through you, then kicks it at you along the floor
- frosted: FROSTED TIPS a8f9bda4-6d5c-43ee-9a11-8324c4b992b0 (64) - boyband spin kick, knee slide across the floor
- scrunchie: SCRUNCHIE 78f6ff62-3fac-4585-bcd0-d6d65d34784c (64) - throws her 3310, which comes back to her (hits going and coming)
- mc: GARAGE MC 34b58eab-356b-4df4-9865-a4e3a62a3a93 (64) - spits bars down the mic: a sound wave that pushes you back, and gees his mates up
The Blacksmiths
- builder: THE BUILDER c713ce1e-b80a-4f88-93cc-68dd51e020ba (80) - shoulder barge (can't be stopped), throws a bar stool
- codger: THE OLD BOY c492d4e0-dd5a-435d-b144-2f47842a65e8 (64) - hooks you with his walking stick from range, drags you in, headbutt
- shark: POOL SHARK 452ae620-53dd-4f6c-a802-e8387f8e0f2e (64) - long cue jab, breaks: three pool balls rolling along the floor
Atlantis
- moschino: MOSCHINO 63aaf8c0-e186-41eb-8199-7e543cc4fbe4 (64) - shakes a bottle of champagne and sprays it: blinded
- raver: RAVER be428fc7-7ff1-46a0-aa8e-f1d164824138 (64) - glowstick flurry, and his whistle sets the dancers off early

## Animations (east only)
Every kind: idle (fight-stance-idle-8-frames), walk (walking-8-frames), hurt (taking-punch), fall (falling-back-death), getup (getting-up)
as PixelLab templates, plus attack and its own moves as v3 custom (8 frames + the reference). Exceptions:
- builder: idle, walk and throw are v3 custom too (the templates drew him much slimmer than his own attack frames)
- scrunchie: her throw row is her attack again (the generated slap came out as pointing the phone, which is the throw)
- frosted: spin is the roundhouse-kick template, slide the running-slide template
- razor: ride is a kick-push run; the scooter (tools/v76/props.py) is drawn under him by the game

## Sheets
`pixelart_workbench join character:<id>:east:idle ...walk ...attack ...hurt ...fall ...getup ...<own rows> --as rows`, the preview it
saves copied to tools/v76/src/<key>.png, then `python3 tools/v76/foe_sheets.py` (row order and frame picks in its KINDS).
