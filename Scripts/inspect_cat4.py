import json, sys

sys.stdout.reconfigure(encoding='utf-8')

with open("parts_manifest.json", "r", encoding="utf-8") as f:
    data = json.load(f)

cat4 = [p for p in data["parts"] if p["category_id"] == "04"]
completed = [p for p in cat4 if p["status"] == "COMPLETED"]
pending = [p for p in cat4 if p["status"] == "PENDING"]

print(f"Cat04 Total: {len(cat4)}, Completed: {len(completed)}, Pending: {len(pending)}")
print("\n--- COMPLETED ---")
for p in completed:
    print(f"  {p['code']} {p['name']}: {p['blend_path']}")

print("\n--- PENDING ---")
for p in pending:
    print(f"  {p['code']} {p['name']} (Sheet P{p['drawing_page']}, Iso P{p['isometric_page']})")
