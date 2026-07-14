with open("c:/Users/llll/Documents/두인경매/바이브코딩/public/map.html", "r", encoding="utf-8") as f:
    content = f.read()

lines = content.split("\n")
for idx, line in enumerate(lines):
    if "<script" in line.lower() and not "src=" in line.lower():
        print(f"Script tag starts at L{idx+1}: {line.strip()[:100]}")
    if "</script>" in line.lower():
        print(f"Script tag ends at L{idx+1}")
