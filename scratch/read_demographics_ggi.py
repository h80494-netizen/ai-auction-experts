with open('backend/app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(1590, 1700):
    if i < len(lines):
        print(f"{i+1}: {lines[i]}", end='')
