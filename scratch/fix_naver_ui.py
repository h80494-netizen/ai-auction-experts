import re

map_path = r'public\map.html'
with open(map_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update JS Payload size calculation
# area_pyeong: size ? (size / 3.3058).toFixed(2) : 25,
content = re.sub(r'area_pyeong:\s*size\s*\?\s*\(size\s*/\s*3\.3058\)\.toFixed\(2\)\s*:\s*25,', 'area_pyeong: size ? size : 25,', content)

# 2. Update Table Header
# <th style="padding:10px; text-align:right;">평당가(원)</th>
content = content.replace('<th style="padding:10px; text-align:right;">평당가(원)</th>', '<th style="padding:10px; text-align:right;">매물호가(억원)</th>')

# 3. Update Left List row value format
# <td style="padding:12px 10px; text-align:right; font-weight:500;">${Math.round(p.price).toLocaleString()}</td>
content = re.sub(r'<td style="padding:12px 10px; text-align:right; font-weight:500;">\$\{Math\.round\(p\.price\)\.toLocaleString\(\)\}</td>', '<td style="padding:12px 10px; text-align:right; font-weight:500;">${(p.price).toFixed(2)}</td>', content)

# 4. Update Right Stats rows
content = content.replace('<th>평당 제비용</th>', '<th>총 제비용</th>')
content = content.replace('expense_per_pyeong', 'total_expense')
content = content.replace('원/평', '억원')
content = content.replace('원</td>', '억원</td>')

# Since the values in backend are already in '억원' (e.g. 10.5), we shouldn't use Math.round(...).toLocaleString(). We should use .toFixed(2).
# e.g. ${Math.round(data.target_indicators.ind_a).toLocaleString()} 원/평
content = re.sub(r'\$\{Math\.round\(data\.target_indicators\.ind_a\)\.toLocaleString\(\)\}\s*억원', '${(data.target_indicators.ind_a).toFixed(2)} 억원', content)
content = re.sub(r'\$\{Math\.round\(data\.target_indicators\.ind_b\)\.toLocaleString\(\)\}\s*억원', '${(data.target_indicators.ind_b).toFixed(2)} 억원', content)

content = re.sub(r'\$\{Math\.round\(data\.market_prices\.avg_per_pyeong\)\.toLocaleString\(\)\}\s*억원', '${(data.market_prices.avg_per_pyeong || 0).toFixed(2)} 억원', content)
content = re.sub(r'\$\{Math\.round\(data\.market_prices\.median_per_pyeong\)\.toLocaleString\(\)\}\s*억원', '${(data.market_prices.median_per_pyeong || 0).toFixed(2)} 억원', content)
content = re.sub(r'\$\{Math\.round\(data\.market_prices\.avg_90\)\.toLocaleString\(\)\}\s*억원', '${(data.market_prices.avg_90 || 0).toFixed(2)} 억원', content)
content = re.sub(r'\$\{Math\.round\(data\.market_prices\.median_90\)\.toLocaleString\(\)\}\s*억원', '${(data.market_prices.median_90 || 0).toFixed(2)} 억원', content)
content = re.sub(r'\$\{Math\.round\(data\.market_prices\.min_per_pyeong\)\.toLocaleString\(\)\}\s*억원', '${(data.market_prices.min_per_pyeong || 0).toFixed(2)} 억원', content)

# also replace total_expense display
# ${data.target_indicators.total_expense.toLocaleString()} 원 -> ${(data.target_indicators.total_expense / 100000000).toFixed(2)} 억원
content = re.sub(r'\$\{data\.target_indicators\.total_expense\.toLocaleString\(\)\}\s*억원', '${(data.target_indicators.total_expense / 100000000).toFixed(2)} 억원', content)

with open(map_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated map.html")
