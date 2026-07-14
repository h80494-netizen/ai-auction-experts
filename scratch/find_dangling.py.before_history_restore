with open('public/map.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'bindPopup' in line and '吏€援' in line:
        print(f"Dangling line at {idx+1}: {line}")
        # print surrounding lines
        for i in range(idx - 10, idx + 15):
            print(f'  {i+1}: {lines[i].rstrip()}')
