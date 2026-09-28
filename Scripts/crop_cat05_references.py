import os
from PIL import Image

iso_dir = r"C:\Users\20858\Desktop\机械练习\王静图集\Blender_零件三维图纸\Drawing_Sheets"
crop_dir = r"C:\Users\20858\Desktop\机械练习\王静图集\Blender_零件三维图纸\Drawing_Sheets\Reference_Crops"
os.makedirs(crop_dir, exist_ok=True)

# P246: LJT05.01 to LJT05.04 (bottom row of 2-row page)
p246 = Image.open(os.path.join(iso_dir, "Appendix_A_Isometric_P246.png"))
w, h = p246.size
cell_w = w / 4.0
cell_h246 = h / 2.0

parts_p246 = [
    ("LJT05.01", "拨叉"), ("LJT05.02", "拨叉"), ("LJT05.03", "支架"), ("LJT05.04", "支架")
]
for idx, (code, name) in enumerate(parts_p246):
    box = (int(idx * cell_w), int(cell_h246), int((idx + 1) * cell_w), int(h))
    crop = p246.crop(box)
    crop.save(os.path.join(crop_dir, f"{code}_{name}_iso.png"))

# P247: LJT05.05 to LJT05.16 (3 rows x 4 cols)
p247 = Image.open(os.path.join(iso_dir, "Appendix_A_Isometric_P247.png"))
w, h = p247.size
cell_w = w / 4.0
cell_h = h / 3.0
parts_p247 = [
    ("LJT05.05", "杠杆"), ("LJT05.06", "曲柄"), ("LJT05.07", "连杆"), ("LJT05.08", "拨叉"),
    ("LJT05.09", "托架"), ("LJT05.10", "支架"), ("LJT05.11", "支架"), ("LJT05.12", "脚踏座"),
    ("LJT05.13", "支架"), ("LJT05.14", "支架"), ("LJT05.15", "支架"), ("LJT05.16", "托架")
]
for idx, (code, name) in enumerate(parts_p247):
    row = idx // 4
    col = idx % 4
    box = (int(col * cell_w), int(row * cell_h), int((col + 1) * cell_w), int((row + 1) * cell_h))
    crop = p247.crop(box)
    crop.save(os.path.join(crop_dir, f"{code}_{name}_iso.png"))

# P248: LJT05.17 to LJT05.24 (2 rows x 4 cols)
p248 = Image.open(os.path.join(iso_dir, "Appendix_A_Isometric_P248.png"))
w, h = p248.size
cell_w = w / 4.0
cell_h = h / 2.0
parts_p248 = [
    ("LJT05.17", "座架"), ("LJT05.18", "连杆"), ("LJT05.19", "踏架"), ("LJT05.20", "拨叉"),
    ("LJT05.21", "脚踏杆"), ("LJT05.22", "支架"), ("LJT05.23", "支架"), ("LJT05.24", "轴座")
]
for idx, (code, name) in enumerate(parts_p248):
    row = idx // 4
    col = idx % 4
    box = (int(col * cell_w), int(row * cell_h), int((col + 1) * cell_w), int((row + 1) * cell_h))
    crop = p248.crop(box)
    crop.save(os.path.join(crop_dir, f"{code}_{name}_iso.png"))

# P249: LJT05.25 to LJT05.36 (3 rows x 4 cols)
p249 = Image.open(os.path.join(iso_dir, "Appendix_A_Isometric_P249.png"))
w, h = p249.size
cell_w = w / 4.0
cell_h = h / 3.0
parts_p249 = [
    ("LJT05.25", "轴承架"), ("LJT05.26", "导向支架"), ("LJT05.27", "十字接头"), ("LJT05.28", "摇臂轴座"),
    ("LJT05.29", "主轴架"), ("LJT05.30", "吊架"), ("LJT05.31", "支座"), ("LJT05.32", "支座"),
    ("LJT05.33", "支架"), ("LJT05.34", "砂轮头架"), ("LJT05.35", "叉"), ("LJT05.36", "轴架")
]
for idx, (code, name) in enumerate(parts_p249):
    row = idx // 4
    col = idx % 4
    box = (int(col * cell_w), int(row * cell_h), int((col + 1) * cell_w), int((row + 1) * cell_h))
    crop = p249.crop(box)
    crop.save(os.path.join(crop_dir, f"{code}_{name}_iso.png"))

# P250: LJT05.37 to LJT05.46 (let's check rows: 10 parts -> 3 rows of 4 cols, last row has 2)
p250 = Image.open(os.path.join(iso_dir, "Appendix_A_Isometric_P250.png"))
w, h = p250.size
cell_w = w / 4.0
cell_h = h / 3.0
parts_p250 = [
    ("LJT05.37", "支座"), ("LJT05.38", "支座"), ("LJT05.39", "支架"), ("LJT05.40", "刹车支架"),
    ("LJT05.41", "拨叉"), ("LJT05.42", "拨叉"), ("LJT05.43", "支架"), ("LJT05.44", "连杆"),
    ("LJT05.45", "往复杠杆"), ("LJT05.46", "连杆")
]
for idx, (code, name) in enumerate(parts_p250):
    row = idx // 4
    col = idx % 4
    box = (int(col * cell_w), int(row * cell_h), int((col + 1) * cell_w), int((row + 1) * cell_h))
    crop = p250.crop(box)
    crop.save(os.path.join(crop_dir, f"{code}_{name}_iso.png"))

print("Cropped all 46 Category 05 isometric reference images successfully.")
