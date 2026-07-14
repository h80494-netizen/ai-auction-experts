with open('public/map.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

with open('scratch/highlighter_listener.txt', 'w', encoding='utf-8') as out:
    for i in range(1444, min(len(lines), 1475)):
        out.write(f'{i+1}: {lines[i]}')

print("SUCCESS: Written to scratch/highlighter_listener.txt")
