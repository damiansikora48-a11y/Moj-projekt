"""RUCH ATAKU: cięcie mieczem z zamachu (żołnierz).

Pozy kluczowe: (czas 0..1, {kość: K(obrót_xyz_stopnie)}). Brakujące kości = poza spoczynkowa.
Konwencja: obrót X dodatni = kończyna do przodu; ujemny shin = zgięcie kolana.
  0.30 zamach – miecz za głową, tułów skręcony
  0.45 trafienie (event 'hit')
  0.62 dokończenie cięcia, 1.0 powrót
"""
from kit import K

_SWORD_STANCE = {'thigh.L': K((18, 0, 0)), 'shin.L': K((-14, 0, 0)), 'thigh.R': K((-12, 0, 0)), 'shin.R': K((-6, 0, 0)),
                 'upper_arm.L': K((18, 0, 12)), 'forearm.L': K((32, 0, 0))}  # tarcza przed sobą, ale poniżej naramiennika

RUCH = {
    'id': 'ciecie',
    'nazwa': 'Cięcie mieczem',
    'typ': 'wrecz',
    'frames': 30, 'event': 0.45, 'event_name': 'hit',
    'keys': [
        (0.0, {}),
        (0.3, {**_SWORD_STANCE, 'upper_arm.R': K((115, 0, 0)), 'forearm.R': K((70, 0, 0)), 'hand.R': K((-20, 0, 0)),
               'chest': K((-6, -28, 0)), 'spine': K((0, -8, 0)), 'head': K((4, 18, 0))}),
        (0.45, {**_SWORD_STANCE, 'upper_arm.R': K((35, 0, 0)), 'forearm.R': K((5, 0, 0)), 'hand.R': K((-70, 0, 0)),
                'chest': K((14, 26, 0)), 'spine': K((6, 8, 0)), 'head': K((-10, -16, 0))}),
        (0.62, {**_SWORD_STANCE, 'upper_arm.R': K((-5, 0, 0)), 'forearm.R': K((0, 0, 0)), 'hand.R': K((-80, 0, 0)),
                'chest': K((16, 32, 0)), 'spine': K((6, 10, 0)), 'head': K((-10, -20, 0))}),
        (1.0, {}),
    ],
}
