with open('public/map.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

with open('scratch/original_dev1_snippet.js', 'w', encoding='utf-8') as out:
    for idx in range(2379, min(2470, len(lines))):
        out.write(f"{idx+1}: {lines[idx]}")

print("Written to scratch/original_dev1_snippet.js")
