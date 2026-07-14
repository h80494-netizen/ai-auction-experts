import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_path = "c:/Users/llll/Documents/두인경매/바이브코딩/public/issues.html"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Try to replace the label
new_content = content.replace('<i class="fa-solid fa-trowel-bricks"></i> 재개발</button>', '<i class="fa-solid fa-trowel-bricks"></i> 재개발재건축</button>')
# If it's something like " 재개발 "
new_content = new_content.replace('</i> 재개발\n', '</i> 재개발재건축\n')

# Actually, let's just do a targeted replace for the button line
lines = new_content.split('\n')
for i, line in enumerate(lines):
    if '<button class="tab-btn" data-category="재개발"' in line:
        if i+1 < len(lines) and '재개발' in lines[i+1] and '재건축' not in lines[i+1]:
            lines[i+1] = lines[i+1].replace('재개발', '재개발재건축')

new_content = '\n'.join(lines)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(new_content)

print("Updated issues.html to display '재개발재건축'.")
