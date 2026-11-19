"""MAPA – USZKODZENIA murów, bramy i wież (widoczne skutki ataku).

4 STANY (wybierane w grze z wytrzymałości elementu, patrz STAN_Z_WYTRZYMALOSCI):
  0 cały              (100–70%)
  1 lekko uszkodzony  (70–40%)  pęknięcia, strącone blanki, kamienie pod murem
  2 mocno uszkodzony  (40–1%)   dziury, sterty gruzu, płonące szczątki (dym: cząsteczki w Godocie)
  3 wyłom             (0%)      dziura do ziemi – wrogowie mogą tędy wejść

Jak to działa: model elementu NIE jest dzielony na osobne pliki. Jeden .glb na etap wyglądu ma
główną siatkę + WARSTWY (dzieci głównego węzła), które Godot chowa i pokazuje:
  <element>_znika_<k>    – części, które odpadają: widoczne, gdy stan < k
  <element>_pojawia_<k>  – gruz, pęknięcia, ogień: widoczne, gdy stan >= k
  <element>_pokaz_<a>_<b> – widoczne tylko, gdy a <= stan < b (np. pęknięcie na kawałku muru,
                           który przy większym uszkodzeniu odpada)
Dym i ogień w ruchu dodaje Godot (cząsteczki) w miejscach uszkodzeń – modele mają tylko płonące szczątki.
Miejsca obrońców ('obronca_NN') leżące na odpadającej części są dziećmi warstwy znika_<k>,
więc znikają razem z nią. Pusty węzeł 'wylom' (w warstwie pojawia_3) to środek wyłomu.

Które części odpadają, decyduje PLAN: kilka miejsc uszkodzeń na długości muru, każde z profilem
„wyszczerbienia” od góry (im głębsze, tym większy stan). Plan jest stały (ziarno), więc dany mur
zawsze psuje się tak samo.
"""
import math
import random
from collections import defaultdict
from contextlib import contextmanager

import bmesh

from kit import V, Slot, box, cyl, ico, rock, mtx, seg

STANY = {0: 'cały', 1: 'lekko uszkodzony', 2: 'mocno uszkodzony', 3: 'wyłom'}
# stan = pierwszy, dla którego wytrzymałość >= próg (wyłom tylko przy 0)
STAN_Z_WYTRZYMALOSCI = [(0.70, 0), (0.40, 1), (0.0001, 2), (0.0, 3)]

PALETA = {
    'soot': ('#2e2925', 0.98), 'crack': ('#241f1b', 0.95),
    'smoke': ('#8d8a86', 1.0), 'smoke_dark': ('#5f5b57', 1.0),
    'ember': ('#ff3d00', 0.5, 0.0, 3.0),
}

NIE_GRUZ = ('rune', 'banner', 'gold', 'fire', 'fire_core', 'iron', 'soot', 'crack')


class Warstwy:
    """Zamiennik Slotu: części trafiają do warstwy głównej ('') albo do warstw uszkodzeń.
    `klasyfikator(tbm, mat)` (jeśli ustawiony) sam przydziela części do warstw znika_<k>."""

    def __init__(self, nazwa):
        self.nazwa = nazwa
        self.sloty = {}
        self.cel = ''
        self.klasyfikator = None
        self.puste = []              # dodatkowe puste węzły: (nazwa, pozycja)
        self.warstwa_pustego = {}    # nazwa pustego węzła -> warstwa (rodzic)
        self.slot('')

    def slot(self, w):
        if w not in self.sloty:
            self.sloty[w] = Slot(self.nazwa + (f'_{w}' if w else ''))
        return self.sloty[w]

    def add(self, tbm, mat, bone, M=None):
        if M is not None:
            bmesh.ops.transform(tbm, matrix=M, verts=tbm.verts)
        w = self.cel
        if not w and self.klasyfikator is not None:
            w = self.klasyfikator(tbm, mat) or ''
        self.slot(w).add(tbm, mat, bone)

    @contextmanager
    def warstwa(self, w):
        poprzednia, self.cel = self.cel, w
        try:
            yield
        finally:
            self.cel = poprzednia


def widoczna(nazwa_warstwy, stan):
    """Czy warstwa (po nazwie węzła) jest widoczna w danym stanie."""
    if '_pokaz_' in nazwa_warstwy:
        return int(nazwa_warstwy[-3]) <= stan < int(nazwa_warstwy[-1])
    k = int(nazwa_warstwy[-1])
    return stan < k if '_znika_' in nazwa_warstwy else stan >= k


class Plan:
    """Plan uszkodzeń elementu (mur, brama, wieża).
    gora – wysokość szczytu (z blankami), pomost – wysokość pomostu,
    lico – y zewnętrznej ściany (liczba albo funkcja x -> y, np. dla okrągłej wieży), lico_tyl – y ściany
    od strony miasta (opcjonalnie), stopa – (y_przod, y_tyl) podstawy (gdzie leży gruz).
    Miejsca uszkodzeń:  wolne=[(a, b), ...] – losowane na długości muru,  albo  dziury=[...] podane wprost:
    (stan, x, pół-szerokość, głębokość od góry[, ostrość profilu]), punkty=[x, ...] – gdzie rysy i kamyki.
    peknięcia=False – bez rys i osmaleń (drewno)."""

    def __init__(self, gora, pomost, lico, stopa, seed=1, lico_tyl=None, wolne=None, dziury=None, punkty=(),
                 wylom_x=None, pekniecia=True, ognie=2):
        self.gora, self.pomost, self.lico, self.stopa = gora, pomost, lico, stopa
        self.lico_tyl = lico_tyl
        self.seed = seed
        self.pekniecia, self.ognie = pekniecia, ognie
        self.usuniete = []  # (stan, środek, rozmiar, materiał)
        if dziury is not None:
            self.dziury = [d if len(d) == 5 else (*d, 2) for d in dziury]
            self.punkty = list(punkty)
            if wylom_x is not None:
                self.x_wylomu = wylom_x
            return
        rng = random.Random(seed * 7919 + 13)
        dl = sum(b - a for a, b in wolne)
        n_lekkie = max(1, round(dl / 12))
        n_ciezkie = max(1, round(dl / 20))
        n = n_lekkie + n_ciezkie
        miejsca = []
        for i in range(n):
            s = (i + 0.5 + rng.uniform(-0.2, 0.2)) * dl / n
            for a, b in wolne:
                if s <= b - a:
                    miejsca.append(min(max(a + s, a + 2.6), b - 2.6))
                    break
                s -= b - a
        ciezkie = set(rng.sample(range(n), n_ciezkie))
        wylom = rng.choice(sorted(ciezkie))
        szczyt = gora - pomost  # wysokość blanków nad pomostem
        self.dziury = []    # (stan, x, pół-szerokość, głębokość od góry, ostrość profilu)
        self.punkty = []    # x miejsc uszkodzeń (rysy, kamyki)
        for i, x in enumerate(miejsca):
            if i in ciezkie:
                self.dziury.append((1, x, rng.uniform(0.9, 1.3), szczyt + rng.uniform(0.2, 0.6), 2))
                self.dziury.append((2, x, rng.uniform(1.9, 2.4), gora * rng.uniform(0.45, 0.6), 2))
            else:
                self.dziury.append((1, x, rng.uniform(1.1, 1.5), szczyt + rng.uniform(0.5, 1.0), 2))
                self.dziury.append((2, x, rng.uniform(1.4, 1.8), szczyt + rng.uniform(1.2, 1.8), 2))
            self.punkty.append(x)
            if i == wylom:
                self.dziury.append((3, x, 3.1, gora + 2.2, 2))
                self.x_wylomu = x

    def stan_usuniecia(self, c):
        """Od którego stanu część o środku c odpada (None = nie odpada nigdy)."""
        wynik = None
        szum = random.Random(f'{self.seed}|{c.x:.2f}|{c.z:.2f}').uniform(-0.22, 0.22)
        for k, x0, hw, gl, ostr in self.dziury:
            t = abs(c.x - x0) / hw
            if t >= 1.0:
                continue
            if c.z > self.gora - gl * (1 - t ** ostr) + szum:
                wynik = k if wynik is None else min(wynik, k)
        return wynik

    def klasyfikator(self, tbm, mat):
        vs = [v.co for v in tbm.verts]
        lo = V((min(v.x for v in vs), min(v.y for v in vs), min(v.z for v in vs)))
        hi = V((max(v.x for v in vs), max(v.y for v in vs), max(v.z for v in vs)))
        c = (lo + hi) / 2
        k = self.stan_usuniecia(c)
        if k is None:
            return ''
        self.usuniete.append((k, c, hi - lo, mat))
        return f'znika_{k}'

    # ---------------------------------------------------------------- co się pojawia

    def _na_licu(self, sl, k, bm, mat, M):
        """Dodaje element na licu muru (pęknięcie, osmalenie), widoczny od stanu k do chwili,
        gdy ten kawałek muru odpada."""
        bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
        vs = [v.co for v in bm.verts]
        c = sum(vs, V((0, 0, 0))) / len(vs)
        koniec = self.stan_usuniecia(V((c.x, c.y, c.z + 0.15)))
        if koniec is not None and koniec <= k:
            bm.free()
            return
        with sl.warstwa(f'pojawia_{k}' if koniec is None else f'pokaz_{k}_{koniec}'):
            sl.add(bm, mat, 'root')

    def dodaj_skutki(self, sl):
        rng = random.Random(self.seed * 31 + 5)
        kopce = defaultdict(float)   # wysokość sterty gruzu w kratce 0.7 m
        y0, y1 = self.stopa

        def poloz(x, y):
            klucz = (round(x / 0.7), round(y / 0.7))
            return klucz, kopce[klucz]

        ogniska = defaultdict(list)  # stan -> [(x, y, z)] miejsca na płonące szczątki
        for k, c, d, mat in self.usuniete:
            if mat in NIE_GRUZ:
                continue
            drewno = mat.startswith('wood')
            ile = 1 if d.x * d.y * d.z < 0.8 else 2
            for _ in range(ile):
                los = rng.random()
                if k == 3 and los < 0.5:
                    y = rng.uniform(y0 + 0.2, y1 - 0.2)            # gruz w samym wyłomie
                elif los < 0.75:
                    y = y0 - rng.uniform(0.3, 2.6)                  # przed murem (strona wroga)
                else:
                    y = y1 + rng.uniform(0.3, 1.8)                  # za murem
                x = c.x + rng.uniform(-0.8, 0.8)
                klucz, z = poloz(x, y)
                with sl.warstwa(f'pojawia_{k}'):
                    if drewno:
                        dl = min(max(d.x, d.z) * rng.uniform(0.4, 0.8), 1.6)
                        a = rng.uniform(0, 180)
                        sl.add(box(dl, 0.16, 0.12, 0.02), rng.choice(('wood_dark', 'wood', 'soot')), 'root',
                               mtx((x, y, z + 0.07), (rng.uniform(-12, 12), rng.uniform(-8, 8), a)))
                        kopce[klucz] += 0.08
                    else:
                        s = rng.uniform(0.35, 0.62)
                        h = s * rng.uniform(0.6, 0.9)
                        sl.add(rock(s * rng.uniform(0.9, 1.3), s, h, rng.randint(0, 9999), rough=0.12, bevel=0.15),
                               rng.choice(('stone', 'stone_dark', 'stone_dark', 'stone_light')), 'root',
                               mtx((x, y, z + h * 0.4), (rng.uniform(-15, 15), rng.uniform(-15, 15), rng.uniform(0, 360))))
                        kopce[klucz] += h * 0.55
                if y < y0:
                    ogniska[k].append((x, y, kopce[klucz]))
        # drobne kamyki pod murem już przy lekkim uszkodzeniu
        for x in self.punkty:
            with sl.warstwa('pojawia_1'):
                for _ in range(5):
                    s = rng.uniform(0.15, 0.3)
                    sl.add(rock(s, s, s * 0.7, rng.randint(0, 9999), rough=0.15), rng.choice(('stone', 'stone_dark')), 'root',
                           mtx((x + rng.uniform(-1.5, 1.5), y0 - rng.uniform(0.2, 1.4), s * 0.3)))
        self._pekniecia(sl, rng)
        self._ogien(sl, rng, ogniska)

    def _pekniecia(self, sl, rng):
        """Ciemne, łamane rysy na licu pod miejscami uszkodzeń (stan 1), większe rysy i
        osmalenia przy dziurach (stan 2)."""
        if not self.pekniecia:
            return
        lica = [(self.lico, -1)] + ([(self.lico_tyl, 1)] if self.lico_tyl is not None else [])
        rozrzut = getattr(self, 'rozrzut', 1.2)
        for x in self.punkty:
            for k, ile, dl_seg in ((1, 2, 0.45), (2, 3, 0.6)):
                gl = [g for kk, xx, hw, g, o in self.dziury if kk == k and abs(xx - x) < hw]
                if not gl:
                    continue
                gl = max(gl)
                for lico, zn in lica:
                    y_lica = lico if callable(lico) else (lambda _x, _y=lico: _y)
                    for j in range(ile):
                        p = V((x + rng.uniform(-rozrzut, rozrzut), 0, self.gora - gl - rng.uniform(0.0, 0.3)))
                        kat = rng.choice((-1, 1)) * rng.uniform(15, 40)
                        for s in range(rng.randint(3, 5)):
                            if p.z < 0.4:
                                break
                            kat = -kat * rng.uniform(0.6, 1.2)
                            r = math.radians(kat)
                            q = p + V((math.sin(r), 0, -math.cos(r))) * dl_seg * rng.uniform(0.7, 1.2)
                            p.y = q.y = y_lica((p.x + q.x) / 2) + zn * 0.05
                            self._na_licu(sl, k, box(0.08, 0.06, (q - p).length + 0.04, 0.01), 'crack', seg(p, q, (0, 1, 0)))
                            p = q
                    if k == 2:  # osmalenia wokół dziury
                        for _ in range(3):
                            w = rng.uniform(0.5, 0.9)
                            xs = x + rng.uniform(-rozrzut * 1.8, rozrzut * 1.8)
                            self._na_licu(sl, 2, box(w, 0.04, w * 0.6, 0.01), 'soot',
                                          mtx((xs, y_lica(xs) + zn * 0.04, self.gora - gl - rng.uniform(0.3, 1.0)),
                                              (0, rng.uniform(-30, 30), 0)))

    def _ogien(self, sl, rng, ogniska):
        """Płonące szczątki na stertach gruzu przed murem (stan 2+) (dym dodaje Godot)."""
        for k in (2, 3):
            miejsca = ogniska.get(k, [])
            rng.shuffle(miejsca)
            for (x, y, z) in miejsca[:self.ognie if k == 2 else 1]:
                with sl.warstwa(f'pojawia_{k}'):
                    for i in range(3):
                        a = i * 2.1 + rng.uniform(0, 0.5)
                        q = V((x + math.cos(a) * 0.18, y + math.sin(a) * 0.18, z))
                        h = rng.uniform(0.55, 0.85)
                        sl.add(cyl(0.16, 0.0, h, 6), 'fire', 'root', mtx(q + V((0, 0, h / 2))))
                    sl.add(cyl(0.1, 0.0, 0.5, 6), 'fire_core', 'root', mtx((x, y, z + 0.25)))
                    for _ in range(4):
                        sl.add(ico(0.05, 0), 'ember', 'root', mtx((x + rng.uniform(-0.5, 0.5), y + rng.uniform(-0.5, 0.5), z + rng.uniform(0.6, 1.5))))

    def miejsce_obroncy(self, nazwa, p, sl):
        """Przypina miejsce obrońcy do warstwy, z którą odpada (np. zawalony pomost)."""
        k = self.stan_usuniecia(V((p[0], p[1], self.pomost + 0.06)))
        if k is not None:
            sl.warstwa_pustego[nazwa] = f'znika_{k}'

    def dodaj_wylom(self, sl):
        if hasattr(self, 'x_wylomu'):
            sl.puste.append(('wylom', (self.x_wylomu, sum(self.stopa) / 2, 0.0)))
            sl.warstwa_pustego['wylom'] = 'pojawia_3'
