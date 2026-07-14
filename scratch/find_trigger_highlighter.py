with open('public/map.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'triggerHighlighter' in line or 'applyHighlighter' in line:
        print(f"{idx+1}: {line.strip()}")
