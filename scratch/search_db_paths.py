with open('backend/app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'db' in line.lower() and ('path' in line.lower() or 'connect' in line.lower()):
        print(f"Line {idx+1}: {line.strip()[:120]}")
