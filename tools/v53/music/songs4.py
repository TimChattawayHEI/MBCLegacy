"""Batch 4: chapter "Nightlife 2006" (a Friday night out in London, 2006).
Six 32-bar seamless loops. House rules: no FM lead voices, beat and bass lead, melody sparse,
short dry riffs, quiet square-wave parts only, no pads, no vibrato brass, no beeping on dark tracks.
Run: python songs4.py [name ...]   (no args renders all six into ./out)"""
import sys, os
import numpy as np
from engine import Song, midi, orch_hit, SR
from kit import *

N = midi


# ---------------------------------------------------------------- shared helpers
def crash(S, bar, vel=0.9):
    S.hit('crash', bar * 16, 'crash', vel)

def tom_fill(S, bar, long=False):
    if long:
        seq = [(8, 'tomH'), (9, 'tomH'), (10, 'tomM'), (11, 'tomM'), (12, 'tomL'), (13, 'tomL'), (14, 'tomL'), (15, 'tomL')]
    else:
        seq = [(12, 'tomH'), (13, 'tomH'), (14, 'tomM'), (15, 'tomL')]
    for i, (st, k) in enumerate(seq):
        S.hit('tom', bar * 16 + st, k, 0.6 + 0.4 * i / max(1, len(seq) - 1))

def four(S, b16, kind='kick', vel=1.0):
    for st in (0, 4, 8, 12): S.hit('kick', b16 + st, kind, vel)

def hats16(S, b16, accent=0.75, ghost=0.35):
    for st in range(16): S.hit('hat', b16 + st, 'hat', accent if st % 4 == 2 else ghost if st % 2 else ghost * 1.3)

def ohats(S, b16, vel=0.8):
    for st in (2, 6, 10, 14): S.hit('ohat', b16 + st, 'ohat', vel)

def bassline(S, track, bar, root, pat, inst, vel=1.0):
    """pat: (step, length, semitones, [vel]) relative to root"""
    for st, ln, semi, *acc in pat:
        S.note(track, bar * 16 + st, ln, root + semi, inst, vel * (acc[0] if acc else 1.0))


# ---------------------------------------------------------------- 16 Platform Zero
def platform_zero():
    """Orpington Station. 2006 electro house: filthy 16th drive bass with an offbeat slap layer,
    claps on 2/4, open hats, sparse gated stabs, quiet square-wave riff only in the last section."""
    S = Song('Platform Zero', 128, 32, INST)
    standard_tracks(S)
    S.track('grit', level=-21, rev=0.0, sc=0.45, pan=0.0)
    kit(S, 'stab')
    prog = [(N('F#1'), 'm'), (N('F#1'), 'm'), (N('D2'), 'M'), (N('E2'), 'M')]
    DRIVE = [(0, 1, 'r', 0.5), (1, 1, 'r', 0.75), (2, 1, 'o'), (3, 1, 'r', 0.6),
             (4, 1, 'r', 0.5), (5, 1, 'r', 0.75), (6, 1, 'o'), (7, 1, 'o5', 0.6),
             (8, 1, 'r', 0.5), (9, 1, 'r', 0.75), (10, 1, 'o'), (11, 1, 'r', 0.6),
             (12, 1, 'r', 0.5), (13, 1, 'o', 0.8), (14, 2, '7', 0.9)]
    DRIVE_B = DRIVE[:12] + [(12, 1, 'o'), (13, 1, 'r', 0.6), (14, 1, 'o5', 0.8), (15, 1, 'o', 0.9)]
    LONG = [(0, 6, 'r'), (6, 2, 'o', 0.7), (8, 6, 'r', 0.9), (14, 2, '5', 0.7)]
    GRIT = [(2, 1, 12), (6, 1, 12), (10, 1, 12), (14, 1, 19)]
    STAB = 'x . . x . . x . . . x . . . . .'
    RIFF = [L('F#4 . . F#4 . . A4 . . . F#4 . E4 . . .'), L('F#4 . . F#4 . . A4 . . . C#5 . B4 . . .')]
    for bar in range(32):
        b = bar * 16
        root, q = prog[bar % 4]
        sec = bar // 8
        brk = 16 <= bar < 22
        # drums
        if not brk: four(S, b)
        if bar in (20, 21):
            for st in (0, 4, 8, 12): S.hit('kick', b + st, 'kick', 0.55)
        for st in (4, 12): S.hit('clap', b + st, 'clap', 1.0)
        if bar % 2 == 1: S.hit('clap', b + 15, 'clap', 0.4)
        if not brk or bar >= 20: ohats(S, b, 0.85)
        hats16(S, b, accent=0.6, ghost=0.3 if sec != 2 else 0.2)
        if bar % 8 == 0: crash(S, bar)
        # bass
        if brk:
            bass_bar(S, bar, root, q, LONG, 'bass_drive', 0.9)
        else:
            bass_bar(S, bar, root, q, DRIVE_B if bar % 4 == 3 else DRIVE, 'bass_drive')
            if sec >= 1: bassline(S, 'grit', bar, root, GRIT, 'bass_slap', 0.9)
        # stabs: sparse in A, gated in B and C
        if sec == 0 and bar % 2 == 1:
            gate(S, 'stab', bar, root, q, 'x . . . . . . . . . x . . . . .', 'stab', 0.7)
        elif sec >= 1:
            gate(S, 'stab', bar, root, q, STAB, 'stab', 0.75)
        # quiet square riff, last section only (and a hint in the break)
        if sec == 3 and bar < 31:
            S.line('arp', bar, RIFF[bar % 2], 'arp_thin', 0.55)
        if bar in (18, 19):
            S.line('arp', bar, RIFF[0], 'arp_thin', 0.45)
        # fills
        if bar in (7, 15): tom_fill(S, bar)
        if bar == 23: tom_fill(S, bar, long=True)
        if bar == 31: end_roll(S, bar)
    S.tracks['arp']['level'] = -25
    return S


# ---------------------------------------------------------------- 17 Mind the Gap
def mind_the_gap():
    """Train to Charing Cross. Sheffield bassline / niche: bouncing warp bass, offbeat organ
    stabs, rolling 4/4 with clickety-clack train hats on a rim/tick layer."""
    S = Song('Mind the Gap', 138, 32, INST)
    garage_tracks(S)
    kit(S, 'perc')
    S.tracks['bass']['level'] = -13
    prog = [(N('G1'), 'm7'), (N('G1'), 'm7'), (N('D#1'), 'maj7'), (N('F1'), 'M')]
    WOB_A = [(0, 3, 0), (3, 1, 12, 0.7), (5, 2, 0, 0.85), (8, 2, 0), (10, 2, 3, 0.85), (12, 2, 5, 0.9), (14, 2, 12, 0.8)]
    WOB_B = [(0, 3, 0), (3, 1, 12, 0.7), (5, 2, 0, 0.85), (8, 3, 12), (11, 1, 10, 0.7), (12, 2, 7, 0.9), (14, 2, 5, 0.8)]
    SPARSE = [(0, 4, 0), (8, 2, 12, 0.7)]
    TRAIN = [(0, 0.9), (2, 0.45), (3, 0.7), (6, 0.5), (8, 0.9), (10, 0.45), (11, 0.7), (14, 0.5)]
    SQ = L('G5 . . G5 . . . . A#5 . . . . . . .')
    for bar in range(32):
        b = bar * 16
        root, q = prog[bar % 4]
        sec = bar // 8
        brk = 16 <= bar < 22
        if not brk: four(S, b, 'kick909')
        if bar in (20, 21):
            for st in (0, 8): S.hit('kick', b + st, 'kick909', 0.7)
        for st in (4, 12): S.hit('clap', b + st, 'clap', 0.95)
        ohats(S, b, 0.8 if not brk else 0.5)
        # train wheels: tick on every 16th, rim clacks in a 3-3-2 rail-joint rhythm
        for st in range(16): S.hit('perc', b + st, 'tick', 0.5 if st % 4 == 0 else 0.25)
        for st, v in TRAIN: S.hit('rim', b + st, 'rim', v)
        if sec >= 1 and not brk:
            for st in range(16): S.hit('shaker', b + st, 'shaker', 0.6 if st % 2 else 0.3)
        if bar % 8 == 0: crash(S, bar)
        # warp bass
        if brk:
            bassline(S, 'bass', bar, root, SPARSE, 'bass_warp')
        elif sec == 0 and bar < 2:
            bassline(S, 'bass', bar, root, WOB_A, 'bass_warp')
        else:
            bassline(S, 'bass', bar, root, WOB_B if bar % 2 else WOB_A, 'bass_warp')
        # organ stabs on the offbeats (bassline house), doubled pushes in B/C
        if sec == 0:
            chop(S, bar, root, q, [2, 10], 0.7)
        elif brk:
            chop(S, bar, root, q, [2], 0.7)
        else:
            chop(S, bar, root, q, [2, 6, 10, 13] if bar % 2 else [2, 6, 10], 0.75)
        if sec == 3 and bar % 2 == 0:
            S.line('arp', bar, SQ, 'chirp', 0.5)
        if bar in (7, 15): tom_fill(S, bar)
        if bar == 23: end_roll(S, bar)
        if bar == 31: end_roll(S, bar)
    S.tracks['arp']['level'] = -26
    return S


# ---------------------------------------------------------------- 18 Terminus
def terminus():
    """Charing Cross. UK funky house: shuffled hats and shaker, conga/bongo groove carrying the
    track, slap bass syncopation, organ chops, cowbell accents. Quiet square only in the C section."""
    S = Song('Terminus', 126, 32, INST)
    S.swing = 0.16
    garage_tracks(S)
    kit(S, 'perc')
    S.track('conga', level=-19, rev=0.12, pan=0.3)
    S.track('bongo', level=-23, rev=0.1, pan=-0.35)
    prog = [(N('A1'), 'm9'), (N('A1'), 'm9'), (N('D2'), 'm7'), (N('E2'), 'm7')]
    SLAP = [(0, 2, 'r'), (3, 1, 'r', 0.7), (6, 2, 'o', 0.8), (10, 1, 'r'), (11, 2, '5', 0.8), (14, 2, '7', 0.7)]
    SLAP_B = [(0, 2, 'r'), (3, 1, 'o', 0.7), (5, 1, 'r', 0.6), (7, 2, '5', 0.8), (10, 1, 'r'), (12, 1, 'o', 0.7), (14, 2, '7', 0.8)]
    CONGA = [(0, 'congaL', 0.9), (3, 'congaH', 0.6), (4, 'congaS', 0.8), (6, 'congaH', 0.7), (7, 'congaH', 0.4),
             (10, 'congaL', 0.8), (11, 'congaH', 0.5), (12, 'congaS', 0.85), (14, 'congaH', 0.7)]
    CONGA_B = [(0, 'congaL', 0.9), (2, 'congaH', 0.5), (3, 'congaH', 0.6), (6, 'congaS', 0.8), (8, 'congaL', 0.8),
               (9, 'congaH', 0.4), (11, 'congaH', 0.7), (12, 'congaS', 0.85), (14, 'congaL', 0.6), (15, 'congaH', 0.5)]
    BONGO = [5, 9, 13, 15]
    SQ = [L('E5 . . . . . G5 . . . . . . . . .'), L('. . . . . . . . A5 . . G5 . . . .')]
    for bar in range(32):
        b = bar * 16
        root, q = prog[bar % 4]
        sec = bar // 8
        brk = 16 <= bar < 22
        # kick: 4/4 with a skippy pickup every other bar (funky)
        if not brk:
            for st in (0, 4, 8, 12): S.hit('kick', b + st, 'kick', 1.0)
            if bar % 2 == 1: S.hit('kick', b + 14, 'kick', 0.5)
        elif bar >= 20:
            S.hit('kick', b, 'kick', 0.8)
        for st in (4, 12): S.hit('clap', b + st, 'clap', 1.0)
        if bar % 4 == 3: S.hit('clap', b + 15, 'clap', 0.45)
        shuffle(S, b, bar, sixteenths=sec != 0)
        if sec >= 1: ohats(S, b, 0.55)
        for st, k, v in (CONGA_B if bar % 2 else CONGA): S.hit('conga', b + st, k, v)
        if sec >= 1:
            for st in BONGO: S.hit('bongo', b + st, 'bongo', 0.7)
        for st in (3, 11): S.hit('rim', b + st, 'rim', 0.6)
        if bar % 4 == 2: S.hit('perc', b + 10, 'cowbell', 0.7)
        if bar % 8 == 0: crash(S, bar, 0.8)
        # bass
        if brk:
            bass_bar(S, bar, root, q, [(0, 3, 'r'), (10, 2, 'o', 0.6)], 'bass_slap', 0.9)
        else:
            bass_bar(S, bar, root, q, SLAP_B if bar % 2 else SLAP, 'bass_slap')
        # organ chops: sparse
        if sec == 0:
            chop(S, bar, root, q, [3] if bar % 2 == 0 else [3, 10], 0.7)
        else:
            chop(S, bar, root, q, [3, 10] if bar % 2 == 0 else [3, 6, 10], 0.75)
        if sec == 3 and bar < 31:
            S.line('arp', bar, SQ[bar % 2], 'arp_thin', 0.5)
        if bar in (7, 15): tom_fill(S, bar)
        if bar == 23: end_roll(S, bar)
        if bar == 31: end_roll(S, bar)
    S.tracks['arp']['level'] = -27
    return S


# ---------------------------------------------------------------- 19 Smoking Area
def smoking_area():
    """Back alley, watch thieves. Dark grime at 140, half-time: kick on 1, snare/clap on 3,
    sub808 with slides, low darkstab chords, reese drone in the break. Eskibeat square stabs
    are single dry hits kept very low (not riffs), so the track does not beep."""
    S = Song('Smoking Area', 140, 32, INST)
    standard_tracks(S)
    kit(S, 'sub', 'stab', 'perc')
    S.tracks['stab']['level'] = -22
    S.track('eski', level=-31, rev=0.12, pan=0.3, sc=0.0)
    S.track('reese', level=-24, rev=0.1, pan=-0.1)
    S.tracks['snare']['level'] = -15
    E1, G1, F1, D1, C2 = N('E1'), N('G1'), N('F1'), N('D1'), N('C2')
    # 2-bar sub phrases: (step, len, note, inst)
    SUB = [[(0, 6, E1, 'sub808'), (10, 4, G1, 'sub808'), (14, 2, F1, 'sub808d')],
           [(0, 3, E1, 'sub808'), (6, 4, E1, 'sub808'), (11, 3, C2, 'sub808d')]]
    SUB2 = [[(0, 6, E1, 'sub808'), (10, 4, D1 + 12, 'sub808'), (14, 2, C2, 'sub808')],
            [(0, 3, E1, 'sub808'), (6, 2, G1, 'sub808'), (8, 6, F1, 'sub808d')]]
    KICK = [[0, 10], [0, 6, 7]]
    CHORDS = [(N('E2'), 'm'), (N('E2'), 'm'), (N('C2'), 'M'), (N('F2'), 'M')]
    DSTAB = ['x . . x . . . . . . . . . . . .', '. . . . . . x . . . . . . . . .']
    ESKI = [(3, 'E4'), (11, 'G4')]
    for bar in range(32):
        b = bar * 16
        sec = bar // 8
        brk = 16 <= bar < 22
        ph = bar % 2
        root, q = CHORDS[(bar // 2) % 4]
        # drums: half-time
        if not brk:
            for st in KICK[ph]: S.hit('kick', b + st, 'kick', 1.0 if st == 0 else 0.75)
            S.hit('snare', b + 8, 'snare', 1.0); S.hit('clap', b + 8, 'clap', 0.9)
        elif bar >= 20:
            S.hit('snare', b + 8, 'snare', 0.8)
        # hats: 8ths, with a 16th triplet-ish roll at the end of each 2-bar phrase
        for st in range(0, 16, 2): S.hit('hat', b + st, 'hat', 0.7 if st % 4 == 0 else 0.45)
        if ph == 1 and not brk:
            for st in (13, 14, 15): S.hit('hat', b + st, 'hat', 0.4)
        if sec >= 1 and not brk and ph == 1: S.hit('ohat', b + 6, 'ohat', 0.5)
        if sec in (1, 3): S.hit('perc', b + 14, 'rim', 0.5)
        if bar % 8 == 0: crash(S, bar, 0.7)
        # sub
        if brk:
            if ph == 0: S.note('sub', b, 12, E1, 'sub808', 0.9)
        else:
            for st, ln, m, ins in (SUB2 if sec == 2 else SUB)[ph]: S.note('sub', b + st, ln, m, ins)
        # reese drone in the break and quietly under C
        if brk and ph == 0:
            S.note('reese', b, 30, N('E2'), 'bass_reese', 0.9)
        # dark stabs: low register, sparse
        if not brk or bar >= 18:
            gate(S, 'stab', bar, root, q, DSTAB[ph], 'darkstab', 0.75, up=0)
        # eskibeat: single short square hits, very low, B and C sections only
        if sec in (1, 3) and ph == 0:
            for st, n in ESKI: S.note('eski', b + st, 1, N(n), 'eski', 0.6, legato=0.4)
        if bar in (7, 15): tom_fill(S, bar)
        if bar == 23: tom_fill(S, bar, long=True)
        if bar == 31: end_roll(S, bar)
    return S


# ---------------------------------------------------------------- 20 Night Bus
def night_bus():
    """N47 top deck. Tired late-night 2-step: heavy swing, skippy kick, rim backbeat,
    sub bass following the kick, soft organ chops, very sparse quiet square motif."""
    S = Song('Night Bus', 132, 32, INST)
    S.swing = 0.22
    garage_tracks(S)
    S.tracks['bass']['level'] = -13
    S.tracks['hat']['level'] = -27
    S.tracks['crash']['level'] = -29
    S.tracks['organ']['level'] = -24
    prog = [(N('F1'), 'm9'), (N('C#2'), 'maj7'), (N('A#1'), 'm7'), (N('C2'), 'm7')]
    KICK = [[0, 10], [0, 7, 10]]
    SUBP = [[(0, 3, 'r'), (3, 1, 'o', 0.5), (10, 4, 'r', 0.9), (14, 2, '5', 0.6)],
            [(0, 3, 'r'), (7, 2, 'r', 0.8), (10, 3, 'o', 0.7), (13, 2, '7', 0.6)]]
    SQ = L('. . . . . . G#5 . . . F5 . . . . .')
    for bar in range(32):
        b = bar * 16
        root, q = prog[bar % 4]
        sec = bar // 8
        brk = 16 <= bar < 22
        ph = bar % 2
        if not brk:
            for st in KICK[ph]: S.hit('kick', b + st, 'kick', 1.0 if st == 0 else 0.7)
        elif bar >= 20 and ph == 0:
            S.hit('kick', b, 'kick', 0.7)
        # snare light on 2 and 4 (rim carries the backbeat)
        for st in (4, 12): S.hit('rim', b + st, 'rim', 0.8)
        if not brk and sec >= 1:
            for st in (4, 12): S.hit('snare', b + st, 'snare', 0.55)
        if ph == 1 and bar != 31: S.hit('rim', b + 15, 'rim', 0.4)
        shuffle(S, b, bar, sixteenths=sec >= 1)
        if sec >= 1 and not brk: S.hit('ohat', b + 14, 'ohat', 0.45)
        if bar % 8 == 0: crash(S, bar, 0.7)
        # sub bass
        if brk:
            bass_bar(S, bar, root, q, [(0, 8, 'r', 0.8)], 'bass_sub')
        else:
            bass_bar(S, bar, root, q, SUBP[ph], 'bass_sub')
        # organ chops (garage stabs), sleepy and sparse
        chop(S, bar, root, q, [3] if (sec == 0 or brk) else [3, 10], 0.6)
        if sec == 3 and bar % 4 == 1:
            S.line('arp', bar, SQ, 'arp_thin', 0.45)
        if bar in (7, 15): tom_fill(S, bar)
        if bar == 23: end_roll(S, bar)
        if bar == 31:   # tired roll: swells then eases off on the swung last 16th so the seam lands softly
            for st in range(8, 16): S.hit('snare', b + st, 'snare', [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.45][st - 8])
    S.tracks['arp']['level'] = -28
    S.tracks['snare']['level'] = -19
    S.tracks['tom']['level'] = -20
    return S


# ---------------------------------------------------------------- 21 Last Orders (boss)
def last_orders_boss():
    """Boss for the chapter (Ticket Inspector, Lewisham Lenny, The Jeweller). The Big One v2
    template without FM leads: driving 16th bass, hammering octave riffs on stab, orchestra hits
    on phrase starts and accents, toms. Break at bars 24-27."""
    S = Song('Last Orders', 150, 32, INST)
    standard_tracks(S)
    kit(S, 'stab')
    S.tracks['stab']['level'] = -18
    S.track('stab2', level=-24, rev=0.1, pan=0.25, sc=0.2)
    S.track('orch', level=-16, rev=0.28)
    S.tracks['bass']['level'] = -13
    prog = [(N('D2'), 'm'), (N('D2'), 'm'), (N('A#1'), 'M'), (N('C2'), 'M'),
            (N('D2'), 'm'), (N('D2'), 'm'), (N('G1'), 'm'), (N('A1'), 'M')]
    DRIVE = [(st, 1, 'o' if st % 4 == 2 else 'r', 1.0 if st % 4 == 2 else 0.6 if st % 2 else 0.8) for st in range(16)]
    DRIVE_T = DRIVE[:12] + [(12, 1, 'o'), (13, 1, '7', 0.8), (14, 1, 'o5', 0.9), (15, 1, 'o', 0.9)]
    # hammering riff, relative semitones from the chord root (stab, 2 octaves up from the bass)
    HAM = [(0, 1, 0), (2, 1, 0), (3, 1, 0), (5, 1, 0), (7, 1, 3), (10, 1, 2), (12, 1, 0), (14, 1, -2)]
    HAM2 = [(0, 1, 0), (2, 1, 0), (3, 1, 0), (5, 1, 0), (7, 1, 7), (8, 1, 5), (10, 1, 3), (11, 1, 2), (13, 1, 0)]
    HAM_C = [(0, 1, 12), (1, 1, 12), (3, 1, 12), (4, 1, 10), (6, 1, 12), (8, 1, 7), (10, 1, 8), (11, 1, 7), (13, 1, 5), (14, 1, 3)]
    for bar in range(32):
        b = bar * 16
        root, q = prog[bar % 8]
        sec = bar // 8
        brk = 24 <= bar < 28
        # drums
        if not brk:
            four(S, b)
            if bar % 2 == 1: S.hit('kick', b + 14, 'kick', 0.7)
            for st in (4, 12): S.hit('snare', b + st, 'snare', 1.0)
            if sec >= 2:
                for st in (4, 12): S.hit('clap', b + st, 'clap', 0.8)
            for st in range(0, 16, 2): S.hit('hat', b + st, 'hat', 0.8)
            for st in range(1, 16, 2): S.hit('hat', b + st, 'hat', 0.3)
            ohats(S, b, 0.6)
        else:
            S.hit('kick', b, 'kick', 1.0)
            if bar >= 26:
                for st in (4, 8, 12): S.hit('kick', b + st, 'kick', 0.7)
            for st in range(0, 16, 2): S.hit('tom', b + st, 'tomL' if st % 4 == 0 else 'tomM', 0.45)
            S.hit('snare', b + 12, 'snare', 0.8)
        if bar % 4 == 0: crash(S, bar, 0.9)
        # bass
        if brk:
            bass_bar(S, bar, root, q, [(0, 4, 'r'), (4, 4, 'r', 0.7), (8, 4, 'o', 0.8), (12, 4, 'r', 0.7)], 'bass_drive')
        else:
            bass_bar(S, bar, root, q, DRIVE_T if bar % 4 == 3 else DRIVE, 'bass_drive')
        # orchestra hits: phrase starts plus a push into turnaround bars
        if bar % 4 == 0 or brk:
            S.add('orch', b, orch_hit(voicing(root, q)) * 0.9)
        if bar % 4 == 3 and not brk:
            S.add('orch', b + 10, orch_hit(voicing(root, q)) * 0.7)
            S.add('orch', b + 14, orch_hit(voicing(root, q)) * 0.8)
        # hammering stab riff with octave double
        top = root + 24
        if sec == 1 or (sec == 3 and not brk):
            pat = HAM2 if bar % 2 else HAM
        elif sec == 2:
            pat = HAM_C if bar % 2 == 0 else HAM2
        else:
            pat = None
        if sec == 0 and bar % 2 == 1:
            pat = [(0, 1, 0), (2, 1, 0), (3, 1, 0)]
        if brk:
            pat = [(0, 1, 0), (3, 1, 0), (6, 1, 0)]
        if pat:
            for st, ln, semi in pat:
                S.note('stab', b + st, ln, top + semi, 'stab', 0.85, legato=0.55)
                S.note('stab2', b + st, ln, top + semi - 12, 'stab', 0.8, legato=0.55)
        if bar in (7, 15): tom_fill(S, bar)
        if bar == 23: tom_fill(S, bar, long=True)
        if bar == 27: end_roll(S, bar)
        if bar == 31: end_roll(S, bar)
    return S


SONGS = {
    '16_Platform_Zero': platform_zero,
    '17_Mind_the_Gap': mind_the_gap,
    '18_Terminus': terminus,
    '19_Smoking_Area': smoking_area,
    '20_Night_Bus': night_bus,
    '21_Last_Orders_Boss': last_orders_boss,
}


def check(mix, S):
    """Level read-out per 8-bar section, plus the largest sample-to-sample step inside the loop
    (a seam_jump at or below that is inaudible)."""
    bar_n = S.L / 32
    secs = []
    for s in range(4):
        seg = mix[:, int(s * 8 * bar_n):int((s + 1) * 8 * bar_n)]
        secs.append(20 * np.log10(np.sqrt((seg ** 2).mean())))
    inner = float(np.max(np.abs(np.diff(mix, axis=1))))
    return secs, inner


if __name__ == '__main__':
    names = sys.argv[1:] or list(SONGS)
    for name in names:
        S = SONGS[name]()
        mix, stats, report = S.render(os.path.join(OUT, name))
        secs, inner = check(mix, S)
        print(f"== {name}  {S.bpm} bpm  {stats['seconds']:.2f}s  peak {stats['peak_db']:.2f} dB  "
              f"rms {stats['rms_db']:.2f} dB  seam_jump {stats['seam_jump']:.4f} (max inner step {inner:.4f})")
        print('   section rms (bars 1-8/9-16/17-24/25-32): ' + ' / '.join(f'{x:.1f}' for x in secs))
        for r in report: print('   ' + r)
