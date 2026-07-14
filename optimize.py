import re

with open('public/map.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove checked from dev4-type-check
content = re.sub(r'<input type="checkbox" class="dev4-type-check" value="(.*?)" checked>', r'<input type="checkbox" class="dev4-type-check" value="\1">', content)

# 2. Remove 25% padding in loadAuctions
old_pad = """                const padLat = latDiff * 0.25;
                const padLng = lngDiff * 0.25;"""
new_pad = """                const padLat = 0;
                const padLng = 0;"""
content = content.replace(old_pad, new_pad)

with open('public/map.html', 'w', encoding='utf-8') as f:
    f.write(content)

with open('backend/app.py', 'r', encoding='utf-8') as f:
    app_content = f.read()

# 3. Change LIMIT 1500 to LIMIT 500
app_content = app_content.replace('query += " LIMIT 1500"', 'query += " LIMIT 500"')

with open('backend/app.py', 'w', encoding='utf-8') as f:
    f.write(app_content)

print("Updates completed successfully.")
