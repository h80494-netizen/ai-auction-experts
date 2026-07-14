with open('public/map.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx in range(2238, min(2252, len(lines))):
    print(f"{idx+1}: {repr(lines[idx])}")
