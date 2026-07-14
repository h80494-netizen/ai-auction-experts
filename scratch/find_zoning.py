with open('public/map.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'zoning' in line or '용도지역' in line or '일반상업' in line:
        print(f"Line {i+1}: {line.strip()}")
