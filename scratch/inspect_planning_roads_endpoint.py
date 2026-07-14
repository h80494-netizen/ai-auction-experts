with open("c:/Users/llll/Documents/두인경매/바이브코딩/backend/app.py", "r", encoding="utf-8") as f:
    content = f.read()

lines = content.split("\n")
print(f"Total app.py lines: {len(lines)}")

print("\n--- ENDPOINTS RELATED TO PLANNING OR ROADS ---")
for idx, line in enumerate(lines):
    if "@app.get" in line and any(k in line for k in ["planning", "road", "zoning", "dev"]):
        print(f"L{idx+1}: {line}")
        # Print next 30 lines
        for j in range(1, 35):
            if idx + j < len(lines):
                print(f"  +{j}: {lines[idx+j]}")
        print("="*50)
