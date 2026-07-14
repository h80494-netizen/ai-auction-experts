with open('public/map.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if '#left-panel' in line or '#right-panel' in line:
        if i < 800: # Styles section is at the beginning
            print(f"Line {i+1}: {line.strip()}")
            for j in range(max(0, i-2), min(len(lines), i+8)):
                print(f"  {j+1}: {lines[j].rstrip()}")
            print("-" * 40)
