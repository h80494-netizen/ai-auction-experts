import re

with open('public/map.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

patterns = [r'toggle-dev', r'updateTaekjiLayer', r'fetchZoning', r'fetchPlanningRoads', r'fetchRedevelopment', r'layers\.dev', r'layers\.zoning', r'layers\.road']
for pat in patterns:
    print(f"--- Pattern: {pat} ---")
    rx = re.compile(pat)
    count = 0
    for idx, line in enumerate(lines):
        if rx.search(line):
            print(f"  {idx+1}: {line.strip()}")
            count += 1
            if count >= 15:
                print("  ... (truncated)")
                break
