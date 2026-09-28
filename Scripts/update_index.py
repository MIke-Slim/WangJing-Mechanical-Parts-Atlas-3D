"""
Update Manifest and Generate PARTS_INDEX.md
"""

import os
import sys
import io
import json

base_dir = r"C:\Users\20858\Desktop\机械练习\王静图集\Blender_零件三维图纸"
manifest_file = os.path.join(base_dir, "parts_manifest.json")

with open(manifest_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# Scan for existing .blend files
blend_files = {}
for root, dirs, files in os.walk(base_dir):
    for f in files:
        if f.endswith(".blend"):
            code = f.split("_")[0]
            blend_files[code] = os.path.relpath(os.path.join(root, f), base_dir)

# Scan for render previews
render_files = {}
renders_dir = os.path.join(base_dir, "Renders")
if os.path.exists(renders_dir):
    for f in os.listdir(renders_dir):
        if f.endswith(".png"):
            code = f.split("_")[0]
            render_files[code] = os.path.join("Renders", f)

completed_count = 0
for p in data["parts"]:
    code = p["code"]
    if code in blend_files:
        p["status"] = "COMPLETED"
        p["blend_path"] = blend_files[code]
        p["render_path"] = render_files.get(code, None)
        completed_count += 1
    else:
        p["status"] = "PENDING"
        p["blend_path"] = None
        p["render_path"] = None

total_num = len(data["parts"])
data["stats"] = {
    "total_parts": total_num,
    "completed": completed_count,
    "pending": total_num - completed_count
}

with open(manifest_file, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Manifest updated: {completed_count} / {total_num} parts completed.")

# Generate PARTS_INDEX.md
md_lines = []
md_lines.append("# 《新标准机械图图集》三维零件模型总览 / Mechanical Parts Atlas 3D Index\n")
md_lines.append(f"> **图集统计 / Atlas Statistics**: 共收录机械零件 **{total_num}** 种，涵盖6大类别及附录三维立体图。")
md_lines.append(f"> **当前已完成三维建模 / Completed Models**: **{completed_count}** 件（包含完整材质、灯光、机位及渲染预览）\n")

md_lines.append("## 目录与分类进度 / Categories & Progress\n")
md_lines.append("| 分类编号 / Category | 类别名称 / Name | 总零件数 / Total | 已建模型 / Done | 状态 / Status |")
md_lines.append("| :--- | :--- | :---: | :---: | :---: |")

cat_groups = {}
for p in data["parts"]:
    cid = p["category_id"]
    cat_groups.setdefault(cid, []).append(p)

for cid, parts in sorted(cat_groups.items()):
    cname = data["categories"][cid][1]
    done = sum(1 for p in parts if p["status"] == "COMPLETED")
    stat_badge = "100% 全部完成 / Complete" if done == len(parts) else f"{done}/{len(parts)} 完成 / In Progress"
    md_lines.append(f"| {cid} | {cname} | {len(parts)} | {done} | {stat_badge} |")

md_lines.append("\n---\n")

for cid, parts in sorted(cat_groups.items()):
    cname = data["categories"][cid][1]
    folder = data["categories"][cid][0]
    md_lines.append(f"### 第 1.{int(cid)} 节 {cname} (目录: `{folder}`)\n")
    md_lines.append("| 序号 | 零件图号 / Code | 零件名称 / Part Name | 图纸页码 | 立体图页码 | 建模状态 | 对应文件 / Blend File |")
    md_lines.append("| :---: | :--- | :--- | :---: | :---: | :---: | :--- |")
    for p in parts:
        status_str = "✅ **已完成 / Done**" if p["status"] == "COMPLETED" else "⏳ 待绘制 / Pending"
        bp = p["blend_path"]
        blend_link = f"`{bp}`" if bp else "-"
        md_lines.append(f"| {p['number']} | **{p['code']}** | {p['name']} | P{p['drawing_page']} | P{p['isometric_page']} | {status_str} | {blend_link} |")
    md_lines.append("")

index_path = os.path.join(base_dir, "PARTS_INDEX.md")
with open(index_path, "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines))

print(f"Generated PARTS_INDEX.md at: {index_path}")
