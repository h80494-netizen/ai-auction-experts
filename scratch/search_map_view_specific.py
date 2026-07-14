for path in ['detail_result.html', 'public_detail.html', 'public/index.html', 'public/map.html']:
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        if '지도보기' in content:
            print(f"Found '지도보기' in {path}")
            # Let's print matching lines
            lines = content.split('\n')
            for idx, line in enumerate(lines):
                if '지도보기' in line:
                    print(f"  Line {idx+1}: {line.strip()[:120]}")
    except Exception as e:
        print(f"Error reading {path}: {e}")
