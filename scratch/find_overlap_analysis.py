with open('public/analysis.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    l_lower = line.lower()
    if 'overlap' in l_lower or '중첩' in l_lower or 'mode' in l_lower:
        print(f"{idx+1}: {line.strip()}")
