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


# rzeka wypływająca z jeziora pod wodospadem (linia łamana x, y)
RZEKA = [(43.5, 3.0), (52.0, 0.5), (60.0, -5.0), (68.0, -14.0), (76.0, -27.0), (84.0, -42.0), (92.0, -60.0), (98.0, -80.0)]


def _odl_od_rzeki(x, y):
    best = 1e9
    for (ax, ay), (bx, by) in zip(RZEKA, RZEKA[1:]):
        dx, dy = bx - ax, by - ay
        t = max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy)))
        best = min(best, math.hypot(x - ax - t * dx, y - ay - t * dy))
    return best


def wys_ziemi(x, y):
    """Wnętrze miasta i pas przy murach płaskie; dalej lekkie falowanie łąk."""
    if _odl_od_rzeki(x, y) < 4.5 or math.hypot(x - U.JEZIORO['srodek'][0], y - U.JEZIORO['srodek'][1]) < U.JEZIORO['promien'] + 3:
        return 0.0  # płasko przy rzece i jeziorze
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
    if _odl_od_rzeki(x, y) < 4.0 or math.hypot(x - U.JEZIORO['srodek'][0], y - U.JEZIORO['srodek'][1]) < U.JEZIORO['promien'] + 4:
        return True
    for (a, b, c, d) in U.STREFY_ATAKU.values():
        if a - 3 < x < b + 3 and c - 3 < y < d + 3:
            return True
    return False


def _na_gorze(x, y, odsun=0.0):
    return V(x, y - odsun, wys_gory(x, y))


def _szczegoly_gory(sl, rng):
    """Duży wodospad z jeziorem i rzeką, półki skalne, duże głazy."""
    # --- wodospad: wstęga wody spływająca po zboczu do jeziora
    (jx, jy), jr = U.JEZIORO['srodek'], U.JEZIORO['promien']
    y = podstawa_gory(jx)
    while wys_gory(jx, y) < 17.0 and y < 60:
        y += 0.25
    y_gora, n = y, 14
    pts = []
    for i in range(n + 1):
        t = i / n
        yy = y_gora + (podstawa_gory(jx) - 0.3 - y_gora) * t
        pts.append(V(jx, yy - 0.7, max(0.05, wys_gory(jx, yy) + 0.25)))
    pts.append(V(jx, jy + jr * 0.6, 0.06))
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        w = 1.8 + 1.6 * (i / len(pts))
        bm = bmesh.new()
        q = [bm.verts.new(a + V(-w / 2, 0, 0)), bm.verts.new(a + V(w / 2, 0, 0)),
             bm.verts.new(b + V(w / 2 + 0.15, 0, 0)), bm.verts.new(b + V(-w / 2 - 0.15, 0, 0))]
        bm.faces.new(q)
        bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.15)
        sl.add(bm, 'fall', 'root')
    # skała-próg, z którego spada woda, i piana
    sl.add(rock(4.0, 2.4, 1.2, 811), 'mtn_dark', 'root', mtx(pts[0] + V(0, 0.4, -0.5)))
    for i in range(14):
        a = 2 * math.pi * i / 14
        sl.add(sphere(0.6, 0.55, 0.35, 10, 6), 'foam', 'root', mtx((jx + math.cos(a) * 1.4, jy + jr * 0.55 + math.sin(a) * 0.9, 0.15)))
    # jezioro i rzeka
    sl.add(cyl(jr, jr, 0.06, 28), 'water', 'root', mtx((jx, jy, 0.05)))
    for i in range(16):
        a = 2 * math.pi * i / 16
        sl.add(rock(1.0, 0.8, 0.6, 820 + i), rng.choice(('stone', 'stone_dark')), 'root',
               mtx((jx + math.cos(a) * jr, jy + math.sin(a) * jr, 0.25), (0, 0, math.degrees(a))))
    for (ax, ay), (bx, by) in zip(RZEKA, RZEKA[1:]):
        a, b = V(ax, ay, 0.045), V(bx, by, 0.045)
        d = b - a
        sl.add(box(3.2, d.length + 1.5, 0.05, 0.0), 'water', 'root',
               mtx(((a + b) / 2).to_tuple(), (0, 0, math.degrees(math.atan2(-d.x, d.y)))))
        for k in range(3):  # kamienie na brzegach
            t = (k + 0.5) / 3
            p = a + d * t
            nrm = V(-d.y, d.x, 0).normalized()
            sg = 1 if k % 2 else -1
            sl.add(rock(0.9, 0.7, 0.5, 900 + int(ax) + k), 'stone', 'root', mtx((p + nrm * sg * 2.0).to_tuple()))
    # --- półki skalne (część z trawą i sosnami)
    n_polek = 0
    proby = 0
    while n_polek < 34 and proby < 2000:
        proby += 1
        x, y = rng.uniform(-80, 80), rng.uniform(podstawa_gory(0) + 3, 45)
        if abs(x - jx) < 6:
            continue
        z = wys_gory(x, y)
        if not (5 < z < 22):
            continue
        w, g, h = rng.uniform(3.5, 7.0), rng.uniform(2.2, 3.6), rng.uniform(0.8, 1.4)
        p = V(x, y - g * 0.35, z - h * 0.3)
        sl.add(rock(w, g, h, 1000 + n_polek, rough=0.06), rng.choice(('mtn', 'mtn_dark')), 'root',
               mtx(p.to_tuple(), (rng.uniform(-4, 4), rng.uniform(-6, 6), rng.uniform(-12, 12))))
        if rng.random() < 0.7:
            sl.add(jitter(box(w * 0.85, g * 0.8, 0.2, 0.06), 0.06, 1100 + n_polek), 'grass', 'root',
                   mtx((p + V(0, 0, h * 0.5)).to_tuple()))
            if rng.random() < 0.6:
                sosna(sl, p + V(rng.uniform(-w / 4, w / 4), 0, h * 0.55), rng.uniform(0.9, 1.3), rng)
        n_polek += 1
    # --- duże głazy u podnóża i na zboczach
    for i in range(46):
        x = rng.uniform(-88, 88)
        if abs(x) < U.SZER / 2 + 3 or abs(x - jx) < 6:
            continue
        y = podstawa_gory(x) + rng.uniform(-1.5, 10.0)
        s = rng.uniform(1.6, 3.6)
        p = V(x, y, max(0.0, wys_gory(x, y)) + s * 0.25)
        sl.add(rock(s * 1.2, s, s * 0.85, 1200 + i, rough=0.14), rng.choice(('mtn', 'mtn_dark', 'stone_dark')), 'root',
               mtx(p.to_tuple(), (rng.uniform(-10, 10), rng.uniform(-10, 10), rng.uniform(0, 90))))


def _podwyzszenie(sl, x, y, w, g, h):
    """Skalna półka pod budynek główny: skalne ściany, trawa na górze, kamienne schody z przodu."""
    rng = random.Random(77)
    sl.add(box(w - 0.4, g - 0.4, h, 0.05), 'mtn', 'root', mtx((x, y, h / 2)))
    sl.add(jitter(box(w - 0.2, g - 0.2, 0.14, 0.04), 0.03, 78), 'grass', 'root', mtx((x, y, h + 0.02)))
    # skalne bloki na krawędziach (półka wygląda na naturalną skałę)
    for bok in range(4):
        dl = w if bok < 2 else g
        n = int(dl / 1.6)
        for i in range(n):
            t = (i + 0.5) / n - 0.5
            if bok == 0 and abs(t * dl) < 2.0:
                continue  # miejsce na schody (przód)
            px, py = ((x + t * dl, y - g / 2) if bok == 0 else (x + t * dl, y + g / 2) if bok == 1
                      else (x - w / 2, y + t * dl) if bok == 2 else (x + w / 2, y + t * dl))
            s = rng.uniform(1.4, 1.9)
            sl.add(rock(s, 1.2, h + rng.uniform(0.0, 0.35), 3000 + bok * 50 + i, rough=0.1), rng.choice(('mtn', 'mtn_dark', 'stone_dark')),
                   'root', mtx((px, py, (h + 0.2) / 2 - 0.05), (0, 0, 0 if bok < 2 else 90)))
    # schody na wprost placu
    kroki = 6
    for k in range(kroki):
        sl.add(box(3.6, 0.5, h * (k + 1) / kroki, 0.03), 'stone', 'root',
               mtx((x, y - g / 2 - 0.25 - (kroki - 1 - k) * 0.45, h * (k + 1) / kroki / 2)))
    for sg in (1, -1):
        sl.add(rock(0.6, 3.0, h * 0.8, 3100 + sg, rough=0.08), 'stone_dark', 'root',
               mtx((x + sg * 2.1, y - g / 2 - 1.3, h * 0.4), (14, 0, 0)))
    # kamienna ścieżka na półce od schodów do budynku
    sl.add(box(2.4, 2.6, 0.06, 0.02), 'paving', 'root', mtx((x, y - g / 2 + 1.4, h + 0.1)))


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
    _szczegoly_gory(sl, rng)
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
        if d.get('podwyzszenie'):
            continue  # do podwyższenia prowadzą schody prosto z placu
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
        if d.get('podwyzszenie'):
            _podwyzszenie(sl, x, y, w, g, d['podwyzszenie'])
            continue
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
    for (x, y) in ((-15.5, -10.0), (15.5, -10.0), (-15.5, 4.5), (15.5, 4.5), (-8.3, 12.3), (8.5, 12.4), (14.5, 11.5)):
        drzewo(sl, V(x, y, 0), 1.0, rng)
