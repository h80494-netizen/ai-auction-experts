with open('public/map.html', 'r', encoding='utf-8') as f:
    content = f.read()

terms = ['toggle-dev1', 'toggle-dev2', 'toggle-dev3', 'layers.dev2', 'district_units']
for t in terms:
    print(f"Term '{t}' count: {content.count(t)}")
