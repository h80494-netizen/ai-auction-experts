import re

with open('public/map.html', 'rb') as f:
    content = f.read().decode('utf-8', errors='replace')

subway_colors_fixed = '''        const SUBWAY_COLORS = {
            '1호선': '#0052A4', '2호선': '#00A84D', '3호선': '#EF7C1C', '4호선': '#00A4E3',
            '5호선': '#996CAC', '6호선': '#CD7C2F', '7호선': '#747F00', '8호선': '#E6186C',
            '9호선': '#BDB092', '경의중앙선': '#77C4A3', '수인분당선': '#FABE00', '경춘선': '#0C8E72',
            '신분당선': '#D4003B', '우이신설': '#B0CE18', '경강선': '#003499', 
            '김포골드': '#A17E46', '서해선': '#8FC31F', '공항철도': '#0090D2', '인천2호선': '#ED8B00',
            '인천1호선': '#7CA8D5', '용인에버': '#56C343', '신림선': '#6789CA'
        };'''

content = re.sub(r'const SUBWAY_COLORS = \{.*?};', subway_colors_fixed, content, flags=re.DOTALL)
content = re.sub(r"let popStr = pop > 0 \? \(pop / 10000\)\.toFixed\(0\) \+ '[^;]+;", "let popStr = pop > 0 ? (pop / 10000).toFixed(0) + '만 명' : '데이터 없음';", content)

with open('public/map.html', 'wb') as f:
    f.write(content.encode('utf-8'))

print('Fix completed.')
