import re

with open('public/map.html', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# Fix the specific broken line
fixed_content = re.sub(
    r'<div class="top-brand" style="cursor:pointer;" onclick="window\.location\.href=\'/\'" title="[^>]*>',
    r'<div class="top-brand" style="cursor:pointer;" onclick="window.location.href=\'/\'" title="메인 대시보드로 돌아가기">',
    content
)

with open('public/map.html', 'w', encoding='utf-8') as f:
    f.write(fixed_content)
print("Fixed map.html")
