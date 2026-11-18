"""MAPA – TEREN: łąki, góra za miastem, lasy, staw z wodospadem, plac, drogi i działki.

Jeden plik teren.glb (bez murów – mury i brama to osobne elementy do ulepszania).
Układ (gdzie co stoi) bierze z mapa/uklad.py.
"""
import math
import random

import bmesh

from kit import V, box, cyl, sphere, ico, rock, jitter, mtx, seg, scale_m
from mapa import uklad as U

PALETA = {
    'grass': ('#6aa84f', 0.95), 'grass_dark': ('#55913f', 0.95), 'meadow': ('#86bf5a', 0.95),
    'dirt': ('#9a7a52', 0.95), 'road': ('#b49b70', 0.95), 'paving': ('#bdb5a6', 0.9), 'plot': ('#a8916a', 0.95),
    'mtn': ('#7f786f', 0.92), 'mtn_dark': ('#615b54', 0.95), 'snow': ('#f2f4f6', 0.7),
    'water': ('#3f9bd6', 0.08, 0.0, 0.25), 'fall': ('#bfe6ff', 0.1, 0.0, 0.9), 'foam': ('#ffffff', 0.4),
    'trunk': ('#6b4423', 0.9), 'leaves': ('#4f9a3a', 0.85), 'leaves_light': ('#69b443', 0.85), 'pine': ('#2f6a3a', 0.85),
    'stone': ('#9a948a', 0.92), 'stone_dark': ('#6d665e', 0.95), 'wood': ('#8a5a2b', 0.85), 'roof': ('#2f5fb8', 0.75),
    'flower_r': ('#e04848', 0.7), 'flower_y': ('#f2d04a', 0.7), 'flower_w': ('#f4f1ea', 0.7),
}


def _szum(x, y):
    return (math.sin(x * 0.71 + y * 0.29) * math.cos(y * 0.53 - x * 0.21) + 0.5 * math.sin(x * 1.7 + 2.1) * math.sin(y * 1.3 + 0.7))


def podstawa_gory(x):
    """Linia, gdzie zaczyna się góra (za miastem; na bokach lekko wysuwa się do przodu)."""
    return U.GLEB / 2 - 1.0 - 2.5 * max(0.0, (abs(x) - 14.0) / 10.0)


def wys_gory(x, y):
    d = y - podstawa_gory(x)
    if d <= 0:
        return 0.0
    H = 24 + 9 * math.exp(-(x / 20) ** 2) + 4 * math.sin(x * 0.13) + 2.5 * math.sin(x * 0.31 + 1)
    prof = 1 - math.exp(-d / 9.0)
    return H * prof + 1.6 * _szum(x * 0.6, y * 0.6) * prof


def wys_ziemi(x, y):
    """Wnętrze miasta i pas przy murach płaskie; dalej lekkie falowanie łąk."""
    if abs(x) < 4.0 and y < U.PRZOD_Y:
        return 0.0  # pas drogi od bramy
    poza = max(0.0, abs(x) - U.SZER / 2 - 4) + max(0.0, U.PRZOD_Y - 4 - y)
    return min(1.0, poza / 10.0) * 0.35 * _szum(x * 0.15, y * 0.15)


def _trojkaty(sl, nx, ny, x0, x1, y0, y1, hfn, matfn):
    pts = [[V(x0 + (x1 - x0) * i / nx, y0 + (y1 - y0) * j / ny, 0) for i in range(nx + 1)] for j in range(ny + 1)]
    for row in pts:
        for p in row:
            p.z = hfn(p.x, p.y)
    grupy = {}
    for j in range(ny):
        for i in range(nx):
            a, b, c, d = pts[j][i], pts[j][i + 1], pts[j + 1][i + 1], pts[j + 1][i]
            for t in (((a, b, c), (a, c, d)) if (i + j) % 2 else ((a, b, d), (b, c, d))):
                mat = matfn(t)
                if mat:
                    grupy.setdefault(mat, []).append(t)
    for mat, tris in grupy.items():
        bm = bmesh.new()
        for t in tris:
            if (t[1] - t[0]).cross(t[2] - t[0]).z < 0:  # zawsze „do góry”
                t = (t[0], t[2], t[1])
            bm.faces.new([bm.verts.new(p) for p in t])
        sl.add(bm, mat, 'root')


def drzewo(sl, p, s, rng):
    sl.add(cyl(0.18 * s, 0.13 * s, 1.4 * s, 7), 'trunk', 'root', mtx(p + V(0, 0, 0.7 * s)))
    for k in range(3):
        o = V(rng.uniform(-0.5, 0.5), rng.uniform(-0.5, 0.5), 1.8 + k * 0.45) * s
        sl.add(jitter(ico(rng.uniform(0.7, 0.95) * s, 1), 0.08 * s, rng.randint(0, 999)),
               rng.choice(('leaves', 'leaves_light')), 'root', mtx(p + o))


def sosna(sl, p, s, rng):
    sl.add(cyl(0.14 * s, 0.1 * s, 0.9 * s, 6), 'trunk', 'root', mtx(p + V(0, 0, 0.45 * s)))
    for k, (r, h) in enumerate(((1.1, 1.4), (0.85, 1.2), (0.6, 1.0))):
        sl.add(cyl(r * s, 0.0, h * s, 7), 'pine', 'root', mtx(p + V(0, 0, (0.8 + k * 0.75 + h / 2) * s), (0, 0, rng.uniform(0, 60))))


def _zajete(x, y):
    """Czy punkt koliduje z miastem, drogą lub strefami ataku (tam nie sadzimy drzew)."""
    if abs(x) < U.SZER / 2 + 5 and U.PRZOD_Y - 5 < y < U.GLEB / 2 + 2:
        return True
    if abs(x) < 4.5 and y < U.PRZOD_Y:
        return True
    for (a, b, c, d) in U.STREFY_ATAKU.values():
        if a - 3 < x < b + 3 and c - 3 < y < d + 3:
            return True
    return False


def teren(sl):
    rng = random.Random(2024)
    # --- ziemia (łąki)
    def mat_ziemi(t):
        cx, cy = sum(p.x for p in t) / 3, sum(p.y for p in t) / 3
        if cy > podstawa_gory(cx) + 1.0:
            return None
        h = _szum(cx * 0.09 + 3, cy * 0.09)
        return 'meadow' if h > 0.55 else ('grass_dark' if h < -0.5 else 'grass')
    _trojkaty(sl, 46, 30, -95.0, 95.0, -85.0, U.GLEB / 2 + 2, wys_ziemi, mat_ziemi)
    # --- góra
    def mat_gory(t):
        if max(p.z for p in t) < 0.05:
            return None
        n = (t[1] - t[0]).cross(t[2] - t[0]).normalized()
        cz = sum(p.z for p in t) / 3
        if cz > 24 and abs(n.z) > 0.55:
            return 'snow'
        if abs(n.z) > 0.66 and cz < 19:
            return 'grass' if cz < 10 else 'grass_dark'
        return 'mtn_dark' if _szum(t[0].x * 0.3, t[0].y * 0.3) > 0.4 else 'mtn'
    _trojkaty(sl, 64, 32, -95.0, 95.0, -12.0, 70.0, wys_gory, mat_gory)
    # sosny na trawiastych półkach góry
    for _ in range(400):
        x, y = rng.uniform(-85, 85), rng.uniform(podstawa_gory(0) + 2, 55)
        z = wys_gory(x, y)
        dz = wys_gory(x, y + 0.8) - z
        if 2 < z < 21 and dz < 1.1:
            sosna(sl, V(x, y, z - 0.1), rng.uniform(1.0, 1.6), rng)
    # --- lasy i kępy drzew wokół (z dala od miasta, drogi i stref ataku)
    for _ in range(420):
        x, y = rng.uniform(-92, 92), rng.uniform(-82, podstawa_gory(0))
        if _zajete(x, y) or y > podstawa_gory(x) - 1:
            continue
        p = V(x, y, wys_ziemi(x, y))
        (drzewo if rng.random() < 0.65 else sosna)(sl, p, rng.uniform(0.9, 1.5), rng)
    for _ in range(70):  # głazy
        x, y = rng.uniform(-90, 90), rng.uniform(-80, 10)
        if _zajete(x, y):
            continue
        s = rng.uniform(0.4, 1.3)
        sl.add(rock(1.2 * s, 1.0 * s, 0.8 * s, rng.randint(0, 9999)), rng.choice(('stone', 'stone_dark')), 'root',
               mtx((x, y, wys_ziemi(x, y) + 0.25 * s), (0, 0, rng.uniform(0, 90))))
    for _ in range(500):  # kwiaty na łąkach
        x, y = rng.uniform(-80, 80), rng.uniform(-75, 8)
        if abs(x) < U.SZER / 2 + 2 and U.PRZOD_Y - 2 < y:
            continue
        sl.add(ico(0.09, 0), rng.choice(('flower_r', 'flower_y', 'flower_w')), 'root', mtx((x, y, wys_ziemi(x, y) + 0.08)))
    # --- drogi: od bramy w dół mapy + ścieżki w mieście
    def pas(p0, p1, w, mat='road'):
        d = p1 - p0
        sl.add(box(w, d.length, 0.06, 0.0), mat, 'root',
               mtx(((p0 + p1) / 2).to_tuple(), (0, 0, math.degrees(math.atan2(-d.x, d.y)))))
    pas(V(0, U.PRZOD_Y + 0.5, 0.03), V(0, -85, 0.03), 4.0)
    plac = V(*U.PLAC['srodek'], 0)
    pas(V(0, U.PRZOD_Y, 0.04), plac, 3.0, 'dirt')
    for d in U.DZIALKI:
        c = V(*d['srodek'], 0.04)
        pas(V(plac.x, plac.y, 0.04), c, 1.6, 'dirt')
    # --- plac ze studnią
    sl.add(cyl(U.PLAC['promien'], U.PLAC['promien'], 0.1, 28), 'paving', 'root', mtx((plac.x, plac.y, 0.05)))
    sl.add(cyl(0.9, 0.9, 0.8, 14), 'stone', 'root', mtx((plac.x, plac.y, 0.5)))
    sl.add(cyl(0.65, 0.65, 0.05, 14), 'water', 'root', mtx((plac.x, plac.y, 0.88)))
    for sg in (1, -1):
        sl.add(cyl(0.08, 0.08, 1.4, 6), 'wood', 'root', mtx((plac.x + sg * 0.75, plac.y, 1.5)))
    sl.add(cyl(1.3, 0.0, 0.7, 4), 'roof', 'root', mtx((plac.x, plac.y, 2.5), (0, 0, 45)))
    # --- działki pod budynki: utwardzony grunt + kamienne narożniki
    for d in U.DZIALKI:
        (x, y), (w, g) = d['srodek'], d['rozmiar']
        sl.add(box(w, g, 0.12, 0.03), 'plot', 'root', mtx((x, y, 0.06)))
        for sx in (-1, 1):
            for sy in (-1, 1):
                sl.add(rock(0.45, 0.45, 0.35, int(x * 7 + y * 13 + sx + sy * 3) % 997), 'stone', 'root',
                       mtx((x + sx * (w / 2 - 0.2), y + sy * (g / 2 - 0.2), 0.18)))
    # --- staw z wodospadem spływającym z góry
    (sx, sy), r = U.STAW['srodek'], U.STAW['promien']
    sl.add(cyl(r, r, 0.06, 24), 'water', 'root', mtx((sx, sy, 0.05)))
    for i in range(14):
        a = 2 * math.pi * i / 14
        sl.add(rock(0.7, 0.5, 0.45, 700 + i), 'stone_dark', 'root', mtx((sx + math.cos(a) * r, sy + math.sin(a) * r, 0.2), (0, 0, math.degrees(a))))
    top = V(sx, podstawa_gory(sx) + 2.2, 0)
    top.z = wys_gory(top.x, top.y) - 0.3
    sl.add(box(1.4, 0.2, top.z, 0.0), 'fall', 'root', mtx((sx, sy + r * 0.8, top.z / 2), (-6, 0, 0)))
    for i in range(6):
        sl.add(sphere(0.35, 0.3, 0.2, 10, 6), 'foam', 'root', mtx((sx + (i - 2.5) * 0.3, sy + r * 0.55, 0.12)))
    # --- kilka drzew w mieście (przy murach i stawie)
    for (x, y) in ((-15.5, -10.0), (15.5, -10.0), (-15.5, 4.5), (15.5, 4.5), (-6.0, 12.3), (6.0, 12.3), (14.5, 11.5)):
        drzewo(sl, V(x, y, 0), 1.0, rng)
