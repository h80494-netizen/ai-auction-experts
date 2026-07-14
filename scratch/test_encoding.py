import sys

with open('public/analysis.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(1000, min(1095, len(lines))):
    sys.stdout.buffer.write(f"{i+1}: {lines[i]}".encode('utf-8'))
