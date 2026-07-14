with open("c:/Users/llll/Documents/두인경매/바이브코딩/public/map.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "planningRoads" in line:
        print(f"L{idx+1}: {line.strip()}")
