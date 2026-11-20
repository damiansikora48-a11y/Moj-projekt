"""RUCH ATAKU: strzał z łuku (łucznik).

Strzała (rekwizyt, kość prop.R) pojawia się w prawej dłoni przy nakładaniu na cięciwę
i znika w chwili wystrzału; gra wypuszcza wtedy pocisk z prop.R.
  0.18 nałożenie strzały, 0.38 uniesienie łuku, 0.58 pełne naciągnięcie,
  0.62 wystrzał (event 'release'), 0.78 przytrzymanie, 1.0 powrót
Kąty pozy naciągnięcia dobrane solverem: łuk pionowo, strzała w linii między dłońmi.
"""
from kit import K, HIDE, SHOW

# --- poza pełnego naciągnięcia (kąty z solvera: łuk pionowo, strzała między dłońmi, tułów bokiem)
NACIAG = {
    'chest': K((0, -45, 0)), 'head': K((0, 38, 0)),
    'upper_arm.L': K((102, 0, 0)), 'forearm.L': K((-10, 0, 0)), 'hand.L': K((-92, 0, 0)),
    'upper_arm.R': K((93, -32, 0)), 'forearm.R': K((129, 9, 0)), 'hand.R': K((-215, 16, 0)),
}
# --- poza po wystrzale: prawa dłoń odskakuje do tyłu
PO_STRZALE = dict(NACIAG)
PO_STRZALE.update({'upper_arm.R': K((98, -40, 0)), 'forearm.R': K((145, 9, 0)), 'hand.R': K((-225, 16, 0))})

_NOGI = {'thigh.L': K((14, 0, 0)), 'shin.L': K((-8, 0, 0)), 'thigh.R': K((-10, 0, 0)), 'shin.R': K((-4, 0, 0))}


def _poza(baza, prop):
    p = dict(_NOGI)
    p.update(baza)
    p['prop.R'] = K(scale=prop)
    return p


RUCH = {
    'id': 'strzal',
    'nazwa': 'Strzał z łuku',
    'typ': 'strzal',
    'rekwizyt': True,
    'kosc_startowa': 'prop.R',
    'frames': 40, 'event': 0.62, 'event_name': 'release',
    'keys': [
        (0.0, {'prop.R': K(scale=HIDE)}),
        (0.16, {'upper_arm.R': K((30, 0, 0)), 'forearm.R': K((60, 0, 0)), 'hand.R': K((-90, 0, 0)), 'upper_arm.L': K((20, 0, 0)), 'prop.R': K(scale=HIDE)}),
        (0.2, {'upper_arm.R': K((32, 0, 0)), 'forearm.R': K((62, 0, 0)), 'hand.R': K((-94, 0, 0)), 'upper_arm.L': K((22, 0, 0)), 'prop.R': K(scale=SHOW)}),
        (0.58, _poza(NACIAG, SHOW)),
        (0.61, _poza(NACIAG, SHOW)),
        (0.62, _poza(PO_STRZALE, HIDE)),
        (0.78, _poza(PO_STRZALE, HIDE)),
        (1.0, {'prop.R': K(scale=HIDE)}),
    ],
}
