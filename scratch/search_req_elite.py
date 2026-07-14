import glob

files = ["public/map.html", "public/script.js"]
for fpath in files:
    print("Checking", fpath)
    with open(fpath, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            if "req-elite-school" in line:
                print(f"Line {i}: {line.strip()}")
