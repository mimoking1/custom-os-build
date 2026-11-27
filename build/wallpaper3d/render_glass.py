import bpy, bmesh, math, sys
from mathutils import Vector
a = sys.argv[sys.argv.index('--')+1:]
name, OUT, W, H, SAMP = a[0], a[1], int(a[2]), int(a[3]), int(a[4])
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
def lin(h, k=1.0):
    h = h.lstrip('#'); r,g,b = [int(h[i:i+2],16)/255 for i in (0,2,4)]
    return ((r**2.2)*k,(g**2.2)*k,(b**2.2)*k,1)
AQUA = name.startswith('aqua')
ACC  = '#08e8de' if AQUA else '#4fb2f7'
DEEP = '#0a9d96' if AQUA else '#2a74c4'     # podium (saturated, glossy)
TINT = '#a8fff9' if AQUA else '#b5dcff'     # frosted glass body
EDGE = '#08e8de' if AQUA else '#4fb2f7'
def sock(b, *n):
    for k in n:
        if k in b.inputs: return b.inputs[k]
def mat(col, rough, trans=0.0, metal=0.0, spec=0.6):
    m = bpy.data.materials.new('m'); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    sock(b,'Base Color').default_value = col
    sock(b,'Roughness').default_value = rough
    sock(b,'Metallic').default_value = metal
    sock(b,'IOR').default_value = 1.5
    t = sock(b,'Transmission Weight','Transmission')
    if t: t.default_value = trans
    return m
glass  = mat(lin(TINT), 0.16, 0.8)
glassE = mat(lin(EDGE), 0.10, 0.7)
podium = mat(lin(DEEP), 0.12, 0.0, 0.0)
white  = mat((0.93,0.95,0.96,1), 0.2)
def fin(o, m, bev=0.035, seg=5):
    o.data.materials.append(m)
    bv = o.modifiers.new('b','BEVEL'); bv.width = bev; bv.segments = seg; bv.limit_method='ANGLE'
    for p in o.data.polygons: p.use_smooth = True
    return o
def disc(x,z,r,t,m,bev=0.035,y=0):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=t, location=(x,y,z), rotation=(math.pi/2,0,0), vertices=128)
    return fin(bpy.context.object, m, bev)
def slab(x,z,w,h,t,m,bev=0.05,y=0):
    bpy.ops.mesh.primitive_cube_add(location=(x,y,z)); o=bpy.context.object
    o.scale=(w/2,t/2,h/2); bpy.ops.object.transform_apply(scale=True)
    return fin(o, m, bev)
def ring(x,z,R,r,m,y=0):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, major_segments=128, minor_segments=40, location=(x,y,z), rotation=(math.pi/2,0,0))
    o=bpy.context.object; o.data.materials.append(m)
    for p in o.data.polygons: p.use_smooth=True
    return o
def poly(pts,t,m,bev=0.03,y=0):
    bm=bmesh.new(); vs=[bm.verts.new((px,0,pz)) for px,pz in pts]; bm.faces.new(vs)
    me=bpy.data.meshes.new('p'); bm.to_mesh(me); bm.free()
    o=bpy.data.objects.new('p',me); bpy.context.collection.objects.link(o); o.location=(0,y,0)
    s=o.modifiers.new('s','SOLIDIFY'); s.thickness=t; s.offset=0
    return fin(o,m,bev,4)
def star(x,z,R,r,t,m,n=5):
    pts=[]
    for i in range(2*n):
        a=math.pi/2+i*math.pi/n; rr=R if i%2==0 else r
        pts.append((x+rr*math.cos(a), z+rr*math.sin(a)))
    return poly(pts,t,m,0.04)
def podiums(R=13.0, top=0.0):
    bpy.ops.mesh.primitive_cylinder_add(radius=R, depth=3, location=(0,2.5,top-1.5), vertices=192)
    o=bpy.context.object; o.data.materials.append(podium)
    for p in o.data.polygons: p.use_smooth=True
    return o
def stage(r=2.7):
    disc(0,0.07,r,0.14,glass,0.05)   # glass plinth on the podium
# ---- scenes: objects stand on z=0.14.. in the XZ plane
Z0=0.14
cam=(0,-12.5,3.2); tgt=(0,0,2.1); lens=34
if name=='aqua-crescent':
    podiums(); stage(3.0)
    # crescent: big disc minus offset disc (boolean)
    big=disc(0,Z0+2.2,1.9,0.55,glass,0.06)
    bpy.ops.mesh.primitive_cylinder_add(radius=1.6,depth=1.2,location=(0.75,0,Z0+2.45),rotation=(math.pi/2,0,0),vertices=128)
    cut=bpy.context.object
    bm=big.modifiers.new('bool','BOOLEAN'); bm.operation='DIFFERENCE'; bm.object=cut
    big.modifiers.move(len(big.modifiers)-1,0) if False else None
    bpy.context.view_layer.objects.active=big
    for md in list(big.modifiers):
        if md.type=='BOOLEAN': bpy.ops.object.modifier_apply(modifier=md.name)
    bpy.data.objects.remove(cut)
    star(1.35,Z0+3.35,0.55,0.24,0.35,glassE)
    star(-2.35,Z0+1.1,0.32,0.14,0.25,glass)
    disc(2.3,Z0+0.45,0.45,0.35,glassE,0.05)
    slab(-2.3,Z0+0.38,0.8,0.76,0.5,glass,0.08)
elif name=='aqua-cloud':
    podiums(); stage(3.0)
    # cloud from discs + base slab, with an up arrow
    disc(-0.9,Z0+1.9,0.95,0.55,glass,0.06); disc(0.3,Z0+2.5,1.35,0.55,glass,0.06); disc(1.55,Z0+1.95,0.95,0.55,glass,0.06)
    slab(0.3,Z0+1.55,3.2,1.0,0.55,glass,0.08)
    poly([(0.3,Z0+3.0),(0.95,Z0+2.15),(0.55,Z0+2.15),(0.55,Z0+1.1),(0.05,Z0+1.1),(0.05,Z0+2.15),(-0.35,Z0+2.15)],0.4,glassE,0.05,y=-0.55)
    disc(-2.4,Z0+0.45,0.45,0.4,glass,0.05); disc(2.5,Z0+0.7,0.7,0.4,glassE,0.05)
elif name=='sky-padlock':
    podiums(); stage(3.0)
    slab(0,Z0+1.1,2.3,1.9,0.7,glass,0.18)                   # body
    # shackle: half ring + two legs
    ring(0,Z0+2.05,0.8,0.2,glassE)
    slab(-0.8,Z0+1.9,0.4,0.55,0.4,glassE,0.08); slab(0.8,Z0+1.9,0.4,0.55,0.4,glassE,0.08)
    disc(0,Z0+1.25,0.28,0.2,white,0.05,y=-0.4); slab(0,Z0+0.85,0.2,0.5,0.2,white,0.04,y=-0.4)
    disc(-2.6,Z0+0.5,0.5,0.4,glass,0.05); star(2.4,Z0+0.9,0.55,0.24,0.3,glassE)
else:  # sky-search
    podiums(); stage(3.0)
    ring(-0.5,Z0+2.2,1.15,0.22,glassE)
    disc(-0.5,Z0+2.2,1.15,0.2,glass,0.04)
    poly([(0.35,Z0+1.35),(0.68,Z0+1.0),(1.9,Z0+0.1+0.0),(1.7,Z0-0.0),(0.35,Z0+1.0)],0.0,glassE,0.0) if False else None
    bpy.ops.mesh.primitive_cylinder_add(radius=0.2,depth=1.9,location=(1.0,0,Z0+0.95),rotation=(math.pi/2,0.0,math.radians(0)),vertices=64)
    h=bpy.context.object; h.rotation_euler=(math.pi/2,math.radians(-45)*0,0)
    h.rotation_euler=(math.pi/2,0,0); h.rotation_mode='XYZ'
    h.rotation_euler=(0,math.radians(45),0)
    h.location=(1.15,0,Z0+1.0); h.data.materials.append(glassE)
    for p in h.data.polygons: p.use_smooth=True
    slab(-2.4,Z0+0.85,1.5,1.7,0.25,white,0.07)
    star(2.6,Z0+2.9,0.5,0.22,0.3,glass)
    disc(2.5,Z0+0.45,0.45,0.4,glass,0.05)
# camera
bpy.ops.object.empty_add(location=tgt); t=bpy.context.object
bpy.ops.object.camera_add(location=cam); c=bpy.context.object
c.data.lens=lens; c.data.dof.use_dof=True; c.data.dof.focus_object=t; c.data.dof.aperture_fstop=16
k=c.constraints.new('TRACK_TO'); k.target=t; k.track_axis='TRACK_NEGATIVE_Z'; k.up_axis='UP_Y'; sc.camera=c
# backdrop wall (pale, soft)
bpy.ops.mesh.primitive_plane_add(size=80, location=(0,9,0), rotation=(math.pi/2,0,0))
bw=bpy.context.object; bw.data.materials.append(mat((0.93,0.95,0.97,1),0.6))
w=bpy.data.worlds.new('w'); sc.world=w; w.use_nodes=True
bg=w.node_tree.nodes['Background']; bg.inputs[0].default_value=(0.9,0.94,0.97,1); bg.inputs[1].default_value=1.0
def area(loc,size,e,col=(1,1,1)):
    bpy.ops.object.light_add(type='AREA',location=loc); l=bpy.context.object
    l.data.size=size; l.data.energy=e; l.data.color=col
    l.rotation_euler=(Vector(tgt)-Vector(loc)).to_track_quat('-Z','Y').to_euler()
area((-6,-8,9),8,1500); area((7,-6,5),6,700,(0.95,0.98,1)); area((0,-3,12),9,900); area((0,4,3),6,500)
sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=SAMP; sc.cycles.use_denoising=True
sc.cycles.max_bounces=12; sc.cycles.transmission_bounces=12; sc.cycles.transparent_max_bounces=12
sc.render.resolution_x=W; sc.render.resolution_y=H; sc.render.resolution_percentage=100
sc.view_settings.view_transform='Standard'
sc.render.image_settings.file_format='PNG'; sc.render.filepath=OUT
bpy.ops.render.render(write_still=True); print('RENDERED',OUT)
