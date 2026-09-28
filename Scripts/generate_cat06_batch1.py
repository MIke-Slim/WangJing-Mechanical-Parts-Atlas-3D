"""
Category 06 Batch 1: 箱壳类零件 (Housings & Casings - Part 1)
Generates the first 15 models for Category 06:
  LJT06.01_缸体,   LJT06.02_箱体,   LJT06.03_阀体,   LJT06.04_缸体,
  LJT06.05_传动箱, LJT06.06_阀体,   LJT06.07_蜗轮壳, LJT06.08_泵缸,
  LJT06.09_箱体,   LJT06.10_泵体,   LJT06.11_尾架体, LJT06.12_泵体,
  LJT06.13_阀体,   LJT06.14_蜗轮箱, LJT06.15_泵体
Procedural CAD modeling in Blender Python (bpy / bmesh)
Author: Antigravity Assistant
"""

import bpy
import bmesh
import math
import os
import sys
from mathutils import Vector, Matrix

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

import blender_cad_generator as bcg

base_dir = os.path.dirname(script_dir)
cat_dir = os.path.join(base_dir, "06_箱壳类_Housings")
renders_dir = os.path.join(base_dir, "Renders")
os.makedirs(cat_dir, exist_ok=True)
os.makedirs(renders_dir, exist_ok=True)

# ==============================================================================
# COMMON CAD MODELING HELPERS
# ==============================================================================

def apply_boolean_difference(target_obj, cutter_obj):
    """Applies a boolean difference modifier and cleans up cutter object."""
    mod = target_obj.modifiers.new(name="BoolDiff", type='BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = cutter_obj
    mod.solver = 'EXACT'
    bpy.context.view_layer.objects.active = target_obj
    try:
        bpy.ops.object.modifier_apply(modifier=mod.name)
    except Exception:
        mod.solver = 'FAST'
        try:
            bpy.ops.object.modifier_apply(modifier=mod.name)
        except Exception as e:
            print(f"Warning: Boolean difference failed: {e}")
    bpy.data.objects.remove(cutter_obj, do_unlink=True)

def apply_boolean_union(target_obj, tool_obj):
    """Applies a boolean union modifier and cleans up tool object."""
    mod = target_obj.modifiers.new(name="BoolUnion", type='BOOLEAN')
    mod.operation = 'UNION'
    mod.object = tool_obj
    mod.solver = 'EXACT'
    bpy.context.view_layer.objects.active = target_obj
    try:
        bpy.ops.object.modifier_apply(modifier=mod.name)
    except Exception:
        mod.solver = 'FAST'
        try:
            bpy.ops.object.modifier_apply(modifier=mod.name)
        except Exception as e:
            print(f"Warning: Boolean union failed: {e}")
    bpy.data.objects.remove(tool_obj, do_unlink=True)

def create_cylinder(radius, depth, location=(0, 0, 0), rotation=(0, 0, 0), vertices=64, name="Cylinder"):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=radius,
        depth=depth,
        location=location,
        rotation=rotation
    )
    obj = bpy.context.active_object
    obj.name = name
    return obj

def create_box(size, location=(0, 0, 0), rotation=(0, 0, 0), name="Box"):
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=location,
        rotation=rotation
    )
    obj = bpy.context.active_object
    obj.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.name = name
    return obj

def drill_hole(target_obj, radius, depth, location, rotation=(0, 0, 0), vertices=32):
    cutter = create_cylinder(radius=radius, depth=depth, location=location, rotation=rotation, vertices=vertices, name="HoleCutter")
    apply_boolean_difference(target_obj, cutter)

def drill_counterbore_hole(target_obj, r_hole, r_cbore, depth_hole, depth_cbore, location, normal_axis='Z'):
    """Drills a hole with a counterbore along normal axis."""
    rot = (0, 0, 0)
    if normal_axis == 'X':
        rot = (0, math.pi / 2, 0)
    elif normal_axis == 'Y':
        rot = (math.pi / 2, 0, 0)
    
    # Through hole
    cutter = create_cylinder(radius=r_hole, depth=depth_hole, location=location, rotation=rot, name="Hole")
    apply_boolean_difference(target_obj, cutter)
    
    # Counterbore
    cb_loc = list(location)
    if normal_axis == 'Z':
        cb_loc[2] += depth_hole / 2.0 - depth_cbore / 2.0
    elif normal_axis == 'Y':
        cb_loc[1] += depth_hole / 2.0 - depth_cbore / 2.0
    elif normal_axis == 'X':
        cb_loc[0] += depth_hole / 2.0 - depth_cbore / 2.0
        
    cb_cutter = create_cylinder(radius=r_cbore, depth=depth_cbore, location=tuple(cb_loc), rotation=rot, name="CBore")
    apply_boolean_difference(target_obj, cb_cutter)

# ==============================================================================
# 1. LJT06.01_缸体 (Cylinder Body - Hydraulic / Pneumatic)
# ==============================================================================
def generate_ljt06_01():
    # Base mounting foot: 92 x 60 x 12 mm
    base = create_box(size=(92, 60, 12), location=(0, 0, 6), name="LJT06_01_Base")
    
    # 4x M8/Phi9 counterbore holes: centers (+-37, +-21)
    for sx in [-37, 37]:
        for sy in [-21, 21]:
            cutter_h = create_cylinder(radius=4.5, depth=20, location=(sx, sy, 6))
            apply_boolean_difference(base, cutter_h)
            cutter_cb = create_cylinder(radius=7.5, depth=6, location=(sx, sy, 10))
            apply_boolean_difference(base, cutter_cb)
            
    # Main cylinder lower stepped portion: OD 70, height 33 (Z=12 to 45)
    cyl_lower = create_cylinder(radius=35, depth=33, location=(0, 0, 28.5), name="CylLower")
    apply_boolean_union(base, cyl_lower)
    
    # Main cylinder upper stepped portion: OD 55, height 50 (Z=45 to 95)
    cyl_upper = create_cylinder(radius=27.5, depth=50, location=(0, 0, 70), name="CylUpper")
    apply_boolean_union(base, cyl_upper)
    
    # Blind central bore Phi 35 from Z=95 down to Z=15 (depth 80)
    bore = create_cylinder(radius=17.5, depth=82, location=(0, 0, 55), name="CentralBore")
    apply_boolean_difference(base, bore)
    
    # Top chamfer at Z=95
    # Side fluid boss ports: 2x M12x1.25 on +Y side at Z=30 and Z=80
    for z_port in [30, 75]:
        boss = create_cylinder(radius=11, depth=15, location=(0, 28, z_port), rotation=(math.pi/2, 0, 0), name="PortBoss")
        apply_boolean_union(base, boss)
        port_hole = create_cylinder(radius=5.25, depth=35, location=(0, 20, z_port), rotation=(math.pi/2, 0, 0), name="PortHole")
        apply_boolean_difference(base, port_hole)
        
    return base, "cast_iron"

# ==============================================================================
# 2. LJT06.02_箱体 (Gearbox Housing)
# ==============================================================================
def generate_ljt06_02():
    # Base plate: 170 x 140 x 18 mm (X: -85..85, Y: -70..70, Z: 0..18)
    body = create_box(size=(170, 140, 18), location=(0, 0, 9), name="LJT06_02_Base")
    
    # Front U-cut: width 60, depth 30 from front edge Y=-70 to -40
    u_cut = create_box(size=(60, 32, 25), location=(0, -55, 9), name="UCut")
    apply_boolean_difference(body, u_cut)
    
    # 4x Phi 14 mounting holes at (+-67, +-52)
    for sx in [-67, 67]:
        for sy in [-52, 52]:
            drill_hole(body, radius=7.0, depth=25, location=(sx, sy, 9))
            
    # Front square flange: 120 x 120 x 25 mm, centered at X=0, Z=75, Y=-25
    front_sq = create_box(size=(120, 25, 120), location=(0, -25, 75), name="FrontSquare")
    apply_boolean_union(body, front_sq)
    
    # Central box cavity / housing connecting front to rear
    mid_box = create_box(size=(90, 65, 95), location=(0, 15, 65), name="MidBox")
    apply_boolean_union(body, mid_box)
    
    # Rear cylindrical neck: OD 60, length 35 along Y from Y=45 to Y=80, at Z=75
    rear_neck = create_cylinder(radius=30, depth=35, location=(0, 62.5, 75), rotation=(math.pi/2, 0, 0), name="RearNeck")
    apply_boolean_union(body, rear_neck)
    
    # Main through bearing bore along Y axis at Z=75
    # Front bearing seat Phi 90 depth 20, internal clearance Phi 75, rear seat Phi 40
    bore_front = create_cylinder(radius=45, depth=40, location=(0, -25, 75), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, bore_front)
    
    bore_mid = create_cylinder(radius=35, depth=60, location=(0, 15, 75), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, bore_mid)
    
    bore_rear = create_cylinder(radius=20, depth=50, location=(0, 65, 75), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, bore_rear)
    
    # 4x M10 tapped holes on front face (pitch 90 x 90, Z=75 +- 45, X=+-45)
    for fx in [-45, 45]:
        for fz in [30, 120]:
            f_hole = create_cylinder(radius=4.25, depth=25, location=(fx, -37.5, fz), rotation=(math.pi/2, 0, 0))
            apply_boolean_difference(body, f_hole)
            
    # Stiffener triangular ribs
    rib1 = create_box(size=(12, 50, 45), location=(-45, 20, 35), name="RibL")
    apply_boolean_union(body, rib1)
    rib2 = create_box(size=(12, 50, 45), location=(45, 20, 35), name="RibR")
    apply_boolean_union(body, rib2)
    
    return body, "cast_iron"

# ==============================================================================
# 3. LJT06.03_阀体 (Valve Body - Cast Steel/Iron)
# ==============================================================================
def generate_ljt06_03():
    # Central spherical body: R30 (Phi 60)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=32, radius=30, location=(0, 0, 0))
    body = bpy.context.active_object
    body.name = "LJT06_03_Body"
    
    # Internal hollow sphere R21 (Phi 42)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=24, radius=21, location=(0, 0, 0))
    cavity = bpy.context.active_object
    apply_boolean_difference(body, cavity)
    
    # Front square flange: 75 x 75 x 14 mm at Y = -42
    flange = create_box(size=(75, 14, 75), location=(0, -42, 0), name="FrontFlange")
    neck_f = create_cylinder(radius=24, depth=25, location=(0, -25, 0), rotation=(math.pi/2, 0, 0))
    apply_boolean_union(flange, neck_f)
    apply_boolean_union(body, flange)
    
    # Front bore Phi 32 through into chamber
    bore_f = create_cylinder(radius=16, depth=45, location=(0, -35, 0), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, bore_f)
    
    # 4x M12 holes on front flange at (+-26, +-26)
    for sx in [-26, 26]:
        for sz in [-26, 26]:
            h = create_cylinder(radius=5.2, depth=25, location=(sx, -42, sz), rotation=(math.pi/2, 0, 0))
            apply_boolean_difference(body, h)
            
    # Top neck port: OD 36, height extending to Z=55
    top_neck = create_cylinder(radius=18, depth=35, location=(0, 0, 37.5), name="TopNeck")
    apply_boolean_union(body, top_neck)
    top_bore = create_cylinder(radius=10.5, depth=45, location=(0, 0, 37.5), name="TopBore")
    apply_boolean_difference(body, top_bore)
    
    # Right threaded port: OD 40, length extending to X=55
    r_neck = create_cylinder(radius=20, depth=35, location=(37.5, 0, 0), rotation=(0, math.pi/2, 0), name="RightNeck")
    apply_boolean_union(body, r_neck)
    r_bore = create_cylinder(radius=12.5, depth=45, location=(37.5, 0, 0), rotation=(0, math.pi/2, 0), name="RightBore")
    apply_boolean_difference(body, r_bore)
    
    # Left port boss: OD 38 extending to X=-42
    l_neck = create_cylinder(radius=19, depth=25, location=(-32, 0, 0), rotation=(0, math.pi/2, 0), name="LeftNeck")
    apply_boolean_union(body, l_neck)
    l_bore = create_cylinder(radius=11, depth=35, location=(-32, 0, 0), rotation=(0, math.pi/2, 0), name="LeftBore")
    apply_boolean_difference(body, l_bore)
    
    return body, "cast_iron"

# ==============================================================================
# 4. LJT06.04_缸体 (Cylinder Body - Aluminum Alloy ZL102)
# ==============================================================================
def generate_ljt06_04():
    # Bottom circular flange: OD 106, thickness 12 mm
    body = create_cylinder(radius=53, depth=12, location=(0, 0, 6), name="LJT06_04_Base")
    
    # 4x Phi 7 holes on PCD 84
    for i in range(4):
        ang = i * math.pi / 2
        hx = 42 * math.cos(ang)
        hy = 42 * math.sin(ang)
        drill_hole(body, radius=3.5, depth=18, location=(hx, hy, 6))
        
    # Central cylinder body: OD 50, height 83 (Z=12 to 95)
    cyl = create_cylinder(radius=25, depth=83, location=(0, 0, 53.5), name="CylBody")
    apply_boolean_union(body, cyl)
    
    # Top stadium flange: 89 x 68 x 12 mm at Z=89
    flange_top = create_box(size=(89, 68, 12), location=(0, 0, 89), name="TopFlange")
    apply_boolean_union(body, flange_top)
    
    # 6x Phi 7 holes on top flange
    top_holes = [(-34, -22), (-34, 22), (34, -22), (34, 22), (0, -25), (0, 25)]
    for tx, ty in top_holes:
        drill_hole(body, radius=3.5, depth=20, location=(tx, ty, 89))
        
    # Central bore: Phi 30 through
    cbore = create_cylinder(radius=15, depth=110, location=(0, 0, 50), name="CentralBore")
    apply_boolean_difference(body, cbore)
    
    # Side manifold block: on +X side (X=20..48, Y=-18..18, Z=30..65)
    manifold = create_box(size=(28, 36, 35), location=(34, 0, 47.5), name="ManifoldBlock")
    apply_boolean_union(body, manifold)
    
    # 2x M6 tapped holes on manifold face X=48
    for mz in [38, 57]:
        m_hole = create_cylinder(radius=2.5, depth=18, location=(40, 0, mz), rotation=(0, math.pi/2, 0))
        apply_boolean_difference(body, m_hole)
        
    # Side boss on +Y side: OD 30, bore 20 at Z=48
    boss_y = create_cylinder(radius=15, depth=18, location=(0, 30, 48), rotation=(math.pi/2, 0, 0), name="BossY")
    apply_boolean_union(body, boss_y)
    boss_y_bore = create_cylinder(radius=10, depth=35, location=(0, 30, 48), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, boss_y_bore)
    
    return body, "machined_steel"

# ==============================================================================
# 5. LJT06.05_传动箱 (Transmission Box)
# ==============================================================================
def generate_ljt06_05():
    # Main cylindrical housing: OD 70, height 56 mm
    body = create_cylinder(radius=35, depth=56, location=(0, 0, 28), name="LJT06_05_Body")
    
    # Side box extension on +X side: X: 15..65, Y: -26..26, Z: 4..52
    ext = create_box(size=(42, 52, 48), location=(40, 0, 28), name="BoxExt")
    apply_boolean_union(body, ext)
    
    # Top bore: Phi 35, depth 25 (Z=31 to 56)
    top_bore = create_cylinder(radius=17.5, depth=26, location=(0, 0, 44), name="TopBore")
    apply_boolean_difference(body, top_bore)
    
    # Bottom bore: Phi 55, depth 20 (Z=0 to 20)
    bot_bore = create_cylinder(radius=27.5, depth=22, location=(0, 0, 10), name="BotBore")
    apply_boolean_difference(body, bot_bore)
    
    # Central web through-hole Phi 20 (Z=18 to 33)
    web_hole = create_cylinder(radius=10, depth=16, location=(0, 0, 25.5), name="WebHole")
    apply_boolean_difference(body, web_hole)
    
    # Inspection window on +X face: 53 x 32 mm, depth 16
    window = create_box(size=(20, 32, 28), location=(55, 0, 28), name="Window")
    apply_boolean_difference(body, window)
    
    # Internal hollow cavity for gears
    gear_cavity = create_box(size=(30, 38, 36), location=(30, 0, 28), name="GearCavity")
    apply_boolean_difference(body, gear_cavity)
    
    # 4x M4 holes around window face on +X face
    for wy in [-20, 20]:
        for wz in [18, 38]:
            wh = create_cylinder(radius=1.65, depth=14, location=(55, wy, wz), rotation=(0, math.pi/2, 0))
            apply_boolean_difference(body, wh)
            
    # Transverse shaft bores along Y axis: Phi 16 on +Y, Phi 10 on -Y at X=38, Z=28
    shaft_bore1 = create_cylinder(radius=8, depth=25, location=(38, 20, 28), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, shaft_bore1)
    shaft_bore2 = create_cylinder(radius=5, depth=25, location=(38, -20, 28), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, shaft_bore2)
    
    return body, "cast_iron"

# ==============================================================================
# 6. LJT06.06_阀体 (Valve Body - Aluminum Alloy ZL102)
# ==============================================================================
def generate_ljt06_06():
    # Base square flange: 70 x 70 x 10 mm
    body = create_box(size=(70, 70, 10), location=(0, 0, 5), name="LJT06_06_Base")
    
    # 4x Phi 10 holes at corners (+-26, +-26)
    for sx in [-26, 26]:
        for sy in [-26, 26]:
            drill_hole(body, radius=5.0, depth=15, location=(sx, sy, 5))
            
    # Central vertical tower: OD 60, height 70 (Z=10 to 80)
    tower = create_cylinder(radius=30, depth=70, location=(0, 0, 45), name="Tower")
    apply_boolean_union(body, tower)
    
    # Transverse cylinder barrel along Y axis at Z=45: length 94 mm (Y: -47..47), OD 46
    barrel = create_cylinder(radius=23, depth=94, location=(0, 0, 45), rotation=(math.pi/2, 0, 0), name="Barrel")
    apply_boolean_union(body, barrel)
    
    # Transverse bore Phi 28 through
    t_bore = create_cylinder(radius=14, depth=110, location=(0, 0, 45), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, t_bore)
    
    # Top vertical stepped bore: M36 internal thread (Phi 33 depth 25), stepped to Phi 20 down into transverse bore
    v_bore_top = create_cylinder(radius=16.5, depth=26, location=(0, 0, 70))
    apply_boolean_difference(body, v_bore_top)
    v_bore_mid = create_cylinder(radius=10, depth=35, location=(0, 0, 45))
    apply_boolean_difference(body, v_bore_mid)
    
    # Rear diamond flange at Y=-47: thickness 8 mm, height 70, width 46
    rear_flange = create_box(size=(46, 8, 70), location=(0, -47, 45), name="RearFlange")
    apply_boolean_union(body, rear_flange)
    # 2x Phi 9 holes at (0, -47, 45 +- 24)
    for fz in [21, 69]:
        rf_hole = create_cylinder(radius=4.5, depth=15, location=(0, -47, fz), rotation=(math.pi/2, 0, 0))
        apply_boolean_difference(body, rf_hole)
        
    # Front square flange at Y=47: 60 x 10 x 60 mm
    front_flange = create_box(size=(60, 10, 60), location=(0, 47, 45), name="FrontFlange")
    apply_boolean_union(body, front_flange)
    # 4x M8 holes at (+-21, 47, 45 +- 21)
    for fx in [-21, 21]:
        for fz in [24, 66]:
            ff_hole = create_cylinder(radius=3.4, depth=18, location=(fx, 47, fz), rotation=(math.pi/2, 0, 0))
            apply_boolean_difference(body, ff_hole)
            
    return body, "machined_steel"

# ==============================================================================
# 7. LJT06.07_蜗轮壳 (Worm Gear Housing)
# ==============================================================================
def generate_ljt06_07():
    # Base mounting plate: 146 x 128 x 14 mm
    body = create_box(size=(146, 128, 14), location=(0, 0, 7), name="LJT06_07_Base")
    
    # 4x Phi 11 holes at (+-60, +-50)
    for sx in [-60, 60]:
        for sy in [-50, 50]:
            drill_hole(body, radius=5.5, depth=20, location=(sx, sy, 7))
            
    # Worm shaft tunnel along X axis at Z=38, Y=0: OD 60, length 140 mm
    worm_tunnel = create_cylinder(radius=30, depth=140, location=(0, 0, 38), rotation=(0, math.pi/2, 0), name="WormTunnel")
    apply_boolean_union(body, worm_tunnel)
    
    # Worm shaft through bore Phi 40
    worm_bore = create_cylinder(radius=20, depth=150, location=(0, 0, 38), rotation=(0, math.pi/2, 0))
    apply_boolean_difference(body, worm_bore)
    
    # Left end flange: OD 75, thickness 10 at X=-70
    flange_l = create_cylinder(radius=37.5, depth=10, location=(-70, 0, 38), rotation=(0, math.pi/2, 0))
    apply_boolean_union(body, flange_l)
    # 4x M6 tapped holes
    for ang in [math.pi/4, 3*math.pi/4, 5*math.pi/4, 7*math.pi/4]:
        ly = 28 * math.cos(ang)
        lz = 38 + 28 * math.sin(ang)
        lh = create_cylinder(radius=2.5, depth=15, location=(-70, ly, lz), rotation=(0, math.pi/2, 0))
        apply_boolean_difference(body, lh)
        
    # Right end flange: OD 70, thickness 10 at X=70
    flange_r = create_cylinder(radius=35, depth=10, location=(70, 0, 38), rotation=(0, math.pi/2, 0))
    apply_boolean_union(body, flange_r)
    # 4x M5 holes
    for ang in [math.pi/4, 3*math.pi/4, 5*math.pi/4, 7*math.pi/4]:
        ry = 26 * math.cos(ang)
        rz = 38 + 26 * math.sin(ang)
        rh = create_cylinder(radius=2.1, depth=15, location=(70, ry, rz), rotation=(0, math.pi/2, 0))
        apply_boolean_difference(body, rh)
        
    # Worm wheel chamber arch along Y axis at X=0, Z=90: OD 110 (R55), width 64 mm (Y: -32..32)
    wheel_arch = create_cylinder(radius=55, depth=64, location=(0, 0, 90), rotation=(math.pi/2, 0, 0), name="WheelArch")
    apply_boolean_union(body, wheel_arch)
    
    # Worm wheel cavity bore Phi 92 through
    wheel_bore = create_cylinder(radius=46, depth=70, location=(0, 0, 90), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, wheel_bore)
    
    # Side cover flange on +Y face: OD 128, thickness 12 at Y=32
    cov_flange = create_cylinder(radius=64, depth=12, location=(0, 32, 90), rotation=(math.pi/2, 0, 0), name="CovFlange")
    apply_boolean_union(body, cov_flange)
    # 6x M6 holes on PCD 110
    for i in range(6):
        ang = i * math.pi / 3
        cx = 55 * math.cos(ang)
        cz = 90 + 55 * math.sin(ang)
        ch = create_cylinder(radius=2.5, depth=18, location=(cx, 32, cz), rotation=(math.pi/2, 0, 0))
        apply_boolean_difference(body, ch)
        
    # Gusset webs connecting worm tunnel, base, and wheel chamber
    web1 = create_box(size=(10, 80, 50), location=(-40, 0, 55), name="WebL")
    apply_boolean_union(body, web1)
    web2 = create_box(size=(10, 80, 50), location=(40, 0, 55), name="WebR")
    apply_boolean_union(body, web2)
    
    return body, "cast_iron"

# ==============================================================================
# 8. LJT06.08_泵缸 (Pump Cylinder)
# ==============================================================================
def generate_ljt06_08():
    # Base mounting feet: 195 x 60 x 15 mm
    body = create_box(size=(195, 60, 15), location=(0, 0, 7.5), name="LJT06_08_Base")
    
    # 2x Phi 17 holes at (+-77.5, 0)
    for sx in [-77.5, 77.5]:
        drill_hole(body, radius=8.5, depth=25, location=(sx, 0, 7.5))
        
    # Main horizontal pump barrel along X axis at Z=48, Y=0: length 167 mm (X: -80..87)
    barrel1 = create_cylinder(radius=38, depth=100, location=(-30, 0, 48), rotation=(0, math.pi/2, 0), name="BarrelMain")
    barrel2 = create_cylinder(radius=30, depth=67, location=(53.5, 0, 48), rotation=(0, math.pi/2, 0), name="BarrelRight")
    apply_boolean_union(body, barrel1)
    apply_boolean_union(body, barrel2)
    
    # External thread boss on right end at X=87: M68x3 (OD 68, length 20)
    thread_boss = create_cylinder(radius=34, depth=20, location=(87, 0, 48), rotation=(0, math.pi/2, 0))
    apply_boolean_union(body, thread_boss)
    
    # Stepped bore through barrel: Phi 64 (right), Phi 52 (mid), Phi 43 (left)
    bore_r = create_cylinder(radius=32, depth=50, location=(75, 0, 48), rotation=(0, math.pi/2, 0))
    apply_boolean_difference(body, bore_r)
    bore_m = create_cylinder(radius=26, depth=80, location=(15, 0, 48), rotation=(0, math.pi/2, 0))
    apply_boolean_difference(body, bore_m)
    bore_l = create_cylinder(radius=21.5, depth=70, location=(-55, 0, 48), rotation=(0, math.pi/2, 0))
    apply_boolean_difference(body, bore_l)
    
    # Top inlet port at X=-30, Y=0, Z=86: 2-bolt diamond flange, thread M27x2 (bore Phi 25)
    inlet_boss = create_cylinder(radius=22, depth=20, location=(-30, 0, 86), name="InletBoss")
    apply_boolean_union(body, inlet_boss)
    inlet_flange = create_box(size=(65, 36, 12), location=(-30, 0, 92), name="InletFlange")
    apply_boolean_union(body, inlet_flange)
    inlet_bore = create_cylinder(radius=12.5, depth=55, location=(-30, 0, 75))
    apply_boolean_difference(body, inlet_bore)
    # 2x bolt holes on diamond flange
    for sx in [-50, -10]:
        ih = create_cylinder(radius=4.5, depth=20, location=(sx, 0, 92))
        apply_boolean_difference(body, ih)
        
    # Side vertical valve chamber offset at X=35, Y=45: OD 56, height 120 (Z: -12..108)
    valve_cyl = create_cylinder(radius=28, depth=120, location=(35, 45, 48), name="ValveChamber")
    apply_boolean_union(body, valve_cyl)
    
    # Top and bottom M39x2 threaded ports (bore Phi 37 depth 25)
    v_top_bore = create_cylinder(radius=18.5, depth=30, location=(35, 45, 95))
    apply_boolean_difference(body, v_top_bore)
    v_bot_bore = create_cylinder(radius=18.5, depth=30, location=(35, 45, 0))
    apply_boolean_difference(body, v_bot_bore)
    v_mid_bore = create_cylinder(radius=14, depth=70, location=(35, 45, 48))
    apply_boolean_difference(body, v_mid_bore)
    
    # Cross gallery bore Phi 22 connecting barrel to valve chamber
    cross_bore = create_cylinder(radius=11, depth=50, location=(35, 22.5, 48), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, cross_bore)
    
    return body, "cast_iron"

# ==============================================================================
# 9. LJT06.09_箱体 (Casing / Housing - Aluminum Alloy ZL102)
# ==============================================================================
def generate_ljt06_09():
    # Main rectangular box: 154 x 82 x 80 mm (X: -77..77, Y: -41..41, Z: 0..80)
    body = create_box(size=(154, 82, 80), location=(0, 0, 40), name="LJT06_09_Body")
    
    # Internal hollow cavity: wall thickness ~8 mm
    cavity = create_box(size=(138, 66, 68), location=(0, 0, 40), name="Cavity")
    apply_boolean_difference(body, cavity)
    
    # Top square port boss: 40 x 40 x 12 mm at Z=86
    top_boss = create_box(size=(40, 40, 12), location=(0, 0, 86), name="TopBoss")
    apply_boolean_union(body, top_boss)
    top_bore = create_cylinder(radius=7, depth=25, location=(0, 0, 80))
    apply_boolean_difference(body, top_bore)
    for bx in [-14, 14]:
        for by in [-14, 14]:
            bh = create_cylinder(radius=2.1, depth=15, location=(bx, by, 86))
            apply_boolean_difference(body, bh)
            
    # Front cantilever snout on +Y face: 40 x 24 x 40 mm extending from Y=41 to 65 at Z=40
    snout = create_box(size=(40, 24, 40), location=(0, 53, 40), name="Snout")
    apply_boolean_union(body, snout)
    snout_bore = create_cylinder(radius=9, depth=35, location=(0, 50, 40), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, snout_bore)
    for sx in [-13, 13]:
        for sz in [27, 53]:
            sh = create_cylinder(radius=2.1, depth=15, location=(sx, 65, sz), rotation=(math.pi/2, 0, 0))
            apply_boolean_difference(body, sh)
            
    # Right side bearing seat boss on +X face: OD 65, depth 16 extending to X=93 at Z=40
    r_boss = create_cylinder(radius=32.5, depth=16, location=(85, 0, 40), rotation=(0, math.pi/2, 0), name="RightBoss")
    apply_boolean_union(body, r_boss)
    # Stepped bore: Phi 45 depth 12, Phi 30 depth 15, Phi 25 through
    r_bore1 = create_cylinder(radius=22.5, depth=15, location=(87, 0, 40), rotation=(0, math.pi/2, 0))
    apply_boolean_difference(body, r_bore1)
    r_bore2 = create_cylinder(radius=15, depth=25, location=(75, 0, 40), rotation=(0, math.pi/2, 0))
    apply_boolean_difference(body, r_bore2)
    
    # 2x rear mounting ears at back Y=-41
    ear1 = create_box(size=(22, 14, 25), location=(-60, -48, 12.5), name="EarL")
    apply_boolean_union(body, ear1)
    ear2 = create_box(size=(22, 14, 25), location=(60, -48, 12.5), name="EarR")
    apply_boolean_union(body, ear2)
    drill_hole(body, radius=3.0, depth=30, location=(-60, -48, 12.5))
    drill_hole(body, radius=3.0, depth=30, location=(60, -48, 12.5))
    
    return body, "machined_steel"

# ==============================================================================
# 10. LJT06.10_泵体 (Pump Body)
# ==============================================================================
def generate_ljt06_10():
    # Base plate: 156 x 75 x 12 mm
    body = create_box(size=(156, 75, 12), location=(0, 0, 6), name="LJT06_10_Base")
    
    # 4x Phi 9 holes at (+-68, +-27.5)
    for sx in [-68, 68]:
        for sy in [-27.5, 27.5]:
            drill_hole(body, radius=4.5, depth=20, location=(sx, sy, 6))
            
    # Main vertical pump cylinder centered at X=-15, Y=0: OD 74, height 88 (Z: 12..100)
    cyl_v = create_cylinder(radius=37, depth=88, location=(-15, 0, 56), name="CylV")
    apply_boolean_union(body, cyl_v)
    
    # Top flange: OD 88, thickness 10 at Z=95
    flange_v = create_cylinder(radius=44, depth=10, location=(-15, 0, 95), name="FlangeV")
    apply_boolean_union(body, flange_v)
    
    # Bore Phi 50 through vertical cylinder down to Z=15
    bore_v = create_cylinder(radius=25, depth=90, location=(-15, 0, 60))
    apply_boolean_difference(body, bore_v)
    
    # 4x M6 tapped holes on top flange (PCD 70)
    for i in range(4):
        ang = i * math.pi / 2
        fx = -15 + 35 * math.cos(ang)
        fy = 35 * math.sin(ang)
        fh = create_cylinder(radius=2.5, depth=18, location=(fx, fy, 95))
        apply_boolean_difference(body, fh)
        
    # Horizontal piston cylinder extending along +X from X=-15 to X=55 at Z=50, Y=0: OD 52
    cyl_h = create_cylinder(radius=26, depth=70, location=(20, 0, 50), rotation=(0, math.pi/2, 0), name="CylH")
    apply_boolean_union(body, cyl_h)
    
    # Front 3-bolt round flange at X=55: OD 72, thickness 12
    flange_h = create_cylinder(radius=36, depth=12, location=(55, 0, 50), rotation=(0, math.pi/2, 0), name="FlangeH")
    apply_boolean_union(body, flange_h)
    
    # Bore Phi 30 through horizontal cylinder into vertical chamber
    bore_h = create_cylinder(radius=15, depth=75, location=(20, 0, 50), rotation=(0, math.pi/2, 0))
    apply_boolean_difference(body, bore_h)
    
    # 3x M6 holes on PCD 58 at front flange
    for i in range(3):
        ang = i * 2 * math.pi / 3
        hy = 29 * math.cos(ang)
        hz = 50 + 29 * math.sin(ang)
        hh = create_cylinder(radius=2.5, depth=18, location=(55, hy, hz), rotation=(0, math.pi/2, 0))
        apply_boolean_difference(body, hh)
        
    # 2x side oil ports with M14x1.5 bosses along +Y and -Y at X=-15, Z=45
    for sy in [-37, 37]:
        boss = create_cylinder(radius=12, depth=15, location=(-15, sy, 45), rotation=(math.pi/2, 0, 0))
        apply_boolean_union(body, boss)
        port_h = create_cylinder(radius=6.0, depth=25, location=(-15, sy, 45), rotation=(math.pi/2, 0, 0))
        apply_boolean_difference(body, port_h)
        
    return body, "cast_iron"

# ==============================================================================
# 11. LJT06.11_尾架体 (Lathe Tailstock Body)
# ==============================================================================
def generate_ljt06_11():
    # Base: 150 x 200 x 35 mm (X: -75..75, Y: -100..100, Z: 0..35)
    body = create_box(size=(150, 200, 35), location=(0, 0, 17.5), name="LJT06_11_Base")
    
    # Precision guide slot on bottom face: central slot width 18, depth 8 mm (Y: -100..100)
    slot = create_box(size=(18, 205, 10), location=(0, 0, 4), name="GuideSlot")
    apply_boolean_difference(body, slot)
    
    # V-way guideway triangular cut on left bottom side
    v_cut = create_box(size=(20, 205, 10), location=(-55, 0, 4), rotation=(0, math.pi/4, 0), name="VWay")
    apply_boolean_difference(body, v_cut)
    
    # 2x Phi 18 through clamping holes at (0, +-50)
    drill_hole(body, radius=9.0, depth=45, location=(0, -50, 17.5))
    drill_hole(body, radius=9.0, depth=45, location=(0, 50, 17.5))
    
    # Upper quill barrel along Y axis at X=0, Z=110: OD 96, length 242 mm (Y: -121..121)
    barrel = create_cylinder(radius=48, depth=242, location=(0, 0, 110), rotation=(math.pi/2, 0, 0), name="QuillBarrel")
    apply_boolean_union(body, barrel)
    
    # Central through bore Phi 62
    q_bore = create_cylinder(radius=31, depth=250, location=(0, 0, 110), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, q_bore)
    
    # Rear counterbore Phi 76 depth 35 (at Y=-121)
    q_cbore = create_cylinder(radius=38, depth=35, location=(0, -110, 110), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, q_cbore)
    
    # Front face 8x M8 holes on PCD 80 at Y=121
    for i in range(8):
        ang = i * math.pi / 4
        hx = 40 * math.cos(ang)
        hz = 110 + 40 * math.sin(ang)
        fh = create_cylinder(radius=3.4, depth=20, location=(hx, 115, hz), rotation=(math.pi/2, 0, 0))
        apply_boolean_difference(body, fh)
        
    # Central bridging web/casting connecting base to barrel
    bridge = create_box(size=(90, 160, 65), location=(0, 0, 65), name="Bridge")
    apply_boolean_union(body, bridge)
    
    # Side lightening pockets in bridge
    pocket_l = create_box(size=(25, 110, 45), location=(-45, 0, 65), name="PocketL")
    apply_boolean_difference(body, pocket_l)
    pocket_r = create_box(size=(25, 110, 45), location=(45, 0, 65), name="PocketR")
    apply_boolean_difference(body, pocket_r)
    
    # Side split-clamp ear on +X side at X=48, Y=60, Z=110: boss OD 48, bore 24
    clamp_boss = create_cylinder(radius=24, depth=30, location=(52, 60, 110), rotation=(0, math.pi/2, 0), name="ClampBoss")
    apply_boolean_union(body, clamp_boss)
    clamp_bore = create_cylinder(radius=12, depth=40, location=(52, 60, 110), rotation=(0, math.pi/2, 0))
    apply_boolean_difference(body, clamp_bore)
    # Split slit
    slit = create_box(size=(45, 30, 4), location=(52, 60, 110), name="ClampSlit")
    apply_boolean_difference(body, slit)
    
    return body, "cast_iron"

# ==============================================================================
# 12. LJT06.12_泵体 (Gear Pump Body)
# ==============================================================================
def generate_ljt06_12():
    # Base mounting flange: 108 x 58 x 12 mm
    body = create_box(size=(108, 58, 12), location=(0, 0, 6), name="LJT06_12_Base")
    
    # 2x Phi 11 holes at (+-40, 0)
    drill_hole(body, radius=5.5, depth=20, location=(-40, 0, 6))
    drill_hole(body, radius=5.5, depth=20, location=(40, 0, 6))
    
    # Main pump body block: 86 x 68 x 73 mm (Z: 12..85, Y: -34..34, X: -43..43)
    block = create_box(size=(86, 68, 73), location=(0, 0, 48.5), name="MainBlock")
    apply_boolean_union(body, block)
    
    # Figure-8 gear cavity along Y axis: two overlapping bores R30 (Phi 60), center distance 42H8 (centers at X=+-21, Z=48)
    # Cavity depth 23 mm from front face Y=34 down to Y=11
    cavity1 = create_cylinder(radius=30, depth=25, location=(-21, 23, 48), rotation=(math.pi/2, 0, 0), name="CavityL")
    apply_boolean_difference(body, cavity1)
    cavity2 = create_cylinder(radius=30, depth=25, location=(21, 23, 48), rotation=(math.pi/2, 0, 0), name="CavityR")
    apply_boolean_difference(body, cavity2)
    
    # Dual shaft bores: Phi 18 through from Y=11 to Y=-34 at X=+-21, Z=48
    shaft1 = create_cylinder(radius=9, depth=50, location=(-21, -10, 48), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, shaft1)
    shaft2 = create_cylinder(radius=9, depth=50, location=(21, -10, 48), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, shaft2)
    
    # 6x M6 holes on front face around figure-8
    f_holes = [(-38, 30, 48), (38, 30, 48), (-21, 30, 80), (21, 30, 80), (-21, 30, 16), (21, 30, 16)]
    for hx, hy, hz in f_holes:
        fh = create_cylinder(radius=2.5, depth=18, location=(hx, hy, hz), rotation=(math.pi/2, 0, 0))
        apply_boolean_difference(body, fh)
        
    # Backside port boss at Y=-34: OD 40, depth 15
    back_boss = create_cylinder(radius=20, depth=15, location=(0, -40, 48), rotation=(math.pi/2, 0, 0), name="BackBoss")
    apply_boolean_union(body, back_boss)
    back_bore = create_cylinder(radius=12, depth=35, location=(0, -35, 48), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, back_bore)
    
    return body, "cast_iron"

# ==============================================================================
# 13. LJT06.13_阀体 (Valve Body - Three-Way Flanged)
# ==============================================================================
def generate_ljt06_13():
    # Central vertical cylinder: OD 55, height 110 mm (Z: -55..55)
    body = create_cylinder(radius=27.5, depth=110, location=(0, 0, 0), name="LJT06_13_Body")
    
    # Top 4-lobed / square flange: 74 x 74 x 12 mm at Z=49
    top_flange = create_box(size=(74, 74, 12), location=(0, 0, 49), name="TopFlange")
    apply_boolean_union(body, top_flange)
    # 4x M6 holes on top flange at (+-26, +-26)
    for sx in [-26, 26]:
        for sy in [-26, 26]:
            drill_hole(body, radius=2.5, depth=18, location=(sx, sy, 49))
            
    # Bottom flange: OD 75, thickness 12 mm at Z=-49
    bot_flange = create_cylinder(radius=37.5, depth=12, location=(0, 0, -49), name="BotFlange")
    apply_boolean_union(body, bot_flange)
    # 4x M6 holes on PCD 60
    for i in range(4):
        ang = i * math.pi / 2
        bx = 30 * math.cos(ang)
        by = 30 * math.sin(ang)
        drill_hole(body, radius=2.5, depth=18, location=(bx, by, -49))
        
    # Central bore Phi 34 through Z
    v_bore = create_cylinder(radius=17, depth=120, location=(0, 0, 0))
    apply_boolean_difference(body, v_bore)
    
    # Transverse side nozzles along X axis at Z=0: total face-to-face 105 mm (X: -52.5..52.5)
    nozzle = create_cylinder(radius=21, depth=105, location=(0, 0, 0), rotation=(0, math.pi/2, 0), name="Nozzle")
    apply_boolean_union(body, nozzle)
    
    # Transverse bore Phi 25 through X
    h_bore = create_cylinder(radius=12.5, depth=120, location=(0, 0, 0), rotation=(0, math.pi/2, 0))
    apply_boolean_difference(body, h_bore)
    
    # Two side round flanges: OD 78, thickness 10 mm at X=-47.5 and X=47.5
    for sx in [-47.5, 47.5]:
        flange_s = create_cylinder(radius=39, depth=10, location=(sx, 0, 0), rotation=(0, math.pi/2, 0))
        apply_boolean_union(body, flange_s)
        # 4x Phi 9 holes on PCD 60
        for i in range(4):
            ang = i * math.pi / 2
            fy = 30 * math.cos(ang)
            fz = 30 * math.sin(ang)
            sh = create_cylinder(radius=4.5, depth=16, location=(sx, fy, fz), rotation=(0, math.pi/2, 0))
            apply_boolean_difference(body, sh)
            
    return body, "cast_iron"

# ==============================================================================
# 14. LJT06.14_蜗轮箱 (Worm Gearbox Housing)
# ==============================================================================
def generate_ljt06_14():
    # Base mounting frame: 145 x 120 x 14 mm
    body = create_box(size=(145, 120, 14), location=(0, 0, 7), name="LJT06_14_Base")
    
    # 4x Phi 11 holes at (+-60, +-47.5)
    for sx in [-60, 60]:
        for sy in [-47.5, 47.5]:
            drill_hole(body, radius=5.5, depth=20, location=(sx, sy, 7))
            
    # Lower worm shaft tunnel along X axis at Z=35, Y=0: OD 62, length 130 mm (X: -65..65)
    tunnel = create_cylinder(radius=31, depth=130, location=(0, 0, 35), rotation=(0, math.pi/2, 0), name="Tunnel")
    apply_boolean_union(body, tunnel)
    
    # Worm bore Phi 42 through X
    w_bore = create_cylinder(radius=21, depth=140, location=(0, 0, 35), rotation=(0, math.pi/2, 0))
    apply_boolean_difference(body, w_bore)
    
    # Upper worm wheel chamber along Y axis at X=0, Z=100 (center distance 65 mm): OD 115, width 85 mm (Y: -42.5..42.5)
    wheel_chamber = create_cylinder(radius=57.5, depth=85, location=(0, 0, 100), rotation=(math.pi/2, 0, 0), name="WheelChamber")
    apply_boolean_union(body, wheel_chamber)
    
    # Wheel bore Phi 80 through Y
    wh_bore = create_cylinder(radius=40, depth=95, location=(0, 0, 100), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, wh_bore)
    
    # Side cover flange on +Y face: OD 125, thickness 12 at Y=42.5
    cov_flange = create_cylinder(radius=62.5, depth=12, location=(0, 42.5, 100), rotation=(math.pi/2, 0, 0), name="CovFlange")
    apply_boolean_union(body, cov_flange)
    # 6x M6 holes on PCD 100
    for i in range(6):
        ang = i * math.pi / 3
        hx = 50 * math.cos(ang)
        hz = 100 + 50 * math.sin(ang)
        hh = create_cylinder(radius=2.5, depth=18, location=(hx, 42.5, hz), rotation=(math.pi/2, 0, 0))
        apply_boolean_difference(body, hh)
        
    # Cast transition shell bridging lower tunnel and upper chamber
    mid_shell = create_box(size=(90, 75, 60), location=(0, 0, 65), name="MidShell")
    apply_boolean_union(body, mid_shell)
    # Internal hollow cavity
    mid_cavity = create_box(size=(72, 58, 50), location=(0, 0, 65), name="MidCavity")
    apply_boolean_difference(body, mid_cavity)
    
    # Top inspection boss at Z=130: OD 32, height 12 with M20 hole
    top_boss = create_cylinder(radius=16, depth=12, location=(0, 0, 130), name="TopBoss")
    apply_boolean_union(body, top_boss)
    top_hole = create_cylinder(radius=9, depth=20, location=(0, 0, 130))
    apply_boolean_difference(body, top_hole)
    
    return body, "cast_iron"

# ==============================================================================
# 15. LJT06.15_泵体 (Pump Volute Casing)
# ==============================================================================
def generate_ljt06_15():
    # Base mounting feet: 160 x 90 x 16 mm
    body = create_box(size=(160, 90, 16), location=(0, 0, 8), name="LJT06_15_Base")
    
    # 4x Phi 12 holes at (+-65, +-30)
    for sx in [-65, 65]:
        for sy in [-30, 30]:
            drill_hole(body, radius=6.0, depth=25, location=(sx, sy, 8))
            
    # Main volute casing along Y axis at X=0, Z=85: OD 140, depth 35 mm (Y: -10..25)
    volute = create_cylinder(radius=70, depth=35, location=(0, 7.5, 85), rotation=(math.pi/2, 0, 0), name="Volute")
    apply_boolean_union(body, volute)
    
    # Front ring flange at Y=25: OD 150, thickness 12
    f_ring = create_cylinder(radius=75, depth=12, location=(0, 25, 85), rotation=(math.pi/2, 0, 0), name="FrontRing")
    apply_boolean_union(body, f_ring)
    
    # Internal impeller chamber bore Phi 110, depth 32
    chamber_bore = create_cylinder(radius=55, depth=35, location=(0, 15, 85), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, chamber_bore)
    
    # 6x M8 holes on front ring (PCD 125)
    for i in range(6):
        ang = i * math.pi / 3
        hx = 62.5 * math.cos(ang)
        hz = 85 + 62.5 * math.sin(ang)
        fh = create_cylinder(radius=3.4, depth=18, location=(hx, 25, hz), rotation=(math.pi/2, 0, 0))
        apply_boolean_difference(body, fh)
        
    # Discharge nozzle (top vertical): from Z=85 up to Z=160. OD 65, bore Phi 32
    d_nozzle = create_cylinder(radius=32.5, depth=75, location=(25, 7.5, 122.5), name="DischargeNozzle")
    apply_boolean_union(body, d_nozzle)
    
    # Top circular flange at Z=160: OD 95, thickness 14
    d_flange = create_cylinder(radius=47.5, depth=14, location=(25, 7.5, 160), name="DischargeFlange")
    apply_boolean_union(body, d_flange)
    
    # Discharge bore Phi 32 through into chamber
    d_bore = create_cylinder(radius=16, depth=95, location=(25, 7.5, 125))
    apply_boolean_difference(body, d_bore)
    
    # 4x Phi 12 holes on top flange (PCD 75)
    for i in range(4):
        ang = i * math.pi / 2
        hx = 25 + 37.5 * math.cos(ang)
        hy = 7.5 + 37.5 * math.sin(ang)
        dh = create_cylinder(radius=6.0, depth=22, location=(hx, hy, 160))
        apply_boolean_difference(body, dh)
        
    # Rear bearing support neck along -Y from Y=-10 to Y=-45: OD 60, bore Phi 35
    rear_neck = create_cylinder(radius=30, depth=35, location=(0, -27.5, 85), rotation=(math.pi/2, 0, 0), name="RearNeck")
    apply_boolean_union(body, rear_neck)
    r_bore = create_cylinder(radius=17.5, depth=45, location=(0, -27.5, 85), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, r_bore)
    
    # Base support pedestal connecting base to volute
    pedestal = create_box(size=(100, 60, 45), location=(0, 0, 35), name="Pedestal")
    apply_boolean_union(body, pedestal)
    
    return body, "cast_iron"

# ==============================================================================
# BATCH GENERATOR LIST & RUNNER
# ==============================================================================

GENERATORS = [
    ("LJT06.01_缸体", generate_ljt06_01),
    ("LJT06.02_箱体", generate_ljt06_02),
    ("LJT06.03_阀体", generate_ljt06_03),
    ("LJT06.04_缸体", generate_ljt06_04),
    ("LJT06.05_传动箱", generate_ljt06_05),
    ("LJT06.06_阀体", generate_ljt06_06),
    ("LJT06.07_蜗轮壳", generate_ljt06_07),
    ("LJT06.08_泵缸", generate_ljt06_08),
    ("LJT06.09_箱体", generate_ljt06_09),
    ("LJT06.10_泵体", generate_ljt06_10),
    ("LJT06.11_尾架体", generate_ljt06_11),
    ("LJT06.12_泵体", generate_ljt06_12),
    ("LJT06.13_阀体", generate_ljt06_13),
    ("LJT06.14_蜗轮箱", generate_ljt06_14),
    ("LJT06.15_泵体", generate_ljt06_15),
]

def run_batch():
    print(f"\n{'='*70}")
    print(f"STARTING CATEGORY 06 BATCH 1 GENERATION (15 PARTS: LJT06.01 ~ LJT06.15)")
    print(f"{'='*70}\n")
    
    success_count = 0
    fail_count = 0
    
    for part_name, gen_func in GENERATORS:
        blend_path = os.path.join(cat_dir, f"{part_name}.blend")
        render_path = os.path.join(renders_dir, f"{part_name}.png")
        
        print(f"\n[GENERATING] {part_name} ...")
        try:
            # Clear scene before modeling
            bpy.ops.wm.read_factory_settings(use_empty=True)
            
            # Generate model
            obj, mat_type = gen_func()
            
            # Render and save
            bcg.render_and_save(obj, blend_path, render_path, mat_type=mat_type)
            print(f"[COMPLETED] {part_name} -> {blend_path}")
            success_count += 1
        except Exception as e:
            print(f"[FAILED] {part_name}: {e}")
            import traceback
            traceback.print_exc()
            fail_count += 1
            
    print(f"\n{'='*70}")
    print(f"BATCH SUMMARY: {success_count} succeeded, {fail_count} failed out of {len(GENERATORS)} parts.")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    run_batch()
