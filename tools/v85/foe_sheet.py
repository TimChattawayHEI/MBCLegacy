"""Version 85: enemies redrawn three-quarters on, with deeper animation sets (same pipeline as the lads).

python3 tools/v85/foe_sheet.py townie [parkie ...]

Reads tools/v85/src/<kind>/q_<anim>@<w>.png strips (cut from workbench joins), lines every animation up on its first
frame (each starts from the kind's own three-quarter stance), cleans stray specks, and writes web/sprites/<kind>.png
plus tools/v85/foes/<kind>.json: the SPRITE_META entry and the FOE_FRAMES picks.

Rows every kind gets: idle, walk, attack, hurt, knockdown (the old five, same names), then hurt2 (a body shot),
dazed (stunned, drowsy) and held (grabbed, netted). Optional rows per kind in FOES: attack2 (the second hit of a
combo2 foe), upper (the anti-air uppercut) and a boss's own moves (close, far, snatch, ball ...).
"""
import json, os, sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from sheetio import frames as read_frames, bbox  # noqa: E402
from lad_sheet import clean, hand, evenly  # noqa: E402

BASE = ['idle', 'walk', 'attack', 'hurt', 'knockdown', 'hurt2', 'dazed', 'held']
SRC = {'hurt': 'hurt_head', 'hurt2': 'hurt_body'}
LOOPS = ['idle', 'walk', 'dazed', 'held']
# per kind: extra rows (strikes), skips, hand-set picks, and FOE_FRAMES routing (wind/hits/loop) for its own states
FOES = {
    'townie': {'extra': ['attack2', 'upper'], 'skip': {'walk': [6, 7, 8], 'attack': [3], 'attack2': [7], 'upper': [5], 'hurt2': [2], 'knockdown': [4]},
               'frames': {'fall': [5, 6, 8, 10, 11]}},
    'parkie': {'extra': ['close', 'ball'], 'ownWeapon': True,
               'skip': {'hurt': [1], 'knockdown': [6]}, 'wind': {'ballWind': 'ball'},
               'frames': {'close': {'pre': [1, 2, 3], 'hit': 4, 'post': [6, 8]}, 'fall': [7, 8, 9, 10, 11], 'up': [15, 16, 17, 18, 19, 20]}},
}


GROUND = ('knockdown',)


def ground(row, f, ox, oy):
    """where a frame is drawn: on its row's frame-0 spot, except where the game lifts him itself (knocked flying,
    jumping), which would double the height. Those frames sit on the ground, and a knockdown is centred on his spot."""
    if row not in GROUND: return ox, oy
    b = bbox(f)
    return (-round((b[0] + b[2]) / 2) if row == 'knockdown' else ox), -(b[3] + 1)


PLAN = json.load(open(os.path.join(HERE, 'foes', 'PLAN.json')))
_OVR = os.path.join(HERE, 'foes', 'overrides.json')   # per-kind skips and hand picks, written as each kind is checked by eye
if os.path.exists(_OVR): FOES.update(json.load(open(_OVR)))
OLD = os.path.join(HERE, 'foes', 'old_frames.json')   # the side-on FOE_FRAMES and SPRITE_META, for each kind's own routing
OLD = json.load(open(OLD)) if os.path.exists(OLD) else {'FF': {}, 'SM': {}}
BASE5 = ['idle', 'walk', 'attack', 'hurt', 'knockdown']


def config(kind):
    """a kind's rows and routing: its own moves from the old sheet, a second punch for combo foes, an uppercut for anti-air
    foes, plus anything set by hand in FOES"""
    cfg = dict(FOES.get(kind, {})); p = PLAN.get(kind)
    if p and 'extra' not in cfg:
        ex = [r for r in OLD['SM'].get(kind, {}).get('rows', p['old_rows']) if r not in BASE5 and r not in BASE]
        if p['c2'] and 'attack2' not in ex: ex.append('attack2')
        if p['aa'] and 'upper' not in ex: ex.append('upper')
        cfg['extra'] = ex + cfg.get('more', [])
    if p and p['boss'] and 'base' not in cfg: cfg['base'] = [r for r in BASE if r != 'held']
    return cfg


def build(kind):
    cfg = config(kind); skip = cfg.get('skip', {})
    rows_list = cfg.get('base', BASE) + [r for r in cfg.get('extra', []) if r not in cfg.get('base', BASE)]
    src_dir = os.path.join(HERE, 'src', kind)
    raw = {}
    for row in rows_list:
        fr, _ = read_frames(os.path.join(src_dir, 'q_' + cfg.get('src', {}).get(row, SRC.get(row, row)) + '.png'))
        raw[row] = [clean(f) for f in fr]
    rb = bbox(raw['idle'][0]); ref_h = rb[3] - rb[1] + 1
    placed = {}; lo_x = lo_y = 10 ** 6; hi_x = hi_y = -10 ** 6
    for row, fr in raw.items():
        b0 = bbox(fr[0]); ox, oy = -round((b0[0] + b0[2]) / 2), -(b0[3] + 1)
        placed[row] = [(f, ox, oy) + ground(row, f, ox, oy) for f in fr]
        for f, _, _, dx, dy in placed[row]:
            b = bbox(f); lo_x = min(lo_x, b[0] + dx); hi_x = max(hi_x, b[2] + dx); lo_y = min(lo_y, b[1] + dy); hi_y = max(hi_y, b[3] + dy)
    span = max(hi_x - lo_x + 1, hi_y - lo_y + 1)
    cell = int(np.ceil((span + 4) / 4) * 4)
    ax = -lo_x + (cell - (hi_x - lo_x + 1)) // 2; ay = -lo_y + (cell - (hi_y - lo_y + 1))
    ncol = max(len(v) for v in placed.values())
    sheet = np.zeros((len(rows_list) * cell, ncol * cell, 4), np.uint8)
    rows, fist, info = {}, {}, {}
    for ri, row in enumerate(rows_list):
        fist[row] = []; info[row] = []
        for k, (f, ox, oy, dx, dy) in enumerate(placed[row]):
            ys, xs = np.where(f[..., 3] > 0)
            sheet[ri * cell + ys + dy + ay, k * cell + xs + dx + ax] = f[ys, xs]
            hx, hy = hand(f, -ox, row == 'knockdown')
            fist[row].append([int(hx + dx + ax), int(hy + dy + ay)])
            b = bbox(f); info[row].append({'reach': b[2] + ox, 'top': b[1] + oy, 'h': b[3] - b[1] + 1})
        rows[row] = [ri, len(placed[row])]
    Image.fromarray(sheet, 'RGBA').save(os.path.join(ROOT, 'web', 'sprites', kind + '.png'), optimize=True)
    meta = {'cell': cell, 'ax': float(ax), 'ay': int(ay), 'h': int(ref_h), 'rows': rows, 'fist': fist}
    F = picks(kind, info, skip, cfg, rows_list)
    os.makedirs(os.path.join(HERE, 'foes'), exist_ok=True)
    json.dump({'meta': meta, 'frames': F}, open(os.path.join(HERE, 'foes', kind + '.json'), 'w'), indent=1)
    print(kind, 'cell', cell, 'height', ref_h, {k: v[1] for k, v in rows.items()})


def strike(info, fr, n, up=False):
    cand = [i for i in fr if i <= max(2, int(n * 0.8))]
    if up: hit = min(cand, key=lambda i: info[i]['top'])            # an uppercut lands at the top
    else: hit = max(cand, key=lambda i: info[i]['reach'])           # anything else at full stretch
    pre = [i for i in fr if i < hit]
    post = [i for i in fr if i > hit]
    return {'pre': evenly(pre, 3) or [hit], 'hit': hit, 'post': evenly(post, 3)}


def picks(kind, info, skip, cfg, rows_list):
    ok = lambda row: [i for i in range(1, len(info[row])) if i not in skip.get(row, [])]
    F = {}
    for row in LOOPS:
        if row in rows_list: F[row] = ok(row)
    for row in rows_list:
        if row in LOOPS or row in ('hurt', 'hurt2', 'knockdown'): continue
        F[row] = strike(info[row], ok(row), len(info[row]), up=(row == 'upper'))
    F['hurt'] = ok('hurt'); F['hurt2'] = ok('hurt2')
    F['_all'] = {row: ok(row) for row in rows_list}   # for remapping an old loop onto the new frames
    kd = ok('knockdown'); hs = {i: info['knockdown'][i]['h'] for i in kd}; stand = info['knockdown'][0]['h']
    flat = [i for i in kd if hs[i] < stand * 0.45]
    if not flat:   # a bulky one lies taller than that: take the lowest run
        lo = min(hs.values()); flat = [i for i in kd if hs[i] <= lo * 1.15]
    F['fall'] = [i for i in kd if i < flat[0]] + [flat[0]]
    F['lie'] = flat[len(flat) // 2]
    F['up'] = [i for i in kd if i > flat[-1]]
    F['fallFlip'] = False
    for k in ('ownWeapon', 'wind', 'hits', 'loop', 'lean'):
        if k in cfg: F[k] = cfg[k]
    F.update(cfg.get('frames', {}))
    F['deep'] = 1
    return F


if __name__ == '__main__':
    for kind in sys.argv[1:]:
        build(kind)
