import os, json
import fitz # PyMuPDF

pdf_path = r"C:\Users\20858\Desktop\机械练习\王静图集\新标准机械图图集.pdf"
out_dir = r"C:\Users\20858\Desktop\机械练习\王静图集\Blender_零件三维图纸\Drawing_Sheets"
os.makedirs(out_dir, exist_ok=True)

with open("parts_manifest.json", "r", encoding="utf-8") as f:
    manifest = json.load(f)

cat4_parts = [p for p in manifest["parts"] if p["category_id"] == "04"]

doc = fitz.open(pdf_path)
print(f"Opened PDF with {len(doc)} pages.")

# Extract drawing sheets for cat 04
for p in cat4_parts:
    page_idx = p["drawing_page"] - 1 # 0-indexed
    code = p["code"]
    name = p["name"]
    target_img = os.path.join(out_dir, f"{code}_{name}_P{p['drawing_page']}.png")
    if not os.path.exists(target_img):
        page = doc[page_idx]
        pix = page.get_pixmap(dpi=150)
        pix.save(target_img)

# Extract isometric reference pages (242 to 246)
for pno in range(242, 247):
    iso_target = os.path.join(out_dir, f"Appendix_A_Isometric_P{pno}.png")
    if not os.path.exists(iso_target):
        page = doc[pno - 1]
        pix = page.get_pixmap(dpi=150)
        pix.save(iso_target)

doc.close()
print("Extracted Category 04 drawing sheets and isometric reference pages successfully.")
