"""Wspólne narzędzia do budowy modułowych jednostek (Blender / bpy).

Każda jednostka składa się z:
  * szkieletu o WSPÓLNYCH nazwach kości (ten sam układ dla każdej jednostki,
    różnią się tylko proporcje) - dzięki temu części i animacje można mieszać,
  * slotów (Head, Helmet, Torso, Arms, Legs, Weapon, Shield, ...) - każdy slot to
    osobny mesh przypięty sztywno do kości (wagi 1.0), więc w Godot można je
    podmieniać / łączyć przy tworzeniu fuzji jednostek.
"""
import math
import random

import bpy  # noqa: F401  (musi być przed bmesh)
import bmesh
from mathutils import Matrix, Vector, Euler

# ---------------------------------------------------------------- helpers

def V(x, y=None, z=None):
    if y is None:
        return Vector(x)
    return Vector((x, y, z))


def srgb(hexstr):
    h = hexstr.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.fps = 30
    sc.unit_settings.system = 'METRIC'


def make_material(name, hexcol, rough=0.7, metal=0.0, emit=0.0):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    try:
        m.use_nodes = True
    except Exception:
        pass
    col = srgb(hexcol)
    bsdf = m.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*col, 1)
    bsdf.inputs['Roughness'].default_value = rough
    bsdf.inputs['Metallic'].default_value = metal
    if emit > 0:
        bsdf.inputs['Emission Color'].default_value = (*col, 1)
        bsdf.inputs['Emission Strength'].default_value = emit
    m.diffuse_color = (*col, 1)
    return m


def mtx(loc=(0, 0, 0), rot=(0, 0, 0)):
    return Matrix.Translation(V(loc)) @ Euler([math.radians(a) for a in rot]).to_matrix().to_4x4()


def frame(origin, z_axis, x_hint=(1, 0, 0)):
    """Macierz z lokalną osią Z wzdłuż z_axis, X możliwie wzdłuż x_hint."""
    z = V(z_axis).normalized()
    x = V(x_hint)
    x = (x - z * x.dot(z))
    if x.length < 1e-6:
        x = V(0, 1, 0) - z * z.y
    x.normalize()
    y = z.cross(x)
    m = Matrix((x, y, z)).transposed().to_4x4()
    m.translation = V(origin)
    return m


def seg(p0, p1, x_hint=(1, 0, 0)):
    """Macierz ustawiająca prymityw (oś Z, wycentrowany) między p0 a p1."""
    p0, p1 = V(p0), V(p1)
    return frame((p0 + p1) / 2, p1 - p0, x_hint)


# ---------------------------------------------------------------- primitives (temp bmesh)

def box(sx, sy, sz, bevel=0.0, segs=2):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(sx, sy, sz), verts=bm.verts)
    if bevel > 0:
        bevel = min(bevel, 0.49 * min(sx, sy, sz))
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=bevel, offset_type='OFFSET',
                        segments=segs, profile=0.5, affect='EDGES', clamp_overlap=True)
    return bm


def cyl(r1, r2, depth, segs=16, bevel=0.0):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segs,
                          radius1=r1, radius2=r2, depth=depth)
    if bevel > 0:
        bm.normal_update()
        rim = [e for e in bm.edges if len(e.link_faces) == 2 and
               sum(abs(f.normal.z) > 0.9 for f in e.link_faces) == 1]
        bmesh.ops.bevel(bm, geom=rim, offset=bevel, offset_type='OFFSET', segments=2,
                        profile=0.5, affect='EDGES', clamp_overlap=True)
    return bm


def sphere(sx, sy=None, sz=None, u=16, v=10):
    sy = sx if sy is None else sy
    sz = sx if sz is None else sz
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=v, radius=1.0)
    bmesh.ops.scale(bm, vec=(sx, sy, sz), verts=bm.verts)
    return bm


def ico(r, sub=1):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=r)
    return bm


def cut_below(bm, z):
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < z], context='VERTS')
    return bm


def taper(bm, bottom=1.0, top=1.0, axis='xy'):
    zs = [v.co.z for v in bm.verts]
    z0, z1 = min(zs), max(zs)
    for v in bm.verts:
        t = (v.co.z - z0) / max(1e-6, z1 - z0)
        f = bottom + (top - bottom) * t
        if 'x' in axis:
            v.co.x *= f
        if 'y' in axis:
            v.co.y *= f
    return bm


def jitter(bm, amount, seed):
    rng = random.Random(seed)
    for v in bm.verts:
        v.co += V(rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-1, 1)) * amount
    return bm


def rock(sx, sy, sz, seed, rough=0.12, bevel=0.22):
    """Kanciasty blok skalny: sfazowany prostopadłościan z losowym zniekształceniem."""
    bm = box(sx, sy, sz, bevel=bevel * min(sx, sy, sz), segs=1)
    return jitter(bm, rough * min(sx, sy, sz), seed)


# ---------------------------------------------------------------- slot = jeden mesh

class Slot:
    def __init__(self, name):
        self.name = name
        self.bm = bmesh.new()
        self.dl = self.bm.verts.layers.deform.verify()
        self.mats = []
        self.groups = []

    def add(self, tbm, mat, bone, M=None):
        if M is not None:
            bmesh.ops.transform(tbm, matrix=M, verts=tbm.verts)
        if mat not in self.mats:
            self.mats.append(mat)
        if bone not in self.groups:
            self.groups.append(bone)
        mi, gi = self.mats.index(mat), self.groups.index(bone)
        vmap = {}
        for v in tbm.verts:
            nv = self.bm.verts.new(v.co)
            nv[self.dl][gi] = 1.0
            vmap[v] = nv
        for f in tbm.faces:
            try:
                nf = self.bm.faces.new([vmap[v] for v in f.verts])
                nf.material_index = mi
            except ValueError:
                pass
        tbm.free()

    def build(self, arm_obj, materials, prefix):
        me = bpy.data.meshes.new(f'{prefix}_{self.name}')
        bmesh.ops.recalc_face_normals(self.bm, faces=self.bm.faces)
        self.bm.to_mesh(me)
        self.bm.free()
        for m in self.mats:
            me.materials.append(materials[m])
        me.shade_smooth()
        me.set_sharp_from_angle(angle=math.radians(38))
        ob = bpy.data.objects.new(f'{prefix}_{self.name}', me)
        bpy.context.scene.collection.objects.link(ob)
        for g in self.groups:
            ob.vertex_groups.new(name=g)
        ob.parent = arm_obj
        mod = ob.modifiers.new('Armature', 'ARMATURE')
        mod.object = arm_obj
        return ob


# ---------------------------------------------------------------- szkielet

BONES = [  # nazwa, rodzic
    ('root', None), ('hips', 'root'), ('spine', 'hips'), ('chest', 'spine'),
    ('neck', 'chest'), ('head', 'neck'),
]
for _s in ('L', 'R'):
    BONES += [(f'shoulder.{_s}', 'chest'), (f'upper_arm.{_s}', f'shoulder.{_s}'),
              (f'forearm.{_s}', f'upper_arm.{_s}'), (f'hand.{_s}', f'forearm.{_s}'),
              (f'thigh.{_s}', 'hips'), (f'shin.{_s}', f'thigh.{_s}'), (f'foot.{_s}', f'shin.{_s}')]
BONES.append(('prop.R', 'hand.R'))  # rekwizyt w prawej dłoni (np. kamień do rzutu)


def joints(s):
    """Pozycje stawów z parametrów proporcji (metry, Z w górę, przód = -Y)."""
    J = {}
    knee = s['ankle'] + s['shin']
    hip = knee + s['thigh']
    J['root'] = V(0, 0, 0)
    J['hip'] = V(0, 0, hip)
    J['spine_base'] = V(0, 0, hip + s['spine'] * 0.35)
    J['chest_base'] = V(0, 0, hip + s['spine'])
    J['sh'] = V(0, 0, hip + s['spine'] + s['chest'])
    J['neck_top'] = J['sh'] + V(0, -s.get('head_fwd', 0.0), s['neck'])
    J['head_top'] = J['neck_top'] + V(0, 0, s['head'])
    a = math.radians(s['arm_angle'])
    f = math.radians(s['forearm_fwd'])
    for sg, S in ((1, '.L'), (-1, '.R')):
        shj = V(sg * s['sh_w'], 0, J['sh'].z - s['sh_drop'])
        d1 = V(sg * math.sin(a), 0, -math.cos(a))
        d2 = V(sg * math.sin(a), -math.sin(f), -math.cos(a)).normalized()
        J['clav' + S] = V(sg * 0.06, 0, J['sh'].z - s['sh_drop'])
        J['shoulder' + S] = shj
        J['elbow' + S] = shj + d1 * s['upper_arm']
        J['wrist' + S] = J['elbow' + S] + d2 * s['forearm']
        J['hand_end' + S] = J['wrist' + S] + d2 * s['hand']
        J['hand_dir' + S] = d2
        J['hipj' + S] = V(sg * s['hip_w'], 0, hip)
        J['knee' + S] = V(sg * s['hip_w'], 0, knee)
        J['ankle' + S] = V(sg * s['hip_w'], 0, s['ankle'])
        J['toe' + S] = V(sg * s['hip_w'], -s['foot'], 0.02)
    J['prop.R'] = J['wrist.R'] + J['hand_dir.R'] * s['hand'] * s.get('prop_at', 1.15)
    return J


def build_armature(name, J):
    arm = bpy.data.armatures.new(name + '_Rig')
    ob = bpy.data.objects.new(name + '_Rig', arm)
    bpy.context.scene.collection.objects.link(ob)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.mode_set(mode='EDIT')
    ht = {
        'root': (J['root'], J['root'] + V(0, 0.25, 0)),
        'hips': (J['hip'], J['spine_base']),
        'spine': (J['spine_base'], J['chest_base']),
        'chest': (J['chest_base'], J['sh']),
        'neck': (J['sh'], J['neck_top']),
        'head': (J['neck_top'], J['head_top']),
    }
    for S in ('.L', '.R'):
        ht['shoulder' + S] = (J['clav' + S], J['shoulder' + S])
        ht['upper_arm' + S] = (J['shoulder' + S], J['elbow' + S])
        ht['forearm' + S] = (J['elbow' + S], J['wrist' + S])
        ht['hand' + S] = (J['wrist' + S], J['hand_end' + S])
        ht['thigh' + S] = (J['hipj' + S], J['knee' + S])
        ht['shin' + S] = (J['knee' + S], J['ankle' + S])
        ht['foot' + S] = (J['ankle' + S], J['toe' + S])
    ht['prop.R'] = (J['prop.R'], J['prop.R'] + V(0, 0, 0.12))
    ebs = {}
    for bname, parent in BONES:
        eb = arm.edit_bones.new(bname)
        eb.head, eb.tail = ht[bname]
        if bname.startswith('foot') or bname == 'root':
            eb.align_roll(V(0, 0, 1))
        else:
            eb.align_roll(V(0, -1, 0))
        if parent:
            eb.parent = ebs[parent]
            eb.use_connect = False
        ebs[bname] = eb
    bpy.ops.object.mode_set(mode='OBJECT')
    for pb in ob.pose.bones:
        pb.rotation_mode = 'XYZ'
    return ob


# ---------------------------------------------------------------- animacje

def bake_action(arm_obj, name, frames, posefn, step=2, rest_scale=None):
    """posefn(t in [0,1]) -> {kość: (rot_xyz_stopnie, loc_xyz[, skala])}; t=0 i t=1 identyczne => pętla."""
    rest_scale = rest_scale or {}
    act = bpy.data.actions.new(name)
    act.use_fake_user = True
    arm_obj.animation_data_create()
    arm_obj.animation_data.action = act
    for f in list(range(0, frames, step)) + [frames]:
        pose = posefn(f / frames)
        for pb in arm_obj.pose.bones:
            e = pose.get(pb.name, ((0, 0, 0), (0, 0, 0)))
            r, l = e[0], e[1]
            sc = e[2] if len(e) > 2 and e[2] is not None else rest_scale.get(pb.name, (1, 1, 1))
            pb.rotation_euler = [math.radians(a) for a in r]
            pb.location = l
            pb.scale = sc
            pb.keyframe_insert('rotation_euler', frame=f, group=pb.name)
            pb.keyframe_insert('location', frame=f, group=pb.name)
            pb.keyframe_insert('scale', frame=f, group=pb.name)
    return act


def set_action(arm_obj, act, frame=0):
    arm_obj.animation_data.action = act
    try:
        if act.slots and arm_obj.animation_data.action_slot is None:
            arm_obj.animation_data.action_slot = act.slots[0]
    except AttributeError:
        pass
    bpy.context.scene.frame_set(frame)


def keyposes(keys, base):
    """keys: [(t, {kość: (rot, loc[, skala])})], każda poza nakładana na `base`.
    Interpolacja smoothstep między kolejnymi pozami kluczowymi."""
    full = []
    for t, p in keys:
        d = dict(base)
        d.update(p)
        full.append((t, d))
    bones = set(b for _, p in full for b in p)

    def norm(e):
        e = tuple(e) + (None,) * (3 - len(e))
        return e

    def fn(t):
        i = 0
        while i < len(full) - 2 and t > full[i + 1][0]:
            i += 1
        (t0, p0), (t1, p1) = full[i], full[i + 1]
        u = min(1.0, max(0.0, (t - t0) / max(1e-6, t1 - t0)))
        u = u * u * (3 - 2 * u)
        out = {}
        for b in bones:
            a = norm(p0.get(b, ((0, 0, 0), (0, 0, 0))))
            c = norm(p1.get(b, ((0, 0, 0), (0, 0, 0))))
            rot = tuple(x + (y - x) * u for x, y in zip(a[0], c[0]))
            loc = tuple(x + (y - x) * u for x, y in zip(a[1], c[1]))
            sc = None
            if a[2] is not None and c[2] is not None:
                sc = tuple(x + (y - x) * u for x, y in zip(a[2], c[2]))
            out[b] = (rot, loc, sc)
        return out
    return fn


def gait(p):
    """Parametryczny cykl chodu + oddech. p = słownik amplitud jednostki."""
    def walk(t):
        ph = 2 * math.pi * t
        s, c = math.sin(ph), math.cos(ph)
        A, K, B = p['thigh'], p['knee'], p['arm']
        pose = {}
        for sg, S in ((1, '.L'), (-1, '.R')):
            ss = s * sg
            cc = c * sg
            pose['thigh' + S] = ((A * ss, 0, 0), (0, 0, 0))
            pose['shin' + S] = ((-p['knee_base'] - K * max(0.0, cc), 0, 0), (0, 0, 0))
            pose['foot' + S] = ((-0.35 * A * ss + 0.4 * K * max(0.0, cc) * 0.5, 0, 0), (0, 0, 0))
            arm_amp = B * p.get('arm_scale' + S, 1.0)
            pose['upper_arm' + S] = ((-arm_amp * ss, 0, 0), (0, 0, 0))
            pose['forearm' + S] = ((p['forearm_base' + S] + 0.35 * arm_amp * max(0.0, -ss), 0, 0), (0, 0, 0))
        T, R = p['twist'], p['sway']
        pose['hips'] = ((0, T * s, R * c), (0, 0, 0))
        pose['spine'] = ((p['lean'], 0, 0), (0, p['bob'] * math.cos(2 * ph), 0))
        pose['chest'] = ((0, -1.6 * T * s, -R * c), (0, 0, 0))
        pose['head'] = ((-p['lean'] * 0.7, 0.8 * T * s, 0.6 * R * c), (0, 0, 0))
        return pose

    def idle(t):
        ph = 2 * math.pi * t
        b = math.sin(ph)
        pose = {
            'spine': ((0, 0, 0), (0, p['breath_loc'] * b, 0)),
            'chest': ((p['breath'] * b, 0, 0), (0, 0, 0)),
            'head': ((-0.8 * p['breath'] * b, 0.6 * p['breath'] * math.sin(ph * 0.5 * 2), 0), (0, 0, 0)),
        }
        for sg, S in ((1, '.L'), (-1, '.R')):
            pose['upper_arm' + S] = ((0.5 * p['breath'] * b, 0, sg * p['breath'] * b), (0, 0, 0))
            pose['forearm' + S] = ((p['forearm_base' + S] * 0.6 + 0.5 * p['breath'] * b, 0, 0), (0, 0, 0))
            pose['shin' + S] = ((-1.0, 0, 0), (0, 0, 0))
        return pose

    return walk, idle


# ---------------------------------------------------------------- budowa jednostki

def build_unit(unit, offset=(0, 0, 0)):
    name = unit['name']
    J = joints(unit['skeleton'])
    arm = build_armature(name, J)
    mats = {k: make_material(f'{name}_{k}', *v) for k, v in unit['palette'].items()}
    meshes = []
    for slot_name, fn in unit['slots']:
        sl = Slot(slot_name)
        fn(sl, J)
        meshes.append(sl.build(arm, mats, name))
    an = unit['anim']
    rs = an.get('rest_scale', {})
    walk, idle = gait(an)
    actions = {
        'walk': bake_action(arm, 'Walk_loop', an['walk_frames'], walk, rest_scale=rs),
        'idle': bake_action(arm, 'Idle_loop', an['idle_frames'], idle, step=3, rest_scale=rs),
    }
    atk = unit.get('attack')
    if atk:
        fn = keyposes(atk['keys'], idle(0.0))
        actions['attack'] = bake_action(arm, atk['name'], atk['frames'], fn, step=1, rest_scale=rs)
    set_action(arm, actions['idle'], 0)
    arm.location = V(offset)
    return {'arm': arm, 'meshes': meshes, 'J': J, 'actions': actions}


def build_static(name, fn, palette, offset=(0, 0, 0)):
    """Obiekt bez szkieletu (pocisk, efekt) – fn(slot) buduje geometrię wokół (0,0,0)."""
    mats = {k: make_material(f'{name}_{k}', *v) for k, v in palette.items()}
    sl = Slot(name)
    fn(sl)
    me = bpy.data.meshes.new(name)
    bmesh.ops.recalc_face_normals(sl.bm, faces=sl.bm.faces)
    sl.bm.to_mesh(me)
    sl.bm.free()
    for m in sl.mats:
        me.materials.append(mats[m])
    me.shade_smooth()
    me.set_sharp_from_angle(angle=math.radians(38))
    ob = bpy.data.objects.new(name, me)
    ob.location = V(offset)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def export_static(obj, path):
    for o in bpy.context.scene.objects:
        o.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', use_selection=True, export_apply=True,
                              export_animations=False, export_yup=True, export_materials='EXPORT')


def export_glb(built, path):
    for o in bpy.context.scene.objects:
        o.select_set(False)
    built['arm'].select_set(True)
    for m in built['meshes']:
        m.select_set(True)
    bpy.context.view_layer.objects.active = built['arm']
    bpy.ops.export_scene.gltf(
        filepath=path, export_format='GLB', use_selection=True, export_apply=True,
        export_animations=True, export_animation_mode='ACTIONS', export_skins=True,
        export_yup=True, export_materials='EXPORT')


# ---------------------------------------------------------------- podgląd (render)

def setup_stage(res=900, samples=48):
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.samples = samples
    try:
        sc.cycles.use_denoising = True
        sc.cycles.denoiser = 'OPENIMAGEDENOISE'
    except Exception:
        pass
    sc.render.resolution_x = res
    sc.render.resolution_y = res
    try:
        sc.view_settings.view_transform = 'AgX'
        sc.view_settings.look = 'AgX - Medium High Contrast'
    except Exception:
        pass
    world = bpy.data.worlds.new('World')
    sc.world = world
    try:
        world.use_nodes = True
    except Exception:
        pass
    bg = world.node_tree.nodes.get('Background')
    bg.inputs['Color'].default_value = (*srgb('#8fa3bf'), 1)
    bg.inputs['Strength'].default_value = 0.55
    # podłoże
    bm = bmesh.new()
    bmesh.ops.create_circle(bm, cap_ends=True, segments=64, radius=12)
    me = bpy.data.meshes.new('Ground')
    bm.to_mesh(me)
    bm.free()
    me.materials.append(make_material('Ground', '#5b6b4c', rough=0.95))
    g = bpy.data.objects.new('Ground', me)
    sc.collection.objects.link(g)
    # światła
    def light(kind, energy, loc, rot, size=None, color='#ffffff'):
        ld = bpy.data.lights.new(kind + '_l', kind)
        ld.energy = energy
        ld.color = srgb(color)
        if size is not None:
            if kind == 'SUN':
                ld.angle = math.radians(size)
            else:
                ld.size = size
        lo = bpy.data.objects.new(kind + '_o', ld)
        lo.location = loc
        lo.rotation_euler = [math.radians(a) for a in rot]
        sc.collection.objects.link(lo)
    light('SUN', 4.2, (0, 0, 10), (48, 0, -38), size=4, color='#fff2dd')
    light('AREA', 400, (4, -3, 3), (65, 0, 55), size=4, color='#cfe0ff')
    light('AREA', 500, (-2, 4, 3.5), (-60, 0, -25), size=3, color='#ffffff')


def render_view(path, target, dist, pitch, yaw, lens=50):
    sc = bpy.context.scene
    cam = sc.camera
    if cam is None:
        cd = bpy.data.cameras.new('Cam')
        cam = bpy.data.objects.new('Cam', cd)
        sc.collection.objects.link(cam)
        sc.camera = cam
    cam.data.lens = lens
    p, y = math.radians(pitch), math.radians(yaw)
    target = V(target)
    cam.location = target + V(math.sin(y) * math.cos(p), -math.cos(y) * math.cos(p), math.sin(p)) * dist
    cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
