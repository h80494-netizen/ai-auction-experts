with open("c:/Users/llll/Documents/두인경매/바이브코딩/public/map.html", "r", encoding="utf-8") as f:
    content = f.read()

lines = content.split("\n")
print(f"Total lines: {len(lines)}")

print("\n--- OCCURRENCES OF ISSUES.HTML OR 이쉬 IN MAP.HTML ---")
for idx, line in enumerate(lines):
    if "issues.html" in line or "이슈" in line:
        print(f"L{idx+1}: {line.strip()[:120]}")
