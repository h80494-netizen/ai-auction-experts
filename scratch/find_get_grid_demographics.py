with open('backend/app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'def get_grid_demographics' in line:
        print(f"{idx+1}: {line.strip()}")
        # print next 40 lines
        for j in range(idx, min(len(lines), idx+45)):
            print(f"  {j+1}: {lines[j]}", end='')
