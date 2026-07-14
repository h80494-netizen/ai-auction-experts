with open(r"c:\Users\llll\Documents\두인경매\바이브코딩\scratch\temp_map.js", "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

print(f"Total lines in temp_map.js: {len(lines)}")

# Search for dev1-stage-check
for idx, line in enumerate(lines):
    if "dev1-stage-check" in line or "planning-road-class-check" in line:
        print(f"L{idx+1}: {line.strip()}")
