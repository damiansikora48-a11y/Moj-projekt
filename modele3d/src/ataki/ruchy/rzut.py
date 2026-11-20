"""RUCH ATAKU: rzut (golem) – schyla się, chwyta rekwizyt z ziemi, unosi nad głowę, rzuca.

Rekwizyt w dłoni (kość prop.R) pochodzi z efektu jednostki (np. ataki/efekty/glaz.py).
  0.22 schylenie, 0.32 chwyt (rekwizyt pojawia się), 0.50 nad głową,
  0.60–0.625 wyrzut (event 'release', rekwizyt znika), 1.0 powrót
"""
from kit import K, HIDE, SHOW

RUCH = {
    'id': 'rzut',
    'nazwa': 'Rzut',
    'typ': 'rzut',
    'rekwizyt': True,  # kość prop.R: rekwizyt (np. głaz) ukryty w spoczynku, pokazywany w ataku
    'kosc_startowa': 'prop.R',  # skąd gra wystrzeliwuje pocisk
    'frames': 60, 'event': 0.62, 'event_name': 'release',
    'keys': [
        (0.0, {'prop.R': K(scale=HIDE)}),
        (0.22, {'spine': K((24, 0, 0)), 'chest': K((18, -10, 0)), 'head': K((-22, 0, 0)),
                'upper_arm.R': K((40, 0, 0)), 'forearm.R': K((20, 0, 0)), 'upper_arm.L': K((25, 0, 0)),
                'thigh.L': K((22, 0, 0)), 'shin.L': K((-28, 0, 0)), 'thigh.R': K((10, 0, 0)), 'shin.R': K((-16, 0, 0)),
                'prop.R': K(scale=HIDE)}),
        (0.32, {'spine': K((24, 0, 0)), 'chest': K((18, -10, 0)), 'head': K((-22, 0, 0)),
                'upper_arm.R': K((40, 0, 0)), 'forearm.R': K((20, 0, 0)), 'upper_arm.L': K((25, 0, 0)),
                'thigh.L': K((22, 0, 0)), 'shin.L': K((-28, 0, 0)), 'thigh.R': K((10, 0, 0)), 'shin.R': K((-16, 0, 0)),
                'prop.R': K(scale=SHOW)}),
        (0.5, {'spine': K((-6, 0, 0)), 'chest': K((-14, -22, 0)), 'head': K((10, 10, 0)),
               'upper_arm.R': K((165, 0, 0)), 'forearm.R': K((60, 0, 0)), 'upper_arm.L': K((60, 0, 0)),
               'forearm.L': K((20, 0, 0)), 'thigh.L': K((8, 0, 0)), 'shin.L': K((-6, 0, 0)), 'thigh.R': K((-8, 0, 0)),
               'prop.R': K(scale=SHOW)}),
        (0.6, {'spine': K((12, 0, 0)), 'chest': K((18, 24, 0)), 'head': K((-10, -12, 0)),
               'upper_arm.R': K((80, 0, 0)), 'forearm.R': K((10, 0, 0)), 'upper_arm.L': K((-15, 0, 0)),
               'thigh.L': K((22, 0, 0)), 'shin.L': K((-14, 0, 0)), 'thigh.R': K((-14, 0, 0)),
               'prop.R': K(scale=SHOW)}),
        (0.625, {'spine': K((13, 0, 0)), 'chest': K((19, 25, 0)), 'head': K((-10, -12, 0)),
                 'upper_arm.R': K((72, 0, 0)), 'forearm.R': K((9, 0, 0)), 'upper_arm.L': K((-15, 0, 0)),
                 'thigh.L': K((22, 0, 0)), 'shin.L': K((-14, 0, 0)), 'thigh.R': K((-14, 0, 0)),
                 'prop.R': K(scale=HIDE)}),
        (0.76, {'spine': K((14, 0, 0)), 'chest': K((22, 28, 0)), 'head': K((-10, -14, 0)),
                'upper_arm.R': K((35, 0, 0)), 'forearm.R': K((5, 0, 0)), 'upper_arm.L': K((-10, 0, 0)),
                'thigh.L': K((22, 0, 0)), 'shin.L': K((-14, 0, 0)), 'thigh.R': K((-14, 0, 0)),
                'prop.R': K(scale=HIDE)}),
        (1.0, {'prop.R': K(scale=HIDE)}),
    ],
}
