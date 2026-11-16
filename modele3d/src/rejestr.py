"""REJESTR: znajduje wszystkie jednostki, fuzje, ruchy i efekty oraz pilnuje zasad.

Nie trzeba go edytować: nowy plik w jednostki/, fuzje/, ataki/ruchy/ lub ataki/efekty/
jest wykrywany automatycznie. Do gry trafia tylko to, co jest wpisane w roster.json.
"""
import importlib
import json
import os
import pkgutil

from kit import HIDE

SRC = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SRC)
ROSTER = os.path.join(ROOT, 'roster.json')

# Stały słownik slotów (części). Nowa jednostka używa tylko tych nazw.
SLOTY = ('Head', 'Headgear', 'Body', 'Back', 'Arms', 'Legs', 'Weapon', 'Offhand')
ANIMACJE = {'idle': 'Idle_loop', 'walk': 'Walk_loop', 'attack': 'Attack'}


def _moduly(pakiet, zmienna):
    out = {}
    sciezka = os.path.join(SRC, *pakiet.split('.'))
    for info in pkgutil.iter_modules([sciezka]):
        mod = importlib.import_module(f'{pakiet}.{info.name}')
        obj = getattr(mod, zmienna, None)
        if obj is None:
            continue
        if obj['id'] in out:
            raise ValueError(f"Powtórzone id '{obj['id']}' w {pakiet}/{info.name}.py")
        obj['_plik'] = f'{pakiet.replace(".", "/")}/{info.name}.py'
        out[obj['id']] = obj
    return out


class Rejestr:
    def __init__(self):
        self.ruchy = _moduly('ataki.ruchy', 'RUCH')
        self.efekty = _moduly('ataki.efekty', 'EFEKT')
        self.podstawowe = _moduly('jednostki', 'JEDNOSTKA')
        self.fuzje = _moduly('fuzje', 'JEDNOSTKA')
        self.wszystkie = {**self.podstawowe, **self.fuzje}
        for j in self.wszystkie.values():
            self.sprawdz(j)

    # ------------------------------------------------------------ zasady
    def sprawdz(self, j):
        gdzie = j.get('_plik', j['id'])
        for slot in j['czesci']:
            if slot not in SLOTY:
                raise ValueError(f"{gdzie}: nieznany slot '{slot}'. Dozwolone: {', '.join(SLOTY)}")
        ruch, efekt = j['atak']['ruch'], j['atak']['efekt']
        if ruch not in self.ruchy:
            raise ValueError(f"{gdzie}: brak ruchu ataku '{ruch}' w ataki/ruchy/")
        if efekt is not None and efekt not in self.efekty:
            raise ValueError(f"{gdzie}: brak efektu '{efekt}' w ataki/efekty/")
        for r in j.get('rodzice', ()):
            if r not in self.podstawowe:
                raise ValueError(f"{gdzie}: rodzic '{r}' nie jest jednostką podstawową")

    # ------------------------------------------------------------ roster
    def roster(self):
        with open(ROSTER, encoding='utf-8') as f:
            r = json.load(f)
        for jid in r['jednostki']:
            if jid not in self.wszystkie:
                raise ValueError(f"roster.json: jednostka '{jid}' nie istnieje (brak pliku w jednostki/ ani fuzje/)")
        return r

    def fuzja_reczna(self, id_a, id_b):
        para = tuple(sorted((id_a, id_b)))
        for j in self.fuzje.values():
            if tuple(sorted(j['rodzice'])) == para:
                return j
        return None

    # ------------------------------------------------------------ do budowy
    def do_budowy(self, j):
        """Zamienia opis jednostki na dane dla kit.build_unit (dokleja ruch i efekt ataku)."""
        ruch = self.ruchy[j['atak']['ruch']]
        efekt = self.efekty.get(j['atak']['efekt']) if j['atak']['efekt'] else None
        paleta = dict(efekt['paleta']) if efekt else {}
        paleta.update(j['paleta'])
        sloty = list(j['czesci'].items())
        chod = dict(j['chod'])
        if ruch.get('rekwizyt'):
            chod['rest_scale'] = {'prop.R': HIDE}
            if efekt and efekt.get('w_dloni'):
                sloty.append(('Prop', efekt['w_dloni']))
        return {
            'name': j['id'], 'skeleton': j['szkielet'], 'palette': paleta, 'slots': sloty, 'anim': chod,
            'attack': {'name': ANIMACJE['attack'], 'frames': ruch['frames'], 'keys': ruch['keys']},
        }

    def metadane(self, j, wersja, fps=30):
        """Wpis jednostki w units.json (to czyta gra)."""
        ruch = self.ruchy[j['atak']['ruch']]
        efekt = self.efekty.get(j['atak']['efekt']) if j['atak']['efekt'] else None
        typ = efekt['typ'] if efekt else ruch['typ']
        return {
            'nazwa': j['nazwa'],
            'wersja': wersja,
            'plik': f"{j['id']}.glb",
            'rodzice': list(j.get('rodzice', ())),
            'opis': j.get('opis', ''),
            'animacje': dict(ANIMACJE),
            'atak': {
                'ruch': ruch['id'],
                'efekt': efekt['id'] if efekt else None,
                'typ': typ,
                'dlugosc_s': round(ruch['frames'] / fps, 3),
                'moment_s': round(ruch['event'] * ruch['frames'] / fps, 3),
                'zdarzenie': ruch['event_name'],
                'plik_efektu': f"efekt_{efekt['id']}.glb" if efekt else None,
                'kosc_startowa': ruch.get('kosc_startowa', 'prop.R') if typ == 'pocisk' else None,
                'uwagi': efekt.get('uwagi') if efekt else None,
            },
        }
