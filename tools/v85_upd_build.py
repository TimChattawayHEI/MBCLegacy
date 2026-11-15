"""Version 85: the in-app update says how it's going. python3 tools/v85_upd_build.py (re-runnable; patches web/index.html).

The soundtrack made one update about 47 MB, and the app showed nothing until all of it had downloaded, so on a phone it
looked as if updates had stopped. Now, on the menus:
- while the files download, the card says DOWNLOADING with files and MB done (no button; Later hides it)
- if the download stops (no signal, a file that didn't match), the card says so with the reason and TRY AGAIN, and the
  game tries again by itself a minute later rather than in 20 minutes
Page only: the Android side (Ota.java) is unchanged, so this arrives as an ordinary in-app update."""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); PAGE = os.path.join(ROOT, 'web', 'index.html')
s = open(PAGE, encoding='utf-8').read()
SWAPS = [
    # what the app is doing: downloading (with progress) and a download that stopped
    ("  else if (st.state === 'apk' && st.latest > UPD.mine) { UPD.latest = st.latest; UPD.kind = 'apk'; UPD.url = UPD_APK; }\n",
     "  else if (st.state === 'apk' && st.latest > UPD.mine) { UPD.latest = st.latest; UPD.kind = 'apk'; UPD.url = UPD_APK; }\n"
     "  else if (st.state === 'downloading' && st.latest > UPD.mine) { UPD.latest = st.latest; UPD.kind = 'down'; UPD.prog = st; }   // Version 85: show the download\n"
     "  else if (st.state === 'error' && st.latest > UPD.mine) { UPD.latest = st.latest; UPD.kind = 'err'; UPD.err = st.err || ''; }   // Version 85: and say if it stopped\n"
     "  else if (st.state === 'checking' && UPD.kind === 'err') { UPD.kind = 'down'; UPD.prog = null; }   // trying again\n"
     "  else if ((UPD.kind === 'down' || UPD.kind === 'err') && st.state === 'current') UPD.kind = '';\n"),
    # a stopped download is tried again after a minute
    ("  if (quiet && now - UPD.checkedT > (UPD.mine ? 20 * 60000 : 4000)) updCheck();",
     "  if (quiet && now - UPD.checkedT > (UPD.kind === 'err' ? 60000 : UPD.mine ? 20 * 60000 : 4000)) updCheck();   // Version 85: a stopped download retries after a minute"),
    # TRY AGAIN
    ("  if (UPD.kind === 'ready') {   // Version 66: switch in the downloaded files and reload",
     "  if (UPD.kind === 'err') {   // Version 85: try the download again now\n"
     "    UPD.dismissed = 0; UPD.dismissedT = -1e9; UPD.kind = 'down'; UPD.prog = null; UPD.checkedT = performance.now();\n"
     "    try { window.MBCNative.otaCheck(); } catch (e) { /* next time */ }\n"
     "    return;\n"
     "  }\n"
     "  if (UPD.kind === 'ready') {   // Version 66: switch in the downloaded files and reload"),
    # the card's words for the two new states, refreshed as the download goes
    ("    if (UPD.kind === 'ready') {\n      el.querySelector('#updWhat').textContent = 'UPDATE READY: 1.' + UPD.latest;",
     "    el.querySelector('#updGo').style.display = UPD.kind === 'down' ? 'none' : '';\n"
     "    if (UPD.kind === 'down') {   // Version 85\n"
     "      el.querySelector('#updWhat').textContent = 'DOWNLOADING 1.' + UPD.latest;\n"
     "    } else if (UPD.kind === 'err') {\n"
     "      el.querySelector('#updWhat').textContent = 'UPDATE 1.' + UPD.latest + ' STOPPED';\n"
     "      el.querySelector('#updSub').textContent = (UPD.err ? UPD.err + '. ' : '') + \"It'll try again in a minute.\";\n"
     "      el.querySelector('#updGo').textContent = 'Try again';\n"
     "    } else if (UPD.kind === 'ready') {\n      el.querySelector('#updWhat').textContent = 'UPDATE READY: 1.' + UPD.latest;"),
    ("    sfx('incoming');\n  }\n  const r = canvas.getBoundingClientRect();",
     "    if (UPD.kind !== 'down') sfx('incoming');\n  }\n"
     "  if (UPD.kind === 'down') {   // Version 85: how far it's got\n"
     "    const p = UPD.prog, mb = v => (v / 1048576).toFixed(v < 10485760 ? 1 : 0);\n"
     "    const t = p && p.total ? p.files + ' of ' + p.of + ' files, ' + mb(p.done) + ' of ' + mb(p.total) + ' MB. Keep the game open; you can play while it downloads.' : 'Starting...';\n"
     "    const sub = el.querySelector('#updSub'); if (sub.textContent !== t) sub.textContent = t;\n"
     "  }\n"
     "  const r = canvas.getBoundingClientRect();"),
]
for old, new in SWAPS:
    if new in s: continue
    assert s.count(old) == 1, old[:80]
    s = s.replace(old, new)
open(PAGE, 'w', encoding='utf-8').write(s); print('v85 update progress: patched')
