import re

with open('public/map.html', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# Fix the broken string literal in line 1399
# Search for something like: }).bindPopup(`<b>?숈썝 ... 諛€吏?).addTo(layers.hagwon);
fixed_content = re.sub(
    r'\}\)\.bindPopup\(`<b>[^`\)]*\)\.addTo\(layers\.hagwon\);',
    r'}).bindPopup(`<b>학원 밀집가</b><br>반경 200m 내 ${poly.count}개 학원 밀집`).addTo(layers.hagwon);',
    content
)

with open('public/map.html', 'w', encoding='utf-8') as f:
    f.write(fixed_content)
print("Fixed backtick in map.html")
