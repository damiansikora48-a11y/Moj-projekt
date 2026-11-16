"""EFEKT ATAKU: głaz (pocisk).

model      – głaz jako osobny plik efekt_glaz.glb (gra wystrzeliwuje go w chwili 'release')
w_dloni    – ten sam głaz trzymany w dłoni (kość prop.R) przy ruchu z rekwizytem (np. rzut)
"""
from kit import V, box, cyl, sphere, ico, rock, cut_below, taper, jitter, mtx, frame, seg, SIDES, lerp, scale_m

PALETA = {
    'stone_light': ('#aaa293', 0.9),
    'stone_dark': ('#625b53', 0.95),
    'moss': ('#5f8f37', 0.95),
    'crystal': ('#3fb8e0', 0.15, 0.0, 0.7),
}


def model_glazu(sl, bone, M):
    """Głaz do rzucania (w dłoni golema i jako osobny pocisk)."""
    from mathutils import Matrix
    M = M if M is not None else Matrix.Identity(4)
    sl.add(jitter(ico(0.2, 2), 0.028, 501), 'stone_light', bone, M @ scale_m(1.05, 0.95, 0.9))
    sl.add(rock(0.16, 0.14, 0.12, 502), 'stone_dark', bone, M @ mtx((0.1, 0.06, -0.08), (10, 20, 0)))
    sl.add(jitter(sphere(0.13, 0.12, 0.04, 10, 6), 0.012, 503), 'moss', bone, M @ mtx((-0.02, 0.02, 0.16), (8, -6, 0)))
    for loc, rot in (((0.07, -0.12, 0.08), (-50, 0, 20)), ((-0.1, -0.1, 0.02), (-60, 0, -35))):
        sl.add(cyl(0.035, 0.035, 0.06, 6), 'crystal', bone, M @ mtx(loc, rot) @ mtx((0, 0, 0.03)))
        sl.add(cyl(0.035, 0.0, 0.05, 6), 'crystal', bone, M @ mtx(loc, rot) @ mtx((0, 0, 0.085)))


def w_dloni(sl, J):
    model_glazu(sl, 'prop.R', mtx(J['prop.R'] + J['hand_dir.R'] * 0.26) @ scale_m(1.3, 1.3, 1.3))


EFEKT = {
    'id': 'glaz',
    'nazwa': 'Głaz',
    'typ': 'pocisk',          # gra wystrzeliwuje model z kości prop.R
    'paleta': PALETA,
    'model': lambda sl: model_glazu(sl, 'root', None),
    'w_dloni': w_dloni,
}
