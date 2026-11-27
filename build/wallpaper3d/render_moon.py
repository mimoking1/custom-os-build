import bpy, math, sys
from mathutils import Vector
a=sys.argv[sys.argv.index('--')+1:]
name,OUT,N,SAMP=a[0],a[1],int(a[2]),int(a[3])
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene
def lin(h):
    h=h.lstrip('#'); return tuple((int(h[i:i+2],16)/255)**2.2 for i in (0,2,4))+(1,)
acc=lin('#08e8de' if name=='aqua' else '#4fb2f7')
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0,segments=256,ring_count=128,location=(0,0,0))
o=bpy.context.object
for p in o.data.polygons: p.use_smooth=True
m=bpy.data.materials.new('moon'); m.use_nodes=True; nt=m.node_tree; N_=nt.nodes; L=nt.links
b=N_['Principled BSDF']
tc=N_.new('ShaderNodeTexCoord')
v=N_.new('ShaderNodeTexVoronoi'); v.feature='F1'; v.inputs['Scale'].default_value=7
n1=N_.new('ShaderNodeTexNoise'); n1.inputs['Scale'].default_value=22; n1.inputs['Detail'].default_value=10; n1.inputs['Roughness'].default_value=0.6
n2=N_.new('ShaderNodeTexNoise'); n2.inputs['Scale'].default_value=2.2; n2.inputs['Detail'].default_value=6
L.new(tc.outputs['Object'],v.inputs['Vector']); L.new(tc.outputs['Object'],n1.inputs['Vector']); L.new(tc.outputs['Object'],n2.inputs['Vector'])
cr=N_.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].position=0.0; cr.color_ramp.elements[1].position=0.32
cr.color_ramp.elements[0].color=(0,0,0,1); cr.color_ramp.elements[1].color=(1,1,1,1)
L.new(v.outputs['Distance'],cr.inputs['Fac'])
mix=N_.new('ShaderNodeMath'); mix.operation='MULTIPLY_ADD'; mix.inputs[1].default_value=0.5
L.new(cr.outputs['Color'],mix.inputs[0]); L.new(n1.outputs['Fac'],mix.inputs[2])
bump=N_.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=1.6; bump.inputs['Distance'].default_value=0.05
L.new(mix.outputs['Value'],bump.inputs['Height']); L.new(bump.outputs['Normal'],b.inputs['Normal'])
# albedo: grey maria from low freq noise
al=N_.new('ShaderNodeValToRGB'); al.color_ramp.elements[0].color=(0.30,0.30,0.31,1); al.color_ramp.elements[1].color=(0.86,0.85,0.82,1)
al.color_ramp.elements[0].position=0.40; al.color_ramp.elements[1].position=0.62
L.new(n2.outputs['Fac'],al.inputs['Fac']); L.new(al.outputs['Color'],b.inputs['Base Color'])
b.inputs['Roughness'].default_value=0.92
o.data.materials.append(m)
tgt=(0,0,0)
bpy.ops.object.camera_add(location=(0,-9,0)); c=bpy.context.object; c.data.lens=60
bpy.ops.object.empty_add(location=tgt); t=bpy.context.object
k=c.constraints.new('TRACK_TO'); k.target=t; k.track_axis='TRACK_NEGATIVE_Z'; k.up_axis='UP_Y'; sc.camera=c
o.rotation_euler=(math.radians(10),0,math.radians(25))
# sun: thin crescent lit from upper-left behind
d=Vector((-0.80,0.62,0.22)).normalized()
bpy.ops.object.light_add(type='SUN'); s=bpy.context.object; s.data.energy=7.0; s.data.angle=math.radians(0.6)
s.rotation_euler=(-d).to_track_quat('-Z','Y').to_euler()
# faint accent earthshine on the dark side
bpy.ops.object.light_add(type='AREA',location=(4,-6,-2)); f=bpy.context.object; f.data.size=6; f.data.energy=45; f.data.color=acc[:3]
f.rotation_euler=(Vector(tgt)-f.location).to_track_quat('-Z','Y').to_euler()
w=bpy.data.worlds.new('w'); sc.world=w; w.use_nodes=True
w.node_tree.nodes['Background'].inputs[0].default_value=acc; w.node_tree.nodes['Background'].inputs[1].default_value=0.05
sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=SAMP; sc.cycles.use_denoising=True
sc.render.film_transparent=True
sc.render.resolution_x=N; sc.render.resolution_y=N
sc.view_settings.view_transform='Standard'
sc.render.image_settings.file_format='PNG'; sc.render.image_settings.color_mode='RGBA'; sc.render.filepath=OUT
bpy.ops.render.render(write_still=True); print('RENDERED',OUT)
