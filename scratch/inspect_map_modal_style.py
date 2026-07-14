with open("c:/Users/llll/Documents/두인경매/바이브코딩/public/issues.html", "r", encoding="utf-8") as f:
    content = f.read()

lines = content.split("\n")

print("\n--- OCCURRENCES OF .MAP-MODAL STYLE ---")
for idx, line in enumerate(lines):
    if ".map-modal" in line:
        print(f"L{idx+1}: {line}")
        # print next 10 lines
        for j in range(1, 15):
            if idx + j < len(lines):
                print(f"  +{j}: {lines[idx+j].strip()}")
        print("="*50)
