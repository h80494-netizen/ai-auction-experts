with open("c:/Users/llll/Documents/두인경매/바이브코딩/public/issues.html", "r", encoding="utf-8") as f:
    content = f.read()

lines = content.split("\n")

print("\n--- OCCURRENCES OF SEARCH-ROW ---")
for idx, line in enumerate(lines):
    if "search-row" in line or "filter" in line or "header" in line:
        if "L" not in line and "idx" not in line:
            # Let's print style lines
            if idx > 30 and idx < 1200:
                print(f"L{idx+1}: {line.strip()[:100]}")
