import re

js = open('public/script.js', encoding='utf-8').read()
html = open('public/index.html', encoding='utf-8').read()

ids = set(re.findall(r"getElementById\('([^']+)'\)", js) + re.findall(r'getElementById\("([^"]+)"\)', js))
missing = [i for i in ids if f'id="{i}"' not in html and f"id='{i}'" not in html]

print("MISSING IDs:", missing)
