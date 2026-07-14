with open('public/map.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re
left_match = re.search(r'<div[^>]*id="left-panel".*?</div>\s*<!--', content, re.DOTALL)
if left_match:
    print("LEFT PANEL MATCH:")
    print(left_match.group(0)[:1000])
else:
    print("LEFT PANEL NOT FOUND BY SIMPLE REGEX")

# Let's find index of id="left-panel" and print 1000 chars
left_idx = content.find('id="left-panel"')
if left_idx != -1:
    print("LEFT PANEL HTML SOURCE:")
    print(content[left_idx-50:left_idx+2000])

right_idx = content.find('id="right-panel"')
if right_idx != -1:
    print("RIGHT PANEL HTML SOURCE:")
    print(content[right_idx-50:right_idx+2000])
