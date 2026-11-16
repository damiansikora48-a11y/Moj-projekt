"""EFEKT ATAKU: kula ognia (pocisk).

model – świecący rdzeń z językami ognia i ogonem; przód pocisku to -Y w Blenderze
        (= +Z w Godot), ogon jest z tyłu. Gra wystrzeliwuje ją z kości z units.json.
"""
import math

from kit import V, cyl, ico, jitter, mtx, frame, seg, scale_m

PALETA = {
    'fire': ('#ff7a1a', 0.4, 0.0, 6.0),
    'fire_core': ('#ffd66b', 0.3, 0.0, 12.0),
    'ember': ('#ff4a1a', 0.5, 0.0, 3.5),
}


def model_kuli(sl):
    sl.add(ico(0.12, 2), 'fire_core', 'root')
    for i in range(10):
        a = 2 * math.pi * i / 10
        d = V(math.cos(a) * 0.8, 0.45, math.sin(a) * 0.8).normalized()  # na zewnątrz i lekko do tyłu
        F = frame(d * 0.08, d, (0, 1, 0))
        L = 0.1 + 0.05 * (i % 3)
        sl.add(cyl(0.05, 0.0, L, 6), 'fire', 'root', F @ mtx((0, 0, L / 2)))
    for i, (x, z, L) in enumerate(((0, 0, 0.42), (0.05, 0.04, 0.3), (-0.05, -0.03, 0.32), (0.02, -0.06, 0.26))):
        base = V(x * 0.5, 0.06, z * 0.5)
        sl.add(cyl(0.07 - 0.012 * i, 0.0, L, 6), 'ember' if i else 'fire', 'root', seg(base, base + V(x, L, z)))


EFEKT = {
    'id': 'kula_ognia',
    'nazwa': 'Kula ognia',
    'typ': 'pocisk',
    'paleta': PALETA,
    'model': model_kuli,
    'w_dloni': None,
}
