import json
import os
import shutil
import time
from urllib.parse import unquote

roaming = os.environ.get('APPDATA')
ide_folders = ['Antigravity', 'Antigravity IDE']

workspace_dir = r"c:\Users\llll\Documents\두인경매\바이브코딩"

restored_files = []

for folder_name in ide_folders:
    history_base = os.path.join(roaming, folder_name)
    if not os.path.exists(history_base):
        continue
    # Recursively find all entries.json files under this folder
    for root, dirs, files in os.walk(history_base):
        if 'entries.json' not in files:
            continue
            
        entries_file = os.path.join(root, "entries.json")
        try:
            with open(entries_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            continue
            
        resource = data.get("resource", "")
        # Decode the resource first
        resource_decoded = unquote(resource)
        
        # Check if the resource belongs to our workspace
        if "두인경매" in resource_decoded and "바이브코딩" in resource_decoded:
            clean_path = resource_decoded.replace("file:///", "").replace("/", "\\")
            
            # Sort entries by timestamp desc to get the latest backup
            entries = data.get("entries", [])
            if not entries:
                continue
                
            entries.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
            
            # Get the latest entry
            latest_entry = entries[0]
            entry_id = latest_entry.get("id")
            entry_ts = latest_entry.get("timestamp", 0) / 1000.0 # convert to seconds
            
            backup_file = os.path.join(root, entry_id)
            if os.path.exists(backup_file):
                print(f"Found history in {folder_name} for {os.path.basename(clean_path)}:")
                print(f"  Resource: {clean_path}")
                print(f"  Latest Backup ID: {entry_id}, Date: {time.ctime(entry_ts)}")
                
                dest_path = clean_path
                
                # Make backup copy of original before restoring, just in case
                if os.path.exists(dest_path):
                    shutil.copy2(dest_path, dest_path + ".before_history_restore")
                    
                shutil.copy2(backup_file, dest_path)
                print(f"  -> Restored to {dest_path}")
                restored_files.append(dest_path)

print(f"\nRestored {len(restored_files)} files successfully from Antigravity History!")
