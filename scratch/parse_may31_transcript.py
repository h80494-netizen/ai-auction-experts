import json
import os

path = r"C:\Users\llll\.gemini\antigravity-ide\brain\d378d121-3b9b-430c-b5ab-08a7c629d9b8\.system_generated\logs\transcript.jsonl"
out_dir = r"c:\Users\llll\Documents\두인경매\바이브코딩\scratch\extracted_may31"
os.makedirs(out_dir, exist_ok=True)

with open(path, 'r', encoding='utf-8', errors='ignore') as f:
    for idx, line in enumerate(f):
        try:
            data = json.loads(line)
        except Exception:
            continue
        
        tool_calls = data.get('tool_calls', [])
        for tc_idx, tc in enumerate(tool_calls):
            name = tc.get('name')
            if name in ['replace_file_content', 'multi_replace_file_content', 'write_to_file']:
                args = tc.get('args', {})
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except:
                        pass
                
                target = args.get('TargetFile') or args.get('AbsolutePath') or args.get('Target')
                if not target:
                    continue
                
                target_str = str(target).replace('"', '').replace("'", "").strip()
                basename = os.path.basename(target_str)
                
                # Check if it modifies app.py or ai_analyzer.py
                if any(x in basename for x in ['app.py', 'ai_analyzer.py']):
                    out_path = os.path.join(out_dir, f"step_{idx}_call_{tc_idx}_{basename}.txt")
                    with open(out_path, 'w', encoding='utf-8') as out_f:
                        out_f.write(json.dumps(args, indent=2, ensure_ascii=False))
                    print(f"Extracted {name} for {basename} to {out_path}")
