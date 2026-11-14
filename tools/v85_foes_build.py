"""Version 85: enemies three-quarters on. python3 tools/v85_foes_build.py (re-runnable; patches web/index.html in place)

- Every kind in tools/v85/foes/<kind>.json (built by tools/v85/foe_sheet.py) gets its SPRITE_META and FOE_FRAMES entry
  replaced between the /* v85 foes */ markers, after SPRITE_ALIAS.
- foeFrame learns the new rows for kinds marked deep: a second punch for the second hit of a combo, an uppercut for the
  anti-air, head and body hurts taking turns, a dazed sway (stunned, drowsy) and a struggle when grabbed or netted.
  Display only: nothing here touches what the online checksum covers (x, y, z, hp).
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PAGE = os.path.join(ROOT, 'web', 'index.html')
FOES = os.path.join(HERE, 'v85', 'foes')
html = open(PAGE, encoding='utf-8').read()


def sub_once(old, new, label):
    global html
    if new in html: return
    if old not in html: sys.exit('v85 foes: anchor not found: ' + label)
    html = html.replace(old, new, 1)


kinds = sorted(f[:-5] for f in os.listdir(FOES) if f.endswith('.json'))
metas, frames = {}, {}
for k in kinds:
    d = json.load(open(os.path.join(FOES, k + '.json'))); metas[k] = d['meta']; frames[k] = d['frames']
block = ('/* v85 foes */ Object.assign(SPRITE_META, ' + json.dumps(metas, separators=(',', ':')) + ');\n'
         'Object.assign(FOE_FRAMES, ' + json.dumps(frames, separators=(',', ':')) + ');\n/* v85 foes end */')
anchor = "const SPRITE_ALIAS = { biglad: 'chunk', doorman: 'bouncer', rider: 'clubm', biker: 'clubm' };"
if '/* v85 foes */' in html:
    html = re.sub(r'/\* v85 foes \*/.*?/\* v85 foes end \*/', lambda m: block, html, flags=re.S)
else:
    sub_once(anchor, anchor + '\n' + block, 'sprite alias')

# foeFrame: count hurts as they start, and pick the deeper rows
sub_once("  if (e._ps !== st) { e._from = e._ps; e._ps = st; }",
         "  if (e._ps !== st) { e._from = e._ps; e._ps = st; if (st === 'hurt' || st === 'reel') e._hn = (e._hn || 0) + 1; }",
         'state change')
sub_once("  if (wRow) { const [a, M] = mv(wRow); return [a, M.pre[Math.min(M.pre.length - 1, Math.floor(t / 0.12))]]; }\n"
         "  if (hRow) { const [a, M] = mv(hRow); return [a, M.hit]; }",
         "  const deepRow = r => {   // Version 85: the second punch of a combo, and the anti-air uppercut\n"
         "    if (!F.deep || r !== 'attack') return r;\n"
         "    if (e.uppercut && has('upper') && F.upper) return 'upper';\n"
         "    if ((e.combo2n || 0) >= 1 && has('attack2') && F.attack2) return 'attack2';\n"
         "    return r;\n  };\n"
         "  if (wRow) { const [a, M] = mv(deepRow(wRow)); e._atkRow = a; return [a, M.pre[Math.min(M.pre.length - 1, Math.floor(t / 0.12))]]; }\n"
         "  if (hRow) { const [a, M] = mv(deepRow(hRow)); e._atkRow = a; return [a, M.hit]; }",
         'wind and hit')
sub_once("    case 'recover': { const M = F.attack; return ['attack',",
         "    case 'recover': { const ar = F.deep && e._atkRow && F[e._atkRow] && has(e._atkRow) ? e._atkRow : 'attack', M = F[ar]; return [ar,",
         'recover')
sub_once("    case 'hurt': case 'reel': return ['hurt', F.hurt[Math.min(F.hurt.length - 1, Math.floor(t / 0.25 * F.hurt.length))]];\n"
         "    case 'grabbed': case 'stunned': case 'netted': case 'drowsy': case 'dazed': return ['hurt', F.hurt[F.hurt.length - 1]];",
         "    case 'hurt': case 'reel': { const body = F.deep && F.hurt2 && has('hurt2') && (e._hn || 0) % 2 === 0, H = body ? F.hurt2 : F.hurt;   // Version 85: head, then body\n"
         "      return [body ? 'hurt2' : 'hurt', H[Math.min(H.length - 1, Math.floor(t / 0.3 * H.length))]]; }\n"
         "    case 'grabbed': case 'netted': if (F.deep && has('held') && F.held) return ['held', F.held[Math.floor(time * 10) % F.held.length]];\n"
         "      return ['hurt', F.hurt[F.hurt.length - 1]];\n"
         "    case 'stunned': case 'drowsy': case 'dazed': if (F.deep && has('dazed') && F.dazed) return ['dazed', F.dazed[Math.floor(time * 9) % F.dazed.length]];\n"
         "      return ['hurt', F.hurt[F.hurt.length - 1]];",
         'hurt')
open(PAGE, 'w', encoding='utf-8').write(html)
print('v85 foes:', kinds)
