import os
import unicodedata

# Let's check both root and backend/ downloads
paths = [
    r"downloads",
    r"backend/downloads"
]

for p in paths:
    if os.path.exists(p):
        print(f"Path {p} exists. Files in it:")
        files = os.listdir(p)
        for f in files:
            if "117137" in f or "5020" in f:
                print(f"  - {f} (NFC: {unicodedata.is_normalized('NFC', f)}, NFD: {unicodedata.is_normalized('NFD', f)})")
                
                # Check path exists
                full_path = os.path.join(p, f)
                print(f"    os.path.exists({full_path}): {os.path.exists(full_path)}")
