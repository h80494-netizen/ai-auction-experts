with open("public/map.html", "r", encoding="utf-8") as f:
    for i, line in enumerate(f, 1):
        if "fetchRoadFlows" in line:
            print(f"Line {i}: {line.strip()}")
