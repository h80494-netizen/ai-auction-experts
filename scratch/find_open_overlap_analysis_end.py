with open('public/map.html', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.splitlines()
start_idx = -1
for idx, line in enumerate(lines):
    if 'window.openOverlapAnalysis = function()' in line:
        start_idx = idx
        break

if start_idx != -1:
    # Let's print out lines from start_idx to start_idx + 60
    for j in range(start_idx, min(len(lines), start_idx + 60)):
        print(f"{j+1}: {lines[j]}")
