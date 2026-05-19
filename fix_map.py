import re

with open('public/map.html', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

new_grid = '''            <div class="checkbox-grid">
                <label class="checkbox-item"><input type="checkbox" value="토지"> 토지</label>
                <label class="checkbox-item"><input type="checkbox" value="지산"> 지산</label>
                <label class="checkbox-item"><input type="checkbox" value="집합"> 집합</label>
                <label class="checkbox-item"><input type="checkbox" value="일반"> 일반</label>
                <label class="checkbox-item"><input type="checkbox" value="오피스텔"> 오피스텔</label>
                <label class="checkbox-item"><input type="checkbox" value="다세대"> 다세대</label>
                <label class="checkbox-item"><input type="checkbox" value="아파트" checked> 아파트</label>
                <label class="checkbox-item"><input type="checkbox" value="단독"> 단독</label>
                <label class="checkbox-item"><input type="checkbox" value="기타"> 기타</label>
                <label class="checkbox-item"><input type="checkbox" value="공장"> 공장</label>
            </div>'''

content = re.sub(r'<div class="checkbox-grid">.*?</div>', new_grid, content, flags=re.DOTALL)

with open('public/map.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
