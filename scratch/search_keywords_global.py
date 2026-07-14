import os

keywords = ['redevelopment_zones', 'zoning', 'planning_roads', 'district_units']
for root, dirs, files in os.walk('.'):
    if '.git' in root:
        continue
    for f in files:
        if f.endswith('.py') or f.endswith('.js') or f.endswith('.html') or f.endswith('.css'):
            path = os.path.join(root, f)
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    found = [kw for kw in keywords if kw in content]
                    if found:
                        print(f"{path}: {found}")
            except Exception:
                pass
