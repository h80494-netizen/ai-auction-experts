import os
import json

brain_dir = r"C:\Users\llll\.gemini\antigravity-ide\brain"
keywords = ["highlighter-mode", "highlighterMode", "AndOr", "And/Or", "횡단보도", "crosswalk"]

for root, dirs, files in os.walk(brain_dir):
    for file in files:
        if file == "transcript.jsonl":
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_idx, line in enumerate(f):
                        for kw in keywords:
                            if kw in line:
                                print(f"Found keyword '{kw}' in {path} at line {line_idx+1}")
            except Exception as e:
                pass
