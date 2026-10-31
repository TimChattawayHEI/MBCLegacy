"""Orpington 2001's comic pages, painted in Meshy the way tools/v71/comics.py paints the story's (it does the work):
python3 tools/v73/comics.py --make [page ...]   (paint, 9 credits a panel; kept in tools/v71/img with the rest)
python3 tools/v73/comics.py                      (cut every page to size for the game, web/bg/comic/pages/)
Captions and speech are in COMIC_PAGES in tools/v73/orp2001.js."""
import importlib.util, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
spec = importlib.util.spec_from_file_location('c71', os.path.join(ROOT, 'tools', 'v71', 'comics.py'))
c71 = importlib.util.module_from_spec(spec); spec.loader.exec_module(c71)
from concurrent.futures import ThreadPoolExecutor

SUE = 'a landlady in her fifties with short spiky blonde hair going grey, heavy eye make-up, big gold hoop earrings and a leopard-print blouse'
MICK = 'a huge fat old bald pub landlord with a white beard, a white short-sleeved shirt and black braces'
ALAN = 'a thin scruffy young man with messy blond hair, unshaven, in a grey hoodie'
JEFF = 'a huge heavy young man with short dark hair in a dirty stretched navy polo shirt'
PAGES = {
    'p2001': ('L2', [
        ('4:3', [], "Orpington High Street, south east London, on a cold night in March 2001: a red brick corner restaurant with a round navy blue sign, a London bus stop with its red and white flag, a red double-decker bus pulling away, wet pavement shining under orange street lamps, little shops with their shutters down."),
        ('4:3', ['byron', 'kelly'], "Two lads waiting at a London bus stop at night, both texting on small chunky old grey Nokia mobile phones with little green-lit screens, their breath misting in the cold: {byron}; {kelly}."),
    ]),
    'pspill': ('L2', [
        ('4:3', [], f"Inside an old English pub: the landlady, {SUE}, glaring over the wooden bar with narrowed eyes while pulling a pint of lager, horse brasses and bottles behind her, warm amber light."),
        ('4:3', [], f"In a dim old pub with horseshoes and a cart wheel on the walls: {ALAN}, drunk and stumbling, spilling a full pint of lager all down the back of {JEFF}, who is turning round, furious, beer flying through the air."),
    ]),
    'pmick': ('L1', [
        ('16:9', [], f"Behind the wooden bar of an old English pub, {MICK} ringing a big brass bell on a bracket with one meaty hand and pointing straight at us with the other, shouting, red in the face, the landlady with short spiky blonde hair beside him with her arms folded, horse brasses, optics and bottles behind them, a pub full of men turning round."),
    ]),
    'pdoor': ('L2', [
        ('4:3', ['kelly'], "Outside a big nightclub at night with a navy and gold sign reading ATLANTIS (that word only): two huge bouncers in black bomber jackets blocking a lad at the red rope with their hands up, purple light from the doorway, a long queue of clubbers along the wall behind: {kelly}."),
        ('4:3', ['kelly'], "A lad sitting alone on an empty coach at night in a dark car park, his cheek pressed against the window, bored stiff, while the coach driver has turned round in his seat to talk at him: {kelly}."),
    ]),
    'p2am': ('L1', [
        ('16:9', ['tim', 'marc'], "2am outside a nightclub in Croydon: a gang of sweaty, happy lads stumbling out under a white wave-shaped steel canopy into the cold night, arms round each other, a coach waiting at the kerb with its door open, Croydon's tower blocks behind: {tim}; {marc}."),
    ]),
}

if __name__ == '__main__':
    c71.PAGES.update(PAGES)
    if '--make' in sys.argv:
        pages = [a for a in sys.argv[1:] if not a.startswith('--')] or list(PAGES)
        jobs = [(p, i) for p in pages for i in range(len(PAGES[p][1])) if not os.path.exists(os.path.join(c71.SRC, f'{p}_{i}.webp'))]
        with ThreadPoolExecutor(8) as ex: list(ex.map(lambda a: c71.make_panel(*a), jobs))
    c71.cut()
