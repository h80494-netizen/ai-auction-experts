with open('public/map.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'function fetchDistrictUnits' in line:
        print(f"=== Found fetchDistrictUnits at line {idx+1} ===")
        for i in range(idx, min(len(lines), idx + 100)):
            print(f'{i+1}: {lines[i].rstrip()}')
            if 'async function' in lines[i] and i > idx:
                break
