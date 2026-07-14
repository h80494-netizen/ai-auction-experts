with open("c:/Users/llll/Documents/두인경매/바이브코딩/public/issues.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

print("\n--- ISSUES.HTML HEADER AREA ---")
for i in range(1340, 1435):
    if i < len(lines):
        print(f"L{i+1}: {lines[i].strip()[:120]}")
