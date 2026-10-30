"""Version 65: the lads' intro card portraits, painted in Meshy -> web/bg/ladcard/<lad>.png.  python3 tools/v65/ladcards.py [--make [lad ...]]

Like the boss cards (bosscards.py): waist up, three-quarter view, the same bold comic style, so picking a lad on the
select screen gets the same slam-in as a boss. References are the lad's own sprite (his outfit in the game) and, for
the seven from photos, his select portrait's Meshy original (tools/v65/img/ladref, his face). Cut out of the flat blue
and shrunk to 150 pixels tall (shown at up to twice that).
"""
import importlib.util, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); WORK = os.environ.get('MESHY_WORK', '/tmp/meshy_work')
spec = importlib.util.spec_from_file_location('bc', os.path.join(HERE, 'bosscards.py')); bc = importlib.util.module_from_spec(spec); spec.loader.exec_module(bc)
OUT = os.path.join(ROOT, 'web', 'bg', 'ladcard'); SRC = os.path.join(HERE, 'img', 'ladcard'); os.makedirs(OUT, exist_ok=True)
WHO = {
    'tim': 'a bald man with a big ginger-brown beard and glasses in an olive green jacket over a dark shirt, jeans',
    'seb': 'a muscular ex-army man with short reddish hair, a beard and dark sunglasses in a green army T-shirt and camouflage trousers',
    'byron': 'a man with short brown hair and a beard in a grey jacket and jeans, a football at his feet',
    'pearcy': 'a big, broad bearded man in a loud orange Hawaiian shirt with a flame pattern and khaki shorts',
    'kelly': 'a slim young man with short brown hair in a red and white striped shirt and jeans',
    'marc': 'a man with black hair and a black beard in a black hoodie and black jeans',
    'sam': 'a man with short fair hair in a navy tracksuit top and light grey trousers',
    'thet': 'a small, quick young man in camouflage gear with a red bandana tied round his head',
    'ash': 'a very tall slim man with ginger hair in a white shirt and beige trousers',
}


def make(lad, M):
    D = os.path.join(WORK, 'ladcard'); os.makedirs(D, exist_ok=True)
    bc.CARDS[lad] = ([lad], WHO[lad]); rp = os.path.join(D, lad + '_sprite.png'); bc.ref(lad, M).save(rp)
    refs = [rp]; face = os.path.join(HERE, 'img', 'ladref', lad + '.webp')
    if os.path.exists(face): refs.append(face)
    prompt = (f"A hero introduction portrait for a retro 16-bit beat 'em up video game of this exact man: {WHO[lad]}. "
              "Keep his look, clothes and colours from the first image" + (" and his face, hair and beard from the second image" if len(refs) > 1 else "") + ". "
              "Waist up, three-quarter view turned to the right, fists up, confident grin, ready for a scrap, larger than life. "
              "Bold comic-book style: thick clean black outlines, flat cel shading with two or three tones per colour, a strong golden rim light. "
              "Plain flat dark blue background, nothing else in it. Only him. No text.")
    subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'v64', 'meshy_free.py'), 'ladcard', lad, prompt, ','.join(refs)], check=True,
                   env=dict(os.environ, MESHY_WORK=WORK, ASPECT='1:1'))
    Image.open(os.path.join(D, lad + '_raw.png')).save(os.path.join(SRC, lad + '.webp'), quality=94, method=6)


if __name__ == '__main__':
    lads = [k for k in sys.argv[1:] if not k.startswith('--')] or list(WHO)
    if '--make' in sys.argv:
        M = bc.meta()
        with ThreadPoolExecutor(5) as ex: list(ex.map(lambda l: make(l, M), lads))
    bc.SRC, bc.OUT, bc.CARD_H = SRC, OUT, 150
    for l in lads:
        if os.path.exists(os.path.join(SRC, l + '.webp')): bc.cut(l)
