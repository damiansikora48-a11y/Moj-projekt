"""MAPA – BUDYNEK GŁÓWNY (20 poziomów, każdy poziom coś widocznie zmienia).

Stoi na skalnej półce (podwyższeniu) działki D1 przy ścianie góry. Środek układu (0,0,0) = środek
górnej powierzchni półki; przód (schody) = -Y. Budynek stoi z tyłu półki, z przodu zostaje podwórze.

Etapy:
   1–5  mała drewniana chata z bali       11–15  kamienna sala
   6–10 duży drewniany dom                16–20  okazała kamienna rezydencja ze zdobieniami
Lista „co daje który poziom” jest w ZMIANY (pokazywana też w uklad.json).
Zmiana wyglądu poziomu: znajdź `p >= N` w funkcjach poniżej.
"""
import math
import random

import bmesh

from kit import V, box, cyl, sphere, ico, rock, taper, jitter, mtx, frame, seg
from mapa.mury import _wieza, _dach, DACHOWKI, GONT

PALETA = {
    'log': ('#8a5a2b', 0.85), 'log_dark': ('#6b4423', 0.9), 'wood': ('#9a6a36', 0.85), 'wood_dark': ('#5e3b1c', 0.9),
    'shingle': ('#7a4e2a', 0.9), 'shingle_dark': ('#5a3820', 0.9),
    'plaster': ('#ece4d0', 0.9), 'beam': ('#4a2f1a', 0.9),
    'stone': ('#9a948a', 0.92), 'stone_dark': ('#6d665e', 0.95), 'stone_light': ('#c4bdaf', 0.9),
    'roof': ('#2f5fb8', 0.75), 'roof_dark': ('#234a94', 0.75), 'gold': ('#e0ac3c', 0.3, 0.9), 'iron': ('#4d545c', 0.45, 0.8),
    'glass': ('#2a3a4a', 0.2), 'glass_lit': ('#ffcf7a', 0.3, 0.0, 1.6), 'lamp': ('#ffd27a', 0.3, 0.0, 3.0),
    'banner': ('#2f5fb8', 0.8), 'banner_red': ('#a82a2a', 0.8), 'carpet': ('#9c2424', 0.85),
    'fire': ('#ff5200', 0.4, 0.0, 2.2), 'fire_core': ('#ffae00', 0.3, 0.0, 3.0),
    'crystal': ('#7fd6ef', 0.12, 0.0, 1.5), 'leaves': ('#4f9a3a', 0.85), 'flower_r': ('#e04848', 0.7), 'flower_y': ('#f2d04a', 0.7),
    'smoke': ('#d8d8d8', 0.9),
}

ZMIANY = {
    1: 'mała chata z bali z drzwiami', 2: 'okna z okiennicami, ławka i beczka', 3: 'kamienny komin',
    4: 'zadaszony ganek, latarnie przy schodach', 5: 'drewniana dobudówka z boku',
    6: 'duży drewniany dom na kamiennym fundamencie', 7: 'piętro z muru pruskiego, donice z kwiatami',
    8: 'skrzydło boczne', 9: 'drewniana wieża obserwacyjna, sztandary przy wejściu', 10: 'duży kamienny komin, latarnie na fasadzie, herb nad drzwiami',
    11: 'kamienna sala z piętrem z muru pruskiego', 12: 'łukowy kamienny portal i narożniki z jasnego kamienia, balustrada na półce',
    13: 'pierwsza kamienna wieża', 14: 'druga kamienna wieża, kosze z ogniem przy schodach', 15: 'dachy z niebieskiej dachówki i flagi',
    16: 'okazała dwupiętrowa rezydencja z łukowymi oknami', 17: 'złote gzymsy, ozdobne obramienia okien, herb, posągi',
    18: 'portyk z kolumnami', 19: 'wysokie wieże z balkonami i długimi sztandarami, czerwony dywan', 20: 'iglica z kryształem, świecące okna, złote zwieńczenia',
}

TY = 0.9  # przesunięcie budynku do tyłu półki (z przodu zostaje podwórze)


# ------------------------------------------------------------------ pomocnicze

def _sciana_bloki(sl, rng, a, b, z0, z1, gl=0.5, mats=('stone', 'stone_dark', 'stone_light'), wys=0.55):
    """Ściana z kamiennych bloków wzdłuż odcinka a->b (punkty 2D)."""
    a, b = V(a[0], a[1], 0), V(b[0], b[1], 0)
    d = b - a
    L, kat = d.length, math.degrees(math.atan2(d.y, d.x))
    u = d.normalized()
    z, r = z0, 0
    while z < z1 - 0.05:
        h = min(wys, z1 - z)
        s = -0.4 if r % 2 else 0.0
        while s < L:
            dl = rng.uniform(0.7, 1.1)
            s0, s1 = max(s, 0.0), min(s + dl, L)
            if s1 - s0 > 0.15:
                p = a + u * ((s0 + s1) / 2)
                sl.add(rock(s1 - s0 - 0.03, gl, h - 0.03, rng.randint(0, 9999), rough=0.03, bevel=0.1), rng.choice(mats), 'root',
                       mtx((p.x, p.y, z + h / 2), (0, 0, kat)))
            s += dl
        z += h
        r += 1


def _bale(sl, cx, cy, w, d, z0, h, r=0.16):
    """Ściany z poziomych bali (narożniki na zakładkę)."""
    z, k = z0 + r, 0
    while z < z0 + h:
        for sg in (1, -1):
            off = 0.0 if k % 2 == 0 else 0.15
            sl.add(cyl(r, r, w + 0.5, 8), 'log' if k % 3 else 'log_dark', 'root',
                   seg(V(cx - w / 2 - 0.25 + off, cy + sg * d / 2, z), V(cx + w / 2 + 0.25 + off, cy + sg * d / 2, z)))
            sl.add(cyl(r, r, d + 0.5, 8), 'log' if (k + 1) % 3 else 'log_dark', 'root',
                   seg(V(cx + sg * w / 2, cy - d / 2 - 0.25, z + r), V(cx + sg * w / 2, cy + d / 2 + 0.25, z + r)))
        z += 2 * r
        k += 1
    sl.add(box(w, d, h, 0.02), 'log_dark', 'root', mtx((cx, cy, z0 + h / 2)))  # wnętrze (bez prześwitów)


def _szczyt(sl, cx, cy, w, d, z0, h, mat, gr=0.18):
    """Trójkątne ściany szczytowe pod dachem dwuspadowym (kalenica wzdłuż X)."""
    for sg in (1, -1):
        bm = bmesh.new()
        x = cx + sg * (w / 2 - gr / 2)
        v = [bm.verts.new(V(x, cy - d / 2, z0)), bm.verts.new(V(x, cy + d / 2, z0)), bm.verts.new(V(x, cy, z0 + h))]
        bm.faces.new(v)
        bm.normal_update()
        bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=gr)
        sl.add(bm, mat, 'root')


def _dach2(sl, cx, cy, z0, w, d, h, mats=GONT, ov=0.45, rzedy=5, szczyt='wood'):
    """Dach dwuspadowy z rzędów gontu/dachówek (kalenica wzdłuż X) + ściany szczytowe."""
    if szczyt:
        _szczyt(sl, cx, cy, w, d, z0, h, szczyt)
    pol = d / 2 + ov
    hh = h * pol / (d / 2)
    kat = math.atan2(hh, pol)
    dl = math.hypot(pol, hh)
    for sg in (-1, 1):
        n = V(0, sg * math.sin(kat), math.cos(kat))
        E, R = V(cx, cy + sg * pol, z0 - (hh - h)), V(cx, cy, z0 + h)
        for k in range(rzedy):
            P = E + (R - E) * ((k + 0.5) / rzedy) + n * (0.07 + 0.02 * (k % 2))
            sl.add(box(w + 2 * ov, dl / rzedy * 1.18, 0.1, 0.02), mats[k % 2], 'root', frame(P, n, (1, 0, 0)))
    sl.add(cyl(0.12, 0.12, w + 2 * ov + 0.1, 8), 'wood_dark', 'root', seg(V(cx - w / 2 - ov - 0.05, cy, z0 + h + 0.1), V(cx + w / 2 + ov + 0.05, cy, z0 + h + 0.1)))


def _szachulec(sl, cx, cy, w, d, z0, h):
    """Mur pruski: biały tynk z ciemnymi belkami (pionowe, poziome, skośne)."""
    sl.add(box(w, d, h, 0.03), 'plaster', 'root', mtx((cx, cy, z0 + h / 2)))
    for y, dl in ((cy - d / 2 - 0.04, w), (cy + d / 2 + 0.04, w)):
        for z in (z0 + 0.08, z0 + h - 0.08):
            sl.add(box(dl, 0.1, 0.16, 0.02), 'beam', 'root', mtx((cx, y, z)))
        n = max(2, int(dl / 1.3))
        for i in range(n + 1):
            x = cx - dl / 2 + i * dl / n
            sl.add(box(0.14, 0.1, h, 0.02), 'beam', 'root', mtx((x, y, z0 + h / 2)))
            if i < n and i % 2 == 0:
                p0, p1 = V(x, y, z0 + 0.1), V(x + dl / n, y, z0 + h - 0.1)
                sl.add(box(0.12, 0.08, (p1 - p0).length), 'beam', 'root', seg(p0, p1, (0, 1, 0)))
    for x in (cx - w / 2 - 0.04, cx + w / 2 + 0.04):
        for z in (z0 + 0.08, z0 + h - 0.08):
            sl.add(box(0.1, d, 0.16, 0.02), 'beam', 'root', mtx((x, cy, z)))
        for yy in (cy - d / 2, cy, cy + d / 2):
            sl.add(box(0.1, 0.14, h, 0.02), 'beam', 'root', mtx((x, yy, z0 + h / 2)))


def _okno(sl, x, y, z, w=0.7, h=0.9, szklo='glass', rama='wood_dark', luk=False, okiennice=False, bok=False):
    """Okno na ścianie przedniej (bok=False, normalna -Y) albo bocznej (bok=True)."""
    def M(px, py, pz):
        return mtx((x + (py if bok else px), y + (px if bok else py), z + pz), (0, 0, 90 if bok else 0))
    sl.add(box(w, 0.08, h, 0.01), szklo, 'root', M(0, 0, 0))
    for sx in (-1, 1):
        sl.add(box(0.1, 0.12, h + 0.15, 0.02), rama, 'root', M(sx * (w / 2 + 0.03), -0.02, 0))
    sl.add(box(w + 0.2, 0.16, 0.1, 0.02), rama, 'root', M(0, -0.04, -h / 2 - 0.05))
    if luk:
        sl.add(cyl(w / 2 + 0.06, w / 2 + 0.06, 0.12, 10), rama, 'root', M(0, -0.02, h / 2) @ mtx(rot=(90, 0, 0)))
        sl.add(cyl(w / 2 - 0.02, w / 2 - 0.02, 0.1, 10), szklo, 'root', M(0, 0.0, h / 2) @ mtx(rot=(90, 0, 0)))
    else:
        sl.add(box(w + 0.2, 0.14, 0.1, 0.02), rama, 'root', M(0, -0.03, h / 2 + 0.05))
    if okiennice:
        for sx in (-1, 1):
            sl.add(box(w / 2, 0.06, h, 0.01), 'wood', 'root', M(sx * (w * 0.75 + 0.05), -0.06, 0))


def _drzwi(sl, x, y, z, w=1.0, h=1.9, luk=False, mat='wood'):
    sl.add(box(w, 0.12, h, 0.02), mat, 'root', mtx((x, y, z + h / 2)))
    for zz in (0.3, h - 0.3):
        sl.add(box(w, 0.04, 0.08, 0.01), 'iron', 'root', mtx((x, y - 0.08, z + zz)))
    sl.add(sphere(0.05, u=8, v=6), 'gold', 'root', mtx((x + w * 0.32, y - 0.1, z + h * 0.5)))
    if luk:
        sl.add(cyl(w / 2, w / 2, 0.12, 12), mat, 'root', mtx((x, y, z + h), (90, 0, 0)))


def _latarnia(sl, x, y, z, wys=1.8):
    sl.add(cyl(0.06, 0.06, wys, 6), 'wood_dark', 'root', mtx((x, y, z + wys / 2)))
    sl.add(box(0.26, 0.26, 0.32, 0.03), 'lamp', 'root', mtx((x, y, z + wys + 0.12)))
    sl.add(cyl(0.22, 0.0, 0.18, 4), 'iron', 'root', mtx((x, y, z + wys + 0.37), (0, 0, 45)))


def _sztandar(sl, x, y, z, wys=3.2, mat='banner'):
    sl.add(cyl(0.05, 0.05, wys, 6), 'wood_dark', 'root', mtx((x, y, z + wys / 2)))
    sl.add(sphere(0.08, u=8, v=6), 'gold', 'root', mtx((x, y, z + wys + 0.05)))
    sl.add(box(0.6, 0.04, 1.3, 0.01), mat, 'root', mtx((x + 0.32, y, z + wys - 0.75)))
    sl.add(box(0.2, 0.05, 0.2, 0.01), 'gold', 'root', mtx((x + 0.32, y - 0.03, z + wys - 0.6), (0, 45, 0)))


def _kosz_ognia(sl, x, y, z):
    sl.add(cyl(0.12, 0.2, 0.9, 8), 'stone_dark', 'root', mtx((x, y, z + 0.45)))
    sl.add(cyl(0.38, 0.22, 0.3, 10), 'iron', 'root', mtx((x, y, z + 1.05)))
    for i in range(4):
        a = i * math.pi / 2
        sl.add(cyl(0.12, 0.0, 0.55, 6), 'fire', 'root', mtx((x + math.cos(a) * 0.12, y + math.sin(a) * 0.12, z + 1.45)))
    sl.add(cyl(0.08, 0.0, 0.4, 6), 'fire_core', 'root', mtx((x, y, z + 1.4)))


def _posag(sl, x, y, z):
    sl.add(box(0.9, 0.9, 0.9, 0.06), 'stone', 'root', mtx((x, y, z + 0.45)))
    sl.add(box(1.0, 1.0, 0.12, 0.03), 'stone_light', 'root', mtx((x, y, z + 0.95)))
    sl.add(cyl(0.28, 0.32, 1.1, 10), 'stone_light', 'root', mtx((x, y, z + 1.55)))
    sl.add(sphere(0.2, u=10, v=8), 'stone_light', 'root', mtx((x, y, z + 2.25)))
    sl.add(box(0.08, 0.06, 1.3, 0.01), 'stone_light', 'root', mtx((x + 0.32, y - 0.15, z + 1.6)))
    sl.add(box(0.3, 0.06, 0.06, 0.01), 'stone_light', 'root', mtx((x + 0.32, y - 0.15, z + 1.05)))


def _komin(sl, x, y, z0, h, w=0.7):
    rng = random.Random(int(x * 10 + h * 7))
    _sciana_bloki(sl, rng, (x - w / 2, y), (x + w / 2, y), z0, z0 + h, gl=w, wys=0.45)
    sl.add(box(w + 0.15, w + 0.15, 0.15, 0.03), 'stone_dark', 'root', mtx((x, y, z0 + h + 0.07)))
    for i in range(3):
        sl.add(sphere(0.22 + 0.08 * i, u=8, v=6), 'smoke', 'root', mtx((x + 0.15 * i, y, z0 + h + 0.45 + 0.4 * i)))


# ------------------------------------------------------------------ podwórze na półce (zmienia się z poziomem)

def _podworze(sl, p):
    y0 = -4.25  # przednia krawędź półki
    if p >= 2:  # ławka i beczka
        sl.add(box(1.4, 0.4, 0.08, 0.02), 'wood', 'root', mtx((-3.6, -1.2, 0.48)))
        for sx in (-0.55, 0.55):
            sl.add(box(0.08, 0.36, 0.44, 0.01), 'wood_dark', 'root', mtx((-3.6 + sx, -1.2, 0.22)))
        sl.add(cyl(0.32, 0.32, 0.75, 10), 'wood', 'root', mtx((3.8, -0.9, 0.38)))
        for z in (0.15, 0.6):
            sl.add(cyl(0.34, 0.34, 0.05, 10), 'iron', 'root', mtx((3.8, -0.9, z)))
    if 4 <= p < 14:  # latarnie przy schodach
        for sx in (-1.6, 1.6):
            _latarnia(sl, sx, y0 + 0.4, 0.0)
    if p >= 14:  # kosze z ogniem zamiast latarni
        for sx in (-1.7, 1.7):
            _kosz_ognia(sl, sx, y0 + 0.5, 0.0)
    if p >= 7:  # donice z kwiatami
        for sx in (-5.6, 5.6):
            sl.add(box(1.2, 0.6, 0.45, 0.04), 'wood_dark' if p < 12 else 'stone', 'root', mtx((sx, -2.6, 0.22)))
            for i in range(4):
                sl.add(ico(0.16, 1), 'leaves', 'root', mtx((sx - 0.4 + i * 0.27, -2.6, 0.55)))
                sl.add(ico(0.07, 0), ('flower_r', 'flower_y')[i % 2], 'root', mtx((sx - 0.4 + i * 0.27, -2.75, 0.68)))
    if p >= 9:  # sztandary przy wejściu
        for sx in (-2.6, 2.6):
            _sztandar(sl, sx, -1.7, 0.0, 3.2 if p < 19 else 4.0, 'banner' if p < 19 else 'banner_red')
    if p >= 12:  # kamienna balustrada na krawędzi półki (z przerwą na schody)
        for sg in (1, -1):
            a, b = sg * 2.0, sg * 6.8
            sl.add(box(abs(b - a), 0.3, 0.12, 0.02), 'stone_light', 'root', mtx(((a + b) / 2, y0 + 0.2, 0.85)))
            x = a
            while (x - b) * sg < 0.01:
                sl.add(cyl(0.08, 0.1, 0.75, 8), 'stone', 'root', mtx((x, y0 + 0.2, 0.38)))
                x += sg * 0.5
    if p >= 17:  # posągi
        for sx in (-4.6, 4.6):
            _posag(sl, sx, -2.9, 0.0)
    if p >= 19:  # czerwony dywan od schodów do drzwi
        sl.add(box(1.6, 3.4, 0.03, 0.0), 'carpet', 'root', mtx((0, -2.5, 0.08)))
        sl.add(box(1.7, 3.4, 0.02, 0.0), 'gold', 'root', mtx((0, -2.5, 0.06)))


# ------------------------------------------------------------------ etapy budynku

def _chata(sl, p):
    cx, cy, w, d = 0.0, TY + 0.6, 4.2, 3.4
    _bale(sl, cx, cy, w, d, 0.0, 2.4)
    _dach2(sl, cx, cy, 2.4, w, d, 1.6, szczyt='log')
    _drzwi(sl, cx, cy - d / 2 - 0.2, 0.0, 1.0, 1.8)
    if p >= 2:
        for sx in (-1.3, 1.3):
            _okno(sl, sx, cy - d / 2 - 0.2, 1.3, 0.6, 0.6, okiennice=True)
    if p >= 3:
        _komin(sl, cx + w / 2 + 0.35, cy + 0.6, 0.0, 4.6, 0.65)
    if p >= 4:  # ganek
        for sx in (-0.9, 0.9):
            sl.add(cyl(0.09, 0.09, 2.1, 6), 'wood_dark', 'root', mtx((sx, cy - d / 2 - 1.2, 1.05)))
        sl.add(box(2.4, 1.5, 0.12, 0.03), 'shingle', 'root', mtx((0, cy - d / 2 - 0.6, 2.2), (-14, 0, 0)))
        sl.add(box(2.2, 1.4, 0.1, 0.02), 'wood', 'root', mtx((0, cy - d / 2 - 0.65, 0.05)))
    if p >= 5:  # dobudówka
        _bale(sl, cx - w / 2 - 1.2, cy + 0.2, 2.2, 2.4, 0.0, 1.8, r=0.14)
        _dach2(sl, cx - w / 2 - 1.2, cy + 0.2, 1.8, 2.2, 2.4, 1.0, ov=0.3, rzedy=3, szczyt='log')
        _okno(sl, cx - w / 2 - 1.2, cy + 0.2 - 1.4, 1.0, 0.5, 0.5, okiennice=True)


def _dom(sl, p):
    cx, cy, w, d = 0.0, TY + 0.4, 6.4, 4.2
    rng = random.Random(606)
    _sciana_bloki(sl, rng, (cx - w / 2 - 0.1, cy - d / 2 - 0.05), (cx + w / 2 + 0.1, cy - d / 2 - 0.05), 0.0, 0.5, gl=0.3)
    sl.add(box(w + 0.2, d + 0.2, 0.5, 0.03), 'stone_dark', 'root', mtx((cx, cy, 0.25)))
    _bale(sl, cx, cy, w, d, 0.5, 2.6, r=0.17)
    top = 3.1
    if p >= 7:  # piętro z muru pruskiego
        _szachulec(sl, cx, cy, w + 0.2, d + 0.2, top, 2.1)
        for sx in (-1.8, 0.0, 1.8):
            _okno(sl, sx, cy - d / 2 - 0.16, top + 1.05, 0.6, 0.8)
        top += 2.1
    _dach2(sl, cx, cy, top, w + 0.2, d + 0.2, 2.0, szczyt='plaster' if p >= 7 else 'log')
    _drzwi(sl, cx, cy - d / 2 - 0.2, 0.5, 1.4, 2.0)
    for sx in (-2.0, 2.0):
        _okno(sl, sx, cy - d / 2 - 0.2, 1.7, 0.7, 0.8, okiennice=True)
    if p >= 8:  # skrzydło boczne
        bx = cx + w / 2 + 1.5
        _bale(sl, bx, cy + 0.4, 2.8, 3.2, 0.0, 2.6, r=0.15)
        _dach2(sl, bx, cy + 0.4, 2.6, 2.8, 3.2, 1.3, ov=0.35, rzedy=4, szczyt='log')
        _okno(sl, bx, cy + 0.4 - 1.8, 1.4, 0.6, 0.7, okiennice=True)
    if p >= 9:  # wieża obserwacyjna
        tx, ty = cx - w / 2 - 0.6, cy + d / 2 - 0.4
        for ox in (-0.7, 0.7):
            for oy in (-0.7, 0.7):
                sl.add(cyl(0.12, 0.12, 6.4, 6), 'wood_dark', 'root', mtx((tx + ox, ty + oy, 3.2)))
        sl.add(box(2.0, 2.0, 0.16, 0.03), 'wood', 'root', mtx((tx, ty, 6.2)))
        for (ox, oy, ww, dd) in ((0, -0.95, 2.0, 0.08), (0, 0.95, 2.0, 0.08), (-0.95, 0, 0.08, 2.0), (0.95, 0, 0.08, 2.0)):
            sl.add(box(ww, dd, 0.7, 0.02), 'wood', 'root', mtx((tx + ox, ty + oy, 6.6)))
        _dach(sl, tx, ty, 7.4, 1.6, 1.4, GONT, boki=4, rzedy=3, obrot=45, iglica=False)
        for ox in (-0.85, 0.85):
            for oy in (-0.85, 0.85):
                sl.add(cyl(0.06, 0.06, 1.2, 6), 'wood_dark', 'root', mtx((tx + ox, ty + oy, 6.9)))
    if p >= 10:  # duży komin, latarnie na fasadzie, herb nad drzwiami
        _komin(sl, cx + 1.8, cy + 0.3, top, 2.6, 0.8)
        for sx in (-1.0, 1.0):
            sl.add(box(0.22, 0.22, 0.3, 0.03), 'lamp', 'root', mtx((sx, cy - d / 2 - 0.3, 2.3)))
        sl.add(box(0.7, 0.08, 0.8, 0.04), 'banner', 'root', mtx((cx, cy - d / 2 - 0.22, 2.95)))
        sl.add(box(0.3, 0.06, 0.3, 0.02), 'gold', 'root', mtx((cx, cy - d / 2 - 0.27, 2.95), (0, 45, 0)))


def _sala(sl, p):
    cx, cy, w, d = 0.0, TY + 0.3, 7.4, 4.6
    rng = random.Random(1111)
    for a, b in (((cx - w / 2, cy - d / 2), (cx + w / 2, cy - d / 2)), ((cx - w / 2, cy + d / 2), (cx + w / 2, cy + d / 2)),
                 ((cx - w / 2, cy - d / 2), (cx - w / 2, cy + d / 2)), ((cx + w / 2, cy - d / 2), (cx + w / 2, cy + d / 2))):
        _sciana_bloki(sl, rng, a, b, 0.0, 3.2)
    sl.add(box(w - 0.3, d - 0.3, 3.2, 0.02), 'stone_dark', 'root', mtx((cx, cy, 1.6)))
    _szachulec(sl, cx, cy, w + 0.1, d + 0.1, 3.2, 2.3)
    for sx in (-2.4, -0.8, 0.8, 2.4):
        _okno(sl, sx, cy - d / 2 - 0.12, 4.3, 0.6, 0.85)
    dachy = DACHOWKI if p >= 15 else GONT
    _dach2(sl, cx, cy, 5.5, w + 0.1, d + 0.1, 2.3, mats=dachy, szczyt='plaster')
    _drzwi(sl, cx, cy - d / 2 - 0.3, 0.0, 1.4, 2.1, luk=p >= 12)
    for sx in (-2.3, 2.3):
        _okno(sl, sx, cy - d / 2 - 0.3, 1.6, 0.7, 1.0, luk=p >= 12, rama='stone_light' if p >= 12 else 'wood_dark')
    if p >= 12:  # łukowy portal i narożniki z jasnego kamienia
        for sx in (-1.05, 1.05):
            sl.add(box(0.3, 0.3, 2.3, 0.04), 'stone_light', 'root', mtx((sx, cy - d / 2 - 0.3, 1.15)))
        sl.add(cyl(1.05, 1.05, 0.3, 12), 'stone_light', 'root', mtx((cx, cy - d / 2 - 0.3, 2.1), (90, 0, 0)))
        for sx in (-w / 2, w / 2):
            for k in range(5):
                sl.add(box(0.5 if k % 2 else 0.36, 0.5 if k % 2 else 0.36, 0.6, 0.04), 'stone_light', 'root',
                       mtx((sx, cy - d / 2, 0.3 + k * 0.62)))
    roof = DACHOWKI if p >= 15 else GONT
    if p >= 13:  # pierwsza wieża
        _wieza(sl, random.Random(13), 1.5, 1.4, 0.0, 6.6, cx=cx - w / 2 - 0.5, cy=cy + d / 2 - 0.4, wys_rzedu=0.6)
        _dach(sl, cx - w / 2 - 0.5, cy + d / 2 - 0.4, 6.6, 1.75, 2.4, roof, boki=14, rzedy=5, iglica=p >= 15)
        _okno(sl, cx - w / 2 - 0.5, cy + d / 2 - 0.4 - 1.5, 4.6, 0.4, 0.7, luk=True)
    if p >= 14:  # druga wieża
        _wieza(sl, random.Random(14), 1.5, 1.4, 0.0, 6.6, cx=cx + w / 2 + 0.5, cy=cy + d / 2 - 0.4, wys_rzedu=0.6)
        _dach(sl, cx + w / 2 + 0.5, cy + d / 2 - 0.4, 6.6, 1.75, 2.4, roof, boki=14, rzedy=5, iglica=p >= 15)
        _okno(sl, cx + w / 2 + 0.5, cy + d / 2 - 0.4 - 1.5, 4.6, 0.4, 0.7, luk=True)
    if p >= 15:  # flagi na wieżach
        for sx in (-w / 2 - 0.5, w / 2 + 0.5):
            sl.add(cyl(0.04, 0.04, 1.2, 6), 'iron', 'root', mtx((sx, cy + d / 2 - 0.4, 9.85)))
            sl.add(box(0.55, 0.03, 0.35, 0.01), 'banner', 'root', mtx((sx + 0.3, cy + d / 2 - 0.4, 10.2)))


def _rezydencja(sl, p):
    cx, cy, w, d = 0.0, TY + 0.2, 8.8, 5.0
    rng = random.Random(1616)
    H = 5.8
    for a, b in (((cx - w / 2, cy - d / 2), (cx + w / 2, cy - d / 2)), ((cx - w / 2, cy + d / 2), (cx + w / 2, cy + d / 2)),
                 ((cx - w / 2, cy - d / 2), (cx - w / 2, cy + d / 2)), ((cx + w / 2, cy - d / 2), (cx + w / 2, cy + d / 2))):
        _sciana_bloki(sl, rng, a, b, 0.0, H, mats=('stone', 'stone_light', 'stone'))
    sl.add(box(w - 0.3, d - 0.3, H, 0.02), 'stone_dark', 'root', mtx((cx, cy, H / 2)))
    sl.add(box(w + 0.3, d + 0.3, 0.25, 0.04), 'stone_light', 'root', mtx((cx, cy, 2.9)))  # gzyms między piętrami
    szklo = 'glass_lit' if p >= 20 else 'glass'
    rama = 'gold' if p >= 17 else 'stone_light'
    for z in (1.5, 4.2):
        for sx in (-3.3, -1.9, 1.9, 3.3):
            _okno(sl, sx, cy - d / 2 - 0.3, z, 0.65, 1.1, szklo=szklo, rama=rama, luk=True)
    _okno(sl, 0.0, cy - d / 2 - 0.3, 4.2, 0.9, 1.2, szklo=szklo, rama=rama, luk=True)
    _drzwi(sl, cx, cy - d / 2 - 0.3, 0.0, 1.6, 2.4, luk=True)
    _dach2(sl, cx, cy, H, w + 0.3, d + 0.3, 3.0, mats=DACHOWKI, rzedy=6, szczyt='stone_light')
    th = 9.0 if p < 19 else 11.0
    for sx in (-1, 1):  # wieże narożne
        tx, ty = cx + sx * (w / 2 + 0.7), cy + d / 2 - 0.6
        _wieza(sl, random.Random(16 + sx), 1.8, 1.65, 0.0, th, cx=tx, cy=ty, wys_rzedu=0.6)
        _dach(sl, tx, ty, th, 2.05, 3.2, boki=16, rzedy=6)
        for z in (3.0, 6.0):
            _okno(sl, tx, ty - 1.8, z, 0.45, 0.8, szklo=szklo, rama=rama, luk=True)
        if p >= 19:  # balkon i długi sztandar
            sl.add(cyl(2.15, 2.15, 0.2, 16), 'stone_light', 'root', mtx((tx, ty, th - 1.6)))
            for i in range(10):
                a = 2 * math.pi * i / 10
                sl.add(cyl(0.06, 0.06, 0.6, 6), 'stone_light', 'root', mtx((tx + math.cos(a) * 2.05, ty + math.sin(a) * 2.05, th - 1.2)))
            sl.add(box(0.9, 0.05, 3.4, 0.01), 'banner_red', 'root', mtx((tx, ty - 1.86, th - 4.0)))
            sl.add(box(0.35, 0.06, 0.35, 0.01), 'gold', 'root', mtx((tx, ty - 1.9, th - 3.0), (0, 45, 0)))
    if p >= 17:  # złote gzymsy i herb
        sl.add(box(w + 0.35, d + 0.35, 0.12, 0.02), 'gold', 'root', mtx((cx, cy, 3.06)))
        sl.add(box(w + 0.35, d + 0.35, 0.14, 0.02), 'gold', 'root', mtx((cx, cy, H - 0.05)))
        sl.add(box(1.2, 0.1, 1.4, 0.05), 'banner', 'root', mtx((cx, cy - d / 2 - 0.34, 2.95 + 0.0)))
        sl.add(box(0.6, 0.08, 0.6, 0.03), 'gold', 'root', mtx((cx, cy - d / 2 - 0.4, 3.0), (0, 45, 0)))
    if p >= 18:  # portyk z kolumnami i trójkątnym szczytem
        py = cy - d / 2 - 1.5
        for sx in (-1.8, -0.7, 0.7, 1.8):
            sl.add(cyl(0.22, 0.22, 3.0, 12), 'stone_light', 'root', mtx((sx, py, 1.5)))
            sl.add(box(0.55, 0.55, 0.2, 0.03), 'stone_light' if p < 17 else 'gold', 'root', mtx((sx, py, 3.1)))
            sl.add(box(0.55, 0.55, 0.2, 0.03), 'stone', 'root', mtx((sx, py, 0.1)))
        sl.add(box(4.4, 2.6, 0.3, 0.04), 'stone_light', 'root', mtx((0, py + 0.75, 3.35)))
        bm = bmesh.new()
        v = [bm.verts.new(V(-2.3, py - 0.6, 3.5)), bm.verts.new(V(2.3, py - 0.6, 3.5)), bm.verts.new(V(0, py - 0.6, 4.7))]
        bm.faces.new(v)
        bm.normal_update()
        bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.3)
        sl.add(bm, 'stone_light', 'root')
        _dach2(sl, 0, py + 0.55, 3.5, 4.6, 2.4, 1.2, mats=DACHOWKI, ov=0.15, rzedy=3, szczyt=None)
    if p >= 20:  # iglica z kryształem i złote zwieńczenia
        sl.add(box(1.2, 1.2, 1.4, 0.05), 'stone_light', 'root', mtx((cx, cy, H + 3.2)))
        _dach(sl, cx, cy, H + 3.9, 0.8, 2.6, boki=8, rzedy=4, iglica=False)
        sl.add(ico(0.42, 1), 'crystal', 'root', mtx((cx, cy, H + 6.9)) @ mtx(rot=(0, 0, 0)) @ __import__('kit').scale_m(1, 1, 1.6))
        for sx in (-w / 2 - 0.15, w / 2 + 0.15):
            sl.add(sphere(0.22, u=10, v=8), 'gold', 'root', mtx((sx, cy - d / 2 - 0.1, H + 0.3)))


def budynek(sl, p):
    """Budynek główny na poziomie p (1–20) wraz z podwórzem na półce."""
    if p <= 5:
        _chata(sl, p)
    elif p <= 10:
        _dom(sl, p)
    elif p <= 15:
        _sala(sl, p)
    else:
        _rezydencja(sl, p)
    _podworze(sl, p)
    return []
