"""EFEKT STATUSU: podpalenie – płomienie przyczepiane do płonącego wroga.

Gra dodaje ten model jako dziecko trafionego wroga na czas podpalenia (atak.status.czas_s
w units.json) i co sekundę zadaje obrażenia od ognia (wartość ustala balans gry).
Środek modelu (0,0,0) = stopy wroga; płomienie sięgają ok. 1 m w górę – skaluj do wielkości wroga.
"""
import math

from kit import V, cyl, ico, box, mtx, seg

PALETA = {
    'fire': ('#ff5200', 0.4, 0.0, 2.2),
    'fire_core': ('#ffae00', 0.3, 0.0, 3.0),
    'ember': ('#ff4a1a', 0.5, 0.0, 3.5),
}


def model_podpalenia(sl):
    for i in range(14):  # języki ognia rozłożone na całej wysokości postaci
        a = 2 * math.pi * i / 7 + (0.4 if i >= 7 else 0.0)
        r = 0.2 + 0.05 * (i % 3)
        z = 0.05 + 0.9 * ((i * 5) % 14) / 14
        h = 0.28 + 0.22 * ((i * 3) % 5) / 5
        p = V(math.cos(a) * r, math.sin(a) * r, z)
        sl.add(cyl(0.07, 0.0, h, 6), 'fire', 'root', seg(p, p + V(math.cos(a) * 0.04, math.sin(a) * 0.04, h)))
        sl.add(cyl(0.04, 0.0, h * 0.55, 6), 'fire_core', 'root', seg(p, p + V(0, 0, h * 0.55)))
    for i, (x, y, z) in enumerate(((0.1, 0.05, 1.0), (-0.12, -0.04, 0.9), (0.02, 0.1, 1.15), (-0.05, -0.1, 1.08))):
        sl.add(box(0.03, 0.03, 0.03, 0.005), 'ember', 'root', mtx((x, y, z), (45, 45 + i * 20, 0)))


EFEKT = {
    'id': 'podpalenie',
    'nazwa': 'Podpalenie',
    'typ': 'status',
    'paleta': PALETA,
    'model': model_podpalenia,
    'w_dloni': None,
}
