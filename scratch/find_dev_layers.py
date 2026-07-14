with open("public/map.html", "r", encoding="utf-8") as f:
    lines = f.readlines()
for idx, line in enumerate(lines):
    if any(x in line for x in ["planningRoads", "planning_roads", "dev1", "dev2", "dev3"]):
        print(f"Line {idx+1}: {line.strip()}")
