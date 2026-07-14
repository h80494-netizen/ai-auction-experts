import json
import os

path = r"C:\Users\llll\.gemini\antigravity-ide\brain\d378d121-3b9b-430c-b5ab-08a7c629d9b8\.system_generated\logs\transcript.jsonl"

line_ranges = [
    (2840, 2930), # crosswalks initiation
    (5390, 5490)  # highlighter AND/OR logic
]

print(f"Extracting lines from {path}...")

for start, end in line_ranges:
    print(f"\n=== Lines {start} to {end} ===")
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        for idx, line in enumerate(f):
            line_no = idx + 1
            if line_no < start:
                continue
            if line_no > end:
                break
                
            try:
                data = json.loads(line)
            except Exception:
                continue
                
            tool_calls = data.get('tool_calls', [])
            if not tool_calls:
                continue
                
            for tc_idx, tc in enumerate(tool_calls):
                name = tc.get('name')
                args = tc.get('args', {})
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except:
                        pass
                
                target = args.get('TargetFile') or args.get('AbsolutePath') or args.get('Target')
                print(f"Line {line_no} | Tool: {name} | Target: {target}")
                
                # Print key contents based on tool type
                if name in ['replace_file_content', 'write_to_file']:
                    replacement = args.get('ReplacementContent') or args.get('CodeContent')
                    target_content = args.get('TargetContent')
                    if target_content:
                        print(f"  TargetContent:\n{target_content[:300]}")
                        if len(target_content) > 300: print("...")
                    if replacement:
                        print(f"  ReplacementContent:\n{replacement[:500]}")
                        if len(replacement) > 500: print("...")
                elif name == 'multi_replace_file_content':
                    chunks = args.get('ReplacementChunks', [])
                    print(f"  MultiReplace with {len(chunks)} chunks:")
                    for c_idx, chunk in enumerate(chunks):
                        print(f"    Chunk {c_idx}: target size {len(chunk.get('TargetContent', ''))}, replacement size {len(chunk.get('ReplacementContent', ''))}")
                        print(f"      Target: {chunk.get('TargetContent', '')[:100]}")
                        print(f"      Replacement: {chunk.get('ReplacementContent', '')[:150]}")
                print("-" * 40)
