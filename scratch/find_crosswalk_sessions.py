import os

brain_dir = r"C:\Users\llll\.gemini\antigravity-ide\brain"
keywords = ["횡단보도", "crosswalk"]

print("Searching for crosswalk sessions...")

results = {}

for root, dirs, files in os.walk(brain_dir):
    for file in files:
        if file == "transcript.jsonl":
            path = os.path.join(root, file)
            session_id = os.path.basename(os.path.dirname(os.path.dirname(root)))
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_idx, line in enumerate(f):
                        for kw in keywords:
                            if kw in line:
                                if session_id not in results:
                                    results[session_id] = []
                                results[session_id].append((line_idx + 1, kw, path))
            except Exception as e:
                pass

print(f"Found crosswalk keywords in {len(results)} sessions:")
for sid, occurrences in results.items():
    print(f"Session ID: {sid} | Total occurrences: {len(occurrences)}")
    # Print first 5 and last 5 occurrences
    if len(occurrences) <= 10:
        for line_no, kw, path in occurrences:
            print(f"  Line {line_no}: {kw} ({os.path.basename(path)})")
    else:
        for line_no, kw, path in occurrences[:5]:
            print(f"  Line {line_no}: {kw} ({os.path.basename(path)})")
        print("  ...")
        for line_no, kw, path in occurrences[-5:]:
            print(f"  Line {line_no}: {kw} ({os.path.basename(path)})")
    print("-" * 50)
