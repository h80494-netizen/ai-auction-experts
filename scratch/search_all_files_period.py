import os

root_dir = r"c:\Users\llll\Documents\두인경매\바이브코딩"
output_file = r"c:\Users\llll\Documents\두인경매\바이브코딩\scratch\workspace_search_results.txt"

keywords = ["fetchPlanningRoads", "planning_roads", "zoning", "redevelopment_zones"]
results = []

for root, dirs, files in os.walk(root_dir):
    if ".git" in root or ".gemini" in root or "node_modules" in root or "__pycache__" in root:
        continue
    for file in files:
        if file.endswith((".py", ".html", ".js", ".css", ".txt")):
            fpath = os.path.join(root, file)
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                
                # Check if any keyword in content
                matched_kws = [kw for kw in keywords if kw in content]
                if matched_kws:
                    # Let's find the lines
                    lines = content.split("\n")
                    for idx, line in enumerate(lines):
                        if any(kw in line for kw in matched_kws):
                            results.append((fpath, idx + 1, line.strip(), matched_kws))
            except Exception as e:
                pass

with open(output_file, "w", encoding="utf-8") as f:
    for fpath, line_num, content, kws in results:
        f.write(f"FILE: {fpath} | LINE: {line_num} | KWS: {kws}\n")
        f.write(content + "\n" + "-"*40 + "\n")

print(f"Done! Found {len(results)} matches.")
