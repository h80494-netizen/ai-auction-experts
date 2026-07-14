import os

map_path = r'public\map.html'
with open(map_path, 'r', encoding='utf-8') as f:
    content = f.read()

with open(r'scratch\add_naver_js.py', 'r', encoding='utf-8') as f:
    script_content = f.read()

js_code = script_content.split('js_code = """')[1].split('"""')[0].strip()

if 'async function openNaverPriceModal' not in content:
    content = content.replace('</body>', js_code + '\n</body>')
    with open(map_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Injected JS successfully")
else:
    print("JS already exists")
