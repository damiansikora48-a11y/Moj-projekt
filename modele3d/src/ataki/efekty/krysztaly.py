"""EFEKT ATAKU: kryształowe kolce wyrastające z ziemi (obszar).

model – kępa kolców jako efekt_krysztaly.glb; gra stawia kilka kęp w linii przed jednostką
        i animuje ich wyrastanie (skala od 0 do 1).
"""
import math

from kit import V, box, cyl, sphere, ico, rock, cut_below, taper, jitter, mtx, frame, seg, SIDES, lerp, scale_m

PALETA = {
    'crystal': ('#3fb8e0', 0.15, 0.0, 0.7),
    'stone': ('#8c847a', 0.92),
    'stone_dark': ('#625b53', 0.95),
    'rune': ('#2fd0ff', 0.4, 0.0, 4.0),
}


def model_kolcow(sl):
    """Efekt ataku: kępa kryształowych kolców wyrastających z ziemi (środek w 0,0,0)."""
    import random
    rng = random.Random(7)
    for i in range(7):
        a = 2 * math.pi * i / 7 + rng.uniform(-0.3, 0.3)
        r = 0.0 if i == 0 else rng.uniform(0.18, 0.32)
        L = 0.75 if i == 0 else rng.uniform(0.35, 0.6)
        tilt = 0 if i == 0 else rng.uniform(15, 30)
        base = V(math.cos(a) * r, math.sin(a) * r, -0.05)
        d = V(math.cos(a) * math.sin(math.radians(tilt)), math.sin(a) * math.sin(math.radians(tilt)),
              math.cos(math.radians(tilt)))
        F = frame(base, d, (1, 0, 0))
        w = 0.08 if i == 0 else rng.uniform(0.045, 0.07)
        sl.add(cyl(w, w * 0.9, L * 0.7, 6), 'crystal', 'root', F @ mtx((0, 0, L * 0.35)))
        sl.add(cyl(w * 0.9, 0.0, L * 0.3, 6), 'crystal', 'root', F @ mtx((0, 0, L * 0.85)))
    for i in range(9):
        a = 2 * math.pi * i / 9
        sl.add(rock(0.16, 0.14, 0.09, 300 + i), ('stone', 'stone_dark')[i % 2], 'root',
               mtx((math.cos(a) * 0.38, math.sin(a) * 0.38, 0.02), (rng.uniform(-15, 15), rng.uniform(-15, 15), math.degrees(a))))
    sl.add(cyl(0.3, 0.3, 0.01, 24), 'rune', 'root', mtx((0, 0, 0.004)))


EFEKT = {
    'id': 'krysztaly',
    'nazwa': 'Kryształowe kolce',
    'typ': 'obszar',          # gra stawia kępy kolców przed jednostką
    'paleta': PALETA,
    'model': model_kolcow,
    'w_dloni': None,
    'uwagi': '3 kępy w linii co 0.8 m, kolejno co 0.08 s',
}
