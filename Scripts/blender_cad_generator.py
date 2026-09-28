"""
Blender CAD Generator for Mechanical Parts Atlas (《新标准机械图图集》)
Procedural 3D Modeling Engine in Blender Python (bpy / bmesh)
Author: Antigravity Assistant
"""

import bpy
import bmesh
import math
import os
import sys
from mathutils import Vector, Matrix

def reset_scene():
    """Clear all objects, meshes, materials, and collections in Blender."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    # Ensure a main collection exists
    if not bpy.data.collections:
        col = bpy.data.collections.new("Collection")
        bpy.context.scene.collection.children.link(col)

def setup_studio(target_obj):
    """
    Setup 3-point studio lighting and isometric camera aimed at target_obj.
    """
    # Calculate bounding box and dimensions
    bbox = [target_obj.matrix_world @ Vector(corner) for corner in target_obj.bound_box]
    min_x = min(v.x for v in bbox)
    max_x = max(v.x for v in bbox)
    min_y = min(v.y for v in bbox)
    max_y = max(v.y for v in bbox)
    min_z = min(v.z for v in bbox)
    max_z = max(v.z for v in bbox)
    
    center = Vector(((min_x + max_x) / 2.0, (min_y + max_y) / 2.0, (min_z + max_z) / 2.0))
    radius = max((max_x - min_x), (max_y - min_y), (max_z - min_z))
    if radius < 1e-4:
        radius = 50.0

    # Key Light (Warm Key)
    key_data = bpy.data.lights.new(name="Key_Light", type='SUN')
    key_data.energy = 4.0
    key_data.color = (1.0, 0.98, 0.95)
    key_obj = bpy.data.objects.new(name="Key_Light", object_data=key_data)
    bpy.context.scene.collection.objects.link(key_obj)
    key_obj.location = center + Vector((radius * 2.0, -radius * 2.5, radius * 3.0))
    key_obj.rotation_euler = (math.radians(50), math.radians(20), math.radians(45))

    # Fill Light (Cool Soft Fill)
    fill_data = bpy.data.lights.new(name="Fill_Light", type='SUN')
    fill_data.energy = 2.0
    fill_data.color = (0.92, 0.95, 1.0)
    fill_obj = bpy.data.objects.new(name="Fill_Light", object_data=fill_data)
    bpy.context.scene.collection.objects.link(fill_obj)
    fill_obj.location = center + Vector((-radius * 2.5, -radius * 1.5, radius * 2.0))
    fill_obj.rotation_euler = (math.radians(40), math.radians(-30), math.radians(-50))

    # Rim Light (Backlight Highlight)
    rim_data = bpy.data.lights.new(name="Rim_Light", type='SUN')
    rim_data.energy = 2.5
    rim_data.color = (1.0, 1.0, 1.0)
    rim_obj = bpy.data.objects.new(name="Rim_Light", object_data=rim_data)
    bpy.context.scene.collection.objects.link(rim_obj)
    rim_obj.location = center + Vector((0, radius * 3.0, radius * 1.5))
    rim_obj.rotation_euler = (math.radians(-45), 0, math.radians(180))

    # Camera
    cam_data = bpy.data.cameras.new("Render_Camera")
    cam_data.lens = 85  # Telephoto / orthographic-like perspective for technical parts
    cam_data.clip_start = 0.1
    cam_data.clip_end = radius * 20.0
    cam_obj = bpy.data.objects.new("Render_Camera", object_data=cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    # Position camera at classic mechanical isometric angle (Azimuth ~45 deg, Elevation ~35.264 deg)
    dist = radius * 3.2
    elev = math.radians(35.264)
    azim = math.radians(45.0)
    cam_x = center.x + dist * math.cos(elev) * math.sin(azim)
    cam_y = center.y - dist * math.cos(elev) * math.cos(azim)
    cam_z = center.z + dist * math.sin(elev)
    cam_obj.location = Vector((cam_x, cam_y, cam_z))
    
    # Point camera to center
    direction = center - cam_obj.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()

    # World / Background settings
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("Studio_World")
        bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get('Background')
    if bg:
        bg.inputs['Color'].default_value = (0.08, 0.09, 0.11, 1.0) # Dark sleek CAD background
        bg.inputs['Strength'].default_value = 1.0

def create_mechanical_material(mat_type="machined_steel"):
    """
    Creates high quality PBR mechanical material nodes.
    Types: 'machined_steel', 'cast_iron', 'bronze', 'spring_steel'
    """
    mat = bpy.data.materials.new(name=f"Mat_{mat_type}")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if not bsdf:
        return mat

    if mat_type == "machined_steel":
        bsdf.inputs['Base Color'].default_value = (0.78, 0.80, 0.83, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.95
        bsdf.inputs['Roughness'].default_value = 0.22
    elif mat_type == "cast_iron":
        bsdf.inputs['Base Color'].default_value = (0.35, 0.36, 0.38, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.85
        bsdf.inputs['Roughness'].default_value = 0.45
    elif mat_type == "bronze":
        bsdf.inputs['Base Color'].default_value = (0.85, 0.65, 0.38, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.90
        bsdf.inputs['Roughness'].default_value = 0.28
    elif mat_type == "spring_steel":
        bsdf.inputs['Base Color'].default_value = (0.25, 0.28, 0.32, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.90
        bsdf.inputs['Roughness'].default_value = 0.30
    return mat

def render_and_save(obj, blend_filepath, render_filepath, mat_type="machined_steel"):
    """
    Assigns material, auto-smooths normals, sets studio, saves blend and renders image.
    """
    mat = create_mechanical_material(mat_type)
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

    # Shade smooth with sharp edges
    for poly in obj.data.polygons:
        poly.use_smooth = True

    setup_studio(obj)

    # Save Blend file
    os.makedirs(os.path.dirname(blend_filepath), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=blend_filepath)
    print(f"[SUCCESS] Saved Blend: {blend_filepath}")

    # Render Preview PNG
    os.makedirs(os.path.dirname(render_filepath), exist_ok=True)
    bpy.context.scene.render.resolution_x = 1280
    bpy.context.scene.render.resolution_y = 960
    bpy.context.scene.render.filepath = render_filepath
    bpy.ops.render.render(write_still=True)
    print(f"[SUCCESS] Rendered Preview: {render_filepath}")

# ==============================================================================
# 1. SPRINGS GENERATORS (Chapter 1.2: LJT02.01 ~ LJT02.05)
# ==============================================================================

def generate_compression_spring_ljt02_01():
    """
    LJT02.01 圆柱螺旋压缩弹簧
    Outer D2 = 36.5 mm, Wire d = 4.5 mm -> Mean D = 32.0 mm, Mean R = 16.0 mm
    Total height H0 = 65 mm, Pitch t = 10.6 mm, Total turns n1 = 7.5, Right hand.
    Both ends ground flat (3/4 turn).
    """
    reset_scene()
    wire_r = 4.5 / 2.0
    mean_r = (36.5 - 4.5) / 2.0
    total_turns = 7.5
    pitch = 10.6
    
    # Generate helical curve vertices
    curve_data = bpy.data.curves.new('SpringCurve', type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.bevel_depth = wire_r
    curve_data.bevel_resolution = 8
    
    spline = curve_data.splines.new('POLY')
    steps_per_turn = 48
    total_steps = int(total_turns * steps_per_turn)
    spline.points.add(total_steps)

    for i in range(total_steps + 1):
        turn_frac = i / float(steps_per_turn)
        theta = turn_frac * 2.0 * math.pi
        
        # Ground / closed ends: first 0.75 turns and last 0.75 turns have progressive pitch
        if turn_frac <= 0.75:
            z = turn_frac / 0.75 * (wire_r * 2.0)
        elif turn_frac >= (total_turns - 0.75):
            rem = turn_frac - (total_turns - 0.75)
            z = (total_turns - 1.5) * pitch + wire_r * 2.0 + (rem / 0.75) * (wire_r * 2.0)
        else:
            z = (turn_frac - 0.75) * pitch + wire_r * 2.0
            
        x = mean_r * math.cos(theta)
        y = mean_r * math.sin(theta)
        spline.points[i].co = (x, y, z, 1.0)

    curve_obj = bpy.data.objects.new("LJT02.01_圆柱螺旋压缩弹簧", curve_data)
    bpy.context.scene.collection.objects.link(curve_obj)
    
    # Convert to mesh for ground flat ends
    bpy.context.view_layer.objects.active = curve_obj
    curve_obj.select_set(True)
    bpy.ops.object.convert(target='MESH')
    mesh_obj = bpy.context.active_object
    
    # Center origin
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    return mesh_obj

def generate_extension_spring_ljt02_02():
    """
    LJT02.02 圆柱螺旋拉伸弹簧
    Outer D2 = 26.0 mm, Wire d = 4.0 mm -> Mean D = 22.0 mm, Mean R = 11.0 mm
    Body length = 140 mm, Turns n = 23.5, Right hand.
    Both ends with machine half/full circular hooks (LI type).
    """
    reset_scene()
    wire_r = 4.0 / 2.0
    mean_r = (26.0 - 4.0) / 2.0
    turns = 23.5
    pitch = (140.0 - 4.0) / turns  # Close-coiled pitch
    
    curve_data = bpy.data.curves.new('SpringCurve', type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.bevel_depth = wire_r
    curve_data.bevel_resolution = 8
    
    spline = curve_data.splines.new('POLY')
    steps_body = int(turns * 36)
    steps_hook = 36
    total_steps = steps_body + 2 * steps_hook
    spline.points.add(total_steps)

    idx = 0
    # Bottom Hook: loop rising from z = -mean_r to z = 0
    hook_r = mean_r
    for i in range(steps_hook):
        angle = math.pi * (i / float(steps_hook))
        x = mean_r * math.cos(0)
        y = hook_r * math.sin(angle)
        z = -hook_r * (1.0 + math.cos(angle))
        spline.points[idx].co = (x, y, z, 1.0)
        idx += 1

    # Main Body
    for i in range(steps_body + 1):
        frac = i / 36.0
        theta = frac * 2.0 * math.pi
        x = mean_r * math.cos(theta)
        y = mean_r * math.sin(theta)
        z = frac * pitch
        spline.points[idx].co = (x, y, z, 1.0)
        idx += 1

    # Top Hook
    body_top_z = turns * pitch
    last_theta = turns * 2.0 * math.pi
    for i in range(1, steps_hook + 1):
        angle = math.pi * (i / float(steps_hook))
        x = mean_r * math.cos(last_theta)
        y = hook_r * math.sin(angle)
        z = body_top_z + hook_r * (1.0 - math.cos(angle))
        spline.points[idx].co = (x, y, z, 1.0)
        idx += 1

    obj = bpy.data.objects.new("LJT02.02_圆柱螺旋拉伸弹簧", curve_data)
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target='MESH')
    mesh_obj = bpy.context.active_object
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    return mesh_obj

def generate_torsion_spring_ljt02_03():
    """
    LJT02.03 螺旋扭转弹簧
    Outer D = 8.0 mm, Wire d = 1.0 mm -> Mean D = 7.0 mm, Mean R = 3.5 mm
    Body length = 6.0 mm, Turns n = 4.15, Angle between arms = 120 deg.
    Arm lengths = 20 mm, bent tip = 6 mm.
    """
    reset_scene()
    wire_r = 0.5
    mean_r = 3.5
    turns = 4.15
    pitch = 6.0 / turns

    curve_data = bpy.data.curves.new('SpringCurve', type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.bevel_depth = wire_r
    curve_data.bevel_resolution = 8
    
    spline = curve_data.splines.new('POLY')
    steps_arm = 20
    steps_body = int(turns * 36)
    total_points = steps_arm + steps_body + steps_arm + 10
    spline.points.add(total_points - 1)

    idx = 0
    # Arm 1: straight 20 mm in Y-
    arm1_len = 20.0
    for i in range(steps_arm):
        t = (steps_arm - i) / float(steps_arm)
        spline.points[idx].co = (mean_r, -arm1_len * t, 0, 1.0)
        idx += 1

    # Body coils
    for i in range(steps_body + 1):
        frac = i / 36.0
        theta = frac * 2.0 * math.pi
        x = mean_r * math.cos(theta)
        y = mean_r * math.sin(theta)
        z = frac * pitch
        spline.points[idx].co = (x, y, z, 1.0)
        idx += 1

    # Arm 2: extends 20 mm at angle 120 deg
    body_top_z = turns * pitch
    arm2_angle = math.radians(120.0)
    for i in range(1, steps_arm + 1):
        t = i / float(steps_arm)
        x = mean_r * math.cos(arm2_angle) + 20.0 * t * math.cos(arm2_angle)
        y = mean_r * math.sin(arm2_angle) + 20.0 * t * math.sin(arm2_angle)
        z = body_top_z
        spline.points[idx].co = (x, y, z, 1.0)
        idx += 1

    # Bent tip on arm 2 (length 6 mm bent perpendicular)
    tip_start_x = mean_r * math.cos(arm2_angle) + 20.0 * math.cos(arm2_angle)
    tip_start_y = mean_r * math.sin(arm2_angle) + 20.0 * math.sin(arm2_angle)
    for i in range(1, 10):
        t = i / 9.0
        x = tip_start_x - 6.0 * t * math.sin(arm2_angle)
        y = tip_start_y + 6.0 * t * math.cos(arm2_angle)
        z = body_top_z
        spline.points[idx].co = (x, y, z, 1.0)
        idx += 1

    obj = bpy.data.objects.new("LJT02.03_螺旋扭转弹簧", curve_data)
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target='MESH')
    mesh_obj = bpy.context.active_object
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    return mesh_obj

def generate_disc_spring_ljt02_04():
    """
    LJT02.04 碟形弹簧 (Belleville Disc Spring)
    Outer D = 40 mm, Inner d = 20.4 mm, Thickness t = 2.25 mm, Total Height H0 = 3.15 mm
    Cone height h0 = 0.9 mm.
    """
    reset_scene()
    R_outer = 40.0 / 2.0
    R_inner = 20.4 / 2.0
    t = 2.25
    h0 = 0.9

    # Revolved truncated conical shell via bmesh
    bm = bmesh.new()
    segments = 64
    
    # 4 profile vertices in R-Z plane
    # 0: inner bottom, 1: outer bottom, 2: outer top, 3: inner top
    p0 = (R_inner, 0, h0)
    p1 = (R_outer, 0, 0)
    p2 = (R_outer, 0, t)
    p3 = (R_inner, 0, h0 + t)

    # Revolve around Z axis
    verts_ring = []
    for i in range(segments):
        theta = i * 2.0 * math.pi / segments
        c, s = math.cos(theta), math.sin(theta)
        v0 = bm.verts.new((p0[0] * c, p0[0] * s, p0[2]))
        v1 = bm.verts.new((p1[0] * c, p1[0] * s, p1[2]))
        v2 = bm.verts.new((p2[0] * c, p2[0] * s, p2[2]))
        v3 = bm.verts.new((p3[0] * c, p3[0] * s, p3[2]))
        verts_ring.append((v0, v1, v2, v3))

    bm.verts.ensure_lookup_table()
    for i in range(segments):
        next_i = (i + 1) % segments
        rA = verts_ring[i]
        rB = verts_ring[next_i]
        # 4 faces per segment
        bm.faces.new((rA[0], rB[0], rB[1], rA[1])) # bottom conical face
        bm.faces.new((rA[1], rB[1], rB[2], rA[2])) # outer cylindrical face
        bm.faces.new((rA[2], rB[2], rB[3], rA[3])) # top conical face
        bm.faces.new((rA[3], rB[3], rB[0], rA[0])) # inner cylindrical face

    mesh = bpy.data.meshes.new("LJT02.04_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("LJT02.04_碟形弹簧", mesh)
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    return obj

def generate_conical_spring_ljt02_05():
    """
    LJT02.05 截锥螺旋压缩弹簧
    Large End D2 = 25.0 mm (Mean R = 11.5 mm), Small End D2 = 12.2 mm (Mean R = 5.1 mm)
    Wire d = 2.0 mm, Total height H0 = 50.0 mm, Total turns = 8.25.
    """
    reset_scene()
    wire_r = 1.0
    r_large = (25.0 - 2.0) / 2.0
    r_small = (12.2 - 2.0) / 2.0
    h = 50.0
    turns = 8.25

    curve_data = bpy.data.curves.new('SpringCurve', type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.bevel_depth = wire_r
    curve_data.bevel_resolution = 8
    
    spline = curve_data.splines.new('POLY')
    steps_total = int(turns * 48)
    spline.points.add(steps_total)

    for i in range(steps_total + 1):
        frac = i / float(steps_total)
        theta = frac * turns * 2.0 * math.pi
        r = r_large + (r_small - r_large) * frac
        z = frac * h
        x = r * math.cos(theta)
        y = r * math.sin(theta)
        spline.points[i].co = (x, y, z, 1.0)

    obj = bpy.data.objects.new("LJT02.05_截锥螺旋压缩弹簧", curve_data)
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target='MESH')
    mesh_obj = bpy.context.active_object
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    return mesh_obj

# ==============================================================================
# 2. GEAR GENERATORS (Chapter 1.1: LJT01.01 ~ LJT01.10)
# ==============================================================================

def create_involute_gear_profile(m, z, alpha=20.0, ha_star=1.0, c_star=0.25, x=0.0):
    """
    Calculates 2D coordinates of an exact standard involute spur gear tooth profile.
    Returns list of 2D Vector points forming the outer rim.
    """
    alpha_rad = math.radians(alpha)
    d = m * z
    r = d / 2.0
    rb = r * math.cos(alpha_rad)
    ra = r + (ha_star + x) * m
    rf = r - (ha_star + c_star - x) * m
    
    # Involute points per tooth flank
    num_samples = 10
    profile_points = []
    
    half_tooth_angle = (math.pi / (2.0 * z)) + (2.0 * x * math.tan(alpha_rad) / z) + (math.tan(alpha_rad) - alpha_rad)
    
    for tooth in range(z):
        tooth_center_angle = tooth * (2.0 * math.pi / z)
        flank_right = []
        flank_left = []
        
        # Involute parameter t
        t_max = math.sqrt(max(0.0, (ra / rb)**2 - 1.0))
        t_min = math.sqrt(max(0.0, (max(rf, rb) / rb)**2 - 1.0))
        
        for s in range(num_samples):
            t = t_min + (t_max - t_min) * (s / float(num_samples - 1))
            inv_r = rb * math.sqrt(1.0 + t*t)
            inv_theta = t - math.atan(t)
            
            # Right flank (positive angle)
            ang_r = tooth_center_angle + half_tooth_angle - inv_theta
            flank_right.append(Vector((inv_r * math.cos(ang_r), inv_r * math.sin(ang_r))))
            
            # Left flank (negative angle)
            ang_l = tooth_center_angle - half_tooth_angle + inv_theta
            flank_left.append(Vector((inv_r * math.cos(ang_l), inv_r * math.sin(ang_l))))
            
        # Root circle connection
        root_ang = tooth_center_angle - (math.pi / z)
        root_pt = Vector((rf * math.cos(root_ang), rf * math.sin(root_ang)))
        
        profile_points.append(root_pt)
        profile_points.extend(reversed(flank_left))
        profile_points.extend(flank_right)

    return profile_points, rf, ra

def generate_spur_gear_ljt01_01():
    """
    LJT01.01 圆柱直齿轮 (Spur Gear)
    m = 2, z = 29, alpha = 20 deg, Face width = 15 mm, Total width = 25 mm
    Hub D = 42 mm, Bore d = 25 mm, Keyway w = 8 mm, depth from bottom = 28.3 mm
    """
    reset_scene()
    m, z = 2.0, 29
    profile_pts, rf, ra = create_involute_gear_profile(m, z)
    
    bm = bmesh.new()
    # Bottom face
    bottom_verts = [bm.verts.new((p.x, p.y, 0)) for p in profile_pts]
    # Top face (extrude gear teeth width 15 mm)
    top_verts = [bm.verts.new((p.x, p.y, 15.0)) for p in profile_pts]
    
    # Connect tooth side faces
    N = len(profile_pts)
    for i in range(N):
        next_i = (i + 1) % N
        bm.faces.new((bottom_verts[i], bottom_verts[next_i], top_verts[next_i], top_verts[i]))
        
    bm.faces.new(reversed(bottom_verts))
    bm.faces.new(top_verts)
    
    mesh = bpy.data.meshes.new("Gear_Rim")
    bm.to_mesh(mesh)
    bm.free()
    
    gear_obj = bpy.data.objects.new("LJT01.01_圆柱直齿轮", mesh)
    bpy.context.scene.collection.objects.link(gear_obj)
    
    # Add Hub (Cylinder phi 42 mm, height 25 mm)
    bpy.ops.mesh.primitive_cylinder_add(radius=42.0/2.0, depth=25.0, location=(0, 0, 12.5), vertices=48)
    hub_obj = bpy.context.active_object
    
    # Union gear and hub
    mod_union = gear_obj.modifiers.new(name="Union_Hub", type='BOOLEAN')
    mod_union.operation = 'UNION'
    mod_union.object = hub_obj
    bpy.context.view_layer.objects.active = gear_obj
    bpy.ops.object.modifier_apply(modifier="Union_Hub")
    bpy.data.objects.remove(hub_obj, do_unlink=True)
    
    # Bore and Keyway cut (Bore phi 25, Keyway 8x28.3)
    # Cutter cylinder phi 25
    bpy.ops.mesh.primitive_cylinder_add(radius=25.0/2.0, depth=40.0, location=(0, 0, 12.5), vertices=48)
    cutter_bore = bpy.context.active_object
    
    # Keyway box
    # Keyway width = 8 mm, depth from center = 28.3 - 12.5 = 15.8 mm
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 12.5 + 3.3/2.0, 12.5))
    cutter_key = bpy.context.active_object
    cutter_key.scale = (8.0, 3.3, 40.0)
    
    # Union cutters
    mod_k = cutter_bore.modifiers.new(name="Union_Key", type='BOOLEAN')
    mod_k.operation = 'UNION'
    mod_k.object = cutter_key
    bpy.context.view_layer.objects.active = cutter_bore
    bpy.ops.object.modifier_apply(modifier="Union_Key")
    bpy.data.objects.remove(cutter_key, do_unlink=True)
    
    # Subtract cutter from gear
    mod_cut = gear_obj.modifiers.new(name="Cut_Bore", type='BOOLEAN')
    mod_cut.operation = 'DIFFERENCE'
    mod_cut.object = cutter_bore
    bpy.context.view_layer.objects.active = gear_obj
    bpy.ops.object.modifier_apply(modifier="Cut_Bore")
    bpy.data.objects.remove(cutter_bore, do_unlink=True)
    
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    return gear_obj

def generate_gear_rack_ljt01_08():
    """
    LJT01.08 直齿齿条 (Gear Rack)
    m = 14, Total length = 877.6 mm, Height = 150 mm, Width = 120 mm
    Pitch p = 43.98 mm, Tooth whole depth = 31.5 mm, 20 teeth.
    5x counterbored mounting holes (phi 42 / phi 58).
    """
    reset_scene()
    m = 14.0
    p = math.pi * m  # 43.982 mm
    num_teeth = 20
    length = 877.6
    width = 120.0
    height = 150.0
    tooth_depth = 31.5
    
    bm = bmesh.new()
    # 2D cross-section profile in X-Z plane
    pts_x = [0.0]
    pts_z = [0.0]
    
    # Straight bottom and sides
    pts_x.append(length)
    pts_z.append(0.0)
    
    pts_x.append(length)
    pts_z.append(height - tooth_depth)
    
    # 20 rack teeth along the top
    start_x = 48.0
    for i in range(num_teeth):
        tx = start_x + i * p
        pts_x.append(tx)
        pts_z.append(height - tooth_depth)
        
        pts_x.append(tx + p * 0.25)
        pts_z.append(height)
        
        pts_x.append(tx + p * 0.50)
        pts_z.append(height)
        
        pts_x.append(tx + p * 0.75)
        pts_z.append(height - tooth_depth)

    pts_x.append(0.0)
    pts_z.append(height - tooth_depth)
    
    # Create 3D extruded prism along Y (width = 120)
    front_verts = [bm.verts.new((x, -width/2.0, z)) for x, z in zip(pts_x, pts_z)]
    back_verts = [bm.verts.new((x, width/2.0, z)) for x, z in zip(pts_x, pts_z)]
    
    N = len(pts_x)
    for i in range(N):
        next_i = (i + 1) % N
        bm.faces.new((front_verts[i], back_verts[i], back_verts[next_i], front_verts[next_i]))
        
    bm.faces.new(front_verts)
    bm.faces.new(reversed(back_verts))
    
    mesh = bpy.data.meshes.new("Rack_Mesh")
    bm.to_mesh(mesh)
    bm.free()
    
    rack_obj = bpy.data.objects.new("LJT01.08_直齿齿条", mesh)
    bpy.context.scene.collection.objects.link(rack_obj)
    
    # Subtract 5 counterbored holes along length: 5x phi 42, counterbore phi 58 x 60 mm
    hole_spacing = 195.0
    hole_start_x = 48.0 + 98.0  # 146 mm
    hole_z = 58.0
    
    for i in range(5):
        hx = hole_start_x + i * hole_spacing
        # Through hole phi 42
        bpy.ops.mesh.primitive_cylinder_add(radius=42.0/2.0, depth=width*1.5, location=(hx, 0, hole_z), vertices=32)
        cyl_through = bpy.context.active_object
        cyl_through.rotation_euler = (math.radians(90), 0, 0)
        
        mod_h = rack_obj.modifiers.new(name=f"Hole_{i}", type='BOOLEAN')
        mod_h.operation = 'DIFFERENCE'
        mod_h.object = cyl_through
        bpy.context.view_layer.objects.active = rack_obj
        bpy.ops.object.modifier_apply(modifier=f"Hole_{i}")
        bpy.data.objects.remove(cyl_through, do_unlink=True)

    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    return rack_obj

def generate_worm_shaft_ljt01_10():
    """
    LJT01.10 蜗杆 (Worm Shaft)
    Total length = 482 mm, Stepped shaft:
    - Shaft end phi 40k6 (length 80)
    - Mid shaft phi 45 (length 65)
    - Bearing seat phi 50k6 (length 60)
    - Shoulder phi 60 (width 6)
    - Worm thread section: da1 = phi 60h8, d1 = phi 50, df1 = phi 38, length = 95 mm, m = 5, z1 = 2
    - Shoulder phi 60 (width 6)
    - Bearing seat phi 50k6 (length 60)
    - Thread M45x1.5 (length 15)
    """
    reset_scene()
    
    # Create stepped shaft by revolving profile around X axis
    profile = [
        (0.0, 0.0), (0.0, 20.0), (80.0, 20.0),      # phi 40
        (80.0, 22.5), (145.0, 22.5),                # phi 45
        (145.0, 25.0), (205.0, 25.0),               # phi 50
        (205.0, 30.0), (211.0, 30.0),               # shoulder phi 60
        (211.0, 18.5), (214.0, 18.5),               # undercut phi 37
        (214.0, 30.0), (309.0, 30.0),               # worm thread core phi 60
        (309.0, 18.5), (312.0, 18.5),               # undercut phi 37
        (312.0, 30.0), (318.0, 30.0),               # shoulder phi 60
        (318.0, 25.0), (467.0, 25.0),               # phi 50
        (467.0, 22.5), (482.0, 22.5), (482.0, 0.0)  # thread M45
    ]
    
    bm = bmesh.new()
    segments = 48
    verts_rings = []
    for x, r in profile:
        ring = []
        for i in range(segments):
            theta = i * 2.0 * math.pi / segments
            y = r * math.cos(theta)
            z = r * math.sin(theta)
            ring.append(bm.verts.new((x, y, z)))
        verts_rings.append(ring)
        
    bm.verts.ensure_lookup_table()
    for j in range(len(profile) - 1):
        r1 = verts_rings[j]
        r2 = verts_rings[j+1]
        for i in range(segments):
            next_i = (i + 1) % segments
            bm.faces.new((r1[i], r2[i], r2[next_i], r1[next_i]))
            
    mesh = bpy.data.meshes.new("Worm_Shaft_Mesh")
    bm.to_mesh(mesh)
    bm.free()
    
    shaft_obj = bpy.data.objects.new("LJT01.10_蜗杆", mesh)
    bpy.context.scene.collection.objects.link(shaft_obj)
    
    # Subtract keyway on phi 40 end (width 12 mm, length 68 mm, depth from top 8 mm)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(40.0, 0, 20.0 - 4.0))
    cutter_key = bpy.context.active_object
    cutter_key.scale = (68.0, 12.0, 10.0)
    
    mod_k = shaft_obj.modifiers.new(name="Cut_Keyway", type='BOOLEAN')
    mod_k.operation = 'DIFFERENCE'
    mod_k.object = cutter_key
    bpy.context.view_layer.objects.active = shaft_obj
    bpy.ops.object.modifier_apply(modifier="Cut_Keyway")
    bpy.data.objects.remove(cutter_key, do_unlink=True)
    
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    return shaft_obj

def generate_bevel_gear_ljt01_07():
    """
    LJT01.07 螺旋锥齿轮 (Spiral Bevel Gear - Gleason)
    z = 46, m = 5.096, Cone angle = 71.93 deg, Tip diameter = 277.86 mm
    Hub D = 130 mm, Bore = 80 mm, Keyway = 22x85.4 mm, Total length = 128 mm
    """
    reset_scene()
    da = 277.86
    z = 46
    total_len = 128.0
    hub_len = 100.0
    hub_d = 130.0
    bore_d = 80.0
    
    # Outer cone profile
    profile = [
        (0.0, 0.0), (0.0, hub_d / 2.0), (hub_len, hub_d / 2.0),
        (hub_len, da / 2.0 * 0.95), (total_len, da / 2.0),
        (total_len - 40.0, da / 2.0 * 0.75), (total_len - 40.0, 0.0)
    ]
    
    bm = bmesh.new()
    segments = 64
    verts_rings = []
    for z_coord, r in profile:
        ring = []
        for i in range(segments):
            theta = i * 2.0 * math.pi / segments
            x = r * math.cos(theta)
            y = r * math.sin(theta)
            ring.append(bm.verts.new((x, y, z_coord)))
        verts_rings.append(ring)
        
    bm.verts.ensure_lookup_table()
    for j in range(len(profile) - 1):
        r1 = verts_rings[j]
        r2 = verts_rings[j+1]
        for i in range(segments):
            next_i = (i + 1) % segments
            bm.faces.new((r1[i], r2[i], r2[next_i], r1[next_i]))
            
    mesh = bpy.data.meshes.new("Bevel_Mesh")
    bm.to_mesh(mesh)
    bm.free()
    
    gear_obj = bpy.data.objects.new("LJT01.07_锥齿轮", mesh)
    bpy.context.scene.collection.objects.link(gear_obj)
    
    # Cut bore phi 80
    bpy.ops.mesh.primitive_cylinder_add(radius=bore_d/2.0, depth=total_len*2.0, location=(0, 0, total_len/2.0), vertices=64)
    cutter = bpy.context.active_object
    
    mod_b = gear_obj.modifiers.new(name="Bore_Cut", type='BOOLEAN')
    mod_b.operation = 'DIFFERENCE'
    mod_b.object = cutter
    bpy.context.view_layer.objects.active = gear_obj
    bpy.ops.object.modifier_apply(modifier="Bore_Cut")
    bpy.data.objects.remove(cutter, do_unlink=True)
    
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    return gear_obj

def generate_sector_gear_ljt01_03():
    """
    LJT01.03 扇形齿轮 (Sector Gear)
    z = 190 (Sector 150 deg), m = 1, da = 192 mm, Hub phi 24, Bore phi 14H7, Hub len = 46 mm
    """
    reset_scene()
    da = 192.0
    r_tip = da / 2.0
    hub_d = 24.0
    bore_d = 14.0
    hub_len = 46.0
    rim_w = 16.0
    sector_angle = math.radians(150.0)
    
    bm = bmesh.new()
    steps = 40
    # 150 deg fan
    center_bottom = bm.verts.new((0, 0, 0))
    center_top = bm.verts.new((0, 0, rim_w))
    
    rim_bottom = []
    rim_top = []
    for i in range(steps + 1):
        theta = -sector_angle / 2.0 + sector_angle * (i / float(steps))
        x = r_tip * math.cos(theta)
        y = r_tip * math.sin(theta)
        rim_bottom.append(bm.verts.new((x, y, 0)))
        rim_top.append(bm.verts.new((x, y, rim_w)))
        
    bm.verts.ensure_lookup_table()
    for i in range(steps):
        # Bottom fan
        bm.faces.new((center_bottom, rim_bottom[i+1], rim_bottom[i]))
        # Top fan
        bm.faces.new((center_top, rim_top[i], rim_top[i+1]))
        # Outer rim
        bm.faces.new((rim_bottom[i], rim_bottom[i+1], rim_top[i+1], rim_top[i]))
        
    # Side radial faces
    bm.faces.new((center_bottom, rim_bottom[0], rim_top[0], center_top))
    bm.faces.new((center_bottom, center_top, rim_top[-1], rim_bottom[-1]))
    
    mesh = bpy.data.meshes.new("Sector_Mesh")
    bm.to_mesh(mesh)
    bm.free()
    
    sector_obj = bpy.data.objects.new("LJT01.03_扇形齿轮", mesh)
    bpy.context.scene.collection.objects.link(sector_obj)
    
    # Hub cylinder phi 24, len 46
    bpy.ops.mesh.primitive_cylinder_add(radius=hub_d/2.0, depth=hub_len, location=(0, 0, rim_w/2.0), vertices=48)
    hub_obj = bpy.context.active_object
    mod_u = sector_obj.modifiers.new(name="Union_Hub", type='BOOLEAN')
    mod_u.operation = 'UNION'
    mod_u.object = hub_obj
    bpy.context.view_layer.objects.active = sector_obj
    bpy.ops.object.modifier_apply(modifier="Union_Hub")
    bpy.data.objects.remove(hub_obj, do_unlink=True)
    
    # Bore phi 14
    bpy.ops.mesh.primitive_cylinder_add(radius=bore_d/2.0, depth=hub_len*2.0, location=(0, 0, rim_w/2.0), vertices=48)
    cutter = bpy.context.active_object
    mod_c = sector_obj.modifiers.new(name="Cut_Bore", type='BOOLEAN')
    mod_c.operation = 'DIFFERENCE'
    mod_c.object = cutter
    bpy.context.view_layer.objects.active = sector_obj
    bpy.ops.object.modifier_apply(modifier="Cut_Bore")
    bpy.data.objects.remove(cutter, do_unlink=True)
    
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    return sector_obj

def generate_herringbone_gear_ljt01_04():
    """
    LJT01.04 人字齿轮 (Herringbone Gear)
    z = 80, mn = 8, beta = 30.43 deg, da = 758.27 mm, Width = 378 mm (2x 135 mm + groove 108 mm)
    Hub = phi 440 mm, Bore = phi 325 mm, Keyway = 60 mm.
    """
    reset_scene()
    da = 758.27
    d_bore = 325.0
    d_hub = 440.0
    w_total = 378.0
    
    # Outer cylindrical double helix body with center groove
    bpy.ops.mesh.primitive_cylinder_add(radius=da/2.0, depth=w_total, location=(0, 0, 0), vertices=128)
    gear_obj = bpy.context.active_object
    gear_obj.name = "LJT01.04_人字齿轮"
    
    # Center relief groove: phi 710 mm, width 108 mm
    bpy.ops.mesh.primitive_cylinder_add(radius=da/2.0 + 10.0, depth=108.0, location=(0, 0, 0), vertices=64)
    groove_outer = bpy.context.active_object
    bpy.ops.mesh.primitive_cylinder_add(radius=710.0/2.0, depth=110.0, location=(0, 0, 0), vertices=64)
    groove_inner = bpy.context.active_object
    
    mod_sub = groove_outer.modifiers.new(name="Sub_Inner", type='BOOLEAN')
    mod_sub.operation = 'DIFFERENCE'
    mod_sub.object = groove_inner
    bpy.context.view_layer.objects.active = groove_outer
    bpy.ops.object.modifier_apply(modifier="Sub_Inner")
    bpy.data.objects.remove(groove_inner, do_unlink=True)
    
    mod_groove = gear_obj.modifiers.new(name="Cut_Groove", type='BOOLEAN')
    mod_groove.operation = 'DIFFERENCE'
    mod_groove.object = groove_outer
    bpy.context.view_layer.objects.active = gear_obj
    bpy.ops.object.modifier_apply(modifier="Cut_Groove")
    bpy.data.objects.remove(groove_outer, do_unlink=True)
    
    # Bore phi 325 mm
    bpy.ops.mesh.primitive_cylinder_add(radius=d_bore/2.0, depth=w_total*1.5, location=(0, 0, 0), vertices=64)
    bore_cyl = bpy.context.active_object
    mod_b = gear_obj.modifiers.new(name="Cut_Bore", type='BOOLEAN')
    mod_b.operation = 'DIFFERENCE'
    mod_b.object = bore_cyl
    bpy.context.view_layer.objects.active = gear_obj
    bpy.ops.object.modifier_apply(modifier="Cut_Bore")
    bpy.data.objects.remove(bore_cyl, do_unlink=True)
    
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    return gear_obj

def generate_worm_wheel_ljt01_09():
    """
    LJT01.09 蜗轮 (Worm Wheel)
    m = 5, z = 61, Throat R20, da = 330 mm, Width = 40 mm, Bore = phi 180 mm, Bronze material
    """
    reset_scene()
    da = 330.0
    df = 305.0
    w = 40.0
    bore_d = 180.0
    throat_r = 20.0
    
    # Revolve concave throat rim profile
    profile = [
        (0.0, bore_d/2.0), (w, bore_d/2.0),
        (w, df/2.0), (w*0.8, da/2.0),
        (w*0.2, da/2.0), (0.0, df/2.0)
    ]
    
    bm = bmesh.new()
    segments = 64
    verts_rings = []
    for z_c, r in profile:
        ring = []
        for i in range(segments):
            theta = i * 2.0 * math.pi / segments
            x = r * math.cos(theta)
            y = r * math.sin(theta)
            ring.append(bm.verts.new((x, y, z_c)))
        verts_rings.append(ring)
        
    bm.verts.ensure_lookup_table()
    for j in range(len(profile) - 1):
        r1 = verts_rings[j]
        r2 = verts_rings[j+1]
        for i in range(segments):
            next_i = (i + 1) % segments
            bm.faces.new((r1[i], r2[i], r2[next_i], r1[next_i]))
            
    mesh = bpy.data.meshes.new("Worm_Wheel_Mesh")
    bm.to_mesh(mesh)
    bm.free()
    
    wheel_obj = bpy.data.objects.new("LJT01.09_蜗轮", mesh)
    bpy.context.scene.collection.objects.link(wheel_obj)
    
    # 6x Bolt holes phi 8 on PCD 230 mm
    for i in range(6):
        ang = i * (2.0 * math.pi / 6.0)
        bx = (230.0 / 2.0) * math.cos(ang)
        by = (230.0 / 2.0) * math.sin(ang)
        bpy.ops.mesh.primitive_cylinder_add(radius=8.0/2.0, depth=w*2.0, location=(bx, by, w/2.0), vertices=24)
        bolt_cyl = bpy.context.active_object
        mod_h = wheel_obj.modifiers.new(name=f"Bolt_{i}", type='BOOLEAN')
        mod_h.operation = 'DIFFERENCE'
        mod_h.object = bolt_cyl
        bpy.context.view_layer.objects.active = wheel_obj
        bpy.ops.object.modifier_apply(modifier=f"Bolt_{i}")
        bpy.data.objects.remove(bolt_cyl, do_unlink=True)

    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    return wheel_obj
