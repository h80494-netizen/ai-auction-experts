import os

downloads_dir = 'backend/downloads'
if os.path.exists(downloads_dir):
    print("Files in downloads:")
    for root, dirs, files in os.walk(downloads_dir):
        for f in files:
            path = os.path.join(root, f)
            print(f" - {path} ({os.path.getsize(path)} bytes)")
else:
    print("downloads folder does not exist.")
