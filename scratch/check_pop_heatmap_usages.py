with open('public/map.html', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
for i, line in enumerate(lines):
    if 'popHeatmap' in line:
        print(f"Line {i+1}: {line.strip()}")
