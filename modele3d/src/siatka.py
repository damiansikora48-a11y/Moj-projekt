"""SIATKA FUZJI: role, żywioły i nazwy wszystkich pól (rola × żywioł).

Reguła fuzji: rola od jednego rodzica, żywioł od drugiego. A + B = B + A (jedna fuzja na parę).
Zmiana nazwy pola: popraw ją tutaj (i w projekt/zasady_gry.md).
"""

ROLE = {
    'wojownik': 'Wojownik',   # wręcz, przy bramie
    'kolos': 'Kolos',         # tank, blokuje wyłomy
    'mag': 'Mag',             # czary z dystansu, na murach
    'strzelec': 'Strzelec',   # dystans fizyczny, na murach
}

ZYWIOLY = ('stal', 'kamien', 'ogien', 'natura')

NAZWY = {
    ('wojownik', 'stal'): 'Żołnierz',
    ('wojownik', 'kamien'): 'Kamienny Rycerz',
    ('wojownik', 'ogien'): 'Płomienny Rycerz',
    ('wojownik', 'natura'): 'Rycerz Cierni',
    ('kolos', 'stal'): 'Stalowy Kolos',
    ('kolos', 'kamien'): 'Golem',
    ('kolos', 'ogien'): 'Magmowy Golem',
    ('kolos', 'natura'): 'Kamienny Ent',
    ('mag', 'stal'): 'Mag Bitewny',
    ('mag', 'kamien'): 'Geomanta',
    ('mag', 'ogien'): 'Mag ognia',
    ('mag', 'natura'): 'Druid',
    ('strzelec', 'stal'): 'Kusznik',
    ('strzelec', 'kamien'): 'Kryształowy Łucznik',
    ('strzelec', 'ogien'): 'Ognisty Łucznik',
    ('strzelec', 'natura'): 'Leśny Łucznik',
}


def nazwa_pola(rola, zywiol):
    return NAZWY.get((rola, zywiol), f'{ROLE[rola]} ({zywiol})')
