with open('public/map.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'toggle-planning-road-buffer' in line:
        print(f"{idx+1}: {line.strip()}")
        # print surrounding 5 lines
        for j in range(max(0, idx-5), min(len(lines), idx+10)):
            print(f"  {j+1}: {lines[j]}", end='')
