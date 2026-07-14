import os

log_path = r"C:\Users\llll\.gemini\antigravity-ide\brain\03a97b0d-7beb-4c39-896d-4743ddee2934\.system_generated\tasks\task-1359.log"

print("Checking task log path:", log_path)

with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")

print("\n--- ERROR SEARCH IN TASK LOG ---")
for idx, line in enumerate(lines):
    line_lower = line.lower()
    if "실패" in line or "error" in line_lower or "exception" in line_lower or "traceback" in line_lower or "failed" in line_lower:
        print(f"Line {idx+1}: {line.strip()}")
