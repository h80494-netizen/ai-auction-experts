with open("c:/Users/llll/Documents/두인경매/바이브코딩/public/issues.html", "r", encoding="utf-8") as f:
    content = f.read()

lines = content.split("\n")

print("\n--- OCCURRENCES OF NAVIGATION ITEMS IN ISSUES.HTML ---")
for idx, line in enumerate(lines):
    if "이슈" in line or "지도" in line or "menu" in line or "nav" in line or "logo" in line:
        if idx > 1200 and idx < 1550: # HTML section
            print(f"L{idx+1}: {line.strip()[:100]}")
