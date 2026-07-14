with open(r"c:\Users\llll\Documents\두인경매\바이브코딩\scratch\modify_map_stages.py", "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "fetchPlanningRoads" in line or "planning-road" in line:
        print(f"L{idx+1}: {line.strip()}")
        # print 5 lines before and after
        start = max(0, idx - 5)
        end = min(len(lines), idx + 25)
        print("--- CONTEXT ---")
        for j in range(start, end):
            print(f"  L{j+1}: {lines[j].strip()}")
        print("=" * 50)
