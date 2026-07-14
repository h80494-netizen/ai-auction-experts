with open("public/map.html", "r", encoding="utf-8") as f:
    content = f.read()
lines = content.splitlines()
print("Total lines in public/map.html:", len(lines))
for idx, line in enumerate(lines):
    if "toggle-dev2" in line:
        print(f"Line {idx+1}: {line.strip()}")
