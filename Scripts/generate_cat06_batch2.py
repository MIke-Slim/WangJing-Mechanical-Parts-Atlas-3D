"""
Category 06 Batch 2: 箱壳类零件 (Housings & Casings - Part 2)
Generates the next 15 models for Category 06:
  LJT06.16_液压缸,   LJT06.17_阀体,   LJT06.18_阀体,   LJT06.19_箱体,
  LJT06.20_蜗轮壳,   LJT06.21_阀体,   LJT06.22_箱体,   LJT06.23_阀体,
  LJT06.24_喷雾器壳体, LJT06.25_箱体,   LJT06.26_箱体,   LJT06.27_泵体,
  LJT06.28_泵体,   LJT06.29_阀体,   LJT06.30_阀体
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

# ==============================================================================
# 16. LJT06.16_液压缸 (Hydraulic Cylinder with Tripod Support Base)
# ==============================================================================
def generate_ljt06_16():
    # Circular base mounting flange: OD 140, thickness 14 mm
    body = create_cylinder(radius=70, depth=14, location=(0, 0, 7), name="LJT06_16_Base")
    
    # Central hole in base: Phi 60
    base_hole = create_cylinder(radius=30, depth=20, location=(0, 0, 7))
    apply_boolean_difference(body, base_hole)
    
    # 4x Phi 11 holes on PCD 115
    for i in range(4):
        ang = i * math.pi / 2
        hx = 57.5 * math.cos(ang)
        hy = 57.5 * math.sin(ang)
        drill_hole(body, radius=5.5, depth=20, location=(hx, hy, 7))
        
    # 3 upright cast support legs spaced at 120 deg from Z=14 to Z=85
    for i in range(3):
        ang = i * 2 * math.pi / 3 + math.pi / 6
        lx = 50 * math.cos(ang)
        ly = 50 * math.sin(ang)
        leg = create_box(size=(14, 28, 71), location=(lx, ly, 49.5), rotation=(0, 0, ang), name=f"Leg_{i}")
        apply_boolean_union(body, leg)
        
    # Upper cylinder barrel: OD 75, height 80 (Z: 70..150)
    barrel = create_cylinder(radius=37.5, depth=80, location=(0, 0, 110), name="Barrel")
    apply_boolean_union(body, barrel)
    
    # Top rim flange: OD 88, thickness 12 (Z: 138..150)
    top_flange = create_cylinder(radius=44, depth=12, location=(0, 0, 144), name="TopFlange")
    apply_boolean_union(body, top_flange)
    
    # Inner hydraulic cylinder sleeve extending down to Z=50: OD 60, height 30
    sleeve = create_cylinder(radius=30, depth=30, location=(0, 0, 65), name="LowerSleeve")
    apply_boolean_union(body, sleeve)
    
    # Central bore: Phi 45 through from Z=150 down to Z=50
    cbore = create_cylinder(radius=22.5, depth=110, location=(0, 0, 100), name="CylinderBore")
    apply_boolean_difference(body, cbore)
    
    # 4x M6 tapped holes on top flange (PCD 76)
    for i in range(4):
        ang = i * math.pi / 2 + math.pi / 4
        tx = 38 * math.cos(ang)
        ty = 38 * math.sin(ang)
        drill_hole(body, radius=2.5, depth=18, location=(tx, ty, 144))
        
    # 2 side port bosses on +X side: at Z=85 and Z=130, OD 24, height 10, bore M14 (Phi 12)
    for pz in [85, 130]:
        boss = create_cylinder(radius=12, depth=15, location=(40, 0, pz), rotation=(0, math.pi/2, 0), name="PortBoss")
        apply_boolean_union(body, boss)
        port_h = create_cylinder(radius=6.0, depth=35, location=(35, 0, pz), rotation=(0, math.pi/2, 0))
        apply_boolean_difference(body, port_h)
        
    return body, "machined_steel"

# ==============================================================================
# 17. LJT06.17_阀体 (Valve Body - Manifold / Flanged)
# ==============================================================================
def generate_ljt06_17():
    # Base mounting plate: 90 x 65 x 12 mm
    body = create_box(size=(90, 65, 12), location=(0, 0, 6), name="LJT06_17_Base")
    
    # 4x Phi 9 holes at (+-36, +-23.5)
    for sx in [-36, 36]:
        for sy in [-23.5, 23.5]:
            drill_hole(body, radius=4.5, depth=20, location=(sx, sy, 6))
            
    # Lower neck: OD 40, height 25 (Z: 12..37)
    neck = create_cylinder(radius=20, depth=25, location=(0, 0, 24.5), name="Neck")
    apply_boolean_union(body, neck)
    
    # Main valve body tower: OD 52, height 60 (Z: 35..95)
    tower = create_cylinder(radius=26, depth=60, location=(0, 0, 65), name="Tower")
    apply_boolean_union(body, tower)
    
    # Right branch cylinder: OD 44, length 55 along +X from X=0 to 55 at Z=65
    r_branch = create_cylinder(radius=22, depth=55, location=(27.5, 0, 65), rotation=(0, math.pi/2, 0), name="RBranch")
    apply_boolean_union(body, r_branch)
    
    # Right 4-eared flange: OD 64, thickness 10 at X=55
    r_flange = create_cylinder(radius=32, depth=10, location=(55, 0, 65), rotation=(0, math.pi/2, 0), name="RFlange")
    apply_boolean_union(body, r_flange)
    
    # 4x M6 tapped holes on right flange
    for ang in [math.pi/4, 3*math.pi/4, 5*math.pi/4, 7*math.pi/4]:
        ry = 23 * math.cos(ang)
        rz = 65 + 23 * math.sin(ang)
        rh = create_cylinder(radius=2.5, depth=18, location=(55, ry, rz), rotation=(0, math.pi/2, 0))
        apply_boolean_difference(body, rh)
        
    # Front square port boss on -Y face at Z=50: 34 x 18 x 34 mm
    f_boss = create_box(size=(34, 18, 34), location=(0, -28, 50), name="FBoss")
    apply_boolean_union(body, f_boss)
    f_bore = create_cylinder(radius=7.0, depth=25, location=(0, -28, 50), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, f_bore)
    
    # Top threaded port: M27x2 (bore Phi 24, depth 35)
    top_bore = create_cylinder(radius=12, depth=40, location=(0, 0, 80))
    apply_boolean_difference(body, top_bore)
    
    # Right branch bore: Phi 22 through into tower
    r_bore = create_cylinder(radius=11, depth=65, location=(30, 0, 65), rotation=(0, math.pi/2, 0))
    apply_boolean_difference(body, r_bore)
    
    # Central internal passage down to base
    c_pass = create_cylinder(radius=10, depth=55, location=(0, 0, 40))
    apply_boolean_difference(body, c_pass)
    
    return body, "cast_iron"

# ==============================================================================
# 18. LJT06.18_阀体 (Valve Body - Elbow / Three-Way)
# ==============================================================================
def generate_ljt06_18():
    # Bottom circular flange: OD 75, thickness 10 mm
    body = create_cylinder(radius=37.5, depth=10, location=(0, 0, 5), name="LJT06_18_Base")
    
    # 4x Phi 9 holes on PCD 60
    for i in range(4):
        ang = i * math.pi / 2
        hx = 30 * math.cos(ang)
        hy = 30 * math.sin(ang)
        drill_hole(body, radius=4.5, depth=15, location=(hx, hy, 5))
        
    # Central cylinder body: OD 65, height 65 (Z: 10..75)
    cyl = create_cylinder(radius=32.5, depth=65, location=(0, 0, 42.5), name="CylBody")
    apply_boolean_union(body, cyl)
    
    # Front threaded nozzle along +Y at Z=45: OD 44, length 30
    f_nozzle = create_cylinder(radius=22, depth=30, location=(0, 30, 45), rotation=(math.pi/2, 0, 0), name="FrontNozzle")
    apply_boolean_union(body, f_nozzle)
    f_bore = create_cylinder(radius=12, depth=40, location=(0, 30, 45), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, f_bore)
    
    # Side circular cover flange on +X face at Z=45: OD 70, thickness 10
    s_flange = create_cylinder(radius=35, depth=10, location=(35, 0, 45), rotation=(0, math.pi/2, 0), name="SideFlange")
    apply_boolean_union(body, s_flange)
    
    # Side cavity bore Phi 42, depth 25
    s_bore = create_cylinder(radius=21, depth=30, location=(30, 0, 45), rotation=(0, math.pi/2, 0))
    apply_boolean_difference(body, s_bore)
    
    # 3 tapped lug ears on side flange (3x M6 on PCD 62)
    for i in range(3):
        ang = i * 2 * math.pi / 3 + math.pi / 6
        sy = 31 * math.cos(ang)
        sz = 45 + 31 * math.sin(ang)
        sh = create_cylinder(radius=2.5, depth=16, location=(35, sy, sz), rotation=(0, math.pi/2, 0))
        apply_boolean_difference(body, sh)
        
    # Upper elbow pipe: branching towards -X, +Z at 45 deg, terminating at (-30, 0, 85)
    elbow_pipe = create_cylinder(radius=18, depth=45, location=(-20, 0, 70), rotation=(0, -math.pi/4, 0), name="ElbowPipe")
    apply_boolean_union(body, elbow_pipe)
    
    # 2-bolt diamond flange at elbow end: pitch 65, thickness 10
    d_flange = create_box(size=(65, 36, 10), location=(-32, 0, 82), rotation=(0, -math.pi/4, 0), name="DiamondFlange")
    apply_boolean_union(body, d_flange)
    
    # Elbow bore Phi 22 through
    e_bore = create_cylinder(radius=11, depth=60, location=(-22, 0, 72), rotation=(0, -math.pi/4, 0))
    apply_boolean_difference(body, e_bore)
    
    # Diamond flange bolt holes (2x Phi 11)
    for offset in [-23, 23]:
        # vector perpendicular in flange plane
        dh = create_cylinder(radius=5.5, depth=20, location=(-32 + offset * math.cos(math.pi/4), 0, 82 + offset * math.sin(math.pi/4)), rotation=(0, -math.pi/4, 0))
        apply_boolean_difference(body, dh)
        
    return body, "cast_iron"

# ==============================================================================
# 19. LJT06.19_箱体 (Open Gearbox Housing)
# ==============================================================================
def generate_ljt06_19():
    # Base plate: 125 x 95 x 12 mm
    body = create_box(size=(125, 95, 12), location=(0, 0, 6), name="LJT06_19_Base")
    
    # 4 counterbore holes at (+-48, +-35): hole Phi 11, cbore Phi 18 depth 6
    for sx in [-48, 48]:
        for sy in [-35, 35]:
            drill_hole(body, radius=5.5, depth=20, location=(sx, sy, 6))
            cb = create_cylinder(radius=9.0, depth=8, location=(sx, sy, 9))
            apply_boolean_difference(body, cb)
            
    # Open-top rectangular box: 90 x 80 x 85 mm (Z: 12..97)
    box = create_box(size=(90, 80, 85), location=(0, 0, 54.5), name="BoxBody")
    apply_boolean_union(body, box)
    
    # Hollow interior cavity: 76 x 66 x 80 mm (wall thickness 7 mm)
    cavity = create_box(size=(76, 66, 82), location=(0, 0, 57), name="Cavity")
    apply_boolean_difference(body, cavity)
    
    # 4x M6 tapped holes at top rim corners (+-40, +-35)
    for tx in [-40, 40]:
        for ty in [-35, 35]:
            th = create_cylinder(radius=2.5, depth=18, location=(tx, ty, 97))
            apply_boolean_difference(body, th)
            
    # Front circular bearing boss on -Y face (Y=-40): OD 72, thickness 8, center Z=50
    f_boss = create_cylinder(radius=36, depth=8, location=(0, -40, 50), rotation=(math.pi/2, 0, 0), name="FrontBoss")
    apply_boolean_union(body, f_boss)
    
    # Through bearing bore Phi 38
    f_bore = create_cylinder(radius=19, depth=25, location=(0, -40, 50), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, f_bore)
    
    # 4 radial oil notches on front boss face
    for ang in [0, math.pi/2, math.pi, 3*math.pi/2]:
        nx = 28 * math.cos(ang)
        nz = 50 + 28 * math.sin(ang)
        notch = create_box(size=(3, 6, 12), location=(nx, -44, nz), rotation=(0, ang, 0))
        apply_boolean_difference(body, notch)
        
    # Rear circular bearing boss on +Y face (Y=40): OD 60, thickness 8, center Z=50
    r_boss = create_cylinder(radius=30, depth=8, location=(0, 40, 50), rotation=(math.pi/2, 0, 0), name="RearBoss")
    apply_boolean_union(body, r_boss)
    r_bore = create_cylinder(radius=15, depth=25, location=(0, 40, 50), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, r_bore)
    
    return body, "cast_iron"

# ==============================================================================
# 20. LJT06.20_蜗轮壳 (Worm Reducer Housing)
# ==============================================================================
def generate_ljt06_20():
    # Base/side cast monolithic frame: 120 x 100 x 120 mm
    body = create_box(size=(85, 100, 100), location=(0, 0, 60), name="LJT06_20_Core")
    
    # Upper worm shaft tunnel along Y axis at X=0, Z=105: OD 58, length 120 mm
    w_tunnel = create_cylinder(radius=29, depth=120, location=(0, 0, 105), rotation=(math.pi/2, 0, 0), name="WormTunnel")
    apply_boolean_union(body, w_tunnel)
    
    # Worm bore Phi 36 through Y
    w_bore = create_cylinder(radius=18, depth=130, location=(0, 0, 105), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, w_bore)
    
    # Front cover seat at Y=60: notched circular flange OD 70 with 4x M5 holes
    flange_f = create_cylinder(radius=35, depth=10, location=(0, 60, 105), rotation=(math.pi/2, 0, 0))
    apply_boolean_union(body, flange_f)
    for ang in [math.pi/4, 3*math.pi/4, 5*math.pi/4, 7*math.pi/4]:
        hx = 26 * math.cos(ang)
        hz = 105 + 26 * math.sin(ang)
        fh = create_cylinder(radius=2.1, depth=16, location=(hx, 60, hz), rotation=(math.pi/2, 0, 0))
        apply_boolean_difference(body, fh)
        
    # Lower worm wheel chamber along X axis at Z=50, Y=0: OD 100, width 70 mm
    wheel_cyl = create_cylinder(radius=50, depth=70, location=(0, 0, 50), rotation=(0, math.pi/2, 0), name="WheelCyl")
    apply_boolean_union(body, wheel_cyl)
    
    # Wheel cavity bore Phi 72 through X
    wh_bore = create_cylinder(radius=36, depth=90, location=(0, 0, 50), rotation=(0, math.pi/2, 0))
    apply_boolean_difference(body, wh_bore)
    
    # Left flanged bearing snout at X=-40: circular flange OD 115, thickness 12 with 4x Phi 9 holes
    snout_flange = create_cylinder(radius=57.5, depth=12, location=(-40, 0, 50), rotation=(0, math.pi/2, 0), name="SnoutFlange")
    apply_boolean_union(body, snout_flange)
    
    # Central tubular extension OD 50, bore 35
    snout_tube = create_cylinder(radius=25, depth=25, location=(-50, 0, 50), rotation=(0, math.pi/2, 0))
    apply_boolean_union(body, snout_tube)
    snout_bore = create_cylinder(radius=17.5, depth=50, location=(-45, 0, 50), rotation=(0, math.pi/2, 0))
    apply_boolean_difference(body, snout_bore)
    
    # 4x Phi 9 holes on PCD 95 on snout flange
    for i in range(4):
        ang = i * math.pi / 2
        sy = 47.5 * math.cos(ang)
        sz = 50 + 47.5 * math.sin(ang)
        sh = create_cylinder(radius=4.5, depth=20, location=(-40, sy, sz), rotation=(0, math.pi/2, 0))
        apply_boolean_difference(body, sh)
        
    # Side stiffening ribs with cast pockets
    rib = create_box(size=(25, 80, 20), location=(20, 0, 30), name="SideRib")
    apply_boolean_union(body, rib)
    
    return body, "cast_iron"

# ==============================================================================
# 21. LJT06.21_阀体 (Valve Body - Horizontal Spool with Base)
# ==============================================================================
def generate_ljt06_21():
    # Base mounting plate: 110 x 80 x 14 mm
    body = create_box(size=(110, 80, 14), location=(0, 0, 7), name="LJT06_21_Base")
    
    # 4 counterbore holes at (+-42, +-28): hole Phi 9, cbore Phi 15 depth 5
    for sx in [-42, 42]:
        for sy in [-28, 28]:
            drill_hole(body, radius=4.5, depth=20, location=(sx, sy, 7))
            cb = create_cylinder(radius=7.5, depth=6, location=(sx, sy, 11))
            apply_boolean_difference(body, cb)
            
    # Central arched cylindrical housing along X axis from X=-35 to 35: OD 60, center Z=42, Y=0
    arch = create_cylinder(radius=30, depth=70, location=(0, 0, 42), rotation=(0, math.pi/2, 0), name="ArchHousing")
    apply_boolean_union(body, arch)
    
    # Front square flanged face at X=35: 50 x 50 x 12 mm
    f_face = create_box(size=(12, 50, 50), location=(35, 0, 42), name="FrontFace")
    apply_boolean_union(body, f_face)
    
    # Central spool bore: Phi 24 through X
    spool_bore = create_cylinder(radius=12, depth=95, location=(0, 0, 42), rotation=(0, math.pi/2, 0))
    apply_boolean_difference(body, spool_bore)
    
    # Counterbore Phi 32 depth 15 on front face
    spool_cbore = create_cylinder(radius=16, depth=16, location=(35, 0, 42), rotation=(0, math.pi/2, 0))
    apply_boolean_difference(body, spool_cbore)
    
    # 2 diagonal tapped holes M6 on front face
    for dy, dz in [(-18, 24), (18, 60)]:
        dh = create_cylinder(radius=2.5, depth=18, location=(35, dy, dz), rotation=(0, math.pi/2, 0))
        apply_boolean_difference(body, dh)
        
    # Stepped rear body behind main arch: Y: 10..35, height 35 mm (Z: 14..45)
    rear_step = create_box(size=(60, 25, 31), location=(0, 22.5, 29.5), name="RearStep")
    apply_boolean_union(body, rear_step)
    
    return body, "cast_iron"

# ==============================================================================
# 22. LJT06.22_箱体 (Rotary Actuator / Worm Gearbox Housing)
# ==============================================================================
def generate_ljt06_22():
    # Base circular flange: OD 110, thickness 12 mm
    body = create_cylinder(radius=55, depth=12, location=(0, 0, 6), name="LJT06_22_Base")
    
    # 4 counterbore holes on PCD 90: hole Phi 9, cbore Phi 15 depth 5
    for i in range(4):
        ang = i * math.pi / 2
        hx = 45 * math.cos(ang)
        hy = 45 * math.sin(ang)
        drill_hole(body, radius=4.5, depth=20, location=(hx, hy, 6))
        cb = create_cylinder(radius=7.5, depth=6, location=(hx, hy, 9))
        apply_boolean_difference(body, cb)
        
    # Lower neck: OD 70, height 20 (Z: 12..32)
    neck = create_cylinder(radius=35, depth=20, location=(0, 0, 22), name="Neck")
    apply_boolean_union(body, neck)
    
    # Upper bowl chamber: OD 130, height 65 (Z: 32..97)
    bowl = create_cylinder(radius=65, depth=65, location=(0, 0, 64.5), name="Bowl")
    apply_boolean_union(body, bowl)
    
    # Chamber internal cavity: Phi 112, depth 60 (from Z=97 down to 37)
    bowl_cavity = create_cylinder(radius=56, depth=62, location=(0, 0, 67), name="BowlCavity")
    apply_boolean_difference(body, bowl_cavity)
    
    # Bottom bearing bore: Phi 35 through neck
    neck_bore = create_cylinder(radius=17.5, depth=45, location=(0, 0, 25))
    apply_boolean_difference(body, neck_bore)
    
    # 4x M5 tapped holes on top rim (PCD 120)
    for i in range(4):
        ang = i * math.pi / 2 + math.pi / 4
        rx = 60 * math.cos(ang)
        ry = 60 * math.sin(ang)
        drill_hole(body, radius=2.1, depth=16, location=(rx, ry, 97))
        
    # Transverse worm tunnel along X axis tangent to bowl at Y=-48, Z=55: OD 46, length 110 mm
    tunnel = create_cylinder(radius=23, depth=110, location=(0, -48, 55), rotation=(0, math.pi/2, 0), name="WormTunnel")
    apply_boolean_union(body, tunnel)
    
    # Stepped bore through tunnel: Phi 28 through
    t_bore = create_cylinder(radius=14, depth=120, location=(0, -48, 55), rotation=(0, math.pi/2, 0))
    apply_boolean_difference(body, t_bore)
    
    # 4x M5 holes on each end face of the tunnel (X=+-55)
    for sx in [-55, 55]:
        for ang in [math.pi/4, 3*math.pi/4, 5*math.pi/4, 7*math.pi/4]:
            ey = -48 + 17 * math.cos(ang)
            ez = 55 + 17 * math.sin(ang)
            eh = create_cylinder(radius=2.1, depth=15, location=(sx, ey, ez), rotation=(0, math.pi/2, 0))
            apply_boolean_difference(body, eh)
            
    return body, "cast_iron"

# ==============================================================================
# 23. LJT06.23_阀体 (Hydraulic Manifold Block)
# ==============================================================================
def generate_ljt06_23():
    # Main block: 95 x 65 x 52 mm
    body = create_box(size=(95, 65, 52), location=(0, 0, 26), name="LJT06_23_Block")
    
    # Top mounting ear lobes at X=+-35, Y=32.5: cylinder radius 12, height 15
    for sx in [-35, 35]:
        lobe = create_cylinder(radius=12, depth=15, location=(sx, 32.5, 44.5), name="Lobe")
        apply_boolean_union(body, lobe)
        lh = create_cylinder(radius=3.4, depth=22, location=(sx, 32.5, 44.5))
        apply_boolean_difference(body, lh)
        
    # Top 2 counterbored mounting holes at (+-18, 5): hole Phi 9, cbore Phi 15 depth 8
    for sx in [-18, 18]:
        drill_hole(body, radius=4.5, depth=60, location=(sx, 5, 26))
        cb = create_cylinder(radius=7.5, depth=10, location=(sx, 5, 48))
        apply_boolean_difference(body, cb)
        
    # Front diamond/oval mounting flange at Y=-32.5: 85 x 10 x 36 mm
    d_flange = create_box(size=(85, 10, 36), location=(0, -32.5, 26), name="DFlange")
    apply_boolean_union(body, d_flange)
    
    # Diamond flange center port Phi 16
    f_port = create_cylinder(radius=8, depth=25, location=(0, -32.5, 26), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, f_port)
    
    # 2x M8 holes on diamond flange at (+-34, -32.5, 26)
    for sx in [-34, 34]:
        dh = create_cylinder(radius=3.4, depth=18, location=(sx, -32.5, 26), rotation=(math.pi/2, 0, 0))
        apply_boolean_difference(body, dh)
        
    # Side threaded port boss on -X face (X=-47.5): OD 36, depth 8, internal thread M20x1.5 (bore Phi 18)
    s_boss = create_cylinder(radius=18, depth=8, location=(-47.5, 0, 26), rotation=(0, math.pi/2, 0), name="SBoss")
    apply_boolean_union(body, s_boss)
    s_bore = create_cylinder(radius=9, depth=25, location=(-47.5, 0, 26), rotation=(0, math.pi/2, 0))
    apply_boolean_difference(body, s_bore)
    
    return body, "machined_steel"

# ==============================================================================
# 24. LJT06.24_喷雾器壳体 (Sprayer Housing)
# ==============================================================================
def generate_ljt06_24():
    # Circular base plate: OD 115, thickness 10 mm
    body = create_cylinder(radius=57.5, depth=10, location=(0, 0, 5), name="LJT06_24_Base")
    
    # 4 outer mounting ears at radius 55 mm
    for i in range(4):
        ang = i * math.pi / 2 + math.pi / 4
        ex = 55 * math.cos(ang)
        ey = 55 * math.sin(ang)
        ear = create_cylinder(radius=14, depth=10, location=(ex, ey, 5))
        apply_boolean_union(body, ear)
        drill_hole(body, radius=4.5, depth=18, location=(ex, ey, 5))
        cb = create_cylinder(radius=8.0, depth=6, location=(ex, ey, 8))
        apply_boolean_difference(body, cb)
        
    # Horizontal valve barrel along X axis at Y=0, Z=24: OD 44, length 90 mm (X: -45..45)
    barrel = create_cylinder(radius=22, depth=90, location=(0, 0, 24), rotation=(0, math.pi/2, 0), name="Barrel")
    apply_boolean_union(body, barrel)
    
    # Through bore Phi 24 through X
    b_bore = create_cylinder(radius=12, depth=100, location=(0, 0, 24), rotation=(0, math.pi/2, 0))
    apply_boolean_difference(body, b_bore)
    
    # Front tapped hole M20x1.5 (bore Phi 18.5 depth 20) at X=45
    t_hole = create_cylinder(radius=9.25, depth=22, location=(40, 0, 24), rotation=(0, math.pi/2, 0))
    apply_boolean_difference(body, t_hole)
    
    # Vertical upright tower at X=0, Y=12: OD 36, rising to Z=78
    tower = create_cylinder(radius=18, depth=54, location=(0, 12, 51), name="Tower")
    apply_boolean_union(body, tower)
    
    # Top teardrop tang extension on tower
    tang = create_box(size=(24, 16, 40), location=(0, 22, 58), name="Tang")
    apply_boolean_union(body, tang)
    
    # Top vertical threaded port: M20x1.5 (bore Phi 18.5, depth 25)
    v_bore = create_cylinder(radius=9.25, depth=35, location=(0, 12, 65))
    apply_boolean_difference(body, v_bore)
    
    # Intermediate fluid port connecting to base
    base_port = create_cylinder(radius=8.0, depth=18, location=(0, -25, 5))
    apply_boolean_difference(body, base_port)
    
    return body, "machined_steel"

# ==============================================================================
# 25. LJT06.25_箱体 (Gearbox Housing with Peanut Dual Bearing Flange)
# ==============================================================================
def generate_ljt06_25():
    # Base mounting flange: 145 x 125 x 14 mm
    body = create_box(size=(145, 125, 14), location=(0, 0, 7), name="LJT06_25_Base")
    
    # 4 corner bolt holes Phi 11 at (+-62.5, +-52.5)
    for sx in [-62.5, 62.5]:
        for sy in [-52.5, 52.5]:
            drill_hole(body, radius=5.5, depth=20, location=(sx, sy, 7))
            
    # Open-top gearbox body: 115 x 100 x 110 mm (Z: 14..124)
    box = create_box(size=(115, 100, 110), location=(0, 0, 69), name="BoxBody")
    apply_boolean_union(body, box)
    
    # Hollow interior cavity: 99 x 84 x 105 mm (wall thickness 8 mm)
    cavity = create_box(size=(99, 84, 108), location=(0, 0, 72), name="Cavity")
    apply_boolean_difference(body, cavity)
    
    # 6x M6 tapped holes on top rim
    top_holes = [(-50, -42), (-50, 42), (50, -42), (50, 42), (0, -42), (0, 42)]
    for tx, ty in top_holes:
        drill_hole(body, radius=2.5, depth=18, location=(tx, ty, 124))
        
    # Front dual bearing boss plate (peanut / figure-8 shape) on -Y face (Y=-50):
    # Lower bearing seat: OD 72 at Z=45
    boss_low = create_cylinder(radius=36, depth=10, location=(-15, -50, 45), rotation=(math.pi/2, 0, 0), name="BossLow")
    # Upper bearing seat: OD 54 at Z=90
    boss_up = create_cylinder(radius=27, depth=10, location=(-15, -50, 90), rotation=(math.pi/2, 0, 0), name="BossUp")
    apply_boolean_union(body, boss_low)
    apply_boolean_union(body, boss_up)
    
    # Lower bearing bore: Phi 52 through
    bore_low = create_cylinder(radius=26, depth=25, location=(-15, -50, 45), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, bore_low)
    
    # Upper bearing bore: Phi 35 through
    bore_up = create_cylinder(radius=17.5, depth=25, location=(-15, -50, 90), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, bore_up)
    
    # 3x M6 holes around lower bore, 3x M5 around upper bore
    for ang in [0, 2*math.pi/3, 4*math.pi/3]:
        lx = -15 + 31 * math.cos(ang)
        lz = 45 + 31 * math.sin(ang)
        lh = create_cylinder(radius=2.5, depth=16, location=(lx, -55, lz), rotation=(math.pi/2, 0, 0))
        apply_boolean_difference(body, lh)
        
        ux = -15 + 23 * math.cos(ang)
        uz = 90 + 23 * math.sin(ang)
        uh = create_cylinder(radius=2.1, depth=16, location=(ux, -55, uz), rotation=(math.pi/2, 0, 0))
        apply_boolean_difference(body, uh)
        
    # Right side bearing boss on +X face (X=57.5) at Z=65: OD 65, bore Phi 40
    r_boss = create_cylinder(radius=32.5, depth=10, location=(57.5, 0, 65), rotation=(0, math.pi/2, 0), name="RightBoss")
    apply_boolean_union(body, r_boss)
    r_bore = create_cylinder(radius=20, depth=25, location=(57.5, 0, 65), rotation=(0, math.pi/2, 0))
    apply_boolean_difference(body, r_bore)
    
    # Matching rear bearing bores on +Y face (Y=50)
    rb_low = create_cylinder(radius=26, depth=25, location=(-15, 50, 45), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, rb_low)
    rb_up = create_cylinder(radius=17.5, depth=25, location=(-15, 50, 90), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, rb_up)
    
    return body, "cast_iron"

# ==============================================================================
# 26. LJT06.26_箱体 (Tall Reducer Housing with 4 Corner Foot Pads)
# ==============================================================================
def generate_ljt06_26():
    # Main upright housing body: 100 x 90 x 150 mm (Z: 16..166)
    body = create_box(size=(100, 90, 150), location=(0, 0, 91), name="LJT06_26_Body")
    
    # 4 corner protruding foot pads: 40 x 40 x 16 mm at (+-60, +-55, 8)
    for sx in [-60, 60]:
        for sy in [-55, 55]:
            pad = create_box(size=(40, 40, 16), location=(sx, sy, 8), name="FootPad")
            apply_boolean_union(body, pad)
            drill_hole(body, radius=5.5, depth=25, location=(sx, sy, 8))
            cb = create_cylinder(radius=9.0, depth=6, location=(sx, sy, 13))
            apply_boolean_difference(body, cb)
            
    # Hollow interior cavity: 84 x 74 x 135 mm
    cavity = create_box(size=(84, 74, 135), location=(0, 0, 91), name="Cavity")
    apply_boolean_difference(body, cavity)
    
    # Front large circular multi-lugged opening on -Y face (Y=-45) at Z=85: OD 105, opening Phi 75
    f_ring = create_cylinder(radius=52.5, depth=10, location=(0, -45, 85), rotation=(math.pi/2, 0, 0), name="FrontRing")
    apply_boolean_union(body, f_ring)
    f_open = create_cylinder(radius=37.5, depth=25, location=(0, -45, 85), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, f_open)
    
    # 6 tapped lug holes on front ring (PCD 92)
    for i in range(6):
        ang = i * math.pi / 3
        hx = 46 * math.cos(ang)
        hz = 85 + 46 * math.sin(ang)
        fh = create_cylinder(radius=2.5, depth=16, location=(hx, -50, hz), rotation=(math.pi/2, 0, 0))
        apply_boolean_difference(body, fh)
        
    # Left flanged bearing seat on -X face (X=-50) at Z=50: OD 65, bore Phi 35
    l_boss = create_cylinder(radius=32.5, depth=10, location=(-50, 0, 50), rotation=(0, math.pi/2, 0), name="LeftBoss")
    apply_boolean_union(body, l_boss)
    l_bore = create_cylinder(radius=17.5, depth=25, location=(-50, 0, 50), rotation=(0, math.pi/2, 0))
    apply_boolean_difference(body, l_bore)
    
    # Right matching bearing seat on +X face (X=50) at Z=50
    r_boss = create_cylinder(radius=32.5, depth=10, location=(50, 0, 50), rotation=(0, math.pi/2, 0), name="RightBoss")
    apply_boolean_union(body, r_boss)
    r_bore = create_cylinder(radius=17.5, depth=25, location=(50, 0, 50), rotation=(0, math.pi/2, 0))
    apply_boolean_difference(body, r_bore)
    
    # Top oil cap boss at Z=166: OD 26, height 8 with M14 hole
    top_boss = create_cylinder(radius=13, depth=8, location=(0, 0, 166), name="TopBoss")
    apply_boolean_union(body, top_boss)
    top_hole = create_cylinder(radius=6.0, depth=18, location=(0, 0, 166))
    apply_boolean_difference(body, top_hole)
    
    return body, "cast_iron"

# ==============================================================================
# 27. LJT06.27_泵体 (Pump Body with Bracket and Dual Bottom Ports)
# ==============================================================================
def generate_ljt06_27():
    # Back vertical mounting bracket plate: 110 x 12 x 95 mm at Y=-15 (Z: 40..135)
    body = create_box(size=(110, 12, 95), location=(0, -15, 87.5), name="LJT06_27_Bracket")
    
    # Top semicircular cutout in bracket: R25 at (0, -15, 135)
    cutout = create_cylinder(radius=25, depth=20, location=(0, -15, 135), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, cutout)
    
    # 4 mounting holes Phi 9 on bracket: (+-38, -15, 115) and (+-25, -15, 65)
    for bx, bz in [(-38, 115), (38, 115), (-25, 65), (25, 65)]:
        drill_hole(body, radius=4.5, depth=20, location=(bx, -15, bz), rotation=(math.pi/2, 0, 0))
        
    # Central circular pump chamber along Y axis: OD 78, length 55 mm (Y: -15..40) at Z=65
    chamber = create_cylinder(radius=39, depth=55, location=(0, 12.5, 65), rotation=(math.pi/2, 0, 0), name="PumpChamber")
    apply_boolean_union(body, chamber)
    
    # Internal pump cavity bore: Phi 56, depth 40 (from Y=40 down to 0)
    c_bore = create_cylinder(radius=28, depth=42, location=(0, 20, 65), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, c_bore)
    
    # 4 tapped mounting ears on front face of chamber (4x M6 on PCD 68)
    for i in range(4):
        ang = i * math.pi / 2 + math.pi / 4
        hx = 34 * math.cos(ang)
        hz = 65 + 34 * math.sin(ang)
        ch = create_cylinder(radius=2.5, depth=18, location=(hx, 40, hz), rotation=(math.pi/2, 0, 0))
        apply_boolean_difference(body, ch)
        
    # Two lower lateral port bosses angled below chamber at Z=20:
    # Left port boss: center at (-38, 15, 20), OD 36, length 40, axis along Y
    l_port = create_cylinder(radius=18, depth=40, location=(-38, 15, 20), rotation=(math.pi/2, 0, 0), name="LeftPort")
    apply_boolean_union(body, l_port)
    l_bore = create_cylinder(radius=10.5, depth=50, location=(-38, 15, 20), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, l_bore)
    
    # Right port boss: center at (38, 15, 20), OD 36, length 40, axis along Y
    r_port = create_cylinder(radius=18, depth=40, location=(38, 15, 20), rotation=(math.pi/2, 0, 0), name="RightPort")
    apply_boolean_union(body, r_port)
    r_bore = create_cylinder(radius=10.5, depth=50, location=(38, 15, 20), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, r_bore)
    
    # Bridging gusset ribs connecting lower ports to chamber
    rib_l = create_box(size=(14, 35, 35), location=(-22, 12.5, 42), name="RibL")
    apply_boolean_union(body, rib_l)
    rib_r = create_box(size=(14, 35, 35), location=(22, 12.5, 42), name="RibR")
    apply_boolean_union(body, rib_r)
    
    return body, "cast_iron"

# ==============================================================================
# 28. LJT06.28_泵体 (Flanged Hydraulic Gear Pump Body)
# ==============================================================================
def generate_ljt06_28():
    # Rear circular mounting flange: OD 150, thickness 14 mm at Y=0 (Y: -14..0)
    body = create_cylinder(radius=75, depth=14, location=(0, -7, 0), rotation=(math.pi/2, 0, 0), name="LJT06_28_Base")
    
    # 4 mounting holes Phi 11 on PCD 128
    for i in range(4):
        ang = i * math.pi / 2 + math.pi / 4
        hx = 64 * math.cos(ang)
        hz = 64 * math.sin(ang)
        drill_hole(body, radius=5.5, depth=20, location=(hx, -7, hz), rotation=(math.pi/2, 0, 0))
        
    # Central pilot spigot on rear face (Y=-14): OD 95 x 4 mm
    spigot = create_cylinder(radius=47.5, depth=4, location=(0, -16, 0), rotation=(math.pi/2, 0, 0), name="Spigot")
    apply_boolean_union(body, spigot)
    
    # Main forward gear pump body block (stadium / oval): 70 x 65 x 105 mm (X: -35..35, Y: 0..65, Z: -52.5..52.5)
    stadium_body = create_box(size=(70, 65, 105), location=(0, 32.5, 0), name="StadiumBody")
    apply_boolean_union(body, stadium_body)
    
    # Figure-8 gear cavity: two overlapping bores R24 (Phi 48), center distance 36 along Z (centers at Z=+-18), depth 40 from Y=65 down to 25
    cav1 = create_cylinder(radius=24, depth=42, location=(0, 45, 18), rotation=(math.pi/2, 0, 0), name="CavityTop")
    apply_boolean_difference(body, cav1)
    cav2 = create_cylinder(radius=24, depth=42, location=(0, 45, -18), rotation=(math.pi/2, 0, 0), name="CavityBot")
    apply_boolean_difference(body, cav2)
    
    # 6x M6 tapped holes on front face Y=65 around figure-8
    f_holes = [(-26, 65, 38), (26, 65, 38), (-26, 65, -38), (26, 65, -38), (-30, 65, 0), (30, 65, 0)]
    for fx, fy, fz in f_holes:
        fh = create_cylinder(radius=2.5, depth=18, location=(fx, fy, fz), rotation=(math.pi/2, 0, 0))
        apply_boolean_difference(body, fh)
        
    # Dual shaft through-bores: Phi 18 through to rear at Z=+-18
    shaft_t = create_cylinder(radius=9, depth=85, location=(0, 10, 18), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, shaft_t)
    shaft_b = create_cylinder(radius=9, depth=85, location=(0, 10, -18), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, shaft_b)
    
    # Left and right side port flanges: 2-bolt diamond flanges on +-X faces at X=+-35
    for sx in [-35, 35]:
        p_flange = create_box(size=(10, 38, 54), location=(sx, 32.5, 0), name="PortFlange")
        apply_boolean_union(body, p_flange)
        # Port bore Phi 18
        p_bore = create_cylinder(radius=9, depth=35, location=(sx, 32.5, 0), rotation=(0, math.pi/2, 0))
        apply_boolean_difference(body, p_bore)
        # 2x M6 tapped holes
        for pz in [-20, 20]:
            ph = create_cylinder(radius=2.5, depth=18, location=(sx, 32.5, pz), rotation=(0, math.pi/2, 0))
            apply_boolean_difference(body, ph)
            
    return body, "cast_iron"

# ==============================================================================
# 29. LJT06.29_阀体 (Valve Body with Front Square Flange & Threaded Branch)
# ==============================================================================
def generate_ljt06_29():
    # Base mounting foot plate: 115 x 85 x 12 mm
    body = create_box(size=(115, 85, 12), location=(0, 0, 6), name="LJT06_29_Base")
    
    # 4 corner bolt holes Phi 9 at (+-45, +-32)
    for sx in [-45, 45]:
        for sy in [-32, 32]:
            drill_hole(body, radius=4.5, depth=20, location=(sx, sy, 6))
            
    # Upper horizontal barrel along Y axis at X=0, Z=75: OD 74, length 110 mm (Y: -55..55)
    barrel = create_cylinder(radius=37, depth=110, location=(0, 0, 75), rotation=(math.pi/2, 0, 0), name="UpperBarrel")
    apply_boolean_union(body, barrel)
    
    # Front square 4-bolt flange at Y=-55: 75 x 14 x 75 mm
    sq_flange = create_box(size=(75, 14, 75), location=(0, -55, 75), name="SqFlange")
    apply_boolean_union(body, sq_flange)
    
    # Upper barrel central bore Phi 45 through
    u_bore = create_cylinder(radius=22.5, depth=125, location=(0, 0, 75), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, u_bore)
    
    # 4x Phi 9 holes on square flange at (+-26, -55, 75 +- 26)
    for fx in [-26, 26]:
        for fz in [49, 101]:
            fh = create_cylinder(radius=4.5, depth=20, location=(fx, -55, fz), rotation=(math.pi/2, 0, 0))
            apply_boolean_difference(body, fh)
            
    # Lower offset pipe branch along Y axis at X=28, Z=30: OD 44, length 120 mm extending to Y=-65
    l_pipe = create_cylinder(radius=22, depth=120, location=(28, -5, 30), rotation=(math.pi/2, 0, 0), name="LowerPipe")
    apply_boolean_union(body, l_pipe)
    
    # External thread boss on front of lower branch (Y=-65): M36x2 (OD 36, length 25)
    th_boss = create_cylinder(radius=18, depth=25, location=(28, -65, 30), rotation=(math.pi/2, 0, 0), name="ThreadBoss")
    apply_boolean_union(body, th_boss)
    
    # Lower branch through bore Phi 24
    l_bore = create_cylinder(radius=12, depth=140, location=(28, -5, 30), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, l_bore)
    
    # Upright cast web connecting upper barrel, lower branch, and base: thickness 14 mm
    web = create_box(size=(14, 90, 65), location=(0, 0, 42.5), name="Web")
    apply_boolean_union(body, web)
    
    # Internal communication port between upper barrel and lower pipe
    comm_bore = create_cylinder(radius=12, depth=50, location=(14, 0, 52.5), rotation=(0, math.pi/4, 0))
    apply_boolean_difference(body, comm_bore)
    
    return body, "cast_iron"

# ==============================================================================
# 30. LJT06.30_阀体 (High-Pressure Valve Body with Bottom Lug & Diamond Flange)
# ==============================================================================
def generate_ljt06_30():
    # Main horizontal valve barrel along Y axis at X=0, Z=45: length 120 mm (Y: -60..60)
    # Rear portion: OD 50 (Y: -20..60)
    barrel_main = create_cylinder(radius=25, depth=80, location=(0, 20, 45), rotation=(math.pi/2, 0, 0), name="LJT06_30_Body")
    # Front stepped nozzle: OD 36 (Y: -60..-20)
    barrel_nozzle = create_cylinder(radius=18, depth=40, location=(0, -40, 45), rotation=(math.pi/2, 0, 0), name="Nozzle")
    apply_boolean_union(barrel_main, barrel_nozzle)
    
    # Through bore Phi 24 through Y axis
    b_bore = create_cylinder(radius=12, depth=130, location=(0, 0, 45), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(barrel_main, b_bore)
    
    # Rear 2-bolt diamond flange at Y=60: 88 x 14 x 48 mm
    d_flange = create_box(size=(88, 14, 48), location=(0, 60, 45), name="DiamondFlange")
    apply_boolean_union(barrel_main, d_flange)
    
    # 2 oval/clearance holes on diamond flange at (+-34, 60, 45): Phi 11
    for sx in [-34, 34]:
        dh = create_cylinder(radius=5.5, depth=20, location=(sx, 60, 45), rotation=(math.pi/2, 0, 0))
        apply_boolean_difference(barrel_main, dh)
        
    # Top port bosses along Z axis:
    # 1. Front smaller boss at Y=-15, Z=45: OD 24, height 18 (Z: 45..63), internal thread M12x1.25 (bore Phi 10.5)
    boss_f = create_cylinder(radius=12, depth=18, location=(0, -15, 54), name="BossFront")
    apply_boolean_union(barrel_main, boss_f)
    bore_bf = create_cylinder(radius=5.25, depth=25, location=(0, -15, 54))
    apply_boolean_difference(barrel_main, bore_bf)
    
    # 2. Rear larger boss at Y=28, Z=45: OD 38 with side flats, height 22 (Z: 45..67), thread M22x1.5 (bore Phi 20)
    boss_r = create_cylinder(radius=19, depth=22, location=(0, 28, 56), name="BossRear")
    apply_boolean_union(barrel_main, boss_r)
    bore_br = create_cylinder(radius=10, depth=30, location=(0, 28, 56))
    apply_boolean_difference(barrel_main, bore_br)
    
    # Bottom mounting lug: 36 x 45 x 30 mm (X: -18..18, Y: 5..50, Z: 15..45)
    bot_lug = create_box(size=(36, 45, 30), location=(0, 27.5, 30), name="BotLug")
    apply_boolean_union(barrel_main, bot_lug)
    
    # Transverse mounting pin hole Phi 16 through X axis at (0, 27.5, 25)
    lug_hole = create_cylinder(radius=8.0, depth=45, location=(0, 27.5, 25), rotation=(0, math.pi/2, 0))
    apply_boolean_difference(barrel_main, lug_hole)
    
    return barrel_main, "machined_steel"

# ==============================================================================
# BATCH GENERATOR LIST & RUNNER
# ==============================================================================

GENERATORS = [
    ("LJT06.16_液压缸", generate_ljt06_16),
    ("LJT06.17_阀体", generate_ljt06_17),
    ("LJT06.18_阀体", generate_ljt06_18),
    ("LJT06.19_箱体", generate_ljt06_19),
    ("LJT06.20_蜗轮壳", generate_ljt06_20),
    ("LJT06.21_阀体", generate_ljt06_21),
    ("LJT06.22_箱体", generate_ljt06_22),
    ("LJT06.23_阀体", generate_ljt06_23),
    ("LJT06.24_喷雾器壳体", generate_ljt06_24),
    ("LJT06.25_箱体", generate_ljt06_25),
    ("LJT06.26_箱体", generate_ljt06_26),
    ("LJT06.27_泵体", generate_ljt06_27),
    ("LJT06.28_泵体", generate_ljt06_28),
    ("LJT06.29_阀体", generate_ljt06_29),
    ("LJT06.30_阀体", generate_ljt06_30),
]

def run_batch():
    print(f"\n{'='*70}")
    print(f"STARTING CATEGORY 06 BATCH 2 GENERATION (15 PARTS: LJT06.16 ~ LJT06.30)")
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
