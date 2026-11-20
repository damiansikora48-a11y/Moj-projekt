"""MAPA – BUDYNKI NA DZIAŁKACH (każdy 20 poziomów, każdy poziom coś widocznie zmienia)
oraz TABLICA OGŁOSZEŃ przy studni.

  kuznia         – Kuźnia (działka D2): ulepszanie broni i pancerzy jednostek
  koszary        – Koszary (działka D6): szkolenie jednostek, zdobywanie doświadczenia
  budynek_fuzji  – Budynek fuzji (działka D3): łączenie jednostek, księga przepisów, Przebudzenie
  magazyn        – Magazyn (działka D5): przechowuje złoto i zapasy
  akademia       – Akademia (działka D4): badania i odkrycia (ulepszenia na całe miasto)

Każdy budynek ma 4 etapy po 5 poziomów:
   1–5  drewniany / prowizoryczny      11–15  kamienny
   6–10 większy drewniany (mur pruski)  16–20  okazały, ze zdobieniami
Lista „co daje który poziom” jest w ZMIANY[<budynek>] (trafia też do uklad.json).

Układ: środek działki = (0, 0, 0), PRZÓD budynku = -Y (w mieście budynek jest obrócony przodem do placu,
patrz uklad.py: 'obrot' działki). Działka ma 7 × 7 m: budynek stoi z tyłu, z przodu jest podwórze.
Nowy budynek: dopisz funkcję `nazwa(sl, p)` + ZMIANY i wpisz go do BUDYNKI poniżej oraz w uklad.DZIALKI.
"""
import math
import random

import bmesh
from mathutils import Matrix

from kit import V, box, cyl, sphere, ico, rock, taper, jitter, mtx, seg, scale_m
from mapa.mury import _wieza, _dach, DACHOWKI, GONT
from mapa import budynek_glowny as BG
from mapa.budynek_glowny import (_bale, _dach2, _szachulec, _okno, _drzwi, _latarnia, _sztandar, _kosz_ognia,
                                 _komin, _sciana_bloki)

PALETA = {
    **BG.PALETA,
    'canvas': ('#e6dcc2', 0.9), 'canvas_red': ('#b0402f', 0.85), 'straw': ('#d4b25a', 0.95), 'rope': ('#a88a5a', 0.9),
    'coal': ('#262321', 0.95), 'water': ('#3f7fbf', 0.1), 'sand': ('#cdb98a', 0.95), 'paving': ('#a8a196', 0.95),
    'target_w': ('#efe9da', 0.9), 'target_r': ('#c23a32', 0.85), 'leather': ('#6e4428', 0.8),
    'molten': ('#ff7a1a', 0.4, 0.0, 3.5), 'forge_glow': ('#ff9a3c', 0.5, 0.0, 1.8),
    'magic': ('#b46cff', 0.2, 0.0, 2.6), 'magic_soft': ('#c9a0ff', 0.3, 0.0, 1.2), 'magic_dark': ('#4b2a78', 0.6),
    'rune': ('#2fd0ff', 0.4, 0.0, 4.0), 'paper': ('#f3ead2', 0.95), 'paper_y': ('#f0d98a', 0.95),
    'dirt': ('#9a7a52', 0.95), 'gravel': ('#b3a68c', 0.95),
}


class _T:
    """Przekazuje części do slotu z dodatkowym przekształceniem (np. obrót rekwizytu)."""
    def __init__(self, sl, M):
        self.sl, self.M = sl, M

    def add(self, tbm, mat, kosc, M=None):
        if M is not None:
            bmesh.ops.transform(tbm, matrix=M, verts=tbm.verts)
        bmesh.ops.transform(tbm, matrix=self.M, verts=tbm.verts)
        self.sl.add(tbm, mat, kosc)


def _w(sl, x, y, z=0.0, obrot=0.0):
    return _T(sl, mtx((x, y, z), (0, 0, obrot)))


# ------------------------------------------------------------------ rekwizyty (w układzie lokalnym, środek w 0,0)

def _kowadlo(sl, run=False):
    sl.add(cyl(0.32, 0.36, 0.6, 10), 'log_dark', 'root', mtx((0, 0, 0.3)))
    m = 'rune' if run else 'iron'
    sl.add(box(0.34, 0.24, 0.18, 0.02), 'iron', 'root', mtx((0, 0, 0.69)))
    sl.add(box(0.7, 0.3, 0.16, 0.03), 'iron', 'root', mtx((0.06, 0, 0.86)))
    sl.add(taper(box(0.3, 0.2, 0.14, 0.01), bottom=1.0, top=0.3, axis='y'), 'iron', 'root', mtx((0.5, 0, 0.86), (0, 90, 0)))
    if run:
        sl.add(box(0.5, 0.31, 0.03, 0.0), m, 'root', mtx((0.06, 0, 0.94)))
    sl.add(box(0.1, 0.1, 0.35, 0.01), 'wood_dark', 'root', mtx((-0.15, 0.25, 0.75), (0, 70, 20)))  # młot
    sl.add(box(0.12, 0.2, 0.12, 0.02), 'iron', 'root', mtx((0.0, 0.3, 0.82)))


def _palenisko(sl, duze=False):
    s = 1.3 if duze else 1.0
    sl.add(box(1.2 * s, 1.0 * s, 0.75, 0.05), 'stone_dark', 'root', mtx((0, 0, 0.375)))
    sl.add(box(1.0 * s, 0.8 * s, 0.06, 0.01), 'coal', 'root', mtx((0, 0, 0.77)))
    for i in range(5):
        a = i * 1.26
        sl.add(cyl(0.11, 0.0, 0.45, 6), 'fire', 'root', mtx((math.cos(a) * 0.22 * s, math.sin(a) * 0.18 * s, 1.0)))
    sl.add(cyl(0.12, 0.0, 0.5, 6), 'fire_core', 'root', mtx((0, 0, 1.0)))
    sl.add(box(0.8 * s, 0.6 * s, 0.04, 0.0), 'molten', 'root', mtx((0, 0, 0.8)))


def _miech(sl):
    sl.add(taper(box(0.5, 0.9, 0.28, 0.04), bottom=1.0, top=0.6, axis='x'), 'leather', 'root', mtx((0, 0, 0.75)))
    sl.add(box(0.55, 0.95, 0.05, 0.01), 'wood_dark', 'root', mtx((0, 0, 0.9)))
    sl.add(cyl(0.05, 0.05, 0.6, 6), 'iron', 'root', mtx((0, -0.7, 0.75), (90, 0, 0)))
    for x in (-0.2, 0.2):
        sl.add(box(0.08, 0.08, 0.62, 0.01), 'wood_dark', 'root', mtx((x, 0.3, 0.31)))


def _stojak_broni(sl, tarcze=True):
    for x in (-0.75, 0.75):
        sl.add(box(0.1, 0.1, 1.5, 0.01), 'wood_dark', 'root', mtx((x, 0, 0.75)))
    for z in (0.35, 1.35):
        sl.add(box(1.6, 0.1, 0.08, 0.01), 'wood', 'root', mtx((0, 0, z)))
    for i in range(4):
        x = -0.5 + i * 0.33
        sl.add(box(0.07, 0.02, 1.0, 0.0), 'iron', 'root', mtx((x, -0.07, 0.9), (0, 6, 0)))
        sl.add(box(0.26, 0.05, 0.05, 0.0), 'gold' if i % 2 else 'iron', 'root', mtx((x, -0.08, 1.25)))
        sl.add(box(0.06, 0.05, 0.2, 0.0), 'leather', 'root', mtx((x, -0.08, 1.37)))
    if tarcze:
        for x in (-0.45, 0.45):
            sl.add(cyl(0.34, 0.34, 0.06, 14), 'banner' if x < 0 else 'banner_red', 'root', mtx((x, 0.12, 0.6), (90, 0, 0)))
            sl.add(sphere(0.08, u=8, v=6), 'iron', 'root', mtx((x, 0.08, 0.6)))


def _zbroja(sl):
    sl.add(box(0.08, 0.08, 1.2, 0.01), 'wood_dark', 'root', mtx((0, 0, 0.6)))
    sl.add(box(0.5, 0.4, 0.1, 0.02), 'wood_dark', 'root', mtx((0, 0, 0.05)))
    sl.add(taper(box(0.55, 0.32, 0.6, 0.06), bottom=0.8, top=1.0), 'iron', 'root', mtx((0, 0, 1.15)))
    for sx in (-1, 1):
        sl.add(sphere(0.17, u=10, v=8), 'iron', 'root', mtx((sx * 0.33, 0, 1.42)))
    sl.add(sphere(0.18, 0.18, 0.21, u=10, v=8), 'iron', 'root', mtx((0, 0, 1.68)))
    sl.add(box(0.26, 0.05, 0.05, 0.0), 'coal', 'root', mtx((0, -0.17, 1.7)))
    sl.add(box(0.06, 0.06, 0.2, 0.0), 'banner_red', 'root', mtx((0, 0, 1.92)))


def _beczka(sl, woda=False):
    sl.add(cyl(0.3, 0.3, 0.75, 10), 'wood', 'root', mtx((0, 0, 0.375)))
    for z in (0.12, 0.63):
        sl.add(cyl(0.32, 0.32, 0.05, 10), 'iron', 'root', mtx((0, 0, z)))
    if woda:
        sl.add(cyl(0.27, 0.27, 0.02, 10), 'water', 'root', mtx((0, 0, 0.74)))


def _namiot(sl, w=2.4, d=2.2, h=1.8, mat='canvas'):
    kat = math.atan2(h, d / 2)
    dl = math.hypot(d / 2, h)
    for sg in (-1, 1):
        sl.add(box(w, dl, 0.05, 0.0), mat, 'root', mtx((0, sg * d / 4, h / 2), (sg * -math.degrees(kat), 0, 0)))
    bm = bmesh.new()  # tylna ściana (trójkąt)
    vs = [bm.verts.new(V(w / 2 - 0.02, -d / 2, 0)), bm.verts.new(V(w / 2 - 0.02, d / 2, 0)), bm.verts.new(V(w / 2 - 0.02, 0, h))]
    bm.faces.new(vs)
    bm.normal_update()
    bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.05)
    sl.add(bm, mat, 'root')
    for x in (-w / 2 - 0.05, w / 2 + 0.05):
        sl.add(cyl(0.05, 0.05, h + 0.3, 6), 'wood_dark', 'root', mtx((x, 0, (h + 0.3) / 2)))
    sl.add(cyl(0.04, 0.04, w + 0.3, 6), 'wood_dark', 'root', mtx((0, 0, h + 0.02), (0, 90, 0)))
    for sg in (-1, 1):  # odchylone poły wejścia
        sl.add(box(0.05, d / 2 * 0.7, h * 0.8, 0.0), mat, 'root', mtx((-w / 2 - 0.1, sg * d * 0.22, h * 0.35), (0, 0, sg * 25)))


def _ognisko(sl):
    for i in range(7):
        a = 2 * math.pi * i / 7
        sl.add(rock(0.25, 0.2, 0.18, 300 + i), 'stone_dark', 'root', mtx((math.cos(a) * 0.45, math.sin(a) * 0.45, 0.09)))
    for i in range(3):
        sl.add(cyl(0.06, 0.06, 0.7, 6), 'log_dark', 'root', mtx((0, 0, 0.12), (90, 0, i * 60)))
    for i in range(4):
        a = i * 1.57
        sl.add(cyl(0.1, 0.0, 0.5, 6), 'fire', 'root', mtx((math.cos(a) * 0.1, math.sin(a) * 0.1, 0.4)))
    sl.add(cyl(0.08, 0.0, 0.4, 6), 'fire_core', 'root', mtx((0, 0, 0.35)))


def _manekin(sl):
    sl.add(cyl(0.06, 0.06, 1.7, 6), 'wood_dark', 'root', mtx((0, 0, 0.85)))
    sl.add(sphere(0.26, 0.2, 0.38, u=10, v=8), 'straw', 'root', mtx((0, 0, 1.15)))
    sl.add(sphere(0.17, u=10, v=8), 'canvas', 'root', mtx((0, 0, 1.65)))
    sl.add(cyl(0.05, 0.05, 1.0, 6), 'wood_dark', 'root', mtx((0, 0, 1.3), (0, 90, 0)))
    sl.add(box(0.12, 0.03, 0.12, 0.0), 'target_r', 'root', mtx((0, -0.2, 1.2), (0, 45, 0)))
    sl.add(box(0.4, 0.4, 0.12, 0.02), 'wood', 'root', mtx((0, 0, 0.06)))


def _tarcza(sl):
    for i, (r, m) in enumerate(((0.55, 'straw'), (0.45, 'target_w'), (0.33, 'target_r'), (0.21, 'target_w'), (0.1, 'target_r'))):
        sl.add(cyl(r, r, 0.12 + i * 0.015, 18), m, 'root', mtx((0, -i * 0.008, 1.0), (80, 0, 0)))
    for sx in (-0.4, 0.4):
        sl.add(cyl(0.04, 0.04, 1.3, 6), 'wood_dark', 'root', seg(V(sx, 0.35, 0), V(sx * 0.4, 0.05, 1.25)))
    sl.add(cyl(0.04, 0.04, 1.2, 6), 'wood_dark', 'root', seg(V(0, 0.55, 0), V(0, 0.1, 1.3)))
    for i in range(3):  # strzały w tarczy
        sl.add(cyl(0.015, 0.015, 0.5, 4), 'wood', 'root', mtx((-0.12 + i * 0.13, -0.25, 1.0 + (i - 1) * 0.1), (80, 0, 0)))


def _plotek(sl, a, b, h=0.9):
    a, b = V(a[0], a[1], 0), V(b[0], b[1], 0)
    L = (b - a).length
    n = max(1, int(L / 1.0))
    for i in range(n + 1):
        p = a + (b - a) * (i / n)
        sl.add(cyl(0.06, 0.06, h, 6), 'wood_dark', 'root', mtx((p.x, p.y, h / 2)))
    for z in (h * 0.45, h * 0.85):
        sl.add(box(L, 0.06, 0.08, 0.0), 'wood', 'root', seg(V(a.x, a.y, z), V(b.x, b.y, z)) @ mtx(rot=(0, 90, 0)))


def _menhir(sl, h, seed, mat='stone', run=False):
    sl.add(taper(jitter(box(0.6, 0.45, h, 0.08), 0.04, seed), bottom=1.0, top=0.6), mat, 'root', mtx((0, 0, h / 2)))
    if run:
        sl.add(box(0.22, 0.05, 0.22, 0.0), 'rune', 'root', mtx((0, -0.24, h * 0.6), (0, 45, 0)))
        sl.add(box(0.12, 0.05, 0.3, 0.0), 'rune', 'root', mtx((0, -0.24, h * 0.32)))


def _krysztal(sl, s=1.0, mat='magic'):
    sl.add(ico(0.22 * s, 1), mat, 'root', mtx((0, 0, 0)) @ scale_m(1, 1, 2.2))
    for i in range(3):
        a = i * 2.1
        sl.add(ico(0.1 * s, 0), mat, 'root', mtx((math.cos(a) * 0.2 * s, math.sin(a) * 0.2 * s, -0.25 * s)) @ scale_m(1, 1, 2.0))


def _pierscien(sl, r, z, mat='gold', n=20, grub=0.08):
    for i in range(n):
        a = 2 * math.pi * i / n
        sl.add(box(2 * math.pi * r / n * 1.05, grub, grub, 0.0), mat, 'root',
               mtx((math.cos(a) * r, math.sin(a) * r, z), (0, 0, math.degrees(a) + 90)))


def _kosz_magii(sl):
    sl.add(cyl(0.12, 0.2, 0.9, 8), 'stone_dark', 'root', mtx((0, 0, 0.45)))
    sl.add(cyl(0.34, 0.2, 0.28, 10), 'iron', 'root', mtx((0, 0, 1.03)))
    for i in range(4):
        a = i * math.pi / 2
        sl.add(cyl(0.1, 0.0, 0.5, 6), 'magic', 'root', mtx((math.cos(a) * 0.11, math.sin(a) * 0.11, 1.4)))
    sl.add(cyl(0.07, 0.0, 0.38, 6), 'magic_soft', 'root', mtx((0, 0, 1.36)))


def _pulpit(sl):
    sl.add(cyl(0.08, 0.12, 1.0, 8), 'wood_dark', 'root', mtx((0, 0, 0.5)))
    sl.add(box(0.6, 0.45, 0.06, 0.01), 'wood', 'root', mtx((0, 0, 1.05), (-25, 0, 0)))
    sl.add(box(0.5, 0.36, 0.08, 0.01), 'magic_dark', 'root', mtx((0, -0.02, 1.11), (-25, 0, 0)))
    sl.add(box(0.46, 0.33, 0.03, 0.0), 'paper', 'root', mtx((0, -0.04, 1.16), (-25, 0, 0)))
    sl.add(box(0.12, 0.02, 0.12, 0.0), 'magic', 'root', mtx((0, -0.08, 1.19), (-25, 45, 0)))


def _posag_postaci(sl, rodzaj):
    """Posąg na cokole: 'golem' (masywny) albo 'rycerz' (z mieczem)."""
    sl.add(box(0.9, 0.9, 0.7, 0.05), 'stone', 'root', mtx((0, 0, 0.35)))
    sl.add(box(1.0, 1.0, 0.1, 0.02), 'gold', 'root', mtx((0, 0, 0.72)))
    if rodzaj == 'golem':
        sl.add(rock(0.75, 0.5, 0.8, 41, rough=0.06), 'stone_light', 'root', mtx((0, 0, 1.25)))
        sl.add(rock(0.38, 0.34, 0.3, 42, rough=0.06), 'stone_light', 'root', mtx((0, 0, 1.82)))
        for sx in (-1, 1):
            sl.add(rock(0.26, 0.26, 0.7, 43 + sx, rough=0.06), 'stone_light', 'root', mtx((sx * 0.5, 0, 1.2)))
        sl.add(box(0.2, 0.05, 0.06, 0.0), 'rune', 'root', mtx((0, -0.18, 1.85)))
    else:
        sl.add(cyl(0.2, 0.26, 0.9, 10), 'stone_light', 'root', mtx((0, 0, 1.2)))
        sl.add(sphere(0.17, u=10, v=8), 'stone_light', 'root', mtx((0, 0, 1.82)))
        sl.add(box(0.07, 0.05, 1.2, 0.0), 'stone_light', 'root', mtx((0.3, -0.15, 1.4)))
        sl.add(box(0.3, 0.06, 0.06, 0.0), 'stone_light', 'root', mtx((0.3, -0.15, 0.95)))
        sl.add(cyl(0.25, 0.25, 0.06, 12), 'stone_light', 'root', mtx((-0.3, -0.12, 1.2), (90, 0, 0)))


def _herb(sl, x, y, z, mat='banner', znak='gold', s=1.0):
    sl.add(box(0.7 * s, 0.08, 0.85 * s, 0.03), mat, 'root', mtx((x, y, z)))
    sl.add(taper(box(0.7 * s, 0.08, 0.3 * s, 0.01), bottom=0.1, top=1.0), mat, 'root', mtx((x, y, z - 0.57 * s)))
    sl.add(box(0.3 * s, 0.06, 0.3 * s, 0.02), znak, 'root', mtx((x, y - 0.05, z), (0, 45, 0)))


def _bloki_prost(sl, rng, cx, cy, w, d, z0, z1, mats=('stone', 'stone_dark', 'stone_light'), otwor=None):
    """Prostokątne ściany z kamiennych bloków + wypełnienie. otwor=(szer, wys) – przejście na środku przodu."""
    a, b = (cx - w / 2, cy - d / 2), (cx + w / 2, cy - d / 2)
    if otwor:
        ow, oh = otwor
        _sciana_bloki(sl, rng, a, (cx - ow / 2, cy - d / 2), z0, z1, mats=mats)
        _sciana_bloki(sl, rng, (cx + ow / 2, cy - d / 2), b, z0, z1, mats=mats)
        _sciana_bloki(sl, rng, (cx - ow / 2, cy - d / 2), (cx + ow / 2, cy - d / 2), z0 + oh, z1, mats=mats)
    else:
        _sciana_bloki(sl, rng, a, b, z0, z1, mats=mats)
    for p, q in (((cx - w / 2, cy + d / 2), (cx + w / 2, cy + d / 2)), ((cx - w / 2, cy - d / 2), (cx - w / 2, cy + d / 2)),
                 ((cx + w / 2, cy - d / 2), (cx + w / 2, cy + d / 2))):
        _sciana_bloki(sl, rng, p, q, z0, z1, mats=mats)
    sl.add(box(w - 0.3, d - 0.3, z1 - z0, 0.02), 'stone_dark', 'root', mtx((cx, cy, (z0 + z1) / 2)))


# ================================================================== KUŹNIA

ZMIANY_KUZNIA = {
    1: 'szopa z bali z daszkiem i kowadłem na pniu', 2: 'kamienne palenisko z ogniem', 3: 'kamienny komin',
    4: 'koryto z wodą i kamień szlifierski', 5: 'stojak z bronią i tarczami',
    6: 'warsztat z muru pruskiego z dużym zadaszeniem', 7: 'skórzany miech przy palenisku',
    8: 'drugie kowadło, sterta węgla i beczka', 9: 'szyld z kowadłem na wysięgniku', 10: 'wysoki komin i latarnie',
    11: 'kamienna kuźnia z łukowym, rozżarzonym wejściem', 12: 'wielki piec hutniczy', 13: 'stojaki z pełnymi zbrojami',
    14: 'żuraw z łańcuchem i zawieszonym ładunkiem', 15: 'dach z niebieskiej dachówki i sztandary',
    16: 'okazała kuźnia: jasne narożniki, łukowe okna, dwa kominy', 17: 'runiczne kowadło świecące na niebiesko',
    18: 'kanał z płynnym metalem od pieca', 19: 'złoty młot-godło na fasadzie i posąg kowala', 20: 'kryształowe płomienie na kominach i świecące okna',
}


def kuznia(sl, p):
    rng = random.Random(2000 + p)
    if p <= 5:
        cx, cy, w, d = 0.0, 1.9, 3.8, 2.2
        _bale(sl, cx, cy, w, d, 0.0, 2.2, r=0.15)
        _dach2(sl, cx, cy, 2.2, w, d, 1.1, ov=0.35, rzedy=3, szczyt='log')
        _drzwi(sl, 1.0, cy - d / 2 - 0.15, 0.0, 0.9, 1.7)
        for sx in (-1.7, 1.7):  # daszek przed szopą
            sl.add(cyl(0.09, 0.09, 2.2, 6), 'wood_dark', 'root', mtx((sx, -0.6, 1.1)))
        sl.add(box(3.8, 2.1, 0.1, 0.02), 'shingle', 'root', mtx((0, -0.05, 2.25), (-10, 0, 0)))
        _kowadlo(_w(sl, 0.7, -0.2))
        if p >= 2:
            _palenisko(_w(sl, -1.0, 0.0))
        if p >= 3:
            _komin(sl, -1.0, 0.65, 0.0, 3.9, 0.6)
        if p >= 4:
            sl.add(box(1.3, 0.5, 0.45, 0.03), 'wood', 'root', mtx((2.2, -2.3, 0.22)))
            sl.add(box(1.15, 0.36, 0.02, 0.0), 'water', 'root', mtx((2.2, -2.3, 0.43)))
            sl.add(cyl(0.4, 0.4, 0.14, 14), 'stone_light', 'root', mtx((-2.3, -2.2, 0.62), (0, 90, 0)))
            for sy in (-0.12, 0.12):
                sl.add(box(0.08, 0.08, 0.6, 0.0), 'wood_dark', 'root', mtx((-2.3 + sy * 2, -2.2, 0.3)))
        if p >= 5:
            _stojak_broni(_w(sl, 2.85, 0.3, 0, 90))
        return
    if p <= 10:
        cx, cy, w, d = 0.0, 1.8, 5.4, 2.6
        sl.add(box(w + 0.2, d + 0.2, 0.4, 0.03), 'stone_dark', 'root', mtx((cx, cy, 0.2)))
        _szachulec(sl, cx, cy, w, d, 0.4, 2.3)
        _dach2(sl, cx, cy, 2.7, w, d, 1.5, ov=0.4, rzedy=4, szczyt='plaster')
        _drzwi(sl, 1.6, cy - d / 2 - 0.1, 0.4, 1.0, 1.8)
        _okno(sl, -1.6, cy - d / 2 - 0.08, 1.6, 0.7, 0.7, okiennice=True)
        for sx in (-2.6, -0.2, 2.6):  # duże zadaszenie warsztatu
            sl.add(box(0.2, 0.2, 2.6, 0.02), 'beam', 'root', mtx((sx, -1.2, 1.3)))
        sl.add(box(5.8, 0.2, 0.25, 0.02), 'beam', 'root', mtx((0, -1.2, 2.55)))
        sl.add(box(5.9, 2.4, 0.1, 0.02), 'shingle', 'root', mtx((0, -0.35, 2.8), (-12, 0, 0)))
        _palenisko(_w(sl, -1.3, -0.2), duze=True)
        _kowadlo(_w(sl, 0.8, -0.5))
        sl.add(box(1.4, 0.5, 0.45, 0.03), 'wood', 'root', mtx((2.4, -2.6, 0.22)))
        sl.add(box(1.25, 0.36, 0.02, 0.0), 'water', 'root', mtx((2.4, -2.6, 0.43)))
        _stojak_broni(_w(sl, -2.9, -2.0, 0, -90))
        if p < 10:
            _komin(sl, -1.3, 0.6, 0.0, 4.4, 0.7)
        if p >= 7:
            _miech(_w(sl, -2.5, -0.2))
        if p >= 8:
            _kowadlo(_w(sl, 0.4, -1.9, 0, 30))
            for i in range(9):
                sl.add(rock(0.3, 0.3, 0.22, 800 + i, rough=0.15), 'coal', 'root',
                       mtx((2.6 + rng.uniform(-0.4, 0.4), 0.1 + rng.uniform(-0.3, 0.3), 0.1 + (i % 3) * 0.12)))
            _beczka(_w(sl, 2.5, -1.1), woda=True)
        if p >= 9:  # szyld na wysięgniku
            sl.add(box(1.0, 0.08, 0.08, 0.0), 'iron', 'root', mtx((-3.0, -1.2, 2.3)))
            sl.add(box(0.8, 0.06, 0.55, 0.02), 'wood', 'root', mtx((-3.2, -1.2, 1.9)))
            sl.add(box(0.4, 0.03, 0.14, 0.0), 'iron', 'root', mtx((-3.2, -1.25, 1.95)))
            sl.add(box(0.16, 0.03, 0.18, 0.0), 'iron', 'root', mtx((-3.2, -1.25, 1.8)))
        if p >= 10:
            _komin(sl, -1.3, 0.6, 0.0, 6.2, 0.85)
            for sx in (-2.6, 2.6):
                sl.add(box(0.24, 0.24, 0.3, 0.03), 'lamp', 'root', mtx((sx, -1.35, 2.2)))
        return
    if p <= 15:
        cx, cy, w, d = -0.3, 1.6, 5.0, 3.0
        _bloki_prost(sl, rng, cx, cy, w, d, 0.0, 3.0, otwor=(1.8, 2.2))
        sl.add(cyl(0.9, 0.9, 0.35, 14), 'stone_light', 'root', mtx((cx, cy - d / 2 - 0.05, 2.2), (90, 0, 0)))
        sl.add(box(1.7, 0.1, 2.2, 0.0), 'forge_glow', 'root', mtx((cx, cy - d / 2 + 0.2, 1.1)))
        sl.add(cyl(0.82, 0.82, 0.08, 14), 'forge_glow', 'root', mtx((cx, cy - d / 2 + 0.2, 2.2), (90, 0, 0)))
        dachy = DACHOWKI if p >= 15 else GONT
        _dach2(sl, cx, cy, 3.0, w, d, 1.7, mats=dachy, ov=0.4, rzedy=5, szczyt='stone_light')
        _komin(sl, cx - 1.4, cy + 0.4, 3.0, 2.6, 0.8)
        for sx in (-1.8, 1.4):
            _okno(sl, cx + sx, cy - d / 2 - 0.1, 1.5, 0.6, 0.8, szklo='forge_glow')
        _kowadlo(_w(sl, -0.6, -1.0))
        _palenisko(_w(sl, -2.0, -1.0))
        _miech(_w(sl, -3.0, -1.0))
        if p >= 12:  # wielki piec
            _wieza(sl, random.Random(12), 0.85, 0.65, 0.0, 3.8, cx=2.75, cy=1.9, wys_rzedu=0.5, mat=('stone_dark', 'stone', 'stone_dark'))
            sl.add(box(0.55, 0.2, 0.6, 0.02), 'molten', 'root', mtx((2.75, 1.0, 0.7)))
            sl.add(cyl(0.45, 0.35, 0.6, 10), 'iron', 'root', mtx((2.75, 1.9, 4.1)))
        if p >= 13:
            for x in (1.2, 2.2):
                _zbroja(_w(sl, x, -2.5))
        if p >= 14:  # żuraw
            sl.add(box(0.25, 0.25, 4.0, 0.02), 'beam', 'root', mtx((2.9, -0.4, 2.0)))
            sl.add(box(2.2, 0.2, 0.22, 0.02), 'beam', 'root', mtx((2.0, -0.4, 3.9)))
            sl.add(cyl(0.05, 0.05, 1.2, 6), 'beam', 'root', seg(V(2.9, -0.4, 2.9), V(2.2, -0.4, 3.85)))
            sl.add(cyl(0.025, 0.025, 1.6, 4), 'iron', 'root', mtx((1.05, -0.4, 3.0)))
            sl.add(box(0.5, 0.5, 0.4, 0.04), 'stone_dark', 'root', mtx((1.05, -0.4, 2.05)))
        if p >= 15:
            for sx in (-2.0, 1.4):
                _sztandar(sl, sx, -1.9, 0.0, 2.8, 'banner_red')
        return
    # 16–20 okazała kuźnia
    cx, cy, w, d = -0.3, 1.7, 5.4, 3.0
    _bloki_prost(sl, rng, cx, cy, w, d, 0.0, 3.6, mats=('stone', 'stone_light', 'stone'), otwor=(2.0, 2.4))
    sl.add(cyl(1.0, 1.0, 0.4, 16), 'gold' if p >= 19 else 'stone_light', 'root', mtx((cx, cy - d / 2 - 0.05, 2.4), (90, 0, 0)))
    sl.add(box(1.9, 0.1, 2.4, 0.0), 'forge_glow', 'root', mtx((cx, cy - d / 2 + 0.2, 1.2)))
    sl.add(cyl(0.92, 0.92, 0.08, 16), 'forge_glow', 'root', mtx((cx, cy - d / 2 + 0.2, 2.4), (90, 0, 0)))
    for sx in (-w / 2, w / 2):  # jasne narożniki
        for k in range(6):
            sl.add(box(0.48 if k % 2 else 0.36, 0.48 if k % 2 else 0.36, 0.58, 0.04), 'stone_light', 'root',
                   mtx((cx + sx, cy - d / 2, 0.3 + k * 0.6)))
    _dach2(sl, cx, cy, 3.6, w, d, 1.9, mats=DACHOWKI, ov=0.4, rzedy=5, szczyt='stone_light')
    szklo = 'glass_lit' if p >= 20 else 'forge_glow'
    for sx in (-2.0, 1.4):
        _okno(sl, cx + sx, cy - d / 2 - 0.1, 1.6, 0.6, 1.0, szklo=szklo, rama='stone_light', luk=True)
    for kx in (cx - 1.6, cx + 1.6):
        _komin(sl, kx, cy + 0.5, 3.6, 3.0, 0.8)
        if p >= 20:
            _krysztal(_w(sl, kx, cy + 0.5, 7.1), 1.0, 'rune')
    _wieza(sl, random.Random(16), 0.85, 0.65, 0.0, 4.4, cx=2.85, cy=2.2, wys_rzedu=0.5, mat=('stone_dark', 'stone', 'stone_dark'))
    sl.add(box(0.55, 0.2, 0.6, 0.02), 'molten', 'root', mtx((2.85, 1.3, 0.7)))
    sl.add(cyl(0.45, 0.35, 0.6, 10), 'iron', 'root', mtx((2.85, 2.2, 4.7)))
    _kowadlo(_w(sl, -0.6, -1.0), run=p >= 17)
    if p >= 17:
        _krysztal(_w(sl, -0.55, -1.0, 1.35), 0.6, 'rune')
    _palenisko(_w(sl, -2.0, -1.0), duze=True)
    for x in (1.3, 2.3):
        _zbroja(_w(sl, x, -2.6))
    _sztandar(sl, -3.0, -2.6, 0.0, 3.2, 'banner_red')
    if p >= 18:  # kanał z płynnym metalem
        sl.add(box(0.5, 2.6, 0.2, 0.03), 'stone_dark', 'root', mtx((2.85, -0.1, 0.1)))
        sl.add(box(0.3, 2.5, 0.03, 0.0), 'molten', 'root', mtx((2.85, -0.1, 0.21)))
        sl.add(box(1.0, 0.8, 0.3, 0.03), 'stone_dark', 'root', mtx((2.85, -1.7, 0.15)))
        sl.add(box(0.8, 0.6, 0.03, 0.0), 'molten', 'root', mtx((2.85, -1.7, 0.31)))
    if p >= 19:  # złoty młot-godło i posąg kowala
        sl.add(box(0.25, 0.08, 1.0, 0.02), 'gold', 'root', mtx((cx, cy - d / 2 - 0.12, 3.05), (0, 35, 0)))
        sl.add(box(0.6, 0.1, 0.32, 0.03), 'gold', 'root', mtx((cx + 0.25, cy - d / 2 - 0.12, 3.4), (0, 35, 0)))
        _posag_postaci(_w(sl, -2.6, -2.5), 'rycerz')


# ================================================================== KOSZARY

ZMIANY_KOSZARY = {
    1: 'namiot i ognisko', 2: 'drugi namiot i stojak z bronią', 3: 'manekin treningowy',
    4: 'drewniany płotek placu ćwiczeń', 5: 'tarcza strzelnicza',
    6: 'długi budynek z bali', 7: 'maszt z flagą i ławka', 8: 'piętro z muru pruskiego',
    9: 'trzy manekiny i worki z piaskiem', 10: 'drewniana strażnica przy budynku',
    11: 'kamienne koszary z piętrem', 12: 'piaszczysta arena ćwiczeń otoczona kamieniami', 13: 'rząd tarcz-herbów na fasadzie',
    14: 'zbrojownia z bronią pod zadaszeniem', 15: 'dach z niebieskiej dachówki i sztandary',
    16: 'okazałe koszary z blankami i wieżyczkami', 17: 'posąg wojownika', 18: 'złote herby i czerwone sztandary',
    19: 'brukowany plac musztry z koszami ognia', 20: 'wysoka wieża z wielkim sztandarem i złotą iglicą',
}


def koszary(sl, p):
    rng = random.Random(3000 + p)
    if p <= 5:
        _namiot(_w(sl, -1.3, 1.6, 0, 90), 2.6, 2.4, 1.9)
        _ognisko(_w(sl, 0.4, -0.4))
        for sx in (-0.6, 1.4):  # pieńki do siedzenia
            sl.add(cyl(0.2, 0.2, 0.4, 8), 'log', 'root', mtx((sx, -0.2 + abs(sx) * 0.2, 0.2)))
        if p >= 2:
            _namiot(_w(sl, 1.7, 1.8, 0, 90), 2.2, 2.2, 1.7, 'canvas_red')
            _stojak_broni(_w(sl, 2.9, -0.4, 0, 90))
        if p >= 3:
            _manekin(_w(sl, -1.6, -2.0))
        if p >= 4:
            _plotek(sl, (-3.2, -0.9), (-3.2, -3.2))
            _plotek(sl, (-3.2, -3.2), (-0.8, -3.2))
            _plotek(sl, (0.8, -3.2), (3.2, -3.2))
        if p >= 5:
            _tarcza(_w(sl, 2.3, -2.3, 0, -20))
        return
    if p <= 10:
        cx, cy, w, d = 0.0, 1.9, 6.0, 2.6
        z0 = 0.0
        _bale(sl, cx, cy, w, d, 0.0, 2.3, r=0.15)
        top = 2.3
        if p >= 8:
            _szachulec(sl, cx, cy, w + 0.1, d + 0.1, top, 1.8)
            for sx in (-2.0, 0.0, 2.0):
                _okno(sl, sx, cy - d / 2 - 0.1, top + 0.9, 0.55, 0.7)
            top += 1.8
        _dach2(sl, cx, cy, top, w, d, 1.4, ov=0.4, rzedy=4, szczyt='plaster' if p >= 8 else 'log')
        _drzwi(sl, cx, cy - d / 2 - 0.15, 0.0, 1.1, 1.9)
        for sx in (-2.0, 2.0):
            _okno(sl, sx, cy - d / 2 - 0.15, 1.3, 0.6, 0.6, okiennice=True)
        _stojak_broni(_w(sl, 2.9, -0.3, 0, 90))
        _manekin(_w(sl, -1.5, -1.6))
        _plotek(sl, (-3.2, -0.6), (-3.2, -3.2))
        _plotek(sl, (-3.2, -3.2), (-0.8, -3.2))
        _plotek(sl, (0.8, -3.2), (3.2, -3.2))
        _tarcza(_w(sl, 2.3, -2.4, 0, -20))
        if p >= 7:
            sl.add(cyl(0.06, 0.06, 5.0, 6), 'wood_dark', 'root', mtx((-2.6, -0.4, 2.5)))
            sl.add(box(1.1, 0.04, 0.7, 0.0), 'banner', 'root', mtx((-2.03, -0.4, 4.55)))
            sl.add(box(1.4, 0.4, 0.08, 0.02), 'wood', 'root', mtx((0.3, 0.2, 0.45)))
            for sx in (-0.5, 0.5):
                sl.add(box(0.08, 0.36, 0.42, 0.01), 'wood_dark', 'root', mtx((0.3 + sx, 0.2, 0.21)))
        if p >= 9:
            for x in (-0.5, 0.6):
                _manekin(_w(sl, x, -2.0))
            for i in range(5):
                sl.add(sphere(0.28, 0.22, 0.18, u=10, v=6), 'canvas', 'root', mtx((-2.8 + i * 0.0, -0.9 - i * 0.42, 0.16)))
        if p >= 10:  # strażnica
            tx, ty = 3.0, 2.8
            for ox in (-0.5, 0.5):
                for oy in (-0.5, 0.5):
                    sl.add(cyl(0.09, 0.09, 4.6, 6), 'wood_dark', 'root', mtx((tx + ox, ty + oy, 2.3)))
            sl.add(box(1.5, 1.5, 0.12, 0.02), 'wood', 'root', mtx((tx, ty, 4.4)))
            for (ox, oy, ww, dd) in ((0, -0.72, 1.5, 0.06), (0, 0.72, 1.5, 0.06), (-0.72, 0, 0.06, 1.5), (0.72, 0, 0.06, 1.5)):
                sl.add(box(ww, dd, 0.55, 0.01), 'wood', 'root', mtx((tx + ox, ty + oy, 4.7)))
            _dach(sl, tx, ty, 5.4, 1.2, 1.0, GONT, boki=4, rzedy=2, obrot=45, iglica=False)
            for ox in (-0.62, 0.62):
                for oy in (-0.62, 0.62):
                    sl.add(cyl(0.04, 0.04, 1.0, 6), 'wood_dark', 'root', mtx((tx + ox, ty + oy, 4.9)))
        return
    if p <= 15:
        cx, cy, w, d = 0.0, 1.8, 6.0, 2.8
        _bloki_prost(sl, rng, cx, cy, w, d, 0.0, 2.6)
        _szachulec(sl, cx, cy, w + 0.1, d + 0.1, 2.6, 1.8)
        for sx in (-2.0, 0.0, 2.0):
            _okno(sl, sx, cy - d / 2 - 0.1, 3.5, 0.55, 0.75)
        dachy = DACHOWKI if p >= 15 else GONT
        _dach2(sl, cx, cy, 4.4, w + 0.1, d + 0.1, 1.6, mats=dachy, ov=0.4, rzedy=4, szczyt='plaster')
        _drzwi(sl, cx, cy - d / 2 - 0.25, 0.0, 1.2, 2.0, luk=True)
        for sx in (-2.0, 2.0):
            _okno(sl, sx, cy - d / 2 - 0.25, 1.3, 0.6, 0.8, luk=True, rama='stone_light')
        if p >= 12:  # arena
            sl.add(cyl(1.9, 1.9, 0.05, 24), 'sand', 'root', mtx((-0.6, -1.5, 0.05)))
            for i in range(16):
                a = 2 * math.pi * i / 16
                sl.add(rock(0.32, 0.26, 0.22, 900 + i), 'stone', 'root', mtx((-0.6 + math.cos(a) * 1.95, -1.5 + math.sin(a) * 1.95, 0.1)))
            _manekin(_w(sl, -0.6, -1.5))
        else:
            _manekin(_w(sl, -1.0, -1.6))
            _manekin(_w(sl, 0.2, -2.0))
        _tarcza(_w(sl, 2.5, -2.5, 0, -20))
        if p >= 13:
            for sx in (-2.4, -0.8, 0.8, 2.4):
                _herb(sl, sx, cy - d / 2 - 0.2, 2.25, 'banner' if sx < 0 else 'banner_red', s=0.55)
        if p >= 14:  # zbrojownia
            sl.add(box(0.2, 0.2, 2.2, 0.02), 'beam', 'root', mtx((3.25, -1.0, 1.1)))
            sl.add(box(1.6, 2.4, 0.1, 0.02), 'shingle', 'root', mtx((3.1, 0.0, 2.25), (0, -10, 0)))
            _stojak_broni(_w(sl, 3.0, 0.1, 0, 90))
            _zbroja(_w(sl, 2.6, -1.2))
        else:
            _stojak_broni(_w(sl, 2.9, -0.2, 0, 90))
        if p >= 15:
            for sx in (-3.2, 3.2):
                _sztandar(sl, sx, -0.2, 0.0, 3.0)
        return
    # 16–20 okazałe koszary
    cx, cy, w, d = 0.0, 1.8, 6.2, 2.9
    H = 4.4
    _bloki_prost(sl, rng, cx, cy, w, d, 0.0, H, mats=('stone', 'stone_light', 'stone'))
    sl.add(box(w + 0.3, d + 0.3, 0.2, 0.03), 'gold' if p >= 18 else 'stone_light', 'root', mtx((cx, cy, 2.2)))
    sl.add(box(w + 0.4, d + 0.4, 0.25, 0.03), 'stone_light', 'root', mtx((cx, cy, H + 0.12)))
    x = -w / 2 + 0.2
    while x < w / 2:  # blanki
        sl.add(box(0.5, 0.4, 0.55, 0.04), 'stone', 'root', mtx((x, cy - d / 2 - 0.05, H + 0.5)))
        sl.add(box(0.5, 0.4, 0.55, 0.04), 'stone', 'root', mtx((x, cy + d / 2 + 0.05, H + 0.5)))
        x += 0.9
    _dach2(sl, cx, cy, H + 0.2, w - 0.6, d - 0.6, 1.3, mats=DACHOWKI, ov=0.1, rzedy=3, szczyt='stone_light')
    for sx in (-1, 1):  # wieżyczki na narożnikach
        tx = sx * (w / 2 + 0.2)
        _wieza(sl, random.Random(160 + sx), 0.75, 0.7, 0.0, H + 1.2, cx=tx, cy=cy - d / 2 + 0.2, wys_rzedu=0.55)
        _dach(sl, tx, cy - d / 2 + 0.2, H + 1.2, 0.95, 1.5, boki=12, rzedy=4, iglica=p >= 18)
    szklo = 'glass_lit' if p >= 20 else 'glass'
    for z in (1.2, 3.3):
        for sx in (-1.9, 1.9):
            _okno(sl, sx, cy - d / 2 - 0.25, z, 0.6, 0.9, szklo=szklo, rama='gold' if p >= 18 else 'stone_light', luk=True)
    _drzwi(sl, cx, cy - d / 2 - 0.25, 0.0, 1.3, 2.1, luk=True)
    for sx in (-2.6, -0.9, 0.9, 2.6):
        _herb(sl, sx, cy - d / 2 - 0.2, 2.75, 'banner_red' if p >= 18 else 'banner', s=0.5)
    if p >= 19:  # brukowany plac i kosze ognia
        sl.add(box(6.6, 3.0, 0.06, 0.01), 'paving', 'root', mtx((0, -1.8, 0.05)))
        for sx in (-1.2, 1.2):
            _kosz_ognia(sl, sx, -0.6, 0.0)
    sl.add(cyl(1.6, 1.6, 0.06, 22), 'sand', 'root', mtx((-0.8, -1.9, 0.09)))
    _manekin(_w(sl, -0.8, -1.9))
    _tarcza(_w(sl, 2.5, -2.6, 0, -20))
    _stojak_broni(_w(sl, 3.1, -0.9, 0, 90))
    if p >= 17:
        _posag_postaci(_w(sl, -2.8, -2.4), 'rycerz')
    if p >= 18:
        for sx in (-2.4, 2.4):
            sl.add(box(0.9, 0.05, 2.0, 0.01), 'banner_red', 'root', mtx((sx, cy - d / 2 - 0.3, H - 1.1)))
            sl.add(box(0.3, 0.06, 0.3, 0.01), 'gold', 'root', mtx((sx, cy - d / 2 - 0.33, H - 0.8), (0, 45, 0)))
    if p >= 20:  # wysoka wieża z wielkim sztandarem
        _wieza(sl, random.Random(200), 1.0, 0.9, 0.0, 8.5, cx=0.0, cy=cy + d / 2 + 0.3, wys_rzedu=0.55)
        _dach(sl, 0.0, cy + d / 2 + 0.3, 8.5, 1.2, 2.4, boki=14, rzedy=5)
        sl.add(cyl(0.04, 0.04, 2.0, 6), 'iron', 'root', mtx((0.0, cy + d / 2 + 0.3, 11.6)))
        sl.add(box(1.4, 0.04, 0.8, 0.01), 'banner_red', 'root', mtx((0.72, cy + d / 2 + 0.3, 12.1)))


# ================================================================== BUDYNEK FUZJI

ZMIANY_FUZJA = {
    1: 'krąg kamieni z ołtarzem i małym kryształem', 2: 'drewniany daszek nad ołtarzem', 3: 'świecące runy na kamieniach',
    4: 'dwa kosze z fioletowym ogniem', 5: 'pulpit z księgą przepisów',
    6: 'okrągła sala z kamienną podstawą i stożkowym dachem', 7: 'kryształ na szczycie dachu',
    8: 'świecący krąg run przed wejściem', 9: 'dwa unoszące się kryształy', 10: 'fioletowe sztandary',
    11: 'kamienna rotunda z kolumnadą', 12: 'kopuła', 13: 'dwa świecące obeliski',
    14: 'runiczny łuk-brama przed wejściem', 15: 'kopuła z niebieskiej dachówki i złota iglica',
    16: 'okazała dwupoziomowa świątynia fuzji', 17: 'złote pierścienie krążące wokół kryształu', 18: 'więcej obelisków i złote zdobienia',
    19: 'posągi golema i rycerza (symbol fuzji)', 20: 'wielki unoszący się kryształ i świecące okna',
}


def budynek_fuzji(sl, p):
    rng = random.Random(4000 + p)
    if p <= 5:
        cy = 0.9
        for i in range(7):
            a = math.pi / 2 + 2 * math.pi * i / 7
            if abs(math.cos(a - math.pi * 1.5)) > 0.97:
                continue  # przerwa na wejście z przodu
            _menhir(_w(sl, math.cos(a) * 2.3, cy + math.sin(a) * 2.3, 0, math.degrees(a) + 90), rng.uniform(1.6, 2.2), 70 + i,
                    run=p >= 3)
        sl.add(box(1.2, 0.8, 0.8, 0.05), 'stone_light', 'root', mtx((0, cy, 0.4)))
        sl.add(box(1.35, 0.95, 0.12, 0.03), 'stone', 'root', mtx((0, cy, 0.86)))
        _krysztal(_w(sl, 0, cy, 1.35), 0.8)
        if p >= 2:
            for sx in (-1.0, 1.0):
                for sy in (-0.8, 0.8):
                    sl.add(cyl(0.09, 0.09, 2.4, 6), 'wood_dark', 'root', mtx((sx, cy + sy, 1.2)))
            _dach(sl, 0, cy, 2.4, 1.7, 1.1, GONT, boki=4, rzedy=3, obrot=45, iglica=False)
        if p >= 4:
            for sx in (-1.4, 1.4):
                _kosz_magii(_w(sl, sx, -1.9))
        if p >= 5:
            _pulpit(_w(sl, 0, -1.1))
        return
    if p <= 10:
        cy, r = 1.0, 2.2
        _wieza(sl, random.Random(60), r, r * 0.97, 0.0, 1.0, cy=cy, wys_rzedu=0.5)
        sl.add(cyl(r - 0.05, r - 0.1, 2.0, 18), 'plaster', 'root', mtx((0, cy, 2.0)))
        for i in range(10):
            a = 2 * math.pi * i / 10
            sl.add(box(0.14, 0.1, 2.0, 0.01), 'beam', 'root', mtx((math.cos(a) * (r - 0.05), cy + math.sin(a) * (r - 0.05), 2.0), (0, 0, math.degrees(a) + 90)))
        sl.add(cyl(r + 0.02, r + 0.02, 0.16, 18), 'beam', 'root', mtx((0, cy, 3.0)))
        _dach(sl, 0, cy, 3.0, r + 0.35, 2.4, GONT, boki=16, rzedy=5, iglica=False)
        _drzwi(sl, 0, cy - r - 0.05, 1.0, 1.0, 1.8, luk=True)
        sl.add(box(1.6, 0.9, 1.0, 0.04), 'stone', 'root', mtx((0, cy - r - 0.3, 0.5)))  # schodek
        for a in (-50, 50):
            ar = math.radians(a - 90)
            _okno(_w(sl, math.cos(ar) * (r + 0.02), cy + math.sin(ar) * (r + 0.02), 0, a), 0, 0, 2.1, 0.5, 0.7,
                  szklo='magic_soft', luk=True)
        for sx in (-1.6, 1.6):
            _kosz_magii(_w(sl, sx, -2.3))
        _pulpit(_w(sl, 2.6, -0.8, 0, -30))
        if p >= 7:
            _krysztal(_w(sl, 0, cy, 6.0), 1.2)
        if p >= 8:
            _pierscien(_w(sl, 0, -2.3, 0.07), 1.0, 0.0, 'rune', n=16, grub=0.07)
            for i in range(6):
                a = 2 * math.pi * i / 6
                sl.add(box(0.18, 0.18, 0.02, 0.0), 'magic', 'root', mtx((math.cos(a) * 0.6, -2.3 + math.sin(a) * 0.6, 0.08), (0, 0, 45)))
        if p >= 9:
            for sx in (-2.8, 2.8):
                _krysztal(_w(sl, sx, 1.6, 2.4 + 0.3 * (sx > 0)), 0.9)
        if p >= 10:
            for sx in (-2.7, 2.7):
                _sztandar(sl, sx, -1.2, 0.0, 3.0, 'magic_dark')
        return
    if p <= 15:
        cy, r = 1.0, 2.2
        _wieza(sl, random.Random(110), r, r, 0.0, 3.2, cy=cy, wys_rzedu=0.55, mat=('stone', 'stone_light', 'stone'))
        for i in range(10):  # kolumnada
            a = 2 * math.pi * (i + 0.5) / 10
            x, y = math.cos(a) * (r + 0.75), cy + math.sin(a) * (r + 0.75)
            sl.add(cyl(0.16, 0.16, 3.2, 10), 'stone_light', 'root', mtx((x, y, 1.6)))
            sl.add(box(0.4, 0.4, 0.15, 0.02), 'stone_light', 'root', mtx((x, y, 3.25)))
        sl.add(cyl(r + 1.05, r + 1.05, 0.25, 20), 'stone_light', 'root', mtx((0, cy, 3.4)))
        sl.add(cyl(r + 1.0, r + 1.0, 0.18, 20), 'stone', 'root', mtx((0, cy, 0.09)))
        _drzwi(sl, 0, cy - r - 0.05, 0.18, 1.1, 2.0, luk=True, mat='magic_dark')
        for a in (-55, 55):
            ar = math.radians(a - 90)
            _okno(_w(sl, math.cos(ar) * (r + 0.02), cy + math.sin(ar) * (r + 0.02), 0, a), 0, 0, 1.8, 0.45, 0.8,
                  szklo='magic_soft', rama='stone_light', luk=True)
        if p >= 12:
            mat = 'roof' if p >= 15 else 'stone_light'
            sl.add(sphere(r + 0.2, r + 0.2, 1.9, u=20, v=10), mat, 'root', mtx((0, cy, 3.45)))
            if p >= 15:
                for k in range(3):
                    sl.add(cyl(r + 0.22 - k * 0.55, r + 0.22 - k * 0.55, 0.1, 20), 'roof_dark', 'root', mtx((0, cy, 3.9 + k * 0.5)))
                sl.add(cyl(0.08, 0.0, 1.6, 8), 'gold', 'root', mtx((0, cy, 5.9)))
                sl.add(sphere(0.18, u=10, v=8), 'gold', 'root', mtx((0, cy, 5.3)))
            else:
                _krysztal(_w(sl, 0, cy, 5.8), 1.0)
        else:
            _dach(sl, 0, cy, 3.5, r + 1.1, 1.6, GONT, boki=16, rzedy=4, iglica=False)
            _krysztal(_w(sl, 0, cy, 5.6), 1.0)
        for sx in (-1.4, 1.4):
            _kosz_magii(_w(sl, sx, -2.6))
        if p >= 13:
            for sx in (-2.9, 2.9):
                _menhir(_w(sl, sx, -1.6), 2.6, 130 + int(sx), 'stone_dark', run=True)
                _krysztal(_w(sl, sx, -1.6, 2.95), 0.5)
        if p >= 14:  # łuk-brama
            for sx in (-1.0, 1.0):
                sl.add(box(0.35, 0.35, 2.4, 0.04), 'stone_light', 'root', mtx((sx, -3.0, 1.2)))
                sl.add(box(0.2, 0.05, 0.2, 0.0), 'rune', 'root', mtx((sx, -3.19, 1.5), (0, 45, 0)))
            sl.add(cyl(1.0, 1.0, 0.3, 14), 'stone_light', 'root', mtx((0, -3.0, 2.4), (90, 0, 0)))
            sl.add(box(0.3, 0.05, 0.3, 0.0), 'magic', 'root', mtx((0, -3.17, 3.1), (0, 45, 0)))
        return
    # 16–20 okazała świątynia fuzji
    cy, r = 1.0, 2.2
    _wieza(sl, random.Random(160), r, r, 0.0, 3.4, cy=cy, wys_rzedu=0.55, mat=('stone', 'stone_light', 'stone'))
    for i in range(10):
        a = 2 * math.pi * (i + 0.5) / 10
        x, y = math.cos(a) * (r + 0.75), cy + math.sin(a) * (r + 0.75)
        sl.add(cyl(0.16, 0.16, 3.4, 10), 'stone_light', 'root', mtx((x, y, 1.7)))
        sl.add(box(0.4, 0.4, 0.15, 0.02), 'gold' if p >= 18 else 'stone_light', 'root', mtx((x, y, 3.45)))
    sl.add(cyl(r + 1.05, r + 1.05, 0.25, 20), 'stone_light', 'root', mtx((0, cy, 3.6)))
    sl.add(cyl(r + 1.0, r + 1.0, 0.18, 20), 'stone', 'root', mtx((0, cy, 0.09)))
    if p >= 18:
        _pierscien(_w(sl, 0, cy, 3.75), r + 1.02, 0.0, 'gold', n=28, grub=0.12)
    _wieza(sl, random.Random(161), 1.5, 1.4, 3.7, 6.0, cy=cy, wys_rzedu=0.5, mat=('stone_light', 'stone', 'stone_light'))
    sl.add(sphere(1.6, 1.6, 1.4, u=20, v=10), 'roof', 'root', mtx((0, cy, 6.0)))
    for k in range(3):
        sl.add(cyl(1.62 - k * 0.42, 1.62 - k * 0.42, 0.1, 20), 'roof_dark', 'root', mtx((0, cy, 6.35 + k * 0.38)))
    szklo = 'glass_lit' if p >= 20 else 'magic_soft'
    rama = 'gold' if p >= 18 else 'stone_light'
    _drzwi(sl, 0, cy - r - 0.05, 0.18, 1.1, 2.1, luk=True, mat='magic_dark')
    for a in (-55, 55):
        ar = math.radians(a - 90)
        _okno(_w(sl, math.cos(ar) * (r + 0.02), cy + math.sin(ar) * (r + 0.02), 0, a), 0, 0, 1.8, 0.45, 0.85,
              szklo=szklo, rama=rama, luk=True)
    for a in (-35, 0, 35):
        ar = math.radians(a - 90)
        _okno(_w(sl, math.cos(ar) * 1.52, cy + math.sin(ar) * 1.52, 0, a), 0, 0, 4.9, 0.35, 0.65, szklo=szklo, rama=rama, luk=True)
    # kryształ na szczycie (od 20 – wielki i unoszący się)
    kz = 8.4 if p < 20 else 9.0
    _krysztal(_w(sl, 0, cy, kz), 1.2 if p < 20 else 2.0)
    if p >= 17:
        for k, (rr, kat) in enumerate(((0.9, 0), (1.15, 35))):
            _pierscien(_T(sl, mtx((0, cy, kz), (kat, k * 40, 0))), rr, 0.0, 'gold', n=22, grub=0.07)
    for sx in (-1.4, 1.4):
        _kosz_magii(_w(sl, sx, -2.6))
    for sx in (-2.9, 2.9):
        _menhir(_w(sl, sx, -1.6), 2.6, 160 + int(sx), 'stone_dark', run=True)
        _krysztal(_w(sl, sx, -1.6, 2.95), 0.5)
    if p >= 18:
        for sx in (-2.9, 2.9):
            _menhir(_w(sl, sx, 2.9), 2.2, 180 + int(sx), 'stone_dark', run=True)
            _krysztal(_w(sl, sx, 2.9, 2.55), 0.45)
    for sx in (-1.0, 1.0):  # łuk-brama
        sl.add(box(0.35, 0.35, 2.4, 0.04), 'stone_light', 'root', mtx((sx, -3.0, 1.2)))
        sl.add(box(0.2, 0.05, 0.2, 0.0), 'rune', 'root', mtx((sx, -3.19, 1.5), (0, 45, 0)))
    sl.add(cyl(1.0, 1.0, 0.3, 14), 'gold' if p >= 18 else 'stone_light', 'root', mtx((0, -3.0, 2.4), (90, 0, 0)))
    sl.add(box(0.3, 0.05, 0.3, 0.0), 'magic', 'root', mtx((0, -3.17, 3.1), (0, 45, 0)))
    if p >= 19:
        _posag_postaci(_w(sl, -2.5, -0.3, 0, 20), 'golem')
        _posag_postaci(_w(sl, 2.5, -0.3, 0, -20), 'rycerz')


# ================================================================== TABLICA OGŁOSZEŃ

def tablica_ogloszen(sl):
    """Tablica ogłoszeń przy studni (aktualizacje, wydarzenia). Przód = -Y. Pusty węzeł 'tablica_info'
    wskazuje środek tablicy (np. dymek „!” przy nowej aktualizacji)."""
    for sx in (-0.95, 0.95):
        sl.add(box(0.16, 0.16, 2.3, 0.02), 'wood_dark', 'root', mtx((sx, 0, 1.15)))
        sl.add(rock(0.4, 0.4, 0.2, 500 + int(sx * 10)), 'stone', 'root', mtx((sx, 0, 0.08)))
    sl.add(box(1.85, 0.1, 1.15, 0.03), 'wood', 'root', mtx((0, 0, 1.45)))
    sl.add(box(2.05, 0.14, 0.1, 0.02), 'wood_dark', 'root', mtx((0, -0.02, 2.06)))
    sl.add(box(2.05, 0.14, 0.1, 0.02), 'wood_dark', 'root', mtx((0, -0.02, 0.85)))
    sl.add(box(2.5, 0.9, 0.08, 0.02), 'shingle', 'root', mtx((0, -0.1, 2.42), (-14, 0, 0)))
    sl.add(box(2.5, 0.08, 0.14, 0.02), 'shingle_dark', 'root', mtx((0, 0.32, 2.5)))
    kartki = [(-0.55, 1.62, 0.42, 0.5, 'paper', 4), (0.0, 1.55, 0.38, 0.62, 'paper_y', -3), (0.52, 1.67, 0.4, 0.45, 'paper', 6),
              (-0.35, 1.1, 0.5, 0.32, 'paper_y', -5), (0.4, 1.12, 0.36, 0.34, 'paper', 2)]
    for x, z, w, h, m, kat in kartki:
        sl.add(box(w, 0.02, h, 0.0), m, 'root', mtx((x, -0.07, z), (0, kat, 0)))
        sl.add(sphere(0.03, u=6, v=4), 'banner_red', 'root', mtx((x, -0.09, z + h / 2 - 0.05)))
        for k in range(3):  # linijki tekstu
            sl.add(box(w * 0.7, 0.01, 0.025, 0.0), 'wood_dark', 'root', mtx((x, -0.085, z + h * 0.2 - k * h * 0.17), (0, kat, 0)))
    sl.add(box(0.5, 0.05, 0.3, 0.01), 'banner', 'root', mtx((0, -0.08, 2.0)))  # szyld „Ogłoszenia”
    sl.add(box(0.14, 0.04, 0.14, 0.0), 'gold', 'root', mtx((0, -0.11, 2.0), (0, 45, 0)))
    _latarnia(sl, 1.25, -0.25, 0.0, 1.7)
    return [('tablica_info', (0.0, -0.3, 1.45))]


# ================================================================== MAGAZYN

ZMIANY_MAGAZYN = {
    1: 'wiata ze skrzyniami i workami', 2: 'mała szopa z bali', 3: 'stos beczek', 4: 'wózek z towarem',
    5: 'ogrodzony plac składowy z kolejnymi skrzyniami',
    6: 'duża drewniana stodoła z podwójnymi wrotami', 7: 'belka z bloczkiem i workiem na strych',
    8: 'przybudówka ze stosami drewna', 9: 'skrzynia ze złotem przy wrotach i latarnia', 10: 'drzwi strychu i wiatrowskaz',
    11: 'kamienny magazyn z łukowymi wrotami', 12: 'rampa załadunkowa ze skrzyniami', 13: 'dźwig z ładunkiem',
    14: 'okuty skarbczyk i budka strażnika', 15: 'dach z niebieskiej dachówki i sztandary',
    16: 'okazały magazyn z dwiema wieżyczkami', 17: 'stosy złotych monet i skrzynie na placu', 18: 'złote zdobienia i herb z monetą',
    19: 'kryty wóz kupiecki z towarem', 20: 'złota kopuła skarbca ze świecącą monetą',
}


def _skrzynia(sl, s=1.0, zloto=False):
    sl.add(box(0.7 * s, 0.6 * s, 0.55 * s, 0.03), 'wood', 'root', mtx((0, 0, 0.275 * s)))
    for x in (-0.33 * s, 0.33 * s):
        sl.add(box(0.06, 0.62 * s, 0.57 * s, 0.0), 'wood_dark' if not zloto else 'iron', 'root', mtx((x, 0, 0.275 * s)))
    if zloto:
        sl.add(box(0.6 * s, 0.5 * s, 0.08, 0.0), 'gold', 'root', mtx((0, 0, 0.58 * s)))
        for i in range(5):
            sl.add(cyl(0.07, 0.07, 0.03, 8), 'gold', 'root', mtx((-0.2 + i * 0.1, -0.1 + (i % 2) * 0.15, 0.64 * s), (20 * i, 0, 0)))


def _worek(sl):
    sl.add(sphere(0.28, 0.24, 0.3, u=10, v=8), 'canvas', 'root', mtx((0, 0, 0.28)))
    sl.add(cyl(0.08, 0.05, 0.14, 6), 'rope', 'root', mtx((0, 0, 0.6)))


def _stos_drewna(sl, dl=1.6):
    for k in range(3):
        for i in range(4 - k):
            sl.add(cyl(0.13, 0.13, dl, 8), 'log' if (i + k) % 2 else 'log_dark', 'root', mtx((0, -0.38 + i * 0.26 + k * 0.13, 0.13 + k * 0.23), (0, 90, 0)))


def _monety(sl, n=7, rng=None):
    rng = rng or random.Random(7)
    sl.add(cyl(0.45, 0.1, 0.4, 12), 'gold', 'root', mtx((0, 0, 0.2)))
    for _ in range(n):
        sl.add(cyl(0.08, 0.08, 0.03, 8), 'gold', 'root', mtx((rng.uniform(-0.6, 0.6), rng.uniform(-0.6, 0.6), 0.03), (rng.uniform(0, 40), 0, 0)))


def _woz(sl, kryty=True):
    sl.add(box(2.0, 1.1, 0.15, 0.02), 'wood', 'root', mtx((0, 0, 0.75)))
    for y in (-0.55, 0.55):
        sl.add(box(2.0, 0.08, 0.35, 0.01), 'wood_dark', 'root', mtx((0, y, 1.0)))
    for x in (-0.65, 0.65):
        for y in (-0.62, 0.62):
            sl.add(cyl(0.38, 0.38, 0.1, 12), 'wood_dark', 'root', mtx((x, y, 0.38), (90, 0, 0)))
            sl.add(cyl(0.1, 0.1, 0.14, 8), 'iron', 'root', mtx((x, y, 0.38), (90, 0, 0)))
    sl.add(cyl(0.04, 0.04, 1.4, 6), 'wood_dark', 'root', mtx((-1.6, 0, 0.6), (0, 75, 0)))
    if kryty:
        sl.add(sphere(1.0, 0.62, 0.7, u=12, v=8), 'canvas', 'root', mtx((0.05, 0, 0.95)) @ scale_m(1, 1, 1))
        sl.add(box(2.1, 1.3, 0.12, 0.0), 'wood', 'root', mtx((0.05, 0, 0.83)))
    _skrzynia(_w(sl, -0.75, 0, 0.82), 0.5)


def magazyn(sl, p):
    rng = random.Random(5000 + p)
    if p <= 5:
        for sx in (-1.6, 1.6):
            for sy in (-0.2, 1.8):
                sl.add(cyl(0.09, 0.09, 2.3, 6), 'wood_dark', 'root', mtx((sx, sy, 1.15)))
        sl.add(box(3.8, 2.6, 0.06, 0.0), 'canvas', 'root', mtx((0, 0.8, 2.35), (-6, 0, 0)))
        for (x, y, s) in ((-1.0, 1.4, 1.0), (-0.2, 1.5, 0.8), (-0.9, 1.4, 0.0)):
            _skrzynia(_w(sl, x, y, 0.55 if s == 0.0 else 0.0), s or 0.75)
        for x in (0.7, 1.2):
            _worek(_w(sl, x, 1.2))
        if p >= 2:
            _bale(sl, 0.0, 2.7, 3.4, 1.0, 0.0, 1.8, r=0.13)
            _dach2(sl, 0.0, 2.7, 1.8, 3.4, 1.0, 0.6, ov=0.3, rzedy=2, szczyt='log')
        if p >= 3:
            for i, (x, y, z) in enumerate(((2.4, -0.6, 0), (2.4, 0.05, 0), (2.4, -0.28, 0.75))):
                _beczka(_w(sl, x, y, z))
        if p >= 4:
            _woz(_w(sl, -1.6, -1.9, 0, 20), kryty=False)
        if p >= 5:
            _plotek(sl, (-3.2, -3.2), (-0.9, -3.2))
            _plotek(sl, (0.9, -3.2), (3.2, -3.2))
            _plotek(sl, (3.2, -3.2), (3.2, 1.0))
            for (x, y) in ((1.4, -2.4), (2.2, -2.5)):
                _skrzynia(_w(sl, x, y, 0, 15), 0.8)
        return
    if p <= 10:
        cx, cy, w, d = 0.0, 1.5, 4.8, 3.4
        sl.add(box(w + 0.2, d + 0.2, 0.3, 0.03), 'stone_dark', 'root', mtx((cx, cy, 0.15)))
        _bale(sl, cx, cy, w, d, 0.3, 2.8, r=0.16)
        _dach2(sl, cx, cy, 3.1, w, d, 2.0, ov=0.4, rzedy=5, szczyt='wood')
        for sx in (-0.65, 0.65):  # podwójne wrota
            sl.add(box(1.25, 0.12, 2.3, 0.03), 'wood', 'root', mtx((sx, cy - d / 2 - 0.12, 1.45)))
            sl.add(cyl(0.04, 0.04, 1.6, 4), 'wood_dark', 'root', seg(V(sx - 0.55, cy - d / 2 - 0.2, 0.5), V(sx + 0.55, cy - d / 2 - 0.2, 2.4)))
        sl.add(box(2.7, 0.15, 0.2, 0.02), 'wood_dark', 'root', mtx((0, cy - d / 2 - 0.15, 2.7)))
        for (x, y, s) in ((-2.4, -0.8, 0.8), (-1.7, -1.4, 0.7), (2.2, -1.0, 0.8)):
            _skrzynia(_w(sl, x, y, 0, rng.uniform(-20, 20)), s)
        _worek(_w(sl, 1.6, -0.5))
        _worek(_w(sl, 1.9, -0.2))
        if p >= 7:
            sl.add(box(0.15, 1.2, 0.15, 0.02), 'beam', 'root', mtx((0, cy - d / 2 - 0.5, 4.45)))
            sl.add(cyl(0.12, 0.12, 0.08, 10), 'wood_dark', 'root', mtx((0, cy - d / 2 - 1.0, 4.3), (0, 90, 0)))
            sl.add(cyl(0.015, 0.015, 1.5, 4), 'rope', 'root', mtx((0, cy - d / 2 - 1.05, 3.5)))
            _worek(_w(sl, 0, cy - d / 2 - 1.05, 2.25))
        if p >= 8:
            sl.add(box(1.4, 3.0, 0.08, 0.0), 'shingle', 'root', mtx((-3.1, cy, 2.0), (0, 14, 0)))
            for sy in (-1.3, 1.3):
                sl.add(cyl(0.07, 0.07, 1.9, 6), 'wood_dark', 'root', mtx((-3.6, cy + sy, 0.95)))
            _stos_drewna(_w(sl, -3.0, cy, 0, 90), 2.6)
        if p >= 9:
            _skrzynia(_w(sl, 1.6, -1.8, 0, -15), 0.8, zloto=True)
            _latarnia(sl, -1.5, -0.2, 0.0, 1.9)
        if p >= 10:
            sl.add(box(0.9, 0.1, 0.9, 0.02), 'wood_dark', 'root', mtx((0, cy - d / 2 - 0.15, 3.9)))
            sl.add(cyl(0.03, 0.03, 0.9, 4), 'iron', 'root', mtx((1.6, cy, 5.5)))
            sl.add(box(0.5, 0.03, 0.25, 0.0), 'iron', 'root', mtx((1.75, cy, 5.85)))
            sl.add(cyl(0.05, 0.0, 0.2, 4), 'gold', 'root', mtx((1.6, cy, 6.05)))
        return
    if p <= 15:
        cx, cy, w, d = 0.0, 1.6, 5.2, 3.2
        _bloki_prost(sl, rng, cx, cy, w, d, 0.0, 3.2, otwor=(2.0, 2.3))
        sl.add(cyl(1.0, 1.0, 0.3, 14), 'stone_light', 'root', mtx((cx, cy - d / 2 - 0.05, 2.3), (90, 0, 0)))
        for sx in (-0.48, 0.48):
            sl.add(box(0.94, 0.12, 2.3, 0.02), 'wood', 'root', mtx((sx, cy - d / 2 + 0.15, 1.15)))
        dachy = DACHOWKI if p >= 15 else GONT
        _dach2(sl, cx, cy, 3.2, w, d, 1.9, mats=dachy, ov=0.4, rzedy=5, szczyt='stone_light')
        for sx in (-1.9, 1.9):
            _okno(sl, sx, cy - d / 2 - 0.1, 2.2, 0.5, 0.6, okiennice=True)
        for (x, y, s) in ((-2.5, -1.0, 0.8), (-2.2, -1.7, 0.7)):
            _skrzynia(_w(sl, x, y, 0, rng.uniform(-20, 20)), s)
        if p >= 12:  # rampa
            sl.add(box(2.0, 1.4, 0.6, 0.03), 'stone', 'root', mtx((2.0, -0.6, 0.3)))
            sl.add(box(2.1, 1.5, 0.08, 0.01), 'wood', 'root', mtx((2.0, -0.6, 0.64)))
            for x in (1.5, 2.3):
                _skrzynia(_w(sl, x, -0.6, 0.68), 0.6)
            _worek(_w(sl, 2.6, -0.3, 0.68))
        if p >= 13:  # dźwig
            sl.add(box(0.22, 0.22, 4.2, 0.02), 'beam', 'root', mtx((-3.0, 0.2, 2.1)))
            sl.add(box(0.2, 2.2, 0.2, 0.02), 'beam', 'root', mtx((-3.0, -0.7, 4.1)))
            sl.add(cyl(0.05, 0.05, 1.3, 6), 'beam', 'root', seg(V(-3.0, 0.2, 3.1), V(-3.0, -0.6, 4.05)))
            sl.add(cyl(0.02, 0.02, 1.8, 4), 'rope', 'root', mtx((-3.0, -1.7, 3.15)))
            _skrzynia(_w(sl, -3.0, -1.7, 1.9), 0.7)
        if p >= 14:  # skarbczyk i budka strażnika
            _skrzynia(_w(sl, 0.9, -2.4, 0, 10), 0.9, zloto=True)
            for ox in (-0.5, 0.5):
                for oy in (-0.5, 0.5):
                    sl.add(cyl(0.07, 0.07, 2.2, 6), 'wood_dark', 'root', mtx((2.7 + ox, -2.5 + oy, 1.1)))
            _dach(sl, 2.7, -2.5, 2.2, 0.9, 0.8, GONT, boki=4, rzedy=2, obrot=45, iglica=False)
        if p >= 15:
            for sx in (-1.4, 1.4):
                _sztandar(sl, sx, cy - d / 2 - 0.35, 0.0, 2.9)
        return
    # 16–20 okazały magazyn
    cx, cy, w, d = 0.0, 1.6, 5.0, 3.2
    _bloki_prost(sl, rng, cx, cy, w, d, 0.0, 3.6, mats=('stone', 'stone_light', 'stone'), otwor=(2.0, 2.4))
    sl.add(cyl(1.0, 1.0, 0.32, 14), 'gold' if p >= 18 else 'stone_light', 'root', mtx((cx, cy - d / 2 - 0.05, 2.4), (90, 0, 0)))
    for sx in (-0.48, 0.48):
        sl.add(box(0.94, 0.12, 2.4, 0.02), 'wood', 'root', mtx((sx, cy - d / 2 + 0.15, 1.2)))
        for z in (0.5, 1.2, 1.9):
            sl.add(box(0.94, 0.06, 0.1, 0.0), 'iron', 'root', mtx((sx, cy - d / 2 + 0.07, z)))
    _dach2(sl, cx, cy, 3.6, w, d, 1.9, mats=DACHOWKI, ov=0.4, rzedy=5, szczyt='stone_light')
    for sx in (-1, 1):  # wieżyczki
        tx = sx * (w / 2 + 0.3)
        _wieza(sl, random.Random(170 + sx), 0.7, 0.65, 0.0, 4.8, cx=tx, cy=cy - d / 2 + 0.3, wys_rzedu=0.5, mat=('stone', 'stone_light', 'stone'))
        _dach(sl, tx, cy - d / 2 + 0.3, 4.8, 0.9, 1.5, boki=12, rzedy=4, iglica=p >= 18)
    if p >= 18:
        _herb(sl, cx, cy - d / 2 - 0.15, 3.2, 'banner', s=0.6)
        sl.add(cyl(0.16, 0.16, 0.05, 12), 'gold', 'root', mtx((cx, cy - d / 2 - 0.22, 3.2), (90, 0, 0)))
    _skrzynia(_w(sl, 0.9, -2.4, 0, 10), 0.9, zloto=True)
    sl.add(box(2.0, 1.4, 0.6, 0.03), 'stone', 'root', mtx((2.2, -0.4, 0.3)))
    sl.add(box(2.1, 1.5, 0.08, 0.01), 'wood', 'root', mtx((2.2, -0.4, 0.64)))
    _skrzynia(_w(sl, 1.8, -0.4, 0.68), 0.6)
    _skrzynia(_w(sl, 2.6, -0.4, 0.68), 0.6, zloto=True)
    if p >= 17:
        _monety(_w(sl, -1.0, -2.2), 9, rng)
        _skrzynia(_w(sl, -2.0, -1.6, 0, -20), 0.85, zloto=True)
    if p >= 19:
        _woz(_w(sl, -2.0, -0.1, 0, 90))
    if p >= 20:  # złota kopuła skarbca
        sl.add(cyl(0.9, 0.9, 0.7, 14), 'stone_light', 'root', mtx((cx, cy + 0.2, 5.4)))
        sl.add(sphere(0.95, 0.95, 0.85, u=16, v=8), 'gold', 'root', mtx((cx, cy + 0.2, 5.75)))
        sl.add(cyl(0.3, 0.3, 0.06, 14), 'glass_lit', 'root', mtx((cx, cy + 0.2, 7.0), (90, 0, 0)))
        sl.add(cyl(0.22, 0.22, 0.07, 14), 'lamp', 'root', mtx((cx, cy + 0.2, 7.0), (90, 0, 0)))


# ================================================================== AKADEMIA (badania)

ZMIANY_AKADEMIA = {
    1: 'chatka uczonego ze stołem i zwojami', 2: 'regał ze zwojami i latarnia', 3: 'luneta na trójnogu',
    4: 'ogródek z ziołami', 5: 'globus na stojaku',
    6: 'dom nauki z muru pruskiego z dużymi oknami', 7: 'przybudówka biblioteki', 8: 'taras obserwacyjny z lunetą na dachu',
    9: 'stół alchemiczny z kolorowymi kolbami', 10: 'tablica z zapiskami, sztandary i latarnie',
    11: 'kamienna akademia z łukowymi oknami', 12: 'wieżyczka obserwatorium z kopułą', 13: 'złota sfera armilarna na placu',
    14: 'posąg uczonego z księgą', 15: 'dach z niebieskiej dachówki i sztandary',
    16: 'okazała akademia z portykiem i kolumnami', 17: 'duże obserwatorium z wielkim teleskopem', 18: 'złote zdobienia i świecące runiczne okna',
    19: 'unoszące się księgi i magiczne kule', 20: 'gwiezdny kryształ nad kopułą',
}


def _stol(sl, rzeczy='zwoje'):
    sl.add(box(1.2, 0.6, 0.06, 0.01), 'wood', 'root', mtx((0, 0, 0.78)))
    for x in (-0.5, 0.5):
        for y in (-0.22, 0.22):
            sl.add(box(0.06, 0.06, 0.75, 0.0), 'wood_dark', 'root', mtx((x, y, 0.375)))
    if rzeczy == 'zwoje':
        for i in range(3):
            sl.add(cyl(0.05, 0.05, 0.4, 8), 'paper', 'root', mtx((-0.3 + i * 0.25, 0.05, 0.86), (0, 90, i * 20)))
        sl.add(box(0.35, 0.25, 0.02, 0.0), 'paper_y', 'root', mtx((0.3, -0.08, 0.82), (0, 0, 10)))
    else:  # kolby alchemiczne
        for i, m in enumerate(('magic', 'rune', 'molten', 'leaves')):
            x = -0.42 + i * 0.28
            sl.add(sphere(0.09, u=8, v=6), 'glass', 'root', mtx((x, 0.05, 0.9)))
            sl.add(sphere(0.07, u=8, v=6), m, 'root', mtx((x, 0.05, 0.88)))
            sl.add(cyl(0.025, 0.025, 0.14, 6), 'glass', 'root', mtx((x, 0.05, 1.03)))


def _regal(sl):
    sl.add(box(1.2, 0.4, 1.8, 0.02), 'wood_dark', 'root', mtx((0, 0, 0.9)))
    for k in range(4):
        z = 0.25 + k * 0.45
        sl.add(box(1.1, 0.34, 0.05, 0.0), 'wood', 'root', mtx((0, -0.04, z)))
        for i in range(7):
            m = ('banner', 'banner_red', 'leather', 'magic_dark', 'leaves')[(i + k) % 5]
            sl.add(box(0.11, 0.28, 0.32, 0.0), m, 'root', mtx((-0.45 + i * 0.15, -0.06, z + 0.18)))


def _luneta(sl, s=1.0):
    for a in (0, 120, 240):
        r = math.radians(a)
        sl.add(cyl(0.025 * s, 0.025 * s, 1.3 * s, 4), 'wood_dark', 'root', seg(V(math.cos(r) * 0.4 * s, math.sin(r) * 0.4 * s, 0), V(0, 0, 1.2 * s)))
    sl.add(cyl(0.07 * s, 0.11 * s, 1.0 * s, 10), 'gold', 'root', mtx((0, -0.1 * s, 1.35 * s), (55, 0, 0)))
    sl.add(cyl(0.12 * s, 0.12 * s, 0.05, 10), 'glass', 'root', mtx((0, -0.5 * s, 1.63 * s), (55, 0, 0)))


def _globus(sl):
    sl.add(cyl(0.06, 0.1, 0.9, 8), 'wood_dark', 'root', mtx((0, 0, 0.45)))
    sl.add(sphere(0.3, u=14, v=10), 'water', 'root', mtx((0, 0, 1.2)))
    for (x, y, z) in ((0.1, -0.22, 1.3), (-0.15, -0.2, 1.1), (0.2, 0.1, 1.05)):
        sl.add(sphere(0.12, 0.08, 0.1, u=8, v=6), 'leaves', 'root', mtx((x, y, z)))
    _pierscien(_T(sl, mtx((0, 0, 1.2), (90, 0, 20))), 0.36, 0.0, 'gold', n=16, grub=0.035)


def _sfera(sl, s=1.0):
    sl.add(cyl(0.12 * s, 0.25 * s, 1.0 * s, 10), 'stone_light', 'root', mtx((0, 0, 0.5 * s)))
    for k, (rx, rz) in enumerate(((0, 0), (90, 0), (90, 60), (90, 120), (30, 0))):
        _pierscien(_T(sl, mtx((0, 0, 1.55 * s), (rx, 0, rz))), 0.5 * s, 0.0, 'gold', n=20, grub=0.05)
    sl.add(sphere(0.14 * s, u=10, v=8), 'lamp', 'root', mtx((0, 0, 1.55 * s)))


def _ksiega(sl, mat='banner'):
    sl.add(box(0.36, 0.26, 0.07, 0.01), mat, 'root', mtx((0, 0, 0)))
    sl.add(box(0.33, 0.24, 0.05, 0.0), 'paper', 'root', mtx((0.01, 0, 0.0)))


def akademia(sl, p):
    rng = random.Random(6000 + p)
    if p <= 5:
        cx, cy, w, d = 0.0, 1.7, 3.4, 2.4
        _bale(sl, cx, cy, w, d, 0.0, 2.2, r=0.14)
        _dach2(sl, cx, cy, 2.2, w, d, 1.3, ov=0.35, rzedy=3, szczyt='log')
        _drzwi(sl, -0.6, cy - d / 2 - 0.15, 0.0, 0.9, 1.7)
        _okno(sl, 0.8, cy - d / 2 - 0.15, 1.3, 0.6, 0.6, okiennice=True)
        _stol(_w(sl, 0.6, -0.6))
        sl.add(cyl(0.18, 0.18, 0.45, 8), 'log', 'root', mtx((0.6, -1.2, 0.22)))
        if p >= 2:
            _regal(_w(sl, -2.3, 0.5, 0, 90))
            _latarnia(sl, -0.9, -0.5, 0.0, 1.8)
        if p >= 3:
            _luneta(_w(sl, 2.2, 0.0, 0, 30))
        if p >= 4:
            sl.add(box(1.6, 1.0, 0.2, 0.02), 'wood_dark', 'root', mtx((-1.8, -2.2, 0.1)))
            sl.add(box(1.5, 0.9, 0.04, 0.0), 'dirt', 'root', mtx((-1.8, -2.2, 0.2)))
            for i in range(8):
                sl.add(ico(0.13, 1), ('leaves', 'flower_y', 'leaves', 'flower_r')[i % 4], 'root',
                       mtx((-2.35 + (i % 4) * 0.37, -2.4 + (i // 4) * 0.4, 0.3)))
        if p >= 5:
            _globus(_w(sl, 1.8, -2.0))
        return
    if p <= 10:
        cx, cy, w, d = 0.0, 1.6, 4.6, 3.0
        sl.add(box(w + 0.2, d + 0.2, 0.4, 0.03), 'stone_dark', 'root', mtx((cx, cy, 0.2)))
        _szachulec(sl, cx, cy, w, d, 0.4, 2.6)
        _dach2(sl, cx, cy, 3.0, w, d, 1.6, ov=0.4, rzedy=4, szczyt='plaster')
        _drzwi(sl, cx, cy - d / 2 - 0.1, 0.4, 1.0, 1.9)
        for sx in (-1.5, 1.5):
            _okno(sl, sx, cy - d / 2 - 0.1, 1.8, 0.9, 1.1, szklo='glass_lit' if p >= 10 else 'glass')
        _stol(_w(sl, 1.5, -1.0))
        _globus(_w(sl, 2.5, -2.2))
        _luneta(_w(sl, -2.4, -2.2, 0, -20))
        if p >= 7:  # biblioteka
            _bale(sl, -2.5, cy + 0.3, 1.4, 2.2, 0.0, 2.0, r=0.12)
            _dach2(sl, -2.5, cy + 0.3, 2.0, 1.4, 2.2, 0.8, ov=0.25, rzedy=2, szczyt='log')
            _regal(_w(sl, -2.5, cy + 0.3 - 1.35, 0, 0))
        if p >= 8:  # taras z lunetą
            sl.add(box(1.6, 1.6, 0.12, 0.02), 'wood', 'root', mtx((1.2, cy + 0.3, 4.15)))
            for sx in (0.45, 1.95):
                sl.add(cyl(0.06, 0.06, 1.3, 6), 'wood_dark', 'root', mtx((sx, cy + 0.3, 3.55)))
            for (ox, oy, ww, dd) in ((0, -0.78, 1.6, 0.05), (0, 0.78, 1.6, 0.05), (-0.78, 0, 0.05, 1.6), (0.78, 0, 0.05, 1.6)):
                sl.add(box(ww, dd, 0.45, 0.0), 'wood_dark', 'root', mtx((1.2 + ox, cy + 0.3 + oy, 4.45)))
            _luneta(_w(sl, 1.2, cy + 0.3, 4.2, 20), 0.8)
        if p >= 9:
            _stol(_w(sl, -0.8, -1.6, 0, 15), 'kolby')
        if p >= 10:
            sl.add(box(1.2, 0.08, 0.8, 0.02), 'coal', 'root', mtx((-2.5, -0.4, 1.3), (0, 0, 90)))
            for k in range(3):
                sl.add(box(0.03, 0.6, 0.03, 0.0), 'paper', 'root', mtx((-2.45, -0.4, 1.5 - k * 0.2)))
            for sy in (-0.5, -0.3):
                sl.add(box(0.06, 0.06, 1.0, 0.0), 'wood_dark', 'root', mtx((-2.55, -0.4 + sy * 1.4 + 0.56, 0.5)))
            for sx in (-1.1, 1.1):
                _sztandar(sl, sx, cy - d / 2 - 0.5, 0.0, 2.6, 'magic_dark')
        return
    if p <= 15:
        cx, cy, w, d = 0.0, 1.5, 4.8, 3.0
        _bloki_prost(sl, rng, cx, cy, w, d, 0.0, 3.4, mats=('stone_light', 'stone', 'stone_light'))
        dachy = DACHOWKI if p >= 15 else GONT
        _dach2(sl, cx, cy, 3.4, w, d, 1.7, mats=dachy, ov=0.4, rzedy=4, szczyt='stone_light')
        _drzwi(sl, cx, cy - d / 2 - 0.1, 0.0, 1.1, 2.1, luk=True)
        for sx in (-1.6, 1.6):
            for z in (1.3, 2.7):
                _okno(sl, sx, cy - d / 2 - 0.1, z, 0.55, 0.8, rama='stone_light', luk=True)
        _regal(_w(sl, -2.5, -1.2, 0, 90))
        _stol(_w(sl, 1.6, -1.4), 'kolby')
        if p >= 12:  # wieżyczka obserwatorium
            _wieza(sl, random.Random(120), 0.95, 0.9, 0.0, 5.4, cx=2.0, cy=cy + 0.8, wys_rzedu=0.55, mat=('stone_light', 'stone', 'stone_light'))
            sl.add(sphere(1.0, 1.0, 0.85, u=16, v=8), 'stone_light' if p < 15 else 'roof', 'root', mtx((2.0, cy + 0.8, 5.4)))
            sl.add(box(0.3, 1.1, 0.9, 0.0), 'coal', 'root', mtx((2.0, cy + 0.25, 5.85), (35, 0, 0)))
            sl.add(cyl(0.1, 0.14, 1.2, 8), 'gold', 'root', mtx((2.0, cy + 0.05, 6.1), (50, 0, 0)))
        if p >= 13:
            _sfera(_w(sl, -0.3, -2.1), 1.0)
        if p >= 14:
            _posag_postaci(_w(sl, -2.4, -2.5), 'rycerz')
            _ksiega(_w(sl, -2.15, -2.75, 1.45, 30), 'banner')
        if p >= 15:
            for sx in (-1.0, 1.0):
                _sztandar(sl, sx, cy - d / 2 - 0.4, 0.0, 2.8, 'magic_dark')
        return
    # 16–20 okazała akademia
    cx, cy, w, d = -0.3, 1.5, 4.6, 3.0
    _bloki_prost(sl, rng, cx, cy, w, d, 0.0, 3.8, mats=('stone_light', 'stone', 'stone_light'))
    _dach2(sl, cx, cy, 3.8, w, d, 1.7, mats=DACHOWKI, ov=0.4, rzedy=4, szczyt='stone_light')
    szklo = 'rune' if p >= 18 else 'glass'
    rama = 'gold' if p >= 18 else 'stone_light'
    _drzwi(sl, cx, cy - d / 2 - 0.1, 0.0, 1.1, 2.1, luk=True)
    for sx in (-1.5, 1.5):
        for z in (1.3, 2.9):
            _okno(sl, cx + sx, cy - d / 2 - 0.1, z, 0.55, 0.85, szklo=szklo, rama=rama, luk=True)
    # portyk
    py = cy - d / 2 - 1.1
    for sx in (-1.2, -0.4, 0.4, 1.2):
        sl.add(cyl(0.16, 0.16, 2.8, 10), 'stone_light', 'root', mtx((cx + sx, py, 1.4)))
        sl.add(box(0.4, 0.4, 0.15, 0.02), rama, 'root', mtx((cx + sx, py, 2.88)))
    sl.add(box(3.2, 1.4, 0.25, 0.03), 'stone_light', 'root', mtx((cx, py + 0.45, 3.05)))
    bm = bmesh.new()  # trójkątny fronton
    vs = [bm.verts.new(V(cx - 1.6, py - 0.2, 3.17)), bm.verts.new(V(cx + 1.6, py - 0.2, 3.17)), bm.verts.new(V(cx, py - 0.2, 3.9))]
    bm.faces.new(vs)
    bm.normal_update()
    bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.3)
    sl.add(bm, 'stone_light', 'root')
    if p >= 18:
        sl.add(box(0.5, 0.06, 0.3, 0.01), 'gold', 'root', mtx((cx, py - 0.38, 3.45)))
    # obserwatorium
    ox, oy = 2.1, cy + 0.9
    r_o = 1.0 if p < 17 else 1.25
    _wieza(sl, random.Random(160), r_o, r_o - 0.05, 0.0, 5.6, cx=ox, cy=oy, wys_rzedu=0.55, mat=('stone_light', 'stone', 'stone_light'))
    sl.add(sphere(r_o + 0.1, r_o + 0.1, r_o, u=18, v=9), 'roof', 'root', mtx((ox, oy, 5.6)))
    sl.add(box(0.35, 1.2, r_o, 0.0), 'coal', 'root', mtx((ox, oy - r_o * 0.55, 6.1), (35, 0, 0)))
    tl = 1.3 if p < 17 else 2.2
    sl.add(cyl(0.12, 0.2 if p >= 17 else 0.14, tl, 10), 'gold', 'root', mtx((ox, oy - 0.5 - tl * 0.25, 6.3), (50, 0, 0)))
    _sfera(_w(sl, -0.3, -2.6), 0.9)
    _regal(_w(sl, -2.8, -1.5, 0, 90))
    if p >= 19:  # unoszące się księgi i kule
        for i, (x, y, z) in enumerate(((-2.2, -2.4, 2.0), (-1.7, -2.7, 2.4), (2.4, -2.3, 2.2), (1.9, -2.7, 1.8))):
            _ksiega(_w(sl, x, y, z, 30 * i), ('banner', 'banner_red', 'magic_dark', 'leather')[i])
        for (x, y, z) in ((-2.6, -0.6, 2.6), (2.7, -1.0, 2.8)):
            sl.add(sphere(0.18, u=10, v=8), 'magic', 'root', mtx((x, y, z)))
    if p >= 20:
        _krysztal(_w(sl, ox, oy, 7.9), 1.3, 'rune')
        _pierscien(_w(sl, ox, oy, 7.9), 0.75, 0.0, 'gold', n=18, grub=0.06)


# ================================================================== PODWÓRZE (grunt pod budynkiem, bez „kwadratu” działki)

def _podloze(sl, p, w, g, seed=1):
    """Nieregularne podwórze budynku – zmienia się z poziomem: ubita ziemia -> żwir -> płyty -> bruk z obwódką."""
    rng = random.Random(seed)
    mat = 'dirt' if p <= 5 else ('gravel' if p <= 10 else 'paving')
    nx, ny = 3, 3
    for i in range(nx):
        for j in range(ny):
            x = -w / 2 + (i + 0.5) * w / nx + rng.uniform(-0.25, 0.25)
            y = -g / 2 + (j + 0.5) * g / ny + rng.uniform(-0.25, 0.25)
            r = min(w, g) / 3 * rng.uniform(0.78, 0.92)
            sl.add(cyl(r, r, 0.04, 10), mat, 'root', mtx((x, y, 0.02 + 0.004 * (i * ny + j)), (0, 0, rng.uniform(0, 36))))
    if p >= 11:  # płyty na przedniej części podwórza
        y0, y1 = -g / 2 + 0.4, -0.2
        y = y0
        k = 0
        while y < y1:
            x = -w / 2 + 0.6 + (0.3 if k % 2 else 0.0)
            while x < w / 2 - 0.5:
                if rng.random() < 0.9:
                    sl.add(rock(0.62, 0.48, 0.07, rng.randint(0, 9999), rough=0.05, bevel=0.2),
                           rng.choice(('paving', 'stone', 'paving')), 'root', mtx((x, y, 0.06), (0, 0, rng.uniform(-6, 6))))
                x += 0.68
            y += 0.55
            k += 1
    if p >= 6:  # krzewy i kwiaty na skraju (nie z przodu – tam jest wejście)
        for i in range(10 if p < 16 else 16):
            a = rng.uniform(0.15, 0.85) * math.pi if i % 2 else rng.uniform(-0.15, 0.15) * math.pi + (0 if i % 4 == 1 else math.pi)
            x, y = math.cos(a) * w * 0.47, math.sin(a) * g * 0.47
            if y < -g * 0.3:
                continue
            sl.add(ico(rng.uniform(0.22, 0.34), 1), 'leaves', 'root', mtx((x, y, 0.2)))
            if p >= 11 and i % 3 == 0:
                sl.add(ico(0.08, 0), rng.choice(('flower_r', 'flower_y')), 'root', mtx((x, y - 0.15, 0.42)))


def budynek(sl, bid, p):
    """Budynek z działki (id z BUDYNKI) na poziomie p, razem z podwórzem."""
    b = BUDYNKI[bid]
    _podloze(sl, p, *b['podworze'], seed=len(bid) * 31 + p // 6)
    b['fn'](sl, p)
    return []


# 'podworze' – rozmiar podwórza w układzie budynku (szer. x gł.), dopasowany do działki
BUDYNKI = {
    'kuznia': {'nazwa': 'Kuźnia', 'fn': kuznia, 'zmiany': ZMIANY_KUZNIA, 'podworze': (6.8, 6.8)},
    'koszary': {'nazwa': 'Koszary', 'fn': koszary, 'zmiany': ZMIANY_KOSZARY, 'podworze': (6.8, 6.8)},
    'budynek_fuzji': {'nazwa': 'Budynek fuzji', 'fn': budynek_fuzji, 'zmiany': ZMIANY_FUZJA, 'podworze': (6.8, 6.8)},
    'magazyn': {'nazwa': 'Magazyn', 'fn': magazyn, 'zmiany': ZMIANY_MAGAZYN, 'podworze': (6.8, 6.8)},
    'akademia': {'nazwa': 'Akademia', 'fn': akademia, 'zmiany': ZMIANY_AKADEMIA, 'podworze': (5.8, 6.3)},
}
