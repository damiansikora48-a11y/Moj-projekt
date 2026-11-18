"""MAPA – UKŁAD MIASTA: wymiary, mury, brama, narożniki, działki pod budynki, strefy ataku.

Tu decydujesz, GDZIE co stoi. Współrzędne w metrach, układ Blendera:
  X – w prawo, Y – do tyłu (w stronę góry), Z – w górę. Przód miasta (brama) jest od strony -Y.
Do Godota (export/mapa/uklad.json) współrzędne są przeliczane: Godot = (x, z, -y).

Nowy budynek w przyszłości = wpis w DZIALKI (zajmij wolną działkę albo dodaj nową).
"""

# --- wnętrze miasta (linia murów)
SZER = 36.0     # odległość między murem lewym a prawym
GLEB = 28.0     # od muru przedniego do góry
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
# wieże na przednich narożnikach: poziom = wyższy z dwóch sąsiednich murów
NAROZNIKI = [
    {'element': 'naroznik', 'srodek': (-SZER / 2, PRZOD_Y), 'obrot': 0, 'sasiedzi': ['lewy', 'przod']},
    {'element': 'naroznik', 'srodek': (SZER / 2, PRZOD_Y), 'obrot': 0, 'sasiedzi': ['prawy', 'przod']},
]

# --- działki pod budynki (środek x, y; rozmiar szer x gł). 'budynek': None = wolna.
PLAC = {'srodek': (0.0, 0.5), 'promien': 4.5}  # plac centralny ze studnią (nie do zabudowy)
DZIALKI = [
    {'id': 'D1', 'srodek': (0.0, 8.75), 'rozmiar': (14.0, 8.5), 'budynek': 'budynek_glowny',
     'uwagi': 'skalna półka (podwyższenie) przy ścianie góry ze schodami – budynek główny z wolnym miejscem wokół',
     'podwyzszenie': 1.6},
    {'id': 'D2', 'srodek': (-10.5, -6.5), 'rozmiar': (6.0, 6.0), 'budynek': None, 'uwagi': ''},
    {'id': 'D3', 'srodek': (-10.5, 1.0), 'rozmiar': (6.0, 6.0), 'budynek': None, 'uwagi': ''},
    {'id': 'D4', 'srodek': (-9.75, 7.5), 'rozmiar': (4.5, 4.0), 'budynek': None, 'uwagi': 'obok stawu z wodospadem'},
    {'id': 'D5', 'srodek': (10.5, -6.5), 'rozmiar': (6.0, 6.0), 'budynek': None, 'uwagi': ''},
    {'id': 'D6', 'srodek': (10.5, 1.0), 'rozmiar': (6.0, 6.0), 'budynek': None, 'uwagi': ''},
    {'id': 'D7', 'srodek': (10.75, 8.0), 'rozmiar': (5.5, 5.0), 'budynek': None, 'uwagi': ''},
    {'id': 'D8', 'srodek': (-4.5, -8.5), 'rozmiar': (4.0, 3.5), 'budynek': None, 'uwagi': 'mała, przy bramie'},
    {'id': 'D9', 'srodek': (4.5, -8.5), 'rozmiar': (4.0, 3.5), 'budynek': None, 'uwagi': 'mała, przy bramie'},
]
# budynek główny: 20 poziomów, każdy coś zmienia (mapa/budynek_glowny.py)
BUDYNEK_GLOWNY = {'dzialka': 'D1', 'poziomy': 20}
STAW = {'srodek': (-14.0, 11.2), 'promien': 1.8}
# duży wodospad na górze (po prawej, za murem) i jezioro z rzeką
JEZIORO = {'srodek': (41.0, 4.0), 'promien': 3.6}

# --- strefy, z których atakujący wypuszcza wojska (prostokąty x0, x1, y0, y1)
STREFY_ATAKU = {
    'przod': (-20.0, 20.0, -42.0, -24.0),
    'lewy': (-48.0, -28.0, -12.0, 8.0),
    'prawy': (28.0, 48.0, -18.0, 0.0),  # z tyłu po prawej jest jezioro pod wodospadem
}


def do_godota(x, y, z=0.0):
    return [round(x, 3), round(z, 3), round(-y, 3)]
