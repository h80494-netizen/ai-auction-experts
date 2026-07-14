import os

scratch_dir = r"c:\Users\llll\Documents\두인경매\바이브코딩\scratch"
output_file = r"c:\Users\llll\Documents\두인경매\바이브코딩\scratch\planning_roads_occurrences.txt"

keyword = "fetchPlanningRoads"

results = []

for file in os.listdir(scratch_dir):
    if file.endswith((".py", ".html", ".js", ".txt")) and file != "planning_roads_occurrences.txt":
        fpath = os.path.join(scratch_dir, file)
        try:
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
            for idx, line in enumerate(lines):
                if keyword in line:
                    start_idx = max(0, idx - 40)
                    end_idx = min(len(lines), idx + 60)
                    snippet = "".join(lines[start_idx:end_idx])
                    results.append((file, idx + 1, snippet))
        except Exception as e:
            pass

with open(output_file, "w", encoding="utf-8") as f:
    for file, line_num, snippet in results:
        f.write("=" * 80 + "\n")
        f.write(f"FILE: {file} | LINE: {line_num}\n")
        f.write("=" * 80 + "\n")
        f.write(snippet + "\n\n")

print(f"Done! Found {len(results)} occurrences.")
