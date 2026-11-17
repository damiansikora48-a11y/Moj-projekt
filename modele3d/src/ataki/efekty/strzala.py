"""EFEKT ATAKU: strzała (pocisk).

model   – strzała jako efekt_strzala.glb; przód to -Y w Blenderze (= +Z w Godot)
w_dloni – ta sama strzała nałożona na cięciwę w prawej dłoni (kość prop.R) przy ruchu 'strzal'
"""
from mathutils import Matrix

from kit import V, cyl, sphere, box, mtx, frame, scale_m

PALETA = {
    'wood': ('#7a5230', 0.8),
    'steel': ('#aab3bd', 0.32, 0.85),
    'feather': ('#e8e0d0', 0.85),
    'leaf': ('#5fa83a', 0.8),
}

DLUGOSC = 0.75


def model_strzaly(sl, kosc='root', M=None):
    """Strzała od nasady (0,0,0) do grotu (0,-DLUGOSC,0)."""
    M = M if M is not None else Matrix.Identity(4)
    F = M @ frame(V(0, 0, 0), V(0, -1, 0), (1, 0, 0))  # lokalna oś Z = kierunek lotu
    sl.add(cyl(0.011, 0.011, DLUGOSC, 8), 'wood', kosc, F @ mtx((0, 0, DLUGOSC / 2)))
    # grot w kształcie liścia
    sl.add(sphere(0.035, 0.008, 0.06, 10, 6), 'steel', kosc, F @ mtx((0, 0, DLUGOSC + 0.03)) @ mtx(rot=(90, 0, 0)))
    # lotki (3 pióra) i nasadka
    for a in (0, 120, 240):
        sl.add(box(0.004, 0.045, 0.13, 0.002), 'leaf' if a == 0 else 'feather', kosc,
               F @ mtx((0, 0, 0.1), (0, 0, a)) @ mtx((0, 0.022, 0)))
    sl.add(cyl(0.016, 0.016, 0.02, 8), 'wood', kosc, F @ mtx((0, 0, 0.01)))


def w_dloni(sl, J):
    model_strzaly(sl, 'prop.R', mtx(J['prop.R']))


EFEKT = {
    'id': 'strzala',
    'nazwa': 'Strzała',
    'typ': 'pocisk',
    'paleta': PALETA,
    'model': model_strzaly,
    'w_dloni': w_dloni,
}
