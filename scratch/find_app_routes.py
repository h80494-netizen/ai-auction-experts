import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('backend/app.py', 'r', encoding='cp949', errors='ignore') as f:
    for idx, line in enumerate(f):
        if '@app.get' in line or '@app.post' in line:
            print(f"Line {idx+1}: {line.strip()}")
