"""
Category 04 Batch 2: 轮盘盖类零件 (Discs, Flanges & Couplings)
Generates 15 models: LJT04.17 ~ LJT04.31
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
            print(f"Warning: Boolean modifier apply failed: {e}")
    bpy.data.objects.remove(cutter_obj, do_unlink=True)

def drill_cylinder_hole(target_obj, radius, depth, location, rotation=(0, 0, 0)):
    """Drills a cylindrical hole through target_obj using boolean difference."""
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius, depth=depth, vertices=32,
        location=location, rotation=rotation
    )
    cutter = bpy.context.active_object
    apply_boolean_difference(target_obj, cutter)

def add_standard_keyway(target_obj, bore_radius, key_width, key_depth, length, center_z=0.0):
    """Adds a standard keyway slot to a central cylindrical bore along Z-axis."""
    box_x = key_width
    box_y = key_depth + 2.0
    box_z = length + 2.0
    center_y = bore_radius + key_depth / 2.0 - 0.5
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(0.0, center_y, center_z)
    )
    cutter = bpy.context.active_object
    cutter.scale = (box_x, box_y, box_z)
    bpy.ops.object.transform_apply(scale=True)
    apply_boolean_difference(target_obj, cutter)

# ==============================================================================
# Model Generators: LJT04.17 ~ LJT04.31
# ==============================================================================

def make_LJT04_17():
    """LJT04.17 法兰盘 (Flange Plate)"""
    # Outer dia 120 (R=60), flange thickness 20 (Z: 18 to 38), total length 45 (Z: 0 to 45)
    # Left hub dia 70 (R=35, Z: 0 to 18), counterbore phi 60H11 (R=30, depth 21: Z 0 to 21)
    # Right shoulder dia 70k6 (R=35, Z: 38 to 45), bore phi 30H7 (R=15)
    profile = [
        (0.0, 30.0),
        (0.0, 35.0),
        (18.0, 35.0),
        (18.0, 60.0),
        (38.0, 60.0),
        (38.0, 35.0),
        (45.0, 35.0),
        (45.0, 15.0),
        (21.0, 15.0),
        (21.0, 30.0),
        (0.0, 30.0)
    ]
    obj = build_revolved_body(profile, segments=72, axis='Z')
    obj.name = "LJT04.17_法兰盘"
    
    # 3 bolt holes phi 11 counterbore phi 18 x 10 on PCD 95 (R=47.5)
    for i in range(3):
        ang = i * (2.0 * math.pi / 3.0) + math.pi / 6.0
        hx = 47.5 * math.cos(ang)
        hy = 47.5 * math.sin(ang)
        drill_cylinder_hole(obj, radius=5.5, depth=30.0, location=(hx, hy, 28.0))
        drill_cylinder_hole(obj, radius=9.0, depth=10.0, location=(hx, hy, 23.0))
        
    # Bottom clearance cutout: arc R30 at offset 50mm, 15°
    bpy.ops.mesh.primitive_cylinder_add(
        radius=30.0, depth=30.0, vertices=36,
        location=(50.0 * math.sin(math.radians(15.0)), -50.0 * math.cos(math.radians(15.0)), 28.0)
    )
    cutter = bpy.context.active_object
    apply_boolean_difference(obj, cutter)
    return obj

def make_LJT04_18():
    """LJT04.18 法兰盘 (Flange Plate with Flats)"""
    # Outer dia 130 (R=65) with two parallel flats width 100 (+/- 50 in X)
    # Flange thickness 12 (Z: 0 to 12), hub dia 55h6 (R=27.5, Z: 12 to 42)
    # Centering recess dia 70 (R=35, depth 3: Z 0 to 3), bore dia 42H7 (R=21)
    profile = [
        (0.0, 35.0),
        (0.0, 65.0),
        (12.0, 65.0),
        (12.0, 27.5),
        (42.0, 27.5),
        (42.0, 21.0),
        (3.0, 21.0),
        (3.0, 35.0),
        (0.0, 35.0)
    ]
    obj = build_revolved_body(profile, segments=72, axis='Z')
    obj.name = "LJT04.18_法兰盘"
    
    # Cut 2 parallel flats at X = +50 and X = -50
    for sign in [1, -1]:
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(sign * 65.0, 0.0, 6.0)
        )
        cutter = bpy.context.active_object
        cutter.scale = (30.0, 150.0, 20.0)
        bpy.ops.object.transform_apply(scale=True)
        apply_boolean_difference(obj, cutter)
        
    # 4 bolt holes phi 7 counterbore phi 12 x 5 on PCD 85 (R=42.5)
    for i in range(4):
        ang = i * (math.pi / 2.0) + math.pi / 4.0
        hx = 42.5 * math.cos(ang)
        hy = 42.5 * math.sin(ang)
        drill_cylinder_hole(obj, radius=3.5, depth=20.0, location=(hx, hy, 6.0))
        drill_cylinder_hole(obj, radius=6.0, depth=5.0, location=(hx, hy, 9.5))
        
    # 2 pin holes phi 5 on PCD 114 (R=57)
    drill_cylinder_hole(obj, radius=2.5, depth=20.0, location=(0.0, 57.0, 6.0))
    drill_cylinder_hole(obj, radius=2.5, depth=20.0, location=(0.0, -57.0, 6.0))
    
    # Radial M6 screw hole on hub at Z=28.5 (13.5 from hub end Z=42)
    drill_cylinder_hole(obj, radius=3.0, depth=30.0, location=(0.0, 25.0, 28.5), rotation=(math.pi/2, 0, 0))
    return obj

def make_LJT04_19():
    """LJT04.19 法兰盘 (Flange with Internal Thread & Snap Ring Groove)"""
    # Outer dia 120 (R=60), bottom straight cut at Y = -34.5
    # Flange Z: 37 to 47 (thickness 10). Left sleeve: dia 80h11 (R=40, Z: 0 to 37)
    # Right neck: dia 58g6 (R=29, Z: 47 to 60). Bore: phi 36 (R=18, Z: 40 to 60), phi 65 (Z: 0 to 40)
    profile = [
        (0.0, 32.5),
        (0.0, 40.0),
        (37.0, 40.0),
        (37.0, 60.0),
        (47.0, 60.0),
        (47.0, 29.0),
        (60.0, 29.0),
        (60.0, 18.0),
        (40.0, 18.0),
        (40.0, 32.5),
        (0.0, 32.5)
    ]
    obj = build_revolved_body(profile, segments=72, axis='Z')
    obj.name = "LJT04.19_法兰盘"
    
    # Bottom straight cut at Y = -34.5
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(0.0, -55.0, 42.0)
    )
    cutter = bpy.context.active_object
    cutter.scale = (150.0, 40.0, 25.0)
    bpy.ops.object.transform_apply(scale=True)
    apply_boolean_difference(obj, cutter)
    
    # 3 bolt holes phi 11 counterbore phi 16.5 x 5 on PCD 98 (R=49)
    for ang_deg in [90, 210, 330]:
        ang = math.radians(ang_deg)
        hx = 49.0 * math.cos(ang)
        hy = 49.0 * math.sin(ang)
        drill_cylinder_hole(obj, radius=5.5, depth=20.0, location=(hx, hy, 42.0))
        drill_cylinder_hole(obj, radius=8.25, depth=5.0, location=(hx, hy, 44.5))
        
    # Keyway on right bore phi 36: width 6, depth 3.3
    add_standard_keyway(obj, bore_radius=18.0, key_width=6.0, key_depth=3.3, length=30.0, center_z=50.0)
    return obj

def make_LJT04_20():
    """LJT04.20 法兰盘 (Flange Plate with Graduated Scale)"""
    # Outer dia 155k6 (R=77.5), thickness 36 (Z: 0 to 36)
    # Front cavity dia 135 (R=67.5) x depth 24 (Z: 12 to 36), inner shoulder dia 130
    profile = [
        (0.0, 0.0),
        (0.0, 77.5),
        (36.0, 77.5),
        (36.0, 67.5),
        (12.0, 67.5),
        (12.0, 0.0),
        (0.0, 0.0)
    ]
    obj = build_revolved_body(profile, segments=72, axis='Z')
    obj.name = "LJT04.20_法兰盘"
    
    # Center through hole phi 8
    drill_cylinder_hole(obj, radius=4.0, depth=45.0, location=(0.0, 0.0, 18.0))
    
    # Eccentric bore phi 30H10 (R=15) at Y = -57
    drill_cylinder_hole(obj, radius=15.0, depth=45.0, location=(0.0, -57.0, 18.0))
    
    # 5 mounting holes phi 8.5 counterbore phi 13 x 9 on PCD 130 (R=65)
    for i in range(5):
        ang = i * (2.0 * math.pi / 5.0) + 0.3
        hx = 65.0 * math.cos(ang)
        hy = 65.0 * math.sin(ang)
        drill_cylinder_hole(obj, radius=4.25, depth=45.0, location=(hx, hy, 18.0))
        drill_cylinder_hole(obj, radius=6.5, depth=9.0, location=(hx, hy, 4.5))
        
    # 2 x M8-7H on PCD 140
    for sign in [1, -1]:
        ang = math.radians(36.0) if sign == 1 else math.radians(144.0)
        hx = 70.0 * math.cos(ang)
        hy = 70.0 * math.sin(ang)
        drill_cylinder_hole(obj, radius=3.4, depth=20.0, location=(hx, hy, 6.0))
    return obj

def make_LJT04_21():
    """LJT04.21 拨盘 (Dial / Geneva Driver Wheel)"""
    # Outer dia 49 (R=24.5), flange thickness 4 (Z: 9 to 13), total 19 (Z: 0 to 19)
    # Left hub dia 16 (R=8, Z: 0 to 9), shoulder dia 29.4h7 (R=14.7, Z: 1.5 to 9), bore dia 10J7 (R=5)
    profile = [
        (0.0, 5.0),
        (0.0, 8.0),
        (1.5, 8.0),
        (1.5, 14.7),
        (9.0, 14.7),
        (9.0, 24.5),
        (13.0, 24.5),
        (13.0, 5.0),
        (0.0, 5.0)
    ]
    obj = build_revolved_body(profile, segments=48, axis='Z')
    obj.name = "LJT04.21_拨盘"
    
    # Geneva drive pin boss: cylinder phi 22 (R=11) at Y = 17.8, Z from 9 to 19 (height 10)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=11.0, depth=10.0, vertices=32,
        location=(0.0, 17.8, 14.0)
    )
    boss = bpy.context.active_object
    
    bpy.ops.object.select_all(action='DESELECT')
    boss.select_set(True)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.join()
    
    # Geneva pin hole phi 6.5H7 through boss
    drill_cylinder_hole(obj, radius=3.25, depth=25.0, location=(0.0, 17.8, 14.0))
    return obj

def make_LJT04_22():
    """LJT04.22 调节盘 (Adjusting Disc with Spherical Nose)"""
    # Outer dia 187 (R=93.5), flange thickness 10 (Z: 0 to 10), total length 46 (Z: 0 to 46)
    # Spherical nose SR30h6 at Z=32 to 46, hub dia 72 (R=36, Z: 10 to 32)
    # Stepped bore: phi 58 (0 to 4), phi 54 (4 to 17), phi 46 (17 to 32), phi 32 (32 to 46)
    profile = [
        (0.0, 29.0),
        (0.0, 93.5),
        (10.0, 93.5),
        (10.0, 36.0),
        (32.0, 36.0),
        (40.0, 30.0),
        (46.0, 20.0),
        (46.0, 16.0),
        (32.0, 16.0),
        (32.0, 23.0),
        (17.0, 23.0),
        (17.0, 27.0),
        (4.0, 27.0),
        (4.0, 29.0),
        (0.0, 29.0)
    ]
    obj = build_revolved_body(profile, segments=72, axis='Z')
    obj.name = "LJT04.22_调节盘"
    
    # 4 bolt holes phi 11 EQS on PCD 170 (R=85)
    for i in range(4):
        ang = i * (math.pi / 2.0)
        hx = 85.0 * math.cos(ang)
        hy = 85.0 * math.sin(ang)
        drill_cylinder_hole(obj, radius=5.5, depth=20.0, location=(hx, hy, 5.0))
        
    # 6 holes phi 6 on PCD 110 (R=55)
    for i in range(6):
        ang = i * (math.pi / 3.0) + math.pi / 6.0
        hx = 55.0 * math.cos(ang)
        hy = 55.0 * math.sin(ang)
        drill_cylinder_hole(obj, radius=3.0, depth=20.0, location=(hx, hy, 5.0))
    return obj

def make_LJT04_23():
    """LJT04.23 调节盘 (Adjusting Disc with Curved Slots)"""
    # Outer dia 180 (R=90), flange thickness 22 (Z: 0 to 22), hub dia 100g6 (R=50, Z: 22 to 64)
    # Total length 64, bore phi 60H7 (0 to 22), phi 64H7 (22 to 64) with groove width 13
    profile = [
        (0.0, 30.0),
        (0.0, 90.0),
        (22.0, 90.0),
        (22.0, 50.0),
        (64.0, 50.0),
        (64.0, 32.0),
        (45.0, 32.0),
        (45.0, 37.0),
        (32.0, 37.0),
        (32.0, 32.0),
        (22.0, 32.0),
        (22.0, 30.0),
        (0.0, 30.0)
    ]
    obj = build_revolved_body(profile, segments=72, axis='Z')
    obj.name = "LJT04.23_调节盘"
    
    # 6 curved adjustment arc slots: width 14 (R7 ends), spanning 30° each on PCD 142 (R=71)
    for k in range(6):
        base_ang = k * (2.0 * math.pi / 6.0)
        # Create arc cutter with multiple overlapping cylinders
        for step in range(7):
            dang = math.radians((step - 3) * 5.0) # -15 to +15 deg
            ang = base_ang + dang
            cx = 71.0 * math.cos(ang)
            cy = 71.0 * math.sin(ang)
            drill_cylinder_hole(obj, radius=7.0, depth=30.0, location=(cx, cy, 11.0))
            
    # Pin holes: phi 8H7 and phi 10H7
    drill_cylinder_hole(obj, radius=4.0, depth=30.0, location=(71.0 * math.cos(math.radians(15.0)), 71.0 * math.sin(math.radians(15.0)), 11.0))
    drill_cylinder_hole(obj, radius=5.0, depth=30.0, location=(71.0 * math.cos(math.radians(45.0)), 71.0 * math.sin(math.radians(45.0)), 11.0))
    return obj

def make_LJT04_24():
    """LJT04.24 读数盘 (Graduated Dial Ring)"""
    # Outer dia 120h11 (R=60), conical beveled scale 27°18', knurled dia 92 (R=46) x 8
    # Shoulder dia 89 (R=44.5), bore phi 60H7 (R=30), total width 21 (Z: 0 to 21)
    profile = [
        (0.0, 30.0),
        (0.0, 46.0),
        (8.0, 46.0),
        (8.0, 44.5),
        (17.0, 44.5),
        (21.0, 60.0),
        (21.0, 30.0),
        (0.0, 30.0)
    ]
    obj = build_revolved_body(profile, segments=72, axis='Z')
    obj.name = "LJT04.24_读数盘"
    
    # Add subtle knurling grooves on cylinder phi 92 (Z: 0 to 8)
    for i in range(36):
        ang = i * (2.0 * math.pi / 36.0)
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(46.0 * math.cos(ang), 46.0 * math.sin(ang), 4.0),
            rotation=(0, 0, ang)
        )
        cutter = bpy.context.active_object
        cutter.scale = (1.5, 0.8, 10.0)
        bpy.ops.object.transform_apply(scale=True)
        apply_boolean_difference(obj, cutter)
    return obj

def make_LJT04_25():
    """LJT04.25 定位盘 (Indexing Plate with 6 Perimeter Notches)"""
    # Outer dia 112 (R=56), width 10 (Z: 20 to 30), total length 40 (Z: 0 to 40)
    # Left hub dia 78js6 (R=39, Z: 0 to 20), right hub dia 78 (Z: 30 to 35), dia 30 (Z: 35 to 40)
    # Stepped bore: phi 30H8 (Z: 0 to 15), phi 18H8 (Z: 15 to 40)
    profile = [
        (0.0, 15.0),
        (0.0, 39.0),
        (20.0, 39.0),
        (20.0, 56.0),
        (30.0, 56.0),
        (30.0, 39.0),
        (35.0, 39.0),
        (35.0, 15.0),
        (40.0, 15.0),
        (40.0, 9.0),
        (15.0, 9.0),
        (15.0, 15.0),
        (0.0, 15.0)
    ]
    obj = build_revolved_body(profile, segments=72, axis='Z')
    obj.name = "LJT04.25_定位盘"
    
    # 6 perimeter indexing notches (20° span, depth to dia 102, R=51)
    for i in range(6):
        ang = i * (2.0 * math.pi / 6.0)
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(54.0 * math.cos(ang), 54.0 * math.sin(ang), 25.0),
            rotation=(0, 0, ang)
        )
        cutter = bpy.context.active_object
        cutter.scale = (10.0, 18.0, 15.0)
        bpy.ops.object.transform_apply(scale=True)
        apply_boolean_difference(obj, cutter)
        
    # 6 x phi 7 on PCD 96 (R=48)
    for i in range(6):
        ang = i * (2.0 * math.pi / 6.0) + math.pi / 6.0
        hx = 48.0 * math.cos(ang)
        hy = 48.0 * math.sin(ang)
        drill_cylinder_hole(obj, radius=3.5, depth=45.0, location=(hx, hy, 20.0))
        
    # 6 x M6 on PCD 56 (R=28)
    for i in range(6):
        ang = i * (2.0 * math.pi / 6.0)
        hx = 28.0 * math.cos(ang)
        hy = 28.0 * math.sin(ang)
        drill_cylinder_hole(obj, radius=2.5, depth=25.0, location=(hx, hy, 20.0))
    return obj

def make_LJT04_26():
    """LJT04.26 偏心盘 (Eccentric Disc)"""
    # Central hub: dia 60 (R=30), total length 76 (Z: 0 to 76), bore dia 36H7 (R=18)
    # Eccentric outer flange: R76 (dia 152), offset e = 18 mm in Y!
    # Flange Z: 10 to 24 (thickness 14), with perimeter groove width 14, depth 10
    
    # 1. Central Hub
    hub_profile = [
        (0.0, 18.0),
        (0.0, 30.0),
        (76.0, 30.0),
        (76.0, 18.0),
        (0.0, 18.0)
    ]
    hub = build_revolved_body(hub_profile, segments=48, axis='Z')
    
    # 2. Eccentric Flange Disk (center at Y = 18.0)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=76.0, depth=14.0, vertices=64,
        location=(0.0, 18.0, 17.0)
    )
    flange = bpy.context.active_object
    
    # Cut eccentric channel groove: radius 46 to 76 at Z=17
    bpy.ops.mesh.primitive_cylinder_add(
        radius=46.0, depth=16.0, vertices=48,
        location=(0.0, 18.0, 17.0)
    )
    inner_cut = bpy.context.active_object
    apply_boolean_difference(flange, inner_cut)
    
    # Join hub and flange
    bpy.ops.object.select_all(action='DESELECT')
    flange.select_set(True)
    hub.select_set(True)
    bpy.context.view_layer.objects.active = hub
    bpy.ops.object.join()
    obj = hub
    obj.name = "LJT04.26_偏心盘"
    
    # Center bore through
    drill_cylinder_hole(obj, radius=18.0, depth=85.0, location=(0.0, 0.0, 38.0))
    
    # 10N9 keyway, depth 3.3
    add_standard_keyway(obj, bore_radius=18.0, key_width=10.0, key_depth=3.3, length=85.0, center_z=38.0)
    
    # Eccentric hole phi 12 at Y = 48
    drill_cylinder_hole(obj, radius=6.0, depth=30.0, location=(0.0, 48.0, 17.0))
    return obj

def make_LJT04_27():
    """LJT04.27 连接盘 (Connecting Plate with Boss & Cross Holes)"""
    # Flange dia 108 (R=54), thickness 14 (Z: 0 to 14), step dia 82 x 6 (Z: 14 to 20)
    # Left hub dia 50 (R=25, Z: -60 to 0), total length 80 (Z: -60 to 20)
    # Bore phi 32H7 (Z: -60 to -4), phi 14 (Z: -4 to 20)
    profile = [
        (-60.0, 16.0),
        (-60.0, 25.0),
        (0.0, 25.0),
        (0.0, 54.0),
        (14.0, 54.0),
        (14.0, 41.0),
        (20.0, 41.0),
        (20.0, 7.0),
        (-4.0, 7.0),
        (-4.0, 16.0),
        (-60.0, 16.0)
    ]
    obj = build_revolved_body(profile, segments=64, axis='Z')
    obj.name = "LJT04.27_连接盘"
    
    # Radial boss on hub (height 36, width 24 at Z = -38)
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(0.0, 25.0, -38.0)
    )
    boss = bpy.context.active_object
    boss.scale = (24.0, 22.0, 24.0)
    bpy.ops.object.transform_apply(scale=True)
    
    bpy.ops.object.select_all(action='DESELECT')
    boss.select_set(True)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.join()
    
    # Cross hole phi 12 through boss with counterbore phi 24
    drill_cylinder_hole(obj, radius=6.0, depth=45.0, location=(0.0, 25.0, -38.0), rotation=(math.pi/2, 0, 0))
    drill_cylinder_hole(obj, radius=12.0, depth=8.0, location=(0.0, 32.0, -38.0), rotation=(math.pi/2, 0, 0))
    
    # Cross hole phi 8 at Z = -22
    drill_cylinder_hole(obj, radius=4.0, depth=35.0, location=(0.0, 0.0, -22.0), rotation=(0, math.pi/2, 0))
    
    # 3 bolt holes phi 12 on PCD 82 (R=41) at 45°
    for ang_deg in [45, 135, 225]:
        ang = math.radians(ang_deg)
        hx = 41.0 * math.cos(ang)
        hy = 41.0 * math.sin(ang)
        drill_cylinder_hole(obj, radius=6.0, depth=30.0, location=(hx, hy, 10.0))
        
    # Bottom notch arc R10
    drill_cylinder_hole(obj, radius=10.0, depth=30.0, location=(0.0, -54.0, 10.0))
    return obj

def make_LJT04_28():
    """LJT04.28 花盘 (Lathe Faceplate)"""
    # Outer dia 320 (R=160), rim width 45 (Z: 35 to 80), inner rim R=147
    # Web thickness 18 (Z: 35 to 53). Hub dia 116 (R=58, Z: 0 to 80), total length 80
    # Hub bore dia 68 (R=34), counterbore phi 72 x 32
    profile = [
        (0.0, 34.0),
        (0.0, 58.0),
        (35.0, 58.0),
        (35.0, 147.0),
        (35.0, 160.0),
        (80.0, 160.0),
        (80.0, 147.0),
        (53.0, 147.0),
        (53.0, 58.0),
        (80.0, 58.0),
        (80.0, 36.0),
        (48.0, 36.0),
        (48.0, 34.0),
        (0.0, 34.0)
    ]
    obj = build_revolved_body(profile, segments=72, axis='Z')
    obj.name = "LJT04.28_花盘"
    
    # 4 orthogonal T-slots (width 24, length from R=65 to 140)
    for q in range(4):
        ang = q * (math.pi / 2.0)
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(102.5 * math.cos(ang), 102.5 * math.sin(ang), 44.0),
            rotation=(0, 0, ang)
        )
        cutter = bpy.context.active_object
        cutter.scale = (75.0, 24.0, 25.0)
        bpy.ops.object.transform_apply(scale=True)
        apply_boolean_difference(obj, cutter)
        
    # 4 diagonal radial slots (width 19, length 66) at 45°
    for q in range(4):
        ang = q * (math.pi / 2.0) + math.pi / 4.0
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(105.0 * math.cos(ang), 105.0 * math.sin(ang), 44.0),
            rotation=(0, 0, ang)
        )
        cutter = bpy.context.active_object
        cutter.scale = (66.0, 19.0, 25.0)
        bpy.ops.object.transform_apply(scale=True)
        apply_boolean_difference(obj, cutter)
    return obj

def make_LJT04_29():
    """LJT04.29 压盘 (Clutch Pressure Plate)"""
    # Outer dia 280 (R=140), inner bore phi 158 (R=79)
    # Friction ring face: dia 178 (R=89) to 274 (R=137), thickness 19 (Z: 0 to 19), total 32.2 (Z: 0 to 32.2)
    # 4 mounting lugs extending to R=153 with 4 x phi 8.2 holes
    profile = [
        (0.0, 79.0),
        (0.0, 140.0),
        (19.0, 140.0),
        (19.0, 137.0),
        (32.2, 137.0),
        (32.2, 89.0),
        (19.0, 89.0),
        (19.0, 79.0),
        (0.0, 79.0)
    ]
    obj = build_revolved_body(profile, segments=72, axis='Z')
    obj.name = "LJT04.29_压盘"
    
    # 4 outer mounting ear lugs at 90°
    lug_objs = []
    for i in range(4):
        ang = i * (math.pi / 2.0)
        bpy.ops.mesh.primitive_cylinder_add(
            radius=15.0, depth=17.0, vertices=32,
            location=(145.0 * math.cos(ang), 145.0 * math.sin(ang), 8.5)
        )
        lug = bpy.context.active_object
        lug_objs.append(lug)
        
    bpy.ops.object.select_all(action='DESELECT')
    for l in lug_objs:
        l.select_set(True)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.join()
    
    # 4 mounting holes phi 8.2 on lugs (PCD 306, R=153)
    for i in range(4):
        ang = i * (math.pi / 2.0)
        hx = 153.0 * math.cos(ang)
        hy = 153.0 * math.sin(ang)
        drill_cylinder_hole(obj, radius=4.1, depth=25.0, location=(hx, hy, 8.5))
        
    # 12 cooling arc slots: width 4 on PCD 254 (R=127)
    for i in range(12):
        ang = i * (2.0 * math.pi / 12.0)
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(127.0 * math.cos(ang), 127.0 * math.sin(ang), 10.0),
            rotation=(0, 0, ang)
        )
        cutter = bpy.context.active_object
        cutter.scale = (4.0, 20.0, 25.0)
        bpy.ops.object.transform_apply(scale=True)
        apply_boolean_difference(obj, cutter)
    return obj

def make_LJT04_30():
    """LJT04.30 半联轴器 (Pin Bushing Flexible Half-Coupling)"""
    # Outer flange dia 200h9 (R=100), flange thickness 42 (Z: 38 to 80)
    # Hub dia 100 (R=50, Z: 0 to 38), total length 80 (Z: 0 to 80), bore dia 42H7 (R=21)
    profile = [
        (0.0, 21.0),
        (0.0, 50.0),
        (38.0, 50.0),
        (38.0, 100.0),
        (80.0, 100.0),
        (80.0, 21.0),
        (0.0, 21.0)
    ]
    obj = build_revolved_body(profile, segments=72, axis='Z')
    obj.name = "LJT04.30_半联轴器"
    
    # 8 coupling pin holes: 8 x phi 18 with counterbore phi 38 / 26 x 16 on PCD 150 (R=75)
    for i in range(8):
        ang = i * (2.0 * math.pi / 8.0)
        hx = 75.0 * math.cos(ang)
        hy = 75.0 * math.sin(ang)
        drill_cylinder_hole(obj, radius=9.0, depth=50.0, location=(hx, hy, 59.0))
        drill_cylinder_hole(obj, radius=16.0, depth=16.0, location=(hx, hy, 46.0))
        
    # Keyway: 12JS9, depth 3.3
    add_standard_keyway(obj, bore_radius=21.0, key_width=12.0, key_depth=3.3, length=90.0, center_z=40.0)
    
    # Radial M12 screw hole at Z=20
    drill_cylinder_hole(obj, radius=6.0, depth=35.0, location=(0.0, 40.0, 20.0), rotation=(math.pi/2, 0, 0))
    return obj

def make_LJT04_31():
    """LJT04.31 半离合器 (Jaw Half-Clutch with Splined Bore)"""
    # Outer dia 140 (R=70), flange thickness 10 (Z: 0 to 10), body dia 115 (R=57.5, Z: 10 to 72)
    # Shifter fork groove: width 25H9 (Z: 25 to 50), root dia 90 (R=45)
    # Total length 72, bore dia 46H7 (R=23)
    profile = [
        (0.0, 23.0),
        (0.0, 70.0),
        (10.0, 70.0),
        (10.0, 57.5),
        (25.0, 57.5),
        (25.0, 45.0),
        (50.0, 45.0),
        (50.0, 57.5),
        (72.0, 57.5),
        (72.0, 23.0),
        (0.0, 23.0)
    ]
    obj = build_revolved_body(profile, segments=64, axis='Z')
    obj.name = "LJT04.31_半离合器"
    
    # 8 interlocking axial clutch jaws on front face (Z: 64 to 72)
    # Tooth pitch 40 deg, jaw tooth width ~ 20 deg, gap ~ 20 deg, depth 8mm
    for i in range(8):
        ang = i * (math.pi / 4.0)
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(45.0 * math.cos(ang), 45.0 * math.sin(ang), 68.0),
            rotation=(0, 0, ang)
        )
        cutter = bpy.context.active_object
        cutter.scale = (35.0, 16.0, 10.0)
        bpy.ops.object.transform_apply(scale=True)
        apply_boolean_difference(obj, cutter)
        
    # 6 internal splines in bore (width 12H9, major dia 50, depth 2.0)
    for i in range(6):
        ang = i * (math.pi / 3.0)
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(24.0 * math.cos(ang), 24.0 * math.sin(ang), 36.0),
            rotation=(0, 0, ang)
        )
        cutter = bpy.context.active_object
        cutter.scale = (4.0, 12.0, 80.0)
        bpy.ops.object.transform_apply(scale=True)
        apply_boolean_difference(obj, cutter)
    return obj


# ==============================================================================
# Batch Execution Runner
# ==============================================================================

MODELS = [
    ("LJT04.17", "法兰盘", make_LJT04_17, "04_轮盘盖类_Discs_Covers", "machined_steel"),
    ("LJT04.18", "法兰盘", make_LJT04_18, "04_轮盘盖类_Discs_Covers", "cast_iron"),
    ("LJT04.19", "法兰盘", make_LJT04_19, "04_轮盘盖类_Discs_Covers", "cast_iron"),
    ("LJT04.20", "法兰盘", make_LJT04_20, "04_轮盘盖类_Discs_Covers", "cast_iron"),
    ("LJT04.21", "拨盘", make_LJT04_21, "04_轮盘盖类_Discs_Covers", "machined_steel"),
    ("LJT04.22", "调节盘", make_LJT04_22, "04_轮盘盖类_Discs_Covers", "machined_steel"),
    ("LJT04.23", "调节盘", make_LJT04_23, "04_轮盘盖类_Discs_Covers", "machined_steel"),
    ("LJT04.24", "读数盘", make_LJT04_24, "04_轮盘盖类_Discs_Covers", "machined_steel"),
    ("LJT04.25", "定位盘", make_LJT04_25, "04_轮盘盖类_Discs_Covers", "cast_iron"),
    ("LJT04.26", "偏心盘", make_LJT04_26, "04_轮盘盖类_Discs_Covers", "cast_iron"),
    ("LJT04.27", "连接盘", make_LJT04_27, "04_轮盘盖类_Discs_Covers", "cast_iron"),
    ("LJT04.28", "花盘", make_LJT04_28, "04_轮盘盖类_Discs_Covers", "cast_iron"),
    ("LJT04.29", "压盘", make_LJT04_29, "04_轮盘盖类_Discs_Covers", "cast_iron"),
    ("LJT04.30", "半联轴器", make_LJT04_30, "04_轮盘盖类_Discs_Covers", "cast_iron"),
    ("LJT04.31", "半离合器", make_LJT04_31, "04_轮盘盖类_Discs_Covers", "machined_steel"),
]

def run_batch():
    total = len(MODELS)
    print(f"\n=======================================================")
    print(f"Starting Category 04 Batch 2: {total} Models (Discs, Flanges & Couplings)")
    print(f"=======================================================\n")
    
    for idx, (code, name, func, folder, mat) in enumerate(MODELS, 1):
        full_name = f"{code}_{name}"
        blend_file = os.path.join(base_dir, folder, f"{full_name}.blend")
        render_file = os.path.join(renders_dir, f"{full_name}.png")
        
        print(f"[{idx}/{total}] Generating {code}: {full_name}...")
        
        try:
            obj = func()
            if obj is not None:
                bcg.render_and_save(obj, blend_file, render_file, mat_type=mat)
                print(f"   [DONE] Generated and saved {full_name}.blend\n")
            else:
                print(f"   [ERROR] Generator returned None for {full_name}\n")
        except Exception as e:
            print(f"   [FAILED] Error generating {full_name}: {e}\n")
            import traceback
            traceback.print_exc()
            
    print("=== Category 04 Batch 2 Generation Completed ===")

if __name__ == "__main__":
    run_batch()
