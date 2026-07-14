import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('public/map.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Let's search for keywords like "상권", "인구", "heatmap", "road", "pop"
keywords = ["상권", "인구", "heatmap", "road", "pop", "gis"]
for kw in keywords:
    count = content.count(kw)
    print(f"Keyword '{kw}': {count} occurrences")

# Find lines containing "인구"
lines = content.split('\n')
for i, line in enumerate(lines):
    if "인구" in line or "pop" in line:
        print(f"   Line {i+1}: {line.strip()[:100]}")
