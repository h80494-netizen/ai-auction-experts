with open(r"c:\Users\llll\Documents\두인경매\바이브코딩\public\map.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "상권" in line or "분석" in line or "demand" in line or "배후수요" in line:
        print(f"Line {i+1}: {line.strip()}")
