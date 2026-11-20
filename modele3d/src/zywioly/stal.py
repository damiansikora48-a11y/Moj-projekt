"""ŻYWIOŁ: Stal (patrz ogien.py – opis pól)."""
from kit import V, cyl, sphere, mtx, SIDES

ZYWIOL = {
    'id': 'stal',
    'nazwa': 'Stal',
    'barwy': {'tabard': '#2f5fb8', 'cape': '#9a2a2a', 'plume': '#d23a2c', 'robe': '#2f4f8a',
              'robe_dark': '#1d3260', 'sash': '#e0ac3c', 'cloak': '#2f4f8a', 'cloak_dark': '#1d3260'},
    'zamiany': {
        'stone': ('#9aa2ab', 0.4, 0.75), 'stone_dark': ('#5d6670', 0.4, 0.8), 'stone_light': ('#b8c0c8', 0.35, 0.8),
        'moss': ('#2f5fb8', 0.75), 'moss_dark': ('#1d3c80', 0.75),
    },
    'swiecenie': ('#ffd27a', 3.0),
    'paleta': {'steel': ('#aab3bd', 0.32, 0.85), 'steel_dark': ('#5d6670', 0.4, 0.8), 'gold': ('#e0ac3c', 0.3, 0.9)},
    # efekt ataku zależnie od RUCHU rodzica-roli; brak wpisu = efekt rodzica-roli
    'efekty': {},
}


def ozdoby(sl, J, s, bark):
    """Stalowy naramiennik z kolcem."""
    for sg, S in SIDES:
        p = J['shoulder' + S] + V(sg * 0.03 * s, 0, bark - 0.02 * s)
        b = 'shoulder' + S
        sl.add(sphere(0.12 * s, 0.12 * s, 0.07 * s, 16, 10), 'steel', b, mtx(p))
        sl.add(cyl(0.122 * s, 0.122 * s, 0.015 * s, 18), 'gold', b, mtx(p - V(0, 0, 0.01 * s)))
        sl.add(cyl(0.035 * s, 0.0, 0.14 * s, 8), 'steel_dark', b, mtx(p + V(sg * 0.02, 0, 0.1) * s, (0, sg * 25, 0)))


ZYWIOL['ozdoby'] = ozdoby
