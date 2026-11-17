"""ŻYWIOŁ: Natura (patrz ogien.py – opis pól)."""
import math

from kit import V, sphere, cyl, jitter, mtx, SIDES

ZYWIOL = {
    'id': 'natura',
    'nazwa': 'Natura',
    'barwy': {'tabard': '#3f7a2c', 'cape': '#2f5a24', 'plume': '#8fcf4a', 'robe': '#3f6e2c',
              'robe_dark': '#26451c', 'sash': '#a8c84a', 'cloak': '#3f6e2c', 'cloak_dark': '#26451c'},
    'zamiany': {
        'stone': ('#6e5a40', 0.9), 'stone_dark': ('#4a3a28', 0.95), 'stone_light': ('#8a7458', 0.9),
    },
    'swiecenie': ('#9cff5a', 4.0),
    'paleta': {'leaf': ('#5fa83a', 0.8), 'leaf_dark': ('#3c7a26', 0.85), 'bark': ('#5a3e26', 0.9)},
    # efekt ataku zależnie od RUCHU rodzica-roli; brak wpisu = efekt rodzica-roli
    'efekty': {'strzal': 'strzala', 'czar': 'strzala'},
}


def ozdoby(sl, J, s, bark):
    """Pęk liści na barkach."""
    for sg, S in SIDES:
        p = J['shoulder' + S] + V(sg * 0.03 * s, 0.02 * s, bark)
        b = 'shoulder' + S
        sl.add(cyl(0.05 * s, 0.06 * s, 0.05 * s, 8), 'bark', b, mtx(p))
        for i in range(5):
            a = 2 * math.pi * i / 5 + sg * 0.3
            q = p + V(math.cos(a) * 0.06, math.sin(a) * 0.06, 0.05) * s
            sl.add(jitter(sphere(0.07 * s, 0.03 * s, 0.012 * s, 10, 6), 0.004, 950 + i),
                   'leaf' if i % 2 else 'leaf_dark', b, mtx(q, (25, 0, math.degrees(a))))


ZYWIOL['ozdoby'] = ozdoby
