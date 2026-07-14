import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('public/map.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re
matches = [i for i, line in enumerate(content.split('\n')) if '권리분석' in line or 'analysis' in line or '보고서' in line]
print(f"Found {len(matches)} occurrences:")
for m in matches[:20]:
    print(f"  Line {m+1}: {content.split('\n')[m].strip()}")
