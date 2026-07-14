import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('public/map.html', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
for i, line in enumerate(lines):
    if "crs" in line.lower() or "proj" in line.lower() or "5181" in line.lower():
        print(f"   Line {i+1}: {line.strip()[:140]}")
