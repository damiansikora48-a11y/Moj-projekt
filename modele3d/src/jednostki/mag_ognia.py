"""JEDNOSTKA: Mag ognia – czarodziej w szacie z kosturem, ciska kulami ognia.

Gdzie co jest w tym pliku:
  SZKIELET, PALETA – proporcje i kolory (ogień świeci: 4. liczba w PALETA)
  glowa      – twarz z długą białą brodą
  kapelusz   – spiczasty, z zagiętym czubkiem (mocna sylwetka z kamery 52°)
  szata      – tułów, pelerynka na ramionach, szarfa z fiolką, poły szaty
  rece       – dzwonowe rękawy
  nogi       – szata rozszerzająca się ku dołowi, zakręcone buty
  kostur     – drewniane szpony trzymające ognisty kryształ
  plomien    – płomień unoszący się nad lewą dłonią
  JEDNOSTKA  – złożenie; atak: ruch 'czar' + efekt 'kula_ognia'
"""
import math

from kit import V, box, cyl, sphere, ico, taper, jitter, mtx, frame, seg, SIDES, scale_m

SZKIELET = dict(
    ankle=0.08, shin=0.34, thigh=0.36, hip_w=0.11, foot=0.18,
    spine=0.20, chest=0.28, neck=0.06, head=0.34, head_fwd=0.0,
    sh_w=0.24, sh_drop=0.06, upper_arm=0.26, forearm=0.25, hand=0.11,
    arm_angle=12, forearm_fwd=14,
)

PALETA = {
    'skin': ('#e8b08a', 0.6),
    'robe': ('#b3302a', 0.8),
    'robe_dark': ('#6e1d1b', 0.85),
    'gold': ('#e0ac3c', 0.3, 0.9),
    'sash': ('#e8892a', 0.75),
    'beard': ('#ece6da', 0.9),
    'wood': ('#6b4423', 0.85),
    'leather': ('#77482a', 0.7),
    'leather_dark': ('#3e2817', 0.75),
    'eye': ('#151515', 0.3),
    'eye_white': ('#f3eee4', 0.4),
    'potion': ('#ff9a2a', 0.15, 0.0, 2.5),
    'fire': ('#ff7a1a', 0.4, 0.0, 6.0),
    'fire_core': ('#ffd66b', 0.3, 0.0, 12.0),
    'ember': ('#ff4a1a', 0.5, 0.0, 3.5),
}


def _srodek_glowy(J):
    return J['neck_top'] + V(0, 0, 0.17)


def glowa(sl, J):
    c = _srodek_glowy(J)
    sl.add(cyl(0.06, 0.055, 0.12, 12), 'skin', 'neck', seg(J['sh'] - V(0, 0, 0.03), J['neck_top'] + V(0, 0, 0.04)))
    sl.add(sphere(0.155, 0.15, 0.17, 20, 14), 'skin', 'head', mtx(c))
    sl.add(box(0.05, 0.055, 0.085, 0.02), 'skin', 'head', mtx(c + V(0, -0.155, -0.02), (-10, 0, 0)))
    for sg in (1, -1):
        sl.add(sphere(0.03, 0.014, 0.028, 12, 8), 'eye_white', 'head', mtx(c + V(sg * 0.056, -0.14, 0.02)))
        sl.add(sphere(0.018, 0.012, 0.02, 10, 8), 'eye', 'head', mtx(c + V(sg * 0.052, -0.15, 0.018)))
        sl.add(box(0.085, 0.035, 0.03, 0.012), 'beard', 'head', mtx(c + V(sg * 0.06, -0.145, 0.058), (0, sg * 14, 0)))
        sl.add(sphere(0.018, 0.04, 0.045, 10, 8), 'skin', 'head', mtx(c + V(sg * 0.153, 0.0, -0.005)))
    sl.add(sphere(0.155, 0.15, 0.12, 16, 10), 'beard', 'head', mtx(c + V(0, 0.035, -0.05)))
    # długa broda zwężająca się ku dołowi + wąsy
    sl.add(taper(box(0.24, 0.12, 0.3, 0.05, 3), bottom=0.45, top=1.0), 'beard', 'head', mtx(c + V(0, -0.085, -0.2), (10, 0, 0)))
    for sg in (1, -1):
        sl.add(box(0.1, 0.035, 0.035, 0.014), 'beard', 'head', mtx(c + V(sg * 0.045, -0.16, -0.06), (0, sg * -22, 0)))


def kapelusz(sl, J):
    c = _srodek_glowy(J)
    b = 'head'
    sl.add(cyl(0.3, 0.28, 0.035, 32, 0.008), 'robe_dark', b, mtx(c + V(0, 0.02, 0.12), (-13, 0, 0)))  # rondo zadarte z przodu
    sl.add(cyl(0.195, 0.19, 0.06, 24), 'gold', b, mtx(c + V(0, 0.01, 0.155)))
    sl.add(ico(0.032, 1), 'fire_core', b, mtx(c + V(0, -0.19, 0.155)))
    p, kat = c + V(0, 0.01, 0.17), 0.0
    for r1, r2, L, zgiecie in ((0.185, 0.13, 0.2, 5), (0.13, 0.08, 0.17, 16), (0.08, 0.035, 0.15, 32), (0.035, 0.004, 0.12, 52)):
        kat += zgiecie
        d = V(0, math.sin(math.radians(kat)), math.cos(math.radians(kat)))  # zagina się do tyłu
        sl.add(cyl(r1, r2, L, 18), 'robe_dark', b, seg(p, p + d * L))
        p = p + d * L * 0.92
    # gwiazdki-iskry na kapeluszu
    for loc in ((0.1, -0.14, 0.27), (-0.08, -0.1, 0.4), (0.05, -0.02, 0.5)):
        sl.add(box(0.03, 0.012, 0.03, 0.004), 'ember', b, mtx(c + V(*loc), (0, 45, 0)))


def szata(sl, J):
    hz, cz, sz = J['hip'].z, J['chest_base'].z, J['sh'].z
    sl.add(box(0.3, 0.22, 0.16, 0.05), 'robe', 'hips', mtx((0, 0, hz)))
    sl.add(box(0.32, 0.23, 0.24, 0.06), 'robe', 'spine', mtx((0, 0, (hz + cz) / 2 + 0.03)))
    sl.add(taper(box(0.4, 0.26, 0.32, 0.08, 3), 0.85, 1.0), 'robe', 'chest', mtx((0, 0, cz + 0.15)))
    for sg in (1, -1):
        sl.add(box(0.025, 0.02, 0.3, 0.006), 'gold', 'chest', mtx((sg * 0.045, -0.132, cz + 0.13)))
    # pelerynka na ramionach i kołnierz
    sl.add(cyl(0.29, 0.15, 0.16, 24, 0.01), 'robe_dark', 'chest', mtx((0, 0.01, sz - 0.02)))
    sl.add(cyl(0.292, 0.292, 0.02, 24), 'gold', 'chest', mtx((0, 0.01, sz - 0.1)))
    sl.add(cyl(0.12, 0.14, 0.08, 18), 'robe_dark', 'chest', mtx((0, 0.02, sz + 0.06)))
    sl.add(ico(0.03, 1), 'ember', 'chest', mtx((0, -0.12, sz + 0.02)))
    # szarfa z węzłem i fiolka z ogniem
    bz = cz - 0.04
    sl.add(cyl(0.185, 0.185, 0.06, 24, 0.01), 'sash', 'spine', mtx((0, 0, bz)) @ scale_m(1, 0.75, 1))
    sl.add(box(0.07, 0.04, 0.07, 0.02), 'sash', 'spine', mtx((0.08, -0.14, bz)))
    sl.add(box(0.04, 0.025, 0.16, 0.01), 'sash', 'spine', mtx((0.1, -0.145, bz - 0.1), (0, -10, 0)))
    sl.add(box(0.04, 0.025, 0.13, 0.01), 'sash', 'spine', mtx((0.06, -0.145, bz - 0.09), (0, 8, 0)))
    sl.add(sphere(0.042, u=12, v=8), 'potion', 'spine', mtx((-0.17, -0.07, bz - 0.06)))
    sl.add(cyl(0.015, 0.015, 0.04, 8), 'potion', 'spine', mtx((-0.17, -0.07, bz - 0.01)))
    sl.add(cyl(0.018, 0.018, 0.015, 8), 'leather', 'spine', mtx((-0.17, -0.07, bz + 0.016)))
    # poły szaty przypięte do ud (nie przenikają nóg w chodzie)
    for sg, S in SIDES:
        for y in (-0.12, 0.12):
            fl = mtx((sg * 0.075, y, hz - 0.16), (-4 if y < 0 else 4, 0, 0))
            sl.add(box(0.15, 0.022, 0.34, 0.008), 'robe_dark', 'thigh' + S, fl)
            sl.add(box(0.155, 0.028, 0.025, 0.006), 'gold', 'thigh' + S, fl @ mtx((0, 0, -0.16)))
        sl.add(box(0.05, 0.02, 0.05, 0.008), 'ember', 'thigh' + S, mtx((sg * 0.075, -0.135, hz - 0.22), (0, 45, 0)))


def rece(sl, J):
    for sg, S in SIDES:
        sh, el, wr = J['shoulder' + S], J['elbow' + S], J['wrist' + S]
        d2 = J['hand_dir' + S]
        sl.add(sphere(0.085, u=14, v=10), 'robe', 'shoulder' + S, mtx(sh))
        sl.add(cyl(0.075, 0.08, (el - sh).length, 14), 'robe', 'upper_arm' + S, seg(sh, el))
        sl.add(cyl(0.085, 0.14, (wr - el).length + 0.01, 16), 'robe', 'forearm' + S, seg(el, wr + d2 * 0.01))
        sl.add(cyl(0.143, 0.143, 0.025, 16), 'gold', 'forearm' + S, seg(wr - d2 * 0.015, wr + d2 * 0.012))
        sl.add(cyl(0.04, 0.045, 0.07, 10), 'skin', 'hand' + S, seg(wr - d2 * 0.035, wr + d2 * 0.035))
        hm = frame(wr + d2 * 0.075, d2, (1, 0, 0))
        sl.add(box(0.09, 0.1, 0.1, 0.03), 'skin', 'hand' + S, hm)
        sl.add(box(0.03, 0.045, 0.055, 0.012), 'skin', 'hand' + S, hm @ mtx((-sg * 0.05, -0.03, -0.005), (0, 0, sg * 15)))


def nogi(sl, J):
    for sg, S in SIDES:
        hp, kn, an = J['hipj' + S], J['knee' + S], J['ankle' + S]
        sl.add(cyl(0.11, 0.12, (kn - hp).length, 16), 'robe', 'thigh' + S, seg(hp, kn))
        dol = an - V(0, 0, 0.045)
        sl.add(cyl(0.12, 0.165, (dol - kn).length, 18), 'robe', 'shin' + S, seg(kn, dol))
        sl.add(cyl(0.168, 0.168, 0.025, 18), 'gold', 'shin' + S, mtx(dol + V(0, 0, 0.012)))
        ft = V(hp.x, 0, 0)
        sl.add(box(0.11, 0.2, 0.08, 0.03), 'leather_dark', 'foot' + S, mtx(ft + V(0, -0.06, 0.04)))
        sl.add(cyl(0.045, 0.0, 0.11, 8), 'leather_dark', 'foot' + S, mtx(ft + V(0, -0.18, 0.06), (70, 0, 0)))


def kostur(sl, J):
    wr, d2 = J['wrist.R'], J['hand_dir.R']
    F = frame(wr + d2 * 0.075, V(0.0, -0.12, 1.0), (1, 0, 0))
    b = 'hand.R'
    sl.add(cyl(0.028, 0.024, 1.9, 10), 'wood', b, F @ mtx((0, 0, 0.25)))
    for z in (-0.12, 0.1, 1.05):
        sl.add(cyl(0.034, 0.034, 0.03, 10), 'gold', b, F @ mtx((0, 0, z)))
    sl.add(cyl(0.0, 0.03, 0.08, 8), 'gold', b, F @ mtx((0, 0, -0.74)))
    top = 1.2
    for i in range(3):
        a = 2 * math.pi * i / 3
        base = V(math.cos(a) * 0.03, math.sin(a) * 0.03, top)
        kolano = V(math.cos(a) * 0.09, math.sin(a) * 0.09, top + 0.15)
        koniec = V(math.cos(a) * 0.045, math.sin(a) * 0.045, top + 0.27)
        sl.add(cyl(0.022, 0.013, (kolano - base).length, 8), 'wood', b, F @ seg(base, kolano))
        sl.add(cyl(0.013, 0.004, (koniec - kolano).length, 8), 'wood', b, F @ seg(kolano, koniec))
    sl.add(ico(0.075, 1), 'fire_core', b, F @ mtx((0, 0, top + 0.16)) @ scale_m(1, 1, 1.25))
    for a, h in ((0.0, 0.22), (2.1, 0.17), (4.2, 0.19)):
        p = V(math.cos(a) * 0.035, math.sin(a) * 0.035, top + 0.2)
        sl.add(cyl(0.045, 0.0, h, 6), 'fire', b, F @ seg(p, p + V(math.cos(a) * 0.04, math.sin(a) * 0.04, h)))


def plomien(sl, J):
    """Płomień unoszący się nad lewą dłonią."""
    wr, d2 = J['wrist.L'], J['hand_dir.L']
    p = wr + d2 * 0.1 + V(0.0, -0.1, 0.04)
    b = 'hand.L'
    sl.add(ico(0.045, 1), 'fire_core', b, mtx(p))
    for a, h in ((0.0, 0.15), (2.1, 0.11), (4.2, 0.12)):
        q = p + V(math.cos(a) * 0.025, math.sin(a) * 0.025, 0.01)
        sl.add(cyl(0.035, 0.0, h, 6), 'fire', b, seg(q, q + V(math.cos(a) * 0.025, math.sin(a) * 0.025, h)))
    for x, z in ((0.05, 0.13), (-0.04, 0.17)):
        sl.add(box(0.018, 0.018, 0.018, 0.004), 'ember', b, mtx(p + V(x, 0, z), (45, 45, 0)))


JEDNOSTKA = {
    'id': 'mag_ognia',
    'nazwa': 'Mag ognia',
    'opis': 'Czarodziej w czerwonej szacie i spiczastym kapeluszu, z kosturem z ognistym kryształem. Ciska kulami ognia.',
    'rola': 'mag',          # patrz siatka.py
    'zywiol': 'ogien',
    'szkielet': SZKIELET,
    'paleta': PALETA,
    'czesci': {
        'Head': glowa, 'Headgear': kapelusz, 'Body': szata, 'Arms': rece, 'Legs': nogi,
        'Weapon': kostur, 'Offhand': plomien,
    },
    'chod': dict(walk_frames=34, idle_frames=80, thigh=22, knee=40, knee_base=4, arm=14,
                 **{'arm_scale.R': 0.3, 'arm_scale.L': 0.6, 'forearm_base.R': 24, 'forearm_base.L': 30},
                 twist=4, sway=2.5, lean=2, bob=0.02, breath=1.8, breath_loc=0.006),
    'atak': {'ruch': 'czar', 'efekt': 'kula_ognia'},
    'tagi': {'material': 'tkanina', 'wielkosc': 'srednia', 'zywiol': 'ogien'},
}
