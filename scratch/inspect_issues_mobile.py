with open("c:/Users/llll/Documents/두인경매/바이브코딩/public/issues.html", "r", encoding="utf-8") as f:
    content = f.read()

lines = content.split("\n")
print(f"Total lines: {len(lines)}")

print("\n--- FIXED WIDTHS IN ISSUES.HTML STYLE ---")
style_started = False
for idx, line in enumerate(lines):
    if "<style>" in line:
        style_started = True
    if "</style>" in line:
        style_started = False
    
    if style_started:
        if "width" in line and "px" in line and not "max-width" in line:
            # check if it's inside media query
            print(f"L{idx+1}: {line.strip()}")
            
print("\n--- MEDIA QUERIES IN ISSUES.HTML ---")
for idx, line in enumerate(lines):
    if "@media" in line:
        print(f"L{idx+1}: {line.strip()}")
        # print next 10 lines
        for j in range(1, 12):
            if idx + j < len(lines):
                print(f"  +{j}: {lines[idx+j].strip()}")
