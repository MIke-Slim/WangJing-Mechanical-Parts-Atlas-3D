import json

manifest_path = r"C:\Users\20858\Desktop\机械练习\王静图集\Blender_零件三维图纸\parts_manifest.json"
with open(manifest_path, "r", encoding="utf-8") as f:
    manifest = json.load(f)

cat6_parts = [p for p in manifest["parts"] if p["category_id"] == "06"]
print(f"Total parts in Category 06: {len(cat6_parts)}")
min_page = min(p["drawing_page"] for p in cat6_parts)
max_page = max(p["drawing_page"] for p in cat6_parts)
print(f"Drawing page range: {min_page} to {max_page}")

for p in cat6_parts:
    print(f"  {p['code']}: {p['name']}, Page {p['drawing_page']}, Status: {p['status']}")
