import os

downloads_dir = 'backend/downloads'
for root, dirs, files in os.walk(downloads_dir):
    if '117137' in root:
        print("Root:", repr(root))
        for f in files:
            path = os.path.join(root, f)
            print(f" - {f} ({os.path.getsize(path)} bytes)")
