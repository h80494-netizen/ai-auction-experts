import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('public/map.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Let's search for how "toggle-road-flows" is wired in JavaScript
lines = content.split('\n')
for i, line in enumerate(lines):
    if "toggle-road-flows" in line or "road-flows" in line:
        print(f"   Line {i+1}: {line.strip()[:140]}")
