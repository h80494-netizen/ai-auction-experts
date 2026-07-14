import os
import re

map_html_path = 'public/map.html'
with open(map_html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove toggle UI
content = re.sub(r'\s*<!-- 장기미집행 10년 이상 -->\s*<div class="toggle-row">\s*<div class="toggle-label"><i class="fa-solid fa-map" style="color: #a855f7;"></i> 장기미집행 10년 이상</div>\s*<label class="switch"><input type="checkbox" id="toggle-unexecuted"><span class="slider"></span></label>\s*</div>\s*', '\n', content)
content = re.sub(r'\s*<!-- [^\n]*10[^\n]*-->\s*<div class="toggle-row">\s*<div class="toggle-label"><i class="fa-solid fa-map" style="color: #a855f7;"></i> .*?</div>\s*<label class="switch"><input type="checkbox" id="toggle-unexecuted"><span class="slider"></span></label>\s*</div>\s*', '\n', content)

# 2. Remove cache variables
content = re.sub(r'\s*let cachedUnexecutedData = null;\s*let cachedUnexecutedBounds = null;\s*let cachedUnexecutedZoom = null;\s*', '\n', content)

# 3. Remove layers object unexecuted
content = re.sub(r'\s*unexecuted: L\.layerGroup\(\),', '', content)

# 4. Remove mapping
content = re.sub(r'\s*\{\s*id:\s*\'toggle-unexecuted\'.*?\},', '', content)
content = re.sub(r'\s*\'toggle-unexecuted\':\s*\[layers\.unexecuted\],', '', content)

# 5. Remove fetch function block
content = re.sub(r'\s*async function fetchUnexecutedFacilities\(\) \{[\s\S]*?triggerHighlighter\(\);\s*\}', '', content)

# 6. Remove handlers
content = re.sub(r'\s*if\s*\(\s*document\.getElementById\(\'toggle-unexecuted\'\)\s*&&\s*document\.getElementById\(\'toggle-unexecuted\'\)\.checked\s*\)\s*\{\s*fetchUnexecutedFacilities\(\);\s*\}', '', content)

content = re.sub(r'\s*document\.getElementById\(\'toggle-unexecuted\'\)\.addEventListener\(\'change\', function\(\)\s*\{[\s\S]*?\}\);', '', content)

with open(map_html_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('Cleaned map.html')
