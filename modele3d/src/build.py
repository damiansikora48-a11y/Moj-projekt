"""BUDOWA – jedyny skrypt, który uruchamiasz.

  python build.py                      zbuduj wszystkie jednostki z roster.json  -> export/
  python build.py zolnierz golem       zbuduj tylko wybrane (mogą być spoza rostera, np. nowa w trakcie pracy)
  python build.py --podglad            ... i zrób rendery podglądu                -> podglad/
  python build.py --szybko             rendery w niskiej jakości (do sprawdzania w trakcie pracy)
  python build.py --szkice             fuzje automatyczne par bez fuzji ręcznej   -> szkice/  (nie idą do gry)
  python build.py --szkice --wszystkie ... także par, które mają fuzję ręczną (do porównania)
  python build.py --sprawdz            co się zmieniło względem ostatniego wydania?
  python build.py --wydaj 1.0          zamroź wydanie gry                         -> wydanie/1.0/

Wymaga modułu `bpy` (Blender jako biblioteka Pythona 3.11), patrz README.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kit import (reset_scene, build_unit, export_glb, setup_stage, render_view, set_action,  # noqa: E402
                 build_static, export_static)
from fuzja import auto_fuzja, wysokosc  # noqa: E402
from rejestr import Rejestr, ROOT, SLOTY  # noqa: E402
import wydania  # noqa: E402

EXPORT = os.path.join(ROOT, 'export')
PODGLAD = os.path.join(ROOT, 'podglad')
SZKICE = os.path.join(ROOT, 'szkice')
GAME_PITCH = 52  # kąt kamery w grze


def zbuduj(rej, j, katalog):
    reset_scene()
    b = build_unit(rej.do_budowy(j))
    export_glb(b, os.path.join(katalog, f"{j['id']}.glb"))
    return b


def rendery(rej, j, b, res, samples):
    setup_stage(res, samples)
    h = wysokosc(j) * 1.08
    tz, d = h * 0.45, h * 2.15
    n = j['id']
    render_view(os.path.join(PODGLAD, f'{n}_gra_52st.png'), (0, 0, tz), d * 0.85, GAME_PITCH, 30)
    render_view(os.path.join(PODGLAD, f'{n}_przod.png'), (0, 0, tz), d, 8, 28)
    render_view(os.path.join(PODGLAD, f'{n}_tyl.png'), (0, 0, tz), d, 14, 155)
    set_action(b['arm'], b['actions']['walk'], j['chod']['walk_frames'] // 4)
    render_view(os.path.join(PODGLAD, f'{n}_chod.png'), (0, 0, tz), d, 4, 90)
    ruch = rej.ruchy[j['atak']['ruch']]
    zamach = 0.5 if ruch.get('rekwizyt') else ruch['keys'][1][0]
    set_action(b['arm'], b['actions']['attack'], round(zamach * ruch['frames']))
    render_view(os.path.join(PODGLAD, f'{n}_atak_1_zamach.png'), (0, 0, tz * 1.1), d * 1.05, 6, 62)
    set_action(b['arm'], b['actions']['attack'], round(ruch['event'] * ruch['frames']))
    render_view(os.path.join(PODGLAD, f'{n}_atak_2_uderzenie.png'), (0, 0, tz * 1.1), d * 1.05, 6, 62)


def razem(rej, ids, samples):
    import bpy
    reset_scene()
    jednostki = [rej.wszystkie[i] for i in ids]
    szer = [max(0.9, wysokosc(j) * 0.75) for j in jednostki]
    x = -sum(szer) / 2
    for j, s in zip(jednostki, szer):
        build_unit(rej.do_budowy(j), offset=(x + s / 2, 0, 0))
        x += s
    setup_stage(1400, samples)
    bpy.context.scene.render.resolution_x = 1800
    bpy.context.scene.render.resolution_y = 1000
    render_view(os.path.join(PODGLAD, 'razem_gra_52st.png'), (0, 0, 0.9), 3.6 + sum(szer) * 1.15, GAME_PITCH, 15)


def szkice(rej, samples, wszystkie=False):
    os.makedirs(SZKICE, exist_ok=True)
    ids = sorted(rej.podstawowe)
    for i, a in enumerate(ids):
        for b_id in ids[i + 1:]:
            if rej.fuzja_reczna(a, b_id) and not wszystkie:
                print(f'SZKIC pominięty: {a}+{b_id} ma już fuzję ręczną')
                continue
            j = auto_fuzja(rej.podstawowe[a], rej.podstawowe[b_id], SLOTY)
            rej.sprawdz(j)
            b = zbuduj(rej, j, SZKICE)
            setup_stage(600, 24)
            h = wysokosc(j) * 1.08
            render_view(os.path.join(SZKICE, f"{j['id']}.png"), (0, 0, h * 0.45), h * 1.85, GAME_PITCH, 30)
            set_action(b['arm'], b['actions']['attack'], round(rej.ruchy[j['atak']['ruch']]['event'] * rej.ruchy[j['atak']['ruch']]['frames']))
            render_view(os.path.join(SZKICE, f"{j['id']}_atak.png"), (0, 0, h * 0.5), h * 2.2, 6, 62)
            print('SZKIC', j['id'])


def main():
    args = sys.argv[1:]
    flagi = {a for a in args if a.startswith('--')}
    wybrane = [a for a in args if not a.startswith('--')]
    wersja_wydania = None
    if '--wydaj' in flagi:
        i = args.index('--wydaj')
        wersja_wydania = args[i + 1]
        wybrane = [a for a in wybrane if a != wersja_wydania]

    rej = Rejestr()
    roster = rej.roster()
    if '--szkice' in flagi:
        szkice(rej, 24, '--wszystkie' in flagi)
        return

    ids = wybrane or list(roster['jednostki'])
    if wersja_wydania or '--sprawdz' in flagi:
        ids = list(roster['jednostki'])  # wydanie zawsze obejmuje cały roster
    for jid in ids:
        if jid not in rej.wszystkie:
            raise SystemExit(f"Nie ma jednostki '{jid}'. Dostępne: {', '.join(sorted(rej.wszystkie))}")

    os.makedirs(EXPORT, exist_ok=True)
    os.makedirs(PODGLAD, exist_ok=True)
    podglad = '--podglad' in flagi or '--szybko' in flagi
    res, samples = (480, 16) if '--szybko' in flagi else (1000, 64)

    # 1) jednostki
    efekty = set()
    for jid in ids:
        j = rej.wszystkie[jid]
        b = zbuduj(rej, j, EXPORT)
        print('EXPORT', jid)
        if j['atak']['efekt']:
            efekty.add(j['atak']['efekt'])
        if podglad:
            rendery(rej, j, b, res, samples)
    # 2) efekty ataków (pociski, kolce...)
    for eid in sorted(efekty):
        e = rej.efekty[eid]
        reset_scene()
        ob = build_static(f'efekt_{eid}', e['model'], e['paleta'])
        export_static(ob, os.path.join(EXPORT, f'efekt_{eid}.glb'))
        print('EXPORT', f'efekt_{eid}')
    # 3) units.json – dane dla gry (tylko jednostki z rostera)
    meta = {jid: rej.metadane(rej.wszystkie[jid], info['wersja']) for jid, info in roster['jednostki'].items()}
    with open(os.path.join(EXPORT, 'units.json'), 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    if podglad and not wybrane and '--szybko' not in flagi:
        razem(rej, list(roster['jednostki']), samples)

    # 4) kontrola zmian / wydanie
    if '--sprawdz' in flagi:
        ost, raport = wydania.porownaj(EXPORT, roster)
        wydania.wypisz(ost, raport)
    if wersja_wydania:
        pliki_efektow = sorted({f"efekt_{rej.wszystkie[j]['atak']['efekt']}.glb"
                                for j in roster['jednostki'] if rej.wszystkie[j]['atak']['efekt']})
        wydania.wydaj(wersja_wydania, EXPORT, roster, pliki_efektow)


if __name__ == '__main__':
    main()
