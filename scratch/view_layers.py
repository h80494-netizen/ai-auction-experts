import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('public/map.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Print lines 1110 to 1170 (0-indexed: 1109 to 1169)
for idx in range(1109, min(1169, len(lines))):
    print(f"{idx+1}: {lines[idx].strip()}")
