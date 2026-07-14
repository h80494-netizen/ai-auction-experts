import os
for f in os.listdir("c:/Users/llll/Documents/두인경매/바이브코딩/scratch"):
    if f.endswith((".py", ".html", ".js")):
        fpath = os.path.join("c:/Users/llll/Documents/두인경매/바이브코딩/scratch", f)
        try:
            with open(fpath, "r", encoding="utf-8", errors="ignore") as file_obj:
                content = file_obj.read()
            if "fetchPlanningRoads" in content or "planning_roads" in content or "planningRoads" in content or "계획도로" in content:
                print("FOUND IN:", f)
                # Find lines
                for idx, line in enumerate(content.split("\n")[:300]): # Limit search area
                    if "fetchPlanningRoads" in line or "function" in line and "Road" in line:
                        print(f"  L{idx+1}: {line.strip()}")
        except Exception:
            pass
