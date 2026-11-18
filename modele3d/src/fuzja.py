"""FUZJE: narzędzia do łączenia jednostek, szkice automatyczne i Przebudzenie.

Reguła (patrz siatka.py i projekt/zasady_gry.md): ROLA od jednego rodzica, ŻYWIOŁ od drugiego.

Szkic automatyczny (auto_fuzja):
  od rodzica-ROLI     – proporcje, wszystkie części, chód i RUCH ataku (części pasują idealnie)
  od rodzica-ŻYWIOŁU  – przepis żywiołu z zywioly/: barwy, przebarwienie materiałów,
                        świecenie, ozdoby na barkach (slot Element) i EFEKT ataku
Fuzja ręczna (plik w fuzje/) używa polacz_szkielet / polacz_palete i własnych części.

Przebudzenie (przebudz): wariant dowolnej fuzji – złocone metale, mocniejsze świecenie,
aureola za głową i krąg run pod stopami (slot Aura). Robi się automatycznie.
"""
import math

from kit import lerp, V, box, cyl, ico, mtx, frame

PODSTAWOWE_SLOTY = ('Head', 'Headgear', 'Body', 'Back', 'Arms', 'Legs', 'Weapon', 'Offhand')


def polacz_szkielet(a, b, t, **korekty):
    """Proporcje pośrednie: t=0 -> jak A, t=1 -> jak B. Korekty nadpisują wybrane wartości."""
    sk = {k: lerp(a[k], b[k], t) for k in a if k in b}
    sk.update(korekty)
    return sk


def polacz_palete(a, b, **dodatki):
    """Kolory obu rodziców (przy tej samej nazwie wygrywa B) + własne dodatki fuzji."""
    pal = dict(a)
    pal.update(b)
    pal.update(dodatki)
    return pal


def wysokosc(j):
    s = j['szkielet']
    return sum(s[k] for k in ('ankle', 'shin', 'thigh', 'spine', 'chest', 'neck', 'head'))


def id_fuzji(id_a, id_b):
    """Nazwa niezależna od kolejności rodziców: golem+zolnierz == zolnierz+golem."""
    return '+'.join(sorted((id_a, id_b)))


# ------------------------------------------------------------------ kolory

def _hex_rgb(h):
    h = h.lstrip('#')
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def _rgb_hex(c):
    return '#' + ''.join(f'{max(0, min(255, round(x))):02x}' for x in c)


def zmieszaj(h1, h2, t):
    a, b = _hex_rgb(h1), _hex_rgb(h2)
    return _rgb_hex([x + (y - x) * t for x, y in zip(a, b)])


def swieci(m):
    return len(m) > 3 and m[3] > 0


def przebarw(paleta, zywiol):
    """Paleta jednostki w barwach żywiołu (zwraca nową paletę)."""
    out = {}
    kolor_sw, moc_sw = zywiol['swiecenie']
    for k, m in paleta.items():
        if k in zywiol['zamiany']:
            out[k] = zywiol['zamiany'][k]
        elif k in zywiol['barwy']:
            out[k] = (zywiol['barwy'][k],) + tuple(m[1:])
        elif swieci(m):
            out[k] = (zmieszaj(m[0], kolor_sw, 0.85), m[1], m[2] if len(m) > 2 else 0.0, max(m[3], moc_sw * 0.7))
        else:
            out[k] = m
    for k, m in zywiol['paleta'].items():
        out.setdefault(k, m)
    return out


# ------------------------------------------------------------------ szkic automatyczny

def auto_fuzja(rola_j, zywiol_j, zywioly, ruchy):
    """Szkic: rola i części od `rola_j`, żywioł (kolory, ozdoby, efekt) od `zywiol_j`."""
    from siatka import nazwa_pola
    zyw = zywioly[zywiol_j['zywiol']]
    efekt = zyw['efekty'].get(rola_j['atak']['ruch'], rola_j['atak']['efekt'])
    s = wysokosc(rola_j) / 1.8
    bark = rola_j.get('kotwice', {}).get('bark', 0.12) * 1.0
    czesci = {k: v for k, v in rola_j['czesci'].items() if k in PODSTAWOWE_SLOTY}
    czesci['Element'] = lambda sl, J, _z=zyw, _s=s, _b=bark: _z['ozdoby'](sl, J, _s, _b)
    rola, zyw_id = rola_j['rola'], zywiol_j['zywiol']
    return {
        'id': f"{id_fuzji(rola_j['id'], zywiol_j['id'])}__{rola}_{zyw_id}",
        'nazwa': f"Szkic: {nazwa_pola(rola, zyw_id)}",
        'opis': f"Szkic automatyczny. Rola i sylwetka: {rola_j['nazwa']}, żywioł: {zywiol_j['nazwa']}.",
        'rodzice': tuple(sorted((rola_j['id'], zywiol_j['id']))),
        'rola': rola,
        'zywiol': zyw_id,
        'szkielet': dict(rola_j['szkielet']),
        'paleta': przebarw(rola_j['paleta'], zyw),
        'czesci': czesci,
        'chod': dict(rola_j['chod']),
        'atak': {'ruch': rola_j['atak']['ruch'], 'efekt': efekt},
        'kotwice': rola_j.get('kotwice', {}),
        'tagi': {'szkic': True},
    }


# ------------------------------------------------------------------ Przebudzenie

ZLOTO = '#e8c25a'


def _aura(sl, J, s):
    # aureola za głową: pierścień z drobnych bloczków (płaszczyzna XZ, za potylicą)
    c = J['head_top'] + V(0, 0.16 * s, -0.12 * s)
    n = 20
    r = 0.2 * s
    for i in range(n):
        a = 2 * math.pi * i / n
        p = c + V(math.cos(a) * r, 0, math.sin(a) * r)
        sl.add(box(0.045 * s, 0.018 * s, 0.03 * s, 0.004), 'aura', 'head', frame(p, V(-math.sin(a), 0, math.cos(a)), (0, 1, 0)))
    for i in range(4):
        a = 2 * math.pi * i / 4 + math.pi / 4
        p = c + V(math.cos(a) * r * 1.25, 0, math.sin(a) * r * 1.25)
        sl.add(ico(0.022 * s, 1), 'aura', 'head', mtx(p))
    # krąg run pod stopami
    n = 28
    r = 0.62 * s
    for i in range(n):
        a = 2 * math.pi * i / n
        p = V(math.cos(a) * r, math.sin(a) * r, 0.006)
        dl = (0.09 if i % 4 == 0 else 0.05) * s
        sl.add(box(dl, 0.022 * s, 0.006), 'aura_soft', 'root', frame(p, V(0, 0, 1), (-math.sin(a), math.cos(a), 0)))
    sl.add(cyl(r * 0.82, r * 0.82, 0.004, 32), 'aura_glow', 'root', mtx((0, 0, 0.003)))
    # unoszące się odłamki nad barkami
    for sg in (1, -1):
        p = J['shoulder' + ('.L' if sg > 0 else '.R')] + V(sg * 0.12 * s, 0.1 * s, 0.32 * s)
        sl.add(cyl(0.03 * s, 0.0, 0.09 * s, 4), 'aura', 'chest', mtx(p))
        sl.add(cyl(0.0, 0.03 * s, 0.06 * s, 4), 'aura', 'chest', mtx(p - V(0, 0, 0.075 * s)))


def przebudz(j):
    """Wersja Przebudzona jednostki (rzadki wynik fuzji).

    Wspólne dla wszystkich: złocone metale i mocniejsze świecenie.
    Każda fuzja może dodać własne, wyjątkowe dodatki w swoim pliku:
        'przebudzenie': {'czesci': {'Aura': funkcja}, 'paleta': {...}, 'poswiata': False,
                         'atak': {'efekt': ..., 'status': {'id': 'podpalenie', 'czas_s': 4.0}}}
    poswiata=True (domyślnie) dodaje ogólną aureolę i krąg run – gdy fuzja nie ma własnego pomysłu.
    """
    cfg = j.get('przebudzenie', {})
    pal = {}
    for k, m in j['paleta'].items():
        metal = m[2] if len(m) > 2 else 0.0
        if swieci(m):
            pal[k] = (m[0], m[1], metal, m[3] * 1.8)
        elif metal >= 0.6:
            pal[k] = (zmieszaj(m[0], ZLOTO, 0.45), m[1] * 0.85, metal)
        else:
            pal[k] = m
    pal.update(cfg.get('paleta', {}))
    s = wysokosc(j) / 1.8
    czesci = dict(j['czesci'])
    if cfg.get('poswiata', True):
        pal['aura'] = ('#ffd76a', 0.3, 0.0, 6.0)
        pal['aura_soft'] = ('#ffe39a', 0.3, 0.0, 3.0)
        pal['aura_glow'] = ('#ffcf5a', 0.3, 0.0, 0.6)
        czesci['Aura'] = lambda sl, J, _s=s: _aura(sl, J, _s)
    czesci.update(cfg.get('czesci', {}))
    v = dict(j)
    v.update({
        'id': j['id'] + '_przebudzony',
        'nazwa': 'Przebudzony ' + j['nazwa'].replace('Szkic: ', ''),
        'opis': 'Rzadki wynik fuzji: ' + j.get('opis', ''),
        'paleta': pal,
        'czesci': czesci,
        'przebudzony': True,
        'baza': j['id'],
        'atak': {**j['atak'], **cfg.get('atak', {})},
    })
    v.pop('_plik', None)
    return v
