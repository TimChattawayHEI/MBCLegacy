# MBC Legacies

The lads vs everybody. A 16-bit beat 'em up, Orpington 1999 to Elba 2002 to Denise's Fishery.

## Get the game (Android)

**[Download the latest APK](https://github.com/TimChattawayHEI/MBCLegacy/releases/latest/download/MBC-Legacies.apk)**

Open the file on your phone. The first time, Android asks whether to allow installs from your browser or files app: allow it. To update, install the new one over the top.

## What's here

- `web/` the game itself (one page plus its art, music and fonts). The same game runs on claude.ai.
- `android/` a small Android app that shows the game full screen.
- `.github/workflows/apk.yml` builds the APK on every push to `main` and publishes it as the latest release.

The signing key (`android/mbc.keystore`) is in the repo on purpose, so every build installs over the previous one. This is a game for friends, not a Play Store app.
