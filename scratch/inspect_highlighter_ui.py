with open('public/map.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

with open('scratch/highlighter_ui.txt', 'w', encoding='utf-8') as out:
    for i in range(899, min(len(lines), 960)):
        out.write(f'{i+1}: {lines[i]}')

print("SUCCESS: Written to scratch/highlighter_ui.txt")
