with open('public/map.html', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'toggleAllCheckboxes' in line or 'function' in line and any(k in line for k in ['Checkbox', 'checkbox']):
        print(f"Line {idx+1}: {line.strip()[:140]}")
