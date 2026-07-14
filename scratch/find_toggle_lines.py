with open('public/map.html', 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f, 1):
        if 'toggle-dev2' in line or 'layers.dev2' in line:
            print(f"{idx}: {line.strip()}")
