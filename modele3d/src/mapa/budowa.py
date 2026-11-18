"""MAPA – budowa: eksport elementów do export/mapa/ + uklad.json + podglądy.

Uruchamiane z build.py:  python build.py --mapa  [--podglad]
Pliki:
  teren.glb                          – ziemia, góra, lasy, staw, plac, drogi, działki
  mur_bok_<1-4>.glb                  – mur boczny (lewy i prawy to ten sam element, obrócony)
  mur_front_<1-4>.glb                – mur przedni z prześwitem na bramę
  brama_<1-4>.glb, naroznik_<1-4>.glb
  uklad.json                         – gdzie co postawić w Godot + działki + strefy ataku
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

EXPORT = None  # ustawiane w zbuduj()


def _obiekt(nazwa, fn, paleta, normalne=True):
    """Mesh z funkcji fn(sl) + puste węzły z miejscami obrońców (zwraca obiekt, lista miejsc)."""
    mats = {k: make_material(f'mapa_{k}', *v) for k, v in paleta.items()}
    sl = Slot(nazwa)
    miejsca = fn(sl) or []
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
    for n, p in miejsca:
        e = bpy.data.objects.new(n, None)
        e.empty_display_type = 'PLAIN_AXES'
        e.location = p
        e.parent = ob
        bpy.context.scene.collection.objects.link(e)
    return ob, miejsca


def _eksport(ob, path):
    for o in bpy.context.scene.objects:
        o.select_set(False)
    ob.select_set(True)
    for c in ob.children:
        c.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', use_selection=True, export_apply=True,
                              export_animations=False, export_yup=True, export_materials='EXPORT')


ELEMENTY = {
    'mur_bok': lambda poz: (lambda sl: M.mur(sl, poz, U.GLEB, 0.0, seed=1)),
    'mur_front': lambda poz: (lambda sl: M.mur(sl, poz, U.SZER, U.BRAMA_SZER, seed=2)),
    'brama': lambda poz: (lambda sl: M.brama(sl, poz)),
    'naroznik': lambda poz: (lambda sl: M.naroznik(sl, poz)),
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
                 'Plik elementu: wstaw poziom w miejsce {poziom}. Przód miasta (brama) jest od strony +Z.',
        'poziomy': {str(k): v for k, v in U.POZIOMY.items()},
        'teren': {'plik': 'teren.glb'},
        'mury': {}, 'brama': {}, 'narozniki': [], 'dzialki': [], 'strefy_ataku': {},
    }
    for strona, m in U.MURY.items():
        out['mury'][strona] = {'plik': m['element'] + '_{poziom}.glb', 'pozycja': U.do_godota(*m['srodek']),
                               'obrot_y_stopnie': m['obrot'], 'dlugosc_m': m['dlugosc'],
                               'miejsca_obroncow': {str(p): liczba_miejsc[(m['element'], p)] for p in U.POZIOMY}}
    out['brama'] = {'plik': 'brama_{poziom}.glb', 'pozycja': U.do_godota(*U.BRAMA['srodek']), 'obrot_y_stopnie': 0,
                    'miejsca_obroncow': {str(p): liczba_miejsc[('brama', p)] for p in U.POZIOMY}}
    for n in U.NAROZNIKI:
        out['narozniki'].append({'plik': 'naroznik_{poziom}.glb', 'pozycja': U.do_godota(*n['srodek']),
                                 'obrot_y_stopnie': 0, 'poziom_jak_wyzszy_z': n['sasiedzi']})
    for d in U.DZIALKI:
        out['dzialki'].append({'id': d['id'], 'pozycja': U.do_godota(*d['srodek']), 'rozmiar_m': list(d['rozmiar']),
                               'budynek': d['budynek'], 'uwagi': d['uwagi']})
    out['plac'] = {'pozycja': U.do_godota(*U.PLAC['srodek']), 'promien_m': U.PLAC['promien']}
    for k, (x0, x1, y0, y1) in U.STREFY_ATAKU.items():
        a, b = U.do_godota(x0, y0), U.do_godota(x1, y1)
        out['strefy_ataku'][k] = {'od': [min(a[0], b[0]), 0, min(a[2], b[2])], 'do': [max(a[0], b[0]), 0, max(a[2], b[2])]}
    return out


def zbuduj(export_dir, podglad_dir, podglad=False):
    katalog = os.path.join(export_dir, 'mapa')
    os.makedirs(katalog, exist_ok=True)
    liczba = {}
    for el, fabryka in ELEMENTY.items():
        for poz in U.POZIOMY:
            reset_scene()
            ob, miejsca = _obiekt(f'{el}_{poz}', fabryka(poz), M.PALETA)
            _eksport(ob, os.path.join(katalog, f'{el}_{poz}.glb'))
            liczba[(el, poz)] = len(miejsca)
            print('EXPORT mapa', el, poz, f'({len(miejsca)} miejsc)')
    reset_scene()
    ob, _ = _obiekt('teren', T.teren, T.PALETA, normalne=False)
    _eksport(ob, os.path.join(katalog, 'teren.glb'))
    print('EXPORT mapa teren')
    with open(os.path.join(katalog, 'uklad.json'), 'w', encoding='utf-8') as f:
        json.dump(uklad_json(liczba), f, indent=2, ensure_ascii=False)
    if podglad:
        podglady(podglad_dir)


# ------------------------------------------------------------------ podglądy

def _scena(poziomy, brama_poz, jednostki=None):
    """Składa całe miasto: poziomy = {'lewy': p, 'przod': p, 'prawy': p}."""
    reset_scene()
    ob, _ = _obiekt('teren', T.teren, T.PALETA, normalne=False)
    for strona, m in U.MURY.items():
        o, miejsca = _obiekt(f"{m['element']}_{strona}", ELEMENTY[m['element']](poziomy[strona]), M.PALETA)
        _postaw(o, m['srodek'], m['obrot'])
        if jednostki and strona in jednostki:
            for (n, p), jed in zip(miejsca, jednostki[strona]):
                if jed:
                    b = build_unit(jed)
                    b['arm'].location = _swiat(m['srodek'], m['obrot'], p)
                    b['arm'].rotation_euler = (0, 0, math.radians(m['obrot']))
    o, miejsca = _obiekt('brama', ELEMENTY['brama'](brama_poz), M.PALETA)
    _postaw(o, U.BRAMA['srodek'], 0)
    if jednostki and 'brama' in jednostki:
        for (n, p), jed in zip(miejsca, jednostki['brama']):
            if jed:
                b = build_unit(jed)
                b['arm'].location = _swiat(U.BRAMA['srodek'], 0, p)
    for nz in U.NAROZNIKI:
        poz = max(poziomy[s] for s in nz['sasiedzi'])
        o, _ = _obiekt('naroznik', ELEMENTY['naroznik'](poz), M.PALETA)
        _postaw(o, nz['srodek'], 0)


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
    _scena({'lewy': 1, 'przod': 1, 'prawy': 1}, 1)
    _studio(1600, 1000, 48)
    render_view(os.path.join(katalog, 'mapa_start_52st.png'), (0, -4, 4), 92, 52, 0, lens=35)
    render_view(os.path.join(katalog, 'mapa_okolica.png'), (0, -30, 8), 150, 30, 0, lens=35)
    # 2) miasto rozbudowane z obrońcami na murach
    jedn = {'przod': [jd['lesny_lucznik'], jd['mag_ognia'], jd['lesny_lucznik'], jd['mag_ognia'], jd['lesny_lucznik'], jd['lesny_lucznik'], jd['mag_ognia']],
            'lewy': [jd['lesny_lucznik'], jd['zolnierz'], jd['lesny_lucznik']],
            'prawy': [jd['mag_ognia'], jd['lesny_lucznik'], jd['zolnierz'], jd['lesny_lucznik'], jd['mag_ognia'], jd['lesny_lucznik']],
            'brama': [jd['zolnierz'], jd['lesny_lucznik'], jd['zolnierz']]}
    _scena({'lewy': 2, 'przod': 3, 'prawy': 4}, 4, jedn)
    b = build_unit(jd['kamienny_rycerz'])
    b['arm'].location = (-2.5, U.PRZOD_Y - 4.5, 0)
    b = build_unit(jd['golem'])
    b['arm'].location = (2.8, U.PRZOD_Y - 5.0, 0)
    _studio(1600, 1000, 48)
    render_view(os.path.join(katalog, 'mapa_rozbudowana_52st.png'), (0, -4, 4), 92, 52, 0, lens=35)
    render_view(os.path.join(katalog, 'mapa_mury_z_bliska.png'), (2, U.PRZOD_Y, 3), 34, 40, 25, lens=35)
    # 3) wszystkie poziomy murów obok siebie (fragment muru z bramą i wieżą)
    reset_scene()
    for i, poz in enumerate(sorted(U.POZIOMY)):
        x0 = (i - 1.5) * 24
        o, _ = _obiekt(f'm{poz}', lambda sl, p=poz: M.mur(sl, p, 18.0, U.BRAMA_SZER, seed=5), M.PALETA)
        _postaw(o, (x0, 0), 0)
        o, _ = _obiekt(f'b{poz}', ELEMENTY['brama'](poz), M.PALETA)
        _postaw(o, (x0, 0), 0)
        o, _ = _obiekt(f'n{poz}', ELEMENTY['naroznik'](poz), M.PALETA)
        _postaw(o, (x0 - 9.5, 0), 0)
    _studio(1800, 800, 48)
    render_view(os.path.join(katalog, 'mapa_poziomy_murow.png'), (0, 0, 3), 78, 28, 12, lens=35)
