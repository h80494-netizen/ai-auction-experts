with open(r"c:\Users\llll\Documents\두인경매\바이브코딩\public\map.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "layers" in line and ("=" in line or "const" in line or "let" in line or "var" in line):
        if i < 1400: # before applyHighlighter
            print(f"Line {i+1}: {line.strip()}")
