import os

fpath = r"c:\Users\llll\Documents\두인경매\바이브코딩\scratch\temp_map.js"
output_file = r"c:\Users\llll\Documents\두인경매\바이브코딩\scratch\temp_map_extracted.txt"

if not os.path.exists(fpath):
    print("temp_map.js does not exist!")
    exit(1)

with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

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

targets = [
    "async function fetchPlanningRoads", "function fetchPlanningRoads",
    "async function fetchZoningPolygons", "function fetchZoningPolygons",
    "async function fetchRedevelopmentZones", "function fetchRedevelopmentZones"
]

extracted = []
for t in targets:
    if t in content:
        body = extract_function_by_braces(content, t)
        if body:
            extracted.append((t, body))

with open(output_file, "w", encoding="utf-8") as f:
    for t, body in extracted:
        f.write("=" * 80 + "\n")
        f.write(f"FUNCTION: {t}\n")
        f.write("=" * 80 + "\n")
        f.write(body + "\n\n")

print(f"Done! Extracted {len(extracted)} functions from temp_map.js")
