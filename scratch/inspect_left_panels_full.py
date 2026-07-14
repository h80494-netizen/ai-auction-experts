import os

scratch_dir = "c:/Users/llll/Documents/두인경매/바이브코딩/scratch"
for f in os.listdir(scratch_dir):
    if f.startswith("left_panel_") and f.endswith(".html"):
        path = os.path.join(scratch_dir, f)
        with open(path, "r", encoding="utf-8", errors="ignore") as file:
            content = file.read()
        print(f"\n=======================================================")
        print(f"FILE: {f} (Length: {len(content)})")
        print(f"=======================================================")
        
        # print if planning or road exists
        for kw in ["planning", "road", "zoning", "fetch", "buffer"]:
            occ = content.lower().count(kw)
            print(f"  {kw}: {occ} times")
            if occ > 0:
                lines = content.split("\n")
                for idx, line in enumerate(lines):
                    if kw in line.lower():
                        print(f"    Line {idx+1}: {line.strip()[:100]}")
