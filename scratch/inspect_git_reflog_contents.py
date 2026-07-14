import subprocess
import re

try:
    # Get all reflog commit hashes
    res = subprocess.run(["git", "reflog", "--pretty=format:%H"], capture_output=True, text=True, shell=True)
    commits = list(set(res.stdout.strip().split("\n")))
    print(f"Total reflog commits: {len(commits)}")
    
    for c in commits:
        if not c:
            continue
        res_show = subprocess.run(["git", "show", f"{c}:public/map.html"], capture_output=True, text=True, encoding="utf-8", errors="ignore", shell=True)
        content = res_show.stdout
        
        target = "fetchPlanningRoads"
        if target in content:
            print(f"\n=======================================================")
            print(f"FOUND IN REFLOG COMMIT: {c}")
            print(f"=======================================================")
            lines = content.split("\n")
            for idx, line in enumerate(lines):
                if "function fetchPlanningRoads" in line or "fetchPlanningRoads = " in line or "fetchPlanningRoads(" in line:
                    print(f"  Line {idx+1}: {line}")
                    # print balanced braces block
                    brace_count = 0
                    started = False
                    for j in range(120):
                        if idx + j < len(lines):
                            curr = lines[idx + j]
                            print(curr)
                            brace_count += curr.count("{")
                            brace_count -= curr.count("}")
                            if brace_count == 0 and j > 0 and "}" in curr:
                                break
                    break
            break
except Exception as e:
    print("ERROR:", e)
