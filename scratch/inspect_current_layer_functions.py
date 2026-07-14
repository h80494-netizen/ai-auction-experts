with open("c:/Users/llll/Documents/두인경매/바이브코딩/public/map.html", "r", encoding="utf-8") as f:
    content = f.read()

lines = content.split("\n")
print("Total lines:", len(lines))

print("\n--- FUNCTIONS CONTAINING 'fetch' ---")
for idx, line in enumerate(lines):
    if "function fetch" in line or "async function fetch" in line:
        print(f"L{idx+1}: {line.strip()}")
