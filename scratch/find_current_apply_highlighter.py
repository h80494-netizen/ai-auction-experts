with open('public/map.html', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.splitlines()
start_idx = -1
for idx, line in enumerate(lines):
    if 'function applyHighlighter()' in line:
        start_idx = idx
        break

if start_idx != -1:
    with open('scratch/current_apply_highlighter.txt', 'w', encoding='utf-8') as out:
        for idx in range(start_idx - 5, start_idx + 120):
            if idx < len(lines):
                out.write(f"{idx+1}: {lines[idx]}\n")
