"""Version 65: boss intro card portraits painted in Meshy -> web/bg/bosscard/<key>.png.  python3 tools/v65/bosscards.py [--make [key ...]]

Each boss's own sprite (idle frame, or the group side by side) is the reference for one Meshy image-to-image portrait
(nano-banana-pro, 1:1, 9 credits) in the same bold comic style as the lads' select portraits, on flat dark blue. The
result is kept as tools/v65/img/bosscard/<key>.webp; without --make each is cut out (the blue flood-filled away from the
edges) and shrunk to CARD_H native pixels tall for the intro card (drawn at 2x, bursting up out of the band).
"""
import json, os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
WEB = os.path.join(ROOT, 'web'); OUT = os.path.join(WEB, 'bg', 'bosscard'); os.makedirs(OUT, exist_ok=True)
SRC = os.path.join(HERE, 'img', 'bosscard'); WORK = os.environ.get('MESHY_WORK', '/tmp/meshy_work')
CARD_H = 118
# key: (sprites, who they are)
CARDS = {
    'parkie': (['parkie'], 'an old park keeper in a council uniform: a flat cap, a grey beard, a dark green jacket with a high-vis strip, holding a litter picker like a weapon'),
    'mc': (['mc'], 'a pirate radio DJ: big studio headphones round his neck, dark sunglasses, a black tracksuit and gold chain, holding a microphone'),
    'denise': (['denise'], 'a formidable older woman who owns a fishing lake and its bar: short grey hair, a dark green fleece, arms folded, a stare that could stop a clock'),
    'lady': (['lady'], 'a loud female radio DJ: long blonde hair, a leopard print jacket, pink and purple clothes, big hoop earrings, holding a vinyl record'),
    'mafioso': (['mafioso'], 'an Italian mafia don on holiday: slicked back black hair, dark sunglasses, a cream linen suit with an open collar, a gold ring'),
    'duo': (['beast', 'quick'], 'two club bouncers side by side: on the left a huge bald man with a black beard in a tight black T-shirt, and on the right a skinny wiry man with slicked hair in a red leather jacket'),
    'carab': (['carab'], 'an Italian carabiniere police officer: a black peaked cap, a black uniform with red stripes and white belt, a bushy moustache'),
    'bros': (['gianni', 'marco', 'luca', 'paolo'], 'four young Italian brothers standing together: one in a black T-shirt, one with a ponytail in a white vest, one in a red polo shirt with sunglasses, one in a blue tracksuit'),
    'inspector': (['inspector'], 'a London train ticket inspector: a peaked cap, a dark uniform with a yellow high-vis vest, a moustache, holding a ticket machine'),
    'lenny': (['lenny'], 'a big south London hard man: a black puffer jacket zipped up over his chin, a shaved head, a cold stare'),
    'jeweller': (['jeweller'], 'a shady man who sells stolen watches: a cream jacket open over a shirt, slicked back hair, both wrists covered in gold watches'),
    'farbank': (['farbank', 'farbank'], 'two grumpy carp anglers side by side: big men in camouflage jackets and black beanie hats, with thick beards'),
    'nozzer': (['nozzer'], 'an old man who never stops talking: white hair, glasses, a beige anorak, holding a pint'),
    'gary': (['fish/gary'], 'an enormous angry golden-orange carp leaping out of the water, scales gleaming, mouth wide open'),
    'gaz': (['fish/gaz'], 'a huge crimson carp with a black baseball cap on backwards and a thick gold chain, snarling, leaping out of the water'),
}


def meta():
    s = open(os.path.join(WEB, 'index.html')).read(); i = s.index('const SPRITE_META = {'); j = s.index('\n', i)
    line = re.sub(r'/\*.*?\*/', '', s[i + len('const SPRITE_META = '):j].rstrip(';')); return json.loads(line[:line.rfind('}') + 1])


def ref(key, M):
    ims = []
    for sp in CARDS[key][0]:
        if '/' in sp: im = Image.open(os.path.join(WEB, 'bg', sp + '.png')).convert('RGBA')
        else:
            m = M[sp]; c = m['cell']; r = m['rows']['idle'][0]; im = Image.open(os.path.join(WEB, 'sprites', sp + '.png')).convert('RGBA').crop((0, r * c, c, (r + 1) * c))
        bb = im.getbbox(); ims.append(im.crop(bb))
    h = max(i.height for i in ims); k = 640 // h
    w = sum(i.width * k for i in ims) + 40 * (len(ims) - 1)
    out = Image.new('RGB', (max(w, 640) + 80, 640 + 80), (60, 64, 72)); x = (out.width - w) // 2
    for i in ims:
        big = i.resize((i.width * k, i.height * k), Image.NEAREST); out.paste(big, (x, 40 + 640 - big.height), big); x += big.width + 40
    return out


def make(key, M):
    D = os.path.join(WORK, 'bosscard'); os.makedirs(D, exist_ok=True); rp = os.path.join(D, key + '_ref.png'); ref(key, M).save(rp)
    many = len(CARDS[key][0]) > 1
    prompt = (f"A boss introduction portrait for a retro 16-bit beat 'em up video game of {'these exact characters' if many else 'this exact character'}: {CARDS[key][1]}. "
              f"Keep {'their' if many else 'his or her'} look, face, hair and clothes from the reference. Waist up, three-quarter view turned to the right, menacing and larger than life, "
              "ready for a fight. Bold comic-book style: thick clean black outlines, flat cel shading with two or three tones per colour, a strong orange rim light. "
              "Plain flat dark blue background, nothing else in it. No text.")
    env = dict(os.environ, MESHY_WORK=WORK, ASPECT='1:1')
    subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'v64', 'meshy_free.py'), 'bosscard', key, prompt, rp], check=True, env=env)
    Image.open(os.path.join(D, key + '_raw.png')).save(os.path.join(SRC, key + '.webp'), quality=94, method=6)


def cut(key):
    im = np.asarray(Image.open(os.path.join(SRC, key + '.webp')).convert('RGB')).astype(int); h, w, _ = im.shape
    bg = np.median(np.concatenate([im[0], im[-1], im[:, 0], im[:, -1]]), 0)
    near = np.abs(im - bg).sum(2) < 70
    keep = np.ones((h, w), bool); st = [(y, x) for y in (0, h - 1) for x in range(w)] + [(y, x) for x in (0, w - 1) for y in range(h)]
    seen = np.zeros((h, w), bool)
    while st:
        y, x = st.pop()
        if y < 0 or x < 0 or y >= h or x >= w or seen[y, x] or not near[y, x]: continue
        seen[y, x] = True; keep[y, x] = False; st += [(y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)]
    a = Image.fromarray(np.dstack([im, keep * 255]).astype(np.uint8), 'RGBA'); a = a.crop(a.getbbox())
    a = a.resize((round(a.width * CARD_H / a.height), CARD_H), Image.LANCZOS)
    arr = np.asarray(a).copy(); arr[..., 3] = np.where(arr[..., 3] > 128, 255, 0); Image.fromarray(arr).save(os.path.join(OUT, key + '.png')); print(key, a.size)


if __name__ == '__main__':
    keys = [k for k in sys.argv[1:] if not k.startswith('--')] or list(CARDS)
    if '--make' in sys.argv:
        M = meta()
        with ThreadPoolExecutor(5) as ex: list(ex.map(lambda k: make(k, M), keys))
    for k in keys:
        if os.path.exists(os.path.join(SRC, k + '.webp')): cut(k)
