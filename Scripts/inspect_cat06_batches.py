import json

manifest_path = r"C:\Users\20858\Desktop\机械练习\王静图集\Blender_零件三维图纸\parts_manifest.json"
with open(manifest_path, "r", encoding="utf-8") as f:
    manifest = json.load(f)

cat6_parts = [p for p in manifest["parts"] if p["category_id"] == "06"]

print("=== Category 06 Batch 1: Parts 01 to 15 ===")
for p in cat6_parts[:15]:
    print(f"{p['code']}_{p['name']}, Page {p['drawing_page']}")

print("\n=== Category 06 Batch 2: Parts 16 to 30 ===")
for p in cat6_parts[15:30]:
    print(f"{p['code']}_{p['name']}, Page {p['drawing_page']}")

print("\n=== Category 06 Batch 3: Parts 31 to 45 ===")
for p in cat6_parts[30:]:
    print(f"{p['code']}_{p['name']}, Page {p['drawing_page']}")
