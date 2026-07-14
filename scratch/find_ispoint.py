with open("public/map.html", "r", encoding="utf-8") as f:
    content = f.read()
lines = content.splitlines()
for idx, line in enumerate(lines):
    if any(x in line for x in ["isPoint", "NearPolygon", "distance", "buffer"]):
        print(f"Line {idx+1}: {line.strip()}")
