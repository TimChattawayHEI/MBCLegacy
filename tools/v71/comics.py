"""Version 71: the story's comic pages, painted in Meshy -> web/bg/comic/pages/<page>_<n>.png.
python3 tools/v71/comics.py --make [page ...]   (paint, 9 credits a panel; results kept in tools/v71/img)
python3 tools/v71/comics.py                      (cut them to size for the game)

A page is two or three panels the game lays out and slides in one at a time (tools/v71/v71.js, COMIC_PAGES, which
also holds the captions and speech: the game writes the words, so they're sharp and easy to change). The lads are
drawn from their intro card portraits (tools/v65/img/ladcard, the comic style) and their photo faces (tools/v65/img/ladref).
Layouts: 'L3' a tall 3:4 panel on the left and two 16:9 panels stacked on the right; 'L2' two 4:3 panels side by side;
'L1' one big 16:9 panel.
"""
import os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); V65 = os.path.join(ROOT, 'tools', 'v65', 'img')
WORK = os.environ.get('MESHY_WORK', '/tmp/meshy_work'); SRC = os.path.join(HERE, 'img'); OUT = os.path.join(ROOT, 'web', 'bg', 'comic', 'pages')
os.makedirs(SRC, exist_ok=True); os.makedirs(OUT, exist_ok=True)

STYLE = ("A single panel from a comic book telling the story of a retro beat 'em up video game, in exactly the bold comic-book style of the "
         "reference portraits: thick clean black ink outlines, flat cel shading with two or three tones per colour, strong rim light, rich colour, "
         "cinematic framing. No text, no letters, no speech bubbles, no captions, no panel border: the picture fills the whole frame. ")
WHO = {
    'tim': 'a bald man with a big ginger-brown beard and glasses in an olive green jacket',
    'seb': 'a powerfully built man with a very short light brown buzz cut and ginger-brown stubble, in an olive-grey short-sleeved shirt over a white T-shirt',
    'byron': 'a man with short brown hair and a beard in a grey jacket',
    'pearcy': 'a big broad bearded man in a loud orange Hawaiian shirt',
    'kelly': 'a slim young man with short brown hair in a red and white striped shirt',
    'marc': 'a man with black hair and a black beard in a black hoodie',
    'sam': 'a man with short fair hair in a navy tracksuit top',
}
# page -> (layout, [(aspect, lads in it, what's in the panel)])
PAGES = {
    'p1999': ('L3', [
        ('3:4', ['seb'], "Seb, {seb}, kneeling in a dusty loft lit by one bare bulb, lifting a pair of old DJ turntables and a home-made radio transmitter with a tall aerial out of a cardboard box, grinning, cobwebs, Christmas decorations, a box of old vinyl."),
        ('16:9', [], "Extreme close-up of a finger turning the glowing orange dial of an old radio transmitter to 104.1 FM, sparks jumping off the aerial, dust in the air."),
        ('16:9', ['seb'], "The loft dissolving into bright crackling TV static and electric light from the edges inwards, Seb silhouetted in the middle with his arms up, comic speed lines, the bulb exploding."),
    ]),
    'pmill': ('L2', [
        ('4:3', [], "Midnight on New Year's Eve 1999 over the rooftops of Bromley, south London: fireworks bursting over grey tower blocks and terraced houses, a pirate radio aerial on a flat roof in the foreground."),
        ('4:3', ['seb'], "Seb, {seb}, in a cramped flat with patterned wallpaper and a red ON AIR light, headphones round his neck, cranking the dial of a home-made radio transmitter, the room fizzing with static and blue sparks."),
    ]),
    'pelba': ('L2', [
        ('4:3', [], "A small white propeller plane landing on a sunny Mediterranean island runway, green mountains and turquoise sea behind, heat haze, August 2002."),
        ('4:3', ['tim', 'pearcy', 'kelly'], "Three British lads walking out of a small island airport into blazing sunshine with their suitcases, squinting, pale and happy: {tim}; {pearcy}; {kelly}. Palm trees and a taxi rank behind."),
    ]),
    'pespace': ('L2', [
        ('4:3', [], "A silver Renault Espace people carrier nose-down in a ditch beside a winding Italian country road at dusk, on fire, black smoke rising, cypress trees and a sunset sky, a hire car sticker on the back window."),
        ('4:3', ['sam'], "Sam, {sam}, standing on the left of the picture beside the burning people carrier at dusk, holding up the car keys, his face lit orange by the flames, puzzled, with his eyes wide open and clearly drawn (pupils, eyebrows raised), looking at the viewer. Open sky above his head."),
    ]),
    'p2006': ('L2', [
        ('4:3', ['byron'], "Byron, {byron}, standing alone under the big clock of a small suburban railway station entrance at night, October 2006, checking his watch, the clock reading five to nine, wet pavement, streetlights."),
        ('4:3', [], "A white and yellow commuter train pulling into a lit suburban platform at night, its doors about to open, the windows bright, a station sign, rain."),
    ]),
    'phome': ('L2', [
        ('4:3', ['marc'], "Sunrise over Bromley high street: Marc, {marc}, asleep sitting up in a bus shelter with half a kebab on his lap, a night bus pulling away in the background, pink and gold sky."),
        ('4:3', [], "A dark modern living room at night, a smartphone on a coffee table lighting up with a group chat full of messages, its glow the only light, a pint glass beside it."),
    ]),
    'pcarp': ('L3', [
        ('3:4', ['tim'], "Tim, {tim}, proudly standing beside a huge black barbecue smoker on a little trailer at the muddy gate of a Lincolnshire carp fishing lake, morning mist, tents and fishing rods behind."),
        ('16:9', [], "The wooden gate and big painted wooden sign reading DENISE'S FISHERY (those words only) of a carp fishing lake in the Lincolnshire countryside, reeds, a misty lake and willow trees behind, a battered estate car towing a black barbecue smoker through the gate."),
        ('16:9', [], "Underwater in a murky green lake: an enormous ancient carp with scarred golden scales and one huge eye, gliding beneath the shadows of fishing lines and floats far above."),
    ]),
    'pfire': ('L2', [
        ('4:3', [], "Midnight on a dark lake: an orange inflatable dinghy erupting in a huge fireball from a disposable barbecue on board, men diving off it into the water, sparks raining down, a caravan with lit windows on the far bank."),
        ('4:3', ['tim', 'seb'], "Dawn mist on a lake: two soot-blackened men standing up in the water only waist deep, looking sheepish, the burnt remains of a dinghy floating beside them: {tim}; {seb}."),
    ]),
    'pend': ('L1', [
        ('16:9', [], "Sunrise over a misty Lincolnshire carp lake: an enormous golden carp leaping clear out of the water, spray glittering, and on the bank a row of men in silhouette with their arms up, fishing rods and tents, a black smoker puffing smoke."),
    ]),
}


def make_panel(page, i):
    asp, lads, what = PAGES[page][1][i]
    refs = []
    for lad in lads[:2]:
        refs.append(os.path.join(V65, 'ladcard', lad + '.webp'))
        if os.path.exists(os.path.join(V65, 'ladref', lad + '.webp')): refs.append(os.path.join(V65, 'ladref', lad + '.webp'))
    if not refs: refs = [os.path.join(V65, 'ladcard', 'seb.webp'), os.path.join(V65, 'ladcard', 'pearcy.webp')]   # the style only
    prompt = STYLE + what.format(**WHO) + (" Draw each man exactly as in his reference pictures, the same face, hair, beard and clothes." if lads else " No people unless described.")
    name = f'{page}_{i}'
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'v64', 'meshy_free.py'), 'comic', name, prompt, ','.join(refs[:4])],
                       env=dict(os.environ, MESHY_WORK=WORK, ASPECT=asp), capture_output=True, text=True)
    raw = os.path.join(WORK, 'comic', name + '_raw.png')
    if not os.path.exists(raw): print('FAILED', name, r.stdout[-300:], r.stderr[-300:]); return
    Image.open(raw).save(os.path.join(SRC, name + '.webp'), quality=93, method=6); print('made', name, flush=True)


def trim(im):
    """Meshy sometimes draws its own white or black frame round a panel: cut off any plain border (up to 60 px a side)"""
    import numpy as np
    a = np.asarray(im).astype(np.float32); H_, W_ = a.shape[:2]
    plain = lambda v: (v.std() < 22 and (v.mean() > 205 or v.mean() < 28)) or (v.mean() < 14 and v.std() < 40)
    t = 0
    while t < 60 and plain(a[t]): t += 1
    b = H_
    while H_ - b < 60 and plain(a[b - 1]): b -= 1
    l = 0
    while l < 60 and plain(a[:, l]): l += 1
    r = W_
    while W_ - r < 60 and plain(a[:, r - 1]): r -= 1
    if (t, b, l, r) != (0, H_, 0, W_): t, b, l, r = t + 3 if t else 0, b - 3 if b < H_ else b, l + 3 if l else 0, r - 3 if r < W_ else r   # and the outline inside it
    return im.crop((l, t, r, b))


def cut():
    for page, (lay, panels) in PAGES.items():
        for i, (asp, _, _) in enumerate(panels):
            p = os.path.join(SRC, f'{page}_{i}.webp')
            if not os.path.exists(p): continue
            im = trim(Image.open(p).convert('RGB')); h = 300 if asp == '3:4' else 240
            im = im.resize((round(im.width * h / im.height), h), Image.LANCZOS)
            im.save(os.path.join(OUT, f'{page}_{i}.png'), optimize=True)
    print('cut', len(os.listdir(OUT)), 'panels')


if __name__ == '__main__':
    if '--make' in sys.argv:
        pages = [a for a in sys.argv[1:] if not a.startswith('--')] or list(PAGES)
        jobs = [(p, i) for p in pages for i in range(len(PAGES[p][1])) if not os.path.exists(os.path.join(SRC, f'{p}_{i}.webp'))]
        with ThreadPoolExecutor(8) as ex: list(ex.map(lambda a: make_panel(*a), jobs))
    cut()
