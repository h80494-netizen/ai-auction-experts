import json
import os

path = r"C:\Users\llll\.gemini\antigravity-ide\brain\683d6340-4168-4009-80df-40851f92307f\.system_generated\logs\transcript.jsonl"
print(f"Searching May 31 transcript for modifications related to crosswalk/횡단보도...")

keywords = ["fetchCrosswalks"]

with open(path, 'r', encoding='utf-8', errors='ignore') as f:
    for idx, line in enumerate(f):
        line_no = idx + 1
        
        # Check raw line first
        if not any(kw in line.lower() or kw in line for kw in keywords):
            continue
            
        try:
            data = json.loads(line)
        except Exception:
            continue
            
        tool_calls = data.get('tool_calls', [])
        for tc_idx, tc in enumerate(tool_calls):
            name = tc.get('name')
            if name not in ['replace_file_content', 'multi_replace_file_content', 'write_to_file']:
                continue
                
            args = tc.get('args', {})
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except:
                    pass
            
            target = args.get('TargetFile') or args.get('AbsolutePath') or args.get('Target') or ""
            target_str = str(target).lower()
            
            # Print if target contains app.py or map.html or script.js
            if any(x in target_str for x in ['app.py', 'map.html', 'script.js']):
                print(f"Line {line_no} | Tool: {name} | Target: {target}")
                print("-" * 50)
                if name in ['replace_file_content', 'write_to_file']:
                    replacement = args.get('ReplacementContent') or args.get('CodeContent') or ""
                    target_content = args.get('TargetContent') or ""
                    print("[TARGET CONTENT PREVIEW]")
                    print(target_content[:200] + "...")
                    print("[REPLACEMENT CONTENT PREVIEW]")
                    print(replacement[:600] + "...")
                elif name == 'multi_replace_file_content':
                    chunks = args.get('ReplacementChunks', [])
                    print(f"Multi-replace chunks: {len(chunks)}")
                print("=" * 80)
