import os

log_path = r"backend/server.log"
if not os.path.exists(log_path):
    log_path = "server.log"

print("Checking log path:", log_path)

with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")

# Search for ERROR, Exception, or Traceback in the last 10000 lines
print("\n--- ERROR AND EXCEPTION SEARCH ---")
count = 0
for idx, line in enumerate(lines[-10000:]):
    if "error" in line.lower() or "exception" in line.lower() or "traceback" in line.lower() or "500" in line:
        # Print the line and maybe 3 lines after if it's traceback
        print(f"Line {len(lines)-10000+idx}: {line.strip()}")
        count += 1
        if count > 100:
            print("Too many errors, truncating...")
            break
