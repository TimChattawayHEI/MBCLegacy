# MBC Legacies

The lads vs everybody. A 16-bit beat 'em up, Orpington 1999 to Elba 2002 to Denise's Fishery.

## Get the game (Android)

**[Download the latest APK](https://github.com/TimChattawayHEI/MBCLegacy/releases/latest/download/MBC-Legacies.apk)**

Open the file on your phone. The first time, Android asks whether to allow installs from your browser or files app: allow it. To update, install the new one over the top.

## How to play

Move with the stick (hold it right out to run), HIT to attack (tap it for your combo), JUMP, and SPECIAL when the bar is full. Hold HIT and let go for your lad's mini special: it hits everyone around you, but costs a little health if it lands. PLAY ONLINE on the select screen starts a two-player game with a friend's phone: one hosts and reads out the code, the other joins.

## What's here

- `web/` the game itself (one page plus its art, music and fonts). The same game runs on claude.ai.
- `android/` a small Android app that shows the game full screen.
- `tools/title3d_build.py` wires the 3D title and select screens (`tools/title3d/`) and any-stage starts into `web/index.html`. Run it again after rebuilding the page from older sources.
- `tools/v44_build.py` (run after `title3d_build.py`) is the Version 44 optimisation pass: no full-size copies of the sprite sheets, skies and the fishery car park drawn once and reused, all art preloaded with a LOADING wait at stage start, and the old vector fallback art removed. Run it again after rebuilding the page from claude.ai.
- `tools/v45_build.py` (run after `v44_build.py`) is the Version 45 quality of life pass: CARRY ON a run after the app closes, RESTART STAGE and a SETTINGS panel in the pause menu (music and effects volume, vibration, gentler shake and flashes, touch button size, see-through buttons, left-handed stick), a SKIP button on group chats, and phone vibration.
- `tools/v47_build.py` (run after `v45_build.py`): hold the touch stick right out to run (a ring fills round the knob first), plus a RUNNING setting for running on any full push. Every lad has his own select-screen pose in `web/sprites/pose_<id>.png` (Version 48): a PixelLab animation drawn three-quarter on (south-east), as a strip of frames at the sheet's cell size with the feet on the sheet's anchor. Frame 0 shows while he's chosen; the rest play when he's picked.
- `tools/v49_build.py` (run after `v47_build.py`): boss finishes (freeze, flash, music cut, slow motion and a punch-in on the last boss of a stage), boss intro cards that take the place of the old boss banners, and S to D stage ranks on the points screen, with the best kept per stage (`carpdiem.ranks`) and shown on the 3D stage list.
- `tools/v50_build.py` (run after `v49_build.py`): Thet, the unlockable eighth lad. His sheet `web/sprites/thet.png` and `tools/v50/thet_meta.json` come from `tools/v50/thet_sheet.py`, which lines up the PixelLab workbench sheets in `tools/v50/src/`. Also edits `tools/title3d/title3d.js` so the 3D select keeps him.
- `tools/v51_build.py` (run after `v50_build.py`): new hand grip points for the weapons that were redrawn in PixelLab (the PNGs in `web/bg/weapons` and `web/bg/shots` are the PixelLab versions).
- `web/vendor/three.module.min.js` is three.js r165 (MIT, see `three.LICENSE`), used by the title screen in the app.
- `.github/workflows/apk.yml` builds the APK on every push to `main` and publishes it as the latest release.

The signing key (`android/mbc.keystore`) is in the repo on purpose, so every build installs over the previous one. This is a game for friends, not a Play Store app.
