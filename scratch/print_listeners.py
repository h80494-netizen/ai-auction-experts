with open('public/map.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(2749, min(len(lines), 2820)):
    print(f'{i+1}: {lines[i].rstrip()}')
