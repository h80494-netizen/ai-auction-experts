import os

log_path = r"C:\Users\llll\.gemini\antigravity-ide\brain\03a97b0d-7beb-4c39-896d-4743ddee2934\.system_generated\tasks\task-1359.log"
if os.path.exists(log_path):
    print("Searching task-1359.log for exceptions/errors...")
    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    found_error = False
    for i, line in enumerate(lines):
        # check for keywords like Error, Exception, Traceback, 500
        if any(kw in line.lower() for kw in ['error', 'exception', 'traceback', ' 500 ']):
            print(f"Line {i+1}: {line.strip()}")
            found_error = True
            
            # Print next 10 lines if it looks like a traceback
            if 'traceback' in line.lower():
                for j in range(i+1, min(i+15, len(lines))):
                    print(f"  {lines[j].strip()}")
    if not found_error:
        print("No exceptions or errors found in the log.")
else:
    print("task-1359.log does not exist.")
