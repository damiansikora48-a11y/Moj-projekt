"""JEDNOSTKA: Golem – kamienny kolos rzucający głazami.

Gdzie co jest w tym pliku:
  SZKIELET, PALETA – proporcje i kolory
  tulow, glowa, rece, nogi – wygląd części
  JEDNOSTKA – złożenie: sloty, chód, atak
Głaz w dłoni i głaz-pocisk to ten sam model z ataki/efekty/glaz.py (slot Prop dodawany automatycznie).
"""
import math

from kit import V, box, cyl, sphere, ico, rock, cut_below, taper, jitter, mtx, frame, seg, SIDES, lerp, scale_m

SZKIELET = dict(
    ankle=0.14, shin=0.34, thigh=0.36, hip_w=0.30, foot=0.38,
    spine=0.30, chest=0.62, neck=0.10, head=0.32, head_fwd=0.27,
    sh_w=0.62, sh_drop=0.14, upper_arm=0.48, forearm=0.52, hand=0.30,
    arm_angle=16, forearm_fwd=14,
)

PALETA = {
    'stone': ('#8c847a', 0.92),
    'stone_dark': ('#625b53', 0.95),
    'stone_light': ('#aaa293', 0.9),
    'moss': ('#5f8f37', 0.95),
    'moss_dark': ('#3e6626', 0.95),
    'rune': ('#2fd0ff', 0.4, 0.0, 4.0),
    'crystal': ('#3fb8e0', 0.15, 0.0, 0.7),
    'core': ('#8ff4ff', 0.2, 0.0, 9.0),
}


def _stone(i):
    return ('stone', 'stone_dark', 'stone_light')[i % 3]


def tulow(sl, J):
    hz, cz, sz = J['hip'].z, J['chest_base'].z, J['sh'].z
    sl.add(rock(0.62, 0.42, 0.30, 1), 'stone_dark', 'hips', mtx((0, 0.02, hz)))
    sl.add(sphere(0.16, u=14, v=10), 'core', 'spine', mtx((0, 0.0, hz + 0.17)))
    sl.add(rock(0.44, 0.34, 0.18, 2), 'stone', 'spine', mtx((0, 0.0, hz + 0.19), (0, 4, 6)))
    sl.add(rock(0.5, 0.38, 0.16, 3), 'stone_light', 'spine', mtx((0, 0.01, cz - 0.02), (0, -3, -4)))
    # masywna klatka
    chest = taper(rock(1.0, 0.64, 0.64, 4, rough=0.08), bottom=0.62, top=1.0, axis='x')
    sl.add(chest, 'stone', 'chest', mtx((0, 0.05, cz + 0.33)))
    for sg in (1, -1):
        sl.add(rock(0.42, 0.2, 0.34, 5 + sg), 'stone_light', 'chest', mtx((sg * 0.23, -0.27, cz + 0.38), (4, 0, sg * 6)))
        # pęknięcia-runy na piersi
        p0 = V(sg * 0.16, -0.385, cz + 0.48)
        pts = [p0, p0 + V(sg * 0.07, 0, -0.08), p0 + V(sg * 0.04, 0, -0.16), p0 + V(sg * 0.11, 0, -0.24)]
        for a, b in zip(pts, pts[1:]):
            sl.add(box(0.022, 0.025, (b - a).length + 0.02), 'rune', 'chest', seg(a, b, (0, 1, 0)))
    # rdzeń + promienie runiczne
    core_p = V(0, -0.33, cz + 0.16)
    sl.add(ico(0.11, 1), 'core', 'chest', mtx(core_p) @ scale_m(1, 0.7, 1.25))
    for i in range(8):
        a = 2 * math.pi * i / 8
        d = V(math.cos(a), 0, math.sin(a))
        sl.add(box(0.025, 0.02, 0.07), 'rune', 'chest', seg(core_p + d * 0.14, core_p + d * 0.22, (0, 1, 0)))
    sl.add(rock(0.34, 0.12, 0.12, 9), 'stone_dark', 'chest', mtx(core_p + V(0, -0.02, -0.17)))
    # mech na barkach i kryształy na plecach
    sl.add(jitter(sphere(0.36, 0.24, 0.06, 14, 6), 0.02, 11), 'moss', 'chest', mtx((0, 0.16, sz + 0.0)))
    crystals = [((0.0, 0.34, sz - 0.05), (-35, 0, 0), 0.42), ((0.18, 0.33, sz - 0.18), (-40, -20, 0), 0.32),
                ((-0.17, 0.35, sz - 0.12), (-45, 22, 0), 0.36), ((0.08, 0.37, sz - 0.32), (-55, -8, 0), 0.24),
                ((-0.1, 0.36, sz - 0.36), (-60, 12, 0), 0.2)]
    for loc, rot, L in crystals:
        M = mtx(loc, rot)
        sl.add(cyl(0.065 * L / 0.3, 0.065 * L / 0.3, L * 0.7, 6), 'crystal', 'chest', M @ mtx((0, 0, L * 0.35)))
        sl.add(cyl(0.065 * L / 0.3, 0.0, L * 0.3, 6), 'crystal', 'chest', M @ mtx((0, 0, L * 0.85)))


def glowa(sl, J):
    c = J['neck_top'] + V(0, 0, 0.12)
    sl.add(rock(0.32, 0.30, 0.27, 21), 'stone_dark', 'head', mtx(c))
    sl.add(rock(0.38, 0.13, 0.09, 22), 'stone', 'head', mtx(c + V(0, -0.14, 0.07), (-8, 0, 0)))
    for sg in (1, -1):
        sl.add(box(0.085, 0.03, 0.05, 0.01), 'core', 'head', mtx(c + V(sg * 0.08, -0.158, 0.0), (0, sg * -10, 0)))
    sl.add(rock(0.28, 0.22, 0.11, 23), 'stone', 'head', mtx(c + V(0, -0.06, -0.14), (10, 0, 0)))
    sl.add(jitter(sphere(0.13, 0.12, 0.035, 10, 6), 0.012, 24), 'moss', 'head', mtx(c + V(0.02, 0.03, 0.14)))
    sl.add(cyl(0.035, 0.0, 0.16, 6), 'crystal', 'head', mtx(c + V(-0.1, 0.05, 0.18), (-20, -25, 0)))


def rece(sl, J):
    for sg, S in SIDES:
        sh, el, wr = J['shoulder' + S], J['elbow' + S], J['wrist' + S]
        d2 = J['hand_dir' + S]
        k = 30 if sg > 0 else 60
        # głaz barkowy z czapą mchu i kryształami
        boulder = jitter(ico(0.27, 2), 0.03, k)
        sl.add(boulder, 'stone', 'shoulder' + S, mtx(sh + V(sg * 0.07, 0.04, 0.06)) @ scale_m(1.05, 1, 0.92))
        sl.add(jitter(sphere(0.27, 0.25, 0.09, 14, 7), 0.025, k + 1), 'moss', 'shoulder' + S,
               mtx(sh + V(sg * 0.07, 0.05, 0.25)))
        sl.add(jitter(sphere(0.12, 0.1, 0.05, 10, 6), 0.015, k + 2), 'moss_dark', 'shoulder' + S,
               mtx(sh + V(sg * 0.22, 0.1, 0.2)))
        sl.add(cyl(0.05, 0.05, 0.16, 6), 'crystal', 'shoulder' + S, mtx(sh + V(sg * 0.12, 0.18, 0.24), (-30, -sg * 20, 0)))
        sl.add(cyl(0.05, 0.0, 0.09, 6), 'crystal', 'shoulder' + S, mtx(sh + V(sg * 0.12, 0.18, 0.24), (-30, -sg * 20, 0)) @ mtx((0, 0, 0.125)))
        # ramię
        for i, t in enumerate((0.3, 0.72)):
            sl.add(rock(0.27, 0.27, 0.24, k + 3 + i), _stone(i + 1), 'upper_arm' + S,
                   seg(lerp(sh, el, t) - (el - sh) * 0.001, lerp(sh, el, t) + (el - sh) * 0.001))
        sl.add(sphere(0.1, u=14, v=10), 'core', 'forearm' + S, mtx(el))
        sl.add(rock(0.22, 0.2, 0.2, k + 6), 'stone_dark', 'forearm' + S, mtx(el + V(sg * 0.02, 0.1, 0.0)))
        # przedramię (szersze ku dłoni)
        fa = taper(rock(0.36, 0.36, 0.46, k + 7, rough=0.08), bottom=0.72, top=1.0)
        sl.add(fa, 'stone', 'forearm' + S, seg(lerp(el, wr, 0.08), lerp(el, wr, 0.98)) @ mtx(rot=(180, 0, 0)))
        for off in (-0.06, 0.06):
            a, b = lerp(el, wr, 0.3), lerp(el, wr, 0.8)
            o = V(sg * 0.19, off, 0)
            sl.add(box(0.02, 0.025, (b - a).length), 'rune', 'forearm' + S, seg(a + o, b + o, (0, 1, 0)))
        sl.add(jitter(sphere(0.13, 0.12, 0.04, 10, 6), 0.015, k + 8), 'moss', 'forearm' + S,
               mtx(lerp(el, wr, 0.45) + V(sg * 0.05, 0.12, 0.08), (-30, 0, 0)))
        sl.add(sphere(0.085, u=12, v=8), 'core', 'hand' + S, mtx(wr))
        # pięść z kłykciami
        H = frame(wr + d2 * 0.22, d2, (1, 0, 0)) @ scale_m(1.2, 1.2, 1.15)
        sl.add(rock(0.38, 0.36, 0.32, k + 9, rough=0.07), 'stone_dark', 'hand' + S, H)
        for i in range(4):
            x = (-0.13 + i * 0.087)
            sl.add(rock(0.08, 0.09, 0.09, k + 10 + i), 'stone_light', 'hand' + S, H @ mtx((x, -0.17, 0.1)))
        sl.add(rock(0.11, 0.12, 0.16, k + 15), 'stone', 'hand' + S, H @ mtx((-sg * 0.2, -0.08, -0.02), (0, 0, sg * 12)))


def nogi(sl, J):
    for sg, S in SIDES:
        hp, kn, an = J['hipj' + S], J['knee' + S], J['ankle' + S]
        k = 80 if sg > 0 else 90
        sl.add(rock(0.36, 0.36, 0.3, k), 'stone_dark', 'thigh' + S, mtx(lerp(hp, kn, 0.5)))
        sl.add(sphere(0.085, u=12, v=8), 'core', 'shin' + S, mtx(kn))
        sl.add(rock(0.22, 0.14, 0.2, k + 1), 'stone_light', 'shin' + S, mtx(kn + V(0, -0.14, 0)))
        shin = taper(rock(0.34, 0.34, 0.3, k + 2, rough=0.08), bottom=1.12, top=0.85)
        sl.add(shin, 'stone', 'shin' + S, mtx(lerp(kn, an, 0.5) + V(0, 0, 0.02)))
        ft = V(hp.x, 0, 0)
        sl.add(rock(0.42, 0.5, 0.18, k + 3, rough=0.06), 'stone_dark', 'foot' + S, mtx(ft + V(0, -0.06, 0.09)))
        for i, x in enumerate((-0.13, 0.0, 0.13)):
            sl.add(rock(0.12, 0.11, 0.1, k + 4 + i), 'stone', 'foot' + S, mtx(ft + V(x, -0.33, 0.06)))
        sl.add(jitter(sphere(0.12, 0.1, 0.035, 10, 6), 0.012, k + 9), 'moss', 'foot' + S, mtx(ft + V(sg * 0.08, 0.05, 0.19)))


JEDNOSTKA = {
    'id': 'golem',
    'nazwa': 'Golem',
    'opis': 'Kamienny kolos z mchem, kryształami i świecącymi runami.',
    'rola': 'kolos',          # patrz siatka.py
    'zywiol': 'kamien',
    'kotwice': {'bark': 0.34},  # ozdoby żywiołu nad głazami barkowymi
    'szkielet': SZKIELET,
    'paleta': PALETA,
    'czesci': {'Body': tulow, 'Head': glowa, 'Arms': rece, 'Legs': nogi},
    'chod': dict(walk_frames=48, idle_frames=96, thigh=18, knee=32, knee_base=3, arm=16,
                 **{'arm_scale.R': 1.0, 'arm_scale.L': 1.0, 'forearm_base.R': 10, 'forearm_base.L': 10},
                 twist=7, sway=5, lean=6, bob=0.035, breath=2.2, breath_loc=0.012,
                 smierc='przod'),  # pada ciężko na twarz
    'atak': {'ruch': 'rzut', 'efekt': 'glaz'},
    'tagi': {'material': 'kamien', 'wielkosc': 'duza'},
}
