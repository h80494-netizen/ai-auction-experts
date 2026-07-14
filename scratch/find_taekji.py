with open('public/map.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'taekji' in line or 'dev1' in line:
        if 'get' in line or 'function' in line or 'update' in line or 'stage' in line:
            print(f"Line {i+1}: {line.strip()}")
            # Print next 10 lines
            for j in range(i+1, min(i+25, len(lines))):
                print(f"  {j+1}: {lines[j].strip()}")
            print("-" * 40)
