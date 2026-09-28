"""
Category 05 Batch 2: 叉架类零件 (Forks, Brackets & Levers - Part 2)
Generates the remaining 22 models for Category 05:
  LJT05.25_轴承架, LJT05.26_导向支架, LJT05.27_十字接头, LJT05.28_摇臂轴座,
  LJT05.29_主轴架, LJT05.30_吊架,     LJT05.31_支座,     LJT05.32_支座,
  LJT05.33_支架,   LJT05.34_砂轮头架, LJT05.35_叉,       LJT05.36_轴架,
  LJT05.37_支座,   LJT05.38_支座,     LJT05.39_支架,     LJT05.40_刹车支架,
  LJT05.41_拨叉,   LJT05.42_拨叉,     LJT05.43_支架,     LJT05.44_连杆,
  LJT05.45_往复杠杆, LJT05.46_连杆
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
cat_dir = os.path.join(base_dir, "05_叉架类_Forks_Brackets")
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

def drill_cylinder_hole(target_obj, radius, depth, location, rotation=(0, 0, 0)):
    """Drills a cylindrical hole through target_obj using boolean difference."""
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius, depth=depth, vertices=32,
        location=location, rotation=rotation
    )
    cutter = bpy.context.active_object
    apply_boolean_difference(target_obj, cutter)

def create_rounded_box(dx, dy, dz, radius, z_start=0.0, segments=16):
    """Creates a rounded rectangular prism extruded along Z-axis."""
    bm = bmesh.new()
    hx = dx / 2.0 - radius
    hy = dy / 2.0 - radius
    
    corners = [(hx, hy), (-hx, hy), (-hx, -hy), (hx, -hy)]
    angles = [0.0, math.pi / 2.0, math.pi, 3.0 * math.pi / 2.0]
    pts = []
    
    for (cx, cy), a0 in zip(corners, angles):
        for i in range(segments):
            th = a0 + (math.pi / 2.0) * i / segments
            x = cx + radius * math.cos(th)
            y = cy + radius * math.sin(th)
            pts.append((x, y))
            
    v_bot = [bm.verts.new((x, y, z_start)) for x, y in pts]
    v_top = [bm.verts.new((x, y, z_start + dz)) for x, y in pts]
    bm.verts.ensure_lookup_table()
    
    n = len(pts)
    for i in range(n):
        i_next = (i + 1) % n
        bm.faces.new([v_bot[i], v_bot[i_next], v_top[i_next], v_top[i]])
    bm.faces.new(list(reversed(v_bot)))
    bm.faces.new(v_top)
    
    mesh = bpy.data.meshes.new("RoundedBox")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("RoundedBox", mesh)
    bpy.context.collection.objects.link(obj)
    return obj

# ==============================================================================
# 22 PART GENERATORS
# ==============================================================================

# ------------------------------------------------------------------------------
# 25. LJT05.25_轴承架 (Bearing Bracket) - Page 133
# ------------------------------------------------------------------------------
def generate_ljt05_25():
    """LJT05.25: 轴承架 (U-shaped bearing bracket with perpendicular hub)."""
    # Back plate: width 134 at top, 108 middle, height 145, thickness 20 mm
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 10, -35))
    plate = bpy.context.active_object
    plate.scale = (134, 20, 140)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    # Bottom angle cuts on plate
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-60, 10, -95), rotation=(0, math.radians(35), 0))
    c1 = bpy.context.active_object
    c1.scale = (60, 30, 80)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    apply_boolean_difference(plate, c1)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(60, 10, -95), rotation=(0, math.radians(-35), 0))
    c2 = bpy.context.active_object
    c2.scale = (60, 30, 80)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    apply_boolean_difference(plate, c2)
    
    # U-yoke arms extending forward
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -16, 0))
    yoke = bpy.context.active_object
    yoke.scale = (134, 52, 70)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    apply_boolean_union(plate, yoke)
    
    # Cut central U-slot (width 72 mm, depth 60 mm)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -20, 10))
    u_cut = bpy.context.active_object
    u_cut.scale = (72, 80, 90)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    apply_boolean_difference(plate, u_cut)
    
    # Coaxial bores across both arms: Φ50 through at Z=0, Y=-22
    drill_cylinder_hole(plate, radius=25.0, depth=150.0, location=(0, -22, 0), rotation=(0, math.pi / 2, 0))
    # Counterbores Φ60 x 4 mm
    drill_cylinder_hole(plate, radius=30.0, depth=20.0, location=(-60, -22, 0), rotation=(0, math.pi / 2, 0))
    drill_cylinder_hole(plate, radius=30.0, depth=20.0, location=(60, -22, 0), rotation=(0, math.pi / 2, 0))
    
    # Top M12 holes on arms
    drill_cylinder_hole(plate, radius=5.0, depth=30.0, location=(-51.5, -22, 30))
    drill_cylinder_hole(plate, radius=5.0, depth=30.0, location=(51.5, -22, 30))
    
    # Lower hub: projecting forward Y=-24 to +10, OD Φ66, bore Φ30, center Z=-70
    bpy.ops.mesh.primitive_cylinder_add(radius=33.0, depth=64.0, location=(0, -12, -70), rotation=(math.pi / 2, 0, 0))
    hub = bpy.context.active_object
    apply_boolean_union(plate, hub)
    
    # Hub bore Φ30H7 and relief Φ35
    drill_cylinder_hole(plate, radius=15.0, depth=80.0, location=(0, -12, -70), rotation=(math.pi / 2, 0, 0))
    drill_cylinder_hole(plate, radius=17.5, depth=24.0, location=(0, -12, -70), rotation=(math.pi / 2, 0, 0))
    
    # Top flat on hub: height 54
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -25, -40))
    flat_cut = bpy.context.active_object
    flat_cut.scale = (70, 40, 10)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    apply_boolean_difference(plate, flat_cut)
    
    # 4 x Φ11 mounting holes on plate (pitch 88 x 56 mm around lower hub)
    for hx in [-44.0, 44.0]:
        for hz in [-50.0, -90.0]:
            drill_cylinder_hole(plate, radius=5.5, depth=40.0, location=(hx, 10, hz), rotation=(math.pi / 2, 0, 0))
            drill_cylinder_hole(plate, radius=8.0, depth=15.0, location=(hx, 3, hz), rotation=(math.pi / 2, 0, 0))
            
    return plate, 'cast_iron'

# ------------------------------------------------------------------------------
# 26. LJT05.26_导向支架 (Guide Bracket) - Page 134
# ------------------------------------------------------------------------------
def generate_ljt05_26():
    """LJT05.26: 导向支架 (Block guide bracket with guideway slot and 3 bores)."""
    # Main block: 170 mm width, 64 mm depth, 109 mm height
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
    body = bpy.context.active_object
    body.scale = (170, 64, 109)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    # Central vertical bore Φ50H7 through
    drill_cylinder_hole(body, radius=25.0, depth=130.0, location=(0, 0, 0))
    # Top counterbore Φ65 x 5 mm
    drill_cylinder_hole(body, radius=32.5, depth=10.0, location=(0, 0, 52))
    
    # Top 4 x M8 bolt holes on PCD Φ58
    for ang in [math.pi/4, 3*math.pi/4, 5*math.pi/4, 7*math.pi/4]:
        hx = 29.0 * math.cos(ang)
        hy = 29.0 * math.sin(ang)
        drill_cylinder_hole(body, radius=3.4, depth=25.0, location=(hx, hy, 45))
        
    # Bottom guideway slot: width 32 mm, depth 26 mm, along Y axis
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, -54.5 + 13))
    slot = bpy.context.active_object
    slot.scale = (32, 70, 26)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    apply_boolean_difference(body, slot)
    
    # Left and right side step downs: top steps down by 16 mm outside |X| > 42
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-65, 0, 48))
    st_l = bpy.context.active_object
    st_l.scale = (50, 70, 20)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    apply_boolean_difference(body, st_l)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(65, 0, 48))
    st_r = bpy.context.active_object
    st_r.scale = (50, 70, 20)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    apply_boolean_difference(body, st_r)
    
    # Bottom side cuts outside |X| > 42: height 45 mm
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-65, 0, -35))
    bs_l = bpy.context.active_object
    bs_l.scale = (50, 70, 45)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    apply_boolean_difference(body, bs_l)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(65, 0, -35))
    bs_r = bpy.context.active_object
    bs_r.scale = (50, 70, 45)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    apply_boolean_difference(body, bs_r)
    
    # Left and right transverse bores Φ30H7 (along Y axis) at X = ±62, Z = 10
    drill_cylinder_hole(body, radius=15.0, depth=80.0, location=(-62, 0, 10), rotation=(math.pi / 2, 0, 0))
    drill_cylinder_hole(body, radius=15.0, depth=80.0, location=(62, 0, 10), rotation=(math.pi / 2, 0, 0))
    
    # Oil hole Φ8 from top down into left bore
    drill_cylinder_hole(body, radius=4.0, depth=40.0, location=(-62, 0, 30))
    
    return body, 'machined_steel'

# ------------------------------------------------------------------------------
# 27. LJT05.27_十字接头 (Cross Joint) - Page 135
# ------------------------------------------------------------------------------
def generate_ljt05_27():
    """LJT05.27: 十字接头 (Perpendicular double-sleeve cross joint with ribbed column)."""
    # Top sleeve: Axis along X. Length 110 mm. Stepped OD: Φ46 x 40 mm, Φ34 x 70 mm
    bpy.ops.mesh.primitive_cylinder_add(radius=23.0, depth=40.0, location=(15, 0, 40), rotation=(0, math.pi / 2, 0))
    top_sleeve_big = bpy.context.active_object
    
    bpy.ops.mesh.primitive_cylinder_add(radius=17.0, depth=70.0, location=(-40, 0, 40), rotation=(0, math.pi / 2, 0))
    top_sleeve_small = bpy.context.active_object
    apply_boolean_union(top_sleeve_big, top_sleeve_small)
    
    # Top bore Φ22 through
    drill_cylinder_hole(top_sleeve_big, radius=11.0, depth=130.0, location=(-15, 0, 40), rotation=(0, math.pi / 2, 0))
    # Oil hole Φ4 with countersink
    drill_cylinder_hole(top_sleeve_big, radius=2.0, depth=25.0, location=(15, 0, 60))
    
    # Bottom sleeve: Axis along Y (perpendicular!). OD Φ53, length 80 mm, bore Φ40, center Z=-40, X=15
    bpy.ops.mesh.primitive_cylinder_add(radius=26.5, depth=80.0, location=(15, 0, -40), rotation=(math.pi / 2, 0, 0))
    bot_sleeve = bpy.context.active_object
    drill_cylinder_hole(bot_sleeve, radius=20.0, depth=90.0, location=(15, 0, -40), rotation=(math.pi / 2, 0, 0))
    
    # Connecting column: Cross (+) shaped section connecting Z=-40 to Z=40 at X=15
    # Flange 1: 32 mm along Y, 8 mm along X
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(15, 0, 0))
    c1 = bpy.context.active_object
    c1.scale = (8, 32, 60)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    # Flange 2: 12 mm along Y, 24 mm along X
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(15, 0, 0))
    c2 = bpy.context.active_object
    c2.scale = (24, 12, 60)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    apply_boolean_union(c1, c2)
    
    # Intermediate boss on column: Φ14, length 26 mm pointing -X, tapped M6
    bpy.ops.mesh.primitive_cylinder_add(radius=7.0, depth=26.0, location=(-2, 0, -10), rotation=(0, math.pi / 2, 0))
    boss = bpy.context.active_object
    drill_cylinder_hole(boss, radius=2.5, depth=16.0, location=(-10, 0, -10), rotation=(0, math.pi / 2, 0))
    apply_boolean_union(c1, boss)
    
    # Combine column, top, bottom sleeves
    apply_boolean_union(top_sleeve_big, c1)
    apply_boolean_union(top_sleeve_big, bot_sleeve)
    
    # Side mounting pad on lower sleeve: 50 x 24 x 6 mm pad with 2 x M10 holes pitch 30
    pad = create_rounded_box(dx=24.0, dy=50.0, dz=6.0, radius=6.0, z_start=-3.0)
    pad.rotation_euler = (0, math.pi / 2, 0)
    pad.location = (41, 0, -40)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=False)
    drill_cylinder_hole(pad, radius=4.2, depth=25.0, location=(40, -15, -40), rotation=(0, math.pi / 2, 0))
    drill_cylinder_hole(pad, radius=4.2, depth=25.0, location=(40, 15, -40), rotation=(0, math.pi / 2, 0))
    apply_boolean_union(top_sleeve_big, pad)
    
    return top_sleeve_big, 'cast_iron'

# ------------------------------------------------------------------------------
# 28. LJT05.28_摇臂轴座 (Rocker Shaft Base) - Page 136
# ------------------------------------------------------------------------------
def generate_ljt05_28():
    """LJT05.28: 摇臂轴座 (Rocker shaft base with split horizontal bore and 2 vertical holes)."""
    # Base: 50 x 52 mm, height 8 mm
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 4))
    base = bpy.context.active_object
    base.scale = (50, 52, 8)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    # Bottom groove 20 mm wide, 2 mm deep along Y
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 1))
    grv = bpy.context.active_object
    grv.scale = (20, 60, 2.5)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    apply_boolean_difference(base, grv)
    
    # Central column: stadium shape 31 mm wide, 45 mm long along Y, height 50 mm (total height 58)
    col = create_rounded_box(dx=31.0, dy=45.0, dz=50.0, radius=12.0, z_start=8.0)
    apply_boolean_union(base, col)
    
    # Transverse bore boss: Φ30 x 31 mm wide along X at Z=38
    bpy.ops.mesh.primitive_cylinder_add(radius=15.0, depth=31.0, location=(0, 0, 38), rotation=(0, math.pi / 2, 0))
    h_boss = bpy.context.active_object
    apply_boolean_union(base, h_boss)
    
    # Transverse bore: Φ16H10 through along X
    drill_cylinder_hole(base, radius=8.0, depth=40.0, location=(0, 0, 38), rotation=(0, math.pi / 2, 0))
    
    # Two vertical through holes: 2 x Φ10.5 through entire height at Y = ±13.9
    drill_cylinder_hole(base, radius=5.25, depth=80.0, location=(0, -13.9, 30))
    drill_cylinder_hole(base, radius=5.25, depth=80.0, location=(0, 13.9, 30))
    
    # Horizontal split slot: 1.5 mm wide, cutting +Y side of the bore horizontally
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 15, 38))
    slot = bpy.context.active_object
    slot.scale = (35, 20, 1.5)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    apply_boolean_difference(base, slot)
    
    # Side triangular stiffeners: 6 mm thickness on both sides of boss
    for sx in [-13.0, 13.0]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sx, 0, 20))
        stiff = bpy.context.active_object
        stiff.scale = (5, 46, 24)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        apply_boolean_union(base, stiff)
        
    return base, 'cast_iron'

# ------------------------------------------------------------------------------
# 29. LJT05.29_主轴架 (Spindle Frame) - Page 137
# ------------------------------------------------------------------------------
def generate_ljt05_29():
    """LJT05.29: 主轴架 (Lathe spindle carriage base with cantilever clamp and rear spindle head)."""
    # Main bed carriage: 80 mm wide, 127 mm long (from X = -30 to +97), 18 mm high
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(33.5, 0, 9))
    bed = bpy.context.active_object
    bed.scale = (127, 80, 18)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    # Bottom channel recess: 60 mm wide along Y, 15 mm deep along X
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(33.5, 0, 7.5))
    rec = bpy.context.active_object
    rec.scale = (135, 60, 15)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    apply_boolean_difference(bed, rec)
    
    # 4 x Φ8.5 counterbore Φ14 mounting holes on bed (pitch 60 x 60 mm)
    for hx in [33.5 - 30, 33.5 + 30]:
        for hy in [-30.0, 30.0]:
            drill_cylinder_hole(bed, radius=4.25, depth=30.0, location=(hx, hy, 10))
            drill_cylinder_hole(bed, radius=7.0, depth=8.0, location=(hx, hy, 15))
            
    # Front cantilever clamp: length 60 mm (X = -90 to -30), width 48 mm, height 40 mm
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-60, 0, 20))
    clamp = bpy.context.active_object
    clamp.scale = (60, 48, 40)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    apply_boolean_union(bed, clamp)
    
    # Front bore Φ20H8 through along X at Z=20
    drill_cylinder_hole(bed, radius=10.0, depth=70.0, location=(-60, 0, 20), rotation=(0, math.pi / 2, 0))
    
    # Front clamp horizontal split slot 2 mm
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-60, 15, 20))
    cslot = bpy.context.active_object
    cslot.scale = (65, 25, 2)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    apply_boolean_difference(bed, cslot)
    
    # Rear elevated neck and spindle head: extends from X = 97 to 155, Z rises to 44
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(115, 0, 28))
    neck = bpy.context.active_object
    neck.scale = (36, 64, 38)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    apply_boolean_union(bed, neck)
    
    # Spindle barrel: stepped OD Φ64 x 22 mm, Φ44 x 36 mm, center Z=44
    bpy.ops.mesh.primitive_cylinder_add(radius=32.0, depth=22.0, location=(108, 0, 44), rotation=(0, math.pi / 2, 0))
    s1 = bpy.context.active_object
    bpy.ops.mesh.primitive_cylinder_add(radius=22.0, depth=36.0, location=(137, 0, 44), rotation=(0, math.pi / 2, 0))
    s2 = bpy.context.active_object
    apply_boolean_union(s1, s2)
    apply_boolean_union(bed, s1)
    
    # Spindle bore: stepped Φ48 x 22 mm, Φ24 x 40 mm
    drill_cylinder_hole(bed, radius=24.0, depth=25.0, location=(108, 0, 44), rotation=(0, math.pi / 2, 0))
    drill_cylinder_hole(bed, radius=12.0, depth=50.0, location=(137, 0, 44), rotation=(0, math.pi / 2, 0))
    
    return bed, 'cast_iron'

# ------------------------------------------------------------------------------
# 30. LJT05.30_吊架 (Hanger Bracket) - Page 138
# ------------------------------------------------------------------------------
def generate_ljt05_30():
    """LJT05.30: 吊架 (Suspension hanger bracket with perpendicular top and bottom sleeves)."""
    # Top sleeve: along X axis. OD Φ38, length 50 mm, bore Φ24H7, center at (0, 0, 35)
    bpy.ops.mesh.primitive_cylinder_add(radius=19.0, depth=50.0, location=(0, 0, 35), rotation=(0, math.pi / 2, 0))
    top_sl = bpy.context.active_object
    drill_cylinder_hole(top_sl, radius=12.0, depth=60.0, location=(0, 0, 35), rotation=(0, math.pi / 2, 0))
    
    # Top clamping lug / eyelet: width 12 mm along X, R9, hole Φ10, height to Z=54
    bpy.ops.mesh.primitive_cylinder_add(radius=9.0, depth=12.0, location=(0, 0, 54), rotation=(0, math.pi / 2, 0))
    lug = bpy.context.active_object
    drill_cylinder_hole(lug, radius=5.0, depth=20.0, location=(0, 0, 54), rotation=(0, math.pi / 2, 0))
    apply_boolean_union(top_sl, lug)
    
    # 4 mm split slot at top
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 48))
    slot = bpy.context.active_object
    slot.scale = (4, 40, 30)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    apply_boolean_difference(top_sl, slot)
    
    # Bottom sleeve: along Y axis (perpendicular!). OD Φ28, length 42 mm, bore Φ18H7, at (40, 0, -35)
    bpy.ops.mesh.primitive_cylinder_add(radius=14.0, depth=42.0, location=(40, 0, -35), rotation=(math.pi / 2, 0, 0))
    bot_sl = bpy.context.active_object
    drill_cylinder_hole(bot_sl, radius=9.0, depth=50.0, location=(40, 0, -35), rotation=(math.pi / 2, 0, 0))
    
    # Connecting arm: T-beam profile (flange 38 x 6 mm, web 6 x 18 mm) curving down and right
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-15, 0, 0))
    arm1 = bpy.context.active_object
    arm1.scale = (12, 38, 70)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(12, 0, -35))
    arm2 = bpy.context.active_object
    arm2.scale = (56, 38, 12)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    apply_boolean_union(arm1, arm2)
    
    apply_boolean_union(top_sl, arm1)
    apply_boolean_union(top_sl, bot_sl)
    
    return top_sl, 'cast_iron'

# ------------------------------------------------------------------------------
# 31. LJT05.31_支座 (Support Bracket) - Page 139
# ------------------------------------------------------------------------------
def generate_ljt05_31():
    """LJT05.31: 支座 (Support bracket with 4-hole base, bearing barrel and triangular rib)."""
    # Base: 90 x 65 mm rounded box, thickness 13 mm
    base = create_rounded_box(dx=90.0, dy=65.0, dz=13.0, radius=10.0, z_start=0.0)
    
    # 4 x Φ9 counterbore Φ14 holes (pitch 70 x 45 mm)
    for hx in [-35.0, 35.0]:
        for hy in [-22.5, 22.5]:
            drill_cylinder_hole(base, radius=4.5, depth=20.0, location=(hx, hy, 6))
            drill_cylinder_hole(base, radius=7.0, depth=5.0, location=(hx, hy, 11))
            
    # Bottom cavity recess: 55 x 30 x 5 mm
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 2.5))
    rec = bpy.context.active_object
    rec.scale = (55, 30, 6)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    apply_boolean_difference(base, rec)
    
    # Horizontal bearing barrel: OD Φ42, length 80 mm along X, center at (0, 0, 58)
    bpy.ops.mesh.primitive_cylinder_add(radius=21.0, depth=80.0, location=(0, 0, 58), rotation=(0, math.pi / 2, 0))
    barrel = bpy.context.active_object
    
    # Stepped bore: Φ30 on left, Φ24 on right
    drill_cylinder_hole(barrel, radius=15.0, depth=45.0, location=(-20, 0, 58), rotation=(0, math.pi / 2, 0))
    drill_cylinder_hole(barrel, radius=12.0, depth=45.0, location=(20, 0, 58), rotation=(0, math.pi / 2, 0))
    
    # Top oil boss: Φ15 with M8 hole
    bpy.ops.mesh.primitive_cylinder_add(radius=7.5, depth=10.0, location=(-15, 0, 78))
    boss = bpy.context.active_object
    drill_cylinder_hole(boss, radius=3.4, depth=15.0, location=(-15, 0, 78))
    apply_boolean_union(barrel, boss)
    
    # Upright web and triangular gusset rib: thickness 14 mm
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 35))
    web = bpy.context.active_object
    web.scale = (24, 40, 48)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(15, 0, 35), rotation=(0, math.radians(-25), 0))
    rib = bpy.context.active_object
    rib.scale = (14, 30, 45)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    apply_boolean_union(web, rib)
    
    apply_boolean_union(base, web)
    apply_boolean_union(base, barrel)
    
    return base, 'cast_iron'

# ------------------------------------------------------------------------------
# 32. LJT05.32_支座 (Support Bracket) - Page 140
# ------------------------------------------------------------------------------
def generate_ljt05_32():
    """LJT05.32: 支座 (Support bracket with 2-hole slotted base, front flange with 6xM6 holes)."""
    # Base: 100 x 36 mm rounded capsule, thickness 8 mm
    base = create_rounded_box(dx=100.0, dy=36.0, dz=8.0, radius=18.0, z_start=0.0)
    
    # 2 x Φ9 counterbore Φ20 depth 2 mm holes (pitch 74 mm)
    for hx in [-37.0, 37.0]:
        drill_cylinder_hole(base, radius=4.5, depth=15.0, location=(hx, 0, 4))
        drill_cylinder_hole(base, radius=10.0, depth=3.0, location=(hx, 0, 7))
        
    # Bottom groove 40 x 3 mm
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 1.5))
    bg = bpy.context.active_object
    bg.scale = (40, 40, 3.5)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    apply_boolean_difference(base, bg)
    
    # Upright T-section column: height 83 mm, web 6 mm, back flange 8 mm
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 45))
    col = bpy.context.active_object
    col.scale = (50, 6, 75)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    apply_boolean_union(base, col)
    
    # Front vertical flange plate: 56 x 70 x 15 mm at Y=-18, Z=83
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -18, 83))
    ff = bpy.context.active_object
    ff.scale = (56, 15, 70)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    apply_boolean_union(base, ff)
    
    # Bearing barrel: extending back along Y from -18 to +35, OD Φ40, bore Φ22H8
    bpy.ops.mesh.primitive_cylinder_add(radius=20.0, depth=53.0, location=(0, 8.5, 83), rotation=(math.pi / 2, 0, 0))
    b_cyl = bpy.context.active_object
    apply_boolean_union(base, b_cyl)
    
    # Bore Φ22H8 through Y and front counterbore Φ30 x 6 mm
    drill_cylinder_hole(base, radius=11.0, depth=80.0, location=(0, 0, 83), rotation=(math.pi / 2, 0, 0))
    drill_cylinder_hole(base, radius=15.0, depth=10.0, location=(0, -22, 83), rotation=(math.pi / 2, 0, 0))
    
    # 6 x M6 holes on front flange (pitch 44 x 46 mm)
    for fx in [-22.0, 22.0]:
        for fz in [83 - 23, 83, 83 + 23]:
            drill_cylinder_hole(base, radius=2.5, depth=15.0, location=(fx, -22, fz), rotation=(math.pi / 2, 0, 0))
            
    return base, 'cast_iron'

# ------------------------------------------------------------------------------
# 33. LJT05.33_支架 (Bracket) - Page 141
# ------------------------------------------------------------------------------
def generate_ljt05_33():
    """LJT05.33: 支架 (Angled dual-prong clevis bracket with H-section column)."""
    # Triangular/trapezoidal base: width 62, depth 46, thickness 5 mm
    bm = bmesh.new()
    pts = [(-31, 23), (31, 23), (20, -23), (-20, -23)]
    v_b = [bm.verts.new((x, y, 0)) for x, y in pts]
    v_t = [bm.verts.new((x, y, 5)) for x, y in pts]
    bm.verts.ensure_lookup_table()
    for i in range(4):
        bm.faces.new([v_b[i], v_b[(i+1)%4], v_t[(i+1)%4], v_t[i]])
    bm.faces.new(list(reversed(v_b)))
    bm.faces.new(v_t)
    m = bpy.data.meshes.new("BaseM")
    bm.to_mesh(m)
    bm.free()
    base = bpy.data.objects.new("BaseObj", m)
    bpy.context.collection.objects.link(base)
    
    # 3 x Φ6 mounting holes
    drill_cylinder_hole(base, radius=3.0, depth=10.0, location=(-20, 15, 2.5))
    drill_cylinder_hole(base, radius=3.0, depth=10.0, location=(20, 15, 2.5))
    drill_cylinder_hole(base, radius=3.0, depth=10.0, location=(0, -15, 2.5))
    
    # Upright column with H-ribs: rises 36 mm vertically, then tilts 60° back
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 5, 20))
    col1 = bpy.context.active_object
    col1.scale = (42, 10, 36)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    apply_boolean_union(base, col1)
    
    # Angled upper clevis body: tilts 60° from horizontal (30° from vertical)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 15, 55), rotation=(math.radians(30), 0, 0))
    clevis = bpy.context.active_object
    clevis.scale = (42, 32, 40)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    apply_boolean_union(base, clevis)
    
    # Clevis inner slot: width 22 mm, cutting through between two prongs
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 20, 58), rotation=(math.radians(30), 0, 0))
    c_slot = bpy.context.active_object
    c_slot.scale = (22, 50, 45)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    apply_boolean_difference(base, c_slot)
    
    # 2 x Φ7 pin holes across prongs
    drill_cylinder_hole(base, radius=3.5, depth=50.0, location=(0, 22, 60), rotation=(0, math.pi / 2, 0))
    
    return base, 'cast_iron'

# ------------------------------------------------------------------------------
# 34. LJT05.34_砂轮头架 (Grinding Head Bracket) - Page 142
# ------------------------------------------------------------------------------
def generate_ljt05_34():
    """LJT05.34: 砂轮头架 (Grinding head spindle housing with conical base)."""
    # Circular base flange: OD Φ92, height 10 mm
    bpy.ops.mesh.primitive_cylinder_add(radius=46.0, depth=10.0, location=(0, 0, 5))
    base = bpy.context.active_object
    
    # Bottom spigot Φ36 x 4 mm
    bpy.ops.mesh.primitive_cylinder_add(radius=18.0, depth=4.0, location=(0, 0, -2))
    spigot = bpy.context.active_object
    apply_boolean_union(base, spigot)
    
    # 2 x Φ10 mounting bolt holes/slots on PCD Φ82
    drill_cylinder_hole(base, radius=5.0, depth=20.0, location=(-41, 0, 5))
    drill_cylinder_hole(base, radius=5.0, depth=20.0, location=(41, 0, 5))
    
    # Conical / hollow column: height to Z=90
    bpy.ops.mesh.primitive_cone_add(radius1=40.0, radius2=26.0, depth=80.0, location=(0, 0, 50))
    cone = bpy.context.active_object
    apply_boolean_union(base, cone)
    
    # Horizontal spindle barrel: along X axis, length 140 mm, OD Φ52, center Z=90
    bpy.ops.mesh.primitive_cylinder_add(radius=26.0, depth=140.0, location=(10, 0, 90), rotation=(0, math.pi / 2, 0))
    barrel = bpy.context.active_object
    apply_boolean_union(base, barrel)
    
    # Stepped bore: Φ35 x 15 mm at both ends, internal relief Φ30
    drill_cylinder_hole(base, radius=15.0, depth=160.0, location=(10, 0, 90), rotation=(0, math.pi / 2, 0))
    drill_cylinder_hole(base, radius=17.5, depth=20.0, location=(-55, 0, 90), rotation=(0, math.pi / 2, 0))
    drill_cylinder_hole(base, radius=17.5, depth=20.0, location=(75, 0, 90), rotation=(0, math.pi / 2, 0))
    
    # Front accessory pad: 55 x 28 mm, with 2 x M6 holes
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-30, -26, 85))
    pad = bpy.context.active_object
    pad.scale = (55, 14, 28)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    drill_cylinder_hole(pad, radius=2.5, depth=20.0, location=(-42, -26, 85), rotation=(math.pi / 2, 0, 0))
    drill_cylinder_hole(pad, radius=2.5, depth=20.0, location=(-17, -26, 85), rotation=(math.pi / 2, 0, 0))
    apply_boolean_union(base, pad)
    
    # Top oil boss: Φ14 with M6 hole
    bpy.ops.mesh.primitive_cylinder_add(radius=7.0, depth=10.0, location=(10, 0, 118))
    boss = bpy.context.active_object
    drill_cylinder_hole(boss, radius=2.5, depth=15.0, location=(10, 0, 118))
    apply_boolean_union(base, boss)
    
    return base, 'cast_iron'

# ------------------------------------------------------------------------------
# 35. LJT05.35_叉 (Fork) - Page 143
# ------------------------------------------------------------------------------
def generate_ljt05_35():
    """LJT05.35: 叉 (Square-hub curved fork with dual prongs)."""
    # Square hub: 50 x 50 mm, length 70 mm along X, bore 30 x 30 mm
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
    hub = bpy.context.active_object
    hub.scale = (70, 50, 50)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
    sq_bore = bpy.context.active_object
    sq_bore.scale = (80, 30, 30)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    apply_boolean_difference(hub, sq_bore)
    
    # Top oval boss: 34 mm wide, thread M16 and 2 x Φ8 holes
    top_pad = create_rounded_box(dx=60.0, dy=34.0, dz=7.0, radius=12.0, z_start=25.0)
    drill_cylinder_hole(top_pad, radius=7.0, depth=20.0, location=(0, 0, 28))
    drill_cylinder_hole(top_pad, radius=4.0, depth=15.0, location=(-18, 0, 28))
    drill_cylinder_hole(top_pad, radius=4.0, depth=15.0, location=(18, 0, 28))
    apply_boolean_union(hub, top_pad)
    
    # Curved arm sweeping along R110 at 45°
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(60, 40, -40), rotation=(0, math.radians(45), math.radians(30)))
    arm = bpy.context.active_object
    arm.scale = (90, 33, 40)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    apply_boolean_union(hub, arm)
    
    # Fork tip prongs: U-slot width 24 mm, total width 50 mm, eyelets OD Φ40, bore Φ25
    bpy.ops.mesh.primitive_cylinder_add(radius=20.0, depth=50.0, location=(95, 75, -80), rotation=(0, math.pi / 2, 0))
    tip = bpy.context.active_object
    apply_boolean_union(hub, tip)
    
    # Cut central U-slot 24 mm wide
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(95, 75, -80))
    u_cut = bpy.context.active_object
    u_cut.scale = (24, 70, 70)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    apply_boolean_difference(hub, u_cut)
    
    # Bore Φ25 through both prongs
    drill_cylinder_hole(hub, radius=12.5, depth=60.0, location=(95, 75, -80), rotation=(0, math.pi / 2, 0))
    
    return hub, 'cast_iron'

# ------------------------------------------------------------------------------
# 36. LJT05.36_轴架 (Shaft Bracket) - Page 144
# ------------------------------------------------------------------------------
def generate_ljt05_36():
    """LJT05.36: 轴架 (Flanged shaft bracket with forward cantilever and front wing sleeve)."""
    # Backplate: 96 x 110 mm, thickness 10 mm at X=0
    bp = create_rounded_box(dx=10.0, dy=96.0, dz=110.0, radius=10.0, z_start=-55.0)
    bp.location = (5, 0, 0)
    
    # 4 x Φ6 mounting holes (pitch 80 x 94 mm)
    for hy in [-40.0, 40.0]:
        for hz in [-47.0, 47.0]:
            drill_cylinder_hole(bp, radius=3.0, depth=20.0, location=(5, hy, hz), rotation=(0, math.pi / 2, 0))
            
    # Main bearing barrel: OD Φ64, length 60 mm along X (from 10 to 70), bore Φ45
    bpy.ops.mesh.primitive_cylinder_add(radius=32.0, depth=60.0, location=(40, 0, 0), rotation=(0, math.pi / 2, 0))
    barrel = bpy.context.active_object
    drill_cylinder_hole(barrel, radius=22.5, depth=70.0, location=(40, 0, 0), rotation=(0, math.pi / 2, 0))
    apply_boolean_union(bp, barrel)
    
    # Cantilever arm: T-beam extending forward 82 mm, height drop 15 mm
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(80, 0, -25))
    arm = bpy.context.active_object
    arm.scale = (70, 40, 20)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    apply_boolean_union(bp, arm)
    
    # Front bearing sleeve: OD Φ45, bore Φ30, length 24 mm along X at X=120, Z=-25
    bpy.ops.mesh.primitive_cylinder_add(radius=22.5, depth=24.0, location=(120, 0, -25), rotation=(0, math.pi / 2, 0))
    f_sleeve = bpy.context.active_object
    drill_cylinder_hole(f_sleeve, radius=15.0, depth=30.0, location=(120, 0, -25), rotation=(0, math.pi / 2, 0))
    
    # Side wings on front sleeve: width 70 mm, thickness 6 mm with 2 x Φ7 holes
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(120, 0, -25))
    wings = bpy.context.active_object
    wings.scale = (6, 70, 25)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    drill_cylinder_hole(wings, radius=3.5, depth=15.0, location=(120, -28, -25), rotation=(0, math.pi / 2, 0))
    drill_cylinder_hole(wings, radius=3.5, depth=15.0, location=(120, 28, -25), rotation=(0, math.pi / 2, 0))
    apply_boolean_union(f_sleeve, wings)
    
    apply_boolean_union(bp, f_sleeve)
    
    return bp, 'cast_iron'

# ------------------------------------------------------------------------------
# 37. LJT05.37_支座 (Support Base / Swivel Base) - Page 145
# ------------------------------------------------------------------------------
def generate_ljt05_37():
    """LJT05.37: 支座 (Swivel base with vertical barrel and angled 2-bolt flange)."""
    # Base flange: 90 x 90 mm, thickness 14 mm, rounded corners R15
    base = create_rounded_box(dx=90.0, dy=90.0, dz=14.0, radius=15.0, z_start=0.0)
    
    # 4 x Φ10 holes (pitch 60 x 60 mm)
    for hx in [-30.0, 30.0]:
        for hy in [-30.0, 30.0]:
            drill_cylinder_hole(base, radius=5.0, depth=20.0, location=(hx, hy, 7))
            
    # Vertical cylinder barrel: OD Φ56, height 86 mm (to Z=100)
    bpy.ops.mesh.primitive_cylinder_add(radius=28.0, depth=86.0, location=(0, 0, 57))
    v_cyl = bpy.context.active_object
    
    # Stepped bore: top thread M36x3 depth 11, bore Φ40, lower bore Φ25
    drill_cylinder_hole(v_cyl, radius=20.0, depth=60.0, location=(0, 0, 75))
    drill_cylinder_hole(v_cyl, radius=12.5, depth=60.0, location=(0, 0, 25))
    apply_boolean_union(base, v_cyl)
    
    # Transverse barrel: center at (45, 0, 82), axis along X, OD Φ50, length 70 mm
    bpy.ops.mesh.primitive_cylinder_add(radius=25.0, depth=70.0, location=(45, 0, 82), rotation=(0, math.pi / 2, 0))
    t_barrel = bpy.context.active_object
    drill_cylinder_hole(t_barrel, radius=16.0, depth=80.0, location=(45, 0, 82), rotation=(0, math.pi / 2, 0))
    apply_boolean_union(base, t_barrel)
    
    # Angled 2-bolt diamond flange at X = 75: 90 mm pitch, 2 x Φ12 holes
    flange = create_rounded_box(dx=10.0, dy=90.0, dz=36.0, radius=12.0, z_start=-18.0)
    flange.rotation_euler = (0, 0, math.radians(45))
    flange.location = (75, 0, 82)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=False)
    drill_cylinder_hole(flange, radius=6.0, depth=20.0, location=(75, -28, 82 + 28), rotation=(0, math.pi / 2, 0))
    drill_cylinder_hole(flange, radius=6.0, depth=20.0, location=(75, 28, 82 - 28), rotation=(0, math.pi / 2, 0))
    apply_boolean_union(base, flange)
    
    return base, 'cast_iron'

# ------------------------------------------------------------------------------
# 38. LJT05.38_支座 (Support Bracket) - Page 146
# ------------------------------------------------------------------------------
def generate_ljt05_38():
    """LJT05.38: 支座 (Multi-bore support bracket with I-beam angled arm)."""
    # Central vertical sleeve: OD Φ22, bore Φ11, height 39 mm
    bpy.ops.mesh.primitive_cylinder_add(radius=11.0, depth=39.0, location=(0, 0, 19.5))
    body = bpy.context.active_object
    drill_cylinder_hole(body, radius=5.5, depth=45.0, location=(0, 0, 19.5))
    
    # Front horizontal sleeve: OD Φ28, bore Φ18, length 37 mm along Y, center at (-16.5, 0, 24)
    bpy.ops.mesh.primitive_cylinder_add(radius=14.0, depth=37.0, location=(-16.5, 0, 24), rotation=(math.pi / 2, 0, 0))
    f_sleeve = bpy.context.active_object
    drill_cylinder_hole(f_sleeve, radius=9.0, depth=45.0, location=(-16.5, 0, 24), rotation=(math.pi / 2, 0, 0))
    apply_boolean_union(body, f_sleeve)
    
    # Angled I-beam arm to upper sleeve: center at (40, 0, 49)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(20, 0, 35), rotation=(0, math.radians(-35), 0))
    arm = bpy.context.active_object
    arm.scale = (45, 12, 16)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    apply_boolean_union(body, arm)
    
    # Upper sleeve: OD Φ26, bore Φ16, length 16 mm along Y at (40, 0, 49)
    bpy.ops.mesh.primitive_cylinder_add(radius=13.0, depth=16.0, location=(40, 0, 49), rotation=(math.pi / 2, 0, 0))
    u_sleeve = bpy.context.active_object
    drill_cylinder_hole(u_sleeve, radius=8.0, depth=25.0, location=(40, 0, 49), rotation=(math.pi / 2, 0, 0))
    apply_boolean_union(body, u_sleeve)
    
    # Small base flange at bottom: width 22 mm
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 4))
    b_flange = bpy.context.active_object
    b_flange.scale = (22, 22, 8)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    apply_boolean_union(body, b_flange)
    
    return body, 'cast_iron'

# ------------------------------------------------------------------------------
# 39. LJT05.39_支架 (Bracket) - Page 147
# ------------------------------------------------------------------------------
def generate_ljt05_39():
    """LJT05.39: 支架 (Cantilever bracket with clamped vertical hub and tip lug)."""
    # Central vertical sleeve: OD Φ60, height 60 mm, bore Φ30
    bpy.ops.mesh.primitive_cylinder_add(radius=30.0, depth=60.0, location=(0, 0, 30))
    hub = bpy.context.active_object
    drill_cylinder_hole(hub, radius=15.0, depth=70.0, location=(0, 0, 30))
    
    # Top collar: OD Φ70, height 8 mm
    bpy.ops.mesh.primitive_cylinder_add(radius=35.0, depth=8.0, location=(0, 0, 56))
    col = bpy.context.active_object
    drill_cylinder_hole(col, radius=15.0, depth=15.0, location=(0, 0, 56))
    apply_boolean_union(hub, col)
    
    # Clamping ears at back: extending to X = -40, width 26 mm, height 20 mm
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-35, 0, 20))
    ears = bpy.context.active_object
    ears.scale = (20, 26, 20)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    apply_boolean_union(hub, ears)
    
    # Split slot 3 mm on ears and hub
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-25, 0, 20))
    slot = bpy.context.active_object
    slot.scale = (35, 3, 25)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    apply_boolean_difference(hub, slot)
    
    # Ear clamp bolt hole Φ11
    drill_cylinder_hole(hub, radius=5.5, depth=35.0, location=(-35, 0, 20), rotation=(math.pi / 2, 0, 0))
    
    # Cantilever arm: extends forward to X = 100 mm, thickness 15 mm
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(50, 0, 52))
    arm = bpy.context.active_object
    arm.scale = (80, 28, 12)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    apply_boolean_union(hub, arm)
    
    # Underside triangular stiffener rib: thickness 8 mm
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(40, 0, 32), rotation=(0, math.radians(-25), 0))
    rib = bpy.context.active_object
    rib.scale = (60, 8, 30)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    apply_boolean_union(hub, rib)
    
    # Tip upright lug: width 10 mm, ear R10, hole Φ8 at X=95, Z=66
    bpy.ops.mesh.primitive_cylinder_add(radius=10.0, depth=10.0, location=(95, 0, 66), rotation=(math.pi / 2, 0, 0))
    lug = bpy.context.active_object
    drill_cylinder_hole(lug, radius=4.0, depth=15.0, location=(95, 0, 66), rotation=(math.pi / 2, 0, 0))
    apply_boolean_union(hub, lug)
    
    return hub, 'cast_iron'

# ------------------------------------------------------------------------------
# 40. LJT05.40_刹车支架 (Brake Bracket) - Page 148
# ------------------------------------------------------------------------------
def generate_ljt05_40():
    """LJT05.40: 刹车支架 (Slotted mounting flange with cantilever arm and front brake hub)."""
    # Vertical mounting flange: 50 x 70 x 12 mm at X=0
    flange = create_rounded_box(dx=12.0, dy=50.0, dz=70.0, radius=8.0, z_start=-35.0)
    flange.location = (6, 0, 0)
    
    # Two slotted mounting holes 12 x 22 mm (pitch 30 mm)
    for hz in [-15.0, 15.0]:
        slot_hole = create_rounded_box(dx=20.0, dy=22.0, dz=12.0, radius=6.0, z_start=hz-6.0)
        slot_hole.location = (6, 0, 0)
        apply_boolean_difference(flange, slot_hole)
        
    # Cantilever arm: extends 145 mm along X, wall thickness 10 mm
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(75, 12, 10))
    arm = bpy.context.active_object
    arm.scale = (140, 10, 30)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    apply_boolean_union(flange, arm)
    
    # Triangular bottom gusset rib: length 46 mm, thickness 8 mm
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(35, 12, -15), rotation=(0, math.radians(-25), 0))
    gusset = bpy.context.active_object
    gusset.scale = (50, 8, 25)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    apply_boolean_union(flange, gusset)
    
    # Intermediate boss: OD Φ20, bore Φ14 at X=70, Z=0
    bpy.ops.mesh.primitive_cylinder_add(radius=10.0, depth=22.0, location=(70, 0, 0), rotation=(math.pi / 2, 0, 0))
    boss = bpy.context.active_object
    drill_cylinder_hole(boss, radius=7.0, depth=30.0, location=(70, 0, 0), rotation=(math.pi / 2, 0, 0))
    apply_boolean_union(flange, boss)
    
    # Front sleeve: OD Φ32, bore Φ16H9, length 32 mm along Y at X=145, Z=0
    bpy.ops.mesh.primitive_cylinder_add(radius=16.0, depth=32.0, location=(145, 0, 0), rotation=(math.pi / 2, 0, 0))
    f_sleeve = bpy.context.active_object
    drill_cylinder_hole(f_sleeve, radius=8.0, depth=40.0, location=(145, 0, 0), rotation=(math.pi / 2, 0, 0))
    
    # Top angled stop lug at 45°
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(145, 0, 20), rotation=(math.radians(45), 0, 0))
    lug = bpy.context.active_object
    lug.scale = (16, 16, 16)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    apply_boolean_union(f_sleeve, lug)
    
    apply_boolean_union(flange, f_sleeve)
    
    return flange, 'cast_iron'

# ------------------------------------------------------------------------------
# 41. LJT05.41_拨叉 (Shift Fork) - Page 149
# ------------------------------------------------------------------------------
def generate_ljt05_41():
    """LJT05.41: 拨叉 (Shift fork with keyed hub and 30° tilted U-fork head)."""
    # Lower hub: OD Φ40, length 45 mm along X, bore Φ20
    bpy.ops.mesh.primitive_cylinder_add(radius=20.0, depth=45.0, location=(0, 0, 0), rotation=(0, math.pi / 2, 0))
    hub = bpy.context.active_object
    drill_cylinder_hole(hub, radius=10.0, depth=55.0, location=(0, 0, 0), rotation=(0, math.pi / 2, 0))
    
    # Keyway 6 mm wide x 2.8 mm deep at bottom
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, -11.5))
    kw = bpy.context.active_object
    kw.scale = (55, 6, 4)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    apply_boolean_difference(hub, kw)
    
    # Side clamping boss at 30°
    bpy.ops.mesh.primitive_cylinder_add(radius=11.0, depth=22.0, location=(0, -22, -12), rotation=(0, math.pi / 2, 0))
    cboss = bpy.context.active_object
    drill_cylinder_hole(cboss, radius=4.5, depth=30.0, location=(0, -22, -12), rotation=(0, math.pi / 2, 0))
    apply_boolean_union(hub, cboss)
    
    # Upright cross (+) arm: length 80 mm from Z=0 to Z=80
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 40))
    c1 = bpy.context.active_object
    c1.scale = (8, 24, 70)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 40))
    c2 = bpy.context.active_object
    c2.scale = (24, 8, 70)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    apply_boolean_union(c1, c2)
    apply_boolean_union(hub, c1)
    
    # Upper U-fork head: tilted 30° from vertical, width 36, length 38, thickness 32 mm
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 10, 80), rotation=(math.radians(30), 0, 0))
    u_head = bpy.context.active_object
    u_head.scale = (32, 38, 36)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    
    # Fork slot 18 mm wide x 28 mm deep
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 15, 88), rotation=(math.radians(30), 0, 0))
    f_slot = bpy.context.active_object
    f_slot.scale = (18, 50, 28)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    apply_boolean_difference(u_head, f_slot)
    
    apply_boolean_union(hub, u_head)
    
    return hub, 'cast_iron'

# ------------------------------------------------------------------------------
# 42. LJT05.42_拨叉 (Shift Fork) - Page 150
# ------------------------------------------------------------------------------
def generate_ljt05_42():
    """LJT05.42: 拨叉 (Shift fork with upper sleeve and lower curved saddle arch)."""
    # Upper sleeve: OD Φ30, bore Φ19, length 55 mm along X at Z=87
    bpy.ops.mesh.primitive_cylinder_add(radius=15.0, depth=55.0, location=(0, 0, 87), rotation=(0, math.pi / 2, 0))
    sleeve = bpy.context.active_object
    drill_cylinder_hole(sleeve, radius=9.5, depth=65.0, location=(0, 0, 87), rotation=(0, math.pi / 2, 0))
    
    # Side clamping boss: M10x1
    bpy.ops.mesh.primitive_cylinder_add(radius=10.0, depth=18.0, location=(15, 16, 87), rotation=(math.pi / 2, 0, 0))
    sboss = bpy.context.active_object
    drill_cylinder_hole(sboss, radius=4.5, depth=25.0, location=(15, 16, 87), rotation=(math.pi / 2, 0, 0))
    apply_boolean_union(sleeve, sboss)
    
    # Neck and web: connects Z=87 down to Z=35
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 60))
    neck = bpy.context.active_object
    neck.scale = (24, 14, 45)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    apply_boolean_union(sleeve, neck)
    
    # Lower saddle fork block: width 46 mm along X, depth 40 mm along Y, height 36 mm (Z=0 to 36)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 18))
    saddle = bpy.context.active_object
    saddle.scale = (46, 50, 36)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    # Cut central opening: slot 30 mm wide along X
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 15))
    s_cut = bpy.context.active_object
    s_cut.scale = (30, 60, 32)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    apply_boolean_difference(saddle, s_cut)
    
    # Cut circular arch: radius R24 along X axis
    drill_cylinder_hole(saddle, radius=24.0, depth=60.0, location=(0, 0, 0), rotation=(0, math.pi / 2, 0))
    
    apply_boolean_union(sleeve, saddle)
    
    return sleeve, 'cast_iron'

# ------------------------------------------------------------------------------
# 43. LJT05.43_支架 (U-Frame Bracket) - Page 151
# ------------------------------------------------------------------------------
def generate_ljt05_43():
    """LJT05.43: 支架 (U-shaped dual upright column bracket with underside pivot lug)."""
    # Base plate: 168 x 80 x 10 mm
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 5))
    base = bpy.context.active_object
    base.scale = (168, 80, 10)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    # Underside central pivot lug: triangular profile with hole Φ15
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, -15))
    lug = bpy.context.active_object
    lug.scale = (120, 30, 20)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    drill_cylinder_hole(lug, radius=7.5, depth=40.0, location=(0, 0, -15), rotation=(math.pi / 2, 0, 0))
    apply_boolean_union(base, lug)
    
    # Two upright column arms: left at X=-71, right at X=+71, height 144 mm, width 50 mm
    for sx in [-71.0, 71.0]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sx, 0, 72))
        arm = bpy.context.active_object
        arm.scale = (20, 50, 134)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        
        # Top bearing head: OD Φ50, bore Φ20, counterbore Φ28 x 4 mm
        bpy.ops.mesh.primitive_cylinder_add(radius=25.0, depth=20.0, location=(sx, 0, 144), rotation=(0, math.pi / 2, 0))
        head = bpy.context.active_object
        drill_cylinder_hole(head, radius=10.0, depth=30.0, location=(sx, 0, 144), rotation=(0, math.pi / 2, 0))
        drill_cylinder_hole(head, radius=14.0, depth=8.0, location=(sx - 7 if sx > 0 else sx + 7, 0, 144), rotation=(0, math.pi / 2, 0))
        apply_boolean_union(arm, head)
        apply_boolean_union(base, arm)
        
    return base, 'cast_iron'

# ------------------------------------------------------------------------------
# 44. LJT05.44_连杆 (Connecting Rod) - Page 152
# ------------------------------------------------------------------------------
def generate_ljt05_44():
    """LJT05.44: 连杆 (Connecting rod with I-beam shank and 30° angled slotted slide head)."""
    # Left sleeve: OD Φ24, bore Φ16, length 24 mm along Y at X=0
    bpy.ops.mesh.primitive_cylinder_add(radius=12.0, depth=24.0, location=(0, 0, 0), rotation=(math.pi / 2, 0, 0))
    rod = bpy.context.active_object
    drill_cylinder_hole(rod, radius=8.0, depth=30.0, location=(0, 0, 0), rotation=(math.pi / 2, 0, 0))
    
    # Middle sleeve: OD Φ32, bore Φ20, length 24 mm along Y at X=110
    bpy.ops.mesh.primitive_cylinder_add(radius=16.0, depth=24.0, location=(110, 0, 0), rotation=(math.pi / 2, 0, 0))
    m_sleeve = bpy.context.active_object
    drill_cylinder_hole(m_sleeve, radius=10.0, depth=30.0, location=(110, 0, 0), rotation=(math.pi / 2, 0, 0))
    apply_boolean_union(rod, m_sleeve)
    
    # I-beam shank connecting X=0 to X=110: height 20 mm, flanges 12 x 4 mm
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(55, 0, 0))
    shank = bpy.context.active_object
    shank.scale = (110, 12, 16)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    apply_boolean_union(rod, shank)
    
    # Right 30° angled slide head: length 48 mm, width 32 mm, thickness 12 mm
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(130, 0, 20), rotation=(0, math.radians(-30), 0))
    head = bpy.context.active_object
    head.scale = (48, 32, 16)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    
    # 3 x Φ8 holes on slide head pitch 16 mm
    for i in [-1, 0, 1]:
        hx = 130 + i * 14 * math.cos(math.radians(30))
        hz = 20 - i * 14 * math.sin(math.radians(30))
        drill_cylinder_hole(head, radius=4.0, depth=30.0, location=(hx, 0, hz), rotation=(math.pi / 2, 0, 0))
        
    apply_boolean_union(rod, head)
    
    return rod, 'cast_iron'

# ------------------------------------------------------------------------------
# 45. LJT05.45_往复杠杆 (Reciprocating Lever) - Page 153
# ------------------------------------------------------------------------------
def generate_ljt05_45():
    """LJT05.45: 往复杠杆 (Heavy reciprocating lever with front dual clevis and rear wide fork)."""
    # Front clevis: width 120 mm, prongs 20 mm, inner slot 22 mm, bores Φ18 & Φ22
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-120, 0, 0))
    clevis = bpy.context.active_object
    clevis.scale = (75, 120, 36)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    # Cut front clevis slot: width 22 mm along Y
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-130, 0, 0))
    c_slot = bpy.context.active_object
    c_slot.scale = (80, 22, 50)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    apply_boolean_difference(clevis, c_slot)
    
    # Bores Φ18 and Φ22 across prongs
    drill_cylinder_hole(clevis, radius=9.0, depth=130.0, location=(-135, 0, 0), rotation=(math.pi / 2, 0, 0))
    drill_cylinder_hole(clevis, radius=11.0, depth=130.0, location=(-95, 0, 0), rotation=(math.pi / 2, 0, 0))
    
    # Central cross (+) stiffened beam: length 150 mm (X = -80 to +70)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-5, 0, 0))
    beam1 = bpy.context.active_object
    beam1.scale = (150, 20, 28)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-5, 0, 0))
    beam2 = bpy.context.active_object
    beam2.scale = (150, 16, 42)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    apply_boolean_union(beam1, beam2)
    apply_boolean_union(clevis, beam1)
    
    # Rear wide fork: spread 180 mm overall (Y = ±52 mm), length 110 mm
    for sy in [-52.0, 52.0]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(110, sy, 0))
        arm = bpy.context.active_object
        arm.scale = (80, 24, 28)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        
        # Bearing hub: OD Φ50, bore Φ35, length 30 mm along Z
        bpy.ops.mesh.primitive_cylinder_add(radius=25.0, depth=30.0, location=(150, sy, 0))
        hub = bpy.context.active_object
        drill_cylinder_hole(hub, radius=17.5, depth=40.0, location=(150, sy, 0))
        apply_boolean_union(arm, hub)
        apply_boolean_union(clevis, arm)
        
    return clevis, 'machined_steel'

# ------------------------------------------------------------------------------
# 46. LJT05.46_连杆 (Engine Connecting Rod) - Page 154
# ------------------------------------------------------------------------------
def generate_ljt05_46():
    """LJT05.46: 连杆 (Large engine conrod with split rod big end and small eye)."""
    # Big end half-journal: bore Φ75, OD Φ90, width 40 mm at X=0
    bpy.ops.mesh.primitive_cylinder_add(radius=45.0, depth=40.0, location=(0, 0, 0))
    big_end = bpy.context.active_object
    drill_cylinder_hole(big_end, radius=37.5, depth=50.0, location=(0, 0, 0))
    
    # Cut half-journal split (X < 0)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-45, 0, 0))
    h_cut = bpy.context.active_object
    h_cut.scale = (90, 110, 50)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    apply_boolean_difference(big_end, h_cut)
    
    # Bolt lugs on big end: bolt pitch 85 mm (Y = ±42.5 mm)
    for ly in [-42.5, 42.5]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(10, ly, 0))
        lug = bpy.context.active_object
        lug.scale = (30, 20, 40)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        drill_cylinder_hole(lug, radius=3.5, depth=50.0, location=(10, ly, 0))
        apply_boolean_union(big_end, lug)
        
    # Small end eye: OD Φ64, bore Φ46, width 40 mm at X=275
    bpy.ops.mesh.primitive_cylinder_add(radius=32.0, depth=40.0, location=(275, 0, 0))
    small_end = bpy.context.active_object
    drill_cylinder_hole(small_end, radius=23.0, depth=50.0, location=(275, 0, 0))
    
    # Shank connecting X=30 to X=245: tapered I-beam profile (length 215 mm)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(140, 0, 0))
    shank = bpy.context.active_object
    shank.scale = (215, 26, 32)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    # I-beam side flutes / recesses on shank
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(140, 0, 14))
    flute_top = bpy.context.active_object
    flute_top.scale = (190, 16, 8)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    apply_boolean_difference(shank, flute_top)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(140, 0, -14))
    flute_bot = bpy.context.active_object
    flute_bot.scale = (190, 16, 8)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    apply_boolean_difference(shank, flute_bot)
    
    apply_boolean_union(big_end, shank)
    apply_boolean_union(big_end, small_end)
    
    return big_end, 'machined_steel'


# ==============================================================================
# MAIN BATCH EXECUTION
# ==============================================================================

GENERATORS = [
    ("LJT05.25_轴承架", generate_ljt05_25),
    ("LJT05.26_导向支架", generate_ljt05_26),
    ("LJT05.27_十字接头", generate_ljt05_27),
    ("LJT05.28_摇臂轴座", generate_ljt05_28),
    ("LJT05.29_主轴架", generate_ljt05_29),
    ("LJT05.30_吊架", generate_ljt05_30),
    ("LJT05.31_支座", generate_ljt05_31),
    ("LJT05.32_支座", generate_ljt05_32),
    ("LJT05.33_支架", generate_ljt05_33),
    ("LJT05.34_砂轮头架", generate_ljt05_34),
    ("LJT05.35_叉", generate_ljt05_35),
    ("LJT05.36_轴架", generate_ljt05_36),
    ("LJT05.37_支座", generate_ljt05_37),
    ("LJT05.38_支座", generate_ljt05_38),
    ("LJT05.39_支架", generate_ljt05_39),
    ("LJT05.40_刹车支架", generate_ljt05_40),
    ("LJT05.41_拨叉", generate_ljt05_41),
    ("LJT05.42_拨叉", generate_ljt05_42),
    ("LJT05.43_支架", generate_ljt05_43),
    ("LJT05.44_连杆", generate_ljt05_44),
    ("LJT05.45_往复杠杆", generate_ljt05_45),
    ("LJT05.46_连杆", generate_ljt05_46),
]

def run_batch():
    print(f"\n{'='*70}")
    print(f"STARTING CATEGORY 05 BATCH 2 GENERATION (22 PARTS: LJT05.25 ~ LJT05.46)")
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
