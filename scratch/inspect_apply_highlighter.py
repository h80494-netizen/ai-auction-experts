with open('public/map.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'function applyHighlighter' in line:
        print(f"Found applyHighlighter at line {idx+1}")
        with open('scratch/apply_highlighter.txt', 'w', encoding='utf-8') as out:
            for i in range(idx, min(len(lines), idx + 120)):
                out.write(f'{i+1}: {lines[i]}')
        break
