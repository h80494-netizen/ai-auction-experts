import os

scratch_dir = "c:/Users/llll/Documents/두인경매/바이브코딩/scratch"
for f in os.listdir(scratch_dir):
    if f.startswith("left_panel_") and f.endswith(".html"):
        path = os.path.join(scratch_dir, f)
        with open(path, "r", encoding="utf-8", errors="ignore") as file:
            content = file.read()
        if "planning" in content.lower() or "계획도로" in content:
            print(f"FOUND in {f}")
            # print lines containing planning or plans
            lines = content.split("\n")
            for idx, line in enumerate(lines):
                if any(x in line.lower() for x in ["planning", "계획도로", "도로종류", "도로종류별", "도로에 대한 버퍼", "도로에"]):
                    print(f"  L{idx+1}: {line.strip()}")
