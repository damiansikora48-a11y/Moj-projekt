"""WYDANIA: zamrażanie plików wydanych do gry i wykrywanie zmian.

wydanie/<wersja>/       – zamrożone pliki .glb + units.json + manifest.json (odciski plików)
wydanie/ZMIANY.md       – historia: co zmieniło się w której wersji gry

Odcisk (fingerprint) pliku .glb to skrót danych każdej części (meshu) i każdej animacji,
dzięki czemu raport mówi nie tylko „zmienił się żołnierz”, ale „zmienił się Headgear i Attack”.
"""
import datetime
import hashlib
import json
import os
import shutil
import struct

from rejestr import ROOT

WYDANIA = os.path.join(ROOT, 'wydanie')
ZMIANY = os.path.join(WYDANIA, 'ZMIANY.md')


def _glb(path):
    raw = open(path, 'rb').read()
    n = struct.unpack('<I', raw[12:16])[0]
    j = json.loads(raw[20:20 + n])
    bin_off = 20 + n + 8
    return j, raw[bin_off:]


def _accessor_bytes(j, binary, idx):
    a = j['accessors'][idx]
    bv = j['bufferViews'][a['bufferView']]
    start = bv.get('byteOffset', 0) + a.get('byteOffset', 0)
    return binary[start:start + bv['byteLength']]


def odcisk(path):
    j, binary = _glb(path)
    czesci = {}
    for m in j.get('meshes', []):
        h = hashlib.sha256()
        for p in m['primitives']:
            for name in sorted(p['attributes']):
                if name in ('POSITION', 'JOINTS_0', 'WEIGHTS_0'):
                    h.update(_accessor_bytes(j, binary, p['attributes'][name]))
            # Kolejność trójkątów (indeksy) pomijamy: Blender potrafi przy każdym eksporcie
            # inaczej podzielić te same czworokąty – wygląd się nie zmienia. Liczymy ich liczbę.
            if 'indices' in p:
                h.update(str(j['accessors'][p['indices']]['count']).encode())
            mat = dict(j['materials'][p['material']]) if 'material' in p else {}
            mat.pop('name', None)  # nazwa materiału to tylko etykieta
            h.update(json.dumps(mat, sort_keys=True).encode())
        czesci[m['name'].rsplit('_', 1)[-1]] = h.hexdigest()[:16]
    animacje = {}
    for a in j.get('animations', []):
        h = hashlib.sha256()
        for s in a['samplers']:
            h.update(_accessor_bytes(j, binary, s['input']))
            h.update(_accessor_bytes(j, binary, s['output']))
        animacje[a['name']] = h.hexdigest()[:16]
    szkielet = hashlib.sha256(json.dumps([n.get('translation') for n in j['nodes']]).encode()).hexdigest()[:16]
    return {'czesci': czesci, 'animacje': animacje, 'szkielet': szkielet}


def ostatnie_wydanie():
    if not os.path.isdir(WYDANIA):
        return None
    wersje = [d for d in os.listdir(WYDANIA) if os.path.isfile(os.path.join(WYDANIA, d, 'manifest.json'))]
    if not wersje:
        return None
    wersje.sort(key=lambda v: [int(x) if x.isdigit() else x for x in v.replace('-', '.').split('.')])
    return wersje[-1]


def porownaj(export_dir, roster):
    """Porównuje świeży build z ostatnim wydaniem. Zwraca (wersja_wydania, lista wierszy raportu)."""
    ost = ostatnie_wydanie()
    stary = {}
    if ost:
        with open(os.path.join(WYDANIA, ost, 'manifest.json'), encoding='utf-8') as f:
            stary = json.load(f)['jednostki']
    raport = []
    for jid, info in roster['jednostki'].items():
        nowy = odcisk(os.path.join(export_dir, f'{jid}.glb'))
        w = info['wersja']
        if jid not in stary:
            raport.append({'id': jid, 'stan': 'nowa', 'wersja': w, 'zmiany': []})
            continue
        s = stary[jid]
        zmiany = []
        for typ in ('czesci', 'animacje'):
            for k in sorted(set(s['odcisk'][typ]) | set(nowy[typ])):
                if s['odcisk'][typ].get(k) != nowy[typ].get(k):
                    zmiany.append(k)
        if s['odcisk']['szkielet'] != nowy['szkielet']:
            zmiany.append('proporcje')
        if not zmiany:
            stan = 'bez zmian' if w == s['wersja'] else 'wersja podbita bez zmian'
        else:
            stan = 'zmieniona' if w > s['wersja'] else 'ZMIENIONA BEZ PODBICIA WERSJI'
        raport.append({'id': jid, 'stan': stan, 'wersja': w, 'poprzednia': s['wersja'], 'zmiany': zmiany})
    for jid in stary:
        if jid not in roster['jednostki']:
            raport.append({'id': jid, 'stan': 'usunięta z rostera', 'wersja': None, 'zmiany': []})
    return ost, raport


def wypisz(ost, raport):
    print(f"\nPorównanie z wydaniem: {ost or '(brak – to będzie pierwsze wydanie)'}")
    for r in raport:
        extra = f" – zmiany: {', '.join(r['zmiany'])}" if r['zmiany'] else ''
        wer = f" v{r.get('poprzednia')} -> v{r['wersja']}" if r.get('poprzednia') and r['wersja'] != r.get('poprzednia') else (f" v{r['wersja']}" if r['wersja'] else '')
        print(f"  {r['id']:<18} {r['stan']}{wer}{extra}")
    bledy = [r for r in raport if r['stan'] == 'ZMIENIONA BEZ PODBICIA WERSJI']
    for r in bledy:
        print(f"  ! {r['id']}: zmieniła się, a wersja w roster.json nadal {r['wersja']}. "
              f"Podnieś ją do {r['wersja'] + 1}, jeśli zmiana jest zamierzona; jeśli nie – cofnij zmianę w kodzie.")
    return not bledy


def wydaj(wersja_gry, export_dir, roster, efekty_pliki):
    ost, raport = porownaj(export_dir, roster)
    if not wypisz(ost, raport):
        raise SystemExit('Wydanie przerwane: są zmiany bez podbitej wersji (patrz wyżej).')
    cel = os.path.join(WYDANIA, wersja_gry)
    if os.path.exists(cel):
        raise SystemExit(f'Wydanie {wersja_gry} już istnieje – wydania są zamrożone. Użyj nowego numeru.')
    os.makedirs(cel)
    manifest = {'wersja_gry': wersja_gry, 'data': datetime.date.today().isoformat(), 'jednostki': {}}
    for jid, info in roster['jednostki'].items():
        src = os.path.join(export_dir, f'{jid}.glb')
        shutil.copy2(src, cel)
        manifest['jednostki'][jid] = {'wersja': info['wersja'], 'odcisk': odcisk(src)}
    for p in efekty_pliki:
        shutil.copy2(os.path.join(export_dir, p), cel)
    shutil.copy2(os.path.join(export_dir, 'units.json'), cel)
    with open(os.path.join(cel, 'manifest.json'), 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    # historia zmian
    linie = [f"\n## {wersja_gry} ({manifest['data']})\n"]
    for r in raport:
        if r['stan'] == 'nowa':
            linie.append(f"- **{r['id']}** v{r['wersja']}: nowa jednostka")
        elif r['stan'].startswith('zmieniona'):
            linie.append(f"- **{r['id']}** v{r['poprzednia']} → v{r['wersja']}: zmiany w {', '.join(r['zmiany'])}")
        elif r['stan'].startswith('usunięta'):
            linie.append(f"- **{r['id']}**: usunięta z gry")
    if len(linie) == 1:
        linie.append('- bez zmian w jednostkach')
    nowy_plik = not os.path.exists(ZMIANY)
    with open(ZMIANY, 'a', encoding='utf-8') as f:
        if nowy_plik:
            f.write('# Historia wydań jednostek\n\nDopisz pod każdą wersją krótko, CO i DLACZEGO zmieniłeś.\n')
        f.write('\n'.join(linie) + '\n')
    print(f'\nWydano {wersja_gry}: {cel}')
