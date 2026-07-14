with open(r"c:\Users\llll\Documents\두인경매\바이브코딩\scratch\planning_roads_occurrences.txt", "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

import re
# Find occurrences of async function fetchPlanningRoads
matches = re.finditer(r'async function fetchPlanningRoads', content)
for m in matches:
    start_idx = m.start()
    # print 1500 characters
    print(content[start_idx:start_idx+1500])
    print("=" * 100)
