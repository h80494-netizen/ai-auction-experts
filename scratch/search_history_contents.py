import json
import os
from urllib.parse import unquote
import time

roaming = os.environ.get('APPDATA')
ide_folders = ['Antigravity', 'Antigravity IDE']

print("Searching IDE history with improved encoding handling...")

found_items = []

for folder_name in ide_folders:
    history_base = os.path.join(roaming, folder_name)
    if not os.path.exists(history_base):
        continue
        
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
        # Try both utf-8 and cp949 decoding for the URL
        resource_decoded = ""
        for enc in ['utf-8', 'cp949', 'euc-kr']:
            try:
                resource_decoded = unquote(resource, encoding=enc)
                if "두인" in resource_decoded or "바이브" in resource_decoded or "map.html" in resource_decoded or "app.py" in resource_decoded:
                    break
            except Exception:
                continue
        if not resource_decoded:
            resource_decoded = unquote(resource) # fallback
            
        entries = data.get("entries", [])
        for entry in entries:
            entry_id = entry.get("id")
            timestamp = entry.get("timestamp", 0) / 1000.0
            
            backup_file = os.path.join(root, entry_id)
            if os.path.exists(backup_file):
                # We try reading as utf-8 or cp949
                content = ""
                for enc in ['utf-8', 'cp949', 'latin-1']:
                    try:
                        with open(backup_file, 'r', encoding=enc) as bf:
                            content = bf.read()
                        break
                    except Exception:
                        continue
                
                if not content:
                    continue
                    
                has_crosswalk = "crosswalk" in content.lower() or "횡단보도" in content
                has_highlighter = "highlighter" in content.lower() or "형광펜" in content or "and/or" in content.lower()
                has_stages = "초기" in content and "중기" in content and "후기" in content
                
                # We also want to match if it's app.py or ai_analyzer.py or map.html regardless of content
                is_target_file = any(x in resource_decoded.lower() for x in ['app.py', 'ai_analyzer.py', 'map.html', 'script.js'])
                
                if has_crosswalk or has_highlighter or has_stages or is_target_file:
                    found_items.append({
                        "folder": folder_name,
                        "resource": resource_decoded,
                        "backup_file": backup_file,
                        "timestamp": timestamp,
                        "has_crosswalk": has_crosswalk,
                        "has_highlighter": has_highlighter,
                        "has_stages": has_stages,
                        "length": len(content)
                    })

# Sort by timestamp desc
found_items.sort(key=lambda x: x['timestamp'], reverse=True)

print(f"\nFound {len(found_items)} history versions matching criteria:\n")
for idx, item in enumerate(found_items[:50]):
    print(f"[{idx}] Time: {time.ctime(item['timestamp'])} | Size: {item['length']} bytes")
    print(f"    Resource: {item['resource']}")
    print(f"    File: {item['backup_file']}")
    print(f"    Flags: Crosswalk={item['has_crosswalk']}, Highlighter={item['has_highlighter']}, Stages={item['has_stages']}")
    print("-" * 60)

