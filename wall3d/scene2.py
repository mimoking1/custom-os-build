# Original 3D wallpaper renders, six DIFFERENT compositions (Blender Cycles). Usage: blender -b -P scene2.py -- NAME OUT.png
import bpy, sys, math, random
from mathutils import Vector

name, out = sys.argv[sys.argv.index("--") + 1:][:2]
random.seed(7)

def hexc(h):
    h = h.lstrip("#"); return tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4)) + (1,)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = 64
try: sc.cycles.use_denoising = True
except Exception: pass
sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
sc.render.filepath = out; sc.render.image_settings.file_format = "PNG"
sc.view_settings.view_transform = "Standard"

def mat(color, rough=0.3, metal=0.0, trans=0.0, ior=1.45, emit=0.0):
    m = bpy.data.materials.new("m"); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    c = hexc(color) if isinstance(color, str) else color
    b.inputs["Base Color"].default_value = c
    b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    for k in ("Transmission Weight", "Transmission"):
        if k in b.inputs: b.inputs[k].default_value = trans; break
    if "IOR" in b.inputs: b.inputs["IOR"].default_value = ior
    if emit:
        for k in ("Emission Color", "Emission"):
            if k in b.inputs: b.inputs[k].default_value = c; break
        if "Emission Strength" in b.inputs: b.inputs["Emission Strength"].default_value = emit
    return m
def glass(c): return mat(c, 0.03, 0, 1.0, 1.5)
def put(o, m):
    o.data.materials.append(m)
    for p in o.data.polygons: p.use_smooth = True
    return o
def world(top, strength=1.0):
    w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = hexc(top)
    w.node_tree.nodes["Background"].inputs[1].default_value = strength
def plane(color, rough=0.5, z=0, size=120):
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, z)); o = bpy.context.active_object
    o.data.materials.append(mat(color, rough)); return o
def sphere(x, y, z, r, m):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=(x, y, z), segments=64, ring_count=32); return put(bpy.context.active_object, m)
def light(kind, loc, energy, size=6, rot=None):
    bpy.ops.object.light_add(type=kind, location=loc, rotation=rot or (0, 0, 0)); l = bpy.context.active_object
    l.data.energy = energy
    if kind == "AREA": l.data.size = size
    return l
def cam(loc, rot, lens=40, ortho=None, fstop=None, focus=10):
    bpy.ops.object.camera_add(location=loc, rotation=tuple(math.radians(r) for r in rot)); c = bpy.context.active_object
    if ortho: c.data.type = "ORTHO"; c.data.ortho_scale = ortho
    else: c.data.lens = lens
    if fstop: c.data.dof.use_dof = True; c.data.dof.focus_distance = focus; c.data.dof.aperture_fstop = fstop
    sc.camera = c

if name == "dunes":            # warm rose desert, low sun, huge moon-sphere
    world("#f6c1b4", 0.9); sc.view_settings.exposure = -0.2
    f = plane("#e8a08a", 0.9)
    s = f.modifiers.new("s", "SUBSURF"); s.subdivision_type = "SIMPLE"; s.levels = 7; s.render_levels = 7
    t = bpy.data.textures.new("n", "CLOUDS"); t.noise_scale = 9.0; t.noise_depth = 1
    d = f.modifiers.new("d", "DISPLACE"); d.texture = t; d.strength = 3.2; d.mid_level = 0.45
    for p in f.data.polygons: p.use_smooth = True
    sphere(8, 45, 8, 5, mat("#fff2e6", 0.9, emit=1.6))
    light("SUN", (0, 0, 10), 3.5, rot=(math.radians(72), 0, math.radians(-70)))
    cam((0, -14, 3.5), (86, 0, 0), 32, fstop=16, focus=18)
elif name == "orbit":          # deep violet night, glowing concentric rings, frontal
    world("#0d0a24", 1.0); sc.view_settings.exposure = 0.0
    sphere(0, 0, 0, 1.3, mat("#ffe9c8", 0.2, emit=1.3))
    cols = ["#8b6bff", "#ff6bd6", "#6bd1ff", "#b49cff", "#ff9ae6"]
    for i, c in enumerate(cols):
        R = 2.6 + i * 1.25
        bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=0.06 + 0.02 * i, location=(0, 0, 0), rotation=(math.radians(68 + i * 4), math.radians(i * 7 - 10), math.radians(i * 22)), major_segments=160, minor_segments=24)
        put(bpy.context.active_object, mat(c, 0.2, emit=1.4))
        a = random.random() * 6.28
        sphere(R * math.cos(a), R * math.sin(a) * 0.35, 0.2, 0.22 + 0.04 * i, mat(c, 0.15, emit=1.8))
    light("AREA", (0, -8, 6), 500, 8)
    cam((0, -26, 2), (87, 0, 0), 38, fstop=8, focus=26)
elif name == "terraces":       # emerald stepped round podiums, high isometric
    world("#d7f3e3", 1.0); sc.view_settings.exposure = -0.3
    plane("#a8e3c4", 0.6)
    ms = [mat("#1fb36b", 0.3), mat("#eafff3", 0.25), mat("#0c7a47", 0.35), mat("#6fd6a0", 0.2, 0.8)]
    for k, (x, y, n) in enumerate([(-4.5, 1, 5), (1.5, 2.5, 7), (6.0, -0.5, 4)]):
        for i in range(n):
            bpy.ops.mesh.primitive_cylinder_add(radius=3.0 - i * (2.6 / n), depth=0.55, location=(x, y, 0.28 + i * 0.55), vertices=96)
            o = bpy.context.active_object; b = o.modifiers.new("b", "BEVEL"); b.width = 0.08; b.segments = 4
            put(o, ms[(i + k) % 4])
    light("AREA", (-6, -6, 12), 1500, 10); light("AREA", (8, -2, 6), 400, 6)
    cam((13, -15, 12), (60, 0, 41), ortho=22)
elif name == "towers":         # gold city of beveled blocks, iso orthographic, long shadows
    world("#fff0c8", 1.0); sc.view_settings.exposure = -0.25
    plane("#f4d078", 0.7)
    ms = [mat("#f2b705", 0.3), mat("#fffaf0", 0.25), mat("#c98a00", 0.35), mat("#ffd966", 0.1, 0.9)]
    random.seed(21)
    for gx in range(-7, 8):
        for gy in range(-3, 6):
            if random.random() < 0.28: continue
            h = 0.6 + random.random() ** 2 * 6.5
            bpy.ops.mesh.primitive_cube_add(size=1, location=(gx * 1.5, gy * 1.5, h / 2)); o = bpy.context.active_object
            o.scale = (1.0, 1.0, h); b = o.modifiers.new("b", "BEVEL"); b.width = 0.05; b.segments = 3
            put(o, ms[random.randrange(4)])
    light("SUN", (0, 0, 10), 4.0, rot=(math.radians(50), 0, math.radians(35)))
    cam((14, -16, 12), (58, 0, 41), ortho=32)
elif name == "pillars":        # slate grid of rounded pillars rising like a wave, low angle
    world("#dde3ea", 1.0); sc.view_settings.exposure = -0.2
    plane("#8f9bab", 0.5)
    m1, m2 = mat("#5a6b82", 0.25), mat("#f4f6f9", 0.2)
    for gx in range(-14, 15):
        for gy in range(-2, 12):
            h = 0.5 + 1.8 * (1 + math.sin(gx * 0.45 + gy * 0.3)) * (1 + math.cos(gy * 0.5 - gx * 0.2)) / 2
            bpy.ops.mesh.primitive_cylinder_add(radius=0.34, depth=h, location=(gx * 0.85, gy * 0.85, h / 2), vertices=24)
            o = bpy.context.active_object
            put(o, m2 if (gx + gy) % 5 == 0 else m1)
    light("AREA", (-6, -8, 10), 1400, 8); light("AREA", (8, -3, 4), 300, 6)
    cam((0, -9, 1.8), (84, 0, 0), 40, fstop=5.6, focus=12)
elif name == "bubbles":        # coral gradient, no floor, many floating glass bubbles, strong bokeh
    world("#ff8a73", 1.0); sc.view_settings.exposure = -0.1
    bpy.ops.mesh.primitive_plane_add(size=120, location=(0, 25, 0), rotation=(math.radians(90), 0, 0))
    o = bpy.context.active_object; o.data.materials.append(mat("#ff6f5a", 0.6, emit=1.2))
    random.seed(5)
    cs = ["#ffd1c8", "#fff4f0", "#ffb09f", "#ffe3a8", "#ffffff"]
    for i in range(46):
        r = 0.25 + random.random() ** 2.2 * 1.6
        x = random.uniform(-9, 9); y = random.uniform(-2, 14); z = random.uniform(-3.5, 3.5)
        sphere(x, y, z, r, glass(random.choice(cs)) if i % 3 else mat(random.choice(cs), 0.12, 0.9))
    light("AREA", (-5, -8, 8), 1500, 9); light("AREA", (8, -6, 2), 500, 6)
    cam((0, -14, 0), (90, 0, 0), 38, fstop=2.4, focus=14)
bpy.ops.render.render(write_still=True)
