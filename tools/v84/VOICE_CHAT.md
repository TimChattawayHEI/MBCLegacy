# Voice chat in online co-op (plan, 9 November)

Two players in an online game can talk to each other. Not the Harvest Moon (a pub full of people needs a hosted voice service in the middle; see the end).

## How it fits what's there

- The co-op link is one WebRTC connection made in the lobby (`rtcStart` in `web/index.html`). Today it carries only the `game` data channel (button presses). Voice goes over the same connection as a second stream, so there's no new server for the audio itself.
- The connection details are swapped once through Firebase (`rtc_offer`, `rtc_answer`), with no renegotiation after. So the audio slot has to be in the offer from the start: the host adds an audio transceiver before `createOffer`, the guest turns its one to send and receive when it answers. The mic is attached later with `replaceTrack`, so switching voice on or off mid-game never touches the connection.
- Voice sits outside the lockstep game, like music and particles. It can't knock the phones out of sync. It does share the connection with the button presses, so it's kept small (mono, about 24 kbps, silence sends next to nothing).
- An old app on the other phone just answers without audio. The game plays as before and the lobby says their app needs updating for voice.
- App only, like PLAY ONLINE. The claude.ai copy doesn't get it.

## 1. The Android app (needs a full APK, not an in-app update)

- `AndroidManifest.xml`: add `RECORD_AUDIO` and `MODIFY_AUDIO_SETTINGS`.
- `MainActivity.java`: a `WebChromeClient` whose `onPermissionRequest` grants the microphone only (nothing else), asking Android for `RECORD_AUDIO` first if it hasn't been given. Refused: the game is told and shows "Mic's off. You can still hear your mate."
- Keep the sound on the loudspeaker. When a phone opens the mic for a call, Android can switch to call mode, which can quieten the game or send it to the earpiece. `MBCNative.voice(true/false)` sets the speaker on while voice is live and puts the phone back to normal after. This is the bit most likely to behave differently from phone to phone, so it's first on the real-phone test.
- `MBCNative.canVoice()` so the game knows this APK can do it (older APKs don't show the voice options).
- Mic off when the app goes to the background, back on when it comes back (if it was on).

## 2. The relay server (TURN)

Right now, if two phones can't connect directly (some 4G networks, strict home routers), the button presses fall back to Firebase. Voice can't go that way. A relay server fixes that for both: voice works, and button presses get a much faster backup than Firebase.

- Recommended to start: Metered's Open Relay, free, 20 GB a month, no server of our own. Voice is about 15 MB an hour each way, so that's a few hundred hours of relayed play a month. Tim signs up and the details go in `web/net.json`, added to `iceServers`.
- If it grows: Cloudflare's TURN (first 1,000 GB a month free), which needs a small Cloudflare Worker to hand out short-lived logins. A bit more setup.
- The HUD shows DIRECT, RELAY or VIA SERVER (Firebase).

## 3. In the game (`tools/v84/voice.js`, `tools/v84_build.py`)

- Mic: echo cancellation, noise suppression and auto gain on. Open mic with a mute button, not push to talk (no spare thumbs mid-fight).
- Your mate's voice goes through the game's own mixer so it has its own volume. (Chrome only plays WebRTC audio through Web Audio if the stream is also on a muted `<audio>` element. Known quirk, handled.)
- Music ducks to about 40% while your mate is talking and comes back over half a second. Effects aren't ducked.
- Lobby: a VOICE pill for each player. The first time you switch it on, one line says why it wants the mic, then Android asks. Talking works from the lobby, so you can chat while picking lads.
- HUD: a mic button by pause (tap to mute, crossed out when muted). Your mate's face in the HUD gets a speaker mark while they talk. M mutes on a keyboard.
- Pause menu: MUTE MIC, MUTE MATE. Settings: VOICE VOLUME, VOICE (on or off by default), DUCK MUSIC.
- Your mate drops for 20 seconds: voice goes with them, as everything else does now.
- Voice is phone to phone and never stored. The mic is only open in an online game after you've switched it on, and Android shows its own mic light.

## 4. Testing

- Headless, two pages over the test relay (`?netmock`) with Chromium's fake mic: audio arrives (WebRTC stats show it flowing), mute stops it, the music ducks, and the lockstep checksums and input delay are the same as without voice.
- An old-app guest (no audio slot) still plays a full stage.
- Forced through the relay only (a `?relayonly` flag): voice and button presses both go through, the HUD says RELAY.
- Tim, two real phones: on wifi and on 4G; game sound stays on the speaker; no echo with the sound up; the mic light goes off when you mute or close the app.

## Later: voice in the Harvest Moon

Every phone sending to every other phone falls over after about four or five people. For the pub it would need a voice service in the middle (LiveKit, or Cloudflare's SFU), which also makes proximity voice possible: louder as you walk up to someone at the bar. New service to run and pay for, so only if co-op voice gets used.
