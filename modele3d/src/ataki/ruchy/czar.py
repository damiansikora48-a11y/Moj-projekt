"""RUCH ATAKU: rzucenie czaru (mag) – zbiera moc przy piersi, wypycha lewą dłoń do przodu.

Pocisk (np. kula ognia) startuje z lewej dłoni (kosc_startowa = hand.L).
Kostur w prawej ręce zostaje pionowo: obrót hand.R kompensuje uniesienie ramienia.
  0.35 skupienie: dłoń przy piersi, kostur uniesiony, tułów skręcony
  0.55 wyrzut dłoni (event 'cast'), 0.70 przytrzymanie, 1.0 powrót
"""
from kit import K

_STOP = {'thigh.L': K((16, 0, 0)), 'shin.L': K((-12, 0, 0)), 'thigh.R': K((-10, 0, 0)), 'shin.R': K((-6, 0, 0))}

RUCH = {
    'id': 'czar',
    'nazwa': 'Rzucenie czaru',
    'typ': 'czar',
    'kosc_startowa': 'hand.L',
    'frames': 36, 'event': 0.55, 'event_name': 'cast',
    'keys': [
        (0.0, {}),
        (0.35, {'upper_arm.L': K((35, 0, 0)), 'forearm.L': K((95, 0, 0)), 'hand.L': K((10, 0, 0)),
                'upper_arm.R': K((55, 0, 0)), 'forearm.R': K((35, 0, 0)), 'hand.R': K((-82, 0, 0)),
                'chest': K((-8, 22, 0)), 'spine': K((-2, 6, 0)), 'head': K((4, -14, 0))}),
        (0.55, {**_STOP, 'upper_arm.L': K((85, 0, 0)), 'forearm.L': K((5, 0, 0)), 'hand.L': K((-15, 0, 0)),
                'upper_arm.R': K((75, 0, 0)), 'forearm.R': K((20, 0, 0)), 'hand.R': K((-90, 0, 0)),
                'chest': K((10, -22, 0)), 'spine': K((4, -6, 0)), 'head': K((-6, 14, 0))}),
        (0.70, {**_STOP, 'upper_arm.L': K((82, 0, 0)), 'forearm.L': K((8, 0, 0)), 'hand.L': K((-15, 0, 0)),
                'upper_arm.R': K((72, 0, 0)), 'forearm.R': K((22, 0, 0)), 'hand.R': K((-88, 0, 0)),
                'chest': K((10, -20, 0)), 'spine': K((4, -6, 0)), 'head': K((-6, 12, 0))}),
        (1.0, {}),
    ],
}
