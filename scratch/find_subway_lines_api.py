with open("backend/app.py", "r", encoding="utf-8") as f:
    lines = f.readlines()
for idx, line in enumerate(lines):
    if "/api/map/subway_lines" in line or "subway_lines" in line:
        print(f"Line {idx+1}: {line.strip()}")
