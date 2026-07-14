import os

diff_paths = ['scratch/git_diff_clean.txt', 'scratch/git_diff_all.txt']

for p in diff_paths:
    if os.path.exists(p):
        print(f"Searching in {p}...")
        with open(p, 'r', encoding='utf-8', errors='ignore') as f:
            for idx, line in enumerate(f):
                if 'btn-highlighter' in line or 'highlighter-mode' in line or '형광펜' in line or 'btn-and' in line:
                    if 'icon-btn' in line or 'button' in line or 'click' in line or 'AND' in line or 'OR' in line:
                        print(f"  Line {idx+1}: {line.strip()}")
