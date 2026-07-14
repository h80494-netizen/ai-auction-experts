import os
import sys

log_path = r"C:\Users\llll\.gemini\antigravity-ide\brain\03a97b0d-7beb-4c39-896d-4743ddee2934\.system_generated\tasks\task-1359.log"
if os.path.exists(log_path):
    print("Reading task-1359.log...")
    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        lines = content.splitlines()
        for line in lines[-200:]:
            # Print line safely ignoring non-cp949 characters
            print(line.encode('cp949', errors='ignore').decode('cp949'))
else:
    print("task-1359.log does not exist.")
