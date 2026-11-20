"""JEDNOSTKA: Leśny Łucznik – strzelec w zielonym kapturze, z łukiem i kołczanem.

Gdzie co jest w tym pliku:
  SZKIELET, PALETA – proporcje (smukły) i kolory
  glowa      – twarz z grzywką spod kaptura
  kaptur     – otwarty z przodu, z ostrym czubkiem z tyłu
  kaftan     – skórzany kaftan, tunika, pas, pas kołczanu, liść na piersi
  kolczan    – kołczan ze strzałami na plecach
  rece, nogi – rękawy, karwasze, rękawice; spodnie i wysokie buty
  luk        – łuk refleksyjny w lewej dłoni (z cięciwą)
  JEDNOSTKA  – złożenie; atak: ruch 'strzal' + efekt 'strzala'
"""
import math

from kit import V, box, cyl, sphere, ico, cut_below, taper, jitter, mtx, frame, seg, SIDES, scale_m

SZKIELET = dict(
    ankle=0.10, shin=0.37, thigh=0.38, hip_w=0.11, foot=0.20,
    spine=0.20, chest=0.28, neck=0.07, head=0.33, head_fwd=0.0,
    sh_w=0.24, sh_drop=0.06, upper_arm=0.28, forearm=0.26, hand=0.11,
    arm_angle=12, forearm_fwd=10,
)

PALETA = {
    'skin': ('#e6ad86', 0.6),
    'cloak': ('#3f6e2c', 0.85),
    'cloak_dark': ('#26451c', 0.85),
    'tunic': ('#6f8a3a', 0.85),
    'leather': ('#7a5230', 0.7),
    'leather_dark': ('#4a3020', 0.75),
    'trousers': ('#4a4232', 0.85),
    'hair': ('#a0602a', 0.85),
    'eye': ('#151515', 0.3),
    'eye_white': ('#f3eee4', 0.4),
    'wood': ('#7a5230', 0.8),
    'string': ('#efe6cc', 0.6),
    'feather': ('#e8e0d0', 0.85),
    'leaf': ('#5fa83a', 0.8),
    'leaf_dark': ('#3c7a26', 0.85),
    'steel': ('#aab3bd', 0.32, 0.85),
    'gold': ('#e0ac3c', 0.3, 0.9),
}


def _c(J):
    return J['neck_top'] + V(0, 0, 0.165)


def glowa(sl, J):
    c = _c(J)
    sl.add(cyl(0.06, 0.055, 0.12, 12), 'skin', 'neck', seg(J['sh'] - V(0, 0, 0.03), J['neck_top'] + V(0, 0, 0.04)))
    sl.add(sphere(0.15, 0.145, 0.165, 20, 14), 'skin', 'head', mtx(c))
    sl.add(box(0.04, 0.05, 0.07, 0.016), 'skin', 'head', mtx(c + V(0, -0.15, -0.02), (-8, 0, 0)))
    for sg in (1, -1):
        sl.add(sphere(0.03, 0.014, 0.028, 12, 8), 'eye_white', 'head', mtx(c + V(sg * 0.055, -0.138, 0.02)))
        sl.add(sphere(0.018, 0.012, 0.02, 10, 8), 'eye', 'head', mtx(c + V(sg * 0.051, -0.148, 0.018)))
        sl.add(box(0.055, 0.02, 0.014, 0.006), 'hair', 'head', mtx(c + V(sg * 0.056, -0.147, 0.058), (0, sg * 12, 0)))
    # włosy pod kapturem (czapka włosów nad czołem + kosmyki przy policzkach)
    sl.add(cut_below(sphere(0.158, 0.153, 0.15, 18, 12), 0.03), 'hair', 'head', mtx(c + V(0, 0.0, 0.04)))
    for sg in (1, -1):
        sl.add(box(0.035, 0.05, 0.12, 0.015), 'hair', 'head', mtx(c + V(sg * 0.115, -0.085, 0.0), (8, 0, sg * -6)))
    # grzywka spod kaptura i mały uśmiech
    for x, rz in ((-0.06, 12), (0.0, 0), (0.06, -12)):  # grzywka: trzy kosmyki
        sl.add(box(0.06, 0.04, 0.035, 0.015), 'hair', 'head', mtx(c + V(x, -0.12, 0.115), (-25, 0, rz)))
    sl.add(box(0.05, 0.02, 0.012, 0.004), 'leather_dark', 'head', mtx(c + V(0, -0.15, -0.075)))


def kaptur(sl, J):
    c = _c(J)
    b = 'head'
    import bmesh
    # otwór na twarz: owal (w jednostkach kuli) – czubek głowy zostaje zakryty
    OX, OZ0, OZ = 0.68, -0.01, 0.57

    def w_otworze(x, z):
        return (x / OX) ** 2 + ((z - OZ0) / OZ) ** 2 < 1.0
    shell = sphere(1, 1, 1, 28, 18)
    bmesh.ops.delete(shell, geom=[v for v in shell.verts if v.co.y < 0 and w_otworze(v.co.x, v.co.z)], context='VERTS')
    hc, R = c + V(0, 0.015, 0.015), V(0.185, 0.18, 0.2)
    sl.add(shell, 'cloak', b, mtx(hc) @ scale_m(*R))
    # czubek kaptura opadający do tyłu
    p0, p1 = c + V(0, 0.13, 0.12), c + V(0, 0.27, -0.02)
    sl.add(cyl(0.07, 0.012, (p1 - p0).length, 10), 'cloak', b, seg(p0, p1))
    # obrzeże twarzy
    rim = []
    for i in range(25):  # lamówka dokładnie po krawędzi otworu
        t = 2 * math.pi * i / 24
        nx, nz = OX * math.cos(t), OZ0 + OZ * math.sin(t)
        ny = -math.sqrt(max(0.0, 1 - nx * nx - nz * nz))
        rim.append(hc + V(nx * R.x, ny * R.y, nz * R.z))
    for p, q in zip(rim, rim[1:]):
        sl.add(cyl(0.019, 0.019, (q - p).length + 0.012, 8), 'cloak_dark', b, seg(p, q))
    # kołnierz kaptura opadający na barki
    sl.add(cyl(0.22, 0.13, 0.12, 22, 0.01), 'cloak', 'chest', mtx(J['sh'] + V(0, 0.01, 0.0)))
    sl.add(jitter(sphere(0.05, 0.02, 0.025, 10, 6), 0.004, 77), 'leaf', 'chest', mtx(J['sh'] + V(0.1, -0.15, -0.02), (10, 30, 0)))
    sl.add(sphere(0.016, u=8, v=6), 'gold', 'chest', mtx(J['sh'] + V(0.1, -0.165, -0.02)))


def kaftan(sl, J):
    hz, cz, sz = J['hip'].z, J['chest_base'].z, J['sh'].z
    sl.add(box(0.3, 0.21, 0.16, 0.05), 'tunic', 'hips', mtx((0, 0, hz)))
    sl.add(box(0.31, 0.22, 0.24, 0.06), 'tunic', 'spine', mtx((0, 0, (hz + cz) / 2 + 0.03)))
    sl.add(taper(box(0.4, 0.25, 0.3, 0.08, 3), 0.85, 1.0), 'leather', 'chest', mtx((0, 0, cz + 0.14)))
    # sznurowanie kaftana
    for i in range(4):
        sl.add(box(0.07, 0.015, 0.012, 0.004), 'leather_dark', 'chest', mtx((0, -0.128, cz + 0.06 + i * 0.05), (0, 18 if i % 2 else -18, 0)))
    # liść na piersi
    sl.add(jitter(sphere(0.045, 0.012, 0.07, 10, 6), 0.003, 78), 'leaf', 'chest', mtx((-0.1, -0.13, cz + 0.2), (0, 20, 0)))
    # pas z klamrą + pas kołczanu na ukos
    bz = cz - 0.04
    sl.add(cyl(0.18, 0.18, 0.05, 22, 0.008), 'leather_dark', 'spine', mtx((0, 0, bz)) @ scale_m(1, 0.74, 1))
    sl.add(box(0.06, 0.02, 0.05, 0.01), 'gold', 'spine', mtx((0, -0.135, bz)))
    a, b = V(0.17, -0.12, cz + 0.02), V(-0.14, -0.13, sz - 0.02)
    sl.add(box(0.045, 0.018, (b - a).length), 'leather_dark', 'chest', seg(a, b, (0, 1, 0)))
    a, b = V(0.17, 0.12, cz + 0.02), V(-0.14, 0.13, sz - 0.02)
    sl.add(box(0.045, 0.018, (b - a).length), 'leather_dark', 'chest', seg(a, b, (0, 1, 0)))
    # poły tuniki przypięte do ud
    for sg, S in SIDES:
        for y in (-0.115, 0.115):
            fl = mtx((sg * 0.075, y, hz - 0.11), (-5 if y < 0 else 5, 0, 0))
            sl.add(box(0.15, 0.022, 0.22, 0.008), 'tunic', 'thigh' + S, fl)
            sl.add(box(0.155, 0.026, 0.02, 0.006), 'cloak_dark', 'thigh' + S, fl @ mtx((0, 0, -0.105)))


def kolczan(sl, J):
    sz = J['sh'].z
    M = mtx((0.08, 0.17, sz - 0.2), (-10, -25, 0))
    sl.add(cyl(0.065, 0.075, 0.46, 14, 0.008), 'leather', 'chest', M)
    sl.add(cyl(0.078, 0.078, 0.03, 14), 'leather_dark', 'chest', M @ mtx((0, 0, 0.2)))
    sl.add(cyl(0.078, 0.078, 0.03, 14), 'leather_dark', 'chest', M @ mtx((0, 0, -0.18)))
    for i, (x, y) in enumerate(((0.025, 0.0), (-0.025, 0.01), (0.0, -0.028), (0.0, 0.03), (-0.03, -0.02))):
        sl.add(cyl(0.008, 0.008, 0.16, 6), 'wood', 'chest', M @ mtx((x, y, 0.3)))
        for a in (0, 120, 240):
            sl.add(box(0.003, 0.03, 0.09, 0.002), 'leaf' if (i + a) % 3 == 0 else 'feather', 'chest',
                   M @ mtx((x, y, 0.33), (0, 0, a + i * 20)) @ mtx((0, 0.016, 0)))


def rece(sl, J):
    for sg, S in SIDES:
        sh, el, wr = J['shoulder' + S], J['elbow' + S], J['wrist' + S]
        d2 = J['hand_dir' + S]
        sl.add(sphere(0.08, u=14, v=10), 'tunic', 'shoulder' + S, mtx(sh))
        if sg > 0:  # skórzany naramiennik na lewym barku (strona łuku)
            sl.add(sphere(0.11, 0.11, 0.06, 14, 8), 'leather', 'shoulder' + S, mtx(sh + V(0.02, 0, 0.03), (0, -20, 0)))
        sl.add(cyl(0.068, 0.062, (el - sh).length, 14), 'tunic', 'upper_arm' + S, seg(sh, el))
        sl.add(cyl(0.065, 0.075, (wr - el).length * 0.85, 14), 'leather', 'forearm' + S, seg(el + (wr - el) * 0.12, wr))
        for t in (0.3, 0.7):
            p = el + (wr - el) * t
            sl.add(cyl(0.078, 0.078, 0.018, 14), 'leather_dark', 'forearm' + S, seg(p - d2 * 0.009, p + d2 * 0.009))
        hm = frame(wr + d2 * 0.07, d2, (1, 0, 0))
        sl.add(box(0.085, 0.1, 0.095, 0.03), 'leather_dark', 'hand' + S, hm)
        sl.add(box(0.03, 0.04, 0.05, 0.012), 'leather_dark', 'hand' + S, hm @ mtx((-sg * 0.045, -0.03, -0.005), (0, 0, sg * 15)))


def nogi(sl, J):
    for sg, S in SIDES:
        hp, kn, an = J['hipj' + S], J['knee' + S], J['ankle' + S]
        sl.add(cyl(0.085, 0.07, (kn - hp).length, 14), 'trousers', 'thigh' + S, seg(hp, kn))
        ft = V(hp.x, 0, 0)
        sl.add(cyl(0.075, 0.08, 0.3, 14), 'leather', 'shin' + S, seg(ft + V(0, 0, 0.04), kn - V(0, 0, 0.02)))
        sl.add(cyl(0.09, 0.085, 0.06, 14, 0.008), 'leather_dark', 'shin' + S, seg(kn - V(0, 0, 0.06), kn + V(0, 0, 0.0)))
        sl.add(box(0.11, 0.22, 0.08, 0.03), 'leather', 'foot' + S, mtx(ft + V(0, -0.05, 0.04)))
        sl.add(box(0.115, 0.23, 0.02, 0.006), 'leather_dark', 'foot' + S, mtx(ft + V(0, -0.05, 0.01)))


def luk(sl, J):
    """Łuk refleksyjny w lewej dłoni: oś pionowa, ramiona zaginają się ku łucznikowi (+Y)."""
    wr, d2 = J['wrist.L'], J['hand_dir.L']
    g = wr + d2 * 0.07
    b = 'hand.L'
    H = 0.55
    pts = []
    for i in range(13):
        t = -1 + 2 * i / 12
        y = 0.13 * t * t - 0.035 * (t ** 6)  # łuk + lekkie odgięcie końców
        pts.append(g + V(0, y + 0.0, t * H))
    for i, (a, c) in enumerate(zip(pts, pts[1:])):
        r = 0.026 - 0.012 * abs((i + 0.5) / 6 - 1)
        sl.add(cyl(r, r, (c - a).length + 0.01, 8), 'wood', b, seg(a, c, (1, 0, 0)))
    sl.add(cyl(0.032, 0.032, 0.14, 10), 'leather_dark', b, mtx(g))
    for z in (-0.08, 0.08):
        sl.add(cyl(0.034, 0.034, 0.015, 10), 'gold', b, mtx(g + V(0, 0, z)))
    # cięciwa między końcami
    sl.add(cyl(0.005, 0.005, (pts[-1] - pts[0]).length, 6), 'string', b, seg(pts[0], pts[-1]))
    # liście przy uchwycie
    for k, (x, z) in enumerate(((0.03, 0.12), (-0.03, -0.12))):
        sl.add(jitter(sphere(0.04, 0.01, 0.06, 10, 6), 0.003, 80 + k), 'leaf', b, mtx(g + V(x, -0.02, z), (0, 25 if x > 0 else -25, 0)))


JEDNOSTKA = {
    'id': 'lesny_lucznik',
    'nazwa': 'Leśny Łucznik',
    'opis': 'Strzelec w zielonym kapturze, z łukiem refleksyjnym i kołczanem. Strzela z murów.',
    'rola': 'strzelec',
    'zywiol': 'natura',
    'szkielet': SZKIELET,
    'paleta': PALETA,
    'czesci': {
        'Head': glowa, 'Headgear': kaptur, 'Body': kaftan, 'Back': kolczan,
        'Arms': rece, 'Legs': nogi, 'Offhand': luk,
    },
    'chod': dict(walk_frames=30, idle_frames=76, thigh=24, knee=44, knee_base=4, arm=18,
                 **{'arm_scale.R': 0.8, 'arm_scale.L': 0.35, 'forearm_base.R': 18, 'forearm_base.L': 20},
                 twist=5, sway=2, lean=3, bob=0.022, breath=1.6, breath_loc=0.006),
    'atak': {'ruch': 'strzal', 'efekt': 'strzala'},
    'tagi': {'material': 'skora', 'wielkosc': 'srednia'},
}
