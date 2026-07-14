import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('public/map.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Print lines 960 to 1010 (0-indexed: 959 to 1009)
for idx in range(959, min(1009, len(lines))):
    print(f"{idx+1}: {lines[idx].strip()}")
