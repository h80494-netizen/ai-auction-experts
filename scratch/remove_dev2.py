import sys

with open('public/map.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

out_lines = []
skip = False
for i, line in enumerate(lines):
    # Remove HTML block
    if '<!-- 개발행위허가제한지역 -->' in line:
        skip = True
        continue
    
    if skip:
        # The block ends after the closing </div>
        # Line 1: <!-- 개발행위허가제한지역 -->
        # Line 2: <div class="toggle-row">
        # Line 3:     <div class="toggle-label">...</div>
        # Line 4:     <label class="switch">...</label>
        # Line 5: </div>
        if '</div>' in line and 'class="switch"' in lines[i-1]:
            skip = False
        continue

    # Remove JS references
    if 'toggle-dev2' in line:
        if 'id: \'toggle-dev2\'' in line:
            continue
        if 'if (!document.getElementById(\'toggle-dev2\').checked) return;' in line:
            continue
        if '\'toggle-dev2\': [layers.dev2],' in line:
            continue
        if 'if (document.getElementById(\'toggle-dev2\')' in line:
            continue

    out_lines.append(line)

with open('public/map.html', 'w', encoding='utf-8') as f:
    f.writelines(out_lines)

print('Success')
