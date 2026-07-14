with open('backend/doc_generator.py', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'detail' in line.lower() or 'html' in line.lower() or 'result' in line.lower():
        print(f"Line {idx+1}: {line.strip()[:140]}")
