with open('public/map.html', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f, 1):
        if '반경' in line or '배후인구' in line or '주거배후' in line:
            print(f"Line {i}: {line.strip()}")
