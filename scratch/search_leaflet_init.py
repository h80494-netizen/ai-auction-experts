import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('public/map.html', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
for i, line in enumerate(lines):
    if "L.map" in line or "map = L." in line or "tileLayer" in line:
        print(f"   Line {i+1}: {line.strip()[:140]}")
