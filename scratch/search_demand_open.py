with open(r"c:\Users\llll\Documents\두인경매\바이브코딩\public\map.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "demand-panel" in line or "Demand" in line or "demand" in line:
        if "style" not in line and "class" not in line and "div" not in line:
            print(f"Line {i+1}: {line.strip()}")
