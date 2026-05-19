import re

with open('public/map.html', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

fixed_content = re.sub(
    r'\}\)\.bindPopup\(`<b>[^`]*\)\.addTo\(layers\.dev2\);',
    r'}).bindPopup(`<b>지구단위계획구역</b><br>${item.name}`).addTo(layers.dev2);',
    content
)

with open('public/map.html', 'w', encoding='utf-8') as f:
    f.write(fixed_content)
print("Fixed dev2 bindPopup in map.html")
