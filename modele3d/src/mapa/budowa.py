"""MAPA – budowa: eksport elementów do export/mapa/ + uklad.json + podglądy.

Uruchamiane z build.py:  python build.py --mapa  [--podglad]
Pliki:
  teren.glb                          – ziemia, góra, lasy, staw, plac, drogi, działki
  mur_bok_etap<1-5>.glb              – mur boczny (lewy i prawy to ten sam element, obrócony)
  mur_front_etap<1-5>.glb            – mur przedni z prześwitem na bramę
  brama_etap<1-5>.glb, wieza_etap<1-5>.glb (6 wież: narożne, tylne przy górze, przy bramie)
Poziomy ulepszeń (1–15) wskazują etap wyglądu – mapowanie w uklad.json ('poziomy').
  uklad.json                         – gdzie co postawić w Godot + działki + strefy ataku
  budynek_glowny_poz<01-20>.glb     – budynek główny (stawiany na skalnej półce działki D1)
Każdy element muru/bramy/wieży ma puste węzły 'obronca_01'… = miejsca dla obrońców.
"""
import json
import math
import os

import bpy

from kit import V, Slot, make_material, reset_scene, setup_stage, render_view, build_unit, mtx
from mapa import uklad as U
from mapa import mury as M
from mapa import teren as T
from mapa import budynek_glowny as BG
from mapa import uszkodzenia as USZ

EXPORT = None  # ustawiane w zbuduj()


def _siatka(nazwa, sl, mats, normalne=True):
    import bmesh
    me = bpy.data.meshes.new(nazwa)
    if normalne:  # teren ma płaskie, rozłączne trójkąty skierowane w górę – nie przeliczamy
        bmesh.ops.recalc_face_normals(sl.bm, faces=sl.bm.faces)
    sl.bm.to_mesh(me)
    sl.bm.free()
    for m in sl.mats:
        me.materials.append(mats[m])
    me.shade_smooth()
    me.set_sharp_from_angle(angle=math.radians(38))
    ob = bpy.data.objects.new(nazwa, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def _obiekt(nazwa, fn, paleta, normalne=True):
    """Mesh z funkcji fn(sl) + puste węzły z miejscami obrońców (zwraca obiekt, lista miejsc).
    Warstwy uszkodzeń (znika_k / pojawia_k / pokaz_a_b, patrz uszkodzenia.py) są dziećmi obiektu."""
    mats = {k: make_material(f'mapa_{k}', *v) for k, v in paleta.items()}
    sl = USZ.Warstwy(nazwa)
    miejsca = fn(sl) or []
    ob = _siatka(nazwa, sl.sloty.pop(''), mats, normalne)
    warstwy = {}
    for w in sorted(sl.sloty):
        o = _siatka(f'{nazwa}_{w}', sl.sloty[w], mats, normalne)
        o.parent = ob
        warstwy[w] = o
    for n, p in list(miejsca) + sl.puste:
        e = bpy.data.objects.new(n, None)
        e.empty_display_type = 'PLAIN_AXES'
        e.location = p
        e.parent = warstwy.get(sl.warstwa_pustego.get(n), ob)
        bpy.context.scene.collection.objects.link(e)
    return ob, miejsca


def ustaw_stan(ob, stan):
    """Podgląd: pokazuje/ukrywa warstwy uszkodzeń obiektu (stan 0–3)."""
    for c in ob.children:
        if c.type == 'MESH' and c.name[-1].isdigit():
            c.hide_render = c.hide_viewport = not USZ.widoczna(c.name, stan)


def _eksport(ob, path):
    for o in bpy.context.scene.objects:
        o.select_set(False)
    ob.select_set(True)
    for c in ob.children_recursive:
        c.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', use_selection=True, export_apply=True,
                              export_animations=False, export_yup=True, export_materials='EXPORT')


ELEMENTY = {
    'mur_bok': lambda poz: (lambda sl: M.mur(sl, poz, U.GLEB, 0.0, seed=1, margines=6.5, uszkodzenia=True)),
    'mur_front': lambda poz: (lambda sl: M.mur(sl, poz, U.SZER, U.BRAMA_SZER, seed=2, uszkodzenia=True)),
    'brama': lambda poz: (lambda sl: M.brama(sl, poz, uszkodzenia=True)),
    'wieza': lambda poz: (lambda sl: M.naroznik(sl, poz, uszkodzenia=True)),
}


def _postaw(ob, srodek, obrot):
    ob.location = (srodek[0], srodek[1], 0)
    ob.rotation_euler = (0, 0, math.radians(obrot))


def _swiat(srodek, obrot, p):
    a = math.radians(obrot)
    x, y, z = p
    return (srodek[0] + x * math.cos(a) - y * math.sin(a), srodek[1] + x * math.sin(a) + y * math.cos(a), z)


def uklad_json(liczba_miejsc):
    out = {
        '_opis': 'Układ miasta dla Godota. Pozycje w układzie Godota (x, y w górę, z), metry. '
                 'Poziom ulepszenia (1–15) -> etap wyglądu w "poziomy"; w nazwie pliku wstaw etap w miejsce {etap}. '
                 'Przód miasta (brama) jest od strony +Z.',
        'etapy': {str(k): v for k, v in U.ETAPY.items()},
        'poziomy': {str(p): {'etap': e} for p, e in U.POZIOMY.items()},
        'teren': {'plik': 'teren.glb'},
        'mury': {}, 'brama': {}, 'wieze': [], 'dzialki': [], 'strefy_ataku': {},
        'uszkodzenia': {
            '_opis': 'Stan uszkodzenia z wytrzymałości (0–1): pierwszy próg, który wytrzymałość osiąga. '
                     'Węzły-warstwy w każdym .glb muru/bramy/wieży: *_znika_k widoczne gdy stan < k, '
                     '*_pojawia_k widoczne gdy stan >= k, *_pokaz_a_b widoczne gdy a <= stan < b. '
                     'Pusty węzeł "wylom" (mury, brama) = środek wyłomu, aktywny w stanie 3.',
            'stany': {str(k): v for k, v in USZ.STANY.items()},
            'progi': [{'od_wytrzymalosci': p, 'stan': k} for p, k in USZ.STAN_Z_WYTRZYMALOSCI],
        },
    }
    for strona, m in U.MURY.items():
        out['mury'][strona] = {'plik': m['element'] + '_etap{etap}.glb', 'pozycja': U.do_godota(*m['srodek']),
                               'obrot_y_stopnie': m['obrot'], 'dlugosc_m': m['dlugosc'],
                               'miejsca_obroncow_na_etap': {str(e): liczba_miejsc[(m['element'], e)] for e in U.ETAPY}}
    out['brama'] = {'plik': 'brama_etap{etap}.glb', 'pozycja': U.do_godota(*U.BRAMA['srodek']), 'obrot_y_stopnie': 0,
                    'miejsca_obroncow_na_etap': {str(e): liczba_miejsc[('brama', e)] for e in U.ETAPY}}
    for n in U.WIEZE:
        out['wieze'].append({'id': n['id'], 'opis': n['opis'], 'plik': 'wieza_etap{etap}.glb', 'pozycja': U.do_godota(*n['srodek']),
                             'obrot_y_stopnie': 0,
                             'miejsca_obroncow_na_etap': {str(e): liczba_miejsc[('wieza', e)] for e in U.ETAPY}})
    for d in U.DZIALKI:
        out['dzialki'].append({'id': d['id'], 'pozycja': U.do_godota(*d['srodek']), 'rozmiar_m': list(d['rozmiar']),
                               'budynek': d['budynek'], 'uwagi': d['uwagi']})
    out['plac'] = {'pozycja': U.do_godota(*U.PLAC['srodek']), 'promien_m': U.PLAC['promien']}
    d1 = next(d for d in U.DZIALKI if d['id'] == U.BUDYNEK_GLOWNY['dzialka'])
    out['budynek_glowny'] = {'plik': 'budynek_glowny_poz{poziom:02}.glb', 'poziomy': U.BUDYNEK_GLOWNY['poziomy'],
                             'pozycja': U.do_godota(*d1['srodek'], d1['podwyzszenie']), 'obrot_y_stopnie': 0,
                             'zmiany': {str(k): v for k, v in BG.ZMIANY.items()}}
    for k, (x0, x1, y0, y1) in U.STREFY_ATAKU.items():
        a, b = U.do_godota(x0, y0), U.do_godota(x1, y1)
        out['strefy_ataku'][k] = {'od': [min(a[0], b[0]), 0, min(a[2], b[2])], 'do': [max(a[0], b[0]), 0, max(a[2], b[2])]}
    return out


def zbuduj(export_dir, podglad_dir, podglad=False):
    katalog = os.path.join(export_dir, 'mapa')
    os.makedirs(katalog, exist_ok=True)
    liczba = {}
    for el, fabryka in ELEMENTY.items():
        for poz in U.ETAPY:
            reset_scene()
            ob, miejsca = _obiekt(f'{el}_etap{poz}', fabryka(poz), M.PALETA)
            _eksport(ob, os.path.join(katalog, f'{el}_etap{poz}.glb'))
            liczba[(el, poz)] = len(miejsca)
            print('EXPORT mapa', el, 'etap', poz, f'({len(miejsca)} miejsc)')
    for p in range(1, U.BUDYNEK_GLOWNY['poziomy'] + 1):
        reset_scene()
        ob, _ = _obiekt(f'budynek_glowny_poz{p:02}', lambda sl, p=p: BG.budynek(sl, p), BG.PALETA)
        _eksport(ob, os.path.join(katalog, f'budynek_glowny_poz{p:02}.glb'))
    print('EXPORT mapa budynek_glowny 1-20')
    reset_scene()
    ob, _ = _obiekt('teren', T.teren, T.PALETA, normalne=False)
    _eksport(ob, os.path.join(katalog, 'teren.glb'))
    print('EXPORT mapa teren')
    with open(os.path.join(katalog, 'uklad.json'), 'w', encoding='utf-8') as f:
        json.dump(uklad_json(liczba), f, indent=2, ensure_ascii=False)
    if podglad:
        podglad_budynku(podglad_dir)
        podglady(podglad_dir)
        podglad_uszkodzen(podglad_dir)


# ------------------------------------------------------------------ podglądy

def _scena(poziomy, brama_poz, jednostki=None, budynek=None, uszkodzenia=None):
    """Składa całe miasto: poziomy = {'lewy': p, 'przod': p, 'prawy': p}."""
    reset_scene()
    ob, _ = _obiekt('teren', T.teren, T.PALETA, normalne=False)
    for strona, m in U.MURY.items():
        o, miejsca = _obiekt(f"{m['element']}_{strona}", ELEMENTY[m['element']](poziomy[strona]), M.PALETA)
        ustaw_stan(o, (uszkodzenia or {}).get(strona, 0))
        _postaw(o, m['srodek'], m['obrot'])
        if jednostki and strona in jednostki:
            for (n, p), jed in zip(miejsca, jednostki[strona]):
                if jed:
                    b = build_unit(jed)
                    b['arm'].location = _swiat(m['srodek'], m['obrot'], p)
                    b['arm'].rotation_euler = (0, 0, math.radians(m['obrot']))
    o, miejsca = _obiekt('brama', ELEMENTY['brama'](brama_poz), M.PALETA)
    ustaw_stan(o, (uszkodzenia or {}).get('brama', 0))
    _postaw(o, U.BRAMA['srodek'], 0)
    if jednostki and 'brama' in jednostki:
        for (n, p), jed in zip(miejsca, jednostki['brama']):
            if jed:
                b = build_unit(jed)
                b['arm'].location = _swiat(U.BRAMA['srodek'], 0, p)
    for nz in U.WIEZE:
        poz = poziomy.get(nz['id'], poziomy['przod'])  # wieże ulepszane osobno
        o, _ = _obiekt(nz['id'], ELEMENTY['wieza'](poz), M.PALETA)
        ustaw_stan(o, (uszkodzenia or {}).get(nz['id'], 0))
        _postaw(o, nz['srodek'], 0)
    if budynek:
        d1 = next(d for d in U.DZIALKI if d['id'] == U.BUDYNEK_GLOWNY['dzialka'])
        o, _ = _obiekt('budynek', lambda sl: BG.budynek(sl, budynek), BG.PALETA)
        o.location = (d1['srodek'][0], d1['srodek'][1], d1['podwyzszenie'])


def _studio(res_x, res_y, samples):
    """Oświetlenie do podglądu mapy (bez okrągłej podłogi ze studia postaci)."""
    setup_stage(res_x, samples)
    bpy.context.scene.render.resolution_y = res_y
    bpy.context.scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.8
    g = bpy.data.objects.get('Ground')
    if g:
        bpy.data.objects.remove(g, do_unlink=True)


def podglady(katalog):
    from rejestr import Rejestr
    rej = Rejestr()
    jd = {k: rej.do_budowy(rej.wszystkie[k]) for k in ('zolnierz', 'lesny_lucznik', 'mag_ognia', 'golem', 'kamienny_rycerz')}
    # 1) miasto na starcie (wszystko poziom 1)
    _scena({'lewy': 1, 'przod': 1, 'prawy': 1}, 1, budynek=1)
    _studio(1600, 1000, 48)
    render_view(os.path.join(katalog, 'mapa_start_52st.png'), (0, -4, 4), 118, 52, 0, lens=35)
    render_view(os.path.join(katalog, 'mapa_okolica.png'), (0, -30, 8), 150, 30, 0, lens=35)
    # 2) miasto rozbudowane z obrońcami na murach
    jedn = {'przod': [jd['lesny_lucznik'], jd['mag_ognia'], jd['lesny_lucznik'], jd['mag_ognia'], jd['lesny_lucznik'], jd['lesny_lucznik'], jd['mag_ognia']],
            'lewy': [jd['lesny_lucznik'], jd['zolnierz'], jd['lesny_lucznik']],
            'prawy': [jd['mag_ognia'], jd['lesny_lucznik'], jd['zolnierz'], jd['lesny_lucznik'], jd['mag_ognia'], jd['lesny_lucznik']],
            'brama': [jd['zolnierz'], jd['lesny_lucznik'], jd['zolnierz']]}
    _scena({'lewy': 3, 'przod': 4, 'prawy': 5, **{w['id']: 5 for w in U.WIEZE}}, 5, jedn, budynek=20)
    b = build_unit(jd['kamienny_rycerz'])
    b['arm'].location = (-2.5, U.PRZOD_Y - 4.5, 0)
    b = build_unit(jd['golem'])
    b['arm'].location = (2.8, U.PRZOD_Y - 5.0, 0)
    _studio(1600, 1000, 48)
    render_view(os.path.join(katalog, 'mapa_rozbudowana_52st.png'), (0, -4, 4), 118, 52, 0, lens=35)
    render_view(os.path.join(katalog, 'mapa_mury_z_bliska.png'), (2, U.PRZOD_Y, 3), 34, 40, 25, lens=35)
    render_view(os.path.join(katalog, 'mapa_budynek_glowny.png'), (0, U.GLEB / 2 - 5.5, 4), 30, 35, 15, lens=35)
    # 2b) miasto po ataku: różne stany uszkodzeń
    _scena({'lewy': 3, 'przod': 4, 'prawy': 5, **{w['id']: 4 for w in U.WIEZE}}, 4, budynek=12,
           uszkodzenia={'lewy': 1, 'przod': 3, 'prawy': 2, 'brama': 2, 'wieza_przod_lewa': 3, 'wieza_brama_prawa': 1})
    _studio(1600, 1000, 48)
    render_view(os.path.join(katalog, 'mapa_po_ataku_52st.png'), (0, -4, 4), 118, 52, 0, lens=35)
    # 3) wszystkie poziomy murów obok siebie (fragment muru z bramą i wieżą)
    reset_scene()
    for i, poz in enumerate(sorted(U.ETAPY)):
        x0 = (i - 2) * 24
        o, _ = _obiekt(f'm{poz}', lambda sl, p=poz: M.mur(sl, p, 22.0, U.BRAMA_SZER, seed=5), M.PALETA)
        _postaw(o, (x0, 0), 0)
        o, _ = _obiekt(f'b{poz}', ELEMENTY['brama'](poz), M.PALETA)
        _postaw(o, (x0, 0), 0)
        for sg in (1, -1):  # wieże przy bramie
            o, _ = _obiekt(f'n{poz}{sg}', ELEMENTY['wieza'](poz), M.PALETA)
            _postaw(o, (x0 + sg * U.WIEZA_BRAMY_X, 0), 0)
    o, _ = _obiekt('trawa', lambda sl: sl.add(__import__('kit').box(160, 40, 0.02), 'grass', 'root', mtx((0, 4, -0.01))), T.PALETA)
    _studio(1800, 700, 48)
    render_view(os.path.join(katalog, 'mapa_poziomy_murow.png'), (-1, 0, 3), 122, 22, 0, lens=35)


def podglad_budynku(katalog, samples=24):
    """Wszystkie 20 poziomów budynku głównego na jednym obrazku (z podpisami)."""
    from PIL import Image, ImageDraw, ImageFont
    import bmesh as _b
    kafle = []
    for p in range(1, U.BUDYNEK_GLOWNY['poziomy'] + 1):
        reset_scene()
        _obiekt('budynek', lambda sl, p=p: BG.budynek(sl, p), BG.PALETA)
        def polka(sl):
            from kit import box as _box
            sl.add(_box(14.0, 8.5, 1.6, 0.05), 'mtn', 'root', mtx((0, 0, -0.8)))
            sl.add(_box(13.8, 8.3, 0.1, 0.02), 'grass', 'root', mtx((0, 0, -0.04)))
            sl.add(_box(60, 60, 0.02), 'grass_dark', 'root', mtx((0, 0, -1.61)))
        _obiekt('polka', polka, T.PALETA)
        _studio(520, 440, samples)
        sciezka = os.path.join(katalog, f'_bg_{p:02}.png')
        daleko = p >= 13
        render_view(sciezka, (0, 0.6, 4.4 if daleko else 3.2), 30 if daleko else 24, 33, 28, lens=35)
        kafle.append(sciezka)
    W, H = 520, 440
    img = Image.new('RGB', (W * 5, (H + 56) * 4), (238, 240, 236))
    d = ImageDraw.Draw(img)
    try:
        f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 20)
        fs = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
    except OSError:
        f = fs = ImageFont.load_default()
    for i, k in enumerate(kafle):
        x, y = (i % 5) * W, (i // 5) * (H + 56)
        img.paste(Image.open(k).convert('RGB'), (x, y))
        d.text((x + 10, y + H + 4), f'Poziom {i + 1}', fill=(35, 39, 31), font=f)
        d.text((x + 10, y + H + 30), BG.ZMIANY[i + 1][:62], fill=(90, 95, 85), font=fs)
        os.remove(k)
    img.save(os.path.join(katalog, 'budynek_glowny_poziomy.png'))


def podglad_uszkodzen(katalog, samples=24, tylko=None):
    """Mury, brama i wieże (etapy 1–5) w 4 stanach uszkodzeń: obrazki uszkodzenia_<rodzaj>.png."""
    from PIL import Image, ImageDraw, ImageFont
    from kit import box as _box
    rodzaje = {
        # rodzaj: (budowa(poz), kamera(poz) -> (cel, odległość, pochylenie, obrót))
        'mury': (lambda poz: (lambda sl: M.mur(sl, poz, 22.0, 0.0, seed=3, margines=1.0, uszkodzenia=True)),
                 lambda poz: ((0, 0.4, 2.2), 21, 38, 14)),
        'brama': (lambda poz: (lambda sl: M.brama(sl, poz, uszkodzenia=True)),
                  lambda poz: ((0, 0.3, 2.6 + poz * 0.2), 13 + poz * 0.6, 30, 18)),
        'wieze': (lambda poz: (lambda sl: M.naroznik(sl, poz, uszkodzenia=True)),
                  lambda poz: ((0, 0, M.USZ_WIEZA[poz]['gora'] * 0.42), 9 + M.USZ_WIEZA[poz]['gora'] * 1.15, 26, 18)),
    }
    W, H, P = 640, 420, 40
    try:
        f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 22)
    except OSError:
        f = ImageFont.load_default()
    for rodzaj, (fabryka, kamera) in rodzaje.items():
        if tylko and rodzaj not in tylko:
            continue
        img = Image.new('RGB', (W * 4, P + (H + P) * 5), (238, 240, 236))
        d = ImageDraw.Draw(img)
        for stan in range(4):
            prog = {0: '100–70%', 1: '70–40%', 2: '40–1%', 3: '0%'}[stan]
            d.text((stan * W + 12, 8), f'{USZ.STANY[stan].capitalize()} ({prog})', fill=(35, 39, 31), font=f)
        for r, poz in enumerate(sorted(U.ETAPY)):
            y = P + r * (H + P)
            for stan in range(4):
                reset_scene()
                o, _ = _obiekt('el', fabryka(poz), M.PALETA)
                ustaw_stan(o, stan)
                _obiekt('trawa', lambda sl: sl.add(_box(80, 60, 0.02), 'grass', 'root', mtx((0, 4, -0.01))), T.PALETA)
                _studio(W, H, samples)
                sc = os.path.join(katalog, f'_usz.png')
                cel, dist, pitch, yaw = kamera(poz)
                render_view(sc, cel, dist, pitch, yaw, lens=35)
                img.paste(Image.open(sc).convert('RGB'), (stan * W, y))
                os.remove(sc)
            d.text((12, y + H + 6), f"Etap {poz}: {U.ETAPY[poz]['nazwa']}", fill=(90, 95, 85), font=f)
        img.save(os.path.join(katalog, f'uszkodzenia_{rodzaj}.png'))
        print('PODGLAD uszkodzenia', rodzaj)
