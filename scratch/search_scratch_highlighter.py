with open('public/map.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'btn-highlighter' in line or 'triggerHighlighter' in line or 'highlight-count' in line or 'highlightedCaseNos' in line:
        print(f"Line {idx+1}: {line.strip()}")
