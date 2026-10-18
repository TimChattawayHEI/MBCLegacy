"""Seamless Nightlife backgrounds: python3 tools/v53/seams.py canvas <name> [...] | palette <key> <piece ...>

PixelLab can only paint what it can see, so a join between two background pieces is made by inpainting:
a canvas the height of the pieces, its left EDGE pixels copied from piece A's right end and its right EDGE pixels
from piece B's left end, the middle left for PixelLab to fill (mcp__PixelLab__inpaint_image, mask = the middle).
The result is saved as tools/v53/img/<name>.png and bg_process.py pastes A's and B's exact edge pixels back over
it, so in the game A, the join and B overlap by EDGE pixels and meet with no seam.

SEAMS lists every join: name -> (piece A, piece B, what goes in the middle). Pieces are the processed images in
web/bg/nightlife (signs repainted, bottoms cropped, tops padded), so all pieces of one stage share a height.
"""
import os, sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
BG = os.path.join(ROOT, 'web', 'bg', 'nightlife')
EDGE, W = 48, 256   # native pixels of each piece kept at either end of a join, and the join's width

SEAMS = {
    # Orpington: Station Approach -> into the ticket hall -> out through the gateline -> along the platform
    'st_j1': ('st_front', 'st_hall', 'the end of the brick station building at night: a lit glass entrance door with a canopy, the outside wall turning into the inside of the ticket hall, pale floor tiles continuing, no text'),
    'st_jh': ('st_hall', 'st_hall2', 'more of the inside of the ticket hall: a pale blue-grey wall with a square pillar, a noticeboard of posters, ceiling strip lights, the same pale floor tiles, no people, no text'),
    'st_j2': ('st_hall2', 'st_platform', 'the back of the ticket hall opening onto the open-air platform at night: a wide doorway out of the hall, a blue sign with a white arrow, the hall ceiling lights ending and the starry sky beginning, platform paving continuing, no people'),
    # Charing Cross: off the train -> the gateline -> the concourse -> the shops -> the way out
    'cx_j1': ('cx_platform', 'cx_hall', 'the end of the platforms under the glass roof: iron columns and the train buffers giving way to the station concourse wall, the same pale floor, no people, no text'),
    'cx_j2': ('cx_hall', 'cx_shops', 'more of the station concourse under the glass roof: an iron column, a bench and a bin, the same floor, no people, no text'),
    'cx_j3': ('cx_shops', 'cx_exit', 'the station concourse ending at the main entrance: tall arched stone doorway, night outside, the same floor, no people, no text'),
    # the smoking area: three stretches of the back of the bars
    'al_j1': ('alley', 'alley2', 'the back wall of London bars at night: brick wall, a drainpipe, a fire escape ladder, a wheelie bin, the same paving, no people, no text'),
    'al_j2': ('alley2', 'alley3', 'the back wall of London bars at night: brick wall, a steel back door, stacked beer crates, a wall lamp, the same paving, no people, no text'),
    'al_j3': ('alley3', 'alley', 'the back wall of London bars at night: brick wall, an air conditioning unit, a pile of bin bags, the same paving, no people, no text'),
}


def piece(k):
    return np.array(Image.open(os.path.join(BG, k + '.png')).convert('RGBA'))


def canvas(name):
    a, b, _ = SEAMS[name]; A, B = piece(a), piece(b)
    h = max(A.shape[0], B.shape[0])
    c = np.zeros((h, W, 4), np.uint8); c[..., 3] = 255
    c[h - A.shape[0]:, :EDGE] = A[:, -EDGE:]; c[h - B.shape[0]:, W - EDGE:] = B[:, :EDGE]
    c[:, EDGE:W - EDGE, :3] = 255   # white where PixelLab paints
    return c


# joins whose right-hand part PixelLab couldn't match (a darker sky than the platform's): from this column to the
# pasted edge, B's own first columns are laid in mirrored, so the join meets B exactly; the column is just past a wall
MIRROR = {'st_j2': 138}


def paste_edges(name, px):
    """put A's and B's exact edge pixels back over a finished join"""
    a, b, _ = SEAMS[name]; A, B = piece(a), piece(b)
    h = px.shape[0]
    px[h - A.shape[0]:, :EDGE] = A[:, -EDGE:]; px[h - B.shape[0]:, W - EDGE:] = B[:, :EDGE]
    if name in MIRROR:
        x0 = MIRROR[name]; n = W - EDGE - x0
        for i in range(n):   # column W-EDGE-1-i takes B's column i, folding back at B's far edge if needed
            k = i % (2 * B.shape[1]); k = k if k < B.shape[1] else 2 * B.shape[1] - 1 - k
            px[h - B.shape[0]:, W - EDGE - 1 - i] = B[:, k]
    return px


if __name__ == '__main__':
    out = sys.argv[2] if len(sys.argv) > 2 else '.'
    if sys.argv[1] == 'canvas':
        for n in sys.argv[3:] or SEAMS:
            c = canvas(n); Image.fromarray(c[..., :3], 'RGB').save(os.path.join(out, n + '_canvas.png'))
            print(n, c.shape[1], 'x', c.shape[0], 'mask x', EDGE, 'w', W - 2 * EDGE)
    elif sys.argv[1] == 'palette':
        # a small swatch image of every colour in some pieces (pixflux color_image)
        key, names = sys.argv[3], sys.argv[4:]
        cols = sorted({tuple(c) for n in names for c in piece(n)[..., :3].reshape(-1, 3)})
        side = int(np.ceil(np.sqrt(len(cols))))
        p = np.zeros((side, side, 3), np.uint8)
        for i, c in enumerate(cols): p[i // side, i % side] = c
        Image.fromarray(p, 'RGB').resize((side * 4, side * 4), Image.NEAREST).save(os.path.join(out, 'pal_' + key + '.png'))
        print(key, len(cols), 'colours')
