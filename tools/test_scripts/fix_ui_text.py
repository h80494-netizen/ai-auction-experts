import re

with open('public/map.html', encoding='utf-8') as f:
    text = f.read()

text = re.sub(r'<p style="margin-top: 15px; color: var\(--primary-blue\); font-weight: bold;">.*?</p>',
              r'<p style="margin-top: 15px; color: var(--primary-blue); font-weight: bold;">지도 데이터를 구성 중입니다...</p>', text)

text = re.sub(r'<i class="fa-solid fa-magnifying-glass-plus"></i>.*?\n',
              r'<i class="fa-solid fa-magnifying-glass-plus"></i> 지도를 동네 수준으로 확대해야 물건이 표시됩니다.\n', text)

text = re.sub(r'title="[^"]*" onclick="window\.location\.href=\'/\'"',
              r'title="메인 대시보드로 돌아가기" onclick="window.location.href=\'/\'"', text)

text = re.sub(r'<i class="fa-solid fa-house"></i>[\s\S]*?</div>',
              r'<i class="fa-solid fa-house"></i> 메인 대시보드\n        </div>', text)

text = re.sub(r'title="[^"]*" id="btn-highlighter"',
              r'title="형광펜 데이터" id="btn-highlighter"', text)

with open('public/map.html', 'w', encoding='utf-8') as f:
    f.write(text)

print('Fixed top ui text')
