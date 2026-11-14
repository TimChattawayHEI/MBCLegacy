"""Version 85: deeper animation for the lads, redrawn three-quarters on.

python3 tools/v85_build.py            (re-runnable; patches web/index.html in place, like V66 onwards)

- Every lad in tools/v85/meta/<lad>.json (built by tools/v85/lad_sheet.py) gets its SPRITE_META and LAD_FRAMES entry
  replaced between the /* v85 lads */ markers, after the Version 41 mini picks.
- ladFrame learns the new rows: a proper jump (crouch, rise, hang, fall, land), the flying kick played through, two
  hurts (head and body, alternating), a dazed loop (dazed, stunned, drowsy), a struggle when held, the dash attack,
  a longer idle and walk, and a victory pose when a stage is won. Lads without the new rows draw as before.
"""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PAGE = os.path.join(ROOT, 'web', 'index.html')
META = os.path.join(HERE, 'v85', 'meta')

html = open(PAGE, encoding='utf-8').read()


def sub_once(old, new, label):
    global html
    if new in html: return
    if old not in html: sys.exit('v85: anchor not found: ' + label)
    html = html.replace(old, new, 1)


# 1. the sheets' meta and frame picks
lads = sorted(f[:-5] for f in os.listdir(META) if f.endswith('.json'))
metas, frames = {}, {}
for lad in lads:
    d = json.load(open(os.path.join(META, lad + '.json')))
    metas[lad] = d['meta']; F = d['frames']; F['deep'] = 1; frames[lad] = F
block = ('/* v85 lads */ Object.assign(SPRITE_META, ' + json.dumps(metas, separators=(',', ':')) + ');\n'
         'for (const [k, v] of Object.entries(' + json.dumps(frames, separators=(',', ':')) + ')) LAD_FRAMES[k] = Object.assign({}, LAD_FRAMES[k] || {}, v);\n'
         'if (typeof V85_FIX === "function") V85_FIX();\n/* v85 lads end */')
anchor = 'Object.assign(LAD_FRAMES.sam, { mini: [1, 2, 3, 4, 5, 6, 7] });'
if '/* v85 lads */' in html:
    html = re.sub(r'/\* v85 lads \*/.*?/\* v85 lads end \*/', lambda m: block, html, flags=re.S)
else:
    sub_once(anchor, anchor + '\n' + block, 'mini picks')

# 2. ladFrame
sub_once("  const walkIdx = () => LAD_WALK[((Math.floor((e.walk || 0) / (Math.PI * 2) * 8) % 8) + 8) % 8];",
         "  const walkIdx = () => { const wl = (F.deep && F.walk) || LAD_WALK, n = wl.length; return wl[((Math.floor((e.walk || 0) / (Math.PI * 2) * n) % n) + n) % n]; };",
         'walkIdx')
if "has('bat')) return ['bat', hitOf(F.bat)]" not in html:
    sub_once("    case 'dash': return e.weapon && has('swing') ? ['swing', hitOf(F.swing)] : ['hook', hitOf(F.hook)];",
             "    case 'dash': if (F.deep && !e.weapon && has('dash')) return ['dash', moveFrame(F.dash, t, 0.03, 0.26, 0.42)];\n"
             "      return e.weapon && has('swing') ? ['swing', hitOf(F.swing)] : ['hook', hitOf(F.hook)];",
             'dash')
V85_DASH1 = "    case 'dash': if (F.deep && !e.weapon && has('dash')) return ['dash', moveFrame(F.dash, t, 0.03, 0.26, 0.42)];"
V85_DASH2 = ("    case 'dash': if (F.deep && e.weapon && has('bat')) return ['bat', hitOf(F.bat)];   // with a weapon: the swing's hit, held\n"
             "      if (F.deep && !e.weapon && has('dash')) return ['dash', moveFrame(F.dash, t, 0.03, 0.26, 0.42)];")
if V85_DASH2 not in html: html = html.replace(V85_DASH1, V85_DASH2, 1)
sub_once("    case 'swing': if (has('swing')) return ['swing', moveFrame(F.swing,",
         "    case 'swing': if (F.deep && e.weapon && has('bat')) return ['bat', moveFrame(F.bat, e.atkT || 0, k ? k.t0 : 0.06, k ? k.t1 : 0.15, e.actDur || 0.3)];   // Version 85: a two-handed swing for weapons\n"
         "      if (has('swing')) return ['swing', moveFrame(F.swing,",
         'swing with a weapon')
sub_once("    case 'squat': case 'land': return F.crouch;\n    case 'jump': return e.airAtk && (e.atkT || 0) < 0.34 ? F.air : F.tuck;",
         "    case 'squat': return F.crouch;\n"
         "    case 'land': if (F.deep && F.land) return ['jump', F.land[Math.min(F.land.length - 1, Math.floor(t / 0.2 * F.land.length))]]; return F.crouch;\n"
         "    case 'jump': {\n"
         "      if (F.deep && F.jk && e.airAtk) { const a = e.atkT || 0; if (a < 0.34) return ['jumpkick', F.jk[Math.min(F.jk.length - 1, Math.floor(a / 0.22 * F.jk.length))]]; }\n"
         "      else if (e.airAtk && (e.atkT || 0) < 0.34) return F.air;\n"
         "      if (F.deep && F.apex) { const vz = e.vz || 0;   // Version 85: up, hang, down\n"
         "        if (vz > 260 && F.rise) return ['jump', F.rise[Math.min(F.rise.length - 1, Math.floor(t / 0.1 * F.rise.length))]];\n"
         "        const k = clamp((260 - vz) / 900, 0, 0.999); return ['jump', F.apex[Math.floor(k * F.apex.length)]]; }\n"
         "      return F.tuck;\n    }",
         'jump')
sub_once("    case 'hurt': return ['hurt', F.hurt[Math.min(F.hurt.length - 1, Math.floor(t / 0.3 * F.hurt.length))]];\n"
         "    case 'drowsy': case 'netted': case 'grabbed': case 'stunned': return ['hurt', F.hurt[F.hurt.length - 1]];",
         "    case 'hurt': { const body = F.deep && F.hurt2 && has('hurt2') && (e.hurtN || 0) % 2, H = body ? F.hurt2 : F.hurt;   // Version 85: head, then body\n"
         "      return [body ? 'hurt2' : 'hurt', H[Math.min(H.length - 1, Math.floor(t / 0.34 * H.length))]]; }\n"
         "    case 'drowsy': case 'stunned': case 'dazed': if (F.deep && has('dazed')) return ['dazed', F.dazed[Math.floor(time * 9) % F.dazed.length]];\n"
         "      return ['hurt', F.hurt[F.hurt.length - 1]];\n"
         "    case 'netted': case 'grabbed': if (F.deep && has('held')) return ['held', F.held[Math.floor(time * 10) % F.held.length]];\n"
         "      return ['hurt', F.hurt[F.hurt.length - 1]];",
         'hurt')
sub_once("  return ['idle', LAD_IDLE[Math.floor(time * 7) % LAD_IDLE.length]];\n}",
         "  if (F.deep && F.victory && has('victory') && S && S.done && mode === 'play' && !e.ally && !e.friend) {   // Version 85: the stage is won\n"
         "    if (!V85_VIC.has(e)) V85_VIC.set(e, time); const vt = time - V85_VIC.get(e);\n"
         "    return ['victory', F.victory[Math.min(F.victory.length - 1, Math.floor(vt * 11))]];\n  }\n"
         "  if (V85_VIC.size && !(S && S.done)) V85_VIC.clear();\n"
         "  if (F.deep && F.idle) return ['idle', F.idle[Math.floor((time + (e.x || 0) * 0.007) * 8) % F.idle.length]];\n"
         "  return ['idle', LAD_IDLE[Math.floor(time * 7) % LAD_IDLE.length]];\n}\nconst V85_VIC = new Map();",
         'idle')
# 3. count hits so the hurt alternates between head and body
sub_once("  else { p.state = 'hurt'; p.t = 0; p.vx = dir * (k.kb || 120); p.vy = 0; }",
         "  else { p.state = 'hurt'; p.t = 0; p.vx = dir * (k.kb || 120); p.vy = 0; p.hurtN = (p.hurtN || 0) + 1; }",
         'hurtPlayer')
sub_once("  } else { t.state = 'hurt'; t.t = 0; t.vx = dir * (k.kb || 90); t.vy = 0; }\n}",
         "  } else { t.state = 'hurt'; t.t = 0; t.vx = dir * (k.kb || 90); t.vy = 0; t.hurtN = (t.hurtN || 0) + 1; }\n}",
         'hurt ally')
# 4. Ash's GINGER SNAP: the new sheet draws the spin itself, so stop flipping him back and forth on top of it
SPIN1 = "  if (m.spin && !(LAD_FRAMES[p.def.id] || {}).deep) {\n    if (t > m.spin[0]"
SPIN2 = "  if (m.spin && !(p.def.id === 'ash' && (LAD_FRAMES.ash || {}).deep)) {\n    if (t > m.spin[0]"   # Kelly's BMX 360 still flips
if SPIN1 in html: html = html.replace(SPIN1, SPIN2, 1)
sub_once("  if (m.spin) {\n    if (t > m.spin[0]", SPIN2, 'mini spin')

# 5. Kelly's MASS HEAD: the head box is the run of pixels through the middle of his head, not a hand or arm beside it
sub_once("    for (let y = top; y < Math.min(m.cell, top + hh); y++) for (let x = 0; x < m.cell; x++) if (d[(y * m.cell + x) * 4 + 3] > 40) { if (x < x0) x0 = x; if (x > x1) x1 = x; }",
         "    const op = (x, y) => x >= 0 && x < m.cell && d[(y * m.cell + x) * 4 + 3] > 40, cx = Math.round(hx);   // Version 85\n"
         "    for (let y = top; y < Math.min(m.cell, top + hh); y++) { if (!op(cx, y)) continue; let a = cx, b = cx; while (a > cx - 9 && op(a - 1, y)) a--; while (b < cx + 9 && op(b + 1, y)) b++; if (a < x0) x0 = a; if (b > x1) x1 = b; }",
         'head box')

# 6. combo swooshes fitted to the new art: where each hit frame's fist or foot actually is
sys.path.insert(0, os.path.join(HERE, 'v85'))
import numpy as np
from PIL import Image
from strike import strike, world, cell
COMBO_ANIMS = {'tim': ['jab', 'hook', 'kick'], 'marc': ['jab', 'hook', 'kick'], 'byron': ['jab', 'hook', 'kick'], 'thet': ['jab', 'hook', 'kick'],
               'seb': ['hook', 'kick'], 'pearcy': ['hook', 'kick'], 'kelly': ['jab', 'hook', 'knee'], 'sam': ['jab', 'hook', 'swing'], 'ash': ['jab', 'hook', 'kick']}
USE = {'ash': {'jab': 'kick', 'hook': 'round'}, 'thet': {'hook': 'upper'}}
KIND = {'jab': 'punch', 'hook': 'punch', 'swing': 'punch', 'kick': 'kick', 'round': 'kick', 'knee': 'knee', 'upper': 'upper'}
OFF = {'jab': (6, 2), 'hook': (6, 2), 'swing': (12, 4), 'kick': (2, 4), 'round': (2, 4), 'knee': (10, 18), 'upper': (0, 8)}   # where Tim's old trails ended, past his fist or foot
fits = {}
for lad in lads:
    M, F = metas[lad], frames[lad]
    sheet = np.array(Image.open(os.path.join(ROOT, 'web', 'sprites', lad + '.png')).convert('RGBA'))
    fit = {'s': round(M['h'] / 62, 2)}
    if lad in USE: fit['use'] = USE[lad]
    for an in COMBO_ANIMS.get(lad, []):
        shape = USE.get(lad, {}).get(an, an)
        p = world(M, strike(cell(sheet, M, an, F[an]['hit']), KIND[shape])); o = OFF[shape]
        fit[an] = [p[0] + o[0], p[1] + o[1]]
    fits[lad] = fit
sw = ('/* v85 swoosh */ SWOOSH.upper = { p: [[4, 30], [40, 52], [24, 112]], w: 20 };   // Thet\'s jumping uppercut\n'
      'Object.assign(SW_FIT, ' + json.dumps(fits, separators=(',', ':')) + ');\n/* v85 swoosh end */\n')
if '/* v85 swoosh */' in html:
    html = re.sub(r'/\* v85 swoosh \*/.*?/\* v85 swoosh end \*/\n', lambda m: sw, html, flags=re.S)
else:
    sub_once('function swKey(p) {', sw + 'function swKey(p) {', 'swoosh fit')
print('v85: swooshes', fits)

open(PAGE, 'w', encoding='utf-8').write(html)
print('v85: lads', lads)
