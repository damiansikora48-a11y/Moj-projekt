"""Buduje jednostki, eksportuje .glb dla Godot i renderuje podglądy.

Użycie:  python build.py [soldier] [golem] [--no-render] [--quick]
(wymaga modułu `bpy`, np. `pip install bpy` na Pythonie 3.11)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kit import reset_scene, build_unit, export_glb, setup_stage, render_view, set_action  # noqa: E402
from units import UNITS  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORT = os.path.join(ROOT, 'export')
PREVIEW = os.path.join(ROOT, 'podglad')

GAME_PITCH = 52  # kąt kamery w grze


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
        b = build_unit(UNITS[n])
        path = os.path.join(EXPORT, f'{n}.glb')
        export_glb(b, path)
        print('EXPORT', path)
        if not render:
            continue
        setup_stage(res, samples)
        h = 2.6 if n == 'golem' else 2.0
        tz = h * 0.45
        d = h * 2.15
        render_view(os.path.join(PREVIEW, f'{n}_gra_52st.png'), (0, 0, tz), d * 0.85, GAME_PITCH, 30)
        render_view(os.path.join(PREVIEW, f'{n}_przod.png'), (0, 0, tz), d, 8, 28)
        render_view(os.path.join(PREVIEW, f'{n}_tyl.png'), (0, 0, tz), d, 14, 155)
        set_action(b['arm'], b['actions']['walk'], UNITS[n]['anim']['walk_frames'] // 4)
        render_view(os.path.join(PREVIEW, f'{n}_chod.png'), (0, 0, tz), d, 4, 90)

    if render and len(names) > 1 and not quick:
        reset_scene()
        build_unit(UNITS['soldier'], offset=(-0.95, 0.15, 0))
        build_unit(UNITS['golem'], offset=(0.75, 0, 0))
        setup_stage(1400, samples)
        bpy_scene_res(1600, 1000)
        render_view(os.path.join(PREVIEW, 'razem_gra_52st.png'), (0, 0, 1.0), 6.2, GAME_PITCH, 20)


def bpy_scene_res(x, y):
    import bpy
    bpy.context.scene.render.resolution_x = x
    bpy.context.scene.render.resolution_y = y


if __name__ == '__main__':
    main()
