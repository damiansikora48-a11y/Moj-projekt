"""RUCH ATAKU: uderzenie oburącz w ziemię (Kamienny Rycerz).

  0.38 miecz nad głową, 0.52 uderzenie (event 'impact'), 0.72 przytrzymanie, 1.0 powrót.
Uwaga: kąty Z ramion są dobrane pod proporcje Kamiennego Rycerza, tak by lewa dłoń trzymała
rękojeść. Dla jednostki o innych proporcjach chwyt może wymagać korekty.
"""
from kit import K

# kąty Z ramion dobrane solverem tak, by lewa dłoń trzymała rękojeść tuż pod prawą (chwyt oburącz)
_HI = {'upper_arm.R': K((165, 0, -24)), 'forearm.R': K((40, 0, 0)), 'hand.R': K((20, 0, 0)),
       'upper_arm.L': K((150, 0, 6)), 'forearm.L': K((45, 0, -20)),
       'chest': K((-12, 0, 0)), 'spine': K((-5, 0, 0)), 'head': K((10, 0, 0)), 'thigh.L': K((10, 0, 0))}
_LO = {'upper_arm.R': K((55, 0, 84)), 'forearm.R': K((5, 0, 0)), 'hand.R': K((-45, 0, 0)),
       'upper_arm.L': K((50, 0, -24)), 'forearm.L': K((15, 0, -60)),
       'chest': K((25, 0, 0)), 'spine': K((12, 0, 0)), 'head': K((-25, 0, 0)),
       'thigh.L': K((28, 0, 0)), 'shin.L': K((-24, 0, 0)), 'thigh.R': K((-16, 0, 0)), 'shin.R': K((-8, 0, 0))}

RUCH = {
    'id': 'uderzenie',
    'nazwa': 'Uderzenie oburącz w ziemię',
    'typ': 'wrecz',
    'frames': 48, 'event': 0.52, 'event_name': 'impact',
    'keys': [(0.0, {}), (0.38, _HI), (0.52, _LO), (0.72, _LO), (1.0, {})],
}
