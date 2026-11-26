# Original 3D wallpaper renders (Blender Cycles). Usage: blender -b -P scene.py -- NAME OUT.png
import bpy, sys, math, random
from mathutils import Vector

name, out = sys.argv[sys.argv.index("--") + 1:][:2]

def hexc(h):
    h = h.lstrip("#"); return tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4)) + (1,)

P = {
 "rose":    dict(sky="#f7d6e0", floor="#f2a7c3", a="#ff7aa8", b="#ffe3ee", c="#d94f84", layout="spheres", seed=3),
 "violet":  dict(sky="#e4dcff", floor="#a99af0", a="#7b61ff", b="#efeaff", c="#4b33c9", layout="torus", seed=5),
 "emerald": dict(sky="#d6f5e4", floor="#6fd6a0", a="#1fb36b", b="#eafff3", c="#0c7a47", layout="waves", seed=11),
 "gold":    dict(sky="#fff3cf", floor="#f6d77a", a="#f2b705", b="#fffaf0", c="#c98a00", layout="cubes", seed=2),
 "slate":   dict(sky="#dde3ea", floor="#8f9bab", a="#5a6b82", b="#f4f6f9", c="#2f3d52", layout="torus", seed=8),
 "coral":   dict(sky="#ffe0d6", floor="#ff9b86", a="#ff5f4a", b="#fff0eb", c="#c93a28", layout="spheres", seed=13),
}[name]
random.seed(P["seed"])

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"
sc.cycles.device = "CPU"
sc.cycles.samples = 64
try: sc.cycles.use_denoising = True
except Exception: pass
sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
sc.render.filepath = out
sc.render.image_settings.file_format = "PNG"

def mat(color, rough=0.25, metal=0.0, trans=0.0, ior=1.45):
    m = bpy.data.materials.new("m"); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = hexc(color) if isinstance(color, str) else color
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    for k in ("Transmission Weight", "Transmission"):
        if k in b.inputs: b.inputs[k].default_value = trans; break
    if "IOR" in b.inputs: b.inputs["IOR"].default_value = ior
    return m

def put(obj, m):
    obj.data.materials.append(m)
    for p in obj.data.polygons: p.use_smooth = True
    return obj

# world: soft sky gradient
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
bg = w.node_tree.nodes["Background"]; bg.inputs[0].default_value = hexc(P["sky"]); bg.inputs[1].default_value = 0.85

# floor
bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 0, 0))
fl = bpy.context.active_object
if P["layout"] == "waves":
    bpy.ops.object.mode_set(mode="OBJECT")
    mod = fl.modifiers.new("s", "SUBSURF"); mod.subdivision_type = "SIMPLE"; mod.levels = 7; mod.render_levels = 7
    tex = bpy.data.textures.new("n", "CLOUDS"); tex.noise_scale = 3.2
    d = fl.modifiers.new("d", "DISPLACE"); d.texture = tex; d.strength = 1.4; d.mid_level = 0.5
fl.data.materials.append(mat(P["floor"], rough=0.35 if P["layout"] != "waves" else 0.8))
for p in fl.data.polygons: p.use_smooth = True

# back wall for the soft horizon band
bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 14, 10), rotation=(math.radians(90), 0, 0))
wall = bpy.context.active_object; wall.data.materials.append(mat(P["sky"], rough=0.9))

glass = lambda c: mat(c, rough=0.03, trans=1.0, ior=1.5)
def sphere(x, y, r, m):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=(x, y, r + (0.35 if P["layout"] == "waves" else 0)), segments=96, ring_count=48)
    return put(bpy.context.active_object, m)

L = P["layout"]
if L == "spheres":
    specs = [(-3.2, 1.0, 1.1, mat(P["b"], 0.3)), (-0.8, 2.2, 1.5, glass(P["a"])), (1.6, 0.4, 0.9, mat(P["a"], 0.12, 0.9)),
             (3.2, 2.0, 1.2, mat(P["c"], 0.35)), (-1.2, -0.6, 0.55, glass(P["b"])), (0.4, -1.1, 0.4, mat(P["b"], 0.2)),
             (-4.8, 3.2, 0.8, mat(P["a"], 0.2)), (5.0, 0.2, 0.6, glass(P["c"]))]
    for s in specs: sphere(*s)
elif L == "torus":
    for i, (x, y, z, rot, m) in enumerate([(-1.4, 2.0, 1.7, (1.1, 0.3, 0.2), glass(P["a"])), (0.9, 2.4, 1.5, (0.4, 1.0, 0.1), mat(P["b"], 0.18, 0.9)),
                                           (-0.2, 1.8, 1.9, (1.5, 0.2, 0.9), mat(P["c"], 0.3))]):
        bpy.ops.mesh.primitive_torus_add(major_radius=1.5 - i * 0.15, minor_radius=0.5, location=(x, y, z), rotation=rot, major_segments=96, minor_segments=48)
        put(bpy.context.active_object, m)
    sphere(-4.2, 0.6, 0.9, mat(P["b"], 0.25)); sphere(4.0, 0.9, 1.0, glass(P["b"])); sphere(2.8, -0.8, 0.5, mat(P["a"], 0.1, 1.0))
elif L == "cubes":
    for x, y, s, rz, m in [(-3.6, 1.4, 1.0, 0.5, mat(P["a"], 0.3)), (-0.6, 2.6, 1.3, 0.9, glass(P["b"])), (2.6, 1.6, 1.1, 0.2, mat(P["c"], 0.25)),
                           (0.8, 0.0, 0.6, 0.7, mat(P["b"], 0.15, 0.9)), (4.8, 3.0, 0.9, 1.2, glass(P["a"]))]:
        bpy.ops.mesh.primitive_cube_add(size=2 * s, location=(x, y, s), rotation=(0, 0, rz))
        bev = bpy.context.active_object.modifiers.new("b", "BEVEL"); bev.width = 0.12 * s; bev.segments = 5
        put(bpy.context.active_object, m)
    sphere(-1.8, -0.4, 0.5, mat(P["b"], 0.2))
else:  # waves
    sphere(-2.2, 1.6, 1.0, mat(P["b"], 0.3)); sphere(1.4, 2.4, 1.4, glass(P["a"])); sphere(3.6, 0.6, 0.7, mat(P["c"], 0.15, 0.9)); sphere(-0.6, -0.4, 0.45, glass(P["b"]))

# lights + camera
bpy.ops.object.light_add(type="AREA", location=(-5, -6, 9)); a = bpy.context.active_object; a.data.energy = 1100; a.data.size = 8
bpy.ops.object.light_add(type="AREA", location=(6, -3, 5)); a2 = bpy.context.active_object; a2.data.energy = 330; a2.data.size = 6
bpy.ops.object.camera_add(location=(0, -9.5, 3.0), rotation=(math.radians(76), 0, 0)); cam = bpy.context.active_object
cam.data.lens = 42; cam.data.dof.use_dof = True; cam.data.dof.focus_distance = 11; cam.data.dof.aperture_fstop = 8
sc.camera = cam
sc.view_settings.view_transform = "Standard"; sc.view_settings.exposure = -0.35
bpy.ops.render.render(write_still=True)
