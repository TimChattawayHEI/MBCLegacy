# Orpington 2001: PixelLab ids (v3, side view)
- mick: Mick, the landlord (boss) 823b7757-670f-4f3c-afd2-6715958b61aa (80)
- jeff: Jeff, his son 7a5e3b22-b166-48a9-ac38-5b90002d436d (80, big bruiser)
- sue: Sue, the landlady c5fa2a6c-2cf2-4810-bce8-eb92f7d5372a (64, "OI!" stun from behind the bar)
- alan: Alan, his son 391b1264-9c21-43e1-b6f0-1f08abd7fa53 (64)

Looks first, animations after Tim signs them off (same set as tools/v53/ART_BRIEF.md: idle 6, walk 8, attack 8, hurt 4, knockdown 16).
`src/family_east.png`: the four facing east, left to right Mick, Jeff, Sue, Alan.

## Animations (east only, saved as workbench sheets in src/<key>/<anim>.png, scale 2, frame 1 is the reference)
Signed off by Tim 31 Oct (Mick keeps the beard PixelLab gave him).
- sue: idle 6, walk 8, attack 8 (slap), shout 8 (the "OI!": leans in, mouth open, jabs a finger), hurt 4 (frame 3 is a white hit smear: skip it), fall 7 + getup 5 (templates)
- alan: idle 6, walk 8 (shambling), attack 8 (sloppy hook; frames 7-8 have a small white swoosh behind him, strip detached specks), hurt 6 (template taking-punch), fall 7 + getup 5 (templates)
- mick: idle 6, walk 8, attack 8 (haymaker), belly 8 (a charge, for the boss's rush), hurt 4 (mild), knockdown 16 (falls back properly; frame 3 has white speed lines and 6-8 white specks: skip 3, strip detached specks)
- jeff: idle 6, walk 8, attack 8 (heavy hook), hurt 6 (template), fall 7 + getup 5 (templates; he comes out a bit slimmer in these, fine at speed)

The v3 knockdowns kept falling forward onto the face (three tries across the family), so the knockdowns for Sue, Alan and Jeff are
PixelLab's falling-back-death + getting-up templates: build the 16 frame knockdown as fall, hold the last fall frame, then getup.
Template sheets are 64 or 80 px canvases; the v3 ones are 84 to 108: line them up by the feet when building the game sheets.
