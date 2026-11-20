"""ŻYWIOŁ: Ogień.

barwy     – kolory „mundurowe” (tabard, peleryna, szata…) jednostki z tym żywiołem
zamiany   – przebarwienie konkretnych materiałów (np. kamień -> bazalt, mech -> popiół)
swiecenie – kolor wszystkich świecących elementów (runy, rdzenie, kryształy -> lawa)
ozdoby    – dodatek na barkach (płomienie), budowany w slocie Element
efekty    – efekt ataku zależnie od ruchu ataku (np. przy 'rzut' -> kula ognia)
"""
import math

from kit import V, cyl, ico, box, mtx, seg, SIDES

ZYWIOL = {
    'id': 'ogien',
    'nazwa': 'Ogień',
    'barwy': {'tabard': '#b8321e', 'cape': '#6e1a12', 'plume': '#ff8a1f', 'robe': '#b3302a',
              'robe_dark': '#6e1d1b', 'sash': '#e8892a', 'cloak': '#8e2a1a', 'cloak_dark': '#55180f'},
    'zamiany': {
        'stone': ('#4a403a', 0.9), 'stone_dark': ('#272221', 0.95), 'stone_light': ('#675a50', 0.9),
        'moss': ('#3c302a', 0.95), 'moss_dark': ('#2a201c', 0.95),
    },
    'swiecenie': ('#ff7a1a', 6.0),
    'paleta': {'fire': ('#ff7a1a', 0.4, 0.0, 6.0), 'fire_core': ('#ffd66b', 0.3, 0.0, 12.0),
               'ember': ('#ff4a1a', 0.5, 0.0, 3.5)},
    # efekt ataku zależnie od RUCHU rodzica-roli; brak wpisu = efekt rodzica-roli
    'efekty': {'rzut': 'kula_ognia', 'czar': 'kula_ognia', 'strzal': 'kula_ognia'},
}


def ozdoby(sl, J, s, bark):
    for sg, S in SIDES:
        p = J['shoulder' + S] + V(sg * 0.03 * s, 0.02 * s, bark)
        sl.add(ico(0.035 * s, 1), 'fire_core', 'shoulder' + S, mtx(p))
        for a, h in ((0.0, 0.16), (2.1, 0.11), (4.2, 0.13)):
            q = p + V(math.cos(a), math.sin(a), 0) * 0.03 * s
            sl.add(cyl(0.035 * s, 0.0, h * s, 6), 'fire', 'shoulder' + S,
                   seg(q, q + V(math.cos(a) * 0.03 * s, math.sin(a) * 0.03 * s, h * s)))
        sl.add(box(0.02 * s, 0.02 * s, 0.02 * s, 0.004), 'ember', 'shoulder' + S, mtx(p + V(sg * 0.06, 0, 0.18) * s, (45, 45, 0)))


ZYWIOL['ozdoby'] = ozdoby
