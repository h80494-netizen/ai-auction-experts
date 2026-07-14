import os

scratch_dir = r"c:\Users\llll\Documents\두인경매\바이브코딩\scratch"
output_file = r"c:\Users\llll\Documents\두인경매\바이브코딩\scratch\found_in_scratch.txt"

targets = ["function fetchPlanningRoads", "function fetchZoningPolygons", "function fetchRedevelopmentZones", "updateTaekjiLayer"]

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

results = []

for file in os.listdir(scratch_dir):
    if file.endswith((".py", ".html", ".js", ".txt")):
        fpath = os.path.join(scratch_dir, file)
        try:
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            for t in targets:
                if t in content:
                    fn_body = extract_function_by_braces(content, t)
                    if fn_body:
                        results.append((file, t, fn_body))
        except Exception as e:
            pass

with open(output_file, "w", encoding="utf-8") as f:
    for file, t, body in results:
        f.write("=" * 80 + "\n")
        f.write(f"FILE: {file} | FUNCTION: {t}\n")
        f.write("=" * 80 + "\n")
        f.write(body + "\n\n")

print(f"Done! Found {len(results)} matches.")
