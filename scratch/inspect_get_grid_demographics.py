with open('backend/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
for i, line in enumerate(lines):
    if 'def get_grid_demographics' in line:
        print(f"Line {i+1}: {line.strip()}")
        # Print next 20 lines
        for j in range(i+1, min(i+25, len(lines))):
            print(f"  {j+1}: {lines[j]}")
        break
