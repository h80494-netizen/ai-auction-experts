import os

scratch_dir = r"c:\Users\llll\Documents\두인경매\바이브코딩\scratch"

for file in os.listdir(scratch_dir):
    if file.startswith("left_panel_") and file.endswith(".html"):
        fpath = os.path.join(scratch_dir, file)
        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        print(f"FILE: {file}")
        print("  dev1-stage-check in file:", "dev1-stage-check" in content)
        print("  planning-road in file:", "planning-road" in content)
        print("  zoning in file:", "zoning" in content)
        print("  dev3 in file:", "dev3" in content)
