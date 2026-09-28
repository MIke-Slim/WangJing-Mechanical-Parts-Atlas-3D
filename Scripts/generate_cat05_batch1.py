"""
Category 05 Batch 1: 叉架类零件 (Forks, Brackets & Levers)
Generates 13 models:
  LJT05.01_拨叉, LJT05.02_拨叉, LJT05.03_支架,
  LJT05.13_支架, LJT05.14_支架, LJT05.15_支架,
  LJT05.18_连杆, LJT05.19_踏架, LJT05.20_拨叉,
  LJT05.21_脚踏杆, LJT05.22_支架, LJT05.23_支架, LJT05.24_轴座
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
        nxt = (i + 1) % n
        bm.faces.new((v_bot[i], v_bot[nxt], v_top[nxt], v_top[i]))
        
    bm.faces.new(reversed(v_bot))
    bm.faces.new(v_top)
    
    mesh = bpy.data.meshes.new("RoundedBoxMesh")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("RoundedBox", mesh)
    bpy.context.collection.objects.link(obj)
    return obj

# ==============================================================================
# 1. LJT05.01: 拨叉 (Shift Fork)
# ==============================================================================

def generate_ljt05_01():
    """
    LJT05.01 拨叉 (Shift Fork, Page 109)
    Material: HT200
    Center distance: 120 mm.
    Right hub: OD Φ30, bore Φ15, height = 28 mm.
    Triangular rib: length = 50 mm, thickness = 6 mm, height = 28 mm.
    Arm: width = 24 mm, thickness = 10 mm.
    Left fork claw: inner arc Φ27, outer arc R27, thickness = 10 mm, claw span = 44 mm.
    Radial cross hole: Φ5 at height 14 mm with 90° conical spotface Φ11.
    """
    # Right cylindrical hub at (60, 0, 14)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=15.0, depth=28.0, vertices=48, location=(60.0, 0, 14.0)
    )
    obj = bpy.context.active_object
    
    # Connecting arm: from X=-60 to X=60, width 24 mm, thickness 10 mm (Z=0 to 10)
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, 0, 5.0)
    )
    arm = bpy.context.active_object
    arm.scale = (120.0, 24.0, 10.0)
    apply_boolean_union(obj, arm)
    
    # Left fork claw base: cylinder OD 54 mm (R27), thickness 10 mm at (-60, 0, 5)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=27.0, depth=10.0, vertices=48, location=(-60.0, 0, 5.0)
    )
    claw_base = bpy.context.active_object
    apply_boolean_union(obj, claw_base)
    
    # Fork inner opening: bore Φ27 through at (-60, 0)
    drill_cylinder_hole(obj, radius=13.5, depth=20.0, location=(-60.0, 0, 5.0))
    # Cut front opening: width 44 mm, cutting towards X=-100
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(-75.0, 0, 5.0)
    )
    front_cut = bpy.context.active_object
    front_cut.scale = (35.0, 27.0, 15.0)
    apply_boolean_difference(obj, front_cut)
    
    # Triangular stiffening rib: length 50 mm, thickness 6 mm, from hub (X=60) leftwards to X=10
    # Height from Z=10 to Z=28
    bm = bmesh.new()
    v1 = bm.verts.new((60.0, -3.0, 10.0))
    v2 = bm.verts.new((60.0, 3.0, 10.0))
    v3 = bm.verts.new((60.0, 3.0, 28.0))
    v4 = bm.verts.new((60.0, -3.0, 28.0))
    v5 = bm.verts.new((10.0, -3.0, 10.0))
    v6 = bm.verts.new((10.0, 3.0, 10.0))
    bm.verts.ensure_lookup_table()
    bm.faces.new((v1, v2, v3, v4))
    bm.faces.new((v1, v5, v6, v2))
    bm.faces.new((v4, v3, v6, v5))
    bm.faces.new((v1, v4, v5))
    bm.faces.new((v2, v6, v3))
    mesh = bpy.data.meshes.new("RibMesh")
    bm.to_mesh(mesh)
    bm.free()
    rib = bpy.data.objects.new("Rib", mesh)
    bpy.context.collection.objects.link(rib)
    apply_boolean_union(obj, rib)
    
    # Bore Φ15 in right hub through Z
    drill_cylinder_hole(obj, radius=7.5, depth=40.0, location=(60.0, 0, 14.0))
    # Radial cross hole Φ5 at height 14 mm along Y
    drill_cylinder_hole(obj, radius=2.5, depth=35.0, location=(60.0, 0, 14.0), rotation=(math.radians(90), 0, 0))
    drill_cylinder_hole(obj, radius=5.5, depth=8.0, location=(60.0, 13.0, 14.0), rotation=(math.radians(90), 0, 0))
    
    obj.name = "LJT05.01_拨叉"
    return obj, "cast_iron"

# ==============================================================================
# 2. LJT05.02: 拨叉 (Shift Fork)
# ==============================================================================

def generate_ljt05_02():
    """
    LJT05.02 拨叉 (Shift Fork, Page 110)
    Material: HT150
    Center distance: 93.75 mm.
    Hub: OD Φ40, bore Φ25, length = 50 mm.
    Fork claw: inner Φ50, outer Φ75, claw thickness = 12 mm.
    Connecting web: thickness = 10 mm.
    Upper boss: width 15 mm, length 25 mm, hole Φ8 depth 15 mm at 40° angle.
    """
    # Hub at (46.875, 0, 25)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=20.0, depth=50.0, vertices=48, location=(46.875, 0, 25.0)
    )
    obj = bpy.context.active_object
    
    # Connecting tapered body
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, 0, 25.0)
    )
    body = bpy.context.active_object
    body.scale = (93.75, 24.0, 12.0)
    apply_boolean_union(obj, body)
    
    # Fork claw base at (-46.875, 0, 25): cylinder OD 75 mm, thickness 12 mm
    bpy.ops.mesh.primitive_cylinder_add(
        radius=37.5, depth=12.0, vertices=48, location=(-46.875, 0, 25.0)
    )
    claw_base = bpy.context.active_object
    apply_boolean_union(obj, claw_base)
    
    # Bore Φ50 in claw
    drill_cylinder_hole(obj, radius=25.0, depth=20.0, location=(-46.875, 0, 25.0))
    # Cut opening towards X=-90
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(-70.0, 0, 25.0)
    )
    cut = bpy.context.active_object
    cut.scale = (40.0, 50.0, 20.0)
    apply_boolean_difference(obj, cut)
    
    # Upper inclined boss on hub at 40°: width 15 mm, length 25 mm
    th = math.radians(40)
    bx = 46.875 + 18.0 * math.cos(th)
    by = 18.0 * math.sin(th)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=7.5, depth=25.0, vertices=32,
        location=(bx, by, 35.0), rotation=(0, 0, th)
    )
    boss = bpy.context.active_object
    apply_boolean_union(obj, boss)
    
    # Bore Φ25 through hub
    drill_cylinder_hole(obj, radius=12.5, depth=60.0, location=(46.875, 0, 25.0))
    # Hole Φ8 depth 15 mm in boss
    drill_cylinder_hole(obj, radius=4.0, depth=15.0, location=(bx, by, 38.0))
    
    obj.name = "LJT05.02_拨叉"
    return obj, "cast_iron"

# ==============================================================================
# 3. LJT05.03: 支架 (Support Bracket)
# ==============================================================================

def generate_ljt05_03():
    """
    LJT05.03 支架 (Support Bracket, Page 111)
    Material: HT200
    Bridge bracket: total length = 222 mm, width = 55 mm, total height = 72 mm.
    Left & right feet: thickness = 12 mm, pitch = 194 mm.
    Cylindrical hub: OD Φ52, bore Φ32, length = 42 mm, center height = 72 mm.
    Stiffening rib: thickness = 10 mm.
    """
    # Base bridge plate: 222 x 55 mm, thickness 12 mm
    obj = create_rounded_box(222.0, 55.0, 12.0, radius=11.0, z_start=0.0)
    
    # Arched bottom cutout: width 120 mm, height 6 mm
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, 0, 3.0)
    )
    cut = bpy.context.active_object
    cut.scale = (140.0, 60.0, 6.0)
    apply_boolean_difference(obj, cut)
    
    # Cylindrical hub: OD Φ52, length 42 mm, at (X=-45, Y=0, Z=50)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=26.0, depth=42.0, vertices=48,
        location=(-45.0, 0, 50.0), rotation=(math.radians(90), 0, 0)
    )
    hub = bpy.context.active_object
    apply_boolean_union(obj, hub)
    
    # Supporting triangular gusset rib: thickness 10 mm, from hub to right foot
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(15.0, 0, 30.0)
    )
    rib = bpy.context.active_object
    rib.scale = (110.0, 10.0, 40.0)
    rib.rotation_euler = (0, math.radians(-15), 0)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    apply_boolean_union(obj, rib)
    
    # Bore Φ32 through hub along Y
    drill_cylinder_hole(obj, radius=16.0, depth=50.0, location=(-45.0, 0, 50.0), rotation=(math.radians(90), 0, 0))
    
    # Mounting holes on feet:
    # Left foot: 2 x Φ11 at X=-97, Y=±16
    drill_cylinder_hole(obj, radius=5.5, depth=25.0, location=(-97.0, 16.0, 6.0))
    drill_cylinder_hole(obj, radius=5.5, depth=25.0, location=(-97.0, -16.0, 6.0))
    
    # Right foot: 2 x Φ8 with 90° countersink Φ12 at X=97, Y=±16
    for dy in [16.0, -16.0]:
        drill_cylinder_hole(obj, radius=4.0, depth=25.0, location=(97.0, dy, 6.0))
        drill_cylinder_hole(obj, radius=6.0, depth=4.0, location=(97.0, dy, 10.0))
    drill_cylinder_hole(obj, radius=5.5, depth=25.0, location=(97.0, 0.0, 6.0))
    
    obj.name = "LJT05.03_支架"
    return obj, "cast_iron"

# ==============================================================================
# 4. LJT05.13: 支架 (Support Bracket)
# ==============================================================================

def generate_ljt05_13():
    """
    LJT05.13 支架 (Support Bracket, Page 121)
    Material: HT200
    Total length = 250 mm, width = 55 mm, pitch = 223 mm.
    Inverted bridge shape with two raised end pads (height 25 mm).
    Bottom inclined sleeve: OD Φ52, bore Φ32, length = 42 mm, inclined at 30°.
    Mounting holes on ends: 3 x Φ11 left, 2 x Φ8 + 1 x Φ11 right.
    """
    # Main beam: 250 x 55 mm, thickness 10 mm at Z=20
    obj = create_rounded_box(250.0, 55.0, 10.0, radius=11.0, z_start=20.0)
    
    # Left raised pad: 40 x 55 x 15 mm (Z=15 to 30)
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(-105.0, 0, 22.5)
    )
    left_pad = bpy.context.active_object
    left_pad.scale = (40.0, 55.0, 15.0)
    apply_boolean_union(obj, left_pad)
    
    # Right raised pad: 40 x 55 x 15 mm
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(105.0, 0, 22.5)
    )
    right_pad = bpy.context.active_object
    right_pad.scale = (40.0, 55.0, 15.0)
    apply_boolean_union(obj, right_pad)
    
    # Inclined bottom sleeve at (X=15, Y=0, Z=-10), inclined at 30°
    bpy.ops.mesh.primitive_cylinder_add(
        radius=26.0, depth=42.0, vertices=48,
        location=(15.0, 0, -10.0), rotation=(math.radians(90), math.radians(30), 0)
    )
    sleeve = bpy.context.active_object
    apply_boolean_union(obj, sleeve)
    
    # Web connecting sleeve to beam: thickness 10 mm
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(15.0, 0, 5.0)
    )
    web = bpy.context.active_object
    web.scale = (35.0, 10.0, 25.0)
    apply_boolean_union(obj, web)
    
    # Bore Φ32 in inclined sleeve
    drill_cylinder_hole(obj, radius=16.0, depth=60.0, location=(15.0, 0, -10.0), rotation=(math.radians(90), math.radians(30), 0))
    
    # Left mounting holes: 3 x Φ11
    drill_cylinder_hole(obj, radius=5.5, depth=35.0, location=(-111.0, 16.0, 22.5))
    drill_cylinder_hole(obj, radius=5.5, depth=35.0, location=(-111.0, -16.0, 22.5))
    drill_cylinder_hole(obj, radius=5.5, depth=35.0, location=(-111.0, 0.0, 22.5))
    
    # Right mounting holes: 2 x Φ8 with countersink, 1 x Φ11
    for dy in [16.0, -16.0]:
        drill_cylinder_hole(obj, radius=4.0, depth=35.0, location=(111.0, dy, 22.5))
        drill_cylinder_hole(obj, radius=5.5, depth=5.0, location=(111.0, dy, 28.0))
    drill_cylinder_hole(obj, radius=5.5, depth=35.0, location=(111.0, 0.0, 22.5))
    
    obj.name = "LJT05.13_支架"
    return obj, "cast_iron"

# ==============================================================================
# 5. LJT05.14: 支架 (Pedestal Bracket)
# ==============================================================================

def generate_ljt05_14():
    """
    LJT05.14 支架 (Pedestal Bracket, Page 122)
    Material: HT150
    Rectangular base 45 x 30 mm, thickness = 7 mm, inclined at 30° / 60°.
    Cross column: 25 x 25 mm, rib thickness = 8 mm, height = 52 mm.
    Horizontal sleeve head: OD Φ25, length = 30 mm, bore Φ10 stepped to Φ14.
    4 x Φ5 mounting holes on base pitch 35 x 20 mm.
    """
    # Top cylindrical sleeve: OD Φ25, length 30 mm along X-axis at (0, 0, 52)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=12.5, depth=30.0, vertices=48,
        location=(0, 0, 52.0), rotation=(0, math.radians(90), 0)
    )
    obj = bpy.context.active_object
    
    # Cross column: 25 x 25 mm, height 45 mm (Z=7 to 52)
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, 0, 28.0)
    )
    col1 = bpy.context.active_object
    col1.scale = (8.0, 25.0, 45.0)
    apply_boolean_union(obj, col1)
    
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, 0, 28.0)
    )
    col2 = bpy.context.active_object
    col2.scale = (25.0, 8.0, 45.0)
    apply_boolean_union(obj, col2)
    
    # Inclined base plate: 45 x 30 mm, thickness 7 mm, inclined at 30° around Y
    base = create_rounded_box(45.0, 30.0, 7.0, radius=5.0, z_start=0.0)
    base.rotation_euler = (0, math.radians(30), 0)
    base.location = (0, 0, 0)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    apply_boolean_union(obj, base)
    
    # Stepped bore in head: Φ10 through, Φ14 depth 15 mm on right side
    drill_cylinder_hole(obj, radius=5.0, depth=40.0, location=(0, 0, 52.0), rotation=(0, math.radians(90), 0))
    drill_cylinder_hole(obj, radius=7.0, depth=15.0, location=(8.0, 0, 52.0), rotation=(0, math.radians(90), 0))
    
    # 4 x Φ5 mounting holes in base plate (pitch 35 x 20)
    for dx in [-17.5, 17.5]:
        for dy in [-10.0, 10.0]:
            lx = dx * math.cos(math.radians(30))
            lz = dx * math.sin(math.radians(-30)) + 3.5
            drill_cylinder_hole(obj, radius=2.5, depth=20.0, location=(lx, dy, lz), rotation=(0, math.radians(30), 0))
            
    obj.name = "LJT05.14_支架"
    return obj, "cast_iron"

# ==============================================================================
# 6. LJT05.15: 支架 (Cantilever Bracket)
# ==============================================================================

def generate_ljt05_15():
    """
    LJT05.15 支架 (Cantilever Bracket, Page 123)
    Material: HT150
    Base foot: 37 x 66 mm, thickness = 10 mm, 2 x Φ10 holes on pitch 46 mm.
    T-section column: rib = 6 mm, height = 78 mm.
    Top horizontal sleeve: OD Φ30, bore Φ10 / Φ18, length = 40 mm.
    Front cantilever lug: width = 27 mm, hole Φ18 spotface / Φ5 hole.
    """
    # Base foot plate: 37 x 66 mm, thickness 10 mm
    obj = create_rounded_box(37.0, 66.0, 10.0, radius=6.0, z_start=0.0)
    
    # Bottom channel recess: 25 x 68 x 3 mm
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, 0, 1.5)
    )
    chan = bpy.context.active_object
    chan.scale = (25.0, 68.0, 3.2)
    apply_boolean_difference(obj, chan)
    
    # Upright T-section column: height from Z=10 to Z=78
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, 0, 44.0)
    )
    col = bpy.context.active_object
    col.scale = (6.0, 46.0, 68.0)
    apply_boolean_union(obj, col)
    
    # Top horizontal sleeve: OD Φ30, length 40 mm along Y at (0, 0, 78)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=15.0, depth=40.0, vertices=48,
        location=(0, 0, 78.0), rotation=(math.radians(90), 0, 0)
    )
    sleeve = bpy.context.active_object
    apply_boolean_union(obj, sleeve)
    
    # Front cantilever lug at X=-15, Z=78: width 27 mm, thickness 14 mm
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(-13.5, 0, 78.0)
    )
    lug = bpy.context.active_object
    lug.scale = (27.0, 20.0, 24.0)
    apply_boolean_union(obj, lug)
    
    # Bore Φ10 through sleeve, Φ18 counterbore depth 9 mm
    drill_cylinder_hole(obj, radius=5.0, depth=50.0, location=(0, 0, 78.0), rotation=(math.radians(90), 0, 0))
    drill_cylinder_hole(obj, radius=9.0, depth=12.0, location=(0, -15.0, 78.0), rotation=(math.radians(90), 0, 0))
    
    # Front lug hole: Φ5 hole, Φ18 spotface
    drill_cylinder_hole(obj, radius=2.5, depth=30.0, location=(-15.0, 0, 78.0), rotation=(math.radians(90), 0, 0))
    drill_cylinder_hole(obj, radius=9.0, depth=6.0, location=(-15.0, 8.0, 78.0), rotation=(math.radians(90), 0, 0))
    
    # 2 x Φ10 holes in base foot (pitch 46 mm along Y)
    drill_cylinder_hole(obj, radius=5.0, depth=20.0, location=(0, 23.0, 5.0))
    drill_cylinder_hole(obj, radius=5.0, depth=20.0, location=(0, -23.0, 5.0))
    
    obj.name = "LJT05.15_支架"
    return obj, "cast_iron"

# ==============================================================================
# 7. LJT05.18: 连杆 (Connecting Rod / Rocking Lever)
# ==============================================================================

def generate_ljt05_18():
    """
    LJT05.18 连杆 (Connecting Rod / Rocking Lever, Page 126)
    Material: HT200
    Left eyelet: OD Φ25, bore Φ12, length = 24 mm.
    Middle hub: OD Φ40, bore Φ16, length = 28 mm at distance 84 mm.
    Right clevis head: fork width = 35 mm, slot = 15 mm, holes Φ10, distance = 46 mm at 30° (height 42 mm).
    T-section connecting beam.
    """
    # Left eyelet at (0, 0, 12)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=12.5, depth=24.0, vertices=48, location=(0, 0, 12.0)
    )
    obj = bpy.context.active_object
    
    # Middle hub at (84, 0, 14): OD Φ40, length 28 mm
    bpy.ops.mesh.primitive_cylinder_add(
        radius=20.0, depth=28.0, vertices=48, location=(84.0, 0, 14.0)
    )
    mid_hub = bpy.context.active_object
    apply_boolean_union(obj, mid_hub)
    
    # Connecting beam 1 (left to middle): length 84 mm, width 20 mm, thickness 10 mm
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(42.0, 0, 12.0)
    )
    beam1 = bpy.context.active_object
    beam1.scale = (84.0, 10.0, 20.0)
    apply_boolean_union(obj, beam1)
    
    # Right clevis head at (130, 0, 42): angled at 30°
    # Clevis outer block: 35 x 30 x 30 mm
    bpy.ops.mesh.primitive_cylinder_add(
        radius=15.0, depth=35.0, vertices=48,
        location=(130.0, 0, 42.0), rotation=(math.radians(90), 0, 0)
    )
    clevis = bpy.context.active_object
    apply_boolean_union(obj, clevis)
    
    # Connecting beam 2 (middle to clevis)
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(107.0, 0, 28.0)
    )
    beam2 = bpy.context.active_object
    beam2.scale = (50.0, 10.0, 20.0)
    beam2.rotation_euler = (0, math.radians(-30), 0)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    apply_boolean_union(obj, beam2)
    
    # Bore Φ12 in left eyelet
    drill_cylinder_hole(obj, radius=6.0, depth=35.0, location=(0, 0, 12.0))
    # Bore Φ16 in middle hub
    drill_cylinder_hole(obj, radius=8.0, depth=40.0, location=(84.0, 0, 14.0))
    
    # Clevis slot: width 15 mm along Y, cutting through clevis head
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(130.0, 0, 42.0)
    )
    slot = bpy.context.active_object
    slot.scale = (40.0, 15.0, 40.0)
    apply_boolean_difference(obj, slot)
    
    # Clevis pin holes: Φ10 through along Y
    drill_cylinder_hole(obj, radius=5.0, depth=50.0, location=(130.0, 0, 42.0), rotation=(math.radians(90), 0, 0))
    
    obj.name = "LJT05.18_连杆"
    return obj, "cast_iron"

# ==============================================================================
# 8. LJT05.19: 踏架 (Pedal Bracket)
# ==============================================================================

def generate_ljt05_19():
    """
    LJT05.19 踏架 (Pedal Bracket, Page 127)
    Material: HT150
    Front sleeve: OD Φ38, bore Φ24, length = 58 mm, with 30° top pad (2 x M10 holes).
    Arched arm: cross-rib 10 mm, height = 37 mm, length = 76 mm.
    Rear flange: 34 x 50 mm, thickness = 7 mm, 2 x Φ7 countersunk holes on pitch 32 mm.
    """
    # Front sleeve at (0, 0, 19): OD Φ38, length 58 mm along Y
    bpy.ops.mesh.primitive_cylinder_add(
        radius=19.0, depth=58.0, vertices=48,
        location=(0, 0, 19.0), rotation=(math.radians(90), 0, 0)
    )
    obj = bpy.context.active_object
    
    # Top inclined mounting pad on sleeve at 30°: width 28 mm, length 35 mm
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, 0, 36.0)
    )
    pad = bpy.context.active_object
    pad.scale = (28.0, 35.0, 8.0)
    pad.rotation_euler = (math.radians(-30), 0, 0)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    apply_boolean_union(obj, pad)
    
    # Rear mounting flange: 34 x 50 mm, thickness 7 mm at (76, 0, 37)
    flange = create_rounded_box(34.0, 50.0, 7.0, radius=5.0, z_start=33.5)
    flange.location = (76.0, 0, 0)
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
    apply_boolean_union(obj, flange)
    
    # Arched arm connecting sleeve to flange: width 10 mm, height 24 mm
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(38.0, 0, 30.0)
    )
    arm = bpy.context.active_object
    arm.scale = (76.0, 10.0, 18.0)
    apply_boolean_union(obj, arm)
    
    # Bore Φ24 through sleeve along Y
    drill_cylinder_hole(obj, radius=12.0, depth=70.0, location=(0, 0, 19.0), rotation=(math.radians(90), 0, 0))
    
    # 2 x M10 holes on top pad (pitch 25 mm)
    for dy in [-12.5, 12.5]:
        drill_cylinder_hole(obj, radius=4.25, depth=25.0, location=(0, dy, 36.0))
        
    # 2 x Φ7 holes with 90° countersink Φ13 in rear flange (pitch 32 mm)
    for dy in [-16.0, 16.0]:
        drill_cylinder_hole(obj, radius=3.5, depth=20.0, location=(76.0, dy, 37.0))
        drill_cylinder_hole(obj, radius=6.5, depth=4.0, location=(76.0, dy, 38.5))
        
    obj.name = "LJT05.19_踏架"
    return obj, "cast_iron"

# ==============================================================================
# 9. LJT05.20: 拨叉 (Split Clamp Shift Fork)
# ==============================================================================

def generate_ljt05_20():
    """
    LJT05.20 拨叉 (Split Clamp Shift Fork, Page 128)
    Material: HT200
    Split clamping sleeve: OD Φ80, bore Φ44, length = 120 mm.
    Clamping lugs: width 70 mm, slot 5 mm, 2 x Φ18.5 holes with Φ33 counterbores.
    Side stop flange: 68 x 39 mm, thickness 15 mm, 2 x M12 holes at 40° angle.
    Arched horn arm: R80/R150, length 180 mm, top eyelet OD Φ45, bore Φ20, length 35 mm.
    """
    # Main clamping sleeve: OD Φ80, length 120 mm along Z at (0, 0, 60)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=40.0, depth=120.0, vertices=48, location=(0, 0, 60.0)
    )
    obj = bpy.context.active_object
    
    # Clamping lugs at bottom (Y=-40 to -55): width 70 mm along X, length 50 mm along Z
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, -45.0, 25.0)
    )
    lugs = bpy.context.active_object
    lugs.scale = (70.0, 25.0, 50.0)
    apply_boolean_union(obj, lugs)
    
    # Side stop flange at 40° angle around Z: 68 x 39 x 15 mm
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(45.0, 35.0, 60.0)
    )
    side_flg = bpy.context.active_object
    side_flg.scale = (15.0, 68.0, 39.0)
    side_flg.rotation_euler = (0, 0, math.radians(40))
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    apply_boolean_union(obj, side_flg)
    
    # Arched horn arm: curved upwards from (0, 0, 90) to (-60, 0, 200)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=14.0, depth=120.0, vertices=32,
        location=(-35.0, 0, 150.0), rotation=(0, math.radians(-30), 0)
    )
    horn = bpy.context.active_object
    apply_boolean_union(obj, horn)
    
    # Top eyelet at (-65, 0, 205): OD Φ45, length 35 mm along Y
    bpy.ops.mesh.primitive_cylinder_add(
        radius=22.5, depth=35.0, vertices=48,
        location=(-65.0, 0, 205.0), rotation=(math.radians(90), 0, 0)
    )
    eyelet = bpy.context.active_object
    apply_boolean_union(obj, eyelet)
    
    # Bore Φ44 through clamping sleeve
    drill_cylinder_hole(obj, radius=22.0, depth=140.0, location=(0, 0, 60.0))
    # Keyway 12 mm wide in bore
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, 23.0, 60.0)
    )
    key_cut = bpy.context.active_object
    key_cut.scale = (12.0, 6.0, 130.0)
    apply_boolean_difference(obj, key_cut)
    
    # Split slot: 5 mm wide along X, through clamping lugs
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, -45.0, 25.0)
    )
    slot_cut = bpy.context.active_object
    slot_cut.scale = (5.0, 40.0, 60.0)
    apply_boolean_difference(obj, slot_cut)
    
    # Clamping bolt holes: 2 x Φ18.5 with Φ33 counterbores through lugs along X
    for dz in [12.0, 38.0]:
        drill_cylinder_hole(obj, radius=9.25, depth=90.0, location=(0, -45.0, dz), rotation=(0, math.radians(90), 0))
        drill_cylinder_hole(obj, radius=16.5, depth=25.0, location=(25.0, -45.0, dz), rotation=(0, math.radians(90), 0))
        
    # Eyelet bore: Φ20 through along Y
    drill_cylinder_hole(obj, radius=10.0, depth=50.0, location=(-65.0, 0, 205.0), rotation=(math.radians(90), 0, 0))
    
    obj.name = "LJT05.20_拨叉"
    return obj, "cast_iron"

# ==============================================================================
# 10. LJT05.21: 脚踏杆 (Foot Pedal Lever)
# ==============================================================================

def generate_ljt05_21():
    """
    LJT05.21 脚踏杆 (Foot Pedal Lever, Page 129)
    Material: HT200
    Central pivot hub: OD Φ28, bore Φ16, length = 40 mm.
    Upward arm: length 46 mm at 60°, eyelet OD Φ20, bore Φ10, length 20 mm.
    Curved lower arm: arched pedal plate width 38 mm, length 64 mm, curved radius R50.
    """
    # Central pivot hub: OD Φ28, length 40 mm along Y at (0, 0, 20)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=14.0, depth=40.0, vertices=48,
        location=(0, 0, 20.0), rotation=(math.radians(90), 0, 0)
    )
    obj = bpy.context.active_object
    
    # Upward lever arm: length 46 mm at 60° (30° from vertical)
    th_up = math.radians(60)
    ex = 46.0 * math.cos(th_up)
    ez = 20.0 + 46.0 * math.sin(th_up)
    
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(ex / 2.0, 0, (20.0 + ez) / 2.0)
    )
    up_arm = bpy.context.active_object
    up_arm.scale = (10.0, 20.0, 46.0)
    up_arm.rotation_euler = (0, math.radians(-30), 0)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    apply_boolean_union(obj, up_arm)
    
    # Top eyelet at (ex, 0, ez): OD Φ20, length 20 mm along Y
    bpy.ops.mesh.primitive_cylinder_add(
        radius=10.0, depth=20.0, vertices=48,
        location=(ex, 0, ez), rotation=(math.radians(90), 0, 0)
    )
    top_eye = bpy.context.active_object
    apply_boolean_union(obj, top_eye)
    
    # Curved forward pedal arm: length 57 mm
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(-30.0, 0, 10.0)
    )
    pedal_arm = bpy.context.active_object
    pedal_arm.scale = (57.0, 20.0, 10.0)
    apply_boolean_union(obj, pedal_arm)
    
    # Arched pedal plate at end: width 38 mm, length 64 mm, curved arc R50
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(-70.0, 0, 5.0)
    )
    plate = bpy.context.active_object
    plate.scale = (64.0, 38.0, 6.0)
    apply_boolean_union(obj, plate)
    
    # Bore Φ16 in pivot hub
    drill_cylinder_hole(obj, radius=8.0, depth=50.0, location=(0, 0, 20.0), rotation=(math.radians(90), 0, 0))
    # Bore Φ10 in top eyelet
    drill_cylinder_hole(obj, radius=5.0, depth=30.0, location=(ex, 0, ez), rotation=(math.radians(90), 0, 0))
    
    obj.name = "LJT05.21_脚踏杆"
    return obj, "cast_iron"

# ==============================================================================
# 11. LJT05.22: 支架 (Cradle Support Bracket)
# ==============================================================================

def generate_ljt05_22():
    """
    LJT05.22 支架 (Cradle Support Bracket, Page 130)
    Material: HT200
    Base plate: 100 x 180 mm, thickness = 10 mm, 4 x Φ12 counterbored holes.
    Semi-cylindrical cradle: bore Φ70 (R35), outer R40, length 42 mm.
    Supporting column: cross-section rib 8 mm with gussets R50/R82, height = 100 mm.
    """
    # Base plate: 100 x 180 mm, thickness 10 mm
    obj = create_rounded_box(180.0, 100.0, 10.0, radius=12.0, z_start=0.0)
    
    # Bottom recess: 140 x 80 x 4 mm
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, 0, 2.0)
    )
    rec = bpy.context.active_object
    rec.scale = (140.0, 80.0, 4.2)
    apply_boolean_difference(obj, rec)
    
    # Supporting central column: cross section 8 mm thick, height from Z=10 to Z=100
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, 0, 55.0)
    )
    col1 = bpy.context.active_object
    col1.scale = (8.0, 86.0, 90.0)
    apply_boolean_union(obj, col1)
    
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, 0, 55.0)
    )
    col2 = bpy.context.active_object
    col2.scale = (70.0, 8.0, 90.0)
    apply_boolean_union(obj, col2)
    
    # Semi-cylindrical cradle body at Z=100: outer R40, length 42 mm along X
    bpy.ops.mesh.primitive_cylinder_add(
        radius=40.0, depth=42.0, vertices=48,
        location=(0, 0, 100.0), rotation=(0, math.radians(90), 0)
    )
    cradle = bpy.context.active_object
    apply_boolean_union(obj, cradle)
    
    # Cradle split flanges: width 100 mm along Y, thickness 10 mm at Z=100
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, 0, 102.5)
    )
    c_flg = bpy.context.active_object
    c_flg.scale = (42.0, 100.0, 5.0)
    apply_boolean_union(obj, c_flg)
    
    # Bore Φ70 (R35) through cradle along X
    drill_cylinder_hole(obj, radius=35.0, depth=60.0, location=(0, 0, 100.0), rotation=(0, math.radians(90), 0))
    # Cut top open above Z=100
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, 0, 125.0)
    )
    top_open = bpy.context.active_object
    top_open.scale = (60.0, 70.0, 50.0)
    apply_boolean_difference(obj, top_open)
    
    # 4 x Φ12 mounting holes on base (pitch 140 x 70) with Φ18 counterbore depth 2 mm
    for dx in [-70.0, 70.0]:
        for dy in [-35.0, 35.0]:
            drill_cylinder_hole(obj, radius=6.0, depth=20.0, location=(dx, dy, 5.0))
            drill_cylinder_hole(obj, radius=9.0, depth=4.0, location=(dx, dy, 9.0))
            
    # 4 x M4 holes on cradle split faces (pitch 24 mm along X, Y=±45)
    for dx in [-12.0, 12.0]:
        for dy in [-45.0, 45.0]:
            drill_cylinder_hole(obj, radius=1.7, depth=10.0, location=(dx, dy, 100.0))
            
    obj.name = "LJT05.22_支架"
    return obj, "cast_iron"

# ==============================================================================
# 12. LJT05.23: 支架 (Swan-neck Column Bracket)
# ==============================================================================

def generate_ljt05_23():
    """
    LJT05.23 支架 (Swan-neck Column Bracket, Page 131)
    Material: HT200
    Lower vertical sleeve: OD Φ60, height = 40 mm, stepped bore M42x2 / Φ27.
    Curved swan-neck column: rib 38 x 8 mm, total height = 110 mm.
    Upper plate: 80 x 70 mm, thickness = 12 mm, 4 x M6 holes.
    Upper horizontal boss: OD Φ30, bore Φ15, length = 38 mm.
    """
    # Lower vertical sleeve: OD Φ60, height 40 mm (Z=0 to 40)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=30.0, depth=40.0, vertices=48, location=(0, 0, 20.0)
    )
    obj = bpy.context.active_object
    
    # Curved swan-neck column: from (0, 0, 40) to (-45, 0, 100)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=18.0, depth=80.0, vertices=32,
        location=(-25.0, 0, 70.0), rotation=(0, math.radians(-25), 0)
    )
    col = bpy.context.active_object
    apply_boolean_union(obj, col)
    
    # Upper mounting plate at (-45, 0, 105): 80 x 70 mm, thickness 12 mm
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(-45.0, 0, 105.0)
    )
    plate = bpy.context.active_object
    plate.scale = (12.0, 80.0, 70.0)
    apply_boolean_union(obj, plate)
    
    # Upper horizontal boss: OD Φ30, length 38 mm along X at (-45, 0, 110)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=15.0, depth=38.0, vertices=48,
        location=(-45.0, 0, 110.0), rotation=(0, math.radians(90), 0)
    )
    boss = bpy.context.active_object
    apply_boolean_union(obj, boss)
    
    # Bores:
    # Lower sleeve bore: Φ27 through, M42x2 (Φ42) counterbore depth 30 mm
    drill_cylinder_hole(obj, radius=13.5, depth=60.0, location=(0, 0, 20.0))
    drill_cylinder_hole(obj, radius=21.0, depth=30.0, location=(0, 0, 15.0))
    
    # Upper boss bore: Φ15 through along X
    drill_cylinder_hole(obj, radius=7.5, depth=50.0, location=(-45.0, 0, 110.0), rotation=(0, math.radians(90), 0))
    
    # 4 x M6 holes in upper plate (pitch 60 x 50)
    for dy in [-30.0, 30.0]:
        for dz in [-25.0, 25.0]:
            drill_cylinder_hole(obj, radius=2.5, depth=20.0, location=(-45.0, dy, 105.0 + dz), rotation=(0, math.radians(90), 0))
            
    obj.name = "LJT05.23_支架"
    return obj, "cast_iron"

# ==============================================================================
# 13. LJT05.24: 轴座 (Bearing Housing Base)
# ==============================================================================

def generate_ljt05_24():
    """
    LJT05.24 轴座 (Bearing Housing Base, Page 132)
    Material: HT200
    Box housing: 244 x 82 x 140 mm.
    Central coaxial bearing bores: OD Φ70, bore Φ35, middle cavity 105 mm.
    Front window opening 80 mm high, 4 x Φ13 counterbored holes.
    Top hinge boss: OD Φ38, bore Φ16, length 75 mm, M24.
    Bottom mounting foot: 2 vertical slots and 2 x M12 holes.
    """
    # Main box body: 244 x 82 x 100 mm at (0, 0, 70)
    obj = create_rounded_box(244.0, 82.0, 100.0, radius=15.0, z_start=20.0)
    
    # Top hinge boss: OD Φ38, length 75 mm along X at (35, 0, 120)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=19.0, depth=75.0, vertices=48,
        location=(35.0, 0, 120.0), rotation=(0, math.radians(90), 0)
    )
    hinge = bpy.context.active_object
    apply_boolean_union(obj, hinge)
    
    # Bottom slotted mounting foot: 130 x 82 x 20 mm (Z=0 to 20)
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(-30.0, 0, 10.0)
    )
    foot = bpy.context.active_object
    foot.scale = (130.0, 82.0, 20.0)
    apply_boolean_union(obj, foot)
    
    # Central coaxial bearing bore Φ35 through along X
    drill_cylinder_hole(obj, radius=17.5, depth=260.0, location=(0, 0, 70.0), rotation=(0, math.radians(90), 0))
    # Middle relief cavity Φ50 length 105 mm
    drill_cylinder_hole(obj, radius=25.0, depth=105.0, location=(0, 0, 70.0), rotation=(0, math.radians(90), 0))
    
    # Front window opening: 80 x 60 mm along Y
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, 30.0, 70.0)
    )
    win = bpy.context.active_object
    win.scale = (80.0, 50.0, 60.0)
    apply_boolean_difference(obj, win)
    
    # Top hinge bore: Φ16 through along X
    drill_cylinder_hole(obj, radius=8.0, depth=90.0, location=(35.0, 0, 120.0), rotation=(0, math.radians(90), 0))
    
    # 4 x Φ13 mounting holes on front face (pitch 150 x 80) with Φ20 counterbores
    for dx in [-75.0, 75.0]:
        for dz in [-40.0, 40.0]:
            drill_cylinder_hole(obj, radius=6.5, depth=40.0, location=(dx, 35.0, 70.0 + dz), rotation=(math.radians(90), 0, 0))
            drill_cylinder_hole(obj, radius=10.0, depth=15.0, location=(dx, 40.0, 70.0 + dz), rotation=(math.radians(90), 0, 0))
            
    # Bottom mounting slots: 2 vertical slots width 18 mm, length 32 mm
    for dx in [-50.0, -10.0]:
        bpy.ops.mesh.primitive_cube_add(
            size=1.0, location=(dx, 0, 10.0)
        )
        slot = bpy.context.active_object
        slot.scale = (18.0, 32.0, 25.0)
        apply_boolean_difference(obj, slot)
        
    obj.name = "LJT05.24_轴座"
    return obj, "cast_iron"

# ==============================================================================
# MAIN BATCH EXECUTION
# ==============================================================================

GENERATORS = [
    ("LJT05.01_拨叉", generate_ljt05_01),
    ("LJT05.02_拨叉", generate_ljt05_02),
    ("LJT05.03_支架", generate_ljt05_03),
    ("LJT05.13_支架", generate_ljt05_13),
    ("LJT05.14_支架", generate_ljt05_14),
    ("LJT05.15_支架", generate_ljt05_15),
    ("LJT05.18_连杆", generate_ljt05_18),
    ("LJT05.19_踏架", generate_ljt05_19),
    ("LJT05.20_拨叉", generate_ljt05_20),
    ("LJT05.21_脚踏杆", generate_ljt05_21),
    ("LJT05.22_支架", generate_ljt05_22),
    ("LJT05.23_支架", generate_ljt05_23),
    ("LJT05.24_轴座", generate_ljt05_24),
]

def run_batch():
    print(f"\n{'='*70}")
    print(f"STARTING CATEGORY 05 BATCH 1 GENERATION (13 PARTS: LJT05.01 ~ LJT05.24)")
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
