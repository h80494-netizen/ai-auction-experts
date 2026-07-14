import re

with open('public/map.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Let's find some ids and search terms
queries = ['road-flow', 'legend', 'draggable', 'resizable', '범례', '경공매', '대시보드']
for q in queries:
    matches = [m.start() for m in re.finditer(q, content, re.IGNORECASE)]
    print(f"Term '{q}': found {len(matches)} times")
    for idx in matches[:5]:
        start = max(0, idx - 40)
        end = min(len(content), idx + 60)
        snippet = content[start:end].replace('\n', ' ')
        print(f"  Snippet: ... {snippet} ...")
