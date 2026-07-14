import os
import shutil

ROOT_DIR = r"c:\Users\llll\Documents\두인경매\바이브코딩"
PROJECT_DIR = os.path.join(ROOT_DIR, "ai_auction_project")

# 1. Create project folder
if not os.path.exists(PROJECT_DIR):
    os.makedirs(PROJECT_DIR)

# 2. Define target folders inside project
DIRS = {
    "tests": os.path.join(PROJECT_DIR, "tests"),
    "scripts_maintenance": os.path.join(PROJECT_DIR, "scripts", "maintenance"),
    "scripts_processing": os.path.join(PROJECT_DIR, "scripts", "processing"),
    "scripts_scraping": os.path.join(PROJECT_DIR, "scripts", "scraping"),
    "logs_and_dumps": os.path.join(PROJECT_DIR, "logs_and_dumps"),
    "data": os.path.join(PROJECT_DIR, "data"),
    "scratch": os.path.join(PROJECT_DIR, "scratch"),
}

for d in DIRS.values():
    if not os.path.exists(d):
        os.makedirs(d)

# 3. Move items
items = os.listdir(ROOT_DIR)
for item in items:
    if item in ["ai_auction_project", ".git", ".gitignore", "CLAUDE.md", "organize_files.py"]:
        continue
    
    src = os.path.join(ROOT_DIR, item)
    is_file = os.path.isfile(src)
    
    target_dir = PROJECT_DIR # default is project root

    if is_file:
        if item.startswith(("test_", "check_")) or item in ["test.html", "test.js", "test.txt", "test_cols.txt"]:
            target_dir = DIRS["tests"]
        elif item.startswith(("fix_", "repair_", "revert_", "replace_", "find_")) or item == "optimize.py":
            target_dir = DIRS["scripts_maintenance"]
        elif item.startswith(("process_", "add_", "update_", "convert_", "load_", "extract_", "inspect_", "generate_", "clip_", "read_")) or item == "create_indexes.py":
            target_dir = DIRS["scripts_processing"]
        elif item.startswith(("download_", "dump_")):
            target_dir = DIRS["scripts_scraping"]
        elif item.startswith("scratch_"):
            target_dir = DIRS["scratch"]
        elif item.endswith((".csv", ".xlsx", ".db", ".shp", ".dbf", ".shx", ".prj", ".cpg", ".qmd")) or item in ["bus_data.txt", "bus_data_utf8.txt", "auction_data.txt", "columns.json", "columns_excel.json", "columns_utf8.txt", "parsed_data.json", "distinct_type_counts.txt", "distinct_types.txt", "public_inputs.json", "temp_cols.json"]:
            target_dir = DIRS["data"]
        elif item.endswith("_dump.html") or item.endswith("_result.html") or item.startswith("error_") or item == "server.log" or item.endswith(".png"):
            target_dir = DIRS["logs_and_dumps"]
            
    # Move the item
    dst = os.path.join(target_dir, item)
    try:
        shutil.move(src, dst)
        print(f"Moved {item} to {target_dir}")
    except Exception as e:
        print(f"Failed to move {item}: {e}")

print("File organization completed.")
