import bpy, math, random, sys
from mathutils import Vector
name = sys.argv[sys.argv.index('--')+1]
OUT = sys.argv[sys.argv.index('--')+2]
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
def hexc(h, k=1.0):
    h = h.lstrip('#'); r,g,b = [int(h[i:i+2],16)/255 for i in (0,2,4)]
    f = lambda c: (c**2.2)*k
    return (f(r),f(g),f(b),1)
FULL = '#08e8de'; LIVE = '#4fb2f7'
ACC = FULL if name.startswith('aqua') else LIVE
FLOOR = '#d9fbf8' if name.startswith('aqua') else '#dcecfb'
def inp(n, *names):
    for k in names:
        if k in n.inputs: return n.inputs[k]
def M(col, rough=0.25, metal=0.0, trans=0.0, ior=1.45):
    m = bpy.data.materials.new('m'); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    inp(b,'Base Color').default_value = col
    inp(b,'Roughness').default_value = rough
    inp(b,'Metallic').default_value = metal
    inp(b,'IOR').default_value = ior
    t = inp(b,'Transmission Weight','Transmission')
    if t: t.default_value = trans
    return m
def put(o, mat, smooth=True):
    o.data.materials.append(mat)
    if smooth:
        for p in o.data.polygons: p.use_smooth = True
    return o
def sphere(loc, r, mat):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=64, ring_count=32)
    return put(bpy.context.object, mat)
def torus(loc, R, r, rot, mat):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, major_segments=96, minor_segments=48, location=loc, rotation=rot)
    return put(bpy.context.object, mat)
def rbox(loc, size, mat, bev=0.08):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o = bpy.context.object; o.scale = (size[0]/2,size[1]/2,size[2]/2)
    bpy.ops.object.transform_apply(scale=True)
    m = o.modifiers.new('b','BEVEL'); m.width = bev; m.segments = 6
    return put(o, mat)
def cyl(loc, r, h, mat, bev=0.1):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, location=loc, vertices=96)
    o = bpy.context.object
    m = o.modifiers.new('b','BEVEL'); m.width = bev; m.segments = 6
    return put(o, mat)
glass = M(hexc(ACC), 0.04, 0, 0.92)
acc = M(hexc(ACC), 0.35)
white = M((0.9,0.92,0.93,1), 0.3)
pearl = M((0.95,0.96,0.97,1), 0.08)
chrome = M((0.9,0.93,0.96,1), 0.03, 1.0)
# floor
bpy.ops.mesh.primitive_plane_add(size=400, location=(0,0,0))
put(bpy.context.object, M(hexc(FLOOR), 0.28), smooth=False)
# world
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
bg = w.node_tree.nodes['Background']; bg.inputs[0].default_value = hexc(FLOOR, 1.0); bg.inputs[1].default_value = 1.1
random.seed(7)
def scatter(n, xr, yr, rmin, rmax, mats):
    for i in range(n):
        r = random.uniform(rmin, rmax)
        sphere((random.uniform(*xr), random.uniform(*yr), r), r, random.choice(mats))
cam_loc, cam_tgt, lens = (0,-9,2.4),(0,0,1.1),50
if name == 'aqua-halo':
    torus((0,0.4,2.05), 1.7, 0.38, (math.pi/2,0,0), glass)
    sphere((0.1,-0.9,0.9), 0.9, pearl)
    sphere((-3.3,-1.2,0.55), 0.55, acc)
    sphere((3.1,-0.4,0.75), 0.75, glass)
    sphere((2.2,-2.2,0.4), 0.4, chrome)
    for x,h,r in ((-5.2,3.6,0.8),(-6.8,2.2,0.7),(5.4,3.0,0.8),(7.0,4.2,0.8)):
        cyl((x,3.5,h/2), r, h, acc if x<0 else white)
    scatter(14,(-5,5),(-3.5,-0.6),0.12,0.25,[glass,white,acc,chrome])
elif name == 'aqua-cascade':
    cam_loc, cam_tgt = (2.5,-11,4.2),(0.3,1.8,1.6)
    for i in range(7):
        h = 0.5+i*0.5
        rbox((-5.1+i*1.75, i*1.05, h/2), (1.65,1.65,h), (white,glass,acc)[i%3])
    sphere((-5.1+3*1.75, 3*1.05, 0.5+3*0.5+0.55), 0.55, pearl)
    sphere((-5.1+5*1.75, 5*1.05, 0.5+5*0.5+0.6), 0.6, chrome)
    sphere((-1.5,-2.0,0.7), 0.7, glass)
    sphere((1.4,-2.6,0.45), 0.45, acc)
    scatter(12,(-6,6),(-4.5,-1.2),0.12,0.25,[glass,white,acc])
elif name == 'sky-arches':
    cam_loc, cam_tgt, lens = (0,-7.5,1.5),(0,6,1.4),35
    for i in range(6):
        torus((0,i*3.2,0), 2.1, 0.3, (math.pi/2,0,0), glass if i%2==0 else white)
    sphere((0,0.0,0.7), 0.7, pearl)
    sphere((-1.1,2.4,1.3), 0.45, chrome)
    sphere((1.2,5.4,1.0), 0.5, acc)
    scatter(14,(-4.5,4.5),(-4,9),0.12,0.3,[glass,white,acc])
else:
    cam_loc, cam_tgt = (0,-12,3.4),(0,0,3.0)
    cyl((0,0,3.2), 0.22, 6.4, glass, 0.05)
    cyl((0,0,0.08), 3.3, 0.16, white, 0.05)
    for i in range(26):
        t = i*0.5
        sphere((math.cos(t)*2.3, math.sin(t)*2.3, 0.4+i*0.22), 0.36-0.005*i, (glass,pearl,acc)[i%3])
    sphere((3.6,-1.8,0.5), 0.5, chrome)
    sphere((-3.9,-2.0,0.6), 0.6, glass)
    scatter(12,(-6,6),(-5,-3.2),0.12,0.25,[glass,white,acc])
# camera
bpy.ops.object.empty_add(location=cam_tgt); tgt = bpy.context.object
bpy.ops.object.camera_add(location=cam_loc); cam = bpy.context.object
cam.data.lens = lens; cam.data.dof.use_dof = True; cam.data.dof.focus_object = tgt; cam.data.dof.aperture_fstop = 11
c = cam.constraints.new('TRACK_TO'); c.target = tgt; c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
sc.camera = cam
# lights
def area(loc, size, energy, col):
    bpy.ops.object.light_add(type='AREA', location=loc); l = bpy.context.object
    l.data.size = size; l.data.energy = energy; l.data.color = col
    d = (Vector(cam_tgt)-Vector(loc)); l.rotation_euler = d.to_track_quat('-Z','Y').to_euler()
area((-6,-7,9), 7, 1800, (1,0.98,0.95))
area((8,-5,5), 6, 500, (0.85,0.95,1))
area((0,6,8), 8, 600, (1,1,1))
# render
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 96
sc.cycles.use_denoising = True
try: sc.cycles.denoiser = 'OPENIMAGEDENOISE'
except Exception: pass
sc.cycles.max_bounces = 10; sc.cycles.transmission_bounces = 10; sc.cycles.glossy_bounces = 6
sc.render.resolution_x = 1920; sc.render.resolution_y = 1080; sc.render.resolution_percentage = 100
sc.view_settings.view_transform = 'Standard'
sc.render.image_settings.file_format = 'PNG'; sc.render.filepath = OUT
bpy.ops.render.render(write_still=True)
print('RENDERED', OUT)
