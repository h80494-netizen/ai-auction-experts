with open("c:/Users/llll/Documents/두인경매/바이브코딩/public/style.css", "r", encoding="utf-8") as f:
    content = f.read()

lines = content.split("\n")
print(f"Total style.css lines: {len(lines)}")

print("\n--- MEDIA QUERIES IN STYLE.CSS ---")
for idx, line in enumerate(lines):
    if "@media" in line:
        print(f"L{idx+1}: {line}")
        # print next 10 lines
        for j in range(1, 12):
            if idx + j < len(lines):
                print(f"  +{j}: {lines[idx+j].strip()}")
