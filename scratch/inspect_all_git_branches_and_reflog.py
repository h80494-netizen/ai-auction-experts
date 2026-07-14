import subprocess

try:
    # 1. Search stashes
    res_stash = subprocess.run(["git", "stash", "list"], capture_output=True, text=True, shell=True)
    print("Stashes:")
    print(res_stash.stdout)
    
    # 2. Search all branches
    res_br = subprocess.run(["git", "branch", "-a"], capture_output=True, text=True, shell=True)
    print("Branches:")
    print(res_br.stdout)

    # 3. Find any commit in any branch/reflog that has fetchPlanningRoads
    res_grep = subprocess.run(["git", "log", "--all", "-S", "fetchPlanningRoads", "--oneline"], capture_output=True, text=True, shell=True)
    print("Commits with fetchPlanningRoads:")
    print(res_grep.stdout)

except Exception as e:
    print("ERROR:", e)
