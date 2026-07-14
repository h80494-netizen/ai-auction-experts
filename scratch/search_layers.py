with open("public/map.html", "r", encoding="utf-8") as f:
    for i, line in enumerate(f, 1):
        if "layers" in line and ("const " in line or "var " in line or "let " in line or " = {" in line):
            print(f"Line {i}: {line.strip()}")
