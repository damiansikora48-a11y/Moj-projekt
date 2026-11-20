"""JEDNOSTKA: Żołnierz – piechota z mieczem i tarczą.

Gdzie co jest w tym pliku:
  SZKIELET  – proporcje ciała (metry)
  PALETA    – kolory i materiały: (kolor, szorstkość[, metaliczność[, świecenie]])
  glowa, helm, tulow, rece, nogi, miecz, tarcza – wygląd poszczególnych części
  JEDNOSTKA – złożenie wszystkiego: części w slotach, chód, atak
Atak (ruch i efekt) jest w folderze ataki/ – tu tylko wybór po nazwie.
"""
import math

import bmesh

from kit import V, box, cyl, sphere, ico, rock, cut_below, taper, jitter, mtx, frame, seg, SIDES, lerp, scale_m
from czesci.tkaniny import peleryna

SZKIELET = dict(
    ankle=0.10, shin=0.36, thigh=0.38, hip_w=0.12, foot=0.20,
    spine=0.20, chest=0.30, neck=0.06, head=0.36, head_fwd=0.0,
    sh_w=0.27, sh_drop=0.06, upper_arm=0.27, forearm=0.25, hand=0.12,
    arm_angle=14, forearm_fwd=10,
)

PALETA = {
    'skin': ('#e3a77c', 0.6),
    'steel': ('#aab3bd', 0.32, 0.85),
    'steel_dark': ('#5d6670', 0.4, 0.8),
    'chain': ('#7f8892', 0.55, 0.7),
    'tabard': ('#2f5fb8', 0.75),
    'gold': ('#e0ac3c', 0.3, 0.9),
    'leather': ('#77482a', 0.7),
    'leather_dark': ('#3e2817', 0.75),
    'cloth': ('#3a3f4c', 0.85),
    'cape': ('#9a2a2a', 0.8),
    'plume': ('#d23a2c', 0.85),
    'wood': ('#8a5a2b', 0.8),
    'eye': ('#151515', 0.3),
    'eye_white': ('#f3eee4', 0.4),
    'hair': ('#5a3820', 0.85),
    'gem': ('#e0283c', 0.15, 0.0, 0.6),
}


def glowa(sl, J):
    c = J['neck_top'] + V(0, 0, 0.17)
    sl.add(cyl(0.065, 0.06, 0.12, 12), 'skin', 'neck', seg(J['sh'] - V(0, 0, 0.03), J['neck_top'] + V(0, 0, 0.04)))
    sl.add(sphere(0.16, 0.155, 0.18, 20, 14), 'skin', 'head', mtx(c))
    sl.add(box(0.045, 0.05, 0.075, 0.016), 'skin', 'head', mtx(c + V(0, -0.157, -0.025), (-8, 0, 0)))
    for sg in (1, -1):
        sl.add(sphere(0.032, 0.014, 0.03, 12, 8), 'eye_white', 'head', mtx(c + V(sg * 0.058, -0.143, 0.018)))
        sl.add(sphere(0.019, 0.012, 0.022, 10, 8), 'eye', 'head', mtx(c + V(sg * 0.054, -0.153, 0.016)))
        sl.add(box(0.07, 0.026, 0.022, 0.008), 'hair', 'head', mtx(c + V(sg * 0.058, -0.152, 0.05), (0, sg * 10, 0)))
        sl.add(sphere(0.018, 0.04, 0.045, 10, 8), 'skin', 'head', mtx(c + V(sg * 0.158, 0.0, -0.005)))
    sl.add(sphere(0.158, 0.15, 0.13, 16, 10), 'hair', 'head', mtx(c + V(0, 0.03, -0.035)))
    # broda i wąsy
    sl.add(box(0.25, 0.13, 0.12, 0.045, 3), 'hair', 'head', mtx(c + V(0, -0.085, -0.125), (12, 0, 0)))
    sl.add(box(0.11, 0.08, 0.06, 0.025), 'hair', 'head', mtx(c + V(0, -0.115, -0.2), (25, 0, 0)))
    for sg in (1, -1):
        sl.add(box(0.075, 0.03, 0.03, 0.012), 'hair', 'head', mtx(c + V(sg * 0.035, -0.162, -0.058), (0, sg * -18, 0)))


def helm(sl, J):
    c = J['neck_top'] + V(0, 0, 0.17)
    dome = cut_below(sphere(1, 1, 1, 24, 16), -0.15)
    sl.add(dome, 'steel', 'head', mtx(c + V(0, 0.005, 0.095)) @ scale_m(0.182, 0.178, 0.18))
    # opaska z nitami
    sl.add(cyl(0.188, 0.188, 0.055, 28, 0.01), 'steel_dark', 'head', mtx(c + V(0, 0.005, 0.08)) @ scale_m(1, 0.985, 1))
    for i in range(14):
        a = math.radians(-90 + 25 + i * (310 / 13))
        p = c + V(math.cos(a) * 0.192, math.sin(a) * 0.19 + 0.005, 0.08)
        sl.add(sphere(0.012, u=8, v=6), 'gold', 'head', mtx(p))
    guard = cut_below(cyl(0.2, 0.188, 0.11, 28), -1)
    bmesh.ops.delete(guard, geom=[v for v in guard.verts if v.co.y < -0.06], context='VERTS')
    sl.add(guard, 'steel', 'head', mtx(c + V(0, 0.01, 0.0)) @ scale_m(1, 0.99, 1))
    sl.add(cyl(0.205, 0.205, 0.016, 28), 'gold', 'head', mtx(c + V(0, 0.07, -0.057)) @ scale_m(0.6, 0.7, 1))
    # nosal i osłony policzków
    sl.add(box(0.03, 0.022, 0.1, 0.009), 'steel', 'head', mtx(c + V(0, -0.186, 0.015)))
    for sg in (1, -1):
        sl.add(box(0.03, 0.12, 0.15, 0.014), 'steel', 'head', mtx(c + V(sg * 0.172, -0.02, -0.02), (0, sg * 8, sg * -10)))
        sl.add(sphere(0.011, u=8, v=6), 'gold', 'head', mtx(c + V(sg * 0.19, -0.02, 0.03)))
    # grzebień i pióropusz
    sl.add(box(0.04, 0.30, 0.04, 0.012), 'gold', 'head', mtx(c + V(0, 0.01, 0.272), (0, 0, 0)))
    R = 0.255
    n = 7
    for i in range(n):
        t = i / (n - 1)
        phi = math.radians(lerp(62, 168, t))
        p = c + V(0, -R * math.cos(phi), R * math.sin(phi) + 0.07)
        size = 0.5 + 0.5 * math.sin(math.pi * (0.25 + 0.75 * t))
        sl.add(sphere(0.045 * size + 0.02, 0.07 * size + 0.03, 0.06 * size + 0.025, 12, 8), 'plume', 'head',
               mtx(p, (math.degrees(phi) - 90, 0, 0)))


def tulow(sl, J):
    hz, cz, sz = J['hip'].z, J['chest_base'].z, J['sh'].z
    sl.add(box(0.34, 0.24, 0.16, 0.05), 'chain', 'hips', mtx((0, 0, hz)))
    sl.add(box(0.36, 0.25, 0.26, 0.06), 'chain', 'spine', mtx((0, 0, (hz + cz) / 2 + 0.03)))
    plate = taper(box(0.48, 0.30, 0.33, 0.09, 3), bottom=0.8, top=1.0)
    sl.add(plate, 'steel', 'chest', mtx((0, 0, cz + 0.15)))
    sl.add(cyl(0.13, 0.105, 0.08, 18, 0.012), 'steel', 'chest', mtx((0, 0.005, sz + 0.015)))
    sl.add(cyl(0.135, 0.135, 0.02, 18), 'gold', 'chest', mtx((0, 0.005, sz - 0.02)))
    # tabard (przód i tył) ze złotą lamówką i herbem
    for y, emblem in ((-0.158, True), (0.158, False)):
        sl.add(box(0.27, 0.025, 0.32, 0.008), 'tabard', 'chest', mtx((0, y, cz + 0.13)))
        sy = -1 if y < 0 else 1
        for sg in (1, -1):
            sl.add(box(0.022, 0.03, 0.32, 0.006), 'gold', 'chest', mtx((sg * 0.135, y, cz + 0.13)))
        sl.add(box(0.29, 0.03, 0.022, 0.006), 'gold', 'chest', mtx((0, y, cz + 0.29)))
        if emblem:
            sl.add(box(0.11, 0.02, 0.11, 0.01), 'gold', 'chest', mtx((0, y - 0.016, cz + 0.15), (0, 45, 0)))
            sl.add(box(0.06, 0.02, 0.06, 0.008), 'gem', 'chest', mtx((0, y - 0.026, cz + 0.15), (0, 45, 0)))
    # pas, sprzączka, sakwa, pochwa miecza
    bz = cz - 0.05
    sl.add(cyl(0.205, 0.205, 0.065, 24, 0.01), 'leather', 'spine', mtx((0, 0, bz)) @ scale_m(1, 0.72, 1))
    sl.add(box(0.075, 0.024, 0.065, 0.012), 'gold', 'spine', mtx((0, -0.15, bz)))
    sl.add(box(0.035, 0.03, 0.03, 0.006), 'leather_dark', 'spine', mtx((0, -0.158, bz)))
    sl.add(box(0.085, 0.065, 0.09, 0.02), 'leather', 'spine', mtx((-0.17, -0.07, bz - 0.06), (0, 0, 20)))
    sl.add(box(0.09, 0.07, 0.035, 0.012), 'leather_dark', 'spine', mtx((-0.17, -0.072, bz - 0.02), (0, 0, 20)))
    sl.add(sphere(0.012, u=8, v=6), 'gold', 'spine', mtx((-0.183, -0.11, bz - 0.03)))
    scab = mtx((0.24, 0.06, hz - 0.12), (28, 0, 0))
    sl.add(box(0.07, 0.035, 0.5, 0.012), 'leather_dark', 'hips', scab)
    sl.add(box(0.075, 0.04, 0.05, 0.01), 'gold', 'hips', scab @ mtx((0, 0, -0.24)))
    sl.add(box(0.078, 0.042, 0.04, 0.01), 'gold', 'hips', scab @ mtx((0, 0, 0.23)))
    # poły tabardu przypięte do ud (nie przenikają nóg w chodzie)
    for sg, S in SIDES:
        for y in (-0.135, 0.135):
            fl = mtx((sg * 0.078, y, hz - 0.12), (-6 if y < 0 else 6, 0, 0))
            sl.add(box(0.15, 0.024, 0.26, 0.008), 'tabard', 'thigh' + S, fl)
            sl.add(box(0.155, 0.03, 0.022, 0.006), 'gold', 'thigh' + S, fl @ mtx((0, 0, -0.12)))


def rece(sl, J):
    for sg, S in SIDES:
        sh, el, wr, he = J['shoulder' + S], J['elbow' + S], J['wrist' + S], J['hand_end' + S]
        d2 = J['hand_dir' + S]
        # naramiennik warstwowy
        sl.add(sphere(0.15, 0.15, 0.115, 18, 12), 'steel', 'shoulder' + S, mtx(sh + V(sg * 0.02, 0, 0.04)))
        sl.add(cyl(0.152, 0.152, 0.02, 20), 'gold', 'shoulder' + S, mtx(sh + V(sg * 0.02, 0, 0.0)))
        sl.add(sphere(0.022, u=10, v=8), 'gold', 'shoulder' + S, mtx(sh + V(sg * 0.03, 0, 0.155)))
        sl.add(sphere(0.13, 0.135, 0.07, 16, 10), 'steel', 'upper_arm' + S, mtx(sh + V(sg * 0.085, 0, -0.045), (0, -sg * 25, 0)))
        sl.add(sphere(0.11, 0.12, 0.06, 16, 10), 'steel_dark', 'upper_arm' + S, mtx(sh + V(sg * 0.12, 0, -0.115), (0, -sg * 40, 0)))
        # ramię, łokieć, karwasz
        sl.add(cyl(0.068, 0.062, (el - sh).length, 14), 'chain', 'upper_arm' + S, seg(sh, el))
        sl.add(sphere(0.072, u=14, v=10), 'steel', 'forearm' + S, mtx(el + V(0, 0.01, 0)))
        sl.add(sphere(0.06, 0.03, 0.075, 12, 8), 'steel', 'forearm' + S, mtx(el + V(sg * 0.06, 0.0, 0)))
        sl.add(cyl(0.065, 0.08, (wr - el).length * 0.9, 14), 'steel', 'forearm' + S,
               seg(el + (wr - el) * 0.08, wr))
        for t in (0.35, 0.72):
            sl.add(cyl(0.077, 0.077, 0.025, 14), 'leather_dark', 'forearm' + S,
                   seg(el + (wr - el) * t - d2 * 0.0125, el + (wr - el) * t + d2 * 0.0125))
        # rękawica
        sl.add(cyl(0.085, 0.095, 0.06, 14, 0.008), 'steel_dark', 'hand' + S, seg(wr - d2 * 0.015, wr + d2 * 0.045))
        hm = frame(wr + d2 * 0.085, d2, (1, 0, 0))
        sl.add(box(0.105, 0.115, 0.11, 0.035), 'steel', 'hand' + S, hm)
        sl.add(box(0.11, 0.04, 0.05, 0.014), 'steel_dark', 'hand' + S, hm @ mtx((0, -0.055, 0.035)))
        sl.add(box(0.035, 0.05, 0.065, 0.014), 'steel', 'hand' + S, hm @ mtx((-sg * 0.06, -0.035, -0.005), (0, 0, sg * 15)))


def nogi(sl, J):
    for sg, S in SIDES:
        hp, kn, an = J['hipj' + S], J['knee' + S], J['ankle' + S]
        sl.add(cyl(0.098, 0.082, (kn - hp).length, 16), 'cloth', 'thigh' + S, seg(hp, kn))
        sl.add(taper(box(0.13, 0.05, 0.22, 0.02), 0.8, 1.0), 'steel', 'thigh' + S,
               mtx(lerp(hp, kn, 0.55) + V(0, -0.075, 0), (-3, 0, 0)))
        sl.add(sphere(0.078, 0.065, 0.075, 14, 10), 'steel', 'shin' + S, mtx(kn + V(0, -0.04, 0)))
        sl.add(sphere(0.05, 0.02, 0.06, 10, 8), 'steel', 'shin' + S, mtx(kn + V(sg * 0.07, -0.02, 0)))
        sl.add(sphere(0.016, u=8, v=6), 'gold', 'shin' + S, mtx(kn + V(0, -0.105, 0)))
        sl.add(cyl(0.08, 0.072, 0.24, 16), 'steel', 'shin' + S, seg(kn - V(0, 0, 0.05), kn - V(0, 0, 0.29)))
        sl.add(box(0.025, 0.03, 0.22, 0.01), 'steel_dark', 'shin' + S, mtx(kn + V(0, -0.075, -0.17)))
        # but
        ft = V(hp.x, 0, 0)
        sl.add(cyl(0.088, 0.085, 0.16, 16), 'leather', 'shin' + S, seg(ft + V(0, 0, 0.03), ft + V(0, 0, 0.19)))
        sl.add(cyl(0.098, 0.1, 0.05, 16, 0.01), 'leather_dark', 'shin' + S, seg(ft + V(0, 0, 0.18), ft + V(0, 0, 0.23)))
        sl.add(box(0.135, 0.24, 0.10, 0.04, 3), 'leather', 'foot' + S, mtx(ft + V(0, -0.055, 0.055)))
        sl.add(box(0.14, 0.09, 0.085, 0.035, 3), 'steel', 'foot' + S, mtx(ft + V(0, -0.15, 0.05)))
        sl.add(box(0.145, 0.27, 0.028, 0.008), 'leather_dark', 'foot' + S, mtx(ft + V(0, -0.06, 0.014)))


def miecz(sl, J):
    wr, d2 = J['wrist.R'], J['hand_dir.R']
    hc = wr + d2 * 0.085
    sd = V(0.06, -0.72, 0.69).normalized()
    F = frame(hc, sd, (1, 0, 0))
    b = 'hand.R'
    sl.add(cyl(0.022, 0.022, 0.19, 10), 'leather_dark', b, F)
    for t in (-0.06, -0.02, 0.02, 0.06):
        sl.add(cyl(0.025, 0.025, 0.012, 10), 'leather', b, F @ mtx((0, 0, t)))
    sl.add(sphere(0.038, 0.038, 0.034, 12, 8), 'gold', b, F @ mtx((0, 0, -0.115)))
    sl.add(sphere(0.016, 0.012, 0.016, 8, 6), 'gem', b, F @ mtx((0, -0.034, -0.115)))
    sl.add(box(0.3, 0.055, 0.05, 0.016), 'gold', b, F @ mtx((0, 0, 0.105)))
    for sg in (1, -1):
        sl.add(sphere(0.032, u=10, v=8), 'gold', b, F @ mtx((sg * 0.155, 0, 0.105)))
    sl.add(box(0.05, 0.035, 0.05, 0.012), 'gold', b, F @ mtx((0, 0, 0.14)))
    L = 0.8
    sl.add(box(0.105, 0.03, L, 0.009), 'steel', b, F @ mtx((0, 0, 0.13 + L / 2)))
    sl.add(box(0.026, 0.034, L - 0.15, 0.005), 'steel_dark', b, F @ mtx((0, 0, 0.13 + (L - 0.15) / 2 + 0.03)))
    tip = cyl(0.074, 0.0, 0.17, 4)
    sl.add(tip, 'steel', b, F @ mtx((0, 0, 0.13 + L + 0.085)) @ scale_m(1.0, 0.3, 1.0) @ mtx(rot=(0, 0, 45)))


def tarcza(sl, J):
    el, wr = J['elbow.L'], J['wrist.L']
    fc = (el + wr) / 2 + V(0.11, -0.05, 0.0)
    n = V(0.72, -0.69, 0.0).normalized()
    F = frame(fc, n, (0, 0, 1))
    b = 'forearm.L'
    sl.add(cyl(0.36, 0.36, 0.05, 36, 0.012), 'steel_dark', b, F @ mtx((0, 0, -0.005)))
    sl.add(cyl(0.335, 0.335, 0.06, 36, 0.01), 'wood', b, F)
    sl.add(cyl(0.3, 0.3, 0.012, 36), 'tabard', b, F @ mtx((0, 0, 0.032)))
    sl.add(box(0.07, 0.58, 0.012, 0.004), 'gold', b, F @ mtx((0, 0, 0.04)))
    sl.add(box(0.58, 0.07, 0.012, 0.004), 'gold', b, F @ mtx((0, 0, 0.04)))
    sl.add(cut_below(sphere(0.1, 0.1, 0.07, 18, 10), -0.005), 'steel', b, F @ mtx((0, 0, 0.035)))
    sl.add(cyl(0.11, 0.11, 0.015, 18), 'gold', b, F @ mtx((0, 0, 0.04)))
    for i in range(12):
        a = 2 * math.pi * i / 12
        sl.add(sphere(0.014, u=8, v=6), 'steel', b, F @ mtx((math.cos(a) * 0.318, math.sin(a) * 0.318, 0.034)))
    sl.add(box(0.05, 0.16, 0.04, 0.012), 'leather_dark', b, F @ mtx((0, 0, -0.05)))


JEDNOSTKA = {
    'id': 'zolnierz',
    'nazwa': 'Żołnierz',
    'opis': 'Piechota w zbroi płytowej z mieczem, okrągłą tarczą i peleryną.',
    'rola': 'wojownik',          # patrz siatka.py
    'zywiol': 'stal',
    'szkielet': SZKIELET,
    'paleta': PALETA,
    'czesci': {  # slot -> funkcja budująca część (nazwy slotów: patrz README)
        'Head': glowa, 'Headgear': helm, 'Body': tulow, 'Back': peleryna(),
        'Arms': rece, 'Legs': nogi, 'Weapon': miecz, 'Offhand': tarcza,
    },
    'chod': dict(walk_frames=32, idle_frames=72, thigh=26, knee=48, knee_base=4, arm=20,
                 **{'arm_scale.R': 0.45, 'arm_scale.L': 0.35, 'forearm_base.R': 22, 'forearm_base.L': 28},
                 twist=5, sway=2, lean=3, bob=0.022, breath=1.6, breath_loc=0.006,
                 smierc_dlon=-105),
    'atak': {'ruch': 'ciecie', 'efekt': None},
    'tagi': {'material': 'metal', 'wielkosc': 'srednia'},
}
