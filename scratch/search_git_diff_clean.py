import re

diff_file = r"c:\Users\llll\Documents\두인경매\바이브코딩\scratch\git_diff_all.txt"

with open(diff_file, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

print(f"Total diff lines: {len(lines)}")

keyword = "fetchPlanningRoads"
found = []
for idx, line in enumerate(lines):
    if keyword in line:
        found.append(idx)

for idx in found:
    print(f"Match at line {idx+1}: {lines[idx].strip()}")
    # print context
    start = max(0, idx - 10)
    end = min(len(lines), idx + 50)
    print("--- CONTEXT ---")
    for j in range(start, end):
        print(f"  {lines[j].strip()}")
    print("=" * 60)
