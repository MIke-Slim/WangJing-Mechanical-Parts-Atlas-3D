import os, json
from PIL import Image

iso_dir = r"C:\Users\20858\Desktop\机械练习\王静图集\Blender_零件三维图纸\Drawing_Sheets"
crop_dir = r"C:\Users\20858\Desktop\机械练习\王静图集\Blender_零件三维图纸\Drawing_Sheets\Reference_Crops"
os.makedirs(crop_dir, exist_ok=True)

manifest_path = r"C:\Users\20858\Desktop\机械练习\王静图集\Blender_零件三维图纸\parts_manifest.json"
with open(manifest_path, "r", encoding="utf-8") as f:
    manifest = json.load(f)

name_map = {p["code"]: p["name"] for p in manifest["parts"] if p["category_id"] == "06"}

# P251: 8 parts (2 rows x 4 cols)
p251 = Image.open(os.path.join(iso_dir, "Appendix_A_Isometric_P251.png"))
w, h = p251.size
w4 = w / 4.0
h2 = h / 2.0
parts_p251 = [
    ["LJT06.01", "LJT06.02", "LJT06.03", "LJT06.04"],
    ["LJT06.05", "LJT06.06", "LJT06.07", "LJT06.08"]
]
for r in range(2):
    for c in range(4):
        code = parts_p251[r][c]
        name = name_map[code]
        box = (int(c * w4), int(r * h2), int((c + 1) * w4), int((r + 1) * h2))
        p251.crop(box).save(os.path.join(crop_dir, f"{code}_{name}_iso.png"))

# P252: 12 parts (3 rows x 4 cols)
p252 = Image.open(os.path.join(iso_dir, "Appendix_A_Isometric_P252.png"))
w, h = p252.size
w4 = w / 4.0
h3 = h / 3.0
parts_p252 = [
    ["LJT06.09", "LJT06.10", "LJT06.11", "LJT06.12"],
    ["LJT06.13", "LJT06.14", "LJT06.15", "LJT06.16"],
    ["LJT06.17", "LJT06.18", "LJT06.19", "LJT06.20"]
]
for r in range(3):
    for c in range(4):
        code = parts_p252[r][c]
        name = name_map[code]
        box = (int(c * w4), int(r * h3), int((c + 1) * w4), int((r + 1) * h3))
        p252.crop(box).save(os.path.join(crop_dir, f"{code}_{name}_iso.png"))

# P253: 12 parts (3 rows x 4 cols)
p253 = Image.open(os.path.join(iso_dir, "Appendix_A_Isometric_P253.png"))
w, h = p253.size
w4 = w / 4.0
h3 = h / 3.0
parts_p253 = [
    ["LJT06.21", "LJT06.22", "LJT06.23", "LJT06.24"],
    ["LJT06.25", "LJT06.26", "LJT06.27", "LJT06.28"],
    ["LJT06.29", "LJT06.30", "LJT06.31", "LJT06.32"]
]
for r in range(3):
    for c in range(4):
        code = parts_p253[r][c]
        name = name_map[code]
        box = (int(c * w4), int(r * h3), int((c + 1) * w4), int((r + 1) * h3))
        p253.crop(box).save(os.path.join(crop_dir, f"{code}_{name}_iso.png"))

# P254: 9 parts (3 rows x 3 cols)
p254 = Image.open(os.path.join(iso_dir, "Appendix_A_Isometric_P254.png"))
w, h = p254.size
w3 = w / 3.0
h3 = h / 3.0
parts_p254 = [
    ["LJT06.33", "LJT06.34", "LJT06.35"],
    ["LJT06.36", "LJT06.37", "LJT06.38"],
    ["LJT06.39", "LJT06.40", "LJT06.41"]
]
for r in range(3):
    for c in range(3):
        code = parts_p254[r][c]
        name = name_map[code]
        box = (int(c * w3), int(r * h3), int((c + 1) * w3), int((r + 1) * h3))
        p254.crop(box).save(os.path.join(crop_dir, f"{code}_{name}_iso.png"))

# P255: 4 parts (2 rows x 2 cols)
p255 = Image.open(os.path.join(iso_dir, "Appendix_A_Isometric_P255.png"))
w, h = p255.size
w2 = w / 2.0
h2 = h / 2.0
parts_p255 = [
    ["LJT06.42", "LJT06.43"],
    ["LJT06.44", "LJT06.45"]
]
for r in range(2):
    for c in range(2):
        code = parts_p255[r][c]
        name = name_map[code]
        box = (int(c * w2), int(r * h2), int((c + 1) * w2), int((r + 1) * h2))
        p255.crop(box).save(os.path.join(crop_dir, f"{code}_{name}_iso.png"))

print("Cropped all 45 Category 06 isometric reference drawings successfully!")
