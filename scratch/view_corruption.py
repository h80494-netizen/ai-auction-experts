# Read public/map.html around the corruption site
with open('public/map.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start = 3680
end = 3740
with open('scratch/corruption_view.html', 'w', encoding='utf-8') as out:
    for idx in range(start, min(end, len(lines))):
        out.write(f"{idx+1}: {lines[idx]}")

print("Written to scratch/corruption_view.html")
