path = r"C:\Users\20858\Desktop\机械练习\王静图集\Blender_零件三维图纸\Scripts\generate_cat05_batch2.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("bcg.MAT_CAST_IRON", "'cast_iron'")
content = content.replace("bcg.MAT_STEEL_MACHINED", "'machined_steel'")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Replaced successfully!")
