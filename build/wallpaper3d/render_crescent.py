import bpy, math, sys
from mathutils import Vector
a=sys.argv[sys.argv.index('--')+1:]
name,OUT,N,SAMP=a[0],a[1],int(a[2]),int(a[3])
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene
def lin(h):
    h=h.lstrip('#'); return tuple((int(h[i:i+2],16)/255)**2.2 for i in (0,2,4))+(1,)
col='#08e8de' if name=='aqua' else '#4fb2f7'
def sock(b,*n):
    for k in n:
        if k in b.inputs: return b.inputs[k]
m=bpy.data.materials.new('c'); m.use_nodes=True
b=m.node_tree.nodes['Principled BSDF']
sock(b,'Base Color').default_value=lin(col)
sock(b,'Roughness').default_value=0.12
sock(b,'Metallic').default_value=0.0
s=sock(b,'Coat Weight','Clearcoat'); s.default_value=1.0
s=sock(b,'Coat Roughness','Clearcoat Roughness'); s.default_value=0.03
bpy.ops.mesh.primitive_cylinder_add(radius=1.0,depth=0.42,location=(0,0,0),rotation=(math.pi/2,0,0),vertices=192)
big=bpy.context.object
bpy.ops.mesh.primitive_cylinder_add(radius=0.82,depth=0.8,location=(0.42,0,0),rotation=(math.pi/2,0,0),vertices=192)
cut=bpy.context.object
bm=big.modifiers.new('bool','BOOLEAN'); bm.operation='DIFFERENCE'; bm.object=cut; bm.solver='EXACT'
bpy.context.view_layer.objects.active=big
bpy.ops.object.modifier_apply(modifier='bool')
bpy.data.objects.remove(cut)
big.data.materials.append(m)
bv=big.modifiers.new('b','BEVEL'); bv.width=0.09; bv.segments=8; bv.limit_method='ANGLE'; bv.angle_limit=math.radians(25)
for p in big.data.polygons: p.use_smooth=True
bpy.ops.object.modifier_apply(modifier='b')
for p in big.data.polygons: p.use_smooth=True
big.rotation_euler=(0,math.radians(-14),math.radians(-18))
tgt=(0.0,0,0)
bpy.ops.object.camera_add(location=(0.35,-8,0.6)); c=bpy.context.object
c.data.lens=50
bpy.ops.object.empty_add(location=tgt); t=bpy.context.object
k=c.constraints.new('TRACK_TO'); k.target=t; k.track_axis='TRACK_NEGATIVE_Z'; k.up_axis='UP_Y'; sc.camera=c
w=bpy.data.worlds.new('w'); sc.world=w; w.use_nodes=True
bg=w.node_tree.nodes['Background']; bg.inputs[0].default_value=(0.9,0.95,1,1); bg.inputs[1].default_value=0.9
def area(loc,size,e,cl=(1,1,1)):
    bpy.ops.object.light_add(type='AREA',location=loc); l=bpy.context.object
    l.data.size=size; l.data.energy=e; l.data.color=cl
    l.rotation_euler=(Vector(tgt)-Vector(loc)).to_track_quat('-Z','Y').to_euler()
area((-5,-6,6),4,900); area((5,-5,2),3,400,(0.9,0.97,1)); area((0,-4,-5),5,200)
sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=SAMP; sc.cycles.use_denoising=True
sc.cycles.max_bounces=10
sc.render.film_transparent=True
sc.render.resolution_x=N; sc.render.resolution_y=N
sc.view_settings.view_transform='Standard'
sc.render.image_settings.file_format='PNG'; sc.render.image_settings.color_mode='RGBA'; sc.render.filepath=OUT
bpy.ops.render.render(write_still=True); print('RENDERED',OUT)
