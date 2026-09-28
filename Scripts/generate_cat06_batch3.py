"""
Category 06 Batch 3: 箱壳类零件 (Housings & Casings - Part 3 - FINAL BATCH)
Generates the final 15 models for Category 06 (and entire 194-part atlas):
  LJT06.31_尾座,   LJT06.32_机油泵体, LJT06.33_阀体,   LJT06.34_箱体,
  LJT06.35_箱体,   LJT06.36_底座,     LJT06.37_泵体,   LJT06.38_泵体,
  LJT06.39_箱体,   LJT06.40_箱体,     LJT06.41_箱体,   LJT06.42_箱体,
  LJT06.43_壳体,   LJT06.44_壳体,     LJT06.45_箱体
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
# 31. LJT06.31_尾座 (Lathe/Grinder Tailstock Body)
# ==============================================================================
def generate_ljt06_31():
    # Solid tailstock body block: 160 x 65 x 95 mm (X: -80..80, Y: -32.5..32.5, Z: 0..95)
    body = create_box(size=(160, 65, 95), location=(0, 0, 47.5), name="LJT06_31_Body")
    
    # Rear angled slope cut on right top corner: X > 55, Z > 60
    cutter_slope = create_box(size=(60, 75, 60), location=(75, 0, 85), rotation=(0, -math.pi/6, 0), name="SlopeCutter")
    apply_boolean_difference(body, cutter_slope)
    
    # Front quill bore along X axis at Y=0, Z=65: through bore Phi 32
    quill_bore = create_cylinder(radius=16, depth=170, location=(0, 0, 65), rotation=(0, math.pi/2, 0))
    apply_boolean_difference(body, quill_bore)
    
    # Front counterbore Phi 38 depth 25 at X=-80
    quill_cbore = create_cylinder(radius=19, depth=26, location=(-70, 0, 65), rotation=(0, math.pi/2, 0))
    apply_boolean_difference(body, quill_cbore)
    
    # Lower clamping hole on front face at X=-80, Z=30: M16 (bore Phi 14 depth 35)
    clamp_hole = create_cylinder(radius=7.0, depth=35, location=(-65, 0, 30), rotation=(0, math.pi/2, 0))
    apply_boolean_difference(body, clamp_hole)
    
    # Front key tab projection: 12 x 10 x 14 mm at X=-80, Z=18
    key_tab = create_box(size=(6, 12, 14), location=(-81, 0, 18), name="KeyTab")
    apply_boolean_union(body, key_tab)
    
    # Transverse clamping kidney/cam slot through Y axis at X=15, Z=40: width 24, height 38
    kidney = create_box(size=(24, 75, 38), location=(15, 0, 40), name="KidneySlot")
    apply_boolean_difference(body, kidney)
    
    # Rear transverse clamping hole through Y axis at X=60, Z=60: Phi 14
    r_hole = create_cylinder(radius=7.0, depth=75, location=(60, 0, 60), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, r_hole)
    
    # Top oil lubrication cup hole on top face at X=20, Z=95: Phi 6, countersink Phi 12
    oil_hole = create_cylinder(radius=3.0, depth=25, location=(20, 0, 88))
    apply_boolean_difference(body, oil_hole)
    oil_cs = create_cylinder(radius=6.0, depth=5, location=(20, 0, 93))
    apply_boolean_difference(body, oil_cs)
    
    return body, "cast_iron"

# ==============================================================================
# 32. LJT06.32_机油泵体 (Engine Oil Pump Body with Base Bracket)
# ==============================================================================
def generate_ljt06_32():
    # Triangular 3-hole base mounting bracket: thickness 12 mm (Z: 0..12)
    body = create_box(size=(110, 100, 12), location=(-10, -10, 6), name="LJT06_32_Base")
    
    # 3 mounting ears at corners: (-50, -45), (45, -45), (-25, 45)
    for ex, ey in [(-50, -45), (45, -45), (-25, 45)]:
        ear = create_cylinder(radius=16, depth=12, location=(ex, ey, 6))
        apply_boolean_union(body, ear)
        drill_hole(body, radius=5.5, depth=20, location=(ex, ey, 6))
        cb = create_cylinder(radius=9.0, depth=6, location=(ex, ey, 9))
        apply_boolean_difference(body, cb)
        
    # Upper pump cavity body: rounded rectangular block 88 x 54 x 55 mm (Z: 30..85) at (0, 0, 57.5)
    pump_body = create_box(size=(88, 54, 55), location=(0, 0, 57.5), name="PumpBody")
    apply_boolean_union(body, pump_body)
    
    # Hollow cavity: 72 x 38 x 48 mm (depth 45 from Z=85 down to 37)
    cavity = create_box(size=(72, 38, 48), location=(0, 0, 62), name="Cavity")
    apply_boolean_difference(body, cavity)
    
    # 4 corner tapped holes M6 on top face (Z=85)
    for tx in [-38, 38]:
        for ty in [-21, 21]:
            th = create_cylinder(radius=2.5, depth=18, location=(tx, ty, 85))
            apply_boolean_difference(body, th)
            
    # Triangular stiffening gusset connecting base to pump body
    gusset = create_box(size=(8, 45, 35), location=(-30, -15, 30), name="Gusset")
    apply_boolean_union(body, gusset)
    
    # Internal oil port threaded hole M18x1.5 through back wall at Y=27, Z=55
    oil_port = create_cylinder(radius=8.5, depth=20, location=(15, 25, 55), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, oil_port)
    
    # Drive shaft bore Phi 20 through floor of cavity down to base at Z=30
    shaft_bore = create_cylinder(radius=10, depth=45, location=(-15, 0, 25))
    apply_boolean_difference(body, shaft_bore)
    
    return body, "cast_iron"

# ==============================================================================
# 33. LJT06.33_阀体 (Valve Body with 45-deg Slotted Diamond Flange)
# ==============================================================================
def generate_ljt06_33():
    # Base mounting feet: 2 side feet at X=+-45, thickness 14 mm (Z: 0..14)
    body = create_box(size=(120, 70, 14), location=(0, 0, 7), name="LJT06_33_Base")
    
    # Central U-slot cut in base: width 40, height 20
    u_cut = create_box(size=(40, 80, 20), location=(0, 0, 7), name="BaseCut")
    apply_boolean_difference(body, u_cut)
    
    # 4 mounting holes Phi 11 on feet: (+-45, +-22)
    for sx in [-45, 45]:
        for sy in [-22, 22]:
            drill_hole(body, radius=5.5, depth=20, location=(sx, sy, 7))
            
    # Lower central body: 50 x 50 x 35 mm (Z: 14..49)
    low_body = create_box(size=(50, 50, 35), location=(0, 0, 31.5), name="LowBody")
    apply_boolean_union(body, low_body)
    
    # Lower horizontal bore Phi 28 through Y at Z=25
    low_bore = create_cylinder(radius=14, depth=60, location=(0, 0, 25), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, low_bore)
    
    # 2 tapped face holes M5 on front face of lower body
    for fx in [-18, 18]:
        fh = create_cylinder(radius=2.1, depth=15, location=(fx, -25, 25), rotation=(math.pi/2, 0, 0))
        apply_boolean_difference(body, fh)
        
    # Upper housing: 55 x 50 x 55 mm (Z: 49..104)
    up_body = create_box(size=(55, 50, 55), location=(0, 0, 76.5), name="UpBody")
    apply_boolean_union(body, up_body)
    
    # Open front rectangular window on -Y face: 42 x 25 x 38 mm
    window = create_box(size=(42, 25, 38), location=(0, -18, 76.5), name="Window")
    apply_boolean_difference(body, window)
    
    # 4 corner tapped holes M4 around window
    for wx in [-23, 23]:
        for wz in [60, 92]:
            wh = create_cylinder(radius=1.65, depth=14, location=(wx, -25, wz), rotation=(math.pi/2, 0, 0))
            apply_boolean_difference(body, wh)
            
    # Side angled diamond flange on +X face at X=27.5, Z=70: angled at 45 deg, length 75, width 42, thickness 10
    d_flange = create_box(size=(10, 75, 42), location=(30, 0, 70), rotation=(math.pi/4, 0, 0), name="DFlange")
    apply_boolean_union(body, d_flange)
    
    # Central bore Phi 22 through side flange
    s_bore = create_cylinder(radius=11, depth=35, location=(30, 0, 70), rotation=(0, math.pi/2, 0))
    apply_boolean_difference(body, s_bore)
    
    # 2 peripheral bolt slots on diamond flange tips
    for offset in [-30, 30]:
        slot = create_cylinder(radius=5.5, depth=20, location=(30, offset * math.cos(math.pi/4), 70 + offset * math.sin(math.pi/4)), rotation=(0, math.pi/2, 0))
        apply_boolean_difference(body, slot)
        
    return body, "cast_iron"

# ==============================================================================
# 34. LJT06.34_箱体 (Cantilever U-Trough Gearbox Housing)
# ==============================================================================
def generate_ljt06_34():
    # Back mounting flange: vertical plate 130 x 14 x 140 mm at Y=-65 (Z: 0..140)
    body = create_box(size=(130, 14, 140), location=(0, -65, 70), name="LJT06_34_Base")
    
    # 4 corner mounting holes Phi 11 at (+-52, -65, 70 +- 55)
    for fx in [-52, 52]:
        for fz in [15, 125]:
            drill_hole(body, radius=5.5, depth=25, location=(fx, -65, fz), rotation=(math.pi/2, 0, 0))
            
    # 2 dowel pin holes Phi 6 at (+-52, -65, 70)
    drill_hole(body, radius=3.0, depth=25, location=(-52, -65, 70), rotation=(math.pi/2, 0, 0))
    drill_hole(body, radius=3.0, depth=25, location=(52, -65, 70), rotation=(math.pi/2, 0, 0))
    
    # Forward cantilever U-trough box extending from Y=-65 to 45 (length 110 mm):
    # Width 90 (X: -45..45), top flat at Z=100, bottom trough to Z=15
    trough = create_box(size=(90, 110, 85), location=(0, -10, 57.5), name="Trough")
    apply_boolean_union(body, trough)
    
    # Internal hollow cavity: width 74, open front and semicircular trough bottom
    cavity = create_box(size=(74, 115, 75), location=(0, -5, 62.5), name="Cavity")
    apply_boolean_difference(body, cavity)
    
    # Top port boss on top face at Z=100: counterbore Phi 40 depth 6, central bore Phi 22
    top_cb = create_cylinder(radius=20, depth=8, location=(0, -10, 97))
    apply_boolean_difference(body, top_cb)
    top_bore = create_cylinder(radius=11, depth=35, location=(0, -10, 85))
    apply_boolean_difference(body, top_bore)
    
    # 3x M5 tapped holes on PCD 32 around top port
    for i in range(3):
        ang = i * 2 * math.pi / 3
        tx = 16 * math.cos(ang)
        ty = -10 + 16 * math.sin(ang)
        drill_hole(body, radius=2.1, depth=15, location=(tx, ty, 100))
        
    # Opposed side bearing seats on +-X walls (X=+-45) at Y=0, Z=55: OD 72, bore Phi 42
    for sx in [-45, 45]:
        boss = create_cylinder(radius=36, depth=8, location=(sx, 0, 55), rotation=(0, math.pi/2, 0), name="SideBoss")
        apply_boolean_union(body, boss)
        bore = create_cylinder(radius=21, depth=25, location=(sx, 0, 55), rotation=(0, math.pi/2, 0))
        apply_boolean_difference(body, bore)
        # 4x M5 tapped holes
        for ang in [math.pi/4, 3*math.pi/4, 5*math.pi/4, 7*math.pi/4]:
            by = 28 * math.cos(ang)
            bz = 55 + 28 * math.sin(ang)
            bh = create_cylinder(radius=2.1, depth=16, location=(sx, by, bz), rotation=(0, math.pi/2, 0))
            apply_boolean_difference(body, bh)
            
    return body, "cast_iron"

# ==============================================================================
# 35. LJT06.35_箱体 (Multi-Flanged Three-Way Housing)
# ==============================================================================
def generate_ljt06_35():
    # Bottom 2-bolt diamond flange: 75 x 40 x 10 mm at Z=5
    body = create_box(size=(75, 40, 10), location=(0, 0, 5), name="LJT06_35_Base")
    
    # 2 mounting holes Phi 9 at (+-27.5, 0, 5)
    drill_hole(body, radius=4.5, depth=18, location=(-27.5, 0, 5))
    drill_hole(body, radius=4.5, depth=18, location=(27.5, 0, 5))
    
    # Conical neck rising to Z=40: OD 40 at base tapering to OD 32
    neck = create_cylinder(radius=18, depth=30, location=(0, 0, 25), name="Neck")
    apply_boolean_union(body, neck)
    
    # Central junction body block: 48 x 44 x 55 mm (Z: 40..95)
    block = create_box(size=(48, 44, 55), location=(0, 0, 67.5), name="JunctionBlock")
    apply_boolean_union(body, block)
    
    # Top port: counterbore Phi 32 depth 10, internal thread M20x1.5 (bore Phi 18.5 depth 30)
    top_cb = create_cylinder(radius=16, depth=12, location=(0, 0, 90))
    apply_boolean_difference(body, top_cb)
    top_bore = create_cylinder(radius=9.25, depth=40, location=(0, 0, 75))
    apply_boolean_difference(body, top_bore)
    
    # Right horizontal pipe branch along +X at Z=70: OD 45, length 30 extending to X=45
    r_pipe = create_cylinder(radius=22.5, depth=30, location=(30, 0, 70), rotation=(0, math.pi/2, 0), name="RightPipe")
    apply_boolean_union(body, r_pipe)
    r_bore = create_cylinder(radius=12.5, depth=45, location=(30, 0, 70), rotation=(0, math.pi/2, 0))
    apply_boolean_difference(body, r_bore)
    
    # Back circular flange on -Y face at Y=-35, Z=70: OD 70, thickness 10 mm
    b_flange = create_cylinder(radius=35, depth=10, location=(0, -35, 70), rotation=(math.pi/2, 0, 0), name="BackFlange")
    apply_boolean_union(body, b_flange)
    b_bore = create_cylinder(radius=12, depth=45, location=(0, -25, 70), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, b_bore)
    
    # 4x Phi 9 holes on PCD 54 on back flange
    for i in range(4):
        ang = i * math.pi / 2
        bx = 27 * math.cos(ang)
        bz = 70 + 27 * math.sin(ang)
        bh = create_cylinder(radius=4.5, depth=18, location=(bx, -35, bz), rotation=(math.pi/2, 0, 0))
        apply_boolean_difference(body, bh)
        
    return body, "cast_iron"

# ==============================================================================
# 36. LJT06.36_底座 (Heavy Machine Base with Spindle Register)
# ==============================================================================
def generate_ljt06_36():
    # Top rectangular mounting plate: 120 x 95 x 12 mm at Z=134 (Z: 128..140)
    body = create_box(size=(120, 95, 12), location=(0, 0, 134), name="LJT06_36_TopPlate")
    
    # 4 corner holes Phi 9 on top plate at (+-48, +-36)
    for tx in [-48, 48]:
        for ty in [-36, 36]:
            drill_hole(body, radius=4.5, depth=20, location=(tx, ty, 134))
            
    # Central raised circular register on top face: OD 65, height 8 (Z: 140..148)
    reg = create_cylinder(radius=32.5, depth=8, location=(0, 0, 144), name="Register")
    apply_boolean_union(body, reg)
    
    # Central through bore Phi 32 through Z
    reg_bore = create_cylinder(radius=16, depth=35, location=(0, 0, 135))
    apply_boolean_difference(body, reg_bore)
    
    # 4x M5 tapped holes on PCD 50 on register
    for i in range(4):
        ang = i * math.pi / 2
        rx = 25 * math.cos(ang)
        ry = 25 * math.sin(ang)
        drill_hole(body, radius=2.1, depth=16, location=(rx, ry, 144))
        
    # Main vertical stadium body from Z=10 to 128: width 75 (X: -37.5..37.5), depth 65 (Y: -32.5..32.5)
    v_body = create_box(size=(75, 65, 118), location=(0, 0, 69), name="VBody")
    apply_boolean_union(body, v_body)
    
    # Rounded bottom arch
    bot_arch = create_cylinder(radius=37.5, depth=65, location=(0, 0, 37.5), rotation=(math.pi/2, 0, 0), name="BotArch")
    apply_boolean_union(body, bot_arch)
    
    # Open front stadium slot cavity on -Y face: 42 x 50 x 85 mm (Z: 25..110)
    slot_cav = create_box(size=(42, 50, 85), location=(0, -15, 67.5), name="SlotCavity")
    apply_boolean_difference(body, slot_cav)
    
    # Bottom through bore Phi 30 through Y at Z=35
    b_bore = create_cylinder(radius=15, depth=75, location=(0, 0, 35), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, b_bore)
    
    # Two side mounting wings on +-X at X=+-50: 25 x 50 x 70 mm (Z: 40..110)
    for sx in [-50, 50]:
        wing = create_box(size=(25, 50, 70), location=(sx, 0, 75), name="SideWing")
        apply_boolean_union(body, wing)
        # 2 vertical tapped holes M10 on each wing at Y=0, Z=55 and Z=95
        for wz in [55, 95]:
            wh = create_cylinder(radius=4.25, depth=35, location=(sx, 0, wz), rotation=(0, math.pi/2, 0))
            apply_boolean_difference(body, wh)
            
    return body, "cast_iron"

# ==============================================================================
# 37. LJT06.37_泵体 (Pump Valve Body / Cap)
# ==============================================================================
def generate_ljt06_37():
    # Square outer block: 80 x 80 x 55 mm (X: -40..40, Y: -40..40, Z: 0..55)
    body = create_box(size=(80, 80, 55), location=(0, 0, 27.5), name="LJT06_37_Body")
    
    # Front raised conical/circular boss on -Y face (Y=-40): OD 70 tapering to 62, depth 12
    boss = create_cylinder(radius=33, depth=12, location=(0, -46, 27.5), rotation=(math.pi/2, 0, 0), name="FrontBoss")
    apply_boolean_union(body, boss)
    
    # 4 corner counterbored through-holes at (+-28, +-28) in X-Z plane: hole Phi 9, cbore Phi 15 depth 8
    for sx in [-28, 28]:
        for sz in [12, 43]:
            drill_hole(body, radius=4.5, depth=80, location=(sx, 0, sz), rotation=(math.pi/2, 0, 0))
            cb = create_cylinder(radius=7.5, depth=12, location=(sx, -45, sz), rotation=(math.pi/2, 0, 0))
            apply_boolean_difference(body, cb)
            
    # Rear internal stepped pump cavity on +Y face (Y=40): bore Phi 56 depth 25
    cav = create_cylinder(radius=28, depth=26, location=(0, 28, 27.5), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, cav)
    
    # Internal stepped bore Phi 36 depth 15
    cav_inner = create_cylinder(radius=18, depth=20, location=(0, 10, 27.5), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, cav_inner)
    
    return body, "machined_steel"

# ==============================================================================
# 38. LJT06.38_泵体 (Pump Body with Top Octagonal Port)
# ==============================================================================
def generate_ljt06_38():
    # Front square flange: 85 x 14 x 85 mm at Y=-25 (Z: 0..85, X: -42.5..42.5)
    body = create_box(size=(85, 14, 85), location=(0, -25, 42.5), name="LJT06_38_Flange")
    
    # 4 corner tapped holes M8 at (+-32, -25, 42.5 +- 32)
    for fx in [-32, 32]:
        for fz in [10.5, 74.5]:
            drill_hole(body, radius=3.4, depth=20, location=(fx, -25, fz), rotation=(math.pi/2, 0, 0))
            
    # Stepped rear body extending backwards: 70 x 50 x 70 mm (Y: -18..32)
    r_body = create_box(size=(70, 50, 70), location=(0, 7, 42.5), name="RearBody")
    apply_boolean_union(body, r_body)
    
    # Central stepped internal chamber: bore Phi 58 depth 15 from Y=-25
    c_bore1 = create_cylinder(radius=29, depth=16, location=(0, -20, 42.5), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, c_bore1)
    
    # Stepped bore Phi 42 depth 25
    c_bore2 = create_cylinder(radius=21, depth=26, location=(0, 0, 42.5), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, c_bore2)
    
    # Central shaft bore Phi 24 through to Y=32
    shaft_bore = create_cylinder(radius=12, depth=35, location=(0, 20, 42.5), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, shaft_bore)
    
    # Top octagonal port boss at Z=85: width across flats 46 mm, height 22 (Z: 85..107)
    oct_boss = create_cylinder(radius=25, depth=22, location=(0, 5, 96), vertices=8, name="OctBoss")
    apply_boolean_union(body, oct_boss)
    
    # Top threaded port: internal thread M20x1.5 (bore Phi 18.5, depth 35 into chamber)
    top_port = create_cylinder(radius=9.25, depth=45, location=(0, 5, 85))
    apply_boolean_difference(body, top_port)
    
    return body, "cast_iron"

# ==============================================================================
# 39. LJT06.39_箱体 (Right-Angle Drive Gearbox Casing)
# ==============================================================================
def generate_ljt06_39():
    # Front large square mounting flange: 120 x 14 x 120 mm at Y=-45 (X: -60..60, Z: -60..60)
    body = create_box(size=(120, 14, 120), location=(0, -45, 0), name="LJT06_39_Flange")
    
    # 8 perimeter bolt holes Phi 9 on square flange
    p_holes = [(-48, -48), (-48, 48), (48, -48), (48, 48), (-48, 0), (48, 0), (0, -48), (0, 48)]
    for hx, hz in p_holes:
        drill_hole(body, radius=4.5, depth=25, location=(hx, -45, hz), rotation=(math.pi/2, 0, 0))
        
    # Main housing box extending from Y=-45 to 45 (length 90 mm): 95 x 90 x 95 mm
    box = create_box(size=(95, 90, 95), location=(0, 0, 0), name="MainBox")
    apply_boolean_union(body, box)
    
    # Open internal gear cavity: 80 x 90 x 80 mm from front face
    cavity = create_box(size=(80, 85, 80), location=(0, -5, 0), name="Cavity")
    apply_boolean_difference(body, cavity)
    
    # Right cylindrical bearing neck along +X at Z=0: OD 65, length 30 extending to X=65
    r_neck = create_cylinder(radius=32.5, depth=30, location=(50, 0, 0), rotation=(0, math.pi/2, 0), name="RightNeck")
    apply_boolean_union(body, r_neck)
    
    # Right bearing bore Phi 40 through X
    r_bore = create_cylinder(radius=20, depth=45, location=(50, 0, 0), rotation=(0, math.pi/2, 0))
    apply_boolean_difference(body, r_bore)
    
    # 4x M6 tapped holes on right neck face
    for ang in [math.pi/4, 3*math.pi/4, 5*math.pi/4, 7*math.pi/4]:
        ry = 24 * math.cos(ang)
        rz = 24 * math.sin(ang)
        rh = create_cylinder(radius=2.5, depth=18, location=(65, ry, rz), rotation=(0, math.pi/2, 0))
        apply_boolean_difference(body, rh)
        
    # Rear bearing seat on back wall at Y=45: bore Phi 45 depth 20
    b_bore = create_cylinder(radius=22.5, depth=25, location=(0, 40, 0), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, b_bore)
    
    # Angled inspection cover boss on upper rear corner at 45 deg: 45 x 20 x 45 mm
    ang_boss = create_box(size=(45, 20, 45), location=(0, 38, 38), rotation=(math.pi/4, 0, 0), name="AngledBoss")
    apply_boolean_union(body, ang_boss)
    
    return body, "cast_iron"

# ==============================================================================
# 40. LJT06.40_箱体 (Flanged Pump / Actuator Housing)
# ==============================================================================
def generate_ljt06_40():
    # Base mounting plate: 135 x 105 x 12 mm (X: -67.5..67.5, Y: -52.5..52.5, Z: 0..12)
    body = create_box(size=(135, 105, 12), location=(0, 0, 6), name="LJT06_40_Base")
    
    # 4 corner counterbore holes at (+-52, +-38): hole Phi 9, cbore Phi 15 depth 5
    for sx in [-52, 52]:
        for sy in [-38, 38]:
            drill_hole(body, radius=4.5, depth=20, location=(sx, sy, 6))
            cb = create_cylinder(radius=7.5, depth=6, location=(sx, sy, 10))
            apply_boolean_difference(body, cb)
            
    # Main longitudinal cylinder barrel along Y axis at X=0, Z=45: length 130 mm (Y: -65..65)
    # Rear portion: OD 52 (Y: -25..65)
    barrel_r = create_cylinder(radius=26, depth=90, location=(0, 20, 45), rotation=(math.pi/2, 0, 0), name="BarrelR")
    # Front stepped nozzle: OD 36 (Y: -65..-25)
    barrel_f = create_cylinder(radius=18, depth=40, location=(0, -45, 45), rotation=(math.pi/2, 0, 0), name="BarrelF")
    apply_boolean_union(body, barrel_r)
    apply_boolean_union(body, barrel_f)
    
    # Main barrel through bore: Phi 24 through Y
    b_bore = create_cylinder(radius=12, depth=140, location=(0, 0, 45), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, b_bore)
    
    # Front internal thread M20x1.5 (bore Phi 18.5 depth 25) at Y=-65
    f_th = create_cylinder(radius=9.25, depth=26, location=(0, -55, 45), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, f_th)
    
    # Side vertical upright tower on -X side at X=-30, Y=-15: OD 32, rising to Z=75
    tower = create_cylinder(radius=16, depth=65, location=(-30, -15, 42.5), name="Tower")
    apply_boolean_union(body, tower)
    t_bore = create_cylinder(radius=9.0, depth=35, location=(-30, -15, 65))
    apply_boolean_difference(body, t_bore)
    
    # Side inclined boss on +X side at X=22, Y=-10, Z=45: boss OD 32 with M16x1.5 thread
    inc_boss = create_cylinder(radius=16, depth=25, location=(22, -10, 45), rotation=(0, math.pi/4, 0), name="IncBoss")
    apply_boolean_union(body, inc_boss)
    inc_bore = create_cylinder(radius=7.0, depth=35, location=(22, -10, 45), rotation=(0, math.pi/4, 0))
    apply_boolean_difference(body, inc_bore)
    
    # Bridging web connecting barrel to base plate: thickness 14 mm
    web = create_box(size=(28, 90, 35), location=(0, 10, 25), name="Web")
    apply_boolean_union(body, web)
    
    return body, "cast_iron"

# ==============================================================================
# 41. LJT06.41_箱体 (Worm Reducer Housing with 4 Corner Feet)
# ==============================================================================
def generate_ljt06_41():
    # Main central upright housing: 95 x 90 x 110 mm (Z: 14..124)
    body = create_box(size=(95, 90, 110), location=(0, 0, 69), name="LJT06_41_Body")
    
    # 4 corner protruding feet: 36 x 36 x 14 mm at (+-55, +-45, 7)
    for sx in [-55, 55]:
        for sy in [-45, 45]:
            foot = create_box(size=(36, 36, 14), location=(sx, sy, 7), name="Foot")
            apply_boolean_union(body, foot)
            drill_hole(body, radius=5.5, depth=25, location=(sx, sy, 7))
            
    # Hollow interior cavity: 79 x 74 x 95 mm
    cavity = create_box(size=(79, 74, 98), location=(0, 0, 69), name="Cavity")
    apply_boolean_difference(body, cavity)
    
    # Front large circular opening on -Y face (Y=-45) at Z=60: OD 100, opening Phi 72
    f_ring = create_cylinder(radius=50, depth=10, location=(0, -45, 60), rotation=(math.pi/2, 0, 0), name="FrontRing")
    apply_boolean_union(body, f_ring)
    f_open = create_cylinder(radius=36, depth=25, location=(0, -45, 60), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, f_open)
    
    # 6x M6 tapped holes on front circular flange (PCD 86)
    for i in range(6):
        ang = i * math.pi / 3
        hx = 43 * math.cos(ang)
        hz = 60 + 43 * math.sin(ang)
        fh = create_cylinder(radius=2.5, depth=16, location=(hx, -50, hz), rotation=(math.pi/2, 0, 0))
        apply_boolean_difference(body, fh)
        
    # Top square cover flange: 75 x 75 x 12 mm at Z=124
    top_flange = create_box(size=(75, 75, 12), location=(0, 0, 124), name="TopFlange")
    apply_boolean_union(body, top_flange)
    
    # Central top opening Phi 45 through
    top_open = create_cylinder(radius=22.5, depth=25, location=(0, 0, 124))
    apply_boolean_difference(body, top_open)
    
    # 4x M6 tapped holes on top flange corners (+-28, +-28)
    for tx in [-28, 28]:
        for ty in [-28, 28]:
            drill_hole(body, radius=2.5, depth=18, location=(tx, ty, 124))
            
    # Rear worm shaft tunnel along X axis at Y=25, Z=60: OD 54, bore Phi 32
    w_tunnel = create_cylinder(radius=27, depth=115, location=(0, 25, 60), rotation=(0, math.pi/2, 0), name="WTunnel")
    apply_boolean_union(body, w_tunnel)
    w_bore = create_cylinder(radius=16, depth=125, location=(0, 25, 60), rotation=(0, math.pi/2, 0))
    apply_boolean_difference(body, w_bore)
    
    return body, "cast_iron"

# ==============================================================================
# 42. LJT06.42_箱体 (Multi-Axis Gearbox Housing with Back Ring Flange)
# ==============================================================================
def generate_ljt06_42():
    # Back large circular mounting flange: OD 140, thickness 14 mm at Y=-60 (Y: -67..-53)
    body = create_cylinder(radius=70, depth=14, location=(0, -60, 45), rotation=(math.pi/2, 0, 0), name="LJT06_42_Base")
    
    # 4x Phi 11 holes on PCD 120
    for i in range(4):
        ang = i * math.pi / 2 + math.pi / 4
        bx = 60 * math.cos(ang)
        bz = 45 + 60 * math.sin(ang)
        drill_hole(body, radius=5.5, depth=20, location=(bx, -60, bz), rotation=(math.pi/2, 0, 0))
        
    # Open-top rectangular box body: 110 x 90 x 90 mm (X: -55..55, Y: -53..37, Z: 0..90)
    box = create_box(size=(110, 90, 90), location=(0, -8, 45), name="BoxBody")
    apply_boolean_union(body, box)
    
    # Hollow interior cavity: 94 x 74 x 85 mm
    cavity = create_box(size=(94, 74, 88), location=(0, -8, 48), name="Cavity")
    apply_boolean_difference(body, cavity)
    
    # Top cover flange rim with 6x M6 tapped holes
    for tx in [-45, 45]:
        for ty in [-40, -8, 25]:
            drill_hole(body, radius=2.5, depth=18, location=(tx, ty, 90))
            
    # Left bearing seat on -X face (X=-55) at Y=-8, Z=45: notched flange OD 70, bore Phi 42
    l_boss = create_cylinder(radius=35, depth=10, location=(-55, -8, 45), rotation=(0, math.pi/2, 0), name="LeftBoss")
    apply_boolean_union(body, l_boss)
    l_bore = create_cylinder(radius=21, depth=25, location=(-55, -8, 45), rotation=(0, math.pi/2, 0))
    apply_boolean_difference(body, l_bore)
    for ang in [math.pi/4, 3*math.pi/4, 5*math.pi/4, 7*math.pi/4]:
        ly = -8 + 26 * math.cos(ang)
        lz = 45 + 26 * math.sin(ang)
        lh = create_cylinder(radius=2.5, depth=16, location=(-55, ly, lz), rotation=(0, math.pi/2, 0))
        apply_boolean_difference(body, lh)
        
    # Right flanged bearing seat on +X face (X=55) at Y=-8, Z=45: OD 75, bore Phi 45
    r_boss = create_cylinder(radius=37.5, depth=10, location=(55, -8, 45), rotation=(0, math.pi/2, 0), name="RightBoss")
    apply_boolean_union(body, r_boss)
    r_bore = create_cylinder(radius=22.5, depth=25, location=(55, -8, 45), rotation=(0, math.pi/2, 0))
    apply_boolean_difference(body, r_bore)
    for ang in [math.pi/4, 3*math.pi/4, 5*math.pi/4, 7*math.pi/4]:
        ry = -8 + 28 * math.cos(ang)
        rz = 45 + 28 * math.sin(ang)
        rh = create_cylinder(radius=2.5, depth=16, location=(55, ry, rz), rotation=(0, math.pi/2, 0))
        apply_boolean_difference(body, rh)
        
    # Front oil drain boss on +Y face (Y=37): boss OD 32 with M16x1.5 threaded hole
    drain_boss = create_cylinder(radius=16, depth=8, location=(0, 37, 20), rotation=(math.pi/2, 0, 0), name="DrainBoss")
    apply_boolean_union(body, drain_boss)
    drain_h = create_cylinder(radius=7.0, depth=20, location=(0, 37, 20), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, drain_h)
    
    return body, "cast_iron"

# ==============================================================================
# 43. LJT06.43_壳体 (Triangular Prismatic Cage Housing)
# ==============================================================================
def generate_ljt06_43():
    # Triangular prismatic cage housing: height 75 mm (Z: 0..75)
    # Upper triangular plate at Z=68 (Z: 61..75): thickness 14 mm
    body = create_cylinder(radius=45, depth=14, location=(0, 0, 68), vertices=3, name="LJT06_43_Top")
    
    # Lower triangular plate at Z=7 (Z: 0..14): thickness 14 mm
    bot_plate = create_cylinder(radius=45, depth=14, location=(0, 0, 7), vertices=3, name="BotPlate")
    apply_boolean_union(body, bot_plate)
    
    # 3 vertical corner pillars connecting top and bottom plates: radius 12, height 55
    for i in range(3):
        ang = i * 2 * math.pi / 3 + math.pi / 6
        px = 32 * math.cos(ang)
        py = 32 * math.sin(ang)
        pillar = create_cylinder(radius=10, depth=55, location=(px, py, 37.5), name=f"Pillar_{i}")
        apply_boolean_union(body, pillar)
        
    # Central through bore Phi 30 through Z axis
    c_bore = create_cylinder(radius=15, depth=85, location=(0, 0, 37.5))
    apply_boolean_difference(body, c_bore)
    
    # 3 corner through-holes Phi 11
    for i in range(3):
        ang = i * 2 * math.pi / 3 + math.pi / 6
        hx = 32 * math.cos(ang)
        hy = 32 * math.sin(ang)
        drill_hole(body, radius=5.5, depth=85, location=(hx, hy, 37.5))
        
    # Back mounting ear on rear pillar: 18 x 20 x 25 mm at Z=20
    ear = create_box(size=(18, 20, 25), location=(0, -42, 20), name="RearEar")
    apply_boolean_union(body, ear)
    ear_h = create_cylinder(radius=4.5, depth=25, location=(0, -42, 20), rotation=(0, math.pi/2, 0))
    apply_boolean_difference(body, ear_h)
    
    return body, "machined_steel"

# ==============================================================================
# 44. LJT06.44_壳体 (Valve Casing with Hose Barb Nozzle & Flanged Wings)
# ==============================================================================
def generate_ljt06_44():
    # Base mounting wings: thickness 10 mm (Z: 0..10)
    # Right wing: 2x Phi 9 holes at (38, +-16, 5)
    # Left wing: 1 slotted hole at (-38, 0, 5)
    body = create_box(size=(105, 55, 10), location=(0, 0, 5), name="LJT06_44_Base")
    
    # 2 holes on right wing
    drill_hole(body, radius=4.5, depth=18, location=(38, -16, 5))
    drill_hole(body, radius=4.5, depth=18, location=(38, 16, 5))
    # 1 hole on left wing
    drill_hole(body, radius=4.5, depth=18, location=(-38, 0, 5))
    
    # Main cubical valve body: 55 x 50 x 52 mm (Z: 10..62)
    cube = create_box(size=(55, 50, 52), location=(0, 0, 36), name="ValveCube")
    apply_boolean_union(body, cube)
    
    # Front circular bore Phi 26 along Y axis at Z=36
    f_bore = create_cylinder(radius=13, depth=35, location=(0, -15, 36), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, f_bore)
    
    # 2 tapped ear lugs M5 on front face rim (+-20, -25, 36)
    for sx in [-20, 20]:
        lug = create_cylinder(radius=7, depth=10, location=(sx, -22, 36), rotation=(math.pi/2, 0, 0))
        apply_boolean_union(body, lug)
        lh = create_cylinder(radius=2.1, depth=16, location=(sx, -25, 36), rotation=(math.pi/2, 0, 0))
        apply_boolean_difference(body, lh)
        
    # Top port: counterbore Phi 28 depth 8, internal thread M20x1.5 (bore Phi 18.5, depth 35)
    top_cb = create_cylinder(radius=14, depth=10, location=(0, 0, 58))
    apply_boolean_difference(body, top_cb)
    top_bore = create_cylinder(radius=9.25, depth=45, location=(0, 0, 42))
    apply_boolean_difference(body, top_bore)
    
    # Rear/side cylindrical pipe nozzle extending along +Y to Y=60: OD 25, bore Phi 15
    nozzle = create_cylinder(radius=12.5, depth=35, location=(15, 42.5, 45), rotation=(math.pi/2, 0, 0), name="Nozzle")
    apply_boolean_union(body, nozzle)
    n_bore = create_cylinder(radius=7.5, depth=50, location=(15, 40, 45), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, n_bore)
    
    # 2 annular hose barb grooves on nozzle (at Y=45 and Y=53)
    for ny in [45, 53]:
        groove = create_cylinder(radius=13.5, depth=2, location=(15, ny, 45), rotation=(math.pi/2, 0, 0))
        apply_boolean_difference(body, groove)
        
    return body, "machined_steel"

# ==============================================================================
# 45. LJT06.45_箱体 (Transmission Arm / Reducer Casing - ATLAS FINAL PART)
# ==============================================================================
def generate_ljt06_45():
    # Back stadium casing body: 160 x 35 x 80 mm along Z axis (Z: -80..80, Y: -35..0, X: -40..40)
    body = create_box(size=(80, 35, 160), location=(0, -17.5, 0), name="LJT06_45_Body")
    
    # Semicircular top and bottom ends: radius 40 at Z=+-40
    top_cyl = create_cylinder(radius=40, depth=35, location=(0, -17.5, 40), rotation=(math.pi/2, 0, 0))
    bot_cyl = create_cylinder(radius=40, depth=35, location=(0, -17.5, -40), rotation=(math.pi/2, 0, 0))
    apply_boolean_union(body, top_cyl)
    apply_boolean_union(body, bot_cyl)
    
    # Hollow interior cavity on rear: 64 x 25 x 140 mm
    cavity = create_box(size=(64, 25, 140), location=(0, -25, 0), name="Cavity")
    apply_boolean_difference(body, cavity)
    
    # Front projecting cylindrical barrel at Z=40, extending along +Y: OD 70, length 65 mm (Y: 0..65)
    barrel = create_cylinder(radius=35, depth=65, location=(0, 32.5, 40), rotation=(math.pi/2, 0, 0), name="MainBarrel")
    apply_boolean_union(body, barrel)
    
    # Large through bore Phi 55 through barrel into cavity
    b_bore = create_cylinder(radius=27.5, depth=85, location=(0, 20, 40), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, b_bore)
    
    # Intermediate shaft bore Phi 28 through Y axis at Z=0
    mid_bore = create_cylinder(radius=14, depth=55, location=(0, 0, 0), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, mid_bore)
    
    # Lower pivot ear at Z=-55 extending down to Z=-75: thickness 16 mm (Y: 0..16), width 36
    ear = create_box(size=(36, 16, 45), location=(0, 8, -55), name="LowerEar")
    apply_boolean_union(body, ear)
    
    # Lower bearing bore Phi 24 through ear
    e_bore = create_cylinder(radius=12, depth=30, location=(0, 8, -55), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, e_bore)
    
    # Lower pin hole Phi 8 at Z=-70
    pin_hole = create_cylinder(radius=4.0, depth=30, location=(0, 8, -70), rotation=(math.pi/2, 0, 0))
    apply_boolean_difference(body, pin_hole)
    
    return body, "cast_iron"

# ==============================================================================
# BATCH GENERATOR LIST & RUNNER
# ==============================================================================

GENERATORS = [
    ("LJT06.31_尾座", generate_ljt06_31),
    ("LJT06.32_机油泵体", generate_ljt06_32),
    ("LJT06.33_阀体", generate_ljt06_33),
    ("LJT06.34_箱体", generate_ljt06_34),
    ("LJT06.35_箱体", generate_ljt06_35),
    ("LJT06.36_底座", generate_ljt06_36),
    ("LJT06.37_泵体", generate_ljt06_37),
    ("LJT06.38_泵体", generate_ljt06_38),
    ("LJT06.39_箱体", generate_ljt06_39),
    ("LJT06.40_箱体", generate_ljt06_40),
    ("LJT06.41_箱体", generate_ljt06_41),
    ("LJT06.42_箱体", generate_ljt06_42),
    ("LJT06.43_壳体", generate_ljt06_43),
    ("LJT06.44_壳体", generate_ljt06_44),
    ("LJT06.45_箱体", generate_ljt06_45),
]

def run_batch():
    print(f"\n{'='*70}")
    print(f"STARTING CATEGORY 06 BATCH 3 (FINAL BATCH: 15 PARTS: LJT06.31 ~ LJT06.45)")
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
    print(f"FINAL BATCH SUMMARY: {success_count} succeeded, {fail_count} failed out of {len(GENERATORS)} parts.")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    run_batch()
