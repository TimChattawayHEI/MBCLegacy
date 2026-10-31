"""Boss intro card portraits for Orpington 2001 (Alan, Jeff, Mick), painted the way tools/v65/bosscards.py paints the others
(it does the work; their own PixelLab sprites are the references): python3 tools/v74/bosscards.py [--make]
Kept in tools/v65/img/bosscard/, cut to web/bg/bosscard/<key>.png. The game finds them through BOSS_ART (tools/v73/orp2001.js)."""
import importlib.util, os, sys
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
spec = importlib.util.spec_from_file_location('b65', os.path.join(ROOT, 'tools', 'v65', 'bosscards.py'))
b65 = importlib.util.module_from_spec(spec); spec.loader.exec_module(b65)
NEW = {
    'alan': (['alan'], 'a thin, scruffy, wasted young man in a grey hoodie and ripped jeans, messy blond hair, unshaven, glassy eyes, swaying, fists up'),
    'jeff': (['jeff'], 'a huge heavy young man in a dirty, stretched navy polo shirt and combat trousers, short dark hair, thick tattooed arms, furious'),
    'mick': (['mick'], 'a huge fat old East End pub landlord: bald on top with white hair at the sides and a big white beard, a white short-sleeved shirt and black braces, tattooed forearms, a bar towel over his shoulder. He has exactly two arms: his left arm hangs by his side and his right fist is clenched in front of his belly; no extra arms or hands anywhere'),
}
b65.CARDS.update(NEW)
if __name__ == '__main__':
    if '--make' in sys.argv:
        M = b65.meta()
        with ThreadPoolExecutor(3) as ex: list(ex.map(lambda k: b65.make(k, M), [k for k in NEW if not os.path.exists(os.path.join(b65.SRC, k + '.webp'))]))
    for k in NEW:
        if os.path.exists(os.path.join(b65.SRC, k + '.webp')): b65.cut(k)
