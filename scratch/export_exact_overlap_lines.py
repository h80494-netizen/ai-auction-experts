with open('public/map.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Let's write the exact lines of openOverlapAnalysis from map.html to a file in scratch directory so we can read it cleanly.
lines = content.splitlines()
with open('scratch/exact_overlap_lines.txt', 'w', encoding='utf-8') as out:
    for idx in range(1760, 1850):
        if idx < len(lines):
            out.write(f"{idx+1}: {lines[idx]}\n")
