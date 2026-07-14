with open("c:/Users/llll/Documents/두인경매/바이브코딩/public/issues.html", "r", encoding="utf-8") as f:
    content = f.read()

lines = content.split("\n")

print("\n--- OCCURRENCES OF CATEGORIES OR TABS ---")
for idx, line in enumerate(lines):
    if "class=\"filter-row\"" in line or "class=\"category" in line or "category-tab" in line:
        print(f"L{idx+1}: {line.strip()[:100]}")
        # print style rules
        for j in range(-5, 10):
            if idx + j >= 0 and idx + j < len(lines):
                print(f"  [{j}]: {lines[idx+j].strip()[:100]}")
        print("="*50)
