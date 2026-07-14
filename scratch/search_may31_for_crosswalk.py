import json
import os

path = r"C:\Users\llll\.gemini\antigravity-ide\brain\89144272-d1f9-49f2-a29f-0fadc3cccd44\.system_generated\logs\transcript.jsonl"
print(f"Reading May 31 transcript from {path}...")

if not os.path.exists(path):
    print("Error: May 31 transcript file not found!")
    exit(1)

keywords = ["crosswalk", "횡단보도"]

results = []

with open(path, 'r', encoding='utf-8', errors='ignore') as f:
    for idx, line in enumerate(f):
        # Quick search
        found_kw = [kw for kw in keywords if kw in line.lower() or kw in line]
        if not found_kw:
            continue
            
        try:
            data = json.loads(line)
        except Exception:
            continue
            
        tool_calls = data.get('tool_calls', [])
        for tc_idx, tc in enumerate(tool_calls):
            name = tc.get('name')
            args = tc.get('args', {})
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except:
                    pass
                    
            # Check if any keyword matches the arguments content
            args_str = json.dumps(args, ensure_ascii=False).lower()
            matching_kw = [kw for kw in keywords if kw in args_str or kw in json.dumps(args, ensure_ascii=False)]
            if matching_kw:
                results.append({
                    "step": idx,
                    "tool": name,
                    "keywords": matching_kw,
                    "target": args.get('TargetFile') or args.get('AbsolutePath') or args.get('Target') or args.get('TargetContent', '')[:50]
                })

print(f"Found {len(results)} tool calls containing keywords:")
for r in results:
    print(f"Step {r['step']} | Tool: {r['tool']} | Keywords: {r['keywords']}")
    print(f"    Target: {r['target']}")
    print("-" * 50)
