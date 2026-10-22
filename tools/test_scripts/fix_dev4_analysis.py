import re

with open('public/map.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add dev4 to openOverlapAnalysis
old_str = """                { id: 'toggle-dev3', layer: layers.dev3, name: '재개발/재건축', isLine: false },
                { id: 'toggle-zoning', layer: layers.zoning, name: '용도지역', isLine: false }"""
new_str = """                { id: 'toggle-dev3', layer: layers.dev3, name: '재개발/재건축', isLine: false },
                { id: 'toggle-dev4', layer: layers.dev4, name: '규제완화지구', isLine: false },
                { id: 'toggle-zoning', layer: layers.zoning, name: '용도지역', isLine: false }"""

if old_str in content:
    content = content.replace(old_str, new_str)
    with open('public/map.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fixed missing dev4 in openOverlapAnalysis")
else:
    print("Could not find old_str")
