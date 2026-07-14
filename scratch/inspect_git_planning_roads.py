import subprocess
import os

try:
    res = subprocess.run(["git", "log", "--pretty=format:%H"], capture_output=True, text=True, shell=True)
    commits = res.stdout.strip().split("\n")
    
    for c in commits:
        res_show = subprocess.run(["git", "show", f"{c}:public/map.html"], capture_output=True, text=True, encoding="utf-8", errors="ignore", shell=True)
        content = res_show.stdout
        
        if "fetchPlanningRoads" in content:
            print(f"\n=======================================================")
            print(f"FOUND IN COMMIT: {c}")
            print(f"=======================================================")
            lines = content.split("\n")
            for idx, line in enumerate(lines):
                if "function fetchPlanningRoads" in line or "fetchPlanningRoads = function" in line or "fetchPlanningRoads = async" in line or ("async" in line and "fetchPlanningRoads" in line and "function" in line):
                    print(f"Match found at line {idx+1}: {line}")
                    # Print 80 lines after it
                    for j in range(80):
                        if idx + j < len(lines):
                            print(lines[idx + j])
                    break
except Exception as e:
    print("ERROR:", e)
