with open('public/map.html', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'zoning-sub-container' in line:
        print(f"Line {idx+1}: {line.strip()[:140]}")
