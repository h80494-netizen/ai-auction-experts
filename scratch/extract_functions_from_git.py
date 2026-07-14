import subprocess
import os

file_path = r"c:\Users\llll\Documents\두인경매\바이브코딩\public\map.html"
output_file = r"c:\Users\llll\Documents\두인경매\바이브코딩\scratch\extracted_functions.txt"

# Let's get the list of commits
res = subprocess.run(["git", "log", "--pretty=format:%H"], capture_output=True, text=True, encoding="utf-8", errors="ignore", shell=True)
commits = res.stdout.strip().split("\n")

print(f"Total commits: {len(commits)}")

def extract_function_by_braces(content, target_name):
    # Find the function signature
    start_idx = content.find(target_name)
    if start_idx == -1:
        return None
    
    # We want to find where the function body starts (at the first '{' after signature)
    brace_start = content.find("{", start_idx)
    if brace_start == -1:
        return None
    
    # Let's count open/close braces
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

targets = ["async function fetchPlanningRoads", "async function fetchZoningPolygons", "async function fetchRedevelopmentZones"]

extracted = {}

for commit in commits:
    res_show = subprocess.run(["git", "show", f"{commit}:public/map.html"], capture_output=True, text=True, encoding="utf-8", errors="ignore", shell=True)
    content = res_show.stdout
    if not content:
        continue
    
    for t in targets:
        if t in content and t not in extracted:
            fn_body = extract_function_by_braces(content, t)
            if fn_body:
                extracted[t] = (commit, fn_body)

# Write extracted functions to file
with open(output_file, "w", encoding="utf-8") as f:
    for t, (commit, body) in extracted.items():
        f.write("=" * 80 + "\n")
        f.write(f"FUNCTION: {t}\n")
        f.write(f"FOUND IN COMMIT: {commit}\n")
        f.write("=" * 80 + "\n")
        f.write(body + "\n\n")

print(f"Extracted {len(extracted)} functions to {output_file}")
