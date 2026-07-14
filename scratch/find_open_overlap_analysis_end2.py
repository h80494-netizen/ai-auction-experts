with open('public/map.html', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.splitlines()
for j in range(1850, min(len(lines), 1910)):
    print(f"{j+1}: {lines[j]}")
