import os

# Check backend/downloads filenames ords
p = r"backend/downloads"
if os.path.exists(p):
    files = os.listdir(p)
    for f in files:
        if "117137" in f:
            print(f"Filename: {f}")
            print("Characters:")
            for c in f:
                print(f"  '{c}': {ord(c)} (hex: {hex(ord(c))})")
