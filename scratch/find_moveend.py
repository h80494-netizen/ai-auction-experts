with open(r"c:\Users\llll\Documents\두인경매\바이브코딩\public\map.html", "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "moveend" in line or "moveEndTimeout" in line:
        print(f"L{idx+1}: {line.strip()}")
        # print 10 lines context
        start = max(0, idx - 5)
        end = min(len(lines), idx + 25)
        print("--- CONTEXT ---")
        for j in range(start, end):
            print(f"  L{j+1}: {lines[j].strip()}")
        print("=" * 60)
