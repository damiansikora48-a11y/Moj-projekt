"""Definicje jednostek: proporcje szkieletu, paleta materiałów, sloty części, parametry animacji.

Każdy slot to funkcja (slot, J) budująca część z prymitywów, przypiętą do kości o
wspólnych nazwach. Fuzja dwóch jednostek = proporcje pośrednie + wybór slotów od A lub B
+ mieszanie palet.
"""
import math

from mathutils import Vector

import bmesh

from kit import V, box, cyl, sphere, ico, rock, cut_below, taper, jitter, mtx, frame, seg

SIDES = ((1, '.L'), (-1, '.R'))


def lerp(a, b, t):
    return a + (b - a) * t


# ====================================================================== ŻOŁNIERZ

SOLDIER_SKELETON = dict(
    ankle=0.10, shin=0.36, thigh=0.38, hip_w=0.12, foot=0.20,
    spine=0.20, chest=0.30, neck=0.06, head=0.36, head_fwd=0.0,
    sh_w=0.27, sh_drop=0.06, upper_arm=0.27, forearm=0.25, hand=0.12,
    arm_angle=14, forearm_fwd=10,
)

SOLDIER_PALETTE = {
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
    'hair': ('#5a3820', 0.85),
    'gem': ('#e0283c', 0.15, 0.0, 0.6),
}


def soldier_head(sl, J):
    c = J['neck_top'] + V(0, 0, 0.17)
    sl.add(cyl(0.065, 0.06, 0.12, 12), 'skin', 'neck', seg(J['sh'] - V(0, 0, 0.03), J['neck_top'] + V(0, 0, 0.04)))
    sl.add(sphere(0.16, 0.155, 0.18, 20, 14), 'skin', 'head', mtx(c))
    sl.add(box(0.045, 0.05, 0.075, 0.016), 'skin', 'head', mtx(c + V(0, -0.157, -0.025), (-8, 0, 0)))
    for sg in (1, -1):
        sl.add(sphere(0.022, 0.012, 0.024, 10, 8), 'eye', 'head', mtx(c + V(sg * 0.056, -0.145, 0.02)))
        sl.add(box(0.065, 0.025, 0.02, 0.008), 'hair', 'head', mtx(c + V(sg * 0.056, -0.148, 0.058), (0, sg * 10, 0)))
        sl.add(sphere(0.018, 0.04, 0.045, 10, 8), 'skin', 'head', mtx(c + V(sg * 0.158, 0.0, -0.005)))
    sl.add(sphere(0.158, 0.15, 0.13, 16, 10), 'hair', 'head', mtx(c + V(0, 0.03, -0.035)))
    # broda i wąsy
    sl.add(box(0.25, 0.13, 0.12, 0.045, 3), 'hair', 'head', mtx(c + V(0, -0.085, -0.125), (12, 0, 0)))
    sl.add(box(0.11, 0.08, 0.06, 0.025), 'hair', 'head', mtx(c + V(0, -0.115, -0.2), (25, 0, 0)))
    for sg in (1, -1):
        sl.add(box(0.075, 0.03, 0.03, 0.012), 'hair', 'head', mtx(c + V(sg * 0.035, -0.162, -0.058), (0, sg * -18, 0)))


def soldier_helmet(sl, J):
    c = J['neck_top'] + V(0, 0, 0.17)
    dome = cut_below(sphere(1, 1, 1, 24, 16), -0.15)
    sl.add(dome, 'steel', 'head', mtx(c + V(0, 0.005, 0.045)) @ mtx() @ _scale(0.182, 0.178, 0.19))
    # opaska z nitami
    sl.add(cyl(0.188, 0.188, 0.055, 28, 0.01), 'steel_dark', 'head', mtx(c + V(0, 0.005, 0.03)) @ _scale(1, 0.985, 1))
    for i in range(14):
        a = math.radians(-90 + 25 + i * (310 / 13))
        p = c + V(math.cos(a) * 0.192, math.sin(a) * 0.19 + 0.005, 0.03)
        sl.add(sphere(0.012, u=8, v=6), 'gold', 'head', mtx(p))
    guard = cut_below(cyl(0.2, 0.188, 0.11, 28), -1)
    bmesh.ops.delete(guard, geom=[v for v in guard.verts if v.co.y < -0.06], context='VERTS')
    sl.add(guard, 'steel', 'head', mtx(c + V(0, 0.01, -0.035)) @ _scale(1, 0.99, 1) @ mtx(rot=(0, 0, 180)))
    sl.add(cyl(0.205, 0.205, 0.016, 28), 'gold', 'head', mtx(c + V(0, 0.01, -0.092)) @ _scale(0.6, 1, 1) @ mtx((0, 0.06, 0)))
    # nosal i osłony policzków
    sl.add(box(0.036, 0.022, 0.15, 0.009), 'steel', 'head', mtx(c + V(0, -0.186, -0.02)))
    for sg in (1, -1):
        sl.add(box(0.03, 0.12, 0.15, 0.014), 'steel', 'head', mtx(c + V(sg * 0.172, -0.035, -0.07), (0, sg * 8, sg * -10)))
        sl.add(sphere(0.011, u=8, v=6), 'gold', 'head', mtx(c + V(sg * 0.19, -0.035, -0.02)))
    # grzebień i pióropusz
    sl.add(box(0.04, 0.30, 0.04, 0.012), 'gold', 'head', mtx(c + V(0, 0.01, 0.235), (0, 0, 0)))
    R = 0.255
    n = 7
    for i in range(n):
        t = i / (n - 1)
        phi = math.radians(lerp(62, 168, t))
        p = c + V(0, -R * math.cos(phi), R * math.sin(phi) + 0.03)
        size = 0.5 + 0.5 * math.sin(math.pi * (0.25 + 0.75 * t))
        sl.add(sphere(0.045 * size + 0.02, 0.07 * size + 0.03, 0.06 * size + 0.025, 12, 8), 'plume', 'head',
               mtx(p, (math.degrees(phi) - 90, 0, 0)))


def _scale(x, y, z):
    from mathutils import Matrix
    return Matrix.Diagonal((x, y, z, 1))


def soldier_torso(sl, J):
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
    sl.add(cyl(0.205, 0.205, 0.065, 24, 0.01), 'leather', 'spine', mtx((0, 0, bz)) @ _scale(1, 0.72, 1))
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


def cloth_sheet(cols, rows, fn, thickness=0.022):
    """Siatka (u w [-1,1], v w [0,1]) wygięta funkcją fn(u, v) -> Vector, z grubością."""
    bm = bmesh.new()
    grid = [[bm.verts.new(fn(-1 + 2 * i / cols, j / rows)) for i in range(cols + 1)] for j in range(rows + 1)]
    for j in range(rows):
        for i in range(cols):
            bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]))
    bm.normal_update()
    bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=thickness)
    return bm


def make_cape(width=1.0, L=0.92, y_top=0.19, y_bot=0.3, clasps=True):
    def build(sl, J):
        _cape(sl, J, width, L, y_top, y_bot, clasps)
    return build


def _cape(sl, J, width, L, y_top, y_bot, clasps):
    sz = J['sh'].z

    def cape(u, v):
        a = u * math.radians(62)
        rw = lerp(0.2, 0.3, v) * width
        y0 = lerp(y_top, y_bot, v ** 1.3)
        x = math.sin(a) * rw
        y = y0 - (1 - math.cos(a)) * 0.13 * (1 - 0.4 * v) + 0.018 * math.sin(u * 3 * math.pi) * v
        return V(x, y, sz + 0.02 - v * L)
    sl.add(cloth_sheet(16, 10, cape), 'cape', 'chest')
    if not clasps:
        return
    for sg in (1, -1):
        sl.add(sphere(0.03, 0.02, 0.03, 10, 8), 'gold', 'chest', mtx((sg * 0.19, 0.06, sz + 0.0)))
        sl.add(box(0.06, 0.12, 0.03, 0.01), 'cape', 'chest', mtx((sg * 0.2, 0.12, sz - 0.01), (20, 0, 0)))


def soldier_arms(sl, J):
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


def soldier_legs(sl, J):
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


def soldier_weapon(sl, J):
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
    sl.add(box(0.26, 0.045, 0.04, 0.014), 'gold', b, F @ mtx((0, 0, 0.105)))
    for sg in (1, -1):
        sl.add(sphere(0.026, u=10, v=8), 'gold', b, F @ mtx((sg * 0.135, 0, 0.105)))
    sl.add(box(0.05, 0.035, 0.05, 0.012), 'gold', b, F @ mtx((0, 0, 0.14)))
    L = 0.72
    sl.add(box(0.078, 0.02, L, 0.006), 'steel', b, F @ mtx((0, 0, 0.13 + L / 2)))
    sl.add(box(0.02, 0.024, L - 0.15, 0.004), 'steel_dark', b, F @ mtx((0, 0, 0.13 + (L - 0.15) / 2 + 0.03)))
    tip = cyl(0.055, 0.0, 0.14, 4)
    sl.add(tip, 'steel', b, F @ mtx((0, 0, 0.13 + L + 0.07)) @ _scale(1.0, 0.26, 1.0) @ mtx(rot=(0, 0, 45)))


def soldier_shield(sl, J):
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


def K(rot=(0, 0, 0), loc=(0, 0, 0), scale=None):
    return (rot, loc, scale)


_SWORD_STANCE = {'thigh.L': K((18, 0, 0)), 'shin.L': K((-14, 0, 0)), 'thigh.R': K((-12, 0, 0)), 'shin.R': K((-6, 0, 0)),
                 'upper_arm.L': K((38, 0, 0)), 'forearm.L': K((52, 0, 0))}

SOLDIER_ATTACK = {
    'name': 'Attack', 'frames': 30, 'event': 0.45, 'event_name': 'hit',
    'keys': [
        (0.0, {}),
        (0.3, {**_SWORD_STANCE, 'upper_arm.R': K((115, 0, 0)), 'forearm.R': K((70, 0, 0)), 'hand.R': K((-20, 0, 0)),
               'chest': K((-6, -28, 0)), 'spine': K((0, -8, 0)), 'head': K((4, 18, 0))}),
        (0.45, {**_SWORD_STANCE, 'upper_arm.R': K((35, 0, 0)), 'forearm.R': K((5, 0, 0)), 'hand.R': K((-70, 0, 0)),
                'chest': K((14, 26, 0)), 'spine': K((6, 8, 0)), 'head': K((-10, -16, 0))}),
        (0.62, {**_SWORD_STANCE, 'upper_arm.R': K((-5, 0, 0)), 'forearm.R': K((0, 0, 0)), 'hand.R': K((-80, 0, 0)),
                'chest': K((16, 32, 0)), 'spine': K((6, 10, 0)), 'head': K((-10, -20, 0))}),
        (1.0, {}),
    ],
}

SOLDIER = {
    'name': 'Soldier',
    'skeleton': SOLDIER_SKELETON,
    'palette': SOLDIER_PALETTE,
    'slots': [('Head', soldier_head), ('Helmet', soldier_helmet), ('Torso', soldier_torso),
              ('Cape', make_cape()), ('Arms', soldier_arms), ('Legs', soldier_legs),
              ('Weapon', soldier_weapon), ('Shield', soldier_shield)],
    'anim': dict(walk_frames=32, idle_frames=72, thigh=26, knee=48, knee_base=4, arm=20,
                 **{'arm_scale.R': 0.45, 'arm_scale.L': 0.35, 'forearm_base.R': 22, 'forearm_base.L': 28},
                 twist=5, sway=2, lean=3, bob=0.022, breath=1.6, breath_loc=0.006),
    'attack': SOLDIER_ATTACK,
}


# ====================================================================== GOLEM

GOLEM_SKELETON = dict(
    ankle=0.14, shin=0.34, thigh=0.36, hip_w=0.30, foot=0.38,
    spine=0.30, chest=0.62, neck=0.10, head=0.32, head_fwd=0.27,
    sh_w=0.62, sh_drop=0.14, upper_arm=0.48, forearm=0.52, hand=0.30,
    arm_angle=16, forearm_fwd=14,
)

GOLEM_PALETTE = {
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


def golem_body(sl, J):
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
    sl.add(ico(0.11, 1), 'core', 'chest', mtx(core_p) @ _scale(1, 0.7, 1.25))
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


def golem_head(sl, J):
    c = J['neck_top'] + V(0, 0, 0.12)
    sl.add(rock(0.32, 0.30, 0.27, 21), 'stone_dark', 'head', mtx(c))
    sl.add(rock(0.38, 0.13, 0.09, 22), 'stone', 'head', mtx(c + V(0, -0.14, 0.07), (-8, 0, 0)))
    for sg in (1, -1):
        sl.add(box(0.085, 0.03, 0.05, 0.01), 'core', 'head', mtx(c + V(sg * 0.08, -0.158, 0.0), (0, sg * -10, 0)))
    sl.add(rock(0.28, 0.22, 0.11, 23), 'stone', 'head', mtx(c + V(0, -0.06, -0.14), (10, 0, 0)))
    sl.add(jitter(sphere(0.13, 0.12, 0.035, 10, 6), 0.012, 24), 'moss', 'head', mtx(c + V(0.02, 0.03, 0.14)))
    sl.add(cyl(0.035, 0.0, 0.16, 6), 'crystal', 'head', mtx(c + V(-0.1, 0.05, 0.18), (-20, -25, 0)))


def golem_arms(sl, J):
    for sg, S in SIDES:
        sh, el, wr = J['shoulder' + S], J['elbow' + S], J['wrist' + S]
        d2 = J['hand_dir' + S]
        k = 30 if sg > 0 else 60
        # głaz barkowy z czapą mchu i kryształami
        boulder = jitter(ico(0.27, 2), 0.03, k)
        sl.add(boulder, 'stone', 'shoulder' + S, mtx(sh + V(sg * 0.07, 0.04, 0.06)) @ _scale(1.05, 1, 0.92))
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
        H = frame(wr + d2 * 0.22, d2, (1, 0, 0)) @ _scale(1.2, 1.2, 1.15)
        sl.add(rock(0.38, 0.36, 0.32, k + 9, rough=0.07), 'stone_dark', 'hand' + S, H)
        for i in range(4):
            x = (-0.13 + i * 0.087)
            sl.add(rock(0.08, 0.09, 0.09, k + 10 + i), 'stone_light', 'hand' + S, H @ mtx((x, -0.17, 0.1)))
        sl.add(rock(0.11, 0.12, 0.16, k + 15), 'stone', 'hand' + S, H @ mtx((-sg * 0.2, -0.08, -0.02), (0, 0, sg * 12)))


def golem_legs(sl, J):
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


def _scale(x, y, z):  # noqa: F811
    from mathutils import Matrix
    return Matrix.Diagonal((x, y, z, 1))


def golem_rock_parts(sl, bone, M):
    """Głaz do rzucania (w dłoni golema i jako osobny pocisk)."""
    from mathutils import Matrix
    M = M if M is not None else Matrix.Identity(4)
    sl.add(jitter(ico(0.2, 2), 0.028, 501), 'stone_light', bone, M @ _scale(1.05, 0.95, 0.9))
    sl.add(rock(0.16, 0.14, 0.12, 502), 'stone_dark', bone, M @ mtx((0.1, 0.06, -0.08), (10, 20, 0)))
    sl.add(jitter(sphere(0.13, 0.12, 0.04, 10, 6), 0.012, 503), 'moss', bone, M @ mtx((-0.02, 0.02, 0.16), (8, -6, 0)))
    for loc, rot in (((0.07, -0.12, 0.08), (-50, 0, 20)), ((-0.1, -0.1, 0.02), (-60, 0, -35))):
        sl.add(cyl(0.035, 0.035, 0.06, 6), 'crystal', bone, M @ mtx(loc, rot) @ mtx((0, 0, 0.03)))
        sl.add(cyl(0.035, 0.0, 0.05, 6), 'crystal', bone, M @ mtx(loc, rot) @ mtx((0, 0, 0.085)))


def golem_rock(sl, J):
    golem_rock_parts(sl, 'prop.R', mtx(J['prop.R'] + J['hand_dir.R'] * 0.26) @ _scale(1.3, 1.3, 1.3))


_H = (0.001, 0.001, 0.001)
_S = (1, 1, 1)
GOLEM_ATTACK = {
    'name': 'Throw', 'frames': 60, 'event': 0.62, 'event_name': 'release',
    'keys': [
        (0.0, {'prop.R': K(scale=_H)}),
        (0.22, {'spine': K((24, 0, 0)), 'chest': K((18, -10, 0)), 'head': K((-22, 0, 0)),
                'upper_arm.R': K((40, 0, 0)), 'forearm.R': K((20, 0, 0)), 'upper_arm.L': K((25, 0, 0)),
                'thigh.L': K((22, 0, 0)), 'shin.L': K((-28, 0, 0)), 'thigh.R': K((10, 0, 0)), 'shin.R': K((-16, 0, 0)),
                'prop.R': K(scale=_H)}),
        (0.32, {'spine': K((24, 0, 0)), 'chest': K((18, -10, 0)), 'head': K((-22, 0, 0)),
                'upper_arm.R': K((40, 0, 0)), 'forearm.R': K((20, 0, 0)), 'upper_arm.L': K((25, 0, 0)),
                'thigh.L': K((22, 0, 0)), 'shin.L': K((-28, 0, 0)), 'thigh.R': K((10, 0, 0)), 'shin.R': K((-16, 0, 0)),
                'prop.R': K(scale=_S)}),
        (0.5, {'spine': K((-6, 0, 0)), 'chest': K((-14, -22, 0)), 'head': K((10, 10, 0)),
               'upper_arm.R': K((165, 0, 0)), 'forearm.R': K((60, 0, 0)), 'upper_arm.L': K((60, 0, 0)),
               'forearm.L': K((20, 0, 0)), 'thigh.L': K((8, 0, 0)), 'shin.L': K((-6, 0, 0)), 'thigh.R': K((-8, 0, 0)),
               'prop.R': K(scale=_S)}),
        (0.6, {'spine': K((12, 0, 0)), 'chest': K((18, 24, 0)), 'head': K((-10, -12, 0)),
               'upper_arm.R': K((80, 0, 0)), 'forearm.R': K((10, 0, 0)), 'upper_arm.L': K((-15, 0, 0)),
               'thigh.L': K((22, 0, 0)), 'shin.L': K((-14, 0, 0)), 'thigh.R': K((-14, 0, 0)),
               'prop.R': K(scale=_S)}),
        (0.625, {'spine': K((13, 0, 0)), 'chest': K((19, 25, 0)), 'head': K((-10, -12, 0)),
                 'upper_arm.R': K((72, 0, 0)), 'forearm.R': K((9, 0, 0)), 'upper_arm.L': K((-15, 0, 0)),
                 'thigh.L': K((22, 0, 0)), 'shin.L': K((-14, 0, 0)), 'thigh.R': K((-14, 0, 0)),
                 'prop.R': K(scale=_H)}),
        (0.76, {'spine': K((14, 0, 0)), 'chest': K((22, 28, 0)), 'head': K((-10, -14, 0)),
                'upper_arm.R': K((35, 0, 0)), 'forearm.R': K((5, 0, 0)), 'upper_arm.L': K((-10, 0, 0)),
                'thigh.L': K((22, 0, 0)), 'shin.L': K((-14, 0, 0)), 'thigh.R': K((-14, 0, 0)),
                'prop.R': K(scale=_H)}),
        (1.0, {'prop.R': K(scale=_H)}),
    ],
}

GOLEM = {
    'name': 'Golem',
    'skeleton': GOLEM_SKELETON,
    'palette': GOLEM_PALETTE,
    'slots': [('Body', golem_body), ('Head', golem_head), ('Arms', golem_arms), ('Legs', golem_legs),
              ('Rock', golem_rock)],
    'anim': dict(walk_frames=48, idle_frames=96, thigh=18, knee=32, knee_base=3, arm=16,
                 **{'arm_scale.R': 1.0, 'arm_scale.L': 1.0, 'forearm_base.R': 10, 'forearm_base.L': 10},
                 twist=7, sway=5, lean=6, bob=0.035, breath=2.2, breath_loc=0.012,
                 rest_scale={'prop.R': _H}),
    'attack': GOLEM_ATTACK,
}


