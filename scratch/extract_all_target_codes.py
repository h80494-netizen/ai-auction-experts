import json
import os

path = r"C:\Users\llll\.gemini\antigravity-ide\brain\d378d121-3b9b-430c-b5ab-08a7c629d9b8\.system_generated\logs\transcript.jsonl"
out_file = r"c:\Users\llll\Documents\두인경매\바이브코딩\scratch\extracted_changes.txt"

print(f"Reading from {path}...")
results = []

keywords = ["crosswalk", "횡단보도", "highlighter", "형광펜", "and/or", "andor"]

with open(path, 'r', encoding='utf-8', errors='ignore') as f:
    for idx, line in enumerate(f):
        line_no = idx + 1
        
        # Check keywords in raw line first for speed
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
            if not any(x in target.lower() for x in ['map.html', 'app.py', 'ai_analyzer.py', 'script.js']):
                continue
                
            results.append({
                "line_no": line_no,
                "tool": name,
                "target": target,
                "args": args
            })

print(f"Found {len(results)} relevant code modifications.")

with open(out_file, 'w', encoding='utf-8') as out:
    for r in results:
        out.write("=" * 80 + "\n")
        out.write(f"Line: {r['line_no']} | Tool: {r['tool']} | Target: {r['target']}\n")
        out.write("=" * 80 + "\n")
        
        args = r['args']
        if r['tool'] in ['replace_file_content', 'write_to_file']:
            target_content = args.get('TargetContent')
            replacement = args.get('ReplacementContent') or args.get('CodeContent')
            start = args.get('StartLine')
            end = args.get('EndLine')
            
            out.write(f"Lines: {start} to {end}\n")
            if target_content:
                out.write("[TARGET CONTENT]\n")
                out.write(target_content + "\n")
            if replacement:
                out.write("[REPLACEMENT CONTENT]\n")
                out.write(replacement + "\n")
        elif r['tool'] == 'multi_replace_file_content':
            chunks = args.get('ReplacementChunks', [])
            if isinstance(chunks, str):
                try:
                    chunks = json.loads(chunks)
                except:
                    pass
            out.write(f"Multi-replace chunks: {len(chunks)}\n")
            for c_idx, chunk in enumerate(chunks):
                if isinstance(chunk, str):
                    try:
                        chunk = json.loads(chunk)
                    except:
                        pass
                if not isinstance(chunk, dict):
                    out.write(f"--- Chunk {c_idx} (Non-dict format) ---\n")
                    out.write(str(chunk) + "\n")
                    continue
                out.write(f"--- Chunk {c_idx} (Lines: {chunk.get('StartLine')} to {chunk.get('EndLine')}) ---\n")
                out.write("[TARGET CONTENT]\n")
                out.write(chunk.get('TargetContent', '') + "\n")
                out.write("[REPLACEMENT CONTENT]\n")
                out.write(chunk.get('ReplacementContent', '') + "\n")
        out.write("\n\n")

print(f"Written all extracted modifications to {out_file}")
