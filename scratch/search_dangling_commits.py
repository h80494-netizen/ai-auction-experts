import subprocess
import os

output_file = r"c:\Users\llll\Documents\두인경매\바이브코딩\scratch\dangling_commits_search.txt"

print("Running git fsck --lost-found...")
res_fsck = subprocess.run(["git", "fsck", "--lost-found"], capture_output=True, text=True, encoding="utf-8", errors="ignore", shell=True)

# Parse dangling commits
# Format: "dangling commit <hash>"
commits = []
for line in res_fsck.stdout.split("\n"):
    if "dangling commit" in line:
        commits.append(line.split()[-1])

print(f"Found {len(commits)} dangling commits.")

found_commits = []

for c in commits:
    res_show = subprocess.run(["git", "show", f"{c}:public/map.html"], capture_output=True, text=True, encoding="utf-8", errors="ignore", shell=True)
    content = res_show.stdout
    if "fetchPlanningRoads" in content:
        print(f"FOUND IN DANGLING COMMIT: {c}")
        # Extract functions
        def extract_function_by_braces(content, target_name):
            start_idx = content.find(target_name)
            if start_idx == -1:
                return None
            brace_start = content.find("{", start_idx)
            if brace_start == -1:
                return None
            brace_count = 1
            idx = brace_start + 1
            while brace_count > 0 and idx < len(content):
                char = content[idx]
                if char == "{":
                    brace_count += 1
                elif char == "}":
                    brace_count -= 1
                idx += 1
            return content[start_idx:idx]
        
        extracted = {}
        for t in ["async function fetchPlanningRoads", "function fetchPlanningRoads", "async function fetchZoningPolygons", "async function fetchRedevelopmentZones"]:
            body = extract_function_by_braces(content, t)
            if body:
                extracted[t] = body
        
        found_commits.append((c, extracted))

with open(output_file, "w", encoding="utf-8") as f:
    f.write(f"FSK OUTPUT:\n{res_fsck.stdout}\n\n")
    for commit, ext in found_commits:
        f.write("=" * 80 + "\n")
        f.write(f"DANGLING COMMIT: {commit}\n")
        f.write("=" * 80 + "\n")
        for t, body in ext.items():
            f.write(f"--- FUNCTION: {t} ---\n")
            f.write(body + "\n\n")

print(f"Done! Searched {len(commits)} commits, found {len(found_commits)} matching.")
