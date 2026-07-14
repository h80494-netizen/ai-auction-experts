with open('public/map.html', 'r', encoding='utf-8') as f:
    in_func = False
    func_lines = []
    for i, line in enumerate(f, 1):
        if 'function applyHighlighter' in line:
            in_func = True
        if in_func:
            func_lines.append(f"{i}: {line.rstrip()}")
            if line.strip() == '}':
                # Wait, could be multiple closing braces, let's keep going until we get a good block
                if len(func_lines) > 80:
                    break
    
    print("\n".join(func_lines[:120]))
