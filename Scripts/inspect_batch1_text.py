import pymupdf as fitz
import sys

sys.stdout.reconfigure(encoding='utf-8')
doc = fitz.open(r"C:\Users\20858\Desktop\机械练习\王静图集\新标准机械图图集.pdf")

pages = [61, 62, 63, 65, 66, 67, 68, 70, 71, 72, 73, 74, 75, 76]

for pno in pages:
    page = doc[pno-1]
    text = page.get_text()
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    print(f"=== Sheet P{pno} ===")
    for l in lines:
        # print lines that might contain numbers, dimensions, or technical requirements
        if any(c.isdigit() for c in l) or any(k in l for k in ['轮', '凸轮', '孔', '槽', 'Ra', '技术要求']):
            print("  ", l)
