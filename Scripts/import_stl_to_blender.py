"""
Phase 2: Blender STL Importer and Studio Staging
Executes inside Blender headless environment.
Author: Antigravity Assistant
"""

import os
import sys
import json
import math
import bpy
from mathutils import Vector

# Import helper functions from blender_cad_generator
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

import blender_cad_generator as bcg

base_dir = os.path.dirname(script_dir)
staging_dir = os.path.join(base_dir, "staging_stl")
renders_dir = os.path.join(base_dir, "Renders")
os.makedirs(renders_dir, exist_ok=True)

tasks_json = os.path.join(staging_dir, "exported_tasks.json")
if not os.path.exists(tasks_json):
    print(f"Error: {tasks_json} does not exist.")
    sys.exit(1)

with open(tasks_json, "r", encoding="utf-8") as f:
    tasks = json.load(f)

print(f"=== Blender Phase 2: Processing {len(tasks)} Models ===")

for idx, t in enumerate(tasks):
    code = t["code"]
    name = t["name"]
    folder = t["folder"]
    stl_path = t["stl_path"]
    
    clean_title = f"{code}_{name}"
    blend_file = os.path.join(base_dir, folder, f"{clean_title}.blend")
    render_file = os.path.join(renders_dir, f"{clean_title}.png")
    
    print(f"\n[{idx+1}/{len(tasks)}] Building Blender Scene for: {clean_title}")
    
    if not os.path.exists(stl_path):
        print(f"   [SKIP] STL not found: {stl_path}")
        continue

    # Reset Blender scene
    bcg.reset_scene()
    
    # Import STL
    bpy.ops.wm.stl_import(filepath=stl_path)
    mesh_objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    
    if not mesh_objs:
        print(f"   [ERROR] No mesh imported from {stl_path}")
        continue
        
    main_obj = mesh_objs[0]
    main_obj.name = clean_title
    
    # Recenter origin to bounding box center
    bpy.context.view_layer.objects.active = main_obj
    main_obj.select_set(True)
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    
    # Determine material based on category
    cat_id = t["category_id"]
    if cat_id in ["01"]:
        mat_type = "machined_steel"
    elif cat_id in ["02"]:
        mat_type = "spring_steel"
    elif cat_id in ["05", "06"]:
        mat_type = "cast_iron"
    else:
        mat_type = "machined_steel"
        
    # Render and save
    try:
        bcg.render_and_save(main_obj, blend_file, render_file, mat_type=mat_type)
        print(f"   [DONE] Saved {clean_title}.blend and rendered preview.")
    except Exception as e:
        print(f"   [ERROR] Failed to render {clean_title}: {e}")
        import traceback
        traceback.print_exc()

print("\n=== Phase 2 Processing Complete ===")
