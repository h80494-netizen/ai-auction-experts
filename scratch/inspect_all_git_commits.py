import subprocess

res = subprocess.run(["git", "log", "--pretty=format:%H"], capture_output=True, text=True, shell=True)
commits = res.stdout.strip().split("\n")
print("Commits:", commits)

for c in commits:
    res_show = subprocess.run(["git", "show", f"{c}:public/map.html"], capture_output=True, text=True, encoding="utf-8", errors="ignore", shell=True)
    content = res_show.stdout
    print(f"\nCommit {c[:8]} content length: {len(content)}")
    
    # Check if keywords exist
    for kw in ["fetchPlanningRoads", "fetchZoningPolygons", "fetchRedevelopmentZones", "planningRoads", "zoning"]:
        occ = content.count(kw)
        if occ > 0:
            print(f"  {kw}: {occ} times")
