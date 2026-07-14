with open('public/map.html', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.splitlines()
with open('scratch/exact_check_point_lines.txt', 'w', encoding='utf-8') as out:
    for idx in range(1624, 1660):
        if idx < len(lines):
            out.write(f"{idx+1}: {lines[idx]}\n")
