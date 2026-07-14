with open(r"c:\Users\llll\Documents\두인경매\바이브코딩\public\map.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "addEventListener" in line and ("toggle-" in line or "change" in line):
        print(f"Line {i+1}: {line.strip()}")
