import os
from PIL import Image

iso_dir = r"C:\Users\20858\Desktop\机械练习\王静图集\Blender_零件三维图纸\Drawing_Sheets"
crop_dir = r"C:\Users\20858\Desktop\机械练习\王静图集\Blender_零件三维图纸\Drawing_Sheets\Reference_Crops"
os.makedirs(crop_dir, exist_ok=True)

# P242: LJT04.01 to LJT04.12 (3 rows x 4 cols)
p242 = Image.open(os.path.join(iso_dir, "Appendix_A_Isometric_P242.png"))
w, h = p242.size

parts_p242 = [
    ("LJT04.01", "平带轮"), ("LJT04.02", "V带轮"), ("LJT04.03", "塔轮"), ("LJT04.04", "手轮"),
    ("LJT04.05", "波纹手轮"), ("LJT04.06", "单排套筒链轮"), ("LJT04.07", "多排链轮"), ("LJT04.08", "盘形凸轮"),
    ("LJT04.09", "套筒凸轮"), ("LJT04.10", "平面沟槽凸轮"), ("LJT04.11", "端面凸轮"), ("LJT04.12", "圆柱沟槽凸轮")
]

cell_w = w / 4.0
cell_h = h / 3.0

for idx, (code, name) in enumerate(parts_p242):
    row = idx // 4
    col = idx % 4
    box = (int(col * cell_w), int(row * cell_h), int((col + 1) * cell_w), int((row + 1) * cell_h))
    crop = p242.crop(box)
    crop.save(os.path.join(crop_dir, f"{code}_{name}_iso.png"))

# P243: LJT04.13 to LJT04.24 (3 rows x 4 cols)
p243 = Image.open(os.path.join(iso_dir, "Appendix_A_Isometric_P243.png"))
parts_p243 = [
    ("LJT04.13", "摆线轮"), ("LJT04.14", "棘轮"), ("LJT04.15", "槽轮"), ("LJT04.16", "星轮"),
    ("LJT04.17", "法兰盘"), ("LJT04.18", "法兰盘"), ("LJT04.19", "法兰盘"), ("LJT04.20", "法兰盘"),
    ("LJT04.21", "拨盘"), ("LJT04.22", "调节盘"), ("LJT04.23", "调节盘"), ("LJT04.24", "读数盘")
]

for idx, (code, name) in enumerate(parts_p243):
    row = idx // 4
    col = idx % 4
    box = (int(col * cell_w), int(row * cell_h), int((col + 1) * cell_w), int((row + 1) * cell_h))
    crop = p243.crop(box)
    crop.save(os.path.join(crop_dir, f"{code}_{name}_iso.png"))

# P244: LJT04.25 to LJT04.36
p244 = Image.open(os.path.join(iso_dir, "Appendix_A_Isometric_P244.png"))
parts_p244 = [
    ("LJT04.25", "定位盘"), ("LJT04.26", "偏心盘"), ("LJT04.27", "连接盘"), ("LJT04.28", "花盘"),
    ("LJT04.29", "压盘"), ("LJT04.30", "半联轴器"), ("LJT04.31", "半离合器"), ("LJT04.32", "闷盖"),
    ("LJT04.33", "透盖"), ("LJT04.34", "填料压盖"), ("LJT04.35", "阀盖"), ("LJT04.36", "轴承盖")
]
for idx, (code, name) in enumerate(parts_p244):
    row = idx // 4
    col = idx % 4
    box = (int(col * cell_w), int(row * cell_h), int((col + 1) * cell_w), int((row + 1) * cell_h))
    crop = p244.crop(box)
    crop.save(os.path.join(crop_dir, f"{code}_{name}_iso.png"))

# P245: LJT04.37 to LJT04.44 (2 rows x 4 cols)
p245 = Image.open(os.path.join(iso_dir, "Appendix_A_Isometric_P245.png"))
cell_h245 = h / 2.0
parts_p245 = [
    ("LJT04.37", "端盖"), ("LJT04.38", "端盖"), ("LJT04.39", "端盖"), ("LJT04.40", "泵盖"),
    ("LJT04.41", "泵盖"), ("LJT04.42", "体盖"), ("LJT04.43", "箱盖"), ("LJT04.44", "左箱盖")
]
for idx, (code, name) in enumerate(parts_p245):
    row = idx // 4
    col = idx % 4
    box = (int(col * cell_w), int(row * cell_h245), int((col + 1) * cell_w), int((row + 1) * cell_h245))
    crop = p245.crop(box)
    crop.save(os.path.join(crop_dir, f"{code}_{name}_iso.png"))

# P246: LJT04.45 to LJT04.48 (top half, 1 row x 4 cols)
p246 = Image.open(os.path.join(iso_dir, "Appendix_A_Isometric_P246.png"))
parts_p246 = [
    ("LJT04.45", "阀盖"), ("LJT04.46", "泵盖"), ("LJT04.47", "前泵盖"), ("LJT04.48", "箱盖")
]
for idx, (code, name) in enumerate(parts_p246):
    box = (int(idx * cell_w), 0, int((idx + 1) * cell_w), int(cell_h245))
    crop = p246.crop(box)
    crop.save(os.path.join(crop_dir, f"{code}_{name}_iso.png"))

print("Cropped all 48 Category 04 isometric reference images successfully.")
