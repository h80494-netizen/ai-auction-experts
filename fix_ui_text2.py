import re

with open('public/map.html', encoding='utf-8') as f:
    text = f.read()

# Left panel texts
text = re.sub(r'<div class="layer-group-title">[^<]*?인프라[^<]*?</div>', '<div class="layer-group-title">기본 인프라</div>', text)
text = re.sub(r'<div class="toggle-label"><i class="fa-solid fa-train-subway"[^>]*></i>[^<]*?</div>', '<div class="toggle-label"><i class="fa-solid fa-train-subway" style="color: #10b981;"></i> 지하철역</div>', text)
text = re.sub(r'([^>]*?)<input type="number" id="buffer-subways"', r'버퍼: <input type="number" id="buffer-subways"', text)

text = re.sub(r'<div class="toggle-label">\s*<div>\s*<i class="fa-solid fa-bus"[^>]*></i>[^<]*?<span class="toggle-desc">[^<]*?</span>', 
              r'<div class="toggle-label">\n                    <div>\n                        <i class="fa-solid fa-bus" style="color: #0ea5e9;"></i> 버스정류장\n                        <span class="toggle-desc">화면 이동 시 자동 로딩</span>', text)

text = re.sub(r'<div class="toggle-label"><i class="fa-solid fa-industry"[^>]*></i>[^<]*?</div>', '<div class="toggle-label"><i class="fa-solid fa-industry" style="color: #f59e0b;"></i> 산업단지</div>', text)
text = re.sub(r'([^>]*?)<input type="number" id="buffer-inds"', r'버퍼: <input type="number" id="buffer-inds"', text)

text = re.sub(r'<div class="toggle-label">\s*<div>\s*<i class="fa-solid fa-store"[^>]*></i>[^<]*?<span class="toggle-desc">[^<]*?</span>', 
              r'<div class="toggle-label">\n                    <div>\n                        <i class="fa-solid fa-store" style="color: #8b5cf6;"></i> 서울 상권\n                        <span class="toggle-desc">화면 이동 시 자동 로딩</span>', text)

text = re.sub(r'<div class="layer-group-title"[^>]*>.*?(?=<div class="toggle-row"|$)', '<div class="layer-group-title" style="margin-top: 15px;">교육 및 학군</div>\n            ', text, count=1) # Replace 援먯쑁 諛??숆뎔

text = re.sub(r'<div class="toggle-label">\s*<div>\s*<i class="fa-solid fa-school"[^>]*></i>[^<]*?<span class="toggle-desc">[^<]*?</span>',
              r'<div class="toggle-label">\n                        <div>\n                            <i class="fa-solid fa-school" style="color: #f43f5e;"></i> 중학교\n                            <span class="toggle-desc">특목고 10%대 배정구역 표시</span>', text)
text = re.sub(r'([^>]*?)<input type="number" id="buffer-middles"', r'버퍼: <input type="number" id="buffer-middles"', text)

text = re.sub(r'<div class="toggle-label"><i class="fa-solid fa-graduation-cap"[^>]*></i>[^<]*?</div>', '<div class="toggle-label"><i class="fa-solid fa-graduation-cap" style="color: #3b82f6;"></i> 대학교</div>', text)
text = re.sub(r'([^>]*?)<input type="number" id="buffer-univs"', r'버퍼: <input type="number" id="buffer-univs"', text)

text = re.sub(r'<div class="toggle-label">\s*<div>\s*<i class="fa-solid fa-building-columns"[^>]*></i>[^<]*?<span class="toggle-desc"[^>]*>[^<]*?</span>',
              r'<div class="toggle-label">\n                    <div>\n                        <i class="fa-solid fa-building-columns" style="color: var(--color-hagwon);"></i> 학원가 폴리곤\n                        <span class="toggle-desc" style="color: #7e22ce;">학원 밀집 구역 시각화 (보라색 히트맵)</span>', text)

text = re.sub(r'<div class="toggle-label">\s*<div>\s*<i class="fa-solid fa-fire"[^>]*></i>[^<]*?<span class="toggle-desc"[^>]*>[^<]*?</span>',
              r'<div class="toggle-label">\n                    <div>\n                        <i class="fa-solid fa-fire" style="color: #e11d48;"></i> 유동인구 히트맵 (250m)\n                        <span class="toggle-desc" style="color: #be123c;">서울의 생활인구 변화를 시각화</span>', text)

text = re.sub(r'<div class="toggle-label">\s*<div>\s*<i class="fa-solid fa-building-circle-exclamation"[^>]*></i>[^<]*?<span class="toggle-desc"[^>]*>[^<]*?</span>',
              r'<div class="toggle-label">\n                    <div>\n                        <i class="fa-solid fa-building-circle-exclamation" style="color: #ea580c;"></i> 노후화 집중 구역\n                        <span class="toggle-desc" style="color: #c2410c;">500가구 60% 이상 또는 1000가구 이상 밀집 격자</span>', text)

# Replace 媛쒕컻援ъ뿭 (以€鍮꾩쨷)
text = re.sub(r'<div class="layer-group-title"[^>]*>[^<]*?\(以€鍮꾩쨷\)</div>', '<div class="layer-group-title" style="margin-top: 15px;">개발구역 (준비중)</div>', text)

text = re.sub(r'<div class="toggle-label"><i class="fa-solid fa-map"[^>]*></i>[^<]*?</div>\s*<label class="switch"><input type="checkbox" id="toggle-dev1"', 
              r'<div class="toggle-label"><i class="fa-solid fa-map" style="color: #64748b;"></i> 택지지구</div>\n                <label class="switch"><input type="checkbox" id="toggle-dev1"', text)
text = re.sub(r'<div class="toggle-label"><i class="fa-solid fa-map"[^>]*></i>[^<]*?</div>\s*<label class="switch"><input type="checkbox" id="toggle-dev2"', 
              r'<div class="toggle-label"><i class="fa-solid fa-map" style="color: #64748b;"></i> 지구단위계획구역</div>\n                <label class="switch"><input type="checkbox" id="toggle-dev2"', text)
text = re.sub(r'<div class="toggle-label"><i class="fa-solid fa-map"[^>]*></i>[^<]*?</div>\s*<label class="switch"><input type="checkbox" id="toggle-dev3"', 
              r'<div class="toggle-label"><i class="fa-solid fa-map" style="color: #64748b;"></i> 재개발/재건축구역</div>\n                <label class="switch"><input type="checkbox" id="toggle-dev3"', text)

# Right Panel Texts
text = re.sub(r'<div class="layer-group-title">[^<]*?좏깮</div>', '<div class="layer-group-title">부동산 종류 다중 선택</div>', text)

text = re.sub(r'<label class="checkbox-item"><input type="checkbox" value="[^"]*" checked>[^<]*?</label>', r'<label class="checkbox-item"><input type="checkbox" value="아파트" checked> 아파트</label>', text, count=1)
text = re.sub(r'<label class="checkbox-item"><input type="checkbox" value="\?[^\"]*,\?[^\"]*">[^<]*?</label>', r'<label class="checkbox-item"><input type="checkbox" value="다세대,빌라"> 다세대/빌라</label>', text, count=1)
text = re.sub(r'<label class="checkbox-item"><input type="checkbox" value="\?[^\"]*">[^<]*?</label>', r'<label class="checkbox-item"><input type="checkbox" value="오피스텔"> 오피스텔</label>', text, count=1)
text = re.sub(r'<label class="checkbox-item"><input type="checkbox" value="\?[^\"]*,\?[^\"]*">[^<]*?</label>', r'<label class="checkbox-item"><input type="checkbox" value="상가,근린"> 상가/점포</label>', text, count=1)
text = re.sub(r'<label class="checkbox-item"><input type="checkbox" value="\?[^\"]*,\?[^\"]*,\?[^\"]*">[^<]*?</label>', r'<label class="checkbox-item"><input type="checkbox" value="토지,대지,임야"> 토지</label>', text, count=1)
text = re.sub(r'<label class="checkbox-item"><input type="checkbox" value="[^\"]*">[^<]*?</label>', r'<label class="checkbox-item"><input type="checkbox" value="공장"> 공장</label>', text, count=1)

text = re.sub(r'<div class="layer-group-title"[^>]*>.*?필터.*?</div>', '<div class="layer-group-title" style="margin-top: 15px;">최저가율 필터 (감정가 대비)</div>', text)
text = re.sub(r'<div class="layer-group-title"[^>]*>[^<]*?\(.*?</div>', '<div class="layer-group-title" style="margin-top: 15px;">전용면적 (평)</div>', text)
text = re.sub(r'<input type="number" id="min-area" placeholder="[^"]*"', r'<input type="number" id="min-area" placeholder="최소"', text)
text = re.sub(r'<input type="number" id="max-area" placeholder="[^"]*"', r'<input type="number" id="max-area" placeholder="최대"', text)

text = re.sub(r'<div class="layer-group-title"[^>]*>.*?議곌굔</div>', '<div class="layer-group-title" style="margin-top: 15px;">추가 조건</div>', text)
text = re.sub(r'<input type="checkbox" id="req-elite-school">[^<]*?\n', r'<input type="checkbox" id="req-elite-school"> 명문학군 포함 (주택 전체)\n', text)
text = re.sub(r'<span>[^<]*?</span>\n\s*<input type="number" id="min-households"', r'<span>세대수</span>\n                    <input type="number" id="min-households"', text)
text = re.sub(r'<span style="color: var\(--text-muted\);">[^<]*?</span>\n\s*</div>', r'<span style="color: var(--text-muted);">(아파트 전용)</span>\n                </div>', text)

text = re.sub(r'<i class="fa-solid fa-download"></i>[^<]*?</button>', r'<i class="fa-solid fa-download"></i> 조건에 맞는 데이터 가져오기\n                </button>', text)

text = re.sub(r'<div style="font-size: 0\.75rem; color: var\(--text-muted\); text-align: center; margin-top: 10px;">\n\s*[^<]*?\n\s*</div>', r'<div style="font-size: 0.75rem; color: var(--text-muted); text-align: center; margin-top: 10px;">\n                현재 화면(BBox) 기준으로 데이터를 불러옵니다.\n            </div>', text)

with open('public/map.html', 'w', encoding='utf-8') as f:
    f.write(text)

print('Fixed UI texts 2')
