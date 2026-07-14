with open('public/map.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'highlighter' in line.lower() or '입지분석기' in line:
        print(f"Match at line {idx+1}: {line.strip()}")
