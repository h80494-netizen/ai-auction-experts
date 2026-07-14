import re

with open('public/map.html', 'r', encoding='utf-8') as f:
    content = f.read()

toggles = re.findall(r'id=["\']toggle-[^"\']+["\']', content)
for t in set(toggles):
    print(t)
