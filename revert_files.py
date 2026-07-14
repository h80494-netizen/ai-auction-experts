import os
import shutil

ROOT_DIR = r"c:\Users\llll\Documents\두인경매\바이브코딩"
LOG_FILE = r"C:\Users\llll\.gemini\antigravity-ide\brain\7d983551-5cad-4a30-9fe4-06f428777699\.system_generated\tasks\task-24.log"

print("Starting revert process...")

if not os.path.exists(LOG_FILE):
    print("Log file not found.")
else:
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    for line in lines:
        if line.startswith("Moved "):
            # Example: Moved revert_index.py to c:\Users\llll\Documents\두인경매\바이브코딩\ai_auction_project\scripts\maintenance
            parts = line.strip().split(" to ")
            if len(parts) == 2:
                item_name = parts[0].replace("Moved ", "").strip()
                dst_dir = parts[1].strip()
                
                # Because of encoding issues in the log (e.g. 'ΰ' instead of '두인경매'),
                # we just use the ROOT_DIR and the item_name directly, because we know where it currently is.
                # Actually, the destination directory might have the garbled path. Let's fix it by replacing the bad root with the correct one.
                # Wait, the item could have been moved INTO a directory.
                # If item_name was a folder like "data", its current location is ai_auction_project/data/data
                # If item_name was a file like "revert_index.py", its current location is ai_auction_project/scripts/maintenance/revert_index.py
                pass

# Simpler approach: 
# We know ALL items originally came from ROOT_DIR.
# So we just move every file that is in the new subdirectories back to ROOT_DIR.
# For the folders that were moved entirely (like 'backend', 'data'), we move them back.

PROJECT_DIR = os.path.join(ROOT_DIR, "ai_auction_project")

# Items that we know are original directories moved into PROJECT_DIR:
# "backend", "cache", "downloads", "public", "realprice", "temp_shp", "test_images", "에이전트경매"
# AND "data", "scratch" which are now at PROJECT_DIR/data/data and PROJECT_DIR/scratch/scratch

# 1. Move back the pure original directories
orig_dirs = ["backend", "cache", "downloads", "public", "realprice", "temp_shp", "test_images", "에이전트경매"]
for d in orig_dirs:
    src = os.path.join(PROJECT_DIR, d)
    dst = os.path.join(ROOT_DIR, d)
    if os.path.exists(src):
        shutil.move(src, dst)
        print(f"Restored directory: {d}")

# 2. Move back 'data' and 'scratch' original directories
for special_dir in ["data", "scratch"]:
    src = os.path.join(PROJECT_DIR, special_dir, special_dir)
    dst = os.path.join(ROOT_DIR, special_dir)
    if os.path.exists(src):
        shutil.move(src, dst)
        print(f"Restored directory: {special_dir}")

# 3. Now move back all files that are inside PROJECT_DIR (and its subdirectories)
for root, dirs, files in os.walk(PROJECT_DIR):
    for file in files:
        src = os.path.join(root, file)
        dst = os.path.join(ROOT_DIR, file)
        if os.path.exists(src) and not os.path.exists(dst):
            shutil.move(src, dst)
            print(f"Restored file: {file}")

# 4. Remove the PROJECT_DIR and its subdirectories (they should be empty now)
for root, dirs, files in os.walk(PROJECT_DIR, topdown=False):
    for name in dirs:
        try:
            os.rmdir(os.path.join(root, name))
        except:
            pass
try:
    os.rmdir(PROJECT_DIR)
except:
    pass

print("Revert completed.")
