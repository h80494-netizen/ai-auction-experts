import os

def search():
    target = "fetchPlanningRoads"
    # Search root and scratch
    for folder in [".", "scratch"]:
        for f in os.listdir(folder):
            if f.endswith((".js", ".html", ".py")):
                path = os.path.join(folder, f)
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as file:
                        content = file.read()
                    if target in content:
                        print(f"FOUND IN: {path} (Length: {len(content)})")
                        # Search for function definition
                        lines = content.split("\n")
                        for idx, line in enumerate(lines):
                            if "function fetchPlanningRoads" in line or "fetchPlanningRoads = " in line or "fetchPlanningRoads(" in line:
                                print(f"  Line {idx+1}: {line.strip()}")
                                # print 40 lines after it
                                for j in range(40):
                                    if idx + j < len(lines):
                                        print(f"    {lines[idx+j]}")
                except Exception as e:
                    pass

search()
