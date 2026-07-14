with open('public/map.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if any(k in line for k in ['분석', '보고서', 'analyze', 'Analyze']):
        print(f"{i+1}: {line.strip()[:120]}")
