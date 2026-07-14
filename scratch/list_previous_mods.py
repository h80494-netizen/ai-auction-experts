import json
import os

path = r"C:\Users\llll\.gemini\antigravity-ide\brain\89144272-d1f9-49f2-a29f-0fadc3cccd44\.system_generated\logs\transcript.jsonl"
if not os.path.exists(path):
    print("Log file not found at", path)
    exit(1)

with open(path, 'r', encoding='utf-8', errors='ignore') as f:
    for line in f:
        try:
            data = json.loads(line)
        except Exception:
            continue
        
        tool_calls = data.get('tool_calls', [])
        if not tool_calls:
            continue
            
        for tc in tool_calls:
            name = tc.get('name')
            if name in ['replace_file_content', 'multi_replace_file_content', 'write_to_file']:
                args = tc.get('args', {})
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except:
                        pass
                target = args.get('TargetFile') or args.get('AbsolutePath') or args.get('Target')
                print(f"Tool: {name}, File: {target}")
