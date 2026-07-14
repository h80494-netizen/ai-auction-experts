import re

path = 'public/map.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

pattern = r'<button onclick=\"window\.innerWidth.*?권리분석 리포트 가기</button>[\s\S]*?수요/환경분석</button>'

replacement = '''<button onclick="window.innerWidth <= 768 ? window.location.href='/?case=${d.case_no}' : (window.opener ? (window.opener.location.href='/?case=${d.case_no}', window.opener.focus()) : window.open('/?case=${d.case_no}', '_blank'))" style="width:100%; background:#0ea5e9; color:white; border:none; padding:10px; border-radius:6px; cursor:pointer; font-size:0.95rem; font-weight:bold; touch-action:manipulation; margin-bottom: 8px;"><i class="fa-solid fa-circle-info"></i> 기본정보 보기</button>
                            <button onclick="window.innerWidth <= 768 ? window.location.href='/?case=${d.case_no}' : (window.opener ? (window.opener.location.href='/?case=${d.case_no}', window.opener.focus()) : window.open('/?case=${d.case_no}', '_blank'))" style="width:100%; background:var(--primary-blue); color:white; border:none; padding:10px; border-radius:6px; cursor:pointer; font-size:0.95rem; font-weight:bold; touch-action:manipulation;"><i class="fa-solid fa-scale-balanced"></i> 권리분석 리포트</button>
                            <button onclick="openDemandPanel(${d.lat}, ${d.lng}, '${d.case_no}', '${escapedAddress}', '${d.property_type}', ${d.area_size || 0}); map.closePopup();" style="width:100%; background:#8b5cf6; color:white; border:none; padding:10px; border-radius:6px; cursor:pointer; font-size:0.95rem; font-weight:bold; margin-top: 8px; touch-action:manipulation;"><i class="fa-solid fa-store"></i> 상권/수요분석</button>'''

if re.search(pattern, content):
    content = re.sub(pattern, replacement, content)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Popup successfully updated!")
else:
    print("Target pattern not found")
