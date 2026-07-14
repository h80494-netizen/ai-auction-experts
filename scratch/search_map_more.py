with open('public/map.html', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")
for idx, line in enumerate(lines):
    if any(k in line for k in ['dev1', 'dev2', 'dev3', 'taekji', '재개발', '택지', '지구경계']):
        print(f"Line {idx+1}: {line.strip()[:140]}")
