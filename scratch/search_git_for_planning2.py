import subprocess
import re

try:
    print("Searching git commits for fetchPlanningRoads or planningRoads...")
    # Get all commit hashes
    res = subprocess.run(["git", "log", "--pretty=format:%H"], capture_output=True, text=True, encoding="utf-8", errors="ignore", shell=True)
    commits = res.stdout.strip().split("\n")
    
    for c in commits:
        res_show = subprocess.run(["git", "show", f"{c}:public/map.html"], capture_output=True, text=True, encoding="utf-8", errors="ignore", shell=True)
        content = res_show.stdout
        if "fetchPlanningRoads" in content or "planningRoads" in content:
            print(f"FOUND IN COMMIT: {c}")
            # Find and print the function definition if exists
            match = re.search(r'async function fetchPlanningRoads.*?\n\s*\}', content, re.DOTALL)
            if match:
                print("  FUNCTION BODY:")
                print(match.group(0))
            else:
                # Let's search line by line
                for idx, line in enumerate(content.split("\n")):
                    if "fetchPlanningRoads" in line:
                        print(f"    L{idx+1}: {line.strip()}")
                
    # Also search reflog or dangling commits if any
    print("\nSearching reflog/dangling commits...")
    res_ref = subprocess.run(["git", "reflog"], capture_output=True, text=True, encoding="utf-8", errors="ignore", shell=True)
    lines = res_ref.stdout.strip().split("\n")
    print("Reflog entries count:", len(lines))
    for l in lines[:10]:
        print(l)
    
except Exception as e:
    print("ERROR:", e)
