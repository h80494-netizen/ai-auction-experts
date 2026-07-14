import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('public/map.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx in range(2340, min(2385, len(lines))):
    print(f"{idx+1}: {lines[idx].strip()}")
