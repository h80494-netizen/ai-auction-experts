import re

file_path = r"c:\Users\llll\Documents\두인경매\바이브코딩\public\map.html"
output_path = r"c:\Users\llll\Documents\두인경매\바이브코딩\scratch\search_map_html_funcs.txt"

with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

out_lines = []
out_lines.append(f"Total lines: {len(lines)}\n")

for i, line in enumerate(lines):
    if "function " in line:
        out_lines.append(f"Line {i+1}: {line.strip()}\n")

with open(output_path, "w", encoding="utf-8") as f:
    f.writelines(out_lines)

print("Done writing function search!")
