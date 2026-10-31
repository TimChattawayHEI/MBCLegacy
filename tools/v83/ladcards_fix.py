"""Version 83: Byron's and Kelly's card portraits repainted: python3 tools/v83/ladcards_fix.py [--make]

Tim (31 October): Byron's card looked like his cartoon game sprite, not the version made from his photo, and Kelly's was
far more pixelated than the other lads'. Same Meshy pipeline as tools/v65/ladcards.py (the card on the lad select, the
roster faces and the intro slam-in all use web/bg/ladcard/<lad>.png), with two changes: his photo-based face
(tools/v65/img/ladref/<lad>.webp) leads, and Tim's finished card goes in as the style to match (smooth comic art, not
pixel art). Kept in tools/v65/img/ladcard/ (the old ones are kept as <lad>_v65.webp)."""
import importlib.util, os, shutil, subprocess, sys
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); WORK = os.environ.get('MESHY_WORK', '/tmp/meshy_work')
spec = importlib.util.spec_from_file_location('lc', os.path.join(ROOT, 'tools', 'v65', 'ladcards.py')); lc = importlib.util.module_from_spec(spec); spec.loader.exec_module(lc)
SRC = os.path.join(ROOT, 'tools', 'v65', 'img', 'ladcard'); REF = os.path.join(ROOT, 'tools', 'v65', 'img', 'ladref')
WHO = {
    'byron': 'a man with short dark hair cut short at the sides and a clean-shaven face, in a grey jacket over a white T-shirt with a referee\'s whistle on a cord round his neck, and jeans',
    'kelly': 'a slim young man with short fair hair swept up at the front, in a striped shirt and jeans',
}


def make(lad, M):
    D = os.path.join(WORK, 'ladcard'); os.makedirs(D, exist_ok=True)
    lc.bc.CARDS[lad] = ([lad], WHO[lad]); rp = os.path.join(D, lad + '_sprite.png'); lc.bc.ref(lad, M).save(rp)
    refs = [os.path.join(REF, lad + '.webp'), rp, os.path.join(SRC, 'tim.webp')]
    prompt = (f"A hero introduction portrait for a beat 'em up video game of this exact man: {WHO[lad]}. "
              "His face, hair and expression exactly as in the first image (it's from his photo). His clothes and colours from the second image. "
              "Draw him in exactly the same art style as the third image: smooth bold comic-book art with thick clean black outlines, flat cel shading "
              "with two or three tones per colour, a golden rim light, normal adult proportions. NOT pixel art, no visible pixels, not chibi, not a big head. "
              "Waist up, three-quarter view turned to the right, fists up, confident grin, ready for a scrap. "
              "Plain flat dark blue background, nothing else in it. Only him. No text.")
    subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'v64', 'meshy_free.py'), 'ladcard', lad + '_v83', prompt, ','.join(refs)], check=True,
                   env=dict(os.environ, MESHY_WORK=WORK, ASPECT='1:1'))
    old = os.path.join(SRC, lad + '.webp'); keep = os.path.join(SRC, lad + '_v65.webp')
    if os.path.exists(old) and not os.path.exists(keep): shutil.copy(old, keep)
    Image.open(os.path.join(D, lad + '_v83_raw.png')).save(old, quality=94, method=6)


if __name__ == '__main__':
    lads = [k for k in sys.argv[1:] if not k.startswith('--')] or list(WHO)
    if '--make' in sys.argv:
        M = lc.bc.meta()
        for l in lads: make(l, M)
    lc.bc.SRC, lc.bc.OUT, lc.bc.CARD_H = SRC, lc.OUT, 150
    for l in lads: lc.bc.cut(l)
    print('cut', lads)
