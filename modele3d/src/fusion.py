"""Fuzje jednostek.

Fuzja = (1) proporcje szkieletu wyliczone automatycznie z obu rodziców,
        (2) połączona paleta materiałów obu rodziców,
        (3) sloty: część wprost od rodzica, część nowych „mieszanych”, które łączą
            elementy obu (np. kamienna głowa golema w hełmie żołnierza),
        (4) własny atak, który miesza style rodziców.

Kamienny Rycerz = Żołnierz + Golem.
Atak „Slam”: rycerskie uderzenie oburącz kamiennym mieczem w ziemię (od żołnierza),
po którym z ziemi wyrastają kryształowe kolce (moc golema) – efekt: hybrid_spikes.glb.
"""
import math

from kit import V, box, cyl, sphere, ico, rock, cut_below, taper, jitter, mtx, frame, seg
from units import (SOLDIER, GOLEM, SIDES, K, lerp, make_cape, _scale)


def fuse_skeleton(a, b, t, **overrides):
    """Proporcje pośrednie: t=0 -> jak A, t=1 -> jak B."""
    sk = {k: lerp(a[k], b[k], t) for k in a if k in b}
    sk.update(overrides)
    return sk


def fuse_palette(a, b, **extra):
    pal = dict(a)
    pal.update(b)
    pal.update(extra)
    return pal


HYBRID_SKELETON = fuse_skeleton(SOLDIER['skeleton'], GOLEM['skeleton'], 0.45,
                                hip_w=0.21, head_fwd=0.1, neck=0.08, head=0.34, prop_at=1.0)
HYBRID_PALETTE = fuse_palette(SOLDIER['palette'], GOLEM['palette'],
                              cape=('#7d2626', 0.85), tabard=('#2c56a8', 0.75))


# ---------------------------------------------------------------- części

def hybrid_body(sl, J):
    hz, cz, sz = J['hip'].z, J['chest_base'].z, J['sh'].z
    sl.add(rock(0.46, 0.34, 0.24, 101), 'stone_dark', 'hips', mtx((0, 0.02, hz)))
    sl.add(sphere(0.12, u=14, v=10), 'core', 'spine', mtx((0, 0.0, hz + 0.14)))
    sl.add(rock(0.38, 0.3, 0.15, 102), 'stone', 'spine', mtx((0, 0.0, hz + 0.17), (0, 3, 5)))
    # pas rycerski na kamiennej talii
    bz = cz - 0.04
    sl.add(cyl(0.25, 0.25, 0.07, 24, 0.01), 'leather', 'spine', mtx((0, 0.01, bz)) @ _scale(1, 0.78, 1))
    sl.add(box(0.09, 0.03, 0.075, 0.014), 'gold', 'spine', mtx((0, -0.19, bz)))
    sl.add(box(0.045, 0.035, 0.035, 0.006), 'leather_dark', 'spine', mtx((0, -0.2, bz)))
    # kamienna klatka z wtopionym napierśnikiem
    chest = taper(rock(0.78, 0.5, 0.48, 104, rough=0.07), bottom=0.7, top=1.0, axis='x')
    sl.add(chest, 'stone', 'chest', mtx((0, 0.04, cz + 0.24)))
    plate = taper(box(0.56, 0.14, 0.36, 0.06, 3), bottom=0.84, top=1.0)
    sl.add(plate, 'steel', 'chest', mtx((0, -0.18, cz + 0.27), (-4, 0, 0)))
    sl.add(box(0.6, 0.05, 0.035, 0.012), 'gold', 'chest', mtx((0, -0.22, cz + 0.44)))
    sl.add(box(0.47, 0.05, 0.03, 0.01), 'gold', 'chest', mtx((0, -0.2, cz + 0.095)))
    # herb: złoty romb z kryształem zamiast klejnotu
    sl.add(box(0.12, 0.025, 0.12, 0.012), 'gold', 'chest', mtx((0, -0.258, cz + 0.29), (0, 45, 0)))
    sl.add(ico(0.04, 1), 'core', 'chest', mtx((0, -0.272, cz + 0.29)) @ _scale(1, 0.6, 1.3))
    # pęknięcia z runami biegnące przez metal
    for sg, pts in ((1, [(0.08, 0.40), (0.16, 0.33), (0.13, 0.25), (0.22, 0.16)]),
                    (-1, [(-0.09, 0.2), (-0.17, 0.27), (-0.15, 0.36), (-0.24, 0.41)])):
        P = [V(x, -0.258, cz + z) for x, z in pts]
        for a, b in zip(P, P[1:]):
            sl.add(box(0.02, 0.022, (b - a).length + 0.018), 'rune', 'chest', seg(a, b, (0, 1, 0)))
    # tabard pod napierśnikiem i poły na udach
    sl.add(box(0.3, 0.03, 0.14, 0.008), 'tabard', 'chest', mtx((0, -0.205, cz + 0.03)))
    for sg in (1, -1):
        sl.add(box(0.02, 0.035, 0.14, 0.006), 'gold', 'chest', mtx((sg * 0.15, -0.205, cz + 0.03)))
    for sg, S in SIDES:
        for y in (-0.19, 0.19):
            fl = mtx((sg * 0.105, y, hz - 0.12), (-6 if y < 0 else 6, 0, 0))
            sl.add(box(0.18, 0.026, 0.28, 0.008), 'tabard', 'thigh' + S, fl)
            sl.add(box(0.185, 0.032, 0.024, 0.006), 'gold', 'thigh' + S, fl @ mtx((0, 0, -0.13)))
    # kołnierz i mech na karku
    sl.add(cyl(0.16, 0.13, 0.08, 18, 0.012), 'steel', 'chest', mtx((0, -0.03, sz + 0.0)))
    sl.add(jitter(sphere(0.3, 0.18, 0.05, 14, 6), 0.018, 105), 'moss', 'chest', mtx((0, 0.17, sz - 0.01)))


def hybrid_head(sl, J):
    c = J['neck_top'] + V(0, 0, 0.15)
    sl.add(rock(0.27, 0.26, 0.26, 111), 'stone_dark', 'head', mtx(c))
    sl.add(rock(0.24, 0.18, 0.09, 112), 'stone', 'head', mtx(c + V(0, -0.05, -0.14), (10, 0, 0)))
    for sg in (1, -1):
        sl.add(box(0.075, 0.03, 0.035, 0.008), 'core', 'head', mtx(c + V(sg * 0.066, -0.137, 0.005), (0, sg * -8, 0)))
    # hełm żołnierza na kamiennej głowie
    hc = c + V(0, 0.005, 0.06)
    sl.add(cut_below(sphere(1, 1, 1, 24, 16), -0.15), 'steel', 'head', mtx(hc) @ _scale(0.19, 0.185, 0.19))
    sl.add(cyl(0.196, 0.196, 0.05, 28, 0.01), 'steel_dark', 'head', mtx(c + V(0, 0.005, 0.045)))
    for i in range(12):
        a = math.radians(-90 + 28 + i * (304 / 11))
        sl.add(sphere(0.012, u=8, v=6), 'gold', 'head', mtx(c + V(math.cos(a) * 0.2, math.sin(a) * 0.2 + 0.005, 0.045)))
    sl.add(box(0.04, 0.025, 0.12, 0.009), 'steel', 'head', mtx(c + V(0, -0.196, 0.0)))
    for sg in (1, -1):
        sl.add(box(0.03, 0.1, 0.1, 0.012), 'steel', 'head', mtx(c + V(sg * 0.18, -0.02, -0.04), (0, sg * 8, sg * -8)))
    # pęknięcie hełmu ze światłem runy
    pts = [V(0.35, -0.75, 0.55), V(0.62, -0.55, 0.55), V(0.62, -0.45, 0.65), V(0.82, -0.3, 0.48)]
    P = [hc + p.normalized() * 0.192 for p in pts]
    for a, b in zip(P, P[1:]):
        sl.add(box(0.018, 0.018, (b - a).length + 0.015), 'rune', 'head', seg(a, b, (0, 0, 1)))
    # grzebień z kryształów zamiast pióropusza
    n = 6
    for i in range(n):
        t = i / (n - 1)
        phi = math.radians(lerp(65, 160, t))
        d = V(0, -math.cos(phi), math.sin(phi))
        L = 0.1 + 0.11 * math.sin(math.pi * (0.2 + 0.8 * t))
        base = hc + d * 0.17
        F = frame(base, d, (1, 0, 0))
        sl.add(cyl(0.035, 0.035, L * 0.65, 6), 'crystal', 'head', F @ mtx((0, 0, L * 0.32)))
        sl.add(cyl(0.035, 0.0, L * 0.35, 6), 'crystal', 'head', F @ mtx((0, 0, L * 0.82)))
    sl.add(box(0.05, 0.3, 0.035, 0.012), 'gold', 'head', mtx(hc + V(0, 0.02, 0.183)))


def hybrid_arms(sl, J):
    for sg, S in SIDES:
        sh, el, wr = J['shoulder' + S], J['elbow' + S], J['wrist' + S]
        d2 = J['hand_dir' + S]
        k = 130 if sg > 0 else 160
        if sg < 0:
            # PRAWE ramię: rycerskie – stalowy naramiennik i kolczuga, przechodzące w kamień
            sl.add(sphere(0.17, 0.17, 0.13, 18, 12), 'steel', 'shoulder' + S, mtx(sh + V(sg * 0.02, 0, 0.05)))
            sl.add(cyl(0.172, 0.172, 0.022, 20), 'gold', 'shoulder' + S, mtx(sh + V(sg * 0.02, 0, 0.005)))
            sl.add(sphere(0.024, u=10, v=8), 'gold', 'shoulder' + S, mtx(sh + V(sg * 0.03, 0, 0.18)))
            sl.add(sphere(0.15, 0.15, 0.08, 16, 10), 'steel', 'upper_arm' + S, mtx(sh + V(sg * 0.1, 0, -0.05), (0, -sg * 25, 0)))
            sl.add(sphere(0.13, 0.135, 0.07, 16, 10), 'steel_dark', 'upper_arm' + S, mtx(sh + V(sg * 0.14, 0, -0.13), (0, -sg * 40, 0)))
            sl.add(cyl(0.085, 0.08, (el - sh).length, 14), 'chain', 'upper_arm' + S, seg(sh, el))
            sl.add(sphere(0.09, u=14, v=10), 'steel', 'forearm' + S, mtx(el + V(0, 0.01, 0)))
        else:
            # LEWE ramię: golemowe – głaz z mchem, spięty stalową obręczą
            sl.add(jitter(ico(0.22, 2), 0.025, k), 'stone', 'shoulder' + S, mtx(sh + V(sg * 0.05, 0.03, 0.05)) @ _scale(1.05, 1, 0.92))
            sl.add(jitter(sphere(0.2, 0.19, 0.07, 14, 7), 0.02, k + 1), 'moss', 'shoulder' + S, mtx(sh + V(sg * 0.05, 0.04, 0.22)))
            sl.add(cyl(0.232, 0.232, 0.05, 20, 0.008), 'steel_dark', 'shoulder' + S, mtx(sh + V(sg * 0.05, 0.03, 0.06)))
            for i in range(6):
                a = 2 * math.pi * i / 6
                sl.add(sphere(0.013, u=8, v=6), 'gold', 'shoulder' + S,
                       mtx(sh + V(sg * 0.05 + math.cos(a) * 0.236, 0.03 + math.sin(a) * 0.236, 0.06)))
            sl.add(cyl(0.04, 0.04, 0.12, 6), 'crystal', 'shoulder' + S, mtx(sh + V(sg * 0.12, 0.12, 0.2), (-30, -sg * 20, 0)))
            sl.add(cyl(0.04, 0.0, 0.07, 6), 'crystal', 'shoulder' + S, mtx(sh + V(sg * 0.12, 0.12, 0.2), (-30, -sg * 20, 0)) @ mtx((0, 0, 0.095)))
            for i, t in enumerate((0.3, 0.72)):
                c = lerp(sh, el, t)
                sl.add(rock(0.2, 0.2, 0.17, k + 3 + i), ('stone_dark', 'stone')[i], 'upper_arm' + S, seg(c - (el - sh) * 0.001, c + (el - sh) * 0.001))
            sl.add(sphere(0.075, u=12, v=8), 'core', 'forearm' + S, mtx(el))
            sl.add(rock(0.16, 0.15, 0.15, k + 6), 'stone_dark', 'forearm' + S, mtx(el + V(sg * 0.02, 0.08, 0)))
        # kamienne przedramię z runami (oba ramiona – tu łączą się światy)
        fa = taper(rock(0.25, 0.25, 0.33, k + 7, rough=0.08), bottom=0.75, top=1.0)
        sl.add(fa, 'stone', 'forearm' + S, seg(lerp(el, wr, 0.1), lerp(el, wr, 0.98)) @ mtx(rot=(180, 0, 0)))
        if sg < 0:
            sl.add(cyl(0.13, 0.14, 0.08, 16, 0.01), 'steel', 'forearm' + S, seg(lerp(el, wr, 0.08), lerp(el, wr, 0.3)))
            sl.add(cyl(0.142, 0.142, 0.018, 16), 'gold', 'forearm' + S, seg(lerp(el, wr, 0.29), lerp(el, wr, 0.33)))
        for off in (-0.05, 0.05):
            a, b = lerp(el, wr, 0.4), lerp(el, wr, 0.85)
            o = V(sg * 0.13, off, 0)
            sl.add(box(0.018, 0.022, (b - a).length), 'rune', 'forearm' + S, seg(a + o, b + o, (0, 1, 0)))
        sl.add(sphere(0.065, u=12, v=8), 'core', 'hand' + S, mtx(wr))
        H = frame(wr + d2 * 0.12, d2, (1, 0, 0))
        fist = 0.22 if sg < 0 else 0.27
        sl.add(rock(fist, fist, fist * 0.9, k + 9, rough=0.07), 'stone_dark', 'hand' + S, H)
        for i in range(4):
            x = (-0.75 + i * 0.5) * fist * 0.5
            sl.add(rock(fist * 0.24, fist * 0.26, fist * 0.26, k + 10 + i), 'stone_light', 'hand' + S,
                   H @ mtx((x, -fist * 0.47, fist * 0.28)))


def hybrid_legs(sl, J):
    for sg, S in SIDES:
        hp, kn, an = J['hipj' + S], J['knee' + S], J['ankle' + S]
        k = 180 if sg > 0 else 190
        sl.add(rock(0.28, 0.28, 0.27, k), 'stone_dark', 'thigh' + S, mtx(lerp(hp, kn, 0.5)))
        sl.add(sphere(0.065, u=12, v=8), 'core', 'shin' + S, mtx(kn))
        sl.add(sphere(0.095, 0.075, 0.09, 14, 10), 'steel', 'shin' + S, mtx(kn + V(0, -0.085, 0)))
        sl.add(sphere(0.06, 0.025, 0.065, 10, 8), 'steel', 'shin' + S, mtx(kn + V(sg * 0.085, -0.05, 0)))
        sl.add(sphere(0.017, u=8, v=6), 'gold', 'shin' + S, mtx(kn + V(0, -0.162, 0)))
        sl.add(taper(rock(0.26, 0.26, 0.26, k + 2, rough=0.08), bottom=1.12, top=0.85), 'stone', 'shin' + S,
               mtx(lerp(kn, an, 0.5) + V(0, 0, 0.02)))
        sl.add(taper(box(0.13, 0.05, 0.2, 0.02), 0.8, 1.0), 'steel', 'shin' + S, mtx(lerp(kn, an, 0.45) + V(0, -0.135, 0), (4, 0, 0)))
        ft = V(hp.x, 0, 0)
        sl.add(rock(0.32, 0.4, 0.15, k + 3, rough=0.06), 'stone_dark', 'foot' + S, mtx(ft + V(0, -0.06, 0.075)))
        for i, x in enumerate((-0.1, 0.0, 0.1)):
            sl.add(rock(0.09, 0.09, 0.085, k + 4 + i), 'stone', 'foot' + S, mtx(ft + V(x, -0.27, 0.05)))
        sl.add(jitter(sphere(0.09, 0.08, 0.03, 10, 6), 0.01, k + 9), 'moss', 'foot' + S, mtx(ft + V(sg * 0.06, 0.04, 0.16)))


def hybrid_weapon(sl, J):
    """Runiczne Ostrze: kamienny miecz z kryształowymi krawędziami."""
    wr, d2 = J['wrist.R'], J['hand_dir.R']
    hc = wr + d2 * 0.12
    sd = V(0.05, -0.95, -0.3).normalized()
    F = frame(hc, sd, (1, 0, 0))
    b = 'hand.R'
    sl.add(cyl(0.03, 0.03, 0.34, 10), 'leather_dark', b, F @ mtx((0, 0, -0.03)))
    for t in (-0.15, -0.09, -0.03, 0.03, 0.09):
        sl.add(cyl(0.034, 0.034, 0.014, 10), 'leather', b, F @ mtx((0, 0, t)))
    sl.add(cyl(0.05, 0.05, 0.04, 8), 'gold', b, F @ mtx((0, 0, -0.21)))
    sl.add(ico(0.05, 1), 'crystal', b, F @ mtx((0, 0, -0.26)) @ _scale(1, 1, 1.4))
    sl.add(rock(0.36, 0.1, 0.09, 201, rough=0.06), 'stone_dark', b, F @ mtx((0, 0, 0.17)))
    for sg in (1, -1):
        sl.add(sphere(0.04, u=10, v=8), 'gold', b, F @ mtx((sg * 0.19, 0, 0.17)))
    sl.add(sphere(0.04, 0.025, 0.04, 10, 8), 'core', b, F @ mtx((0, -0.045, 0.17)))
    L = 1.0
    blade = taper(rock(0.17, 0.06, L, 202, rough=0.035, bevel=0.3), bottom=1.0, top=0.78, axis='x')
    sl.add(blade, 'stone', b, F @ mtx((0, 0, 0.21 + L / 2)))
    for sg in (1, -1):
        sl.add(box(0.026, 0.034, L * 0.9), 'crystal', b, F @ mtx((sg * 0.085, 0, 0.21 + L * 0.47), (0, sg * -1.2, 0)))
    for z in (0.35, 0.5, 0.65, 0.8, 0.95):
        sl.add(box(0.05, 0.066, 0.022, 0.004), 'rune', b, F @ mtx((0, 0, z), (0, 35 if z * 20 % 2 < 1 else -35, 0)))
    tip = cyl(0.09, 0.0, 0.24, 6)
    sl.add(tip, 'crystal', b, F @ mtx((0, 0, 0.21 + L + 0.1)) @ _scale(1.0, 0.42, 1.0))


def spikes_parts(sl):
    """Efekt ataku: kępa kryształowych kolców wyrastających z ziemi (środek w 0,0,0)."""
    import random
    rng = random.Random(7)
    for i in range(7):
        a = 2 * math.pi * i / 7 + rng.uniform(-0.3, 0.3)
        r = 0.0 if i == 0 else rng.uniform(0.18, 0.32)
        L = 0.75 if i == 0 else rng.uniform(0.35, 0.6)
        tilt = 0 if i == 0 else rng.uniform(15, 30)
        base = V(math.cos(a) * r, math.sin(a) * r, -0.05)
        d = V(math.cos(a) * math.sin(math.radians(tilt)), math.sin(a) * math.sin(math.radians(tilt)),
              math.cos(math.radians(tilt)))
        F = frame(base, d, (1, 0, 0))
        w = 0.08 if i == 0 else rng.uniform(0.045, 0.07)
        sl.add(cyl(w, w * 0.9, L * 0.7, 6), 'crystal', 'root', F @ mtx((0, 0, L * 0.35)))
        sl.add(cyl(w * 0.9, 0.0, L * 0.3, 6), 'crystal', 'root', F @ mtx((0, 0, L * 0.85)))
    for i in range(9):
        a = 2 * math.pi * i / 9
        sl.add(rock(0.16, 0.14, 0.09, 300 + i), ('stone', 'stone_dark')[i % 2], 'root',
               mtx((math.cos(a) * 0.38, math.sin(a) * 0.38, 0.02), (rng.uniform(-15, 15), rng.uniform(-15, 15), math.degrees(a))))
    sl.add(cyl(0.3, 0.3, 0.01, 24), 'rune', 'root', mtx((0, 0, 0.004)))


# ---------------------------------------------------------------- atak „Slam”

_HI = {'upper_arm.R': K((165, 0, 0)), 'forearm.R': K((40, 0, 0)), 'hand.R': K((20, 0, 0)),
       'upper_arm.L': K((160, 0, 0)), 'forearm.L': K((45, 0, 0)),
       'chest': K((-12, 0, 0)), 'spine': K((-5, 0, 0)), 'head': K((10, 0, 0)), 'thigh.L': K((10, 0, 0))}
_LO = {'upper_arm.R': K((55, 0, 0)), 'forearm.R': K((5, 0, 0)), 'hand.R': K((-45, 0, 0)),
       'upper_arm.L': K((50, 0, 0)), 'forearm.L': K((15, 0, 0)),
       'chest': K((25, 0, 0)), 'spine': K((12, 0, 0)), 'head': K((-25, 0, 0)),
       'thigh.L': K((28, 0, 0)), 'shin.L': K((-24, 0, 0)), 'thigh.R': K((-16, 0, 0)), 'shin.R': K((-8, 0, 0))}

HYBRID_ATTACK = {
    'name': 'Slam', 'frames': 48, 'event': 0.52, 'event_name': 'impact',
    'keys': [(0.0, {}), (0.38, _HI), (0.52, _LO), (0.72, _LO), (1.0, {})],
}

HYBRID = {
    'name': 'Hybrid',
    'skeleton': HYBRID_SKELETON,
    'palette': HYBRID_PALETTE,
    'slots': [('Body', hybrid_body), ('Head', hybrid_head), ('Cape', make_cape(1.45, 1.0, 0.3, 0.42, clasps=False)),
              ('Arms', hybrid_arms), ('Legs', hybrid_legs), ('Weapon', hybrid_weapon)],
    'anim': dict(walk_frames=40, idle_frames=84, thigh=22, knee=40, knee_base=3, arm=16,
                 **{'arm_scale.R': 0.4, 'arm_scale.L': 0.9, 'forearm_base.R': 18, 'forearm_base.L': 12},
                 twist=6, sway=3.5, lean=4, bob=0.028, breath=1.9, breath_loc=0.009),
    'attack': HYBRID_ATTACK,
}

UNITS = {'soldier': SOLDIER, 'golem': GOLEM, 'hybrid': HYBRID}
