with open('public/map.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'layers = ' in line or 'layers ={' in line or 'const layers' in line or 'var layers' in line or 'let layers' in line:
        print(f"{idx+1}: {line.strip()}")
        # print next 25 lines
        for j in range(idx, min(len(lines), idx+35)):
            print(f"  {j+1}: {lines[j]}", end='')
