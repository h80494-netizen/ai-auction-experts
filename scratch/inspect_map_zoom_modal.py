with open("c:/Users/llll/Documents/두인경매/바이브코딩/public/issues.html", "r", encoding="utf-8") as f:
    content = f.read()

lines = content.split("\n")

print("\n--- OCCURRENCES OF MAP ZOOM MODAL ---")
for idx, line in enumerate(lines):
    if "mapZoomModal" in line or "map-dialog" in line or "modalMap" in line:
        print(f"L{idx+1}: {line.strip()[:100]}")
