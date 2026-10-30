import bpy, math, wave, struct
from mathutils import Vector
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
OUT.mkdir(exist_ok=True)
WAV = OUT / "pilot_voice.wav"

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.render.engine='BLENDER_EEVEE_NEXT'
scene.eevee.taa_render_samples=24
scene.render.resolution_x=1080
scene.render.resolution_y=1920
scene.render.resolution_percentage=65
scene.render.fps=30
scene.frame_start=1
scene.frame_end=150
scene.render.image_settings.file_format='PNG'
scene.render.film_transparent=False
scene.world.color=(0.018,0.025,0.05)

def mat(name,color,metal=0,rough=.45, emission=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    bs=m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(*color,1)
    bs.inputs["Metallic"].default_value=metal; bs.inputs["Roughness"].default_value=rough
    if emission:
        bs.inputs["Emission Color"].default_value=(*color,1); bs.inputs["Emission Strength"].default_value=emission
    return m
navy=mat("Midnight navy",(0.012,.025,.06),rough=.8)
blue=mat("Electric blue",(.025,.22,.48),metal=.35)
cyan=mat("Neon cyan",(.02,.8,.95),metal=.25,emission=2)
white=mat("Porcelain white",(.92,.96,1),rough=.25)
black=mat("Graphite",(.018,.025,.04),metal=.25)
gold=mat("Payday gold",(1,.55,.06),metal=.55)
green=mat("Savings green",(.08,.85,.4),metal=.2,emission=.35)

def cube(name,loc,scale,material, bevel=.08):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o=bpy.context.object; o.name=name
    o.dimensions=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(material)
    if bevel:
        mod=o.modifiers.new("Soft premium edges","BEVEL"); mod.width=bevel; mod.segments=4
        o.modifiers.new("Weighted normals","WEIGHTED_NORMAL")
    return o
def uv(name,loc,scale,material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=20,radius=1,location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale; o.data.materials.append(material)
    bpy.ops.object.shade_smooth(); return o
def cyl_between(name,a,b,r,material):
    mid=(Vector(a)+Vector(b))/2; vec=Vector(b)-Vector(a)
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=r, depth=vec.length, location=mid)
    o=bpy.context.object; o.name=name; o.rotation_mode='QUATERNION'; o.rotation_quaternion=vec.to_track_quat('Z','Y')
    o.data.materials.append(material); bpy.ops.object.shade_smooth()
    bevel=o.modifiers.new("Rounded joints","BEVEL"); bevel.width=r*.65; bevel.segments=3
    o.modifiers.new("Normals","WEIGHTED_NORMAL")
    return o

# Cinematic studio-office set
cube("Floor",(0,0,-.16),(12,12,.3),navy,.12)
cube("Back wall",(0,3.2,3.4),(12,.25,7),black,.1)
for x in (-4.4,4.4):
    cube("Neon architectural strip",(x,3.02,3.4),(.045,.04,6),cyan,.02)
# City skyline through large window
cube("Window",(0,3.02,3.8),(7,.06,4.4),blue,.03)
for i in range(9):
    h=1.2+(i%4)*.55
    cube("City tower",(-3.3+i*.82,2.95,1.6+h/2),(.48,.08,h),black,.02)
# Desk and monitor
cube("Desk top",(0,.2,1.45),(5.5,1.5,.18),black,.1)
for x in (-2.2,2.2): cube("Desk leg",(x,.25,.72),(.13,.13,1.4),blue,.04)
cube("Monitor body",(0,.92,2.75),(2.65,.16,1.55),black,.12)
cube("Monitor screen",(0,.815,2.77),(2.43,.025,1.32),blue,.04)
# Screen glow bars
cube("Bank UI panel",(0,.79,2.78),(1.95,.02,.72),navy,.04)
# Text object helper
def text_obj(body,loc,size,material):
    cu=bpy.data.curves.new("Text","FONT"); cu.body=body; cu.size=size; cu.extrude=.002
    ob=bpy.data.objects.new(body,cu); scene.collection.objects.link(ob); ob.location=loc
    ob.rotation_euler=(math.radians(90),0,0); ob.data.materials.append(material); return ob
text_obj("PAYDAY  +$2,400",(-.88,.755,2.9),.22,green)
text_obj("AVAILABLE BALANCE",(-.88,.75,2.57),.11,white)

# Character: consistent smooth porcelain-white 3D stick figure
cx,cy=-.15,-.65
head=uv("Stickman head",(cx,cy,3.22),(.48,.43,.5),white)
torso=cyl_between("Stickman torso",(cx,cy,2.75),(cx,cy,1.85),.16,white)
# face facing camera (camera at y=-9)
eye1=uv("Left eye",(cx-.15,cy-.405,3.3),(.055,.035,.075),black)
eye2=uv("Right eye",(cx+.15,cy-.405,3.3),(.055,.035,.075),black)
mouth=uv("Talking mouth",(cx,cy-.44,3.08),(.09,.025,.035),black)
# arms and legs separate, animated segments
arms=[]; legs=[]
for side in (-1,1):
    shoulder=(cx+side*.12,cy,2.65); elbow=(cx+side*.42,cy,2.25); hand=(cx+side*.62,cy,1.95)
    a=cyl_between("Upper arm",shoulder,elbow,.085,white)
    b=cyl_between("Forearm",elbow,hand,.075,white); arms.append((a,b,side))
    hip=(cx+side*.08,cy,1.86); knee=(cx+side*.18,cy,.98); foot=(cx+side*.34,cy-.12,.3)
    l1=cyl_between("Thigh",hip,knee,.095,white); l2=cyl_between("Shin",knee,foot,.08,white); legs.append((l1,l2,side))
# floating coin and bills
coin=uv("Golden payday coin",(1.65,-.7,2.05),(.42,.12,.42),gold)
for i in range(3):
    bill=cube("Floating dollar bill",(1.7+i*.42,-.3,1.8+i*.48),(.58,.035,.32),green,.04)
    bill.rotation_euler[1]=-.25+i*.2

# Lighting
def area(name,loc,power,color,size,target):
    data=bpy.data.lights.new(name,'AREA'); data.energy=power; data.color=color; data.shape='DISK'; data.size=size
    ob=bpy.data.objects.new(name,data); scene.collection.objects.link(ob); ob.location=loc; ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
area("Key softbox",(-4,-5,7),900,(.55,.78,1),5,(0,0,2))
area("Warm rim",(4,1,5),1100,(1,.48,.16),3,(0,0,2))
area("Front fill",(0,-5,3),450,(.2,.8,1),4,(0,0,2))
# camera portrait
camdata=bpy.data.cameras.new("Portrait camera"); cam=bpy.data.objects.new("Portrait camera",camdata); scene.collection.objects.link(cam)
cam.location=(4.5,-10,4.5); target=Vector((0,0,2.25)); cam.rotation_euler=(target-Vector(cam.location)).to_track_quat('-Z','Y').to_euler()
camdata.lens=48; scene.camera=cam
# camera push-in and tiny whip-style reframing
cam.location.x=4.5; cam.keyframe_insert(data_path="location",frame=1)
cam.location.x=2.8; cam.keyframe_insert(data_path="location",frame=55)
cam.location.x=1.4; cam.keyframe_insert(data_path="location",frame=100)
cam.location.x=0.7; cam.keyframe_insert(data_path="location",frame=150)
# character body bounce, arm gestures
for frame,z in [(1,0),(18,.12),(35,0),(60,.08),(80,0),(110,.15),(130,0),(150,.05)]:
    head.location.z=3.22+z; head.keyframe_insert(data_path="location",frame=frame)
    torso.location.z=2.3+z; torso.keyframe_insert(data_path="location",frame=frame)
for a,b,side in arms:
    for frame,ang in [(1,0),(20,side*.55),(42,-side*.2),(65,side*.8),(90,-side*.35),(120,side*.5),(150,0)]:
        a.rotation_euler[1]=ang; a.keyframe_insert(data_path="rotation_euler",frame=frame)
        b.rotation_euler[1]=-ang*.7; b.keyframe_insert(data_path="rotation_euler",frame=frame)
# Mouth pulse driven from actual voice waveform envelope (frame-by-frame)
with wave.open(str(WAV),"rb") as wf:
    sr=wf.getframerate(); n=wf.getnframes(); raw=wf.readframes(n)
    sw=wf.getsampwidth()
    if sw==2:
        vals=struct.unpack("<"+"h"*(len(raw)//2),raw); samples=[v/32768 for v in vals]
    else: samples=[0.0]*n
for frame in range(1,151):
    t=(frame-1)/30
    start=int(t*sr); end=min(n,start+int(.035*sr))
    chunk=samples[start:end] or [0]
    rms=(sum(v*v for v in chunk)/len(chunk))**.5
    mouth.scale=(.09,.025,.025+min(.18,rms*.7))
    mouth.keyframe_insert(data_path="scale",frame=frame)
# Timeline accents, floating coin spin
for frame,rot in [(1,0),(150,math.tau*1.3)]:
    coin.rotation_euler[1]=rot; coin.keyframe_insert(data_path="rotation_euler",frame=frame)
# Color management
scene.view_settings.view_transform='AgX'
scene.view_settings.look='AgX - Medium High Contrast'
scene.render.filepath=str(OUT/"pilot_frame_")
scene.camera.data.dof.use_dof=True
scene.camera.data.dof.focus_object=head
scene.camera.data.dof.aperture_fstop=5.6
scene.render.image_settings.color_mode='RGB'
scene.render.resolution_percentage=65
scene.render.filepath=str(OUT/"pilot_frame_")
# Render frames
bpy.ops.render.render(animation=True)
