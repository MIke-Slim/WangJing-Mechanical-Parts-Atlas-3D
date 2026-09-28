"""
Batch Converter: SolidWorks (.SLDPRT) -> Blender (.blend + PBR Materials + 3D Render)
Author: Antigravity Assistant
"""

import os
import sys
import io
import time
import json
import re
import win32com.client

# Set stdout encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sw_dir = r"C:\Users\20858\Desktop\机械练习\王静图集"
base_dir = os.path.join(sw_dir, "Blender_零件三维图纸")
staging_dir = os.path.join(base_dir, "staging_stl")
os.makedirs(staging_dir, exist_ok=True)

manifest_file = os.path.join(base_dir, "parts_manifest.json")
with open(manifest_file, "r", encoding="utf-8") as f:
    manifest = json.load(f)

parts_by_code = {p["code"]: p for p in manifest["parts"]}

# Find all valid completed SLDPRT files
all_files = [
    f for f in os.listdir(sw_dir)
    if f.lower().endswith((".sldprt", ".sldasm"))
    and not f.startswith("~$")
    and "undone" not in f.lower()
]

# Match files to manifest parts
tasks = []
for f in all_files:
    m = re.search(r'L[JT]{2}(\d{2})\.(\d{2})', f, re.IGNORECASE)
    if m:
        code = f"LJT{m.group(1)}.{m.group(2)}"
        if code in parts_by_code:
            part_info = parts_by_code[code]
            tasks.append({
                "filename": f,
                "filepath": os.path.join(sw_dir, f),
                "code": code,
                "name": part_info["name"],
                "folder": part_info["folder"],
                "category_id": part_info["category_id"]
            })

print(f"=== Found {len(tasks)} Completed CAD Parts to Convert ===")

# Step 1: Export all SLDPRT to STL using SolidWorks COM
print("\n--- Phase 1: SolidWorks Headless Export to STL ---")
swApp = win32com.client.Dispatch("SldWorks.Application")
swApp.Visible = False

exported_tasks = []
for idx, t in enumerate(tasks):
    clean_name = f"{t['code']}_{t['name']}"
    out_stl = os.path.join(staging_dir, f"{clean_name}.stl")
    
    # Check if already exported and recent
    if os.path.exists(out_stl) and os.path.getsize(out_stl) > 1000:
        print(f"[{idx+1}/{len(tasks)}] Already cached: {clean_name}")
        t["stl_path"] = out_stl
        exported_tasks.append(t)
        continue

    print(f"[{idx+1}/{len(tasks)}] Exporting {t['filename']} -> {clean_name}.stl")
    errors = win32com.client.VARIANT(win32com.client.pythoncom.VT_BYREF | win32com.client.pythoncom.VT_I4, 0)
    warnings = win32com.client.VARIANT(win32com.client.pythoncom.VT_BYREF | win32com.client.pythoncom.VT_I4, 0)
    
    doc_type = 2 if t["filename"].lower().endswith(".sldasm") else 1
    model = swApp.OpenDoc6(t["filepath"], doc_type, 1, "", errors, warnings)
    if model:
        res = model.SaveAs3(out_stl, 0, 1)
        if os.path.exists(out_stl) and os.path.getsize(out_stl) > 0:
            print(f"   [SUCCESS] Saved STL ({os.path.getsize(out_stl)/1024:.1f} KB)")
            t["stl_path"] = out_stl
            exported_tasks.append(t)
        else:
            print(f"   [FAILED] SaveAs returned {res}")
        time.sleep(0.3)
    else:
        print(f"   [FAILED] Could not open {t['filename']}")

try:
    swApp.ExitApp()
except:
    pass

print(f"\nPhase 1 Completed. Successfully exported {len(exported_tasks)} STLs.")

# Save exported tasks list for Blender runner
tasks_json = os.path.join(staging_dir, "exported_tasks.json")
with open(tasks_json, "w", encoding="utf-8") as f:
    json.dump(exported_tasks, f, ensure_ascii=False, indent=2)

print(f"Task definition saved to {tasks_json}.")
