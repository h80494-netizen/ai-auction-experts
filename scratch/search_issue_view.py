with open("c:/Users/llll/Documents/두인경매/바이브코딩/public/map.html", "r", encoding="utf-8") as f:
    content = f.read()

lines = content.split("\n")
print(f"Total lines: {len(lines)}")

print("\n--- OCCURRENCES OF ISSUE/이슈 ---")
for idx, line in enumerate(lines):
    if "이슈" in line or "issue" in line.lower():
        print(f"L{idx+1}: {line.strip()}")
