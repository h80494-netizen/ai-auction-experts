with open('public/map.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, l in enumerate(lines):
    if 'id="right-panel"' in l:
        for j in range(i, i+30):
            print(f'{j+1}: {lines[j].rstrip()}')
        break
