with open('public/map.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'fetch(' in line or '/api/map/' in line:
        print(f"{i+1}: {line.strip()}")
