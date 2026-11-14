"""Version 85: the lads redrawn three-quarters on, with deeper animation sets.

python3 tools/v85/lad_sheet.py tim [seb ...]

Reads the PixelLab workbench sheets in tools/v85/src/<lad>/q_<anim>.png (`inspect character:<id>:east:q_<anim> --scale 2`),
lines every animation up on its first frame (each one starts from the same three-quarter stance), cleans stray specks
(hit sparks, a dropped pebble), and writes web/sprites/<lad>.png plus tools/v85/meta/<lad>.json: the SPRITE_META entry
and the LAD_FRAMES picks. Picks are worked out from the frames themselves (the hit is the frame reaching furthest
forward; the fall, lie and get-up come from how tall he stands), with per-lad overrides in LADS below.
"""
import json, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from sheetio import frames as read_frames, bbox  # noqa: E402

# sheet rows, in order. The first 17 are the rows every lad has always had (so old code keeps working); the rest are new.
ROWS = ['idle', 'walk', 'jab', 'hook', 'kick', 'jumpkick', 'hurt', 'knockdown', 'special', 'run', 'grab', 'knee', 'throw',
        'backkick', 'pickup', 'swing', 'mini', 'hurt2', 'jump', 'dazed', 'held', 'dash', 'victory', 'bat']
SRC = {'hook': 'cross', 'hurt': 'hurt_head', 'hurt2': 'hurt_body', 'backkick': 'kick'}
LOOPS = ['idle', 'walk', 'run', 'dazed', 'held']
STRIKES = ['jab', 'hook', 'kick', 'knee', 'swing', 'dash', 'throw', 'bat']

# per lad: frames to leave out (hit flashes, smears, turned-away frames), by row, and pick overrides
LADS = {
    'tim': {'skip': {'hurt': [1], 'hurt2': [1], 'knockdown': [1], 'swing': [3], 'kick': [4]},
            'frames': {'knee': {'pre': [1, 2], 'hit': 3, 'post': [5, 7, 8]}, 'bat': {'pre': [1, 3, 5], 'hit': 6, 'post': [5, 3]}}},
    'seb': {'skip': {'hurt': [1, 2], 'hurt2': [2], 'knockdown': [1], 'swing': [6], 'hook': [5]},
            'frames': {'knee': {'pre': [2, 3, 4], 'hit': 5, 'post': [6, 7, 8]}, 'mini': [1, 6, 12, 12, 11, 9, 10], 'bat': {'pre': [1, 3, 4], 'hit': 5, 'post': [4, 2]}}},
    'pearcy': {'skip': {'hook': [5], 'knockdown': [2], 'throw': [8], 'swing': [7, 8], 'dash': [2]},
               'frames': {'knee': {'pre': [2, 3, 4], 'hit': 5, 'post': [6, 7, 8]}}},
    'kelly': {'src': {'special': 'q_special2'}, 'skip': {'hook': [3, 6], 'knockdown': [2, 3], 'swing': [6], 'dash': [5]},
              'frames': {'knee': {'pre': [2, 3], 'hit': 4, 'post': [6, 7, 8]}, 'spHold': [2, 3, 4, 5, 6], 'spBlow': [9, 10, 11, 12, 12]}},
    'marc': {'skip': {'hurt': [1], 'knockdown': [2], 'swing': [6], 'bat': [5, 6]},
             'frames': {'knee': {'pre': [2, 3], 'hit': 4, 'post': [6, 7, 8]}, 'bat': {'pre': [1, 2, 3], 'hit': 4, 'post': [3, 2]}}},
    'sam': {'skip': {'hurt': [1], 'swing': [4], 'bat': [6, 7], 'knockdown': [4], 'dazed': [6, 7, 8], 'dash': [2]},
            'frames': {'knee': {'pre': [2, 3, 4], 'hit': 5, 'post': [6, 7, 8]}}},
    'thet': {'skip': {'hurt': [1], 'kick': [5], 'knockdown': [1, 2], 'swing': [4]},
             'frames': {'jab': {'pre': [1, 2], 'hit': 3, 'post': [4, 5, 7]}, 'hook': {'pre': [1, 2, 3], 'hit': 4, 'post': [6, 9, 10]},
                        'knee': {'pre': [2, 3, 4], 'hit': 5, 'post': [6, 7, 8]}, 'dash': {'pre': [2], 'hit': 3, 'post': [5, 6, 7]},
                        'kick': {'pre': [3, 4], 'hit': 6, 'post': [8, 9, 10]}, 'backkick': {'pre': [3, 4], 'hit': 6, 'post': [8, 9, 10]}}},
    'ash': {'skip': {'jab': [2], 'hook': [2], 'hurt': [1], 'hurt2': [1], 'knockdown': [1, 2, 3]},
            'frames': {'knee': {'pre': [1, 2, 3], 'hit': 4, 'post': [6, 7, 8]}, 'fall': [4, 5, 6, 8]}},
    'byron': {'skip': {'swing': [5], 'knockdown': [3], 'dash': [1]},
              'frames': {'knee': {'pre': [2, 3, 4], 'hit': 5, 'post': [6, 7, 8]}}},
}


def clean(f, min_keep=30):
    """drop small specks that aren't joined to the body (sparks, dust, a dropped pebble)"""
    a = f[..., 3] > 0
    lab, n = ndimage.label(a, structure=np.ones((3, 3)))
    if n <= 1: return f
    sizes = ndimage.sum(a, lab, range(1, n + 1)); big = sizes.max()
    out = f.copy()
    for i, s in enumerate(sizes, 1):
        if s < big and (s < min_keep or s < big * 0.12): out[lab == i] = 0
    return out


def is_skin(px):
    r, g, b, a = (int(v) for v in px)
    return a > 0 and r > 190 and 120 < g < 215 and 90 < b < 190 and r - b > 40 and r - g > 32   # not Ash's chinos


def hand(f, ax, low=False):
    """the frontmost fist: the frontmost lump of skin between the shoulders and the hips (to the floor when he's
    picking something up), so tan boots and skin-coloured smears on the legs don't count"""
    x0, y0, x1, y1 = bbox(f); h = y1 - y0
    ys, xs = np.where(f[..., 3] > 0)
    sk = np.zeros(f.shape[:2], bool)
    hi = y0 + h * (1.0 if low else 0.72)
    for y, x in zip(ys, xs):
        if y0 + h * 0.18 < y <= hi and is_skin(f[y, x]): sk[y, x] = True
    if sk.sum():
        lab, n = ndimage.label(sk, structure=np.ones((3, 3)))
        best = None
        for i in range(1, n + 1):
            yy, xx = np.where(lab == i)
            if len(xx) < 3: continue
            if best is None or xx.max() > best[0]: best = (xx.max(), yy[xx >= xx.max() - 1].mean())
        if best: return [int(best[0]), int(round(best[1]))]
    return [int(ax + 10), int(y0 + h * 0.45)]


def evenly(seq, n):
    if len(seq) <= n: return list(seq)
    return [seq[round(i * (len(seq) - 1) / (n - 1))] for i in range(n)]


GROUND = ('knockdown', 'jump', 'jumpkick')


def ground(row, f, ox, oy):
    """where a frame is drawn: on its row's frame-0 spot, except where the game lifts him itself (knocked flying,
    jumping), which would double the height. Those frames sit on the ground, and a knockdown is centred on his spot."""
    if row not in GROUND: return ox, oy
    b = bbox(f)
    return (-round((b[0] + b[2]) / 2) if row == 'knockdown' else ox), -(b[3] + 1)


def build(lad):
    cfg = LADS.get(lad, {}); skip = cfg.get('skip', {})
    src_dir = os.path.join(HERE, 'src', lad)
    raw = {}
    for row in ROWS:
        name = 'q_' + SRC.get(row, row)
        path = os.path.join(src_dir, cfg.get('src', {}).get(row, name) + '.png')
        fr, _ = read_frames(path)
        raw[row] = [clean(f) for f in fr]
    # the anchor: feet of the reference stance (frame 0 of idle)
    rb = bbox(raw['idle'][0]); ref_cx = (rb[0] + rb[2]) / 2; ref_bot = rb[3]; ref_h = rb[3] - rb[1] + 1
    placed = {}  # row -> list of (frame, ox, oy) in anchor space (anchor at 0,0 = feet centre)
    lo_x = lo_y = 10 ** 6; hi_x = hi_y = -10 ** 6
    for row, fr in raw.items():
        b0 = bbox(fr[0]); cx0 = (b0[0] + b0[2]) / 2
        ox, oy = -round(cx0), -(b0[3] + 1)          # this file's frame 0 lands on the anchor
        placed[row] = []
        for f in fr:
            dx, dy = ground(row, f, ox, oy)
            placed[row].append((f, ox, oy, dx, dy))
            b = bbox(f); lo_x = min(lo_x, b[0] + dx); hi_x = max(hi_x, b[2] + dx); lo_y = min(lo_y, b[1] + dy); hi_y = max(hi_y, b[3] + dy)
    span = max(hi_x - lo_x + 1, hi_y - lo_y + 1)
    cell = int(np.ceil((span + 4) / 4) * 4)
    ax = -lo_x + (cell - (hi_x - lo_x + 1)) // 2; ay = -lo_y + (cell - (hi_y - lo_y + 1))   # feet near the bottom
    ncol = max(len(v) for v in placed.values())
    sheet = np.zeros((len(ROWS) * cell, ncol * cell, 4), np.uint8)
    rows, fist, info = {}, {}, {}
    for ri, row in enumerate(ROWS):
        fist[row] = []; info[row] = []
        for k, (f, ox, oy, dx, dy) in enumerate(placed[row]):
            ys, xs = np.where(f[..., 3] > 0)
            ty, tx = ys + dy + ay, xs + dx + ax
            sheet[ri * cell + ty, k * cell + tx] = f[ys, xs]
            hx, hy = hand(f, -ox, row in ('pickup', 'knockdown', 'throw'))
            fist[row].append([int(hx + dx + ax), int(hy + dy + ay)])
            b = bbox(f); info[row].append({'reach': b[2] + ox, 'top': b[1] + oy, 'h': b[3] - b[1] + 1, 'w': b[2] - b[0] + 1})
        rows[row] = [ri, len(placed[row])]
    out_png = os.path.join(ROOT, 'web', 'sprites', lad + '.png')
    Image.fromarray(sheet, 'RGBA').save(out_png, optimize=True)
    meta = {'cell': cell, 'ax': float(ax), 'ay': int(ay), 'h': int(ref_h), 'rows': rows, 'fist': fist}
    F = picks(lad, info, skip, cfg)
    os.makedirs(os.path.join(HERE, 'meta'), exist_ok=True)
    json.dump({'meta': meta, 'frames': F}, open(os.path.join(HERE, 'meta', lad + '.json'), 'w'), indent=1)
    print(lad, 'cell', cell, 'anchor', ax, ay, 'height', ref_h, {k: v[1] for k, v in rows.items()})
    return meta, F


def picks(lad, info, skip, cfg):
    ok = lambda row: [i for i in range(1, len(info[row])) if i not in skip.get(row, [])]
    F = {}
    for row in LOOPS:
        F[row] = ok(row)
    for row in STRIKES:
        fr = ok(row); n = len(info[row])
        cand = [i for i in fr if i <= max(2, int(n * 0.8))]
        hit = max(cand, key=lambda i: info[row][i]['reach'])
        pre = [i for i in fr if i < hit]; hr = info[row][hit]['reach']; last = hit
        for i in fr:
            if i > last and i == next((j for j in fr if j > last), None) and info[row][i]['reach'] >= hr - 4: last = i
        post = [i for i in fr if i > last]
        # after the hit, keep the frames until he's back in his guard
        F[row] = {'pre': evenly(pre, 3), 'hit': hit, 'post': evenly(post, 3)}
    # knockdown: falling until he's flat, lying, then getting up
    kd = ok('knockdown'); hs = {i: info['knockdown'][i]['h'] for i in kd}; stand = info['knockdown'][0]['h']
    flat = [i for i in kd if hs[i] < stand * 0.45]
    first_flat, last_flat = flat[0], flat[-1]
    F['fall'] = [i for i in kd if i < first_flat] + [first_flat]
    F['lie'] = flat[len(flat) // 2]
    F['up'] = [i for i in kd if i > last_flat]
    # jumping: the jump row's lowest frames at either end are the crouches, the middle ones the air
    jp = ok('jump'); jh = {i: info['jump'][i]['top'] for i in jp}
    air = sorted(jp, key=lambda i: jh[i])[:max(3, len(jp) // 3)]
    air.sort()
    F['crouch'] = ['jump', jp[0]]
    F['land'] = [i for i in jp if i > air[-1]][:3] or [jp[-1]]
    F['rise'] = [i for i in jp if i < air[0]][-2:] or [air[0]]
    F['apex'] = air
    F['tuck'] = ['jump', air[len(air) // 2]]
    jk = ok('jumpkick'); jhit = max(jk, key=lambda i: info['jumpkick'][i]['reach'])
    F['air'] = ['jumpkick', jhit]
    F['jk'] = [i for i in jk if i <= jhit] + [i for i in jk if i > jhit and info['jumpkick'][i]['reach'] >= info['jumpkick'][jhit]['reach'] - 3]
    F['hurt'] = ok('hurt'); F['hurt2'] = ok('hurt2')
    F['special'] = ok('special'); F['mini'] = ok('mini'); F['victory'] = ok('victory')
    gr = ok('grab'); F['grab'] = gr[len(gr) // 3:] or gr
    pk = ok('pickup'); low = min(pk, key=lambda i: info['pickup'][i]['h'])
    F['pickup'] = [i for i in pk if i <= low][-3:]
    F['backkick'] = F['kick']; F['fallFlip'] = False
    F.update(cfg.get('frames', {}))
    return F


if __name__ == '__main__':
    for lad in sys.argv[1:] or ['tim']:
        build(lad)
