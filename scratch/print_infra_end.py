with open('public/map.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

with open('scratch/infra_end.txt', 'w', encoding='utf-8') as out:
    for i in range(1570, min(len(lines), 1715)):
        out.write(f'{i+1}: {lines[i]}')

print("SUCCESS: Written to scratch/infra_end.txt")
