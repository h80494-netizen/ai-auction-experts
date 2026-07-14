with open('backend/app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'is_seoul' in line:
        print(f"{idx+1}: {line.strip()}")
