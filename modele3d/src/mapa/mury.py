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
from mapa import uszkodzenia as USZ

PALETA = {
    'wood': ('#8a5a2b', 0.85), 'wood_dark': ('#5e3b1c', 0.9), 'wood_light': ('#b07a42', 0.85),
    'iron': ('#4d545c', 0.45, 0.8),
    'stone': ('#9a948a', 0.92), 'stone_dark': ('#6d665e', 0.95), 'stone_light': ('#b9b2a5', 0.9),
    'roof': ('#2f5fb8', 0.75), 'roof_dark': ('#234a94', 0.75), 'banner': ('#2f5fb8', 0.8), 'gold': ('#e0ac3c', 0.3, 0.9),
    'shingle': ('#7a4e2a', 0.9), 'shingle_dark': ('#5a3820', 0.9),
    'rune': ('#2fd0ff', 0.4, 0.0, 4.0),
    'fire': ('#ff5200', 0.4, 0.0, 2.2), 'fire_core': ('#ffae00', 0.3, 0.0, 3.0),
    **USZ.PALETA,
}

# wysokość pomostu (gdzie stoją obrońcy) i liczba miejsc na 28 m muru – dla każdego ETAPU
POMOST = {1: 0.0, 2: 2.6, 3: 3.6, 4: 4.2, 5: 5.0}
OBRONCY_NA_28M = {1: 0, 2: 2, 3: 3, 4: 5, 5: 6}


def _miejsca(poz, L, brama_szer, y, margines=0.0, strefa_bramy=0.0):
    """Miejsca dla obrońców wzdłuż pomostu – z pominięciem końców muru (margines, tam stoją wieże)
    i okolicy bramy (strefa_bramy: bramа i wieże przy bramie)."""
    if OBRONCY_NA_28M[poz] == 0:
        return []
    n = max(1, round(OBRONCY_NA_28M[poz] * L / 28.0))
    out = []
    a0, b0 = -L / 2 + margines, L / 2 - margines
    odcinki = [(a0, -strefa_bramy), (strefa_bramy, b0)] if brama_szer else [(a0, b0)]
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


def _wieza(sl, rng, r0, r1, z0, z1, cx=0.0, cy=0.0, wys_rzedu=0.7, mat=('stone', 'stone_dark', 'stone_light')):
    """Okrągła wieża z kamiennych bloków ułożonych w rzędach (przesuniętych jak w murze).
    r0 – promień na dole, r1 – na górze (zwężenie)."""
    n = max(1, round((z1 - z0) / 1.2))  # rdzeń z kilku kawałków (przy uszkodzeniu odpada od góry)
    for i in range(n):
        za, zb = z0 + (z1 - z0) * i / n, z0 + (z1 - z0) * (i + 1) / n
        ra, rb = r0 + (r1 - r0) * i / n, r0 + (r1 - r0) * (i + 1) / n
        sl.add(cyl(ra * 0.88, rb * 0.88, zb - za, 14), 'stone_dark', 'root', mtx((cx, cy, (za + zb) / 2)))
    z, rzad = z0, 0
    while z < z1 - 0.05:
        h = min(wys_rzedu, z1 - z)
        r = r0 + (r1 - r0) * ((z + h / 2 - z0) / (z1 - z0))
        n = max(6, int(2 * math.pi * r / 1.15))
        dl = 2 * math.pi * r / n
        for i in range(n):
            a = 2 * math.pi * (i + 0.5 * (rzad % 2)) / n
            sl.add(rock(dl - 0.06, 0.62, h - 0.03, rng.randint(0, 9999), rough=0.04, bevel=0.12), rng.choice(mat), 'root',
                   mtx((cx + math.cos(a) * (r - 0.3), cy + math.sin(a) * (r - 0.3), z + h / 2), (0, 0, math.degrees(a) + 90)))
        z += h
        rzad += 1


DACHOWKI = ('roof', 'roof_dark')
GONT = ('shingle', 'shingle_dark')


def _dach(sl, cx, cy, z0, r, h, mat=DACHOWKI, boki=16, rzedy=6, obrot=0.0, iglica=True):
    """Dach z rzędów dachówek/gontu: pierścienie lekko na siebie nachodzą (dwa odcienie na zmianę),
    okap na dole i złota iglica na szczycie. z0 – wysokość okapu, h – wysokość dachu."""
    dz = h / rzedy
    for k in range(rzedy):
        t0, t1 = k / rzedy, (k + 1) / rzedy
        rb, rt = r * (1 - t0) + 0.1, r * (1 - t1) * 0.92
        sl.add(cyl(rb, rt, dz * 1.18, boki), mat[k % 2], 'root', mtx((cx, cy, z0 + dz * (k + 0.5)), (0, 0, obrot)))
    sl.add(cyl(r + 0.12, r + 0.12, 0.12, boki), 'wood_dark', 'root', mtx((cx, cy, z0 - 0.02), (0, 0, obrot)))
    if iglica:
        sl.add(sphere(0.13, u=10, v=8), 'gold', 'root', mtx((cx, cy, z0 + h + 0.05)))
        sl.add(cyl(0.06, 0.0, 0.45, 8), 'gold', 'root', mtx((cx, cy, z0 + h + 0.35)))


def _pas(sl, a, b, gl, h, bevel, mat, y, z, kawalek=1.6, ksztalt=None):
    """Długa listwa/belka wzdłuż X złożona z kawałków (≤ kawalek m), żeby przy uszkodzeniu
    mogła odpaść tylko jej część (np. zawalony fragment pomostu nad dziurą)."""
    n = max(1, math.ceil((b - a) / kawalek))
    dl = (b - a) / n
    for i in range(n):
        bm = box(dl - 0.01, gl, h, bevel)
        if ksztalt:
            bm = ksztalt(bm)
        sl.add(bm, mat, 'root', mtx((a + (i + 0.5) * dl, y, z)))


def _pal(sl, x, y, r, h, mat, segs=8):
    """Pal/słup z dwóch kawałków – przy uszkodzeniu może odpaść sama górna część (złamany pal)."""
    h0 = h * 0.55
    sl.add(cyl(r, r, h0, segs), mat, 'root', mtx((x, y, h0 / 2)))
    sl.add(cyl(r, r, h - h0, segs), mat, 'root', mtx((x, y, h0 + (h - h0) / 2)))


def _z_uszkodzeniami(sl, plan, budowa):
    """Buduje element (budowa() -> miejsca obrońców); z planem dzieli części na warstwy uszkodzeń
    i dodaje gruz, rysy i ogień (patrz uszkodzenia.py)."""
    if plan is None:
        return budowa()
    sl.klasyfikator = plan.klasyfikator
    miejsca = budowa()
    sl.klasyfikator = None
    plan.dodaj_skutki(sl)
    plan.dodaj_wylom(sl)
    for n, p in miejsca:
        plan.miejsce_obroncy(n, p, sl)
    return miejsca


# --- wymiary do planu uszkodzeń dla każdego ETAPU: szczyt (gora), pomost (gdzie zaczynają się blanki),
# lico zewnętrzne/wewnętrzne (rysy), stopa = (y przód, y tył) podstawy (gruz); drewno: bez rys, więcej ognia
USZ_MUR = {
    1: {'gora': 3.45, 'pomost': 2.3, 'lico': -0.22, 'stopa': (-0.25, 0.4), 'pekniecia': False, 'ognie': 3},
    2: {'gora': 4.1, 'pomost': POMOST[2], 'lico': -0.4, 'stopa': (-0.55, 2.2), 'pekniecia': False, 'ognie': 3},
    3: {'gora': POMOST[3] + 0.95, 'pomost': POMOST[3], 'lico': -0.45, 'lico_tyl': 1.45, 'stopa': (-0.45, 1.45)},
    4: {'gora': POMOST[4] + 0.9, 'pomost': POMOST[4], 'lico': -0.5, 'lico_tyl': 1.7, 'stopa': (-0.5, 1.75)},
    5: {'gora': POMOST[5] + 1.07, 'pomost': POMOST[5], 'lico': -0.8, 'lico_tyl': 2.0, 'stopa': (-1.25, 2.4)},
}
USZ_BRAMA = {
    1: {'gora': 4.7, 'pomost': 3.7, 'lico': -0.4, 'stopa': (-0.45, 0.45), 'pekniecia': False, 'ognie': 3},
    2: {'gora': 7.0, 'pomost': 4.22, 'lico': -0.6, 'stopa': (-0.7, 1.9), 'pekniecia': False, 'ognie': 3},
    3: {'gora': 5.55, 'pomost': 4.7, 'lico': -0.8, 'stopa': (-0.85, 1.85)},
    4: {'gora': 6.9, 'pomost': 6.15, 'lico': -1.1, 'stopa': (-1.2, 2.3)},
    5: {'gora': 7.95, 'pomost': 7.15, 'lico': -1.25, 'stopa': (-1.3, 2.4)},
}
USZ_WIEZA = {  # r – promień wieży
    1: {'r': 1.08, 'gora': 3.9, 'pomost': 2.9, 'pekniecia': False, 'ognie': 2},
    2: {'r': 1.45, 'gora': 7.45, 'pomost': 4.3, 'pekniecia': False, 'ognie': 2},
    3: {'r': 2.2, 'gora': 8.2, 'pomost': 4.98},
    4: {'r': 2.45, 'gora': 7.25, 'pomost': 6.42},
    5: {'r': 3.15, 'gora': 13.4, 'pomost': 7.75},
}


def _plan(d, seed, **kw):
    return USZ.Plan(d['gora'], d['pomost'], d.get('lico', 0.0), d.get('stopa', (0.0, 0.0)), seed=seed,
                    lico_tyl=d.get('lico_tyl'), pekniecia=d.get('pekniecia', True), ognie=d.get('ognie', 2), **kw)


def plan_bramy(poz):
    d = USZ_BRAMA[poz]
    g, sz = d['gora'], d['gora'] - d['pomost']
    dziury = [(1, -2.3, 1.2, sz + 0.4), (1, 2.6, 1.0, sz + 0.3),
              (2, 1.4, 2.4, g * 0.6), (2, -3.2, 1.0, sz + 1.0),
              (3, 0.0, 3.0, g + 3.0, 8)]           # wyłom: wrota i nadproże między filarami
    plan = _plan(d, 900 + poz, dziury=dziury, punkty=[-3.45, 3.45] if d.get('pekniecia', True) else [1.4],
                 wylom_x=0.0)
    plan.rozrzut = 0.25  # rysy tylko na filarach
    return plan


def plan_wiezy(poz):
    d = dict(USZ_WIEZA[poz])
    r, g, pm = d['r'], d['gora'], d['pomost']
    d['lico'] = lambda x: -math.sqrt(max(r * r - x * x, 0.04)) - 0.02
    d['lico_tyl'] = lambda x: math.sqrt(max(r * r - x * x, 0.04)) + 0.02
    d['stopa'] = (-r - 0.1, r + 0.1)
    dziury = [(1, 0.9 * r, 0.9 * r, (g - pm) * 0.5 + 0.4),
              (2, -0.3 * r, 2.2 * r, (g - pm) + 0.35 * pm),
              (3, 0.0, 2.6 * r, g - pm * 0.35)]     # stan 3: ruina – zostaje tylko dół wieży
    plan = _plan(d, 950 + poz, dziury=dziury, punkty=[0.3 * r])
    plan.rozrzut = 0.35 * r
    return plan


# ------------------------------------------------------------------ odcinek muru

def _odcinek(sl, poz, a, b, rng):
    L, m = b - a, (a + b) / 2
    if poz == 1:  # palisada (bez pomostu – obrońcy nie mają gdzie stanąć)
        n = max(1, int(L / 0.44))
        for i in range(n):
            x = a + (i + 0.5) * L / n
            r, h = 0.2 + rng.uniform(-0.02, 0.03), 3.0 + rng.uniform(-0.25, 0.2)
            _pal(sl, x, 0, r, h, 'wood')
            sl.add(cyl(r, 0.0, 0.45, 8), 'wood_light', 'root', mtx((x, 0, h + 0.22)))
        for z in (1.0, 2.4):
            _pas(sl, a, b, 0.12, 0.18, 0.03, 'wood_dark', 0.24, z)
        x = a + 2.0
        while x < b - 1.0:  # podpórki od strony miasta
            p0, p1 = V(x, 1.6, 0), V(x, 0.3, 2.2)
            sl.add(cyl(0.1, 0.1, (p1 - p0).length, 6), 'wood_dark', 'root', seg(p0, p1))
            x += 4.0
    elif poz == 2:  # wzmocniona palisada
        _pas(sl, a, b, 1.1, 0.35, 0.08, 'stone_dark', -0.05, 0.17)
        n = max(1, int(L / 0.52))
        for i in range(n):
            x = a + (i + 0.5) * L / n
            r, h = 0.26 + rng.uniform(-0.02, 0.03), 3.6 + rng.uniform(-0.2, 0.2)
            _pal(sl, x, 0, r, h, 'wood')
            sl.add(cyl(r, 0.0, 0.5, 8), 'wood_light', 'root', mtx((x, 0, h + 0.25)))
        n2 = max(1, int(L / 0.46))
        for i in range(n2):
            x = a + (i + 0.25) * L / n2
            _pal(sl, x, 0.45, 0.21, 2.7, 'wood_dark')
        for z in (1.2, 2.8):
            _pas(sl, a, b, 0.1, 0.32, 0.03, 'wood_dark', -0.3, z)
            x = a + 0.5
            while x < b:
                sl.add(sphere(0.045, u=8, v=6), 'iron', 'root', mtx((x, -0.36, z)))
                x += 1.0
        _pas(sl, a, b, 1.7, 0.12, 0.02, 'wood_light', 1.25, 2.6)
        x = a + 0.4
        while x < b:
            sl.add(cyl(0.1, 0.1, 2.6, 6), 'wood_dark', 'root', mtx((x, 2.0, 1.3)))
            sl.add(cyl(0.06, 0.06, 1.0, 6), 'wood_dark', 'root', mtx((x, 2.05, 3.1)))
            x += 1.6
        _pas(sl, a, b, 0.08, 0.1, 0.02, 'wood', 2.05, 3.55)
        x = a + 3.5
        while x < b - 0.5:  # skośne podpory
            p0, p1 = V(x, 2.6, 0), V(x, 0.6, 2.4)
            sl.add(cyl(0.12, 0.12, (p1 - p0).length, 6), 'wood_dark', 'root', seg(p0, p1))
            x += 7.0
    elif poz == 3:  # słaby mur kamienny: nieobrobione kamienie, drewniane blanki
        H = POMOST[3]
        _bloki(sl, rng, a, b, 0.5, 1.9, 0.0, H, wys_rzedu=0.9, mat=('stone_dark', 'stone', 'stone_dark'))
        _pas(sl, a, b, 1.7, 0.1, 0.02, 'wood_light', 0.55, H + 0.05)
        _pas(sl, a, b, 0.14, 0.9, 0.02, 'wood', -0.35, H + 0.45, kawalek=1.0)
        x = a + 0.5
        while x < b:
            sl.add(cyl(0.08, 0.08, 1.2, 6), 'wood_dark', 'root', mtx((x, -0.35, H + 0.5)))
            x += 1.5
    elif poz == 4:  # lepszy mur kamienny
        H = POMOST[4]
        _bloki(sl, rng, a, b, 0.6, 2.2, 0.0, H)
        _pas(sl, a, b, 2.0, 0.12, 0.02, 'stone_light', 0.6, H + 0.06)
        x = a + 0.4
        while x < b - 0.3:
            sl.add(box(0.75, 0.5, 0.85, 0.06), 'stone', 'root', mtx((x + 0.37, -0.3, H + 0.48)))
            x += 1.3
        _pas(sl, a, b, 0.25, 0.4, 0.03, 'stone_dark', 1.6, H + 0.2)
    elif poz == 5:  # warownia
        H = POMOST[5]
        _pas(sl, a, b, 3.6, 1.2, 0.1, 'stone_dark', 0.6, 0.6, kawalek=1.4,
             ksztalt=lambda bm: taper(bm, bottom=1.0, top=0.85, axis='y'))
        _bloki(sl, rng, a, b, 0.6, 2.8, 1.2, H, wys_rzedu=0.75)
        _pas(sl, a, b, 2.6, 0.14, 0.02, 'stone_light', 0.6, H + 0.07)
        x = a + 0.4
        while x < b - 0.4:
            sl.add(box(0.9, 0.6, 1.0, 0.07), 'stone', 'root', mtx((x + 0.45, -0.5, H + 0.57)))
            x += 1.5
        _pas(sl, a, b, 0.3, 0.55, 0.03, 'stone_dark', 1.75, H + 0.27)
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


def mur(sl, poz, L, brama_szer=0.0, seed=1, margines=3.6, strefa_bramy=9.6, uszkodzenia=False):
    """uszkodzenia=True: dodaje warstwy uszkodzeń (sl musi być uszkodzenia.Warstwy), patrz uszkodzenia.py."""
    rng = random.Random(seed * 100 + poz)
    plan = None
    if uszkodzenia:
        a0, b0 = -L / 2 + margines, L / 2 - margines
        wolne = [(a0, -strefa_bramy), (strefa_bramy, b0)] if brama_szer else [(a0, b0)]
        plan = _plan(USZ_MUR[poz], seed * 10 + poz, wolne=wolne)

    def budowa():
        if brama_szer:
            _odcinek(sl, poz, -L / 2, -brama_szer / 2, rng)
            _odcinek(sl, poz, brama_szer / 2, L / 2, rng)
        else:
            _odcinek(sl, poz, -L / 2, L / 2, rng)
        y = {1: 0.0, 2: 1.25, 3: 0.55, 4: 0.6, 5: 0.6}[poz]
        return _miejsca(poz, L, brama_szer, y, margines, strefa_bramy if brama_szer else 0.0)
    return _z_uszkodzeniami(sl, plan, budowa)


# ------------------------------------------------------------------ brama (środek prześwitu w 0,0)

def brama(sl, poz, uszkodzenia=False):
    return _z_uszkodzeniami(sl, plan_bramy(poz) if uszkodzenia else None, lambda: _brama(sl, poz))


def _brama(sl, poz):
    W = 6.0
    miejsca = []

    def wrota(h, okucia):
        for sg in (1, -1):
            x = sg * W / 4
            n, szer = 4, (W / 2 - 0.12) / 4      # skrzydło z 4 desek – przy uszkodzeniu odpadają pojedynczo
            for i in range(n):
                xi = x - (W / 2 - 0.12) / 2 + (i + 0.5) * szer
                sl.add(box(szer - 0.02, 0.18, h, 0.03), 'wood', 'root', mtx((xi, 0.0, h / 2)))
                for z in ((0.5, h - 0.5) if not okucia else (0.5, h / 2, h - 0.5)):
                    sl.add(box(szer, 0.1, 0.22, 0.01), 'iron' if okucia else 'wood_dark', 'root', mtx((xi, -0.13, z)))
            p0, p1 = V(x - sg * 1.2, -0.13, 0.6), V(x + sg * 1.2, -0.13, h - 0.6)
            for q0, q1 in ((p0, (p0 + p1) / 2), ((p0 + p1) / 2, p1)):
                sl.add(box(0.2, 0.08, (q1 - q0).length), 'wood_dark', 'root', seg(q0, q1, (0, 1, 0)))
            if okucia:
                for i in range(5):
                    for z in (0.5, h / 2, h - 0.5):
                        sl.add(sphere(0.05, u=8, v=6), 'iron', 'root', mtx((x - 1.1 + i * 0.55, -0.19, z)))

    if poz == 1:
        for sg in (1, -1):
            sl.add(cyl(0.36, 0.36, 4.2, 10), 'wood_dark', 'root', mtx((sg * 3.25, 0, 2.1)))
            sl.add(cyl(0.36, 0.0, 0.5, 10), 'wood_light', 'root', mtx((sg * 3.25, 0, 4.45)))
        _pas(sl, -3.5, 3.5, 0.4, 0.4, 0.06, 'wood_dark', 0, 3.9)
        wrota(3.4, False)
    elif poz == 2:
        for sg in (1, -1):
            sl.add(cyl(0.44, 0.44, 5.0, 10), 'wood_dark', 'root', mtx((sg * 3.3, 0.3, 2.5)))
            sl.add(cyl(0.46, 0.46, 0.15, 10), 'iron', 'root', mtx((sg * 3.3, 0.3, 1.5)))
            sl.add(cyl(0.46, 0.46, 0.15, 10), 'iron', 'root', mtx((sg * 3.3, 0.3, 3.5)))
        _pas(sl, -3.8, 3.8, 2.4, 0.22, 0.04, 'wood_light', 0.6, 4.1)
        _pas(sl, -3.8, 3.8, 0.1, 0.9, 0.03, 'wood', -0.55, 4.6)
        _dach(sl, 0, 0.6, 5.1, 4.4, 1.9, GONT, boki=4, rzedy=4, obrot=45, iglica=False)
        for sg in (1, -1):
            for y in (-0.4, 1.6):
                sl.add(cyl(0.1, 0.1, 1.2, 6), 'wood_dark', 'root', mtx((sg * 3.5, y, 4.8)))
        wrota(3.8, True)
        miejsca = [('obronca_01', (-1.8, 0.8, 4.22)), ('obronca_02', (1.8, 0.8, 4.22))]
    elif poz == 3:  # słaby kamień: filary z polnego kamienia, drewniany pomost nad bramą
        rng = random.Random(30)
        for sg in (1, -1):
            _bloki(sl, rng, sg * 3.45 - 0.45, sg * 3.45 + 0.45, 0.5, 2.6, 0.0, 4.6, wys_rzedu=0.9,
                   mat=('stone_dark', 'stone', 'stone_dark'))
        _pas(sl, -3.9, 3.9, 2.2, 0.16, 0.03, 'wood_light', 0.5, 4.6)
        _pas(sl, -3.9, 3.9, 0.14, 0.9, 0.02, 'wood', -0.55, 5.1)
        _pas(sl, -3.2, 3.2, 0.5, 0.5, 0.06, 'wood_dark', -0.2, 4.3)
        wrota(4.0, True)
        miejsca = [('obronca_01', (-1.5, 0.6, 4.7)), ('obronca_02', (1.5, 0.6, 4.7))]
    elif poz == 4:
        rng = random.Random(33)
        for sg in (1, -1):
            _bloki(sl, rng, sg * 3.45 - 0.45, sg * 3.45 + 0.45, 0.6, 3.4, 0.0, 6.0)
            sl.add(box(0.8, 0.5, 0.8, 0.06), 'stone', 'root', mtx((sg * 3.45, -0.95, 6.4)))
        _bloki(sl, rng, -3.0, 3.0, 0.6, 3.4, 4.4, 6.0, wys_rzedu=0.8)
        _pas(sl, -3.9, 3.9, 3.2, 0.14, 0.02, 'stone_light', 0.6, 6.07)
        for x in (-1.9, -0.6, 0.7, 2.0):
            sl.add(box(0.8, 0.5, 0.8, 0.06), 'stone', 'root', mtx((x, -0.95, 6.47)))
        wrota(4.3, True)
        miejsca = [('obronca_01', (-3.6, 0.8, 6.15)), ('obronca_02', (0.0, 0.8, 6.15)), ('obronca_03', (3.6, 0.8, 6.15))]
    elif poz == 5:
        rng = random.Random(44)
        for sg in (1, -1):  # filary bramy (wieże przy bramie są osobnymi elementami)
            _bloki(sl, rng, sg * 3.45 - 0.45, sg * 3.45 + 0.45, 0.6, 3.6, 0.0, 7.0, wys_rzedu=0.75)
            sl.add(box(0.36, 0.06, 0.36, 0.02), 'rune', 'root', mtx((sg * 3.45, -1.23, 4.2), (0, 45, 0)))
            sl.add(box(0.85, 0.55, 0.9, 0.06), 'stone', 'root', mtx((sg * 3.45, -1.0, 7.5)))
        _bloki(sl, rng, -3.0, 3.0, 0.6, 3.6, 4.6, 7.0, wys_rzedu=0.8)
        _pas(sl, -3.9, 3.9, 3.4, 0.14, 0.02, 'stone_light', 0.6, 7.07)
        for x in (-1.8, -0.6, 0.6, 1.8):
            sl.add(box(0.85, 0.55, 0.9, 0.06), 'stone', 'root', mtx((x, -1.0, 7.5)))
        sl.add(box(1.6, 0.06, 2.4, 0.02), 'banner', 'root', mtx((0, -1.25, 5.5)))
        sl.add(box(0.5, 0.05, 0.5, 0.02), 'gold', 'root', mtx((0, -1.29, 5.6), (0, 45, 0)))
        # brona (krata) przed wrotami
        for i in range(13):
            x = -2.7 + i * 0.45
            sl.add(cyl(0.05, 0.05, 4.2, 6), 'iron', 'root', mtx((x, -0.55, 2.4)))
        for z in (1.0, 2.2, 3.4):
            _pas(sl, -2.8, 2.8, 0.08, 0.08, 0.01, 'iron', -0.55, z)
        wrota(4.4, True)
        miejsca = [('obronca_01', (-1.6, 0.8, 7.15)), ('obronca_02', (0.0, 0.8, 7.15)), ('obronca_03', (1.6, 0.8, 7.15))]
    return miejsca


# ------------------------------------------------------------------ wieża (narożna, tylna albo przy bramie; środek w 0,0)

def naroznik(sl, poz, uszkodzenia=False):
    return _z_uszkodzeniami(sl, plan_wiezy(poz) if uszkodzenia else None, lambda: _naroznik(sl, poz))


def _naroznik(sl, poz):
    if poz == 1:  # palisada: wiązka grubych pali na rogu, bez miejsca dla obrońcy
        for i in range(9):
            a = 2 * math.pi * i / 9
            r, h = 0.3, 3.4 + 0.3 * math.sin(i * 1.7)
            p = V(math.cos(a) * 0.75, math.sin(a) * 0.75, 0)
            _pal(sl, p.x, p.y, r, h, 'wood')
            sl.add(cyl(r, 0.0, 0.5, 8), 'wood_light', 'root', mtx(p + V(0, 0, h + 0.25)))
        sl.add(cyl(1.08, 1.08, 0.2, 12), 'wood_dark', 'root', mtx((0, 0, 1.4)))
        sl.add(cyl(1.08, 1.08, 0.2, 12), 'wood_dark', 'root', mtx((0, 0, 2.6)))
        return []
    if poz == 2:
        for x in (-1.1, 1.1):
            for y in (-1.1, 1.1):
                _pal(sl, x, y, 0.16, 4.4, 'wood_dark')
        sl.add(box(2.9, 2.9, 0.16, 0.03), 'wood_light', 'root', mtx((0, 0, 4.2)))
        for (x, y, w, d) in ((0, -1.4, 2.9, 0.1), (0, 1.4, 2.9, 0.1), (-1.4, 0, 0.1, 2.9), (1.4, 0, 0.1, 2.9)):
            sl.add(box(w, d, 0.8, 0.02), 'wood', 'root', mtx((x, y, 4.65)))
        for x in (-1.3, 1.3):
            for y in (-1.3, 1.3):
                sl.add(cyl(0.08, 0.08, 1.6, 6), 'wood_dark', 'root', mtx((x, y, 5.1)))
        _dach(sl, 0, 0, 5.85, 2.2, 1.6, GONT, boki=4, rzedy=4, obrot=45, iglica=False)
        return [('obronca_01', (0.0, 0.0, 4.3))]
    if poz == 3:  # mała wieża z polnego kamienia z drewnianym daszkiem
        rng = random.Random(31)
        _wieza(sl, rng, 2.2, 2.05, 0.0, 4.8, wys_rzedu=0.9, mat=('stone_dark', 'stone', 'stone_dark'))
        sl.add(cyl(2.25, 2.25, 0.16, 12), 'wood_light', 'root', mtx((0, 0, 4.88)))
        for i in range(6):
            a = 2 * math.pi * i / 6
            sl.add(cyl(0.09, 0.09, 1.6, 6), 'wood_dark', 'root', mtx((math.cos(a) * 1.9, math.sin(a) * 1.9, 5.7)))
        _dach(sl, 0, 0, 6.5, 2.5, 1.7, GONT, boki=8, rzedy=4, iglica=False)
        return [('obronca_01', (0.0, 0.0, 4.98))]
    if poz == 4:
        _wieza(sl, random.Random(41), 2.45, 2.4, 0.0, 6.2)
        sl.add(cyl(2.55, 2.55, 0.2, 18), 'stone_light', 'root', mtx((0, 0, 6.3)))
        for i in range(10):
            a = 2 * math.pi * i / 10
            sl.add(box(0.75, 0.5, 0.85, 0.06), 'stone', 'root', mtx((math.cos(a) * 2.25, math.sin(a) * 2.25, 6.8), (0, 0, math.degrees(a) + 90)))
        return [('obronca_01', (-0.8, 0.0, 6.42)), ('obronca_02', (0.8, 0.0, 6.42))]
    # poz 5
    _wieza(sl, random.Random(51), 3.15, 2.8, 0.0, 7.5, wys_rzedu=0.75)
    sl.add(cyl(3.0, 3.0, 0.25, 18), 'stone_light', 'root', mtx((0, 0, 7.6)))
    for i in range(4):
        a = 2 * math.pi * i / 4 + math.pi / 4
        sl.add(box(0.4, 0.4, 2.4, 0.04), 'stone_dark', 'root', mtx((math.cos(a) * 2.4, math.sin(a) * 2.4, 8.9)))
        sl.add(box(0.36, 0.06, 0.36, 0.02), 'rune', 'root', mtx((math.cos(a) * 2.95, math.sin(a) * 2.95, 3.5), (0, 45, math.degrees(a) + 90)))
    _dach(sl, 0, 0, 10.1, 3.3, 3.3, boki=18, rzedy=7)
    sl.add(cyl(0.05, 0.05, 1.6, 6), 'iron', 'root', mtx((0, 0, 14.0)))
    sl.add(box(0.9, 0.04, 0.55, 0.01), 'banner', 'root', mtx((0.47, 0, 14.4)))
    return [('obronca_01', (-0.9, 0.0, 7.75)), ('obronca_02', (0.9, 0.0, 7.75))]
