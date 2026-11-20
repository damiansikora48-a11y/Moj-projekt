"""ŻYWIOŁ: Kamień (patrz ogien.py – opis pól)."""
from kit import V, cyl, rock, jitter, sphere, mtx, SIDES

ZYWIOL = {
    'id': 'kamien',
    'nazwa': 'Kamień',
    'barwy': {'tabard': '#2c56a8', 'cape': '#7d2626', 'plume': '#7fd6ef', 'robe': '#6b6f78',
              'robe_dark': '#3f434b', 'sash': '#8c847a', 'cloak': '#6b6f78', 'cloak_dark': '#3f434b'},
    'zamiany': {},
    'swiecenie': ('#2fd0ff', 4.0),
    'paleta': {'stone': ('#8c847a', 0.92), 'stone_dark': ('#625b53', 0.95), 'moss': ('#5f8f37', 0.95),
               'crystal': ('#3fb8e0', 0.15, 0.0, 0.7)},
    # efekt ataku zależnie od RUCHU rodzica-roli; brak wpisu = efekt rodzica-roli
    'efekty': {'rzut': 'glaz', 'czar': 'glaz', 'ciecie': 'krysztaly', 'uderzenie': 'krysztaly'},
}


def ozdoby(sl, J, s, bark):
    for sg, S in SIDES:
        p = J['shoulder' + S] + V(sg * 0.03 * s, 0.03 * s, bark)
        b = 'shoulder' + S
        sl.add(rock(0.13 * s, 0.12 * s, 0.07 * s, 900 + sg), 'stone_dark', b, mtx(p))
        sl.add(jitter(sphere(0.07 * s, 0.065 * s, 0.025 * s, 10, 6), 0.006, 910 + sg), 'moss', b, mtx(p + V(-sg * 0.02, 0.02, 0.04) * s))
        for loc, rot, L in (((0.02, 0.0, 0.03), (-15, -sg * 15, 0), 0.16), ((-0.03, 0.03, 0.02), (-35, sg * 20, 0), 0.11)):
            M = mtx(p + V(sg * loc[0], loc[1], loc[2]) * s, rot)
            sl.add(cyl(0.025 * s, 0.025 * s, L * 0.65 * s, 6), 'crystal', b, M @ mtx((0, 0, L * 0.32 * s)))
            sl.add(cyl(0.025 * s, 0.0, L * 0.35 * s, 6), 'crystal', b, M @ mtx((0, 0, L * 0.82 * s)))


ZYWIOL['ozdoby'] = ozdoby
