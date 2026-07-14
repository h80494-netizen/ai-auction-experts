with open('public/map.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

with open('scratch/topbar_snippet.html', 'w', encoding='utf-8') as out:
    for idx in range(894, min(970, len(lines))):
        out.write(f"{idx+1}: {lines[idx]}")

print("Written to scratch/topbar_snippet.html")
