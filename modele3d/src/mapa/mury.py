"""MAPA – MURY, BRAMA I WIEŻE NAROŻNE w 5 ETAPACH WYGLĄDU.

Gra ma 15 poziomów ulepszeń; wygląd zmienia się co 3 poziomy (etap = (poziom + 2) // 3),
patrz mapa/uklad.py (POZIOMY, ETAPY). Tu jest wygląd każdego ETAPU:
  1 Palisada (bez pomostu – brak obrońców), 2 Mur drewniany (mało obrońców),
  3 Słaby mur kamienny, 4 Lepszy mur kamienny, 5 Warownia.

Układ elementu: mur biegnie wzdłuż osi X (środek w 0,0), strona ZEWNĘTRZNA (wróg) to -Y,
wewnętrzna (miasto, pomost dla obrońców) to +Y. Ziemia: z = 0.

Każda funkcja zwraca listę MIEJSC DLA OBROŃCÓW: [(nazwa, (x, y, z)), ...] – eksportowane jako
puste węzły 'obronca_01'... w pliku .glb, Godot stawia na nich jednostki.

Nowy etap wyglądu: dopisz gałąź `elif poz == 6:` w funkcjach poniżej i wpis w uklad.ETAPY.
(W kodzie zmienna `poz` oznacza ETAP wyglądu.)
"""
import math
import random

from kit import V, box, cyl, sphere, ico, rock, taper, jitter, mtx, frame, seg

PALETA = {
    'wood': ('#8a5a2b', 0.85), 'wood_dark': ('#5e3b1c', 0.9), 'wood_light': ('#b07a42', 0.85),
    'iron': ('#4d545c', 0.45, 0.8),
    'stone': ('#9a948a', 0.92), 'stone_dark': ('#6d665e', 0.95), 'stone_light': ('#b9b2a5', 0.9),
    'roof': ('#2f5fb8', 0.75), 'banner': ('#2f5fb8', 0.8), 'gold': ('#e0ac3c', 0.3, 0.9),
    'rune': ('#2fd0ff', 0.4, 0.0, 4.0),
    'fire': ('#ff5200', 0.4, 0.0, 2.2), 'fire_core': ('#ffae00', 0.3, 0.0, 3.0),
}

# wysokość pomostu (gdzie stoją obrońcy) i liczba miejsc na 28 m muru – dla każdego ETAPU
POMOST = {1: 0.0, 2: 2.6, 3: 3.6, 4: 4.2, 5: 5.0}
OBRONCY_NA_28M = {1: 0, 2: 2, 3: 3, 4: 5, 5: 6}


def _miejsca(poz, L, brama_szer, y):
    if OBRONCY_NA_28M[poz] == 0:
        return []
    n = max(1, round(OBRONCY_NA_28M[poz] * L / 28.0))
    out = []
    odcinki = [(-L / 2, -brama_szer / 2 - 1.0), (brama_szer / 2 + 1.0, L / 2)] if brama_szer else [(-L / 2, L / 2)]
    dl = sum(b - a for a, b in odcinki)
    for i in range(n):
        s = (i + 0.5) * dl / n
        for a, b in odcinki:
            if s <= b - a:
                out.append((a + s, y, POMOST[poz] + 0.02))
                break
            s -= b - a
    return [(f'obronca_{k + 1:02d}', p) for k, p in enumerate(out)]


def _bloki(sl, rng, a, b, y, gl, z0, z1, wys_rzedu=0.7, mat=('stone', 'stone_dark', 'stone_light')):
    """Mur z kamiennych bloków: rzędy przesunięte jak w prawdziwym murze."""
    z, r = z0, 0
    while z < z1 - 0.05:
        h = min(wys_rzedu, z1 - z)
        x = a - (0.6 if r % 2 else 0.0)
        while x < b:
            dl = rng.uniform(1.0, 1.6)
            x0, x1 = max(x, a), min(x + dl, b)
            if x1 - x0 > 0.2:
                sl.add(rock(x1 - x0 - 0.04, gl, h - 0.03, rng.randint(0, 9999), rough=0.04, bevel=0.12),
                       rng.choice(mat), 'root', mtx(((x0 + x1) / 2, y, z + h / 2)))
            x += dl
        z += h
        r += 1


# ------------------------------------------------------------------ odcinek muru

def _odcinek(sl, poz, a, b, rng):
    L, m = b - a, (a + b) / 2
    if poz == 1:  # palisada (bez pomostu – obrońcy nie mają gdzie stanąć)
        n = max(1, int(L / 0.44))
        for i in range(n):
            x = a + (i + 0.5) * L / n
            r, h = 0.2 + rng.uniform(-0.02, 0.03), 3.0 + rng.uniform(-0.25, 0.2)
            sl.add(cyl(r, r, h, 8), 'wood', 'root', mtx((x, 0, h / 2)))
            sl.add(cyl(r, 0.0, 0.45, 8), 'wood_light', 'root', mtx((x, 0, h + 0.22)))
        for z in (1.0, 2.4):
            sl.add(box(L, 0.12, 0.18, 0.03), 'wood_dark', 'root', mtx((m, 0.24, z)))
        x = a + 2.0
        while x < b - 1.0:  # podpórki od strony miasta
            p0, p1 = V(x, 1.6, 0), V(x, 0.3, 2.2)
            sl.add(cyl(0.1, 0.1, (p1 - p0).length, 6), 'wood_dark', 'root', seg(p0, p1))
            x += 4.0
    elif poz == 2:  # wzmocniona palisada
        sl.add(box(L, 1.1, 0.35, 0.08), 'stone_dark', 'root', mtx((m, -0.05, 0.17)))
        n = max(1, int(L / 0.52))
        for i in range(n):
            x = a + (i + 0.5) * L / n
            r, h = 0.26 + rng.uniform(-0.02, 0.03), 3.6 + rng.uniform(-0.2, 0.2)
            sl.add(cyl(r, r, h, 8), 'wood', 'root', mtx((x, 0, h / 2)))
            sl.add(cyl(r, 0.0, 0.5, 8), 'wood_light', 'root', mtx((x, 0, h + 0.25)))
        n2 = max(1, int(L / 0.46))
        for i in range(n2):
            x = a + (i + 0.25) * L / n2
            sl.add(cyl(0.21, 0.21, 2.7, 8), 'wood_dark', 'root', mtx((x, 0.45, 1.35)))
        for z in (1.2, 2.8):
            sl.add(box(L, 0.1, 0.32, 0.03), 'wood_dark', 'root', mtx((m, -0.3, z)))
            x = a + 0.5
            while x < b:
                sl.add(sphere(0.045, u=8, v=6), 'iron', 'root', mtx((x, -0.36, z)))
                x += 1.0
        sl.add(box(L, 1.7, 0.12, 0.02), 'wood_light', 'root', mtx((m, 1.25, 2.6)))
        x = a + 0.4
        while x < b:
            sl.add(cyl(0.1, 0.1, 2.6, 6), 'wood_dark', 'root', mtx((x, 2.0, 1.3)))
            sl.add(cyl(0.06, 0.06, 1.0, 6), 'wood_dark', 'root', mtx((x, 2.05, 3.1)))
            x += 1.6
        sl.add(box(L, 0.08, 0.1, 0.02), 'wood', 'root', mtx((m, 2.05, 3.55)))
        x = a + 3.5
        while x < b - 0.5:  # skośne podpory
            p0, p1 = V(x, 2.6, 0), V(x, 0.6, 2.4)
            sl.add(cyl(0.12, 0.12, (p1 - p0).length, 6), 'wood_dark', 'root', seg(p0, p1))
            x += 7.0
    elif poz == 3:  # słaby mur kamienny: nieobrobione kamienie, drewniane blanki
        H = POMOST[3]
        _bloki(sl, rng, a, b, 0.5, 1.9, 0.0, H, wys_rzedu=0.9, mat=('stone_dark', 'stone', 'stone_dark'))
        sl.add(box(L, 1.7, 0.1, 0.02), 'wood_light', 'root', mtx((m, 0.55, H + 0.05)))
        sl.add(box(L, 0.14, 0.9, 0.02), 'wood', 'root', mtx((m, -0.35, H + 0.45)))
        x = a + 0.5
        while x < b:
            sl.add(cyl(0.08, 0.08, 1.2, 6), 'wood_dark', 'root', mtx((x, -0.35, H + 0.5)))
            x += 1.5
    elif poz == 4:  # lepszy mur kamienny
        H = POMOST[4]
        _bloki(sl, rng, a, b, 0.6, 2.2, 0.0, H)
        sl.add(box(L, 2.0, 0.12, 0.02), 'stone_light', 'root', mtx((m, 0.6, H + 0.06)))
        x = a + 0.4
        while x < b - 0.3:
            sl.add(box(0.75, 0.5, 0.85, 0.06), 'stone', 'root', mtx((x + 0.37, -0.3, H + 0.48)))
            x += 1.3
        sl.add(box(L, 0.25, 0.4, 0.03), 'stone_dark', 'root', mtx((m, 1.6, H + 0.2)))
    elif poz == 5:  # warownia
        H = POMOST[5]
        sl.add(taper(box(L, 3.6, 1.2, 0.1), bottom=1.0, top=0.85, axis='y'), 'stone_dark', 'root', mtx((m, 0.6, 0.6)))
        _bloki(sl, rng, a, b, 0.6, 2.8, 1.2, H, wys_rzedu=0.75)
        sl.add(box(L, 2.6, 0.14, 0.02), 'stone_light', 'root', mtx((m, 0.6, H + 0.07)))
        x = a + 0.4
        while x < b - 0.4:
            sl.add(box(0.9, 0.6, 1.0, 0.07), 'stone', 'root', mtx((x + 0.45, -0.5, H + 0.57)))
            x += 1.5
        sl.add(box(L, 0.3, 0.55, 0.03), 'stone_dark', 'root', mtx((m, 1.75, H + 0.27)))
        x = a + 3.2
        k = 0
        while x < b - 1.0:
            sl.add(taper(box(1.3, 1.4, H * 0.85, 0.08), bottom=1.25, top=0.8), 'stone_dark', 'root', mtx((x, -1.35, H * 0.42)))
            sl.add(box(0.36, 0.06, 0.36, 0.02), 'rune', 'root', mtx((x, -2.06, 2.4), (0, 45, 0)))
            if k % 2 == 0:  # sztandar z herbem i kosz z ogniem
                sl.add(box(1.3, 0.06, 2.3, 0.02), 'banner', 'root', mtx((x + 1.6, -0.84, H - 1.45)))
                sl.add(box(1.32, 0.08, 0.08, 0.01), 'gold', 'root', mtx((x + 1.6, -0.86, H - 0.32)))
                sl.add(box(0.4, 0.04, 0.4, 0.02), 'gold', 'root', mtx((x + 1.6, -0.89, H - 1.4), (0, 45, 0)))
                sl.add(cyl(0.3, 0.18, 0.3, 10), 'iron', 'root', mtx((x + 1.6, 1.6, H + 0.5)))
                for i in range(4):
                    a2 = i * math.pi / 2
                    q = V(x + 1.6 + math.cos(a2) * 0.1, 1.6 + math.sin(a2) * 0.1, H + 0.6)
                    sl.add(cyl(0.12, 0.0, 0.5, 6), 'fire', 'root', mtx(q + V(0, 0, 0.25)))
                sl.add(cyl(0.08, 0.0, 0.35, 6), 'fire_core', 'root', mtx((x + 1.6, 1.6, H + 0.8)))
            x += 6.5
            k += 1


def mur(sl, poz, L, brama_szer=0.0, seed=1):
    rng = random.Random(seed * 100 + poz)
    if brama_szer:
        _odcinek(sl, poz, -L / 2, -brama_szer / 2, rng)
        _odcinek(sl, poz, brama_szer / 2, L / 2, rng)
    else:
        _odcinek(sl, poz, -L / 2, L / 2, rng)
    y = {1: 0.0, 2: 1.25, 3: 0.55, 4: 0.6, 5: 0.6}[poz]
    return _miejsca(poz, L, brama_szer, y)


# ------------------------------------------------------------------ brama (środek prześwitu w 0,0)

def brama(sl, poz):
    W = 6.0
    miejsca = []

    def wrota(h, okucia):
        for sg in (1, -1):
            x = sg * W / 4
            sl.add(box(W / 2 - 0.12, 0.18, h, 0.03), 'wood', 'root', mtx((x, 0.0, h / 2)))
            for z in ((0.5, h - 0.5) if not okucia else (0.5, h / 2, h - 0.5)):
                sl.add(box(W / 2 - 0.2, 0.1, 0.22, 0.02), 'iron' if okucia else 'wood_dark', 'root', mtx((x, -0.13, z)))
            p0, p1 = V(x - sg * 1.2, -0.13, 0.6), V(x + sg * 1.2, -0.13, h - 0.6)
            sl.add(box(0.2, 0.08, (p1 - p0).length), 'wood_dark', 'root', seg(p0, p1, (0, 1, 0)))
            if okucia:
                for i in range(5):
                    for z in (0.5, h / 2, h - 0.5):
                        sl.add(sphere(0.05, u=8, v=6), 'iron', 'root', mtx((x - 1.1 + i * 0.55, -0.19, z)))

    if poz == 1:
        for sg in (1, -1):
            sl.add(cyl(0.36, 0.36, 4.2, 10), 'wood_dark', 'root', mtx((sg * 3.25, 0, 2.1)))
            sl.add(cyl(0.36, 0.0, 0.5, 10), 'wood_light', 'root', mtx((sg * 3.25, 0, 4.45)))
        sl.add(box(7.0, 0.4, 0.4, 0.06), 'wood_dark', 'root', mtx((0, 0, 3.9)))
        wrota(3.4, False)
    elif poz == 2:
        for sg in (1, -1):
            sl.add(cyl(0.44, 0.44, 5.0, 10), 'wood_dark', 'root', mtx((sg * 3.3, 0.3, 2.5)))
            sl.add(cyl(0.46, 0.46, 0.15, 10), 'iron', 'root', mtx((sg * 3.3, 0.3, 1.5)))
            sl.add(cyl(0.46, 0.46, 0.15, 10), 'iron', 'root', mtx((sg * 3.3, 0.3, 3.5)))
        sl.add(box(7.6, 2.4, 0.22, 0.04), 'wood_light', 'root', mtx((0, 0.6, 4.1)))
        sl.add(box(7.6, 0.1, 0.9, 0.03), 'wood', 'root', mtx((0, -0.55, 4.6)))
        sl.add(cyl(4.6, 0.6, 1.6, 4), 'wood_dark', 'root', mtx((0, 0.6, 5.9), (0, 0, 45)) @ mtx() )
        for sg in (1, -1):
            for y in (-0.4, 1.6):
                sl.add(cyl(0.1, 0.1, 1.2, 6), 'wood_dark', 'root', mtx((sg * 3.5, y, 4.8)))
        wrota(3.8, True)
        miejsca = [('obronca_01', (-1.8, 0.8, 4.22)), ('obronca_02', (1.8, 0.8, 4.22))]
    elif poz == 3:  # słaby kamień: filary z polnego kamienia, drewniany pomost nad bramą
        rng = random.Random(30)
        for sg in (1, -1):
            _bloki(sl, rng, sg * 3.9 - 1.0, sg * 3.9 + 1.0, 0.5, 2.6, 0.0, 4.6, wys_rzedu=0.9,
                   mat=('stone_dark', 'stone', 'stone_dark'))
        sl.add(box(9.8, 2.2, 0.16, 0.03), 'wood_light', 'root', mtx((0, 0.5, 4.6)))
        sl.add(box(9.8, 0.14, 0.9, 0.02), 'wood', 'root', mtx((0, -0.55, 5.1)))
        sl.add(box(6.4, 0.5, 0.5, 0.06), 'wood_dark', 'root', mtx((0, -0.2, 4.3)))
        wrota(4.0, True)
        miejsca = [('obronca_01', (-1.5, 0.6, 4.7)), ('obronca_02', (1.5, 0.6, 4.7))]
    elif poz == 4:
        rng = random.Random(33)
        for sg in (1, -1):
            _bloki(sl, rng, sg * 4.2 - 1.3, sg * 4.2 + 1.3, 0.6, 3.4, 0.0, 6.0)
            for i in range(2):
                sl.add(box(0.8, 0.5, 0.8, 0.06), 'stone', 'root', mtx((sg * 4.2 + (i - 0.5) * 1.3, -0.95, 6.4)))
        _bloki(sl, rng, -3.0, 3.0, 0.6, 3.4, 4.4, 6.0, wys_rzedu=0.8)
        sl.add(box(10.8, 3.2, 0.14, 0.02), 'stone_light', 'root', mtx((0, 0.6, 6.07)))
        for x in (-1.9, -0.6, 0.7, 2.0):
            sl.add(box(0.8, 0.5, 0.8, 0.06), 'stone', 'root', mtx((x, -0.95, 6.47)))
        wrota(4.3, True)
        miejsca = [('obronca_01', (-3.6, 0.8, 6.15)), ('obronca_02', (0.0, 0.8, 6.15)), ('obronca_03', (3.6, 0.8, 6.15))]
    elif poz == 5:
        rng = random.Random(44)
        for sg in (1, -1):
            sl.add(taper(cyl(2.3, 2.3, 8.0, 16), bottom=1.15, top=1.0), 'stone', 'root', mtx((sg * 4.7, 0.3, 4.0)))
            sl.add(cyl(2.4, 2.4, 0.3, 16), 'stone_dark', 'root', mtx((sg * 4.7, 0.3, 8.1)))
            sl.add(cyl(2.6, 0.0, 3.0, 16), 'roof', 'root', mtx((sg * 4.7, 0.3, 9.7)))
            sl.add(cyl(0.05, 0.05, 1.4, 6), 'iron', 'root', mtx((sg * 4.7, 0.3, 11.8)))
            sl.add(box(0.7, 0.04, 0.45, 0.01), 'banner', 'root', mtx((sg * 4.7 + 0.37, 0.3, 12.2)))
            sl.add(box(0.36, 0.06, 0.36, 0.02), 'rune', 'root', mtx((sg * 4.7, -2.0, 4.2), (0, 45, 0)))
        _bloki(sl, rng, -2.6, 2.6, 0.6, 3.6, 4.6, 7.0, wys_rzedu=0.8)
        sl.add(box(5.4, 3.4, 0.14, 0.02), 'stone_light', 'root', mtx((0, 0.6, 7.07)))
        for x in (-1.8, -0.6, 0.6, 1.8):
            sl.add(box(0.85, 0.55, 0.9, 0.06), 'stone', 'root', mtx((x, -1.0, 7.5)))
        sl.add(box(1.6, 0.06, 2.4, 0.02), 'banner', 'root', mtx((0, -1.25, 5.5)))
        sl.add(box(0.5, 0.05, 0.5, 0.02), 'gold', 'root', mtx((0, -1.29, 5.6), (0, 45, 0)))
        # brona (krata) przed wrotami
        for i in range(13):
            x = -2.7 + i * 0.45
            sl.add(cyl(0.05, 0.05, 4.2, 6), 'iron', 'root', mtx((x, -0.55, 2.4)))
        for z in (1.0, 2.2, 3.4):
            sl.add(box(5.6, 0.08, 0.08, 0.01), 'iron', 'root', mtx((0, -0.55, z)))
        wrota(4.4, True)
        miejsca = [('obronca_01', (-1.6, 0.8, 7.15)), ('obronca_02', (0.0, 0.8, 7.15)), ('obronca_03', (1.6, 0.8, 7.15))]
    return miejsca


# ------------------------------------------------------------------ wieża narożna (środek w 0,0)

def naroznik(sl, poz):
    if poz == 1:  # palisada: wiązka grubych pali na rogu, bez miejsca dla obrońcy
        for i in range(9):
            a = 2 * math.pi * i / 9
            r, h = 0.3, 3.4 + 0.3 * math.sin(i * 1.7)
            p = V(math.cos(a) * 0.75, math.sin(a) * 0.75, 0)
            sl.add(cyl(r, r, h, 8), 'wood', 'root', mtx(p + V(0, 0, h / 2)))
            sl.add(cyl(r, 0.0, 0.5, 8), 'wood_light', 'root', mtx(p + V(0, 0, h + 0.25)))
        sl.add(cyl(1.08, 1.08, 0.2, 12), 'wood_dark', 'root', mtx((0, 0, 1.4)))
        sl.add(cyl(1.08, 1.08, 0.2, 12), 'wood_dark', 'root', mtx((0, 0, 2.6)))
        return []
    if poz == 2:
        for x in (-1.1, 1.1):
            for y in (-1.1, 1.1):
                sl.add(cyl(0.16, 0.16, 4.4, 8), 'wood_dark', 'root', mtx((x, y, 2.2)))
        sl.add(box(2.9, 2.9, 0.16, 0.03), 'wood_light', 'root', mtx((0, 0, 4.2)))
        for (x, y, w, d) in ((0, -1.4, 2.9, 0.1), (0, 1.4, 2.9, 0.1), (-1.4, 0, 0.1, 2.9), (1.4, 0, 0.1, 2.9)):
            sl.add(box(w, d, 0.8, 0.02), 'wood', 'root', mtx((x, y, 4.65)))
        for x in (-1.3, 1.3):
            for y in (-1.3, 1.3):
                sl.add(cyl(0.08, 0.08, 1.6, 6), 'wood_dark', 'root', mtx((x, y, 5.1)))
        sl.add(cyl(2.3, 0.0, 1.5, 4), 'wood_dark', 'root', mtx((0, 0, 6.6), (0, 0, 45)))
        return [('obronca_01', (0.0, 0.0, 4.3))]
    if poz == 3:  # mała wieża z polnego kamienia z drewnianym daszkiem
        rng = random.Random(31)
        sl.add(cyl(2.0, 2.15, 4.8, 12), 'stone_dark', 'root', mtx((0, 0, 2.4)))
        for z in (1.2, 2.6, 4.0):
            sl.add(cyl(2.12, 2.12, 0.12, 12), 'stone', 'root', mtx((0, 0, z)))
        sl.add(cyl(2.25, 2.25, 0.16, 12), 'wood_light', 'root', mtx((0, 0, 4.88)))
        for i in range(6):
            a = 2 * math.pi * i / 6
            sl.add(cyl(0.09, 0.09, 1.6, 6), 'wood_dark', 'root', mtx((math.cos(a) * 1.9, math.sin(a) * 1.9, 5.7)))
        sl.add(cyl(2.6, 0.0, 1.6, 6), 'wood_dark', 'root', mtx((0, 0, 7.3)))
        return [('obronca_01', (0.0, 0.0, 4.98))]
    if poz == 4:
        sl.add(cyl(2.4, 2.4, 6.2, 18), 'stone', 'root', mtx((0, 0, 3.1)))
        for z in (1.5, 3.2, 4.9):
            sl.add(cyl(2.45, 2.45, 0.15, 18), 'stone_dark', 'root', mtx((0, 0, z)))
        sl.add(cyl(2.55, 2.55, 0.2, 18), 'stone_light', 'root', mtx((0, 0, 6.3)))
        for i in range(10):
            a = 2 * math.pi * i / 10
            sl.add(box(0.75, 0.5, 0.85, 0.06), 'stone', 'root', mtx((math.cos(a) * 2.25, math.sin(a) * 2.25, 6.8), (0, 0, math.degrees(a) + 90)))
        return [('obronca_01', (-0.8, 0.0, 6.42)), ('obronca_02', (0.8, 0.0, 6.42))]
    # poz 5
    sl.add(taper(cyl(2.8, 2.8, 7.5, 18), bottom=1.12, top=1.0), 'stone', 'root', mtx((0, 0, 3.75)))
    sl.add(cyl(3.0, 3.0, 0.25, 18), 'stone_light', 'root', mtx((0, 0, 7.6)))
    for i in range(4):
        a = 2 * math.pi * i / 4 + math.pi / 4
        sl.add(box(0.4, 0.4, 2.4, 0.04), 'stone_dark', 'root', mtx((math.cos(a) * 2.4, math.sin(a) * 2.4, 8.9)))
        sl.add(box(0.36, 0.06, 0.36, 0.02), 'rune', 'root', mtx((math.cos(a) * 2.95, math.sin(a) * 2.95, 3.5), (0, 45, math.degrees(a) + 90)))
    sl.add(cyl(3.3, 0.0, 3.2, 18), 'roof', 'root', mtx((0, 0, 11.7)))
    sl.add(cyl(0.05, 0.05, 1.6, 6), 'iron', 'root', mtx((0, 0, 14.0)))
    sl.add(box(0.9, 0.04, 0.55, 0.01), 'banner', 'root', mtx((0.47, 0, 14.4)))
    return [('obronca_01', (-0.9, 0.0, 7.75)), ('obronca_02', (0.9, 0.0, 7.75))]
