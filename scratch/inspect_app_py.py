with open('backend/app.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

print("File size:", len(content))
lines = content.split('\n')
print("Total lines:", len(lines))

import re
# Find all lines containing "@app"
for i, line in enumerate(lines):
    if '@app.' in line:
        print(f"Line {i+1}: {line.strip()}")
