"""CZĘŚCI WSPÓLNE: tkaniny (peleryna).

Używają: żołnierz (peleryna standardowa), Kamienny Rycerz (szersza i dłuższa).
Zmiana kształtu peleryny tutaj zmienia ją u WSZYSTKICH jednostek, które jej używają.
"""
import math

import bmesh

from kit import V, box, cyl, sphere, ico, rock, cut_below, taper, jitter, mtx, frame, seg, SIDES, lerp, scale_m


def cloth_sheet(cols, rows, fn, thickness=0.022):
    """Siatka (u w [-1,1], v w [0,1]) wygięta funkcją fn(u, v) -> Vector, z grubością."""
    bm = bmesh.new()
    grid = [[bm.verts.new(fn(-1 + 2 * i / cols, j / rows)) for i in range(cols + 1)] for j in range(rows + 1)]
    for j in range(rows):
        for i in range(cols):
            bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]))
    bm.normal_update()
    bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=thickness)
    return bm


def peleryna(width=1.0, L=0.92, y_top=0.19, y_bot=0.3, clasps=True):
    def build(sl, J):
        _cape(sl, J, width, L, y_top, y_bot, clasps)
    return build


def _cape(sl, J, width, L, y_top, y_bot, clasps):
    sz = J['sh'].z

    def cape(u, v):
        a = u * math.radians(62)
        rw = lerp(0.2, 0.3, v) * width
        y0 = lerp(y_top, y_bot, v ** 1.3)
        x = math.sin(a) * rw
        y = y0 - (1 - math.cos(a)) * 0.13 * (1 - 0.4 * v) + 0.018 * math.sin(u * 3 * math.pi) * v
        return V(x, y, sz + 0.02 - v * L)
    sl.add(cloth_sheet(16, 10, cape), 'cape', 'chest')
    if not clasps:
        return
    for sg in (1, -1):
        sl.add(sphere(0.03, 0.02, 0.03, 10, 8), 'gold', 'chest', mtx((sg * 0.19, 0.06, sz + 0.0)))
        sl.add(box(0.06, 0.12, 0.03, 0.01), 'cape', 'chest', mtx((sg * 0.2, 0.12, sz - 0.01), (20, 0, 0)))
