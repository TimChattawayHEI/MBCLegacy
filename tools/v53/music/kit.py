"""Instruments and helpers from songs.py, songs2.py and songs3.py (the Project's soundtrack/), gathered in one module.
Song functions are left out; these are the shared building blocks, copied unchanged."""
import os
from engine import Song, fm, pulse, midi, CH, SEVENTH, orch_hit

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
os.makedirs(OUT, exist_ok=True)

INST = {
    'bass_house': lambda f, g, v: fm(f, g, v, ratio=1, i0=3.0, idec=0.07, i1=0.8, fb=0.5, a=0.002, d=0.2, s=0.6, r=0.04, sub=0.6),
    'bass_slap':  lambda f, g, v: fm(f, g, v, ratio=1, i0=5.0, idec=0.03, i1=1.0, fb=0.6, a=0.001, d=0.15, s=0.45, r=0.04, sub=0.5),
    'bass_drive': lambda f, g, v: fm(f, g, v, ratio=1, i0=3.0, idec=0.05, i1=1.3, fb=0.75, a=0.001, d=0.1, s=0.4, r=0.03, sub=0.5),
    'stab':       lambda f, g, v: fm(f, g, v, ratio=1, i0=2.5, idec=0.04, i1=0.45, fb=0.2, a=0.001, d=0.12, s=0.25, r=0.06, det=5),
    'pluck':      lambda f, g, v: fm(f, g, v, ratio=3, i0=2.0, idec=0.025, i1=0.15, a=0.001, d=0.09, s=0.0, r=0.04),
    'arp':        lambda f, g, v: pulse(f, g, v, duty=0.25),
    'arp_thin':   lambda f, g, v: pulse(f, g, v, duty=0.125, d=0.05, s=0.3),
    'bass_sub':   lambda f, g, v: fm(f, g, v, ratio=1, i0=1.6, idec=0.05, i1=0.45, fb=0.3, a=0.003, d=0.3, s=0.8, r=0.06, sub=0.9),
    'organ':      lambda f, g, v: fm(f, g, v, ratio=2, i0=1.2, idec=0.05, i1=0.6, fb=0.15, a=0.002, d=0.18, s=0.35, r=0.08, det=6),
    # songs2
    'bass_warp':  lambda f, g, v: fm(f, g, v, ratio=0.5, i0=3.2, wah=0.09, i1=0.5, fb=0.4, a=0.004, d=0.4, s=0.85, r=0.05, sub=0.9),
    'bass_reese': lambda f, g, v: fm(f, g, v, ratio=1, i0=0.6, idec=0.1, i1=1.0, fb=0.5, a=0.005, d=0.3, s=0.85, r=0.05, det=18, sub=0.8),
    'chirp':      lambda f, g, v: pulse(f, g, v, duty=0.5, d=0.1, s=0.5, r=0.04),
    # songs3
    'chime':      lambda f, g, v: fm(f, g, v, ratio=1.0, i0=0.5, idec=0.3, i1=0.1, a=0.005, d=0.8, s=0.0, r=0.4),
    'eski':       lambda f, g, v: pulse(f, g, v, duty=0.5, d=0.12, s=0.55, r=0.03),
    'eski_thin':  lambda f, g, v: pulse(f, g, v, duty=0.125, d=0.08, s=0.4, r=0.03),
    'sub808':     lambda f, g, v: fm(f, g, v, ratio=1.0, i0=0.4, idec=0.05, i1=0.1, a=0.003, d=0.6, s=0.9, r=0.08, sub=1.0),
    'sub808d':    lambda f, g, v: fm(f, g, v, ratio=1.0, i0=0.4, idec=0.05, i1=0.1, a=0.003, d=0.6, s=0.9, r=0.08, sub=1.0, bend=-7, bend_t=0.25),
    'darkstab':   lambda f, g, v: fm(f, g, v, ratio=1.0, i0=1.6, idec=0.06, i1=0.3, fb=0.3, a=0.002, d=0.25, s=0.2, r=0.15, det=8),
    'organ_hi':   lambda f, g, v: fm(f, g, v, ratio=2, i0=1.0, idec=0.05, i1=0.5, fb=0.1, a=0.002, d=0.15, s=0.3, r=0.06, det=5),
}

def voicing(root, q):
    notes = [root + 12 + i for i in CH[q]]
    if min(notes) < 50: notes = [n + 12 for n in notes]
    return notes

def arp_notes(root, q):
    base = sorted(root + 24 + i for i in CH[q][:4])
    if len(base) == 3: base.append(base[0] + 12)
    if base[0] < 64: base = [n + 12 for n in base]
    return base + [base[0] + 12]

UPDOWN = [0, 1, 2, 3, 4, 3, 2, 1] * 2

def bass_bar(S, bar, root, q, pattern, inst, vel=1.0):
    """pattern: (step, length, 'r'|'o'|'5'|'7'|'o5', [velocity])"""
    off = {'r': 0, 'o': 12, '5': 7, '7': SEVENTH[q], 'o5': 19}
    for st, ln, tok, *acc in pattern:
        v = vel * (acc[0] if acc else 1.0)
        S.note('bass', bar * 16 + st, ln, root + off[tok], inst, v)

def standard_tracks(S, lead_level=-15):
    S.track('kick', level=-11, rev=0.0)
    S.track('snare', level=-16, rev=0.15)
    S.track('clap', level=-16, rev=0.2, pan=0.05)
    S.track('hat', level=-25, rev=0.04, pan=0.25)
    S.track('ohat', level=-25, rev=0.06, pan=-0.2)
    S.track('crash', level=-26, rev=0.1, pan=-0.35)
    S.track('tom', level=-17, rev=0.15, pan=0.0)
    S.track('bass', level=-14, rev=0.0, sc=0.35)
    S.track('lead', level=lead_level, rev=0.07, dly=0.05, pan=0.08)
    S.track('lead2', level=lead_level - 7, rev=0.05, pan=-0.12)   # octave-down double
    S.track('arp', level=-24, rev=0.12, dly=0.15, pan=0.35, sc=0.2)

def lead(S, bar, text, inst, double=False, vel=1.0):
    S.line('lead', bar, text, inst, vel)
    if double: S.line('lead2', bar, text, inst, vel, transpose=-12)

def garage_tracks(S, lead_level=-20):
    standard_tracks(S, lead_level=lead_level)
    S.track('shaker', level=-29, rev=0.05, pan=0.3)
    S.track('rim', level=-23, rev=0.12, pan=-0.2)
    S.track('organ', level=-23, rev=0.22, dly=0.25, pan=-0.25, sc=0.3)
    S.track('orch', level=-21, rev=0.3)

def shuffle(S, b16, bar, sixteenths=True):
    for st in (2, 6, 10, 14): S.hit('hat', b16 + st, 'hat', 0.7)
    if sixteenths:
        for st in (3, 7, 11, 15): S.hit('hat', b16 + st, 'hat', 0.35)
    for st in range(16): S.hit('shaker', b16 + st, 'shaker', 0.6 if st % 2 else 0.35)

def chop(S, bar, root, q, steps, vel=0.7):
    """organ chord chops (needs an 'organ' track)"""
    for st in steps:
        for m in voicing(root, q)[:4]:
            S.note('organ', bar * 16 + st, 2, m + 12, 'organ', vel, legato=0.5)

def end_roll(S, bar):
    for st in range(8, 16): S.hit('snare', bar * 16 + st, 'snare', 0.35 + 0.65 * (st - 8) / 7)

def L(text):
    n = len(text.split())
    assert n == 16, f'{n} steps: {text}'
    return text

def kit(S, *names):
    lv = {'perc': (-22, 0.12, 0.25), 'stab': (-21, 0.18, -0.25), 'pluck': (-21, 0.15, 0.3),
          'mando': (-22, 0.2, 0.3), 'fx': (-20, 0.3, 0.0), 'organ': (-23, 0.22, -0.25),
          'shaker': (-29, 0.05, 0.3), 'rim': (-23, 0.12, -0.2), 'orch': (-15, 0.3, 0.0), 'sub': (-15, 0.0, 0.0)}
    for n in names:
        level, rev, pan = lv[n]
        S.track(n, level=level, rev=rev, pan=pan, sc=0.25 if n in ('stab', 'organ', 'pluck') else 0.0)

def arp(S, bar, root, q, inst='arp', vel=0.6, eighths=False):
    notes = arp_notes(root, q)
    for st in range(0, 16, 2 if eighths else 1):
        S.note('arp', bar * 16 + st, 2 if eighths else 1, notes[UPDOWN[st]], inst, vel if st % 4 == 0 else vel * 0.7, legato=0.6)

def gate(S, track, bar, root, q, pattern, inst, vel=0.7, up=12):
    """Chord stab gated to a 16-step pattern of x and dots."""
    for st, c in enumerate(pattern.split()):
        if c == 'x':
            for m in voicing(root, q)[:4]:
                S.note(track, bar * 16 + st, 1, m + up, inst, vel, legato=0.5)
