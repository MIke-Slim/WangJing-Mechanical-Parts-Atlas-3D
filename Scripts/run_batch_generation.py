"""
Batch Generation Runner for Blender CAD Models
Executes within Blender headless environment.
"""

import os
import sys

# Add script directory to sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

import blender_cad_generator as bcg

base_dir = os.path.dirname(script_dir)
renders_dir = os.path.join(base_dir, "Renders")
os.makedirs(renders_dir, exist_ok=True)

tasks = [
    # 02 Springs
    (
        "LJT02.01",
        "02_弹簧类_Springs",
        "LJT02.01_圆柱螺旋压缩弹簧",
        bcg.generate_compression_spring_ljt02_01,
        "spring_steel"
    ),
    (
        "LJT02.02",
        "02_弹簧类_Springs",
        "LJT02.02_圆柱螺旋拉伸弹簧",
        bcg.generate_extension_spring_ljt02_02,
        "spring_steel"
    ),
    (
        "LJT02.03",
        "02_弹簧类_Springs",
        "LJT02.03_螺旋扭转弹簧",
        bcg.generate_torsion_spring_ljt02_03,
        "spring_steel"
    ),
    (
        "LJT02.04",
        "02_弹簧类_Springs",
        "LJT02.04_碟形弹簧",
        bcg.generate_disc_spring_ljt02_04,
        "spring_steel"
    ),
    (
        "LJT02.05",
        "02_弹簧类_Springs",
        "LJT02.05_截锥螺旋压缩弹簧",
        bcg.generate_conical_spring_ljt02_05,
        "spring_steel"
    ),
    # 01 Gears
    (
        "LJT01.01",
        "01_齿轮类_Gears",
        "LJT01.01_圆柱直齿轮",
        bcg.generate_spur_gear_ljt01_01,
        "machined_steel"
    ),
    (
        "LJT01.03",
        "01_齿轮类_Gears",
        "LJT01.03_扇形齿轮",
        bcg.generate_sector_gear_ljt01_03,
        "cast_iron"
    ),
    (
        "LJT01.04",
        "01_齿轮类_Gears",
        "LJT01.04_人字齿轮",
        bcg.generate_herringbone_gear_ljt01_04,
        "cast_iron"
    ),
    (
        "LJT01.07",
        "01_齿轮类_Gears",
        "LJT01.07_锥齿轮",
        bcg.generate_bevel_gear_ljt01_07,
        "machined_steel"
    ),
    (
        "LJT01.08",
        "01_齿轮类_Gears",
        "LJT01.08_直齿齿条",
        bcg.generate_gear_rack_ljt01_08,
        "machined_steel"
    ),
    (
        "LJT01.09",
        "01_齿轮类_Gears",
        "LJT01.09_蜗轮",
        bcg.generate_worm_wheel_ljt01_09,
        "bronze"
    ),
    (
        "LJT01.10",
        "01_齿轮类_Gears",
        "LJT01.10_蜗杆",
        bcg.generate_worm_shaft_ljt01_10,
        "machined_steel"
    ),
]

print(f"=== Starting Batch Generation of {len(tasks)} Mechanical Parts ===")
for code, folder, name, func, mat in tasks:
    print(f"\n--- Generating {code}: {name} ---")
    try:
        obj = func()
        blend_file = os.path.join(base_dir, folder, f"{name}.blend")
        render_file = os.path.join(renders_dir, f"{name}.png")
        bcg.render_and_save(obj, blend_file, render_file, mat_type=mat)
        print(f"[COMPLETED] {code}: {name}")
    except Exception as e:
        print(f"[ERROR] Failed to generate {code}: {e}")
        import traceback
        traceback.print_exc()

print("\n=== Batch Generation Finished ===")
