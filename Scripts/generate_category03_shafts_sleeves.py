"""
Category 03: 轴套类零件图 (Shafts & Sleeves) Complete Procedural CAD Generator
Generates all 26 remaining models (LJT03.01 ~ LJT03.40) in Blender Python (bpy / bmesh)
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
cat_dir = os.path.join(base_dir, "03_轴套类_Shafts_Sleeves")
renders_dir = os.path.join(base_dir, "Renders")
os.makedirs(cat_dir, exist_ok=True)
os.makedirs(renders_dir, exist_ok=True)

def build_revolved_body(profile_pts, segments=64, axis='X'):
    """
    Builds a 3D revolved body from 2D profile coordinates (along axis, radius).
    profile_pts: list of (pos, radius) tuples.
    axis: 'X' revolves around X-axis; 'Z' revolves around Z-axis.
    """
    bm = bmesh.new()
    rings = []
    
    for pos, r in profile_pts:
        ring = []
        for i in range(segments):
            theta = i * 2.0 * math.pi / segments
            if axis == 'X':
                x = pos
                y = r * math.cos(theta)
                z = r * math.sin(theta)
            else:
                x = r * math.cos(theta)
                y = r * math.sin(theta)
                z = pos
            ring.append(bm.verts.new((x, y, z)))
        rings.append(ring)
        
    bm.verts.ensure_lookup_table()
    for j in range(len(profile_pts) - 1):
        r1 = rings[j]
        r2 = rings[j+1]
        for i in range(segments):
            next_i = (i + 1) % segments
            # Normal oriented outward
            if axis == 'X':
                bm.faces.new((r1[i], r2[i], r2[next_i], r1[next_i]))
            else:
                bm.faces.new((r1[i], r1[next_i], r2[next_i], r2[i]))

    # End caps if radius at ends is > 0
    if profile_pts[0][1] > 0:
        c_v = bm.verts.new((profile_pts[0][0], 0, 0) if axis == 'X' else (0, 0, profile_pts[0][0]))
        r0 = rings[0]
        for i in range(segments):
            next_i = (i + 1) % segments
            if axis == 'X':
                bm.faces.new((c_v, r0[next_i], r0[i]))
            else:
                bm.faces.new((c_v, r0[i], r0[next_i]))
                
    if profile_pts[-1][1] > 0:
        c_v = bm.verts.new((profile_pts[-1][0], 0, 0) if axis == 'X' else (0, 0, profile_pts[-1][0]))
        rN = rings[-1]
        for i in range(segments):
            next_i = (i + 1) % segments
            if axis == 'X':
                bm.faces.new((c_v, rN[i], rN[next_i]))
            else:
                bm.faces.new((c_v, rN[next_i], rN[i]))

    mesh = bpy.data.meshes.new("Revolved_Body")
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new("Revolved_Object", mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj

def cut_keyway(obj, center_x, top_z, length, width, depth):
    """Cuts an engineering keyway on a shaft along X-axis."""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(center_x, 0, top_z - depth/2.0))
    cutter = bpy.context.active_object
    cutter.scale = (length, width, depth + 2.0)
    
    mod = obj.modifiers.new(name="Cut_Keyway", type='BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = cutter
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier="Cut_Keyway")
    bpy.data.objects.remove(cutter, do_unlink=True)

# ------------------------------------------------------------------------------
# 1. LJT03.01 转轴 (Shaft)
# ------------------------------------------------------------------------------
def generate_ljt03_01():
    bcg.reset_scene()
    prof = [
        (0.0, 0.0), (0.0, 6.0), (15.0, 6.0),         # M12 thread
        (15.0, 8.0), (47.0, 8.0),                   # phi 16
        (47.0, 10.0), (79.0, 10.0),                 # phi 20
        (79.0, 13.0), (112.0, 13.0),                # phi 26 collar
        (112.0, 10.0), (144.0, 10.0),               # phi 20
        (144.0, 8.0), (176.0, 8.0), (176.0, 0.0)    # phi 16
    ]
    obj = build_revolved_body(prof, segments=48)
    obj.name = "LJT03.01_转轴"
    cut_keyway(obj, center_x=32.0, top_z=8.0, length=20.0, width=5.0, depth=3.0)
    cut_keyway(obj, center_x=161.0, top_z=8.0, length=20.0, width=5.0, depth=3.0)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    return obj

# ------------------------------------------------------------------------------
# 2. LJT03.02 手柄 (Handle)
# ------------------------------------------------------------------------------
def generate_ljt03_02():
    bcg.reset_scene()
    # Teardrop contour along X axis: length = 125 mm
    prof = []
    # Mounting stem phi 12 (length 25)
    prof.append((0.0, 0.0))
    prof.append((0.0, 6.0))
    prof.append((25.0, 6.0))
    # Base collar phi 18 (length 13)
    prof.append((25.0, 9.0))
    prof.append((38.0, 9.0))
    # Waist and bulb: X from 38 to 125
    steps = 40
    for i in range(steps + 1):
        x = 38.0 + (125.0 - 38.0) * (i / float(steps))
        t = (x - 38.0) / (125.0 - 38.0) # 0 to 1
        # Polynomial teardrop: waist phi 16 at t=0.15, max phi 32 at t=0.6, tip SR4.5 at t=1.0
        r = 8.0 + 8.0 * math.sin(t * math.pi) * (1.1 - 0.5 * t)
        if t > 0.95:
            r *= math.sqrt(max(0.0, 1.0 - ((t - 0.95)/0.05)**2))
        prof.append((x, r))
    prof.append((125.0, 0.0))
    
    obj = build_revolved_body(prof, segments=48)
    obj.name = "LJT03.02_手柄"
    # Cut internal mounting hole phi 9 x 6 mm
    bpy.ops.mesh.primitive_cylinder_add(radius=4.5, depth=12.0, location=(3.0, 0, 0), vertices=32)
    hole = bpy.context.active_object
    hole.rotation_euler = (0, math.radians(90), 0)
    mod = obj.modifiers.new(name="Bore", type='BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = hole
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier="Bore")
    bpy.data.objects.remove(hole, do_unlink=True)
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    return obj

# ------------------------------------------------------------------------------
# 3. LJT03.03 阀杆 (Valve Stem)
# ------------------------------------------------------------------------------
def generate_ljt03_03():
    bcg.reset_scene()
    prof = [
        (0.0, 0.0), (0.0, 7.0), (50.0, 7.0),       # phi 14 body
        (50.0, 9.0), (57.0, 9.0),                   # phi 18 collar
        (57.0, 4.25), (62.0, 4.25), (62.0, 0.0)    # phi 8.5 tip
    ]
    obj = build_revolved_body(prof, segments=48)
    obj.name = "LJT03.03_阀杆"
    # Cut 11x11 square head on front 14 mm
    # Cut top & bottom
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(7.0, 0, 5.5 + 5.0))
    c1 = bpy.context.active_object
    c1.scale = (14.0, 20.0, 10.0)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(7.0, 0, -5.5 - 5.0))
    c2 = bpy.context.active_object
    c2.scale = (14.0, 20.0, 10.0)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(7.0, 5.5 + 5.0, 0))
    c3 = bpy.context.active_object
    c3.scale = (14.0, 10.0, 20.0)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(7.0, -5.5 - 5.0, 0))
    c4 = bpy.context.active_object
    c4.scale = (14.0, 10.0, 20.0)
    
    for c in [c1, c2, c3, c4]:
        mod = obj.modifiers.new(name="Square_Cut", type='BOOLEAN')
        mod.operation = 'DIFFERENCE'
        mod.object = c
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier="Square_Cut")
        bpy.data.objects.remove(c, do_unlink=True)
        
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    return obj

# ------------------------------------------------------------------------------
# 4. LJT03.14 滚子轴 (Roller Shaft)
# ------------------------------------------------------------------------------
def generate_ljt03_14():
    bcg.reset_scene()
    prof = [
        (0.0, 0.0), (0.0, 15.0), (17.0, 15.0),     # Left phi 30h6
        (17.0, 18.0), (28.0, 18.0),                 # phi 36 shoulder
        (28.0, 50.0), (114.0, 50.0),                # Roller left half phi 100
        (118.0, 46.0), (122.0, 50.0),               # Center V-groove
        (122.0, 50.0), (208.0, 50.0),               # Roller right half
        (208.0, 18.0), (219.0, 18.0),               # phi 36 shoulder
        (219.0, 15.0), (235.0, 15.0),               # phi 30h6
        (235.0, 14.5), (255.0, 14.5),               # phi 29 groove
        (255.0, 13.0), (295.0, 13.0), (295.0, 0.0)  # phi 26h6 shaft end
    ]
    obj = build_revolved_body(prof, segments=64)
    obj.name = "LJT03.14_滚子轴"
    cut_keyway(obj, center_x=275.0, top_z=13.0, length=32.0, width=8.0, depth=4.0)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    return obj

# ------------------------------------------------------------------------------
# 5. LJT03.15 十字轴 (Spider / Cross Shaft)
# ------------------------------------------------------------------------------
def generate_ljt03_15():
    bcg.reset_scene()
    # 4 orthogonal arms phi 25, total length = 108 mm
    # Arm X
    bpy.ops.mesh.primitive_cylinder_add(radius=12.5, depth=108.0, location=(0, 0, 0), vertices=48)
    arm_x = bpy.context.active_object
    arm_x.rotation_euler = (0, math.radians(90), 0)
    
    # Arm Y
    bpy.ops.mesh.primitive_cylinder_add(radius=12.5, depth=108.0, location=(0, 0, 0), vertices=48)
    arm_y = bpy.context.active_object
    arm_y.rotation_euler = (math.radians(90), 0, 0)
    
    # Center hub block
    bpy.ops.mesh.primitive_cylinder_add(radius=18.0, depth=28.0, location=(0, 0, 0), vertices=48)
    hub = bpy.context.active_object
    
    # Union all
    for part in [arm_y, hub]:
        mod = arm_x.modifiers.new(name="Union", type='BOOLEAN')
        mod.operation = 'UNION'
        mod.object = part
        bpy.context.view_layer.objects.active = arm_x
        bpy.ops.object.modifier_apply(modifier="Union")
        bpy.data.objects.remove(part, do_unlink=True)
        
    # Lubrication through holes phi 6 along X and Y
    bpy.ops.mesh.primitive_cylinder_add(radius=3.0, depth=120.0, location=(0, 0, 0), vertices=24)
    oil_x = bpy.context.active_object
    oil_x.rotation_euler = (0, math.radians(90), 0)
    bpy.ops.mesh.primitive_cylinder_add(radius=3.0, depth=120.0, location=(0, 0, 0), vertices=24)
    oil_y = bpy.context.active_object
    oil_y.rotation_euler = (math.radians(90), 0, 0)
    
    for o in [oil_x, oil_y]:
        mod = arm_x.modifiers.new(name="OilHole", type='BOOLEAN')
        mod.operation = 'DIFFERENCE'
        mod.object = o
        bpy.context.view_layer.objects.active = arm_x
        bpy.ops.object.modifier_apply(modifier="OilHole")
        bpy.data.objects.remove(o, do_unlink=True)
        
    arm_x.name = "LJT03.15_十字轴"
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    return arm_x

# ------------------------------------------------------------------------------
# 6. LJT03.16 滑柱 (Sliding Pillar)
# ------------------------------------------------------------------------------
def generate_ljt03_16():
    bcg.reset_scene()
    prof = [
        (0.0, 0.0), (0.0, 16.0), (79.0, 16.0),     # phi 32g6 main body
        (79.0, 14.5), (82.0, 14.5),                 # 3x2 undercut
        (82.0, 16.0), (113.0, 16.0),                # phi 32
        (113.0, 20.0), (118.0, 20.0), (118.0, 0.0)  # phi 40 flange (thick 5)
    ]
    obj = build_revolved_body(prof, segments=48)
    obj.name = "LJT03.16_滑柱"
    
    # Cut front flattened tang: thickness 12 mm, length 26 mm
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(13.0, 0, 6.0 + 10.0))
    c1 = bpy.context.active_object
    c1.scale = (26.0, 40.0, 20.0)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(13.0, 0, -6.0 - 10.0))
    c2 = bpy.context.active_object
    c2.scale = (26.0, 40.0, 20.0)
    
    for c in [c1, c2]:
        mod = obj.modifiers.new(name="Tang_Cut", type='BOOLEAN')
        mod.operation = 'DIFFERENCE'
        mod.object = c
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier="Tang_Cut")
        bpy.data.objects.remove(c, do_unlink=True)
        
    # Tang pin hole phi 12
    bpy.ops.mesh.primitive_cylinder_add(radius=6.0, depth=30.0, location=(11.0, 0, 0), vertices=32)
    pin = bpy.context.active_object
    mod_p = obj.modifiers.new(name="Pin_Hole", type='BOOLEAN')
    mod_p.operation = 'DIFFERENCE'
    mod_p.object = pin
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier="Pin_Hole")
    bpy.data.objects.remove(pin, do_unlink=True)
    
    # Tail internal bore phi 24 x 30 mm
    bpy.ops.mesh.primitive_cylinder_add(radius=12.0, depth=60.0, location=(118.0, 0, 0), vertices=48)
    tail_bore = bpy.context.active_object
    tail_bore.rotation_euler = (0, math.radians(90), 0)
    mod_b = obj.modifiers.new(name="Tail_Bore", type='BOOLEAN')
    mod_b.operation = 'DIFFERENCE'
    mod_b.object = tail_bore
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier="Tail_Bore")
    bpy.data.objects.remove(tail_bore, do_unlink=True)
    
    # Keyway
    cut_keyway(obj, center_x=45.5, top_z=16.0, length=39.0, width=8.0, depth=3.5)
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    return obj

# ------------------------------------------------------------------------------
# 7. LJT03.17 传动轴 (Transmission Shaft)
# ------------------------------------------------------------------------------
def generate_ljt03_17():
    bcg.reset_scene()
    prof = [
        (0.0, 0.0), (0.0, 10.0), (35.0, 10.0),      # phi 20
        (35.0, 12.5), (75.0, 12.5),                 # phi 25
        (75.0, 15.0), (180.0, 15.0),                # phi 30 center shaft
        (180.0, 12.5), (220.0, 12.5),               # phi 25
        (220.0, 10.0), (250.0, 10.0), (250.0, 0.0)  # phi 20
    ]
    obj = build_revolved_body(prof, segments=48)
    obj.name = "LJT03.17_传动轴"
    cut_keyway(obj, center_x=17.5, top_z=10.0, length=20.0, width=6.0, depth=3.5)
    cut_keyway(obj, center_x=235.0, top_z=10.0, length=20.0, width=6.0, depth=3.5)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    return obj

# ------------------------------------------------------------------------------
# 8. LJT03.18 矩形花键轴 (Spline Shaft)
# ------------------------------------------------------------------------------
def generate_ljt03_18():
    bcg.reset_scene()
    prof = [
        (0.0, 0.0), (0.0, 22.5), (26.5, 22.5),      # phi 45js6
        (26.5, 31.0), (49.5, 31.0),                 # phi 62 collar
        (49.5, 24.0), (296.5, 24.0),                # phi 48 spline major
        (296.5, 20.0), (321.5, 20.0),               # phi 40js6
        (321.5, 12.5), (388.0, 12.5), (388.0, 0.0)  # phi 25js6
    ]
    obj = build_revolved_body(prof, segments=64)
    obj.name = "LJT03.18_矩形花键轴"
    
    # 6 Spline grooves on phi 48 (minor dia phi 42, width 12)
    # Cut 6 radial grooves
    groove_len = 247.0
    center_gx = 49.5 + groove_len / 2.0
    for i in range(6):
        ang = i * (2.0 * math.pi / 6.0) + (math.pi / 6.0)
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(center_gx, 0, 0))
        g = bpy.context.active_object
        g.scale = (groove_len, 12.0, 50.0)
        g.rotation_euler = (ang, 0, 0)
        mod = obj.modifiers.new(name=f"Spline_{i}", type='BOOLEAN')
        mod.operation = 'DIFFERENCE'
        mod.object = g
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=f"Spline_{i}")
        bpy.data.objects.remove(g, do_unlink=True)
        
    cut_keyway(obj, center_x=345.0, top_z=12.5, length=40.0, width=8.0, depth=4.0)
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    return obj

# ------------------------------------------------------------------------------
# 9. LJT03.20 齿轮轴 (Gear Shaft)
# ------------------------------------------------------------------------------
def generate_ljt03_20():
    bcg.reset_scene()
    prof = [
        (0.0, 0.0), (0.0, 15.0), (30.0, 15.0),       # phi 30m6
        (30.0, 18.0), (36.0, 18.0),                  # phi 36 shoulder
        (36.0, 23.25), (76.0, 23.25),                # Helical gear tip phi 46.5 x 40
        (76.0, 17.5), (146.0, 17.5),                 # phi 35 shaft
        (146.0, 17.5), (186.0, 17.5), (186.0, 0.0)   # phi 35 / phi 30
    ]
    obj = build_revolved_body(prof, segments=48)
    obj.name = "LJT03.20_齿轮轴"
    cut_keyway(obj, center_x=166.0, top_z=17.5, length=35.0, width=10.0, depth=5.0)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    return obj

# ------------------------------------------------------------------------------
# 10. LJT03.21 锥齿轮轴 (Bevel Gear Shaft)
# ------------------------------------------------------------------------------
def generate_ljt03_21():
    bcg.reset_scene()
    prof = [
        (0.0, 0.0), (0.0, 17.5), (60.0, 17.5),       # phi 35
        (60.0, 21.0), (110.0, 21.0),                 # phi 42
        (110.0, 22.5), (135.0, 22.5),                # phi 45
        (135.0, 21.0), (160.0, 21.0),                # phi 42
        (160.0, 22.5), (185.0, 22.5),                # phi 45
        (185.0, 27.5), (225.0, 27.5),                # phi 55 shoulder
        (225.0, 40.06), (258.0, 30.0),               # Bevel gear cone phi 80.13 to cone
        (265.0, 0.0)
    ]
    obj = build_revolved_body(prof, segments=48)
    obj.name = "LJT03.21_锥齿轮轴"
    cut_keyway(obj, center_x=30.0, top_z=17.5, length=50.0, width=10.0, depth=5.0)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    return obj

# ------------------------------------------------------------------------------
# 11. LJT03.22 凸轮轴 (Camshaft)
# ------------------------------------------------------------------------------
def generate_ljt03_22():
    bcg.reset_scene()
    prof = [
        (0.0, 0.0), (0.0, 20.0), (45.0, 20.0),       # phi 40 front bearing
        (45.0, 12.5), (129.0, 12.5),                 # phi 25 intermediate
        (129.0, 12.5), (198.0, 12.5),                # phi 25
        (198.0, 14.0), (224.0, 14.0), (224.0, 0.0)   # phi 28 rear bearing
    ]
    shaft = build_revolved_body(prof, segments=48)
    shaft.name = "LJT03.22_凸轮轴"
    
    # Add 2 peach-shaped cams (intake & exhaust: width 14 mm each)
    # Cam 1 at X = 74 mm, Cam 2 at X = 157 mm
    for cx, angle in [(74.0, 0.0), (157.0, math.radians(104.0))]:
        bpy.ops.mesh.primitive_cylinder_add(radius=16.0, depth=14.0, location=(cx, 0, 0), vertices=32)
        cam_base = bpy.context.active_object
        cam_base.rotation_euler = (0, math.radians(90), 0)
        # Cam lobe
        bpy.ops.mesh.primitive_cylinder_add(radius=5.5, depth=14.0, location=(cx, 0, 14.0), vertices=24)
        lobe = bpy.context.active_object
        lobe.rotation_euler = (0, math.radians(90), 0)
        
        mod_l = cam_base.modifiers.new(name="Lobe", type='BOOLEAN')
        mod_l.operation = 'UNION'
        mod_l.object = lobe
        bpy.context.view_layer.objects.active = cam_base
        bpy.ops.object.modifier_apply(modifier="Lobe")
        bpy.data.objects.remove(lobe, do_unlink=True)
        
        cam_base.rotation_euler = (angle, 0, 0)
        mod_u = shaft.modifiers.new(name="Cam", type='BOOLEAN')
        mod_u.operation = 'UNION'
        mod_u.object = cam_base
        bpy.context.view_layer.objects.active = shaft
        bpy.ops.object.modifier_apply(modifier="Cam")
        bpy.data.objects.remove(cam_base, do_unlink=True)
        
    cut_keyway(shaft, center_x=17.5, top_z=20.0, length=35.0, width=10.0, depth=5.0)
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    return shaft

# ------------------------------------------------------------------------------
# 12. LJT03.23 轴 (Shaft)
# ------------------------------------------------------------------------------
def generate_ljt03_23():
    bcg.reset_scene()
    prof = [
        (0.0, 0.0), (0.0, 12.5), (45.0, 12.5),      # phi 25
        (45.0, 15.0), (95.0, 15.0),                 # phi 30
        (95.0, 17.5), (160.0, 17.5),                # phi 35
        (160.0, 15.0), (210.0, 15.0), (210.0, 0.0)  # phi 30
    ]
    obj = build_revolved_body(prof, segments=48)
    obj.name = "LJT03.23_轴"
    cut_keyway(obj, center_x=22.5, top_z=12.5, length=30.0, width=8.0, depth=4.0)
    cut_keyway(obj, center_x=127.5, top_z=17.5, length=40.0, width=10.0, depth=5.0)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    return obj

# ------------------------------------------------------------------------------
# 13. LJT03.25 主轴 (Spindle)
# ------------------------------------------------------------------------------
def generate_ljt03_25():
    bcg.reset_scene()
    prof = [
        (0.0, 0.0), (0.0, 34.9), (22.0, 34.9),       # Front flange phi 69.8
        (22.0, 22.5), (60.0, 22.5),                  # phi 45
        (60.0, 18.0), (78.0, 18.0),                  # M36x1.5
        (78.0, 16.5), (103.0, 16.5),                 # phi 33
        (103.0, 15.5), (196.0, 15.5),                # phi 31 body
        (196.0, 14.0), (237.0, 14.0),                # phi 28
        (237.0, 13.5), (252.0, 13.5),                # M27
        (252.0, 11.0), (265.0, 11.0), (265.0, 0.0)   # M22
    ]
    obj = build_revolved_body(prof, segments=48)
    obj.name = "LJT03.25_主轴"
    
    # Internal taper 7:24 bore (large dia 31.75 mm, depth 75 mm)
    bpy.ops.mesh.primitive_cone_add(radius1=31.75/2.0, radius2=17.0/2.0, depth=75.0, location=(37.5, 0, 0), vertices=32)
    cone = bpy.context.active_object
    cone.rotation_euler = (0, math.radians(-90), 0)
    
    # Internal through hole phi 16
    bpy.ops.mesh.primitive_cylinder_add(radius=8.0, depth=280.0, location=(140.0, 0, 0), vertices=32)
    bore = bpy.context.active_object
    bore.rotation_euler = (0, math.radians(90), 0)
    
    for c in [cone, bore]:
        mod = obj.modifiers.new(name="Bore", type='BOOLEAN')
        mod.operation = 'DIFFERENCE'
        mod.object = c
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier="Bore")
        bpy.data.objects.remove(c, do_unlink=True)
        
    cut_keyway(obj, center_x=90.0, top_z=16.5, length=20.0, width=6.0, depth=3.5)
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    return obj

# ------------------------------------------------------------------------------
# 14. LJT03.26 单拐曲轴 (Single-Throw Crankshaft)
# ------------------------------------------------------------------------------
def generate_ljt03_26():
    bcg.reset_scene()
    # Left main journal phi 70 x 40.5 mm
    bpy.ops.mesh.primitive_cylinder_add(radius=35.0, depth=40.5, location=(20.25, 0, 0), vertices=48)
    left_j = bpy.context.active_object
    left_j.rotation_euler = (0, math.radians(90), 0)
    
    # Crankweb 1 (thickness 29 mm)
    bpy.ops.mesh.primitive_cylinder_add(radius=55.0, depth=29.0, location=(40.5 + 14.5, 0, 28.75), vertices=48)
    web1 = bpy.context.active_object
    web1.rotation_euler = (0, math.radians(90), 0)
    
    # Crankpin (connecting rod journal) phi 65 x 38 mm offset by 57.5 mm in Z
    bpy.ops.mesh.primitive_cylinder_add(radius=32.5, depth=38.0, location=(40.5 + 29.0 + 19.0, 0, 57.5), vertices=48)
    pin = bpy.context.active_object
    pin.rotation_euler = (0, math.radians(90), 0)
    
    # Crankweb 2 (thickness 29 mm)
    bpy.ops.mesh.primitive_cylinder_add(radius=55.0, depth=29.0, location=(40.5 + 29.0 + 38.0 + 14.5, 0, 28.75), vertices=48)
    web2 = bpy.context.active_object
    web2.rotation_euler = (0, math.radians(90), 0)
    
    # Right main journal phi 70 x 40 mm
    bpy.ops.mesh.primitive_cylinder_add(radius=35.0, depth=40.0, location=(40.5 + 29.0 + 38.0 + 29.0 + 20.0, 0, 0), vertices=48)
    right_j = bpy.context.active_object
    right_j.rotation_euler = (0, math.radians(90), 0)
    
    # Output shaft with taper 1:10 (length 71 mm)
    bpy.ops.mesh.primitive_cylinder_add(radius=25.0, depth=71.0, location=(176.5 + 35.5, 0, 0), vertices=48)
    out_s = bpy.context.active_object
    out_s.rotation_euler = (0, math.radians(90), 0)
    
    # Union all parts
    main = left_j
    for part in [web1, pin, web2, right_j, out_s]:
        mod = main.modifiers.new(name="Union", type='BOOLEAN')
        mod.operation = 'UNION'
        mod.object = part
        bpy.context.view_layer.objects.active = main
        bpy.ops.object.modifier_apply(modifier="Union")
        bpy.data.objects.remove(part, do_unlink=True)
        
    main.name = "LJT03.26_单拐曲轴"
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    return main

# ------------------------------------------------------------------------------
# 15. LJT03.27 轴套 (Bushing)
# ------------------------------------------------------------------------------
def generate_ljt03_27():
    bcg.reset_scene()
    # Flanged bushing: outer phi 60, flange phi 100 x 10, total len = 72, bore = phi 44
    prof = [
        (0.0, 0.0), (0.0, 30.0), (62.0, 30.0),
        (62.0, 50.0), (72.0, 50.0), (72.0, 0.0)
    ]
    obj = build_revolved_body(prof, segments=48)
    obj.name = "LJT03.27_轴套"
    
    # Center bore phi 44
    bpy.ops.mesh.primitive_cylinder_add(radius=22.0, depth=100.0, location=(36.0, 0, 0), vertices=48)
    bore = bpy.context.active_object
    bore.rotation_euler = (0, math.radians(90), 0)
    mod = obj.modifiers.new(name="Bore", type='BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = bore
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier="Bore")
    bpy.data.objects.remove(bore, do_unlink=True)
    
    # 4 Flange bolt holes 4x phi 10 on PCD phi 80
    for i in range(4):
        ang = i * (math.pi / 2.0)
        by = 40.0 * math.cos(ang)
        bz = 40.0 * math.sin(ang)
        bpy.ops.mesh.primitive_cylinder_add(radius=5.0, depth=30.0, location=(67.0, by, bz), vertices=24)
        bh = bpy.context.active_object
        bh.rotation_euler = (0, math.radians(90), 0)
        mod_h = obj.modifiers.new(name=f"Hole_{i}", type='BOOLEAN')
        mod_h.operation = 'DIFFERENCE'
        mod_h.object = bh
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=f"Hole_{i}")
        bpy.data.objects.remove(bh, do_unlink=True)
        
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    return obj

# ------------------------------------------------------------------------------
# 16. LJT03.28 定位套 (Locating Sleeve)
# ------------------------------------------------------------------------------
def generate_ljt03_28():
    bcg.reset_scene()
    prof = [
        (0.0, 0.0), (0.0, 50.0), (15.0, 50.0),       # phi 100js6
        (15.0, 95.0), (48.0, 95.0),                  # Flange phi 190 (thick 33)
        (48.0, 55.0), (70.0, 55.0),                  # phi 110h6
        (70.0, 50.0), (160.0, 50.0),                 # phi 100
        (160.0, 40.0), (190.0, 40.0), (190.0, 0.0)   # M80x2
    ]
    obj = build_revolved_body(prof, segments=64)
    obj.name = "LJT03.28_定位套"
    
    # Internal bore phi 74
    bpy.ops.mesh.primitive_cylinder_add(radius=37.0, depth=220.0, location=(95.0, 0, 0), vertices=48)
    bore = bpy.context.active_object
    bore.rotation_euler = (0, math.radians(90), 0)
    mod = obj.modifiers.new(name="Bore", type='BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = bore
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier="Bore")
    bpy.data.objects.remove(bore, do_unlink=True)
    
    # Flat cut on bottom of flange to height 70 mm
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(31.5, 0, -85.0))
    flat_cutter = bpy.context.active_object
    flat_cutter.scale = (40.0, 220.0, 30.0)
    mod_f = obj.modifiers.new(name="Flat_Cut", type='BOOLEAN')
    mod_f.operation = 'DIFFERENCE'
    mod_f.object = flat_cutter
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier="Flat_Cut")
    bpy.data.objects.remove(flat_cutter, do_unlink=True)
    
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    return obj

# ------------------------------------------------------------------------------
# 17. LJT03.29 矩形花键套 (Spline Sleeve)
# ------------------------------------------------------------------------------
def generate_ljt03_29():
    bcg.reset_scene()
    prof = [
        (0.0, 0.0), (0.0, 31.0), (25.0, 31.0),       # phi 62 end
        (25.0, 36.0), (135.0, 36.0),                 # phi 72 center
        (135.0, 31.0), (160.0, 31.0), (160.0, 0.0)   # phi 62 end
    ]
    obj = build_revolved_body(prof, segments=48)
    obj.name = "LJT03.29_矩形花键套"
    
    # Internal bore phi 42
    bpy.ops.mesh.primitive_cylinder_add(radius=21.0, depth=180.0, location=(80.0, 0, 0), vertices=48)
    bore = bpy.context.active_object
    bore.rotation_euler = (0, math.radians(90), 0)
    mod = obj.modifiers.new(name="Bore", type='BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = bore
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier="Bore")
    bpy.data.objects.remove(bore, do_unlink=True)
    
    # 8 internal spline keyways: 8x42x48x8 EQS
    for i in range(8):
        ang = i * (2.0 * math.pi / 8.0)
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(80.0, 0, 0))
        c = bpy.context.active_object
        c.scale = (180.0, 8.0, 48.0)
        c.rotation_euler = (ang, 0, 0)
        mod_s = obj.modifiers.new(name=f"Key_{i}", type='BOOLEAN')
        mod_s.operation = 'DIFFERENCE'
        mod_s.object = c
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=f"Key_{i}")
        bpy.data.objects.remove(c, do_unlink=True)
        
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    return obj

# ------------------------------------------------------------------------------
# 18. LJT03.31 缸套 (Cylinder Liner)
# ------------------------------------------------------------------------------
def generate_ljt03_31():
    bcg.reset_scene()
    prof = [
        (0.0, 0.0), (0.0, 47.5), (15.0, 47.5),
        (15.0, 55.0), (30.0, 55.0),
        (30.0, 47.5), (145.0, 47.5), (145.0, 0.0)
    ]
    obj = build_revolved_body(prof, segments=48)
    obj.name = "LJT03.31_缸套"
    # Bore phi 80
    bpy.ops.mesh.primitive_cylinder_add(radius=40.0, depth=170.0, location=(72.5, 0, 0), vertices=48)
    bore = bpy.context.active_object
    bore.rotation_euler = (0, math.radians(90), 0)
    mod = obj.modifiers.new(name="Bore", type='BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = bore
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier="Bore")
    bpy.data.objects.remove(bore, do_unlink=True)
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    return obj

# ------------------------------------------------------------------------------
# 19. LJT03.32 定位螺套 (Locating Threaded Sleeve)
# ------------------------------------------------------------------------------
def generate_ljt03_32():
    bcg.reset_scene()
    prof = [
        (0.0, 0.0), (0.0, 22.0), (10.0, 22.0),       # Flange phi 44 x 10
        (10.0, 16.0), (75.0, 16.0), (75.0, 0.0)      # Body phi 32
    ]
    obj = build_revolved_body(prof, segments=48)
    obj.name = "LJT03.32_定位螺套"
    # Internal bore M20
    bpy.ops.mesh.primitive_cylinder_add(radius=10.0, depth=100.0, location=(37.5, 0, 0), vertices=32)
    bore = bpy.context.active_object
    bore.rotation_euler = (0, math.radians(90), 0)
    mod = obj.modifiers.new(name="Bore", type='BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = bore
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier="Bore")
    bpy.data.objects.remove(bore, do_unlink=True)
    
    # Wrench flats 24 mm on body
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(45.0, 0, 12.0 + 10.0))
    f1 = bpy.context.active_object
    f1.scale = (40.0, 50.0, 20.0)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(45.0, 0, -12.0 - 10.0))
    f2 = bpy.context.active_object
    f2.scale = (40.0, 50.0, 20.0)
    for f in [f1, f2]:
        mod = obj.modifiers.new(name="WrenchFlat", type='BOOLEAN')
        mod.operation = 'DIFFERENCE'
        mod.object = f
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier="WrenchFlat")
        bpy.data.objects.remove(f, do_unlink=True)
        
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    return obj

# ------------------------------------------------------------------------------
# 20. LJT03.34 套筒 (Sleeve)
# ------------------------------------------------------------------------------
def generate_ljt03_34():
    bcg.reset_scene()
    prof = [
        (0.0, 0.0), (0.0, 17.5), (90.0, 17.5),
        (90.0, 15.0), (110.0, 15.0), (110.0, 0.0)
    ]
    obj = build_revolved_body(prof, segments=48)
    obj.name = "LJT03.34_套筒"
    # Bore phi 20
    bpy.ops.mesh.primitive_cylinder_add(radius=10.0, depth=130.0, location=(55.0, 0, 0), vertices=32)
    bore = bpy.context.active_object
    bore.rotation_euler = (0, math.radians(90), 0)
    mod = obj.modifiers.new(name="Bore", type='BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = bore
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier="Bore")
    bpy.data.objects.remove(bore, do_unlink=True)
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    return obj

# ------------------------------------------------------------------------------
# 21. LJT03.35 套筒 (Flanged Sleeve)
# ------------------------------------------------------------------------------
def generate_ljt03_35():
    bcg.reset_scene()
    prof = [
        (0.0, 0.0), (0.0, 9.0), (22.0, 9.0),
        (22.0, 19.0), (28.0, 19.0),
        (28.0, 9.0), (62.0, 9.0), (62.0, 0.0)
    ]
    obj = build_revolved_body(prof, segments=48)
    obj.name = "LJT03.35_套筒"
    # Bore phi 12 x 47 mm
    bpy.ops.mesh.primitive_cylinder_add(radius=6.0, depth=47.0*2, location=(0, 0, 0), vertices=32)
    bore = bpy.context.active_object
    bore.rotation_euler = (0, math.radians(90), 0)
    mod = obj.modifiers.new(name="Bore", type='BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = bore
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier="Bore")
    bpy.data.objects.remove(bore, do_unlink=True)
    # End cross slot 3.5 mm x 12 mm
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(56.0, 0, 0))
    slot = bpy.context.active_object
    slot.scale = (12.0, 3.5, 25.0)
    mod_s = obj.modifiers.new(name="Slot", type='BOOLEAN')
    mod_s.operation = 'DIFFERENCE'
    mod_s.object = slot
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier="Slot")
    bpy.data.objects.remove(slot, do_unlink=True)
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    return obj

# ------------------------------------------------------------------------------
# 22. LJT03.36 柱塞套 (Plunger Sleeve)
# ------------------------------------------------------------------------------
def generate_ljt03_36():
    bcg.reset_scene()
    prof = [
        (0.0, 0.0), (0.0, 15.0), (40.0, 15.0),
        (40.0, 17.5), (90.0, 17.5), (90.0, 0.0)
    ]
    obj = build_revolved_body(prof, segments=48)
    obj.name = "LJT03.36_柱塞套"
    # Bore phi 16
    bpy.ops.mesh.primitive_cylinder_add(radius=8.0, depth=110.0, location=(45.0, 0, 0), vertices=32)
    bore = bpy.context.active_object
    bore.rotation_euler = (0, math.radians(90), 0)
    mod = obj.modifiers.new(name="Bore", type='BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = bore
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier="Bore")
    bpy.data.objects.remove(bore, do_unlink=True)
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    return obj

# ------------------------------------------------------------------------------
# 23. LJT03.37 连接套 (Connecting Sleeve)
# ------------------------------------------------------------------------------
def generate_ljt03_37():
    bcg.reset_scene()
    prof = [
        (0.0, 0.0), (0.0, 25.0), (25.0, 25.0),
        (25.0, 20.0), (60.0, 20.0),
        (60.0, 25.0), (85.0, 25.0), (85.0, 0.0)
    ]
    obj = build_revolved_body(prof, segments=48)
    obj.name = "LJT03.37_连接套"
    # Bore phi 30
    bpy.ops.mesh.primitive_cylinder_add(radius=15.0, depth=100.0, location=(42.5, 0, 0), vertices=32)
    bore = bpy.context.active_object
    bore.rotation_euler = (0, math.radians(90), 0)
    mod = obj.modifiers.new(name="Bore", type='BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = bore
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier="Bore")
    bpy.data.objects.remove(bore, do_unlink=True)
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    return obj

# ------------------------------------------------------------------------------
# 24. LJT03.38 双键套 (Double-Key Sleeve)
# ------------------------------------------------------------------------------
def generate_ljt03_38():
    bcg.reset_scene()
    prof = [
        (0.0, 0.0), (0.0, 20.0), (25.0, 20.0),
        (25.0, 26.0), (85.0, 26.0),
        (85.0, 22.0), (105.0, 22.0), (105.0, 0.0)
    ]
    obj = build_revolved_body(prof, segments=48)
    obj.name = "LJT03.38_双键套"
    # Bore phi 28
    bpy.ops.mesh.primitive_cylinder_add(radius=14.0, depth=120.0, location=(52.5, 0, 0), vertices=32)
    bore = bpy.context.active_object
    bore.rotation_euler = (0, math.radians(90), 0)
    mod = obj.modifiers.new(name="Bore", type='BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = bore
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier="Bore")
    bpy.data.objects.remove(bore, do_unlink=True)
    # Dual keyways on outside: 2x 8 mm wide
    cut_keyway(obj, center_x=55.0, top_z=26.0, length=40.0, width=8.0, depth=4.0)
    cut_keyway(obj, center_x=55.0, top_z=-26.0, length=40.0, width=8.0, depth=-4.0)
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    return obj

# ------------------------------------------------------------------------------
# 25. LJT03.39 轴套 (Valve Bushing)
# ------------------------------------------------------------------------------
def generate_ljt03_39():
    bcg.reset_scene()
    prof = [
        (0.0, 0.0), (0.0, 47.5), (274.0, 47.5),       # phi 95h6
        (274.0, 66.0), (294.0, 66.0), (294.0, 0.0)   # Flange phi 132 x 20
    ]
    obj = build_revolved_body(prof, segments=64)
    obj.name = "LJT03.39_轴套"
    # Bore phi 60
    bpy.ops.mesh.primitive_cylinder_add(radius=30.0, depth=320.0, location=(147.0, 0, 0), vertices=48)
    bore = bpy.context.active_object
    bore.rotation_euler = (0, math.radians(90), 0)
    mod = obj.modifiers.new(name="Bore", type='BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = bore
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier="Bore")
    bpy.data.objects.remove(bore, do_unlink=True)
    
    # 2 Cross radial oil ports phi 40
    bpy.ops.mesh.primitive_cylinder_add(radius=20.0, depth=120.0, location=(120.0, 0, 0), vertices=32)
    p1 = bpy.context.active_object
    mod_p = obj.modifiers.new(name="OilPort", type='BOOLEAN')
    mod_p.operation = 'DIFFERENCE'
    mod_p.object = p1
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier="OilPort")
    bpy.data.objects.remove(p1, do_unlink=True)
    
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    return obj

# ------------------------------------------------------------------------------
# 26. LJT03.40 空心套 (Hollow Sleeve)
# ------------------------------------------------------------------------------
def generate_ljt03_40():
    bcg.reset_scene()
    prof = [
        (0.0, 0.0), (0.0, 16.0), (120.0, 16.0), (120.0, 0.0)  # phi 32 x 120
    ]
    obj = build_revolved_body(prof, segments=48)
    obj.name = "LJT03.40_空心套"
    # Bore phi 20
    bpy.ops.mesh.primitive_cylinder_add(radius=10.0, depth=140.0, location=(60.0, 0, 0), vertices=32)
    bore = bpy.context.active_object
    bore.rotation_euler = (0, math.radians(90), 0)
    mod = obj.modifiers.new(name="Bore", type='BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = bore
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier="Bore")
    bpy.data.objects.remove(bore, do_unlink=True)
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    return obj

# ------------------------------------------------------------------------------
# Task Execution List
# ------------------------------------------------------------------------------
tasks = [
    ("LJT03.01", "LJT03.01_转轴", generate_ljt03_01, "machined_steel"),
    ("LJT03.02", "LJT03.02_手柄", generate_ljt03_02, "machined_steel"),
    ("LJT03.03", "LJT03.03_阀杆", generate_ljt03_03, "machined_steel"),
    ("LJT03.14", "LJT03.14_滚子轴", generate_ljt03_14, "machined_steel"),
    ("LJT03.15", "LJT03.15_十字轴", generate_ljt03_15, "machined_steel"),
    ("LJT03.16", "LJT03.16_滑柱", generate_ljt03_16, "machined_steel"),
    ("LJT03.17", "LJT03.17_传动轴", generate_ljt03_17, "machined_steel"),
    ("LJT03.18", "LJT03.18_矩形花键轴", generate_ljt03_18, "machined_steel"),
    ("LJT03.20", "LJT03.20_齿轮轴", generate_ljt03_20, "machined_steel"),
    ("LJT03.21", "LJT03.21_锥齿轮轴", generate_ljt03_21, "machined_steel"),
    ("LJT03.22", "LJT03.22_凸轮轴", generate_ljt03_22, "cast_iron"),
    ("LJT03.23", "LJT03.23_轴", generate_ljt03_23, "machined_steel"),
    ("LJT03.25", "LJT03.25_主轴", generate_ljt03_25, "machined_steel"),
    ("LJT03.26", "LJT03.26_单拐曲轴", generate_ljt03_26, "machined_steel"),
    ("LJT03.27", "LJT03.27_轴套", generate_ljt03_27, "bronze"),
    ("LJT03.28", "LJT03.28_定位套", generate_ljt03_28, "machined_steel"),
    ("LJT03.29", "LJT03.29_矩形花键套", generate_ljt03_29, "machined_steel"),
    ("LJT03.31", "LJT03.31_缸套", generate_ljt03_31, "cast_iron"),
    ("LJT03.32", "LJT03.32_定位螺套", generate_ljt03_32, "machined_steel"),
    ("LJT03.34", "LJT03.34_套筒", generate_ljt03_34, "machined_steel"),
    ("LJT03.35", "LJT03.35_套筒", generate_ljt03_35, "machined_steel"),
    ("LJT03.36", "LJT03.36_柱塞套", generate_ljt03_36, "machined_steel"),
    ("LJT03.37", "LJT03.37_连接套", generate_ljt03_37, "machined_steel"),
    ("LJT03.38", "LJT03.38_双键套", generate_ljt03_38, "machined_steel"),
    ("LJT03.39", "LJT03.39_轴套", generate_ljt03_39, "bronze"),
    ("LJT03.40", "LJT03.40_空心套", generate_ljt03_40, "machined_steel"),
]

print(f"=== Category 03 Batch Runner: Generating {len(tasks)} Models ===")

for idx, (code, name, func, mat) in enumerate(tasks):
    blend_path = os.path.join(cat_dir, f"{name}.blend")
    render_path = os.path.join(renders_dir, f"{name}.png")
    print(f"\n[{idx+1}/{len(tasks)}] Generating {code}: {name}...")
    try:
        obj = func()
        bcg.render_and_save(obj, blend_path, render_path, mat_type=mat)
        print(f"   [DONE] Generated and saved {name}.blend")
    except Exception as e:
        print(f"   [ERROR] Failed to generate {code}: {e}")
        import traceback
        traceback.print_exc()

print("\n=== Category 03 Batch Generation Completed ===")
