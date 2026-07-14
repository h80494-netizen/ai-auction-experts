import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('public/map.html', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
for i, line in enumerate(lines):
    if "const layers" in line or "var layers" in line or "layers =" in line:
        print(f"   Line {i+1}: {line.strip()[:140]}")
