import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('public/map.html', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
for i, line in enumerate(lines):
    if "region-checkbox" in line or "loadAuctions" in line:
        if i < 2000: # only print start references
            print(f"   Line {i+1}: {line.strip()[:140]}")
