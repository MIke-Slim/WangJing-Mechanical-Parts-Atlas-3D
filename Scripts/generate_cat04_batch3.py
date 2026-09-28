"""
Category 04 Batch 3: 轮盘盖类零件 (Covers, Caps & Casings)
Generates 17 models: LJT04.32 ~ LJT04.48
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
cat_dir = os.path.join(base_dir, "04_轮盘盖类_Discs_Covers")
renders_dir = os.path.join(base_dir, "Renders")
os.makedirs(cat_dir, exist_ok=True)
os.makedirs(renders_dir, exist_ok=True)

# ==============================================================================
# COMMON CAD MODELING HELPERS
# ==============================================================================

def build_revolved_body(profile_pts, segments=64, axis='Z'):
    """
    Builds a 3D revolved body from 2D profile coordinates (along axis, radius).
    profile_pts: list of (pos, radius) tuples.
    axis: 'Z' revolves around Z-axis (default for discs); 'X' around X-axis.
    """
    bm = bmesh.new()
    rings = []
    
    for pos, r in profile_pts:
        ring = []
        for i in range(segments):
            theta = i * 2.0 * math.pi / segments
            if axis == 'Z':
                x = r * math.cos(theta)
                y = r * math.sin(theta)
                z = pos
            else:
                x = pos
                y = r * math.cos(theta)
                z = r * math.sin(theta)
            ring.append(bm.verts.new((x, y, z)))
        rings.append(ring)
        
    bm.verts.ensure_lookup_table()
    for j in range(len(profile_pts) - 1):
        r1 = rings[j]
        r2 = rings[j+1]
        for i in range(segments):
            next_i = (i + 1) % segments
            if axis == 'Z':
                bm.faces.new((r1[i], r1[next_i], r2[next_i], r2[i]))
            else:
                bm.faces.new((r1[i], r2[i], r2[next_i], r1[next_i]))
                
    mesh = bpy.data.meshes.new("RevolvedMesh")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("RevolvedBody", mesh)
    bpy.context.collection.objects.link(obj)
    return obj

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

def create_stadium_prism(length_between_centers, radius, height, z_start=0.0):
    """
    Creates an extruded stadium/obround prism along Z-axis.
    Ends are semi-circles of radius at (0, ±length/2).
    """
    bm = bmesh.new()
    half_l = length_between_centers / 2.0
    segs = 32
    bottom_ring = []
    
    # Upper semi-circle (around (0, half_l))
    for i in range(segs // 2 + 1):
        th = math.pi * i / (segs // 2)
        x = radius * math.cos(th)
        y = half_l + radius * math.sin(th)
        bottom_ring.append((x, y))
        
    # Lower semi-circle (around (0, -half_l))
    for i in range(segs // 2 + 1):
        th = math.pi + math.pi * i / (segs // 2)
        x = radius * math.cos(th)
        y = -half_l + radius * math.sin(th)
        bottom_ring.append((x, y))
        
    v_bot = [bm.verts.new((x, y, z_start)) for x, y in bottom_ring]
    v_top = [bm.verts.new((x, y, z_start + height)) for x, y in bottom_ring]
    bm.verts.ensure_lookup_table()
    
    n = len(bottom_ring)
    for i in range(n):
        nxt = (i + 1) % n
        bm.faces.new((v_bot[i], v_bot[nxt], v_top[nxt], v_top[i]))
        
    bm.faces.new(reversed(v_bot))
    bm.faces.new(v_top)
    
    mesh = bpy.data.meshes.new("StadiumMesh")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("StadiumPrism", mesh)
    bpy.context.collection.objects.link(obj)
    return obj

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
# 1. LJT04.32: 闷盖 (Blind Bearing Cover)
# ==============================================================================

def generate_ljt04_32():
    """
    LJT04.32 闷盖 (Blind Bearing Cover, Page 92)
    Material: HT150
    Outer D = 100 mm, flange thickness = 12 mm, total length = 28 mm.
    Spigot OD = 62 mm, length = 16 mm, tip chamfer C1.5.
    Internal cavity: D = 52 mm, depth = 16 mm.
    Right face shallow recess: D = 62 mm, depth = 2 mm.
    4 x Φ9 bolt holes on PCD Φ82.
    """
    profile = [
        (0.0, 31.0),
        (2.0, 31.0),
        (2.0, 50.0),
        (12.0, 50.0),
        (12.0, 31.0),
        (26.5, 31.0),
        (28.0, 29.5),
        (28.0, 26.0),
        (12.0, 26.0),
        (12.0, 0.0),
        (0.0, 0.0),
    ]
    obj = build_revolved_body(profile, segments=64, axis='Z')
    
    # 4 x Φ9 holes on PCD Φ82
    for angle in [0, 90, 180, 270]:
        rad = math.radians(angle)
        x = 41.0 * math.cos(rad)
        y = 41.0 * math.sin(rad)
        drill_cylinder_hole(obj, radius=4.5, depth=40.0, location=(x, y, 6.0))
        
    obj.name = "LJT04.32_闷盖"
    return obj, "cast_iron"

# ==============================================================================
# 2. LJT04.33: 透盖 (Open Bearing Cover)
# ==============================================================================

def generate_ljt04_33():
    """
    LJT04.33 透盖 (Open Bearing Cover, Page 93)
    Material: HT150
    Outer D = 120 mm, total thickness = 18 mm.
    Flange thickness = 13 mm, right spigot D = 80 mm, length = 5 mm.
    Central bore D = 35 mm through.
    Right face recess D = 68 mm, depth = 5 mm.
    Felt seal groove: D = 48 mm, width = 4 mm.
    6 x counterbored holes on PCD Φ98: Φ9 through, counterbore Φ16 depth 6 mm.
    """
    profile = [
        (0.0, 17.5),
        (6.0, 17.5),
        (6.0, 24.0),
        (10.0, 24.0),
        (10.0, 17.5),
        (18.0, 17.5),
        (18.0, 34.0),
        (13.0, 34.0),
        (13.0, 40.0),
        (18.0, 40.0),
        (18.0, 60.0),
        (0.0, 60.0),
        (0.0, 17.5),
    ]
    obj = build_revolved_body(profile, segments=64, axis='Z')
    
    # 6 x Φ9 holes with Φ16 counterbores on PCD Φ98
    for i in range(6):
        angle = math.radians(i * 60.0 + 30.0)
        x = 49.0 * math.cos(angle)
        y = 49.0 * math.sin(angle)
        drill_cylinder_hole(obj, radius=4.5, depth=40.0, location=(x, y, 9.0))
        drill_cylinder_hole(obj, radius=8.0, depth=12.0, location=(x, y, 3.0))
        
    obj.name = "LJT04.33_透盖"
    return obj, "cast_iron"

# ==============================================================================
# 3. LJT04.34: 填料压盖 (Packing Gland)
# ==============================================================================

def generate_ljt04_34():
    """
    LJT04.34 填料压盖 (Packing Gland, Page 94)
    Material: HT150
    Diamond flange: center circle Φ44, ear centers distance = 70 mm, ear R12.
    Flange thickness = 15 mm.
    Central sleeve: OD = Φ34, total length = 40 mm, tip 30° chamfer (width 2 mm).
    Central bore: Φ22 through.
    2 x Φ12 mounting holes at (0, ±35).
    """
    # Build diamond flange
    bm = bmesh.new()
    pts = []
    # Right tangent connecting ear (0, 35) to center (0, 0)
    segs = 16
    # Upper ear (0, 35), radius 12
    for i in range(segs + 1):
        th = -math.pi / 4.0 + (3.0 * math.pi / 2.0) * i / segs
        x = 12.0 * math.cos(th)
        y = 35.0 + 12.0 * math.sin(th)
        pts.append((x, y))
    # Lower ear (0, -35), radius 12
    for i in range(segs + 1):
        th = 3.0 * math.pi / 4.0 + (3.0 * math.pi / 2.0) * i / segs
        x = 12.0 * math.cos(th)
        y = -35.0 + 12.0 * math.sin(th)
        pts.append((x, y))
        
    v_bot = [bm.verts.new((x, y, 0.0)) for x, y in pts]
    v_top = [bm.verts.new((x, y, 15.0)) for x, y in pts]
    bm.verts.ensure_lookup_table()
    n = len(pts)
    for i in range(n):
        nxt = (i + 1) % n
        bm.faces.new((v_bot[i], v_bot[nxt], v_top[nxt], v_top[i]))
    bm.faces.new(reversed(v_bot))
    bm.faces.new(v_top)
    mesh = bpy.data.meshes.new("GlandFlangeMesh")
    bm.to_mesh(mesh)
    bm.free()
    flange_obj = bpy.data.objects.new("GlandFlange", mesh)
    bpy.context.collection.objects.link(flange_obj)
    
    # Central sleeve boss: OD 34, from Z=15 to Z=40, with tip chamfer
    sleeve_prof = [
        (15.0, 11.0),
        (38.0, 11.0),
        (40.0, 13.0),
        (40.0, 15.0),
        (38.0, 17.0),
        (15.0, 17.0),
        (15.0, 11.0),
    ]
    sleeve_obj = build_revolved_body(sleeve_prof, segments=48, axis='Z')
    apply_boolean_union(flange_obj, sleeve_obj)
    
    # Drill central bore Φ22 through
    drill_cylinder_hole(flange_obj, radius=11.0, depth=60.0, location=(0, 0, 20.0))
    # Drill 2 x Φ12 mounting holes
    drill_cylinder_hole(flange_obj, radius=6.0, depth=30.0, location=(0, 35.0, 7.5))
    drill_cylinder_hole(flange_obj, radius=6.0, depth=30.0, location=(0, -35.0, 7.5))
    
    flange_obj.name = "LJT04.34_填料压盖"
    return flange_obj, "cast_iron"

# ==============================================================================
# 4. LJT04.35: 阀盖 (Valve Bonnet)
# ==============================================================================

def generate_ljt04_35():
    """
    LJT04.35 阀盖 (Valve Bonnet, Page 95)
    Material: Q235A (machined steel)
    Square flange 94 x 94 mm with 4 ear corners (pitch 70 x 70, R12, side arcs Φ94).
    Thickness = 12 mm, total length = 42 mm.
    Front hex boss across-flats S = 65 mm (length 17 mm, neck R4).
    Internal thread G 1 1/2 (bore ~Φ44, thread relief Φ50).
    Back spigot recess Φ80 depth 4, counterbore Φ52 depth 7, through bore Φ40.
    4 x M10 threaded holes at (±35, ±35).
    """
    # Flange with corner ears and curved sides
    flange_obj = create_rounded_box(94.0, 94.0, 12.0, radius=12.0, z_start=0.0)
    
    # Hexagonal boss: S=65 -> R = 65 / (sqrt(3)) = 37.527 mm
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=6, radius=37.53, depth=30.0,
        location=(0, 0, 27.0)
    )
    hex_obj = bpy.context.active_object
    apply_boolean_union(flange_obj, hex_obj)
    
    # Undercut groove at transition (Z=12 to 16 mm): R4 neck
    bpy.ops.mesh.primitive_cylinder_add(
        radius=39.0, depth=4.0, vertices=48, location=(0, 0, 14.0)
    )
    neck_cut = bpy.context.active_object
    bpy.ops.mesh.primitive_cylinder_add(
        radius=32.0, depth=6.0, vertices=48, location=(0, 0, 14.0)
    )
    neck_keep = bpy.context.active_object
    apply_boolean_difference(neck_cut, neck_keep)
    apply_boolean_difference(flange_obj, neck_cut)
    
    # Back spigot recess Φ80 depth 4
    drill_cylinder_hole(flange_obj, radius=40.0, depth=8.0, location=(0, 0, 2.0))
    # Counterbore Φ52 depth 7
    drill_cylinder_hole(flange_obj, radius=26.0, depth=14.0, location=(0, 0, 3.5))
    # Central through bore Φ40
    drill_cylinder_hole(flange_obj, radius=20.0, depth=100.0, location=(0, 0, 21.0))
    # Internal thread G 1 1/2: bore ~Φ45 from Z=22 to 43
    drill_cylinder_hole(flange_obj, radius=22.5, depth=24.0, location=(0, 0, 32.0))
    # Thread relief groove Φ50 width 5 at Z=20
    drill_cylinder_hole(flange_obj, radius=25.0, depth=5.0, location=(0, 0, 20.0))
    
    # 4 x M10 holes at (±35, ±35)
    for cx in [-35.0, 35.0]:
        for cy in [-35.0, 35.0]:
            drill_cylinder_hole(flange_obj, radius=4.25, depth=30.0, location=(cx, cy, 6.0))
            
    flange_obj.name = "LJT04.35_阀盖"
    return flange_obj, "machined_steel"

# ==============================================================================
# 5. LJT04.36: 轴承盖 (Bearing Cover)
# ==============================================================================

def generate_ljt04_36():
    """
    LJT04.36 轴承盖 (Bearing Cover, Page 96)
    Material: HT200
    Outer rim OD = Φ142, thickness = 18 mm.
    Central hub: OD = Φ80, bore = Φ60, total length = 40 mm.
    Back recess: Φ128 depth 10 mm.
    6 mounting ears on PCD Φ160, ear R12, 6 x Φ9 EQS, counterbore Φ18 depth 2.
    6 radial ribs: thickness 8 mm, web recess depth 20 mm.
    """
    # Outer ring + central hub + web base
    main_prof = [
        (0.0, 30.0),
        (40.0, 30.0),
        (40.0, 40.0),
        (20.0, 40.0),
        (20.0, 64.0),
        (18.0, 71.0),
        (0.0, 71.0),
        (0.0, 64.0),
        (10.0, 64.0),
        (10.0, 30.0),
        (0.0, 30.0),
    ]
    obj = build_revolved_body(main_prof, segments=64, axis='Z')
    
    # 6 mounting ears on PCD Φ160: outer R12 cylinders
    for i in range(6):
        th = math.radians(i * 60.0)
        ex = 80.0 * math.cos(th)
        ey = 80.0 * math.sin(th)
        bpy.ops.mesh.primitive_cylinder_add(
            radius=12.0, depth=18.0, vertices=32, location=(ex, ey, 9.0)
        )
        ear = bpy.context.active_object
        apply_boolean_union(obj, ear)
        
    # 6 radial stiffening ribs: 8 mm thick, from R40 to R64, height from Z=20 to 38
    for i in range(6):
        th = math.radians(i * 60.0 + 30.0)
        bpy.ops.mesh.primitive_cube_add(
            size=1.0, location=(52.0 * math.cos(th), 52.0 * math.sin(th), 29.0)
        )
        rib = bpy.context.active_object
        rib.scale = (24.0, 8.0, 18.0)
        rib.rotation_euler = (0, 0, th)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        apply_boolean_union(obj, rib)
        
    # 6 x Φ9 bolt holes on PCD Φ160 with Φ18 x 2 counterbore
    for i in range(6):
        th = math.radians(i * 60.0)
        hx = 80.0 * math.cos(th)
        hy = 80.0 * math.sin(th)
        drill_cylinder_hole(obj, radius=4.5, depth=40.0, location=(hx, hy, 9.0))
        drill_cylinder_hole(obj, radius=9.0, depth=4.0, location=(hx, hy, 17.0))
        
    obj.name = "LJT04.36_轴承盖"
    return obj, "cast_iron"

# ==============================================================================
# 6. LJT04.37: 端盖 (End Cover)
# ==============================================================================

def generate_ljt04_37():
    """
    LJT04.37 端盖 (End Cover, Page 97)
    Material: HT200
    Total length = 56 mm.
    Main flange: OD = Φ144, from Z=8 to Z=32 (thickness 24 mm).
    Right spigot: OD = Φ86, length = 8 mm (Z=0 to 8).
    Left boss: OD = Φ84, length = 24 mm (Z=32 to 56), C1.6 chamfer.
    Central bore: Φ26 through. Left counterbore Φ48 depth 15. Right counterbore Φ56 depth 6.
    6 x counterbored holes on PCD Φ114: Φ9 through, counterbore Φ15 depth 9 mm.
    3 x M8 holes on left face on PCD Φ66.
    Radial tapped oil port: Rc 1/4 at Z=40 mm.
    """
    profile = [
        (0.0, 28.0),
        (6.0, 28.0),
        (6.0, 13.0),
        (41.0, 13.0),
        (41.0, 24.0),
        (56.0, 24.0),
        (56.0, 40.4),
        (54.4, 42.0),
        (32.0, 42.0),
        (32.0, 72.0),
        (8.0, 72.0),
        (8.0, 43.0),
        (0.0, 43.0),
        (0.0, 28.0),
    ]
    obj = build_revolved_body(profile, segments=64, axis='Z')
    
    # 6 x Φ9 holes with Φ15 counterbores on PCD Φ114
    for i in range(6):
        th = math.radians(i * 60.0)
        hx = 57.0 * math.cos(th)
        hy = 57.0 * math.sin(th)
        drill_cylinder_hole(obj, radius=4.5, depth=60.0, location=(hx, hy, 20.0))
        drill_cylinder_hole(obj, radius=7.5, depth=18.0, location=(hx, hy, 27.5))
        
    # 3 x M8 holes on left face (Z=56) on PCD Φ66
    for i in range(3):
        th = math.radians(i * 120.0 + 30.0)
        bx = 33.0 * math.cos(th)
        by = 33.0 * math.sin(th)
        drill_cylinder_hole(obj, radius=3.4, depth=20.0, location=(bx, by, 48.0))
        
    # 1 radial oil port: Rc 1/4 at Z=40 mm (drilled from Y=+72 down to center)
    drill_cylinder_hole(obj, radius=5.7, depth=50.0, location=(0, 45.0, 40.0), rotation=(math.radians(90), 0, 0))
    
    obj.name = "LJT04.37_端盖"
    return obj, "cast_iron"

# ==============================================================================
# 7. LJT04.38: 端盖 (End Cover)
# ==============================================================================

def generate_ljt04_38():
    """
    LJT04.38 端盖 (End Cover, Page 98)
    Material: HT150
    115 x 115 mm square flange, thickness = 15 mm.
    3 corners R27.5, bottom edge has arc cutout R33 centered at X=10, Y=-27.5.
    Front spigot boss: OD = Φ75, height = 7 mm.
    Back cylindrical hub: OD = Φ60, total length = 58 mm.
    Central bore: Φ25 through, middle relief cavity Φ30.
    4 x Φ9 holes on PCD Φ110 at 45° angles.
    Radial oil hole: Φ14 counterbore, Φ4 drill into cavity.
    """
    # Flange plate
    flange_obj = create_rounded_box(115.0, 115.0, 15.0, radius=27.5, z_start=7.0)
    
    # Bottom cutout arc R33 centered at (10, -27.5)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=33.0, depth=30.0, vertices=48, location=(10.0, -27.5, 14.0)
    )
    cutout = bpy.context.active_object
    apply_boolean_difference(flange_obj, cutout)
    
    # Front spigot boss: OD Φ75, from Z=0 to Z=7 mm
    bpy.ops.mesh.primitive_cylinder_add(
        radius=37.5, depth=7.0, vertices=48, location=(0, 0, 3.5)
    )
    front_boss = bpy.context.active_object
    apply_boolean_union(flange_obj, front_boss)
    
    # Back hub: OD Φ60, from Z=22 to Z=58 mm (length 36 mm)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=30.0, depth=36.0, vertices=48, location=(0, 0, 40.0)
    )
    back_hub = bpy.context.active_object
    apply_boolean_union(flange_obj, back_hub)
    
    # Central bore Φ25 through (Z=0 to 58)
    drill_cylinder_hole(flange_obj, radius=12.5, depth=80.0, location=(0, 0, 29.0))
    # Middle cavity Φ30 (Z=17 to 48)
    drill_cylinder_hole(flange_obj, radius=15.0, depth=31.0, location=(0, 0, 32.5))
    
    # 4 x Φ9 mounting holes on PCD Φ110 at 45°
    for th in [math.pi/4, 3*math.pi/4, 5*math.pi/4, 7*math.pi/4]:
        hx = 55.0 * math.cos(th)
        hy = 55.0 * math.sin(th)
        drill_cylinder_hole(flange_obj, radius=4.5, depth=30.0, location=(hx, hy, 14.5))
        
    # Top radial oil hole: Φ14 counterbore depth 12, Φ4 through to center
    drill_cylinder_hole(flange_obj, radius=7.0, depth=15.0, location=(0, 25.0, 38.0), rotation=(math.radians(90), 0, 0))
    drill_cylinder_hole(flange_obj, radius=2.0, depth=35.0, location=(0, 15.0, 38.0), rotation=(math.radians(90), 0, 0))
    
    flange_obj.name = "LJT04.38_端盖"
    return flange_obj, "cast_iron"

# ==============================================================================
# 8. LJT04.39: 端盖 (Domed End Cover)
# ==============================================================================

def generate_ljt04_39():
    """
    LJT04.39 端盖 (Domed End Cover, Page 99)
    Material: HT300
    Spherical domed shell: R90 inner, R95 outer, opening Φ164, total depth = 64 mm.
    Mounting flange rim: thickness 8 mm, 6 ears on PCD Φ190, ear R12, 6 x Φ8 holes.
    Central hub: OD Φ44, bore Φ26, counterbore Φ34 depth 17 mm.
    Top vertical bracket rib: width 16 mm, height 70 mm, Φ8 hole.
    Bottom oil sight pocket: length 42 mm, depth 56 mm.
    """
    # Build domed shell + outer flange by revolution
    # Arc profile from theta = 0 to theta ~ 60 deg
    segs = 24
    r_in = 90.0
    r_out = 95.0
    # Dome center at (0, 0, 64.0 - r_out) = (0, 0, -31.0)
    # Flange face at Z = 0.0, crown at Z = 64.0
    # Revolve profile around Z-axis
    profile = []
    # Inner arc from opening R82 to center
    for i in range(segs + 1):
        # r goes from 22.0 (hub) to 82.0 (opening)
        r = 22.0 + (82.0 - 22.0) * i / segs
        # z on sphere: z = z_center + sqrt(R^2 - r^2)
        # to ensure crown at Z=55: z = 55.0 - (r_in - math.sqrt(max(0.0, r_in**2 - r**2)))
        z = 55.0 - (r_in - math.sqrt(max(0.0, r_in**2 - r**2)))
        profile.append((z, r))
    # Flange rim: at z=0, r goes from 82 to 95, then flange thickness 8 mm to R102
    profile.append((0.0, 82.0))
    profile.append((0.0, 102.0))
    profile.append((8.0, 102.0))
    # Outer arc back from R95 to R22
    for i in range(segs, -1, -1):
        r = 22.0 + (95.0 - 22.0) * i / segs
        z = 60.0 - (r_out - math.sqrt(max(0.0, r_out**2 - r**2)))
        profile.append((z, r))
    # Central hub: OD Φ44 (R22), from Z=60 to 64 mm
    profile.append((64.0, 22.0))
    profile.append((64.0, 13.0))
    profile.append((47.0, 13.0))
    profile.append((47.0, 17.0))
    profile.append((38.0, 17.0))
    
    obj = build_revolved_body(profile, segments=64, axis='Z')
    
    # 6 ear lugs on PCD Φ190: R12 cylinders
    for i in range(6):
        th = math.radians(i * 60.0)
        ex = 95.0 * math.cos(th)
        ey = 95.0 * math.sin(th)
        bpy.ops.mesh.primitive_cylinder_add(
            radius=12.0, depth=8.0, vertices=32, location=(ex, ey, 4.0)
        )
        ear = bpy.context.active_object
        apply_boolean_union(obj, ear)
        
    # 6 x Φ8 holes on PCD Φ190 with Φ14 counterbores
    for i in range(6):
        th = math.radians(i * 60.0)
        hx = 95.0 * math.cos(th)
        hy = 95.0 * math.sin(th)
        drill_cylinder_hole(obj, radius=4.0, depth=20.0, location=(hx, hy, 4.0))
        drill_cylinder_hole(obj, radius=7.0, depth=4.0, location=(hx, hy, 7.0))
        
    # Top vertical rib: width 16 mm, extending to Y=70 mm, height from dome to Z=55
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, 45.0, 45.0)
    )
    rib = bpy.context.active_object
    rib.scale = (16.0, 35.0, 24.0)
    apply_boolean_union(obj, rib)
    # Drill cross hole Φ8 through top rib
    drill_cylinder_hole(obj, radius=4.0, depth=30.0, location=(0, 50.0, 52.0), rotation=(0, math.radians(90), 0))
    
    # Bottom oil pocket: width 16 mm, length 42 mm, depth 56 mm
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, -25.0, 28.0)
    )
    pocket = bpy.context.active_object
    pocket.scale = (16.0, 24.0, 48.0)
    apply_boolean_union(obj, pocket)
    
    obj.name = "LJT04.39_端盖"
    return obj, "cast_iron"

# ==============================================================================
# 9. LJT04.40: 泵盖 (Pump Cover)
# ==============================================================================

def generate_ljt04_40():
    """
    LJT04.40 泵盖 (Pump Cover, Page 100)
    Material: HT200
    Main flange: circular profile R32, top flat at Y=27.5, width 55 mm.
    Thickness = 5 mm, back recess depth = 2 mm.
    3 ear lugs: R7 with Φ7 holes (two at +30° above horizontal, one at -90°).
    2 dowel holes: 2 x Φ5.
    Central sleeve boss: OD Φ26, bore Φ18, height = 8 mm (total length 13 mm).
    """
    # Main circular body
    bpy.ops.mesh.primitive_cylinder_add(
        radius=32.0, depth=5.0, vertices=48, location=(0, 0, 2.5)
    )
    obj = bpy.context.active_object
    
    # 3 ear lugs: R7 cylinders at radius 32 mm
    # Angles: 30°, 150°, 270° (-90°)
    for deg in [30.0, 150.0, 270.0]:
        th = math.radians(deg)
        ex = 32.0 * math.cos(th)
        ey = 32.0 * math.sin(th)
        bpy.ops.mesh.primitive_cylinder_add(
            radius=7.0, depth=5.0, vertices=32, location=(ex, ey, 2.5)
        )
        ear = bpy.context.active_object
        apply_boolean_union(obj, ear)
        
    # Cut top flat at Y=27.5: cutter above Y=27.5
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, 45.0, 2.5)
    )
    cutter = bpy.context.active_object
    cutter.scale = (100.0, 35.0, 10.0)
    apply_boolean_difference(obj, cutter)
    
    # Central sleeve boss: OD Φ26, length 13 mm (Z=0 to 13 mm)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=13.0, depth=8.0, vertices=48, location=(0, 0, 9.0)
    )
    boss = bpy.context.active_object
    apply_boolean_union(obj, boss)
    
    # Central bore Φ18 through (Z=0 to 13 mm)
    drill_cylinder_hole(obj, radius=9.0, depth=30.0, location=(0, 0, 6.5))
    
    # Back face recess: depth 2 mm, radius 25 mm
    drill_cylinder_hole(obj, radius=25.0, depth=4.0, location=(0, 0, 1.0))
    
    # 3 x Φ7 mounting holes in ears
    for deg in [30.0, 150.0, 270.0]:
        th = math.radians(deg)
        hx = 32.0 * math.cos(th)
        hy = 32.0 * math.sin(th)
        drill_cylinder_hole(obj, radius=3.5, depth=20.0, location=(hx, hy, 2.5))
        
    # 2 dowel holes: 2 x Φ5 at Y=3.5 mm, X=±27.5 mm
    drill_cylinder_hole(obj, radius=2.5, depth=20.0, location=(27.5, 3.5, 2.5))
    drill_cylinder_hole(obj, radius=2.5, depth=20.0, location=(-27.5, 3.5, 2.5))
    
    obj.name = "LJT04.40_泵盖"
    return obj, "cast_iron"

# ==============================================================================
# 10. LJT04.41: 泵盖 (Pump Cover)
# ==============================================================================

def generate_ljt04_41():
    """
    LJT04.41 泵盖 (Pump Cover, Page 101)
    Material: HT200
    Circular flange OD Φ100, thickness = 10 mm.
    Rear tapered hub: OD Φ38 at tip, total length = 43 mm.
    Eccentric bore: Φ21 through, center offset Y = +18 mm.
    Front face: 4 x Φ11 bolt holes with Φ20 spotfaces.
    Crescent/obround relief slot: width 10 mm, length 20 mm, depth 4 mm at Y = -20 mm.
    Inclined oil passage: Φ3 at 60° into bore.
    """
    # Flange OD 100, thickness 10 (Z=0 to 10)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=50.0, depth=10.0, vertices=64, location=(0, 0, 5.0)
    )
    obj = bpy.context.active_object
    
    # Rear hub: tapered cylinder from Z=10 to Z=43 (centered at (0, 18))
    bpy.ops.mesh.primitive_cylinder_add(
        radius=19.0, depth=33.0, vertices=48, location=(0, 18.0, 26.5)
    )
    hub = bpy.context.active_object
    apply_boolean_union(obj, hub)
    
    # Eccentric bore Φ21 through at (0, 18)
    drill_cylinder_hole(obj, radius=10.5, depth=70.0, location=(0, 18.0, 21.5))
    
    # 4 x Φ11 bolt holes with Φ20 spotfaces on front face (Z=0)
    coords = [(31.0, 28.0), (-31.0, 28.0), (42.0, -28.0), (-42.0, -28.0)]
    for bx, by in coords:
        drill_cylinder_hole(obj, radius=5.5, depth=30.0, location=(bx, by, 5.0))
        drill_cylinder_hole(obj, radius=10.0, depth=4.0, location=(bx, by, 2.0))
        
    # Relief slot: obround width 10, length 20, depth 4 at Y=-20 mm
    slot_cutter = create_stadium_prism(length_between_centers=10.0, radius=5.0, height=8.0, z_start=-2.0)
    slot_cutter.location = (0, -20.0, 0.0)
    slot_cutter.rotation_euler = (0, 0, math.radians(90))
    apply_boolean_difference(obj, slot_cutter)
    
    # 2 dowel holes: Φ4 at (X=±18, Y=-18)
    drill_cylinder_hole(obj, radius=2.0, depth=15.0, location=(38.0, 0.0, 5.0))
    drill_cylinder_hole(obj, radius=2.0, depth=15.0, location=(-38.0, 10.0, 5.0))
    
    obj.name = "LJT04.41_泵盖"
    return obj, "cast_iron"

# ==============================================================================
# 11. LJT04.42: 体盖 (Body Cover)
# ==============================================================================

def generate_ljt04_42():
    """
    LJT04.42 体盖 (Body Cover, Page 102)
    Material: HT150
    Large domed casing cover:
    Rim OD = Φ302, opening = Φ294, rim thickness = 12 mm, depth = 36 mm.
    4 ear lugs on PCD Φ342, ear R15, 4 x Φ10.5 holes.
    Central hub: OD Φ89 x length 20 mm, step Φ50 x length 12 mm, total height = 98 mm.
    Center bore Φ26 through, inner cavity Φ64 x 40 mm.
    4 diagonal ribs: 6 mm thickness.
    """
    # Revolved main body (outer shell + rim + central hub)
    profile = [
        (0.0, 13.0),
        (58.0, 13.0),
        (58.0, 32.0),
        (98.0, 32.0),
        (98.0, 25.0),
        (86.0, 25.0),
        (86.0, 44.5),
        (66.0, 44.5),
        (66.0, 72.5),
        (36.0, 147.0),
        (36.0, 151.0),
        (24.0, 151.0),
        (24.0, 160.0),
        (12.0, 160.0),
        (12.0, 151.0),
        (0.0, 151.0),
        (0.0, 147.0),
        (28.0, 147.0),
        (50.0, 72.5),
        (50.0, 32.0),
        (0.0, 32.0),
        (0.0, 13.0),
    ]
    obj = build_revolved_body(profile, segments=64, axis='Z')
    
    # 4 mounting ears on PCD Φ342: R15 cylinders
    for i in range(4):
        th = math.radians(i * 90.0 + 45.0)
        ex = 171.0 * math.cos(th)
        ey = 171.0 * math.sin(th)
        bpy.ops.mesh.primitive_cylinder_add(
            radius=15.0, depth=12.0, vertices=32, location=(ex, ey, 18.0)
        )
        ear = bpy.context.active_object
        apply_boolean_union(obj, ear)
        
    # 4 diagonal ribs: 6 mm thick, connecting hub to shell
    for i in range(4):
        th = math.radians(i * 90.0 + 45.0)
        bpy.ops.mesh.primitive_cube_add(
            size=1.0, location=(90.0 * math.cos(th), 90.0 * math.sin(th), 60.0)
        )
        rib = bpy.context.active_object
        rib.scale = (80.0, 6.0, 30.0)
        rib.rotation_euler = (0, math.radians(-25), th)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        apply_boolean_union(obj, rib)
        
    # 4 x Φ10.5 bolt holes in ears
    for i in range(4):
        th = math.radians(i * 90.0 + 45.0)
        hx = 171.0 * math.cos(th)
        hy = 171.0 * math.sin(th)
        drill_cylinder_hole(obj, radius=5.25, depth=30.0, location=(hx, hy, 18.0))
        
    # Arc window slots around hub
    for th in [math.radians(0), math.radians(180)]:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=55.0, depth=40.0, vertices=32,
            location=(0, 0, 50.0)
        )
        cut = bpy.context.active_object
        drill_cylinder_hole(obj, radius=8.0, depth=40.0, location=(55.0 * math.cos(th), 55.0 * math.sin(th), 50.0))
        bpy.data.objects.remove(cut, do_unlink=True)
        
    obj.name = "LJT04.42_体盖"
    return obj, "cast_iron"

# ==============================================================================
# 12. LJT04.43: 箱盖 (Gearbox Cover)
# ==============================================================================

def generate_ljt04_43():
    """
    LJT04.43 箱盖 (Gearbox Cover, Page 103)
    Material: HT150
    Rectangular cover 104 x 116 mm, flange thickness = 8 mm.
    Bottom lip 7 mm, cavity recess depth 3 mm.
    4 corner bolt bosses: pitch 90 x 102 mm, holes Φ6.5 counterbore Φ11 depth 5 mm.
    Raised inspection window pad: 40 x 60 mm, height 10 mm (protrudes 2 mm),
    with cutout 20 x 40 mm, 4 x M4 holes on 30 x 50 mm pitch.
    """
    # Main base plate
    obj = create_rounded_box(104.0, 116.0, 8.0, radius=7.0, z_start=0.0)
    
    # Bottom cavity recess: 90 x 102 mm, depth 3 mm (Z=0 to 3)
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, 0, 1.5)
    )
    cavity = bpy.context.active_object
    cavity.scale = (90.0, 102.0, 3.2)
    apply_boolean_difference(obj, cavity)
    
    # Raised window pad on left: 40 x 60 mm, Z=8 to 10 mm
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(-25.0, 0, 9.0)
    )
    pad = bpy.context.active_object
    pad.scale = (40.0, 60.0, 2.0)
    apply_boolean_union(obj, pad)
    
    # Window cutout 20 x 40 mm through
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(-25.0, 0, 5.0)
    )
    cutout = bpy.context.active_object
    cutout.scale = (20.0, 40.0, 15.0)
    apply_boolean_difference(obj, cutout)
    
    # 4 x M4 holes on window pad (pitch 30 x 50 mm, centered at (-25, 0))
    for dx in [-15.0, 15.0]:
        for dy in [-25.0, 25.0]:
            drill_cylinder_hole(obj, radius=1.7, depth=12.0, location=(-25.0 + dx, dy, 7.0))
            
    # 4 corner mounting holes: pitch 90 x 102 mm, Φ6.5 through, Φ11 counterbore depth 5 mm
    for cx in [-45.0, 45.0]:
        for cy in [-51.0, 51.0]:
            drill_cylinder_hole(obj, radius=3.25, depth=20.0, location=(cx, cy, 4.0))
            drill_cylinder_hole(obj, radius=5.5, depth=10.0, location=(cx, cy, 5.5))
            
    obj.name = "LJT04.43_箱盖"
    return obj, "cast_iron"

# ==============================================================================
# 13. LJT04.44: 左箱盖 (Left Gearbox Cover)
# ==============================================================================

def generate_ljt04_44():
    """
    LJT04.44 左箱盖 (Left Gearbox Cover, Page 104)
    Material: ZL102 (machined steel / aluminum)
    Dual bore seats: large bore Φ42 at (0, 0), small bore Φ26 at (0, 40).
    Flange profile with top ear at Y=63, side ears at (±38.5, 20), bottom ears at (±27, -27).
    Flange thickness = 10 mm.
    Front face: 4 x M6 on 32 x 32 pitch around Φ42 bore.
    Back face: spigot OD Φ42, length 28 mm.
    """
    # Create contoured body from 2 blended cylinders
    bpy.ops.mesh.primitive_cylinder_add(
        radius=36.0, depth=10.0, vertices=48, location=(0, 0, 5.0)
    )
    obj = bpy.context.active_object
    
    bpy.ops.mesh.primitive_cylinder_add(
        radius=24.0, depth=10.0, vertices=48, location=(0, 40.0, 5.0)
    )
    top_cyl = bpy.context.active_object
    apply_boolean_union(obj, top_cyl)
    
    # Back spigot for large bore: OD Φ42, from Z=10 to Z=28
    bpy.ops.mesh.primitive_cylinder_add(
        radius=21.0, depth=18.0, vertices=48, location=(0, 0, 19.0)
    )
    spigot1 = bpy.context.active_object
    apply_boolean_union(obj, spigot1)
    
    # Back spigot for small bore: OD Φ26, from Z=10 to Z=20
    bpy.ops.mesh.primitive_cylinder_add(
        radius=13.0, depth=10.0, vertices=48, location=(0, 40.0, 15.0)
    )
    spigot2 = bpy.context.active_object
    apply_boolean_union(obj, spigot2)
    
    # Ears:
    ear_locs = [(0, 63.0), (38.5, 20.0), (-38.5, 20.0), (27.0, -27.0), (-27.0, -27.0)]
    for ex, ey in ear_locs:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=8.0, depth=10.0, vertices=32, location=(ex, ey, 5.0)
        )
        ear = bpy.context.active_object
        apply_boolean_union(obj, ear)
        
    # Large bore Φ42 through
    drill_cylinder_hole(obj, radius=21.0, depth=60.0, location=(0, 0, 15.0))
    # Small bore Φ26 through
    drill_cylinder_hole(obj, radius=13.0, depth=40.0, location=(0, 40.0, 15.0))
    
    # 4 x M6 holes around large bore (pitch 32 x 32)
    for dx in [-16.0, 16.0]:
        for dy in [-16.0, 16.0]:
            drill_cylinder_hole(obj, radius=2.5, depth=15.0, location=(dx, dy, 2.5))
            
    # 4 mounting holes in ears: Φ6.5
    for ex, ey in ear_locs[:4]:
        drill_cylinder_hole(obj, radius=3.25, depth=20.0, location=(ex, ey, 5.0))
    # 1 dowel hole: Φ8H7 in 5th ear
    drill_cylinder_hole(obj, radius=4.0, depth=20.0, location=(ear_locs[4][0], ear_locs[4][1], 5.0))
    
    obj.name = "LJT04.44_左箱盖"
    return obj, "machined_steel"

# ==============================================================================
# 14. LJT04.45: 阀盖 (Valve Cover)
# ==============================================================================

def generate_ljt04_45():
    """
    LJT04.45 阀盖 (Valve Cover, Page 105)
    Material: HT200
    Base flange: stadium shape 80 x 124 mm, thickness = 10 mm.
    Vertical column: OD Φ30, bore Φ15, height = 100 mm.
    Horizontal cylinder: OD Φ44 at height 52 mm, with spherical cap SR14.
    Side flange: 58 x 58 mm with 4 x M8 holes.
    Bottom cavity opening: 32 x 46 mm.
    6 x Φ8.5 mounting holes on base flange.
    """
    # Base flange: stadium shape
    obj = create_stadium_prism(length_between_centers=44.0, radius=40.0, height=10.0, z_start=0.0)
    
    # Vertical column: OD Φ30, height 100 mm
    bpy.ops.mesh.primitive_cylinder_add(
        radius=15.0, depth=100.0, vertices=48, location=(0, 0, 50.0)
    )
    col = bpy.context.active_object
    apply_boolean_union(obj, col)
    
    # Horizontal cylinder: OD Φ44, centered at Z=52, length 60 mm along X-axis
    bpy.ops.mesh.primitive_cylinder_add(
        radius=22.0, depth=50.0, vertices=48,
        location=(0, 0, 52.0), rotation=(0, math.radians(90), 0)
    )
    horiz_cyl = bpy.context.active_object
    apply_boolean_union(obj, horiz_cyl)
    
    # Spherical cap SR14 at left end (-25, 0, 52)
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=14.0, segments=32, ring_count=24, location=(-25.0, 0, 52.0)
    )
    sphere_cap = bpy.context.active_object
    apply_boolean_union(obj, sphere_cap)
    
    # Side flange at right end (25, 0, 52): 58 x 58 mm square flange, thickness 14 mm
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(25.0, 0, 52.0)
    )
    side_flg = bpy.context.active_object
    side_flg.scale = (14.0, 58.0, 58.0)
    apply_boolean_union(obj, side_flg)
    
    # Reinforcement slope/ramp from horizontal cylinder to base
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(-10.0, 0, 25.0)
    )
    ramp = bpy.context.active_object
    ramp.scale = (40.0, 44.0, 30.0)
    apply_boolean_union(obj, ramp)
    
    # Vertical bore Φ15 in column
    drill_cylinder_hole(obj, radius=7.5, depth=110.0, location=(0, 0, 50.0))
    # Horizontal bore Φ24 in side flange through to central column
    drill_cylinder_hole(obj, radius=12.0, depth=60.0, location=(15.0, 0, 52.0), rotation=(0, math.radians(90), 0))
    # Bottom cavity opening 32 x 46 mm
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, 0, 15.0)
    )
    bot_cut = bpy.context.active_object
    bot_cut.scale = (32.0, 46.0, 32.0)
    apply_boolean_difference(obj, bot_cut)
    
    # 4 x M8 holes in side flange (pitch 40 x 40)
    for dy in [-20.0, 20.0]:
        for dz in [-20.0, 20.0]:
            drill_cylinder_hole(obj, radius=3.4, depth=25.0, location=(25.0, dy, 52.0 + dz), rotation=(0, math.radians(90), 0))
            
    # 6 x Φ8.5 mounting holes in base flange
    flange_holes = [(0, 45.0), (0, -45.0), (25.0, 22.0), (-25.0, 22.0), (25.0, -22.0), (-25.0, -22.0)]
    for hx, hy in flange_holes:
        drill_cylinder_hole(obj, radius=4.25, depth=25.0, location=(hx, hy, 5.0))
        
    obj.name = "LJT04.45_阀盖"
    return obj, "cast_iron"

# ==============================================================================
# 15. LJT04.46: 泵盖 (Pump Cover)
# ==============================================================================

def generate_ljt04_46():
    """
    LJT04.46 泵盖 (Pump Cover, Page 106)
    Material: HT200
    Stadium flange 76 x 118 mm (ends R38, center pitch 42 mm), thickness = 10 mm.
    Front raised body: stadium shape 44 x 86 mm, height = 22 mm.
    Side pipe boss: width 34 mm with G3/8 internal pipe thread.
    Rear face: 2 blind bearing pockets Φ18 x depth 20 mm at Y = ±21 mm.
    6 x counterbored mounting holes: Φ7 through, counterbore Φ13 depth 3 mm.
    2 dowel pin holes: Φ5.
    """
    # Main stadium flange
    obj = create_stadium_prism(length_between_centers=42.0, radius=38.0, height=10.0, z_start=0.0)
    
    # Front raised body: stadium prism
    raised_body = create_stadium_prism(length_between_centers=42.0, radius=22.0, height=22.0, z_start=10.0)
    apply_boolean_union(obj, raised_body)
    
    # Side rectangular pipe boss: width 34 mm along Y, extending along X
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(28.0, 0, 21.0)
    )
    side_boss = bpy.context.active_object
    side_boss.scale = (20.0, 34.0, 22.0)
    apply_boolean_union(obj, side_boss)
    
    # G3/8 threaded port into side boss: Φ15 bore along X
    drill_cylinder_hole(obj, radius=7.5, depth=35.0, location=(28.0, 0, 21.0), rotation=(0, math.radians(90), 0))
    # Internal cross oil channel Φ10
    drill_cylinder_hole(obj, radius=5.0, depth=30.0, location=(18.0, 0, 21.0), rotation=(math.radians(90), 0, 0))
    
    # Rear face: 2 blind bearing pockets Φ18 x 20 mm at (0, ±21)
    drill_cylinder_hole(obj, radius=9.0, depth=20.0, location=(0, 21.0, 10.0))
    drill_cylinder_hole(obj, radius=9.0, depth=20.0, location=(0, -21.0, 10.0))
    
    # 6 mounting holes: Φ7 through with Φ13 counterbore depth 3 mm
    bolt_coords = [(0, 48.0), (0, -48.0), (28.0, 21.0), (-28.0, 21.0), (28.0, -21.0), (-28.0, -21.0)]
    for bx, by in bolt_coords:
        drill_cylinder_hole(obj, radius=3.5, depth=25.0, location=(bx, by, 5.0))
        drill_cylinder_hole(obj, radius=6.5, depth=6.0, location=(bx, by, 8.5))
        
    # 2 dowel holes: Φ5 at (X=±20, Y=0)
    drill_cylinder_hole(obj, radius=2.5, depth=20.0, location=(20.0, 0, 5.0))
    drill_cylinder_hole(obj, radius=2.5, depth=20.0, location=(-20.0, 0, 5.0))
    
    obj.name = "LJT04.46_泵盖"
    return obj, "cast_iron"

# ==============================================================================
# 16. LJT04.47: 前泵盖 (Front Pump Cover)
# ==============================================================================

def generate_ljt04_47():
    """
    LJT04.47 前泵盖 (Front Pump Cover, Page 107)
    Material: ZL107 (machined steel / aluminum)
    Rectangular plate 86 x 116 mm, corner radii R8, thickness = 18 mm.
    Front spigot boss: OD Φ45 step Φ38, protrusion = 3 mm.
    Central bore: stepped Φ30H7 depth 8, Φ20H7 through.
    Bolt holes: 4 x Φ9 on pitch 60 x 100 mm, 4 x Φ12.5 on pitch 60 x 60 mm.
    Back face grid ribs: pocket depth 12 mm, rib width 3 mm.
    """
    # Main rectangular plate
    obj = create_rounded_box(86.0, 116.0, 18.0, radius=8.0, z_start=0.0)
    
    # Front spigot boss: OD Φ45 x 3 mm (Z=18 to 21)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=22.5, depth=3.0, vertices=48, location=(0, 15.0, 19.5)
    )
    spigot = bpy.context.active_object
    apply_boolean_union(obj, spigot)
    
    # Central stepped bore at (0, 15): Φ30 depth 8 from Z=21, Φ20 through
    drill_cylinder_hole(obj, radius=15.0, depth=16.0, location=(0, 15.0, 17.0))
    drill_cylinder_hole(obj, radius=10.0, depth=35.0, location=(0, 15.0, 9.0))
    
    # 4 corner holes: Φ9 on pitch 60 x 100 mm
    for cx in [-30.0, 30.0]:
        for cy in [-50.0, 50.0]:
            drill_cylinder_hole(obj, radius=4.5, depth=30.0, location=(cx, cy, 9.0))
            
    # 4 secondary holes: Φ12.5 on pitch 60 x 60 mm
    for cx in [-30.0, 30.0]:
        for cy in [-30.0, 30.0]:
            drill_cylinder_hole(obj, radius=6.25, depth=30.0, location=(cx, cy + 15.0, 9.0))
            
    # Back face grid pockets: pocket depth 12 mm (leaving 6 mm plate)
    # 2 rows x 3 columns of rectangular pocket recesses
    for px in [-22.0, 22.0]:
        for py in [-35.0, -15.0, 35.0]:
            bpy.ops.mesh.primitive_cube_add(
                size=1.0, location=(px, py, 6.0)
            )
            pock = bpy.context.active_object
            pock.scale = (20.0, 16.0, 12.0)
            apply_boolean_difference(obj, pock)
            
    obj.name = "LJT04.47_前泵盖"
    return obj, "machined_steel"

# ==============================================================================
# 17. LJT04.48: 箱盖 (Gearbox Upper Cover)
# ==============================================================================

def generate_ljt04_48():
    """
    LJT04.48 箱盖 (Gearbox Upper Cover, Page 108)
    Material: HT200
    Reducer upper housing:
    Split face base flange: 230 x 100 mm, thickness = 7 mm.
    Two semi-cylindrical bearing seats:
      Shaft 1 (left): semi-cylindrical arch R35 (bore Φ70), step Φ62 / Φ41.
      Shaft 2 (right): semi-cylindrical arch R40 (bore Φ80), step Φ70 / Φ62.
      Center distance between shafts = 70 mm.
    Main arched hood: outer radius R70, wall thickness = 6 mm, total height = 67 mm.
    Top inspection window: raised pad 46 x 36 mm, height 2 mm, 4 x M3 holes.
    6 x mounting holes on flange: Φ9 with Φ17 spotface.
    4 stiffening ribs: 6 mm thickness.
    """
    # Base flange plate
    obj = create_rounded_box(230.0, 100.0, 7.0, radius=23.0, z_start=0.0)
    
    # Main arched hood: half cylinder along Y-axis, centered at X=0, radius R70, length 80 mm
    bpy.ops.mesh.primitive_cylinder_add(
        radius=70.0, depth=80.0, vertices=64,
        location=(0, 0, 7.0), rotation=(math.radians(90), 0, 0)
    )
    hood = bpy.context.active_object
    # Cut off bottom half below Z=7
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, 0, -35.0)
    )
    bot_half = bpy.context.active_object
    bot_half.scale = (200.0, 100.0, 70.0)
    apply_boolean_difference(hood, bot_half)
    apply_boolean_union(obj, hood)
    
    # Left bearing seat boss: arch R35, centered at X=-35 mm
    bpy.ops.mesh.primitive_cylinder_add(
        radius=35.0, depth=100.0, vertices=48,
        location=(-35.0, 0, 7.0), rotation=(math.radians(90), 0, 0)
    )
    b_seat1 = bpy.context.active_object
    apply_boolean_union(obj, b_seat1)
    
    # Right bearing seat boss: arch R40, centered at X=35 mm
    bpy.ops.mesh.primitive_cylinder_add(
        radius=40.0, depth=100.0, vertices=48,
        location=(35.0, 0, 7.0), rotation=(math.radians(90), 0, 0)
    )
    b_seat2 = bpy.context.active_object
    apply_boolean_union(obj, b_seat2)
    
    # Cut bottom split plane at Z=0
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, 0, -25.0)
    )
    split_plane = bpy.context.active_object
    split_plane.scale = (250.0, 120.0, 50.0)
    apply_boolean_difference(obj, split_plane)
    
    # Hollow inside cavity: arch radius R64 (wall thickness 6 mm)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=64.0, depth=72.0, vertices=64,
        location=(0, 0, 7.0), rotation=(math.radians(90), 0, 0)
    )
    inner_cav = bpy.context.active_object
    apply_boolean_difference(obj, inner_cav)
    
    # Left semi-bore Φ41 through at X=-35
    drill_cylinder_hole(obj, radius=20.5, depth=120.0, location=(-35.0, 0, 0.0), rotation=(math.radians(90), 0, 0))
    # Right semi-bore Φ62 through at X=35
    drill_cylinder_hole(obj, radius=31.0, depth=120.0, location=(35.0, 0, 0.0), rotation=(math.radians(90), 0, 0))
    
    # Top inspection pad: 46 x 36 mm at top crown (Z=67 mm)
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, 0, 68.0)
    )
    pad = bpy.context.active_object
    pad.scale = (46.0, 36.0, 4.0)
    apply_boolean_union(obj, pad)
    
    # Top window cutout: 30 x 24 mm through
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0, 0, 60.0)
    )
    win_cut = bpy.context.active_object
    win_cut.scale = (30.0, 24.0, 25.0)
    apply_boolean_difference(obj, win_cut)
    
    # 4 x M3 holes on inspection pad (pitch 36 x 28)
    for dx in [-18.0, 18.0]:
        for dy in [-14.0, 14.0]:
            drill_cylinder_hole(obj, radius=1.3, depth=10.0, location=(dx, dy, 68.0))
            
    # 6 x Φ9 mounting holes on split flange with Φ17 spotfaces
    flange_holes = [
        (-95.0, 0), (95.0, 0),
        (-35.0, 40.0), (-35.0, -40.0),
        (35.0, 40.0), (35.0, -40.0)
    ]
    for hx, hy in flange_holes:
        drill_cylinder_hole(obj, radius=4.5, depth=30.0, location=(hx, hy, 3.5))
        drill_cylinder_hole(obj, radius=8.5, depth=5.0, location=(hx, hy, 5.0))
        
    obj.name = "LJT04.48_箱盖"
    return obj, "cast_iron"

# ==============================================================================
# MAIN BATCH EXECUTION
# ==============================================================================

GENERATORS = [
    ("LJT04.32_闷盖", generate_ljt04_32),
    ("LJT04.33_透盖", generate_ljt04_33),
    ("LJT04.34_填料压盖", generate_ljt04_34),
    ("LJT04.35_阀盖", generate_ljt04_35),
    ("LJT04.36_轴承盖", generate_ljt04_36),
    ("LJT04.37_端盖", generate_ljt04_37),
    ("LJT04.38_端盖", generate_ljt04_38),
    ("LJT04.39_端盖", generate_ljt04_39),
    ("LJT04.40_泵盖", generate_ljt04_40),
    ("LJT04.41_泵盖", generate_ljt04_41),
    ("LJT04.42_体盖", generate_ljt04_42),
    ("LJT04.43_箱盖", generate_ljt04_43),
    ("LJT04.44_左箱盖", generate_ljt04_44),
    ("LJT04.45_阀盖", generate_ljt04_45),
    ("LJT04.46_泵盖", generate_ljt04_46),
    ("LJT04.47_前泵盖", generate_ljt04_47),
    ("LJT04.48_箱盖", generate_ljt04_48),
]

def run_batch():
    print(f"\n{'='*70}")
    print(f"STARTING CATEGORY 04 BATCH 3 GENERATION (17 PARTS: LJT04.32 ~ LJT04.48)")
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
