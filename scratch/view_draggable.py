# Read public/map.html and find where makeDraggableAndResizable is defined, then write it to a temp file
with open('public/map.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'makeDraggableAndResizable' in line:
        start_line = max(0, i - 10)
        end_line = min(len(lines), i + 120)
        print(f"makeDraggableAndResizable found at line {i+1}. Printing lines {start_line+1} to {end_line+1}...")
        with open('scratch/draggable_snippet.js', 'w', encoding='utf-8') as out:
            for l_idx in range(start_line, end_line):
                out.write(f"{l_idx+1}: {lines[l_idx]}")
        break
