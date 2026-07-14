import os

keywords = ["단계별", "도로종류", "도로종류별", "dev1-stages", "dev3-stages", "road_class", "road-class", "planning-road-class"]
found = []

for root, dirs, files in os.walk("c:/Users/llll/Documents/두인경매/바이브코딩"):
    if ".git" in root or "node_modules" in root or "__pycache__" in root or ".gemini" in root:
        continue
    for file in files:
        if file.endswith((".py", ".html", ".js", ".css", ".txt", ".json", ".md")):
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                for kw in keywords:
                    if kw in content:
                        found.append((file_path, kw))
            except Exception:
                pass

print(f"Found {len(found)} occurrences:")
for fpath, kw in found:
    print(f"File: {fpath} | Keyword: {kw}")
