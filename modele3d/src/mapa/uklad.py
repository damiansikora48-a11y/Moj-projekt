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

# --- poziomy ulepszeń murów i bramy (łatwo dodać kolejne – patrz mapa/mury.py)
POZIOMY = {
    1: {'nazwa': 'Palisada', 'opis': 'pale z zaostrzonymi końcami, drewniany pomost'},
    2: {'nazwa': 'Wzmocniona palisada', 'opis': 'grubsze podwójne pale, okucia, kamienny fundament, pomost z barierką'},
    3: {'nazwa': 'Mur kamienny', 'opis': 'mur z kamiennych bloków z blankami'},
    4: {'nazwa': 'Warownia', 'opis': 'grubszy i wyższy mur, przypory, sztandary, runy, kosze z ogniem'},
}

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
    {'id': 'D1', 'srodek': (0.0, 8.5), 'rozmiar': (9.0, 6.0), 'budynek': None, 'uwagi': 'największa – np. główna siedziba'},
    {'id': 'D2', 'srodek': (-10.5, -6.5), 'rozmiar': (6.0, 6.0), 'budynek': None, 'uwagi': ''},
    {'id': 'D3', 'srodek': (-10.5, 1.0), 'rozmiar': (6.0, 6.0), 'budynek': None, 'uwagi': ''},
    {'id': 'D4', 'srodek': (-9.0, 7.5), 'rozmiar': (5.0, 4.0), 'budynek': None, 'uwagi': 'obok stawu z wodospadem'},
    {'id': 'D5', 'srodek': (10.5, -6.5), 'rozmiar': (6.0, 6.0), 'budynek': None, 'uwagi': ''},
    {'id': 'D6', 'srodek': (10.5, 1.0), 'rozmiar': (6.0, 6.0), 'budynek': None, 'uwagi': ''},
    {'id': 'D7', 'srodek': (10.5, 8.0), 'rozmiar': (6.0, 5.0), 'budynek': None, 'uwagi': ''},
    {'id': 'D8', 'srodek': (-4.5, -8.5), 'rozmiar': (4.0, 3.5), 'budynek': None, 'uwagi': 'mała, przy bramie'},
    {'id': 'D9', 'srodek': (4.5, -8.5), 'rozmiar': (4.0, 3.5), 'budynek': None, 'uwagi': 'mała, przy bramie'},
]
STAW = {'srodek': (-14.0, 11.2), 'promien': 1.8}

# --- strefy, z których atakujący wypuszcza wojska (prostokąty x0, x1, y0, y1)
STREFY_ATAKU = {
    'przod': (-20.0, 20.0, -42.0, -24.0),
    'lewy': (-48.0, -28.0, -12.0, 8.0),
    'prawy': (28.0, 48.0, -12.0, 8.0),
}


def do_godota(x, y, z=0.0):
    return [round(x, 3), round(z, 3), round(-y, 3)]
