"""FUZJE: narzędzia do łączenia dwóch jednostek + fuzja automatyczna (szkic).

Fuzja ręczna (plik w fuzje/) używa polacz_szkielet i polacz_palete, a części projektuje sama.
Fuzja automatyczna (auto_fuzja) składa szkic z gotowych części rodziców według prostych reguł:
  * proporcje: średnia obu rodziców
  * Body, Arms, Legs  – od WIĘKSZEGO rodzica (on daje sylwetkę)
  * Head, Headgear, Back, Weapon, Offhand – od MNIEJSZEGO (on daje „charakter” i broń)
  * atak: RUCH mniejszego rodzica + EFEKT większego (jeśli go nie ma – efekt mniejszego)
Szkice trafiają do szkice/ i NIE wchodzą do gry, dopóki nie zrobisz z nich fuzji ręcznej
i nie dopiszesz jej do roster.json.
"""
from kit import lerp

SYLWETKA = ('Body', 'Arms', 'Legs')


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


def auto_fuzja(a, b, sloty):
    duzy, maly = (a, b) if wysokosc(a) >= wysokosc(b) else (b, a)
    czesci = {}
    for slot in sloty:
        zrodlo, zapas = (duzy, maly) if slot in SYLWETKA else (maly, duzy)
        fn = zrodlo['czesci'].get(slot) or zapas['czesci'].get(slot)
        if fn:
            czesci[slot] = fn
    chod = {}
    for k in set(a['chod']) | set(b['chod']):
        va, vb = a['chod'].get(k), b['chod'].get(k)
        if isinstance(va, (int, float)) and isinstance(vb, (int, float)):
            chod[k] = round(lerp(va, vb, 0.5)) if k.endswith('_frames') else lerp(va, vb, 0.5)
        else:
            chod[k] = va if va is not None else vb
    efekt = duzy['atak']['efekt'] or maly['atak']['efekt']
    return {
        'id': id_fuzji(a['id'], b['id']),
        'nazwa': f"Szkic: {a['nazwa']} + {b['nazwa']}",
        'opis': f"Fuzja automatyczna. Sylwetka: {duzy['nazwa']}, głowa i broń: {maly['nazwa']}.",
        'rodzice': tuple(sorted((a['id'], b['id']))),
        'szkielet': polacz_szkielet(a['szkielet'], b['szkielet'], 0.5),
        'paleta': polacz_palete(a['paleta'], b['paleta']),
        'czesci': czesci,
        'chod': chod,
        'atak': {'ruch': maly['atak']['ruch'], 'efekt': efekt},
        'tagi': {'szkic': True},
    }
