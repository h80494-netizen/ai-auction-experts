with open('backend/app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'run_in_threadpool' in line:
        print(f"L{idx+1}: {line.strip()}")
