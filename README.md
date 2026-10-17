# MBC Legacies

The lads vs everybody. A 16-bit beat 'em up, Orpington 1999 to Elba 2002 to Denise's Fishery.

## Get the game (Android)

**[Download the latest APK](https://github.com/TimChattawayHEI/MBCLegacy/releases/latest/download/MBC-Legacies.apk)**

Open the file on your phone. The first time, Android asks whether to allow installs from your browser or files app: allow it. To update, install the new one over the top.

## How to play

Move with the stick, HIT to attack (tap it for your combo), JUMP, and SPECIAL when the bar is full. Hold HIT and let go for your lad's mini special: it hits everyone around you, but costs a little health if it lands. PLAY ONLINE on the select screen starts a two-player game with a friend's phone: one hosts and reads out the code, the other joins.

## What's here

- `web/` the game itself (one page plus its art, music and fonts). The same game runs on claude.ai.
- `android/` a small Android app that shows the game full screen.
- `tools/title3d_build.py` wires the 3D title and select screens (`tools/title3d/`) and any-stage starts into `web/index.html`. Run it again after rebuilding the page from older sources.
- `tools/v44_build.py` (run after `title3d_build.py`) is the Version 44 optimisation pass: no full-size copies of the sprite sheets, skies and the fishery car park drawn once and reused, all art preloaded with a LOADING wait at stage start, and the old vector fallback art removed. Run it again after rebuilding the page from claude.ai.
- `web/vendor/three.module.min.js` is three.js r165 (MIT, see `three.LICENSE`), used by the title screen in the app.
- `.github/workflows/apk.yml` builds the APK on every push to `main` and publishes it as the latest release.

The signing key (`android/mbc.keystore`) is in the repo on purpose, so every build installs over the previous one. This is a game for friends, not a Play Store app.
