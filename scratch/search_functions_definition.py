import re

file_path = r"c:\Users\llll\Documents\두인경매\바이브코딩\scratch\workspace_search_results.txt"

with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

# Let's find any matches with fetchPlanningRoads
matches = re.findall(r'FILE: (.*?) \| LINE: (\d+).*?\n(.*?)\n', content)

print(f"Total lines in results: {len(matches)}")

for fpath, line_num, line_content in matches:
    if "planning_roads_occurrences" in fpath or "workspace_search_results" in fpath or "found_in_scratch" in fpath:
        continue
    if "function" in line_content or "fetchPlanningRoads" in line_content:
        # print if it defines it
        if "function fetchPlanningRoads" in line_content or "fetchPlanningRoads = " in line_content or "fetchPlanningRoads(" in line_content:
            print(f"FILE: {fpath} | L{line_num}: {line_content}")
