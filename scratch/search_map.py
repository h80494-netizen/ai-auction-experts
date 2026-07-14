with open('public/map.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

keywords = ['redevelopment_zones', 'zoning', 'planning_roads', 'district_units']
for i, line in enumerate(lines):
    for kw in keywords:
        if kw in line:
            print(f"{i+1} ({kw}): {line.strip()}")
