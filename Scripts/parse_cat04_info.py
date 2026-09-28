import pymupdf as fitz
import sys

sys.stdout.reconfigure(encoding='utf-8')
doc = fitz.open(r"C:\Users\20858\Desktop\机械练习\王静图集\新标准机械图图集.pdf")

for pno in range(61, 109):
    txt = doc[pno-1].get_text()
    lines = [line.strip() for line in txt.split('\n') if line.strip()]
    print(f"=== Page {pno} (Total lines: {len(lines)}) ===")
    for l in lines[:10]:
        print("  ", repr(l))
