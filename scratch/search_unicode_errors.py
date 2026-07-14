import os

log_path = r"backend/server.log"
if not os.path.exists(log_path):
    log_path = "server.log"

print("Checking log path:", log_path)

with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")

print("\n--- UnicodeEncodeError SEARCH ---")
for idx, line in enumerate(lines):
    if "unicodeencodeerror" in line.lower() or "latin-1" in line.lower():
        print(f"Line {idx+1}: {line.strip()}")
