with open('public/map.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re
# Find all divs with id containing report, modal, popup, panel, or analysis
divs = re.findall(r'<div[^>]*id="([^"]+)"', content)
print("Div IDs found in map.html:")
for d in divs:
    if any(k in d.lower() for k in ['report', 'modal', 'popup', 'panel', 'analysis', 'overlap']):
        print(" -", d)
