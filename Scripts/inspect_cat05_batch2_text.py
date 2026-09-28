import fitz

doc = fitz.open(r"C:\Users\20858\Desktop\机械练习\王静图集\新标准机械图图集.pdf")
out_path = r"C:\Users\20858\Desktop\机械练习\王静图集\Blender_零件三维图纸\Scripts\cat05_batch2_text.txt"

with open(out_path, "w", encoding="utf-8") as f:
    for pno in range(133, 155):
        page = doc[pno-1]
        text = page.get_text()
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        f.write(f"=== Page {pno} (LJT05.{pno-108:02d}) ===\n")
        for line in lines:
            f.write(f"  {line}\n")
        f.write("\n")

print("Dumped text successfully.")
