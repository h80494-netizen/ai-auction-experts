with open('public/map.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

with open('scratch/css_snippet.css', 'w', encoding='utf-8') as out:
    for idx in range(69, min(200, len(lines))):
        out.write(f"{idx+1}: {lines[idx]}")

print("Written to scratch/css_snippet.css")
