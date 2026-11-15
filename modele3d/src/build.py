"""Buduje jednostki, eksportuje .glb dla Godot i renderuje podglądy.

Użycie:  python build.py [soldier] [golem] [hybrid] [--no-render] [--quick]
(wymaga modułu `bpy`, np. `pip install bpy` na Pythonie 3.11)
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kit import (reset_scene, build_unit, export_glb, setup_stage, render_view, set_action,  # noqa: E402
                 build_static, export_static)
from fusion import UNITS, HYBRID_PALETTE, spikes_parts  # noqa: E402
from units import GOLEM, golem_rock_parts  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORT = os.path.join(ROOT, 'export')
PREVIEW = os.path.join(ROOT, 'podglad')

GAME_PITCH = 52  # kąt kamery w grze
HEIGHT = {'soldier': 2.0, 'golem': 2.6, 'hybrid': 2.3}
FPS = 30

PROPS = {
    'golem_rock': dict(fn=lambda sl: golem_rock_parts(sl, 'root', None), palette=GOLEM['palette']),
    'hybrid_spikes': dict(fn=spikes_parts, palette=HYBRID_PALETTE),
}


def metadata():
    meta = {}
    for key, u in UNITS.items():
        a = u['attack']
        meta[key] = {
            'file': f'{key}.glb',
            'animations': {'idle': 'Idle_loop', 'walk': 'Walk_loop', 'attack': a['name']},
            'attack_length_s': round(a['frames'] / FPS, 3),
            'attack_event': a['event_name'],
            'attack_event_time_s': round(a['event'] * a['frames'] / FPS, 3),
        }
    meta['soldier'].update(attack_type='melee', reach_m=1.6)
    meta['golem'].update(attack_type='projectile', projectile='golem_rock.glb', spawn_bone='prop.R')
    meta['hybrid'].update(attack_type='melee_aoe', reach_m=2.0, effect='hybrid_spikes.glb',
                          effect_note='kolce w linii przed jednostką, 3 sztuki co 0.8 m, kolejno co 0.08 s')
    return meta


def main():
    args = sys.argv[1:]
    names = [a for a in args if not a.startswith('--')] or list(UNITS)
    render = '--no-render' not in args
    quick = '--quick' in args
    res, samples = (480, 16) if quick else (1000, 64)
    os.makedirs(EXPORT, exist_ok=True)
    os.makedirs(PREVIEW, exist_ok=True)

    for n in names:
        reset_scene()
        u = UNITS[n]
        b = build_unit(u)
        export_glb(b, os.path.join(EXPORT, f'{n}.glb'))
        print('EXPORT', n)
        if not render:
            continue
        setup_stage(res, samples)
        h = HEIGHT[n]
        tz, d = h * 0.45, h * 2.15
        render_view(os.path.join(PREVIEW, f'{n}_gra_52st.png'), (0, 0, tz), d * 0.85, GAME_PITCH, 30)
        render_view(os.path.join(PREVIEW, f'{n}_przod.png'), (0, 0, tz), d, 8, 28)
        render_view(os.path.join(PREVIEW, f'{n}_tyl.png'), (0, 0, tz), d, 14, 155)
        set_action(b['arm'], b['actions']['walk'], u['anim']['walk_frames'] // 4)
        render_view(os.path.join(PREVIEW, f'{n}_chod.png'), (0, 0, tz), d, 4, 90)
        atk = u['attack']
        wind = atk['keys'][1][0] if n != 'golem' else 0.5
        set_action(b['arm'], b['actions']['attack'], round(wind * atk['frames']))
        render_view(os.path.join(PREVIEW, f'{n}_atak_1_zamach.png'), (0, 0, tz * 1.1), d * 1.05, 6, 62)
        set_action(b['arm'], b['actions']['attack'], round(atk['event'] * atk['frames']))
        render_view(os.path.join(PREVIEW, f'{n}_atak_2_uderzenie.png'), (0, 0, tz * 1.1), d * 1.05, 6, 62)

    # rekwizyty: pocisk golema i efekt hybrydy
    for pname, pdef in PROPS.items():
        reset_scene()
        ob = build_static(pname, pdef['fn'], pdef['palette'])
        export_static(ob, os.path.join(EXPORT, f'{pname}.glb'))
        print('EXPORT', pname)

    with open(os.path.join(EXPORT, 'units.json'), 'w', encoding='utf-8') as f:
        json.dump(metadata(), f, indent=2, ensure_ascii=False)

    if render and len(names) == len(UNITS) and not quick:
        import bpy
        reset_scene()
        build_unit(UNITS['soldier'], offset=(-1.55, 0.25, 0))
        build_unit(UNITS['hybrid'], offset=(0.0, 0.0, 0))
        build_unit(UNITS['golem'], offset=(1.75, 0.1, 0))
        setup_stage(1400, samples)
        bpy.context.scene.render.resolution_x = 1800
        bpy.context.scene.render.resolution_y = 1000
        render_view(os.path.join(PREVIEW, 'razem_gra_52st.png'), (0.1, 0, 1.0), 7.6, GAME_PITCH, 20)


if __name__ == '__main__':
    main()
