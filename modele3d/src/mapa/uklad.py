"""MAPA – UKŁAD MIASTA: wymiary, mury, brama, narożniki, działki pod budynki, strefy ataku.

Tu decydujesz, GDZIE co stoi. Współrzędne w metrach, układ Blendera:
  X – w prawo, Y – do tyłu (w stronę góry), Z – w górę. Przód miasta (brama) jest od strony -Y.
Do Godota (export/mapa/uklad.json) współrzędne są przeliczane: Godot = (x, z, -y).

Nowy budynek w przyszłości = wpis w DZIALKI (zajmij wolną działkę albo dodaj nową).
"""

# --- wnętrze miasta (linia murów)
SZER = 52.0     # odległość między murem lewym a prawym
GLEB = 40.0     # od muru przedniego do góry
PRZOD_Y = -GLEB / 2   # linia muru przedniego
BRAMA_SZER = 6.0      # szerokość prześwitu bramy w murze przednim

# --- ETAPY WYGLĄDU murów, bramy i wież (modele są robione dla etapów – patrz mapa/mury.py)
ETAPY = {
    1: {'nazwa': 'Palisada', 'opis': 'pale z zaostrzonymi końcami, bez pomostu – brak miejsc dla obrońców'},
    2: {'nazwa': 'Mur drewniany', 'opis': 'grubsze podwójne pale, okucia, kamienny fundament, pomost – mało obrońców'},
    3: {'nazwa': 'Słaby mur kamienny', 'opis': 'nieobrobione kamienie, drewniane blanki i pomost'},
    4: {'nazwa': 'Lepszy mur kamienny', 'opis': 'mur z ciosanych bloków z kamiennymi blankami'},
    5: {'nazwa': 'Warownia', 'opis': 'grubszy i wyższy mur, przypory, sztandary, runy, kosze z ogniem'},
}

# --- POZIOMY ULEPSZEŃ w grze (osobno dla każdego muru i dla bramy): poziom -> etap wyglądu.
# Wygląd zmienia się co 3 poziomy. Zmiana liczby poziomów albo progów: tylko tutaj.
LICZBA_POZIOMOW = 15
POZIOMY = {p: (p + 2) // 3 for p in range(1, LICZBA_POZIOMOW + 1)}

# --- elementy do ulepszania (każdy osobno)
MURY = {
    'lewy': {'element': 'mur_bok', 'srodek': (-SZER / 2, 0.0), 'obrot': -90, 'dlugosc': GLEB},
    'przod': {'element': 'mur_front', 'srodek': (0.0, PRZOD_Y), 'obrot': 0, 'dlugosc': SZER, 'brama_szer': BRAMA_SZER},
    'prawy': {'element': 'mur_bok', 'srodek': (SZER / 2, 0.0), 'obrot': 90, 'dlugosc': GLEB},
}
BRAMA = {'element': 'brama', 'srodek': (0.0, PRZOD_Y), 'obrot': 0}
# 6 wież, każda ulepszana OSOBNO (poziomy 1–15, jak mury i brama); wszystkie mają ten sam wygląd etapów
WIEZA_BRAMY_X = BRAMA_SZER / 2 + 3.2   # odległość wież przy bramie od środka bramy
WIEZE = [
    {'id': 'wieza_przod_lewa', 'element': 'wieza', 'srodek': (-SZER / 2, PRZOD_Y), 'obrot': 0, 'opis': 'przedni lewy narożnik'},
    {'id': 'wieza_przod_prawa', 'element': 'wieza', 'srodek': (SZER / 2, PRZOD_Y), 'obrot': 0, 'opis': 'przedni prawy narożnik'},
    {'id': 'wieza_tyl_lewa', 'element': 'wieza', 'srodek': (-SZER / 2, GLEB / 2 - 3.0), 'obrot': 0, 'opis': 'koniec lewego muru przy górze'},
    {'id': 'wieza_tyl_prawa', 'element': 'wieza', 'srodek': (SZER / 2, GLEB / 2 - 3.0), 'obrot': 0, 'opis': 'koniec prawego muru przy górze'},
    {'id': 'wieza_brama_lewa', 'element': 'wieza', 'srodek': (-WIEZA_BRAMY_X, PRZOD_Y), 'obrot': 0, 'opis': 'po lewej stronie bramy'},
    {'id': 'wieza_brama_prawa', 'element': 'wieza', 'srodek': (WIEZA_BRAMY_X, PRZOD_Y), 'obrot': 0, 'opis': 'po prawej stronie bramy'},
]

# --- działki pod budynki (środek x, y; rozmiar szer x gł). 'budynek': None = wolna.
PLAC = {'srodek': (0.0, 2.0), 'promien': 5.0}  # plac centralny ze studnią (nie do zabudowy)
DZIALKI = [
    {'id': 'D1', 'srodek': (0.0, GLEB / 2 - 1.0 - 4.25), 'rozmiar': (14.0, 8.5), 'budynek': 'budynek_glowny',
     'uwagi': 'skalna półka (podwyższenie) przy ścianie góry ze schodami – budynek główny z wolnym miejscem wokół',
     'podwyzszenie': 1.6},
    {'id': 'D2', 'srodek': (-15.0, -10.0), 'rozmiar': (7.0, 7.0), 'budynek': 'kuznia', 'uwagi': 'Kuźnia', 'obrot': 90},
    {'id': 'D3', 'srodek': (-15.0, 0.0), 'rozmiar': (7.0, 7.0), 'budynek': 'budynek_fuzji', 'uwagi': 'Budynek fuzji', 'obrot': 90},
    {'id': 'D4', 'srodek': (-15.0, 9.5), 'rozmiar': (6.5, 6.0), 'budynek': None, 'uwagi': ''},
    {'id': 'D5', 'srodek': (15.0, -10.0), 'rozmiar': (7.0, 7.0), 'budynek': None, 'uwagi': ''},
    {'id': 'D6', 'srodek': (15.0, 0.0), 'rozmiar': (7.0, 7.0), 'budynek': 'koszary', 'uwagi': 'Koszary', 'obrot': -90},
    {'id': 'D7', 'srodek': (15.0, 9.5), 'rozmiar': (6.5, 6.0), 'budynek': None, 'uwagi': ''},
    {'id': 'D8', 'srodek': (-6.5, -13.5), 'rozmiar': (5.0, 4.0), 'budynek': None, 'uwagi': 'mała, przy bramie'},
    {'id': 'D9', 'srodek': (6.5, -13.5), 'rozmiar': (5.0, 4.0), 'budynek': None, 'uwagi': 'mała, przy bramie'},
    {'id': 'D10', 'srodek': (-12.0, 16.0), 'rozmiar': (5.0, 4.0), 'budynek': None, 'uwagi': 'obok półki budynku głównego'},
    {'id': 'D11', 'srodek': (12.0, 16.0), 'rozmiar': (5.0, 4.0), 'budynek': None, 'uwagi': 'obok półki budynku głównego'},
]
# 'obrot' działki: obrót budynku (stopnie wokół osi pionowej) – przodem do placu
# budynek główny: 20 poziomów, każdy coś zmienia (mapa/budynek_glowny.py)
BUDYNEK_GLOWNY = {'dzialka': 'D1', 'poziomy': 20}
# budynki na działkach (mapa/budynki.py): każdy 20 poziomów; działka -> budynek w DZIALKI ('budynek')
POZIOMY_BUDYNKOW = 20
# tablica ogłoszeń na placu przy studni (aktualizacje, wydarzenia) – od strony bramy, obok drogi
TABLICA = {'srodek': (2.7, -0.9), 'obrot': -15}
STAW = {'srodek': (-20.5, 16.5), 'promien': 1.9}
# duży wodospad na górze (po prawej, za murem) i jezioro z rzeką
JEZIORO = {'srodek': (41.0, 4.0), 'promien': 3.6}

# --- strefy, z których atakujący wypuszcza wojska (prostokąty x0, x1, y0, y1)
STREFY_ATAKU = {
    'przod': (-26.0, 26.0, -52.0, -30.0),
    'lewy': (-58.0, -34.0, -16.0, 6.0),
    'prawy': (34.0, 58.0, -24.0, -4.0),  # z tyłu po prawej jest jezioro pod wodospadem
}


def do_godota(x, y, z=0.0):
    return [round(x, 3), round(z, 3), round(-y, 3)]
