import os

log_path = r"C:\Users\llll\.gemini\antigravity-ide\brain\7fc71f7c-05d1-45e3-807b-237db18fcee3\.system_generated\tasks\task-198.log"
if os.path.exists(log_path):
    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
        print("Last 15 lines of log:")
        for line in lines[-15:]:
            print(line.strip())
else:
    print("Log file not found.")
