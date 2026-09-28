import json

manifest_path = r"C:\Users\20858\Desktop\机械练习\王静图集\Blender_零件三维图纸\parts_manifest.json"
with open(manifest_path, "r", encoding="utf-8") as f:
    manifest = json.load(f)

cat6_parts = [p for p in manifest["parts"] if p["category_id"] == "06"]

out_txt = r"C:\Users\20858\Desktop\机械练习\王静图集\Blender_零件三维图纸\Scripts\cat06_parts_list.txt"
with open(out_txt, "w", encoding="utf-8") as f:
    f.write("=== Category 06: 箱壳类零件 (45 parts) ===\n\n")
    for i, p in enumerate(cat6_parts, 1):
        f.write(f"{i:2d}. {p['code']}_{p['name']} (Drawing Sheet P{p['drawing_page']})\n")

print("Saved cat06 parts list.")
