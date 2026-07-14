with open("c:/Users/llll/Documents/두인경매/바이브코딩/public/issues.html", "r", encoding="utf-8") as f:
    content = f.read()

lines = content.split("\n")

print("\n--- STYLING FOR MAP-MODAL ---")
style_started = False
for idx, line in enumerate(lines):
    if "<style>" in line:
        style_started = True
    if "</style>" in line:
        style_started = False
    
    if style_started:
        if "modal" in line.lower() or "dialog" in line.lower() or "map-modal" in line:
            print(f"L{idx+1}: {line.strip()}")
            # Print next 20 lines
            for j in range(1, 25):
                if idx + j < len(lines):
                    print(f"  +{j}: {lines[idx+j].strip()}")
            print("="*50)
