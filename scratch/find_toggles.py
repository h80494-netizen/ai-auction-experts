with open('public/map.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if '<input type="checkbox"' in line or 'toggle-' in line:
        print(f"{i+1}: {line.strip()}")
