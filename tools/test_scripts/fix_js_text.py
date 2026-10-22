import re

with open('public/map.html', encoding='utf-8') as f:
    text = f.read()

# Fix JS corrupted strings
replacements = {
    "<b>${name}</b><br>?곴텒<br>?좊룞?멸뎄: ${popStr}": "<b>${name}</b><br>상권<br>유동인구: ${popStr}",
    "<b>${line.line} 湲곗젏</b>": "<b>${line.line} 기점</b>",
    "<b>${line.line} 醫낆젏</b>": "<b>${line.line} 종점</b>",
    "?숈썝 諛€吏묎?": "학원 밀집가",
    "諛섍꼍 200m ??${poly.count}媛??숈썝 諛€吏?": "반경 200m 내 ${poly.count}개 학원 밀집",
    "?고븳 珥덈줉??": "연한 초록색",
    "吏€援щ떒?꾧퀎?띻뎄??/b>": "지구단위계획구역</b>"
}

for k, v in replacements.items():
    text = text.replace(k, v)

with open('public/map.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Replaced JS strings")
