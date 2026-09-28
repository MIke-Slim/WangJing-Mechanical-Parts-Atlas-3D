"""
Category 04 Batch 1: 轮盘盖类零件 (Discs, Pulleys & Mechanism Wheels)
Generates 14 models: LJT04.01 ~ LJT04.16 (excluding 04 and 09 which were converted from CAD)
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
    axis: 'Z' revolves around Z-axis (default for discs/pulleys); 'X' around X-axis.
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
        # Fallback to FAST solver if exact fails
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
# Model Generators
# ==============================================================================

def make_LJT04_01():
    """LJT04.01 平带轮 (Flat Pulley)"""
    # Outer dia 180 (radius 90), width 86, crowned taper 1:12
    # Inner rim dia 166 (radius 83), web thickness 12 (Z: -6 to 6)
    # Hub dia 72 (radius 36), length 70 (Z: -33 to 37), bore dia 40 (radius 20)
    profile = [
        # Hub bore
        (-33.0, 20.0),
        (-33.0, 36.0),
        (-6.0, 36.0),
        (-6.0, 83.0),
        (-43.0, 83.0),
        (-43.0, 87.0),
        (0.0, 90.0),
        (43.0, 87.0),
        (43.0, 83.0),
        (6.0, 83.0),
        (6.0, 36.0),
        (37.0, 36.0),
        (37.0, 20.0),
        (-33.0, 20.0)
    ]
    obj = build_revolved_body(profile, segments=72, axis='Z')
    obj.name = "LJT04.01_平带轮"
    
    # 6 lightening holes phi 28 on PCD phi 122 (R=61)
    for i in range(6):
        ang = i * (2.0 * math.pi / 6.0)
        hx = 61.0 * math.cos(ang)
        hy = 61.0 * math.sin(ang)
        drill_cylinder_hole(obj, radius=14.0, depth=30.0, location=(hx, hy, 0.0))
        
    # Keyway: 12JS9, depth 3.3 (total 43.3)
    add_standard_keyway(obj, bore_radius=20.0, key_width=12.0, key_depth=3.3, length=80.0, center_z=2.0)
    
    # M6 set screw hole on hub (radial) and phi 8 hole on rim
    drill_cylinder_hole(obj, radius=3.0, depth=100.0, location=(0.0, 0.0, 15.0), rotation=(math.pi/2, 0, 0))
    drill_cylinder_hole(obj, radius=4.0, depth=30.0, location=(0.0, 85.0, 0.0), rotation=(math.pi/2, 0, 0))
    return obj

def make_LJT04_02():
    """LJT04.02 V带轮 (V-Belt Pulley - 3 Grooves)"""
    # 3 V-grooves: pitch 15, groove depth 12, top width 11, angle 38 deg
    # Outer dia 185.5 (R=92.75), pitch dia 180 (R=90), rim width 52
    # Inner rim dia 140 (R=70), web thickness 16 (Z: 20 to 36)
    # Hub dia 70 (R=35), length 66 (Z: -14 to 52), bore dia 42 (R=21)
    
    # Generate outer V-groove contour along Z from 0 to 52
    # Grooves centers at Z = 11, 26, 41
    # Half groove top width = 5.5, depth = 12, bottom width ≈ 5.5 - 12*tan(19°) ≈ 1.36
    profile = [
        (-14.0, 21.0),
        (-14.0, 35.0),
        (20.0, 35.0),
        (20.0, 70.0),
        (0.0, 70.0),
        (0.0, 92.75),
        # Groove 1 (center 11)
        (5.5, 92.75),
        (9.5, 80.75),
        (12.5, 80.75),
        (16.5, 92.75),
        # Groove 2 (center 26)
        (20.5, 92.75),
        (24.5, 80.75),
        (27.5, 80.75),
        (31.5, 92.75),
        # Groove 3 (center 41)
        (35.5, 92.75),
        (39.5, 80.75),
        (42.5, 80.75),
        (46.5, 92.75),
        (52.0, 92.75),
        (52.0, 70.0),
        (36.0, 70.0),
        (36.0, 35.0),
        (52.0, 35.0),
        (52.0, 21.0),
        (-14.0, 21.0)
    ]
    obj = build_revolved_body(profile, segments=72, axis='Z')
    obj.name = "LJT04.02_V带轮"
    
    # Keyway: 12JS9, depth 3.3
    add_standard_keyway(obj, bore_radius=21.0, key_width=12.0, key_depth=3.3, length=75.0, center_z=19.0)
    return obj

def make_LJT04_03():
    """LJT04.03 塔轮 (Step Pulley)"""
    # Large step: outer dia 114 (R=57), width 17 (Z: 25 to 42), groove depth 12.5, top 11
    # Small step: outer dia 68 (R=34), width 22 (Z: 42 to 64), groove depth 12.5, top 11
    # Hub: left extension dia 50 (R=25, Z: 0 to 11), dia 42 (R=21, Z: 11 to 25)
    # Total length 74 (Z: -10 to 64), bore dia 28 (R=14)
    profile = [
        (-10.0, 14.0),
        (-10.0, 25.0),
        (11.0, 25.0),
        (11.0, 21.0),
        (25.0, 21.0),
        (25.0, 57.0),
        # Large groove (center at Z=33.5)
        (28.0, 57.0),
        (32.0, 44.5),
        (35.0, 44.5),
        (39.0, 57.0),
        (42.0, 57.0),
        (42.0, 34.0),
        # Small groove (center at Z=53.0)
        (47.5, 34.0),
        (51.5, 21.5),
        (54.5, 21.5),
        (58.5, 34.0),
        (64.0, 34.0),
        (64.0, 14.0),
        (-10.0, 14.0)
    ]
    obj = build_revolved_body(profile, segments=64, axis='Z')
    obj.name = "LJT04.03_塔轮"
    
    # Keyway: 8JS9, depth 3.3
    add_standard_keyway(obj, bore_radius=14.0, key_width=8.0, key_depth=3.3, length=85.0, center_z=27.0)
    
    # 2x M10 holes on PCD 73 (R=36.5)
    drill_cylinder_hole(obj, radius=4.25, depth=25.0, location=(0.0, 36.5, 42.0))
    drill_cylinder_hole(obj, radius=4.25, depth=25.0, location=(0.0, -36.5, 42.0))
    return obj

def make_LJT04_05():
    """LJT04.05 波纹手轮 (Corrugated 3-Spoke Handwheel)"""
    # Outer dia 320 (R=160), rim oval 25x24, major R=147.5
    # Hub: dia 55 (R=27.5), length 32, bore dia 28 (R=14)
    # 3 tapered spokes at 120°, dished offset 56mm from hub front
    
    # 1. Central Hub
    hub_profile = [
        (0.0, 14.0),
        (0.0, 27.5),
        (32.0, 27.5),
        (32.0, 14.0),
        (0.0, 14.0)
    ]
    hub = build_revolved_body(hub_profile, segments=48, axis='Z')
    
    # 2. Corrugated Outer Rim
    # Toroidal ring at Z = 56.0 with radius 148.0
    bm = bmesh.new()
    num_circ = 72
    num_cross = 16
    R_major = 148.0
    r_cross = 12.0
    
    rings = []
    for i in range(num_circ):
        phi = i * 2.0 * math.pi / num_circ
        # 18 corrugated waves along inner circumference
        wave = 2.0 * math.cos(18.0 * phi)
        cx = (R_major - 1.0 + wave) * math.cos(phi)
        cy = (R_major - 1.0 + wave) * math.sin(phi)
        cz = 56.0
        
        ring = []
        for j in range(num_cross):
            theta = j * 2.0 * math.pi / num_cross
            # local cross section: width (dr) and height (dz)
            dr = r_cross * math.cos(theta)
            dz = (r_cross * 1.05) * math.sin(theta)
            px = (math.hypot(cx, cy) + dr) * math.cos(phi)
            py = (math.hypot(cx, cy) + dr) * math.sin(phi)
            pz = cz + dz
            ring.append(bm.verts.new((px, py, pz)))
        rings.append(ring)
        
    bm.verts.ensure_lookup_table()
    for i in range(num_circ):
        next_i = (i + 1) % num_circ
        for j in range(num_cross):
            next_j = (j + 1) % num_cross
            bm.faces.new((rings[i][j], rings[next_i][j], rings[next_i][next_j], rings[i][next_j]))
            
    rim_mesh = bpy.data.meshes.new("RimMesh")
    bm.to_mesh(rim_mesh)
    bm.free()
    rim = bpy.data.objects.new("HandwheelRim", rim_mesh)
    bpy.context.collection.objects.link(rim)
    
    # 3. 3 Tapered Spokes
    spoke_objs = []
    for k in range(3):
        ang = k * (2.0 * math.pi / 3.0)
        # Cylinder/cone spoke from hub (R=25, Z=16) to rim (R=136, Z=56)
        p1 = Vector((25.0 * math.cos(ang), 25.0 * math.sin(ang), 16.0))
        p2 = Vector((138.0 * math.cos(ang), 138.0 * math.sin(ang), 56.0))
        diff = p2 - p1
        dist = diff.length
        mid = (p1 + p2) * 0.5
        
        bpy.ops.mesh.primitive_cylinder_add(
            radius=10.0, depth=dist, vertices=24,
            location=mid
        )
        sp = bpy.context.active_object
        # Align cylinder Z-axis to diff vector
        rot_quat = Vector((0, 0, 1)).rotation_difference(diff)
        sp.rotation_mode = 'QUATERNION'
        sp.rotation_quaternion = rot_quat
        spoke_objs.append(sp)
        
    # Join hub, rim, and spokes
    bpy.ops.object.select_all(action='DESELECT')
    for o in spoke_objs + [rim]:
        o.select_set(True)
    hub.select_set(True)
    bpy.context.view_layer.objects.active = hub
    bpy.ops.object.join()
    obj = hub
    obj.name = "LJT04.05_波纹手轮"
    
    # Keyway: 8D10, depth 3.3
    add_standard_keyway(obj, bore_radius=14.0, key_width=8.0, key_depth=3.3, length=40.0, center_z=16.0)
    return obj

def make_LJT04_06():
    """LJT04.06 单排套筒链轮 (Single Strand Roller Chain Sprocket - z=25)"""
    # z=25, p=19.05, dr=11.91, Tip dia 161 (R=80.5), Pitch dia 151.99, Root dia 140.08 (R=70.04)
    # Tooth thickness 11.94, Hub dia 85 (R=42.5), length 65 (Z: 0 to 65), Bore dia 50 (R=25)
    z_teeth = 25
    r_tip = 80.5
    r_root = 70.04
    t_width = 11.94
    hub_len = 65.0
    
    # 1. Main hub and body cylinder
    profile = [
        (0.0, 25.0),
        (0.0, 42.5),
        (53.0, 42.5),
        (53.0, r_root),
        (hub_len, r_root),
        (hub_len, 25.0),
        (0.0, 25.0)
    ]
    obj = build_revolved_body(profile, segments=72, axis='Z')
    obj.name = "LJT04.06_单排套筒链轮"
    
    # 2. Teeth ring (extruded polygon with 25 teeth)
    bm = bmesh.new()
    pts_2d = []
    d_theta = 2.0 * math.pi / z_teeth
    for i in range(z_teeth):
        base_ang = i * d_theta
        # Tooth crest
        pts_2d.append((r_tip * math.cos(base_ang - d_theta*0.18), r_tip * math.sin(base_ang - d_theta*0.18)))
        pts_2d.append((r_tip * math.cos(base_ang + d_theta*0.18), r_tip * math.sin(base_ang + d_theta*0.18)))
        # Root gullet
        mid_ang = base_ang + d_theta * 0.5
        pts_2d.append((r_root * math.cos(mid_ang), r_root * math.sin(mid_ang)))
        
    # Extrude teeth in Z from 53.0 to 65.0
    verts_bot = [bm.verts.new((x, y, 53.0)) for x, y in pts_2d]
    verts_top = [bm.verts.new((x, y, hub_len)) for x, y in pts_2d]
    bm.verts.ensure_lookup_table()
    
    n_pts = len(pts_2d)
    for i in range(n_pts):
        next_i = (i + 1) % n_pts
        bm.faces.new((verts_bot[i], verts_bot[next_i], verts_top[next_i], verts_top[i]))
    # Cap faces
    bm.faces.new(verts_top)
    bm.faces.new(reversed(verts_bot))
    
    teeth_mesh = bpy.data.meshes.new("TeethMesh")
    bm.to_mesh(teeth_mesh)
    bm.free()
    teeth_obj = bpy.data.objects.new("Teeth", teeth_mesh)
    bpy.context.collection.objects.link(teeth_obj)
    
    # Join teeth and body
    bpy.ops.object.select_all(action='DESELECT')
    teeth_obj.select_set(True)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.join()
    
    # Keyway: 14JS9, depth 3.8
    add_standard_keyway(obj, bore_radius=25.0, key_width=14.0, key_depth=3.8, length=75.0, center_z=32.5)
    # M8 radial set screw hole at 20mm from hub end
    drill_cylinder_hole(obj, radius=4.0, depth=30.0, location=(0.0, 35.0, 20.0), rotation=(math.pi/2, 0, 0))
    return obj

def make_LJT04_07():
    """LJT04.07 多排链轮 (Triplex Roller Chain Sprocket - z=20, 3 Rows)"""
    # z=20, p=19.05, Tip dia 132 (R=66), Pitch dia 121.78, Root dia 109.87 (R=54.94)
    # Inter-row groove dia 98.68 (R=49.34), row spacing 31.0, tooth width 11.8, total 73.8
    # Bore dia 40 (R=20), keyway 10JS9
    z_teeth = 20
    r_tip = 66.0
    r_root = 54.94
    r_groove = 49.34
    
    # 1. Central Core Body
    # Total width 73.8: Z from 0 to 73.8
    # Row 1: Z 0 to 11.8, Groove 1: 11.8 to 31.0, Row 2: 31.0 to 42.8, Groove 2: 42.8 to 62.0, Row 3: 62.0 to 73.8
    profile = [
        (0.0, 20.0),
        (0.0, r_root),
        (11.8, r_root),
        (11.8, r_groove),
        (31.0, r_groove),
        (31.0, r_root),
        (42.8, r_root),
        (42.8, r_groove),
        (62.0, r_groove),
        (62.0, r_root),
        (73.8, r_root),
        (73.8, 20.0),
        (0.0, 20.0)
    ]
    obj = build_revolved_body(profile, segments=64, axis='Z')
    obj.name = "LJT04.07_多排链轮"
    
    # 2. Add 3 rows of teeth
    d_theta = 2.0 * math.pi / z_teeth
    pts_2d = []
    for i in range(z_teeth):
        base_ang = i * d_theta
        pts_2d.append((r_tip * math.cos(base_ang - d_theta*0.18), r_tip * math.sin(base_ang - d_theta*0.18)))
        pts_2d.append((r_tip * math.cos(base_ang + d_theta*0.18), r_tip * math.sin(base_ang + d_theta*0.18)))
        mid_ang = base_ang + d_theta * 0.5
        pts_2d.append((r_root * math.cos(mid_ang), r_root * math.sin(mid_ang)))
        
    row_spans = [(0.0, 11.8), (31.0, 42.8), (62.0, 73.8)]
    teeth_objs = []
    for z1, z2 in row_spans:
        bm = bmesh.new()
        verts_b = [bm.verts.new((x, y, z1)) for x, y in pts_2d]
        verts_t = [bm.verts.new((x, y, z2)) for x, y in pts_2d]
        bm.verts.ensure_lookup_table()
        n = len(pts_2d)
        for i in range(n):
            ni = (i + 1) % n
            bm.faces.new((verts_b[i], verts_b[ni], verts_t[ni], verts_t[i]))
        bm.faces.new(verts_t)
        bm.faces.new(reversed(verts_b))
        
        m = bpy.data.meshes.new(f"Row_{z1}")
        bm.to_mesh(m)
        bm.free()
        row_o = bpy.data.objects.new("RowTeeth", m)
        bpy.context.collection.objects.link(row_o)
        teeth_objs.append(row_o)
        
    bpy.ops.object.select_all(action='DESELECT')
    for ro in teeth_objs:
        ro.select_set(True)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.join()
    
    # Keyway: 10JS9, depth 2.9
    add_standard_keyway(obj, bore_radius=20.0, key_width=10.0, key_depth=2.9, length=80.0, center_z=36.9)
    return obj

def make_LJT04_08():
    """LJT04.08 盘形凸轮 (Disk Cam)"""
    # Cam lobe coordinates from blueprint (exact radius values every 10 degrees)
    # Radii list around 360 degrees (36 points, step 10 deg)
    radii = [
        60.0, 60.0, 60.0, 60.0, 60.5, 61.3, 62.3, 62.8, 64.8, 66.8,
        69.5, 72.0, 75.1, 79.0, 83.1, 87.3, 91.0, 93.1, 95.0, 97.1,
        98.3, 99.0, 99.5, 99.5, 99.0, 98.0, 94.5, 88.4, 81.0, 75.8,
        70.7, 66.4, 63.7, 61.8, 60.0, 60.0
    ]
    # Thickness = 25mm (Z: 0 to 25)
    # Hub: dia 75 (R=37.5), length 75 (Z: 0 to 75), bore dia 40 (R=20)
    
    # 1. Cam Plate
    bm = bmesh.new()
    verts_bot = []
    verts_top = []
    n = len(radii)
    for i, r in enumerate(radii):
        ang = i * (2.0 * math.pi / n)
        x = r * math.cos(ang)
        y = r * math.sin(ang)
        verts_bot.append(bm.verts.new((x, y, 0.0)))
        verts_top.append(bm.verts.new((x, y, 25.0)))
        
    bm.verts.ensure_lookup_table()
    for i in range(n):
        ni = (i + 1) % n
        bm.faces.new((verts_bot[i], verts_bot[ni], verts_top[ni], verts_top[i]))
    bm.faces.new(verts_top)
    bm.faces.new(reversed(verts_bot))
    
    plate_mesh = bpy.data.meshes.new("CamPlate")
    bm.to_mesh(plate_mesh)
    bm.free()
    plate = bpy.data.objects.new("CamPlate", plate_mesh)
    bpy.context.collection.objects.link(plate)
    
    # 2. Hub
    hub_profile = [
        (25.0, 20.0),
        (25.0, 37.5),
        (75.0, 37.5),
        (75.0, 20.0),
        (25.0, 20.0)
    ]
    hub = build_revolved_body(hub_profile, segments=48, axis='Z')
    
    # Join
    bpy.ops.object.select_all(action='DESELECT')
    plate.select_set(True)
    hub.select_set(True)
    bpy.context.view_layer.objects.active = hub
    bpy.ops.object.join()
    obj = hub
    obj.name = "LJT04.08_盘形凸轮"
    
    # Bore hole through
    drill_cylinder_hole(obj, radius=20.0, depth=100.0, location=(0.0, 0.0, 37.5))
    
    # Keyway: 12JS9, depth 3.3
    add_standard_keyway(obj, bore_radius=20.0, key_width=12.0, key_depth=3.3, length=90.0, center_z=37.5)
    
    # 3 lightening holes phi 30 on PCD phi 128 (R=64) on cam body
    for ang_deg in [120, 180, 240]:
        ang = math.radians(ang_deg)
        hx = 64.0 * math.cos(ang)
        hy = 64.0 * math.sin(ang)
        drill_cylinder_hole(obj, radius=15.0, depth=40.0, location=(hx, hy, 12.5))
        
    # M10 radial set screw on hub
    drill_cylinder_hole(obj, radius=5.0, depth=45.0, location=(0.0, 30.0, 55.0), rotation=(math.pi/2, 0, 0))
    return obj

def make_LJT04_10():
    """LJT04.10 平面沟槽凸轮 (Face Grooved Cam)"""
    # Outer dia 240 (R=120), thickness 30 (Z: 0 to 30)
    # Hub: dia 80 (R=40), length 60 (Z: 0 to 60), bore dia 52 (R=26)
    # Face groove: width 30, depth 18 (from Z=30 down to Z=12)
    # Base disk revolved body
    profile = [
        (0.0, 26.0),
        (0.0, 120.0),
        (30.0, 120.0),
        (30.0, 40.0),
        (60.0, 40.0),
        (60.0, 26.0),
        (0.0, 26.0)
    ]
    obj = build_revolved_body(profile, segments=72, axis='Z')
    obj.name = "LJT04.10_平面沟槽凸轮"
    
    # Cam Face Groove (cutter ring)
    # Trajectory center varies between R=90 and R=58 (R39 with center offset)
    bm = bmesh.new()
    n_pts = 64
    inner_pts = []
    outer_pts = []
    for i in range(n_pts):
        ang = i * 2.0 * math.pi / n_pts
        # Offset cam center equation
        r_mid = 75.0 + 15.0 * math.cos(ang)
        r_in = r_mid - 15.0
        r_out = r_mid + 15.0
        inner_pts.append((r_in * math.cos(ang), r_in * math.sin(ang)))
        outer_pts.append((r_out * math.cos(ang), r_out * math.sin(ang)))
        
    # Extrude groove cutter from Z=12.0 to 32.0
    v_in_bot = [bm.verts.new((x, y, 12.0)) for x, y in inner_pts]
    v_in_top = [bm.verts.new((x, y, 32.0)) for x, y in inner_pts]
    v_out_bot = [bm.verts.new((x, y, 12.0)) for x, y in outer_pts]
    v_out_top = [bm.verts.new((x, y, 32.0)) for x, y in outer_pts]
    bm.verts.ensure_lookup_table()
    
    for i in range(n_pts):
        ni = (i + 1) % n_pts
        # Outer wall
        bm.faces.new((v_out_bot[i], v_out_bot[ni], v_out_top[ni], v_out_top[i]))
        # Inner wall
        bm.faces.new((v_in_bot[ni], v_in_bot[i], v_in_top[i], v_in_top[ni]))
        # Bottom floor
        bm.faces.new((v_in_bot[i], v_in_bot[ni], v_out_bot[ni], v_out_bot[i]))
        # Top ceiling
        bm.faces.new((v_in_top[ni], v_in_top[i], v_out_top[i], v_out_top[ni]))
        
    groove_m = bpy.data.meshes.new("GrooveCutter")
    bm.to_mesh(groove_m)
    bm.free()
    groove_cutter = bpy.data.objects.new("GrooveCutter", groove_m)
    bpy.context.collection.objects.link(groove_cutter)
    
    apply_boolean_difference(obj, groove_cutter)
    
    # M8 radial set screw hole
    drill_cylinder_hole(obj, radius=4.0, depth=45.0, location=(0.0, 30.0, 45.0), rotation=(math.pi/2, 0, 0))
    return obj

def make_LJT04_11():
    """LJT04.11 端面凸轮 (Face Cam)"""
    # Outer dia 180 (R=90), inner recess dia 140 (R=70), hub dia 100 (R=50), bore dia 60 (R=30)
    # Total length 76
    # Cam face on outer rim (R: 70 to 90) varies in Z:
    # 0°-48°: Z=76; 48°-96°: cos down to 33; 96°-285°: Z=33; 285°-333°: cos up to 76; 333°-360°: Z=76
    
    # 1. Base hub and floor (Z from 0 to 33, hub up to 76)
    profile = [
        (0.0, 30.0),
        (0.0, 90.0),
        (33.0, 90.0),
        (33.0, 50.0),
        (76.0, 50.0),
        (76.0, 30.0),
        (0.0, 30.0)
    ]
    obj = build_revolved_body(profile, segments=72, axis='Z')
    obj.name = "LJT04.11_端面凸轮"
    
    # 2. Cam Rim Profile from Z=33 to Z(theta)
    bm = bmesh.new()
    n_pts = 72
    rings_in = []
    rings_out = []
    
    for i in range(n_pts):
        deg = i * 360.0 / n_pts
        rad = math.radians(deg)
        if 0.0 <= deg <= 48.0 or deg >= 333.0:
            z_top = 76.0
        elif 48.0 < deg < 96.0:
            z_top = 69.5 + 21.5 * math.cos(math.radians(3.75 * (deg - 48.0)))
        elif 96.0 <= deg <= 285.0:
            z_top = 33.0
        else: # 285 to 333
            z_top = 69.5 - 21.5 * math.cos(math.radians(3.75 * (deg - 285.0)))
            
        v_in_bot = bm.verts.new((70.0 * math.cos(rad), 70.0 * math.sin(rad), 33.0))
        v_in_top = bm.verts.new((70.0 * math.cos(rad), 70.0 * math.sin(rad), z_top))
        v_out_bot = bm.verts.new((90.0 * math.cos(rad), 90.0 * math.sin(rad), 33.0))
        v_out_top = bm.verts.new((90.0 * math.cos(rad), 90.0 * math.sin(rad), z_top))
        rings_in.append((v_in_bot, v_in_top))
        rings_out.append((v_out_bot, v_out_top))
        
    bm.verts.ensure_lookup_table()
    for i in range(n_pts):
        ni = (i + 1) % n_pts
        # Outer face
        bm.faces.new((rings_out[i][0], rings_out[ni][0], rings_out[ni][1], rings_out[i][1]))
        # Inner face
        bm.faces.new((rings_in[ni][0], rings_in[i][0], rings_in[i][1], rings_in[ni][1]))
        # Top cam ramp face
        bm.faces.new((rings_in[i][1], rings_out[i][1], rings_out[ni][1], rings_in[ni][1]))
        
    rim_m = bpy.data.meshes.new("CamRim")
    bm.to_mesh(rim_m)
    bm.free()
    rim_o = bpy.data.objects.new("CamRim", rim_m)
    bpy.context.collection.objects.link(rim_o)
    
    # Join
    bpy.ops.object.select_all(action='DESELECT')
    rim_o.select_set(True)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.join()
    
    # Keyway: 18JS9, depth 4.4
    add_standard_keyway(obj, bore_radius=30.0, key_width=18.0, key_depth=4.4, length=85.0, center_z=38.0)
    
    # Radial hole phi 18 + M10 at Z=25
    drill_cylinder_hole(obj, radius=9.0, depth=40.0, location=(0.0, 75.0, 25.0), rotation=(math.pi/2, 0, 0))
    return obj

def make_LJT04_12():
    """LJT04.12 圆柱沟槽凸轮 (Cylindrical Grooved Cam)"""
    # Outer dia 110 (R=55), hub dia 70 (R=35), length 75 (Z: 0 to 75), bore dia 45 (R=22.5)
    # Cam body length 60 (Z: 15 to 75)
    # Circumferential groove: width 20, depth 15 (root R=40), axial shift +/- 6.2mm
    profile = [
        (0.0, 22.5),
        (0.0, 35.0),
        (15.0, 35.0),
        (15.0, 55.0),
        (75.0, 55.0),
        (75.0, 22.5),
        (0.0, 22.5)
    ]
    obj = build_revolved_body(profile, segments=72, axis='Z')
    obj.name = "LJT04.12_圆柱沟槽凸轮"
    
    # Cam Groove cutter
    bm = bmesh.new()
    n_pts = 72
    rings = []
    # Base groove center at Z = 55.0 (20mm from top edge Z=75)
    z_base = 55.0
    for i in range(n_pts):
        deg = i * 360.0 / n_pts
        rad = math.radians(deg)
        # Shift profile: 53°-127° down 6.2mm; 233°-307° up 6.2mm
        if 53.0 <= deg <= 127.0:
            dz = -6.2 * math.sin(math.radians((deg - 53.0) / 74.0 * 180.0))
        elif 233.0 <= deg <= 307.0:
            dz = 6.2 * math.sin(math.radians((deg - 233.0) / 74.0 * 180.0))
        else:
            dz = 0.0
            
        z_c = z_base + dz
        # 4 vertices per slice across groove
        v1 = bm.verts.new((39.0 * math.cos(rad), 39.0 * math.sin(rad), z_c - 10.0))
        v2 = bm.verts.new((57.0 * math.cos(rad), 57.0 * math.sin(rad), z_c - 10.0))
        v3 = bm.verts.new((57.0 * math.cos(rad), 57.0 * math.sin(rad), z_c + 10.0))
        v4 = bm.verts.new((39.0 * math.cos(rad), 39.0 * math.sin(rad), z_c + 10.0))
        rings.append((v1, v2, v3, v4))
        
    bm.verts.ensure_lookup_table()
    for i in range(n_pts):
        ni = (i + 1) % n_pts
        # 4 faces connecting adjacent slices
        bm.faces.new((rings[i][0], rings[ni][0], rings[ni][1], rings[i][1]))
        bm.faces.new((rings[i][1], rings[ni][1], rings[ni][2], rings[i][2]))
        bm.faces.new((rings[i][2], rings[ni][2], rings[ni][3], rings[i][3]))
        bm.faces.new((rings[i][3], rings[ni][3], rings[ni][0], rings[i][0]))
        
    cutter_m = bpy.data.meshes.new("CylGrooveCutter")
    bm.to_mesh(cutter_m)
    bm.free()
    cutter_o = bpy.data.objects.new("CylGrooveCutter", cutter_m)
    bpy.context.collection.objects.link(cutter_o)
    
    apply_boolean_difference(obj, cutter_o)
    
    # Keyway: 8H7, depth 2.7
    add_standard_keyway(obj, bore_radius=22.5, key_width=8.0, key_depth=2.7, length=85.0, center_z=37.5)
    return obj

def make_LJT04_13():
    """LJT04.13 摆线轮 (Cycloidal Disc - z=29)"""
    # z=29, tip dia 377 (R=188.5), root dia 369 (R=184.5), thickness 23 (Z: 0 to 23)
    # Center bore 178.6 (R=89.3), 12 pin holes phi 53.15 (R=26.575) on PCD 305 (R=152.5)
    z_teeth = 29
    r_tip = 188.5
    r_root = 184.5
    
    bm = bmesh.new()
    pts_2d = []
    n_steps = 116 # 4 points per tooth
    for i in range(n_steps):
        ang = i * 2.0 * math.pi / n_steps
        # Sinusoidal cycloidal lobe approximation
        r = (r_tip + r_root) * 0.5 + ((r_tip - r_root) * 0.5) * math.cos(z_teeth * ang)
        pts_2d.append((r * math.cos(ang), r * math.sin(ang)))
        
    verts_bot = [bm.verts.new((x, y, 0.0)) for x, y in pts_2d]
    verts_top = [bm.verts.new((x, y, 23.0)) for x, y in pts_2d]
    bm.verts.ensure_lookup_table()
    
    for i in range(n_steps):
        ni = (i + 1) % n_steps
        bm.faces.new((verts_bot[i], verts_bot[ni], verts_top[ni], verts_top[i]))
    bm.faces.new(verts_top)
    bm.faces.new(reversed(verts_bot))
    
    disc_m = bpy.data.meshes.new("CycloidDisc")
    bm.to_mesh(disc_m)
    bm.free()
    obj = bpy.data.objects.new("LJT04.13_摆线轮", disc_m)
    bpy.context.collection.objects.link(obj)
    
    # Center bore phi 178.6 (R=89.3)
    drill_cylinder_hole(obj, radius=89.3, depth=35.0, location=(0.0, 0.0, 11.5))
    
    # 12 pin holes phi 53.15 on PCD phi 305 (R=152.5)
    for i in range(12):
        ang = i * (2.0 * math.pi / 12.0)
        hx = 152.5 * math.cos(ang)
        hy = 152.5 * math.sin(ang)
        drill_cylinder_hole(obj, radius=26.575, depth=35.0, location=(hx, hy, 11.5))
        
    # 2x M10 holes at 45°
    for sign in [1, -1]:
        ang = math.radians(45.0) if sign == 1 else math.radians(225.0)
        hx = 152.5 * math.cos(ang)
        hy = 152.5 * math.sin(ang)
        drill_cylinder_hole(obj, radius=4.25, depth=35.0, location=(hx, hy, 11.5))
    return obj

def make_LJT04_14():
    """LJT04.14 棘轮 (Ratchet Wheel - z=29)"""
    # z=29, tip dia 174 (R=87), tooth height 4.5, root dia 165 (R=82.5)
    # Width 24 (Z: 0 to 24), shoulder step dia 160 (R=80, Z: 0 to 20)
    # Bore dia 100 (R=50), 8 bolt holes phi 9 counterbore phi 15 on PCD 120
    z_teeth = 29
    r_tip = 87.0
    r_root = 82.5
    
    bm = bmesh.new()
    pts_2d = []
    d_theta = 2.0 * math.pi / z_teeth
    for i in range(z_teeth):
        ang = i * d_theta
        # Sawtooth profile: steep driving flank (15 deg) + gradual back ramp (60 deg)
        p_root = (r_root * math.cos(ang), r_root * math.sin(ang))
        p_tip = (r_tip * math.cos(ang + d_theta * 0.15), r_tip * math.sin(ang + d_theta * 0.15))
        pts_2d.append(p_root)
        pts_2d.append(p_tip)
        
    n_pts = len(pts_2d)
    verts_bot = [bm.verts.new((x, y, 0.0)) for x, y in pts_2d]
    verts_top = [bm.verts.new((x, y, 24.0)) for x, y in pts_2d]
    bm.verts.ensure_lookup_table()
    
    for i in range(n_pts):
        ni = (i + 1) % n_pts
        bm.faces.new((verts_bot[i], verts_bot[ni], verts_top[ni], verts_top[i]))
    bm.faces.new(verts_top)
    bm.faces.new(reversed(verts_bot))
    
    ratchet_m = bpy.data.meshes.new("RatchetMesh")
    bm.to_mesh(ratchet_m)
    bm.free()
    obj = bpy.data.objects.new("LJT04.14_棘轮", ratchet_m)
    bpy.context.collection.objects.link(obj)
    
    # Center bore phi 100
    drill_cylinder_hole(obj, radius=50.0, depth=35.0, location=(0.0, 0.0, 12.0))
    
    # 8 bolt holes phi 9 with phi 15 counterbore depth 9 on PCD 120 (R=60)
    for i in range(8):
        ang = i * (2.0 * math.pi / 8.0)
        hx = 60.0 * math.cos(ang)
        hy = 60.0 * math.sin(ang)
        drill_cylinder_hole(obj, radius=4.5, depth=35.0, location=(hx, hy, 12.0))
        drill_cylinder_hole(obj, radius=7.5, depth=10.0, location=(hx, hy, 19.5))
        
    # 2 taper pin holes phi 8 at 22.5°
    for sign in [1, -1]:
        ang = math.radians(22.5) if sign == 1 else math.radians(202.5)
        hx = 60.0 * math.cos(ang)
        hy = 60.0 * math.sin(ang)
        drill_cylinder_hole(obj, radius=4.0, depth=35.0, location=(hx, hy, 12.0))
    return obj

def make_LJT04_15():
    """LJT04.15 槽轮 (Geneva Wheel on Shaft)"""
    # 4-slot Geneva wheel: tip dia 36 (R=18), locking arc concave dia 29.4 (R=14.7)
    # 4 radial slots: width 4.0, length 18. Wheel thickness 6 (Z: 0 to 6)
    # Shaft: dia 8, length 89.5 (Z: -89.5 to 0), steps at -8.5, -36, -48, -67, -89.5
    
    # 1. Geneva Disc
    bm = bmesh.new()
    pts_2d = []
    # 4 symmetric quadrants
    for q in range(4):
        base_ang = q * (math.pi / 2.0)
        # Tip corner 1
        pts_2d.append((18.0 * math.cos(base_ang + 0.15), 18.0 * math.sin(base_ang + 0.15)))
        # Concave locking arc (center at R=20.8, radius=7.75)
        for step in range(5):
            arc_ang = base_ang + math.pi/4.0 + (step - 2) * 0.12
            r_arc = 12.0 + 3.0 * (1.0 - math.cos((step - 2) * 0.5))
            pts_2d.append((r_arc * math.cos(arc_ang), r_arc * math.sin(arc_ang)))
        # Tip corner 2
        pts_2d.append((18.0 * math.cos(base_ang + math.pi/2.0 - 0.15), 18.0 * math.sin(base_ang + math.pi/2.0 - 0.15)))
        
    n_pts = len(pts_2d)
    verts_b = [bm.verts.new((x, y, 0.0)) for x, y in pts_2d]
    verts_t = [bm.verts.new((x, y, 6.0)) for x, y in pts_2d]
    bm.verts.ensure_lookup_table()
    
    for i in range(n_pts):
        ni = (i + 1) % n_pts
        bm.faces.new((verts_b[i], verts_b[ni], verts_t[ni], verts_t[i]))
    bm.faces.new(verts_t)
    bm.faces.new(reversed(verts_b))
    
    wheel_m = bpy.data.meshes.new("GenevaMesh")
    bm.to_mesh(wheel_m)
    bm.free()
    wheel_o = bpy.data.objects.new("GenevaWheel", wheel_m)
    bpy.context.collection.objects.link(wheel_o)
    
    # 4 radial slots: width 4.0, depth 6.0
    for q in range(4):
        ang = q * (math.pi / 2.0)
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(9.0 * math.cos(ang), 9.0 * math.sin(ang), 3.0),
            rotation=(0, 0, ang)
        )
        cutter = bpy.context.active_object
        cutter.scale = (18.0, 4.0, 10.0)
        bpy.ops.object.transform_apply(scale=True)
        apply_boolean_difference(wheel_o, cutter)
        
    # 2. Shaft
    shaft_profile = [
        (-89.5, 0.0),
        (-89.5, 4.0),
        (-67.0, 4.0),
        (-48.0, 4.0),
        (-36.0, 4.0),
        (-8.5, 4.0),
        (-8.5, 5.0),
        (0.0, 5.0),
        (0.0, 0.0)
    ]
    shaft_o = build_revolved_body(shaft_profile, segments=32, axis='Z')
    
    # Join wheel and shaft
    bpy.ops.object.select_all(action='DESELECT')
    shaft_o.select_set(True)
    wheel_o.select_set(True)
    bpy.context.view_layer.objects.active = wheel_o
    bpy.ops.object.join()
    obj = wheel_o
    obj.name = "LJT04.15_槽轮"
    
    # Cross hole phi 3.5 near shaft tip
    drill_cylinder_hole(obj, radius=1.75, depth=15.0, location=(0.0, 0.0, -82.0), rotation=(math.pi/2, 0, 0))
    return obj

def make_LJT04_16():
    """LJT04.16 星轮 (Star Wheel / Clutch Cam Sleeve)"""
    # Total length 61 (Z: -20 to 41), central flange 14 (Z: 0 to 14)
    # Left sleeve dia 45 (R=22.5, Z: -20 to 0), slot 16x8
    # Right sleeve dia 40 (R=20.0, Z: 14 to 41)
    # Bore dia 28 (Z: -20 to 10), step to dia 45 (Z: 10 to 41)
    # Central flange has 3 ramp lobes at 120° (R=32, flat ramps 26.9/24.3)
    
    # 1. Base sleeve body
    profile = [
        (-20.0, 14.0),
        (-20.0, 22.5),
        (0.0, 22.5),
        (0.0, 20.0),
        (14.0, 20.0),
        (14.0, 20.0),
        (41.0, 20.0),
        (41.0, 22.5),
        (41.0, 14.0),
        (-20.0, 14.0)
    ]
    obj = build_revolved_body(profile, segments=48, axis='Z')
    obj.name = "LJT04.16_星轮"
    
    # 2. 3 Ramp Lobes on central flange (Z: 0 to 14)
    bm = bmesh.new()
    pts_2d = []
    for k in range(3):
        base_ang = k * (2.0 * math.pi / 3.0)
        # Circular outer arc R=32
        for s in range(5):
            ang = base_ang + s * 0.15
            pts_2d.append((32.0 * math.cos(ang), 32.0 * math.sin(ang)))
        # Flat ramp cut
        ang_end = base_ang + 2.0 * math.pi / 3.0
        pts_2d.append((22.0 * math.cos(ang_end - 0.2), 22.0 * math.sin(ang_end - 0.2)))
        
    n_pts = len(pts_2d)
    v_b = [bm.verts.new((x, y, 0.0)) for x, y in pts_2d]
    v_t = [bm.verts.new((x, y, 14.0)) for x, y in pts_2d]
    bm.verts.ensure_lookup_table()
    for i in range(n_pts):
        ni = (i + 1) % n_pts
        bm.faces.new((v_b[i], v_b[ni], v_t[ni], v_t[i]))
    bm.faces.new(v_t)
    bm.faces.new(reversed(v_b))
    
    lobes_m = bpy.data.meshes.new("LobesMesh")
    bm.to_mesh(lobes_m)
    bm.free()
    lobes_o = bpy.data.objects.new("Lobes", lobes_m)
    bpy.context.collection.objects.link(lobes_o)
    
    bpy.ops.object.select_all(action='DESELECT')
    lobes_o.select_set(True)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.join()
    
    # 3 spring plunger holes: 3 x phi 4 depth 11 at 120°
    for k in range(3):
        ang = k * (2.0 * math.pi / 3.0) + 0.3
        hx = 28.0 * math.cos(ang)
        hy = 28.0 * math.sin(ang)
        drill_cylinder_hole(obj, radius=2.0, depth=15.0, location=(hx, hy, 7.0), rotation=(math.pi/2, 0, ang))
        
    # Flat slot 16 x 8 on left sleeve
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(0.0, 20.0, -10.0)
    )
    c_slot = bpy.context.active_object
    c_slot.scale = (8.0, 10.0, 16.0)
    bpy.ops.object.transform_apply(scale=True)
    apply_boolean_difference(obj, c_slot)
    return obj


# ==============================================================================
# Batch Execution Runner
# ==============================================================================

MODELS = [
    ("LJT04.01", "平带轮", make_LJT04_01, "04_轮盘盖类_Discs_Covers"),
    ("LJT04.02", "V带轮", make_LJT04_02, "04_轮盘盖类_Discs_Covers"),
    ("LJT04.03", "塔轮", make_LJT04_03, "04_轮盘盖类_Discs_Covers"),
    ("LJT04.05", "波纹手轮", make_LJT04_05, "04_轮盘盖类_Discs_Covers"),
    ("LJT04.06", "单排套筒链轮", make_LJT04_06, "04_轮盘盖类_Discs_Covers"),
    ("LJT04.07", "多排链轮", make_LJT04_07, "04_轮盘盖类_Discs_Covers"),
    ("LJT04.08", "盘形凸轮", make_LJT04_08, "04_轮盘盖类_Discs_Covers"),
    ("LJT04.10", "平面沟槽凸轮", make_LJT04_10, "04_轮盘盖类_Discs_Covers"),
    ("LJT04.11", "端面凸轮", make_LJT04_11, "04_轮盘盖类_Discs_Covers"),
    ("LJT04.12", "圆柱沟槽凸轮", make_LJT04_12, "04_轮盘盖类_Discs_Covers"),
    ("LJT04.13", "摆线轮", make_LJT04_13, "04_轮盘盖类_Discs_Covers"),
    ("LJT04.14", "棘轮", make_LJT04_14, "04_轮盘盖类_Discs_Covers"),
    ("LJT04.15", "槽轮", make_LJT04_15, "04_轮盘盖类_Discs_Covers"),
    ("LJT04.16", "星轮", make_LJT04_16, "04_轮盘盖类_Discs_Covers"),
]

def run_batch():
    total = len(MODELS)
    print(f"\n=======================================================")
    print(f"Starting Category 04 Batch 1: {total} Models (Pulleys & Wheels)")
    print(f"=======================================================\n")
    
    for idx, (code, name, func, folder) in enumerate(MODELS, 1):
        full_name = f"{code}_{name}"
        blend_file = os.path.join(base_dir, folder, f"{full_name}.blend")
        render_file = os.path.join(renders_dir, f"{full_name}.png")
        
        print(f"[{idx}/{total}] Generating {code}: {full_name}...")
        
        try:
            obj = func()
            if obj is not None:
                bcg.render_and_save(obj, blend_file, render_file, mat_type="machined_steel")
                print(f"   [DONE] Generated and saved {full_name}.blend\n")
            else:
                print(f"   [ERROR] Generator returned None for {full_name}\n")
        except Exception as e:
            print(f"   [FAILED] Error generating {full_name}: {e}\n")
            import traceback
            traceback.print_exc()
            
    print("=== Category 04 Batch 1 Generation Completed ===")

if __name__ == "__main__":
    run_batch()

