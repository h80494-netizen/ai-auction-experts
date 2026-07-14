import os

def search_text_files():
    target = "function fetchPlanningRoads"
    for root, dirs, files in os.walk("c:/Users/llll/Documents/두인경매/바이브코딩"):
        if ".git" in root or "node_modules" in root or "__pycache__" in root or ".gemini" in root:
            continue
        for file in files:
            if file.endswith((".py", ".html", ".js", ".txt")):
                fpath = os.path.join(root, file)
                try:
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    if target in content:
                        print(f"FOUND FUNCTION IN {fpath}")
                        # Print function definition block
                        lines = content.split("\n")
                        started = False
                        brace_count = 0
                        for idx, line in enumerate(lines):
                            if target in line:
                                started = True
                            if started:
                                print(f"L{idx+1}: {line}")
                                brace_count += line.count("{")
                                brace_count -= line.count("}")
                                if brace_count == 0 and idx > 0 and "}" in line:
                                    break
                except Exception as e:
                    print("ERROR:", e)

search_text_files()
