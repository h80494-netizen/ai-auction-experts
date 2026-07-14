with open('public/map.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if '/api/map/road_flows' in line:
        print(f"{idx+1}: {line.strip()}")
        # print next 30 lines
        for j in range(idx, min(len(lines), idx+35)):
            print(f"  {j+1}: {lines[j]}", end='')
