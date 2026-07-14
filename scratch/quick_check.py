import json

path = r"C:\Users\llll\.gemini\antigravity-ide\brain\66584ca7-1547-4893-92a1-419574cb4123\.system_generated\logs\transcript.jsonl"
with open(path, 'r', encoding='utf-8', errors='ignore') as f:
    for idx, line in enumerate(f):
        line_no = idx + 1
        if 80 <= line_no <= 85:
            try:
                data = json.loads(line)
                tool_calls = data.get('tool_calls', [])
                for tc in tool_calls:
                    name = tc.get('name')
                    args = tc.get('args', {})
                    if isinstance(args, str):
                        try: args = json.loads(args)
                        except: pass
                    replacement = args.get('ReplacementContent') or args.get('CodeContent') or ""
                    print(f"--- Line {line_no} ---")
                    print(replacement)
                    print("="*60)
            except Exception as e:
                print(f"Error: {e}")
