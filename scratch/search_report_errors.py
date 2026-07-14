import os

log_path = r"C:\Users\llll\.gemini\antigravity-ide\brain\03a97b0d-7beb-4c39-896d-4743ddee2934\.system_generated\tasks\task-1359.log"
if os.path.exists(log_path):
    print("Searching task-1359.log for 2024 or 117137...")
    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines):
        if '117137' in line or '2024' in line or 'ERROR' in line or 'error' in line:
            # Print line and surroundings
            start = max(0, i-2)
            end = min(len(lines), i+8)
            print(f"--- Match at line {i+1} ---")
            for j in range(start, end):
                l_safe = lines[j].strip().encode('cp949', errors='ignore').decode('cp949')
                print(f"{j+1}: {l_safe}")
else:
    print("task-1359.log does not exist.")
