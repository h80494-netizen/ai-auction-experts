import re
import os

# 1. FIX map.html (Clean up the template completely to avoid 억억원)
map_path = r'public\map.html'
with open(map_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Let's replace the ENTIRE script for openNaverPriceModal to be safe and clean.
# I will find the script block and replace it.
script_pattern = re.compile(r'<script>\s*async function openNaverPriceModal.*?<\/script>', re.DOTALL)

new_script = """<script>
async function openNaverPriceModal(caseNo, lat, lng, type, size) {
    document.getElementById('naverPriceModal').style.display = 'flex';
    document.getElementById('naverPriceLoading').style.display = 'block';
    document.getElementById('naverPriceResult').style.display = 'none';
    document.getElementById('naverPriceError').style.display = 'none';

    const payload = {
        lat: lat || 37.5665,
        lon: lng || 126.9780,
        type: type || "아파트",
        area_pyeong: size ? size : 25,
        floor: "5층",
        total_floor: "15층",
        build_year: "2010",
        appraised_price: 500000000,
        min_price: 400000000,
        senior_debt: 0
    };
    
    if(window.auctions && window.auctions.length > 0) {
        const ac = window.auctions.find(a => a.case_no === caseNo);
        if(ac) {
            payload.appraised_price = ac.appraisal_price || payload.appraised_price;
            payload.min_price = ac.minimum_price || payload.min_price;
            if(ac.pyeong) payload.area_pyeong = ac.pyeong;
            if(ac.floor) payload.floor = String(ac.floor);
        }
    }

    try {
        const response = await fetch('/api/naver_price_analysis', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const res = await response.json();
        
        document.getElementById('naverPriceLoading').style.display = 'none';
        if (res.status === 'success') {
            const data = res.data;
            document.getElementById('naverPriceResult').style.display = 'flex';
            
            let html = `
                <tr style="border-bottom:1px solid #eee;"><th style="padding:12px 8px; width:45%; color:#475569;">분석 대상</th><td style="font-weight:bold;">${type} / ${data.target_categories.floor} / ${data.target_categories.area} / ${data.target_categories.age}</td></tr>
                <tr style="border-bottom:1px solid #eee;"><th style="padding:12px 8px; color:#475569;">탐색 반경</th><td style="color:#0284c7; font-weight:bold;">${data.radius_used}m <span style="font-size:0.9em; color:#64748b;">(매칭: ${data.matched_count}건)</span></td></tr>
                <tr style="border-bottom:1px solid #eee;"><th style="padding:12px 8px; color:#475569;">총 제비용</th><td>${(data.target_indicators.total_expense / 100000000).toFixed(2)} 억원</td></tr>
                <tr style="border-bottom:1px solid #eee; background:#f8fafc;"><th style="padding:12px 8px; color:#475569;">지표 A (최저가+비용)</th><td style="font-weight:bold; color:#0f172a;">${(data.target_indicators.ind_a || 0).toFixed(2)} 억원</td></tr>
                <tr style="border-bottom:1px solid #eee; background:#f8fafc;"><th style="padding:12px 8px; color:#475569;">지표 B (적정가+비용)</th><td style="font-weight:bold; color:#0f172a;">${(data.target_indicators.ind_b || 0).toFixed(2)} 억원</td></tr>
                
                <tr style="border-bottom:1px solid #eee;"><th style="padding:12px 8px; color:#475569;">사례 평균가</th><td>${(data.market_prices.avg_price || 0).toFixed(2)} 억원</td></tr>
                <tr style="border-bottom:1px solid #eee;"><th style="padding:12px 8px; color:#475569;">사례 중간값</th><td>${(data.market_prices.median_price || 0).toFixed(2)} 억원</td></tr>
                <tr style="border-bottom:1px solid #eee;"><th style="padding:12px 8px; color:#475569;">평균 90% 수준</th><td style="color:#16a34a; font-weight:bold;">${(data.market_prices.avg_90 || 0).toFixed(2)} 억원</td></tr>
                <tr style="border-bottom:1px solid #eee;"><th style="padding:12px 8px; color:#475569;">중간 90% 수준</th><td style="color:#16a34a; font-weight:bold;">${(data.market_prices.median_90 || 0).toFixed(2)} 억원</td></tr>
                <tr style="border-bottom:1px solid #eee;"><th style="padding:12px 8px; color:#475569;">사례 최저가</th><td style="color:#dc2626; font-weight:bold;">${(data.market_prices.min_price || 0).toFixed(2)} 억원</td></tr>
                
                <tr style="border-bottom:1px solid #eee;"><th style="padding:12px 8px; color:#475569;">괴리율 (지표A vs 평균)</th><td><span style="padding:4px 8px; border-radius:12px; background:${(data.disparities.ind_a_vs_avg || 0) > 0 ? '#dcfce7' : '#fee2e2'}; color:${(data.disparities.ind_a_vs_avg || 0) > 0 ? '#166534' : '#991b1b'};">${(data.disparities.ind_a_vs_avg || 0).toFixed(2)}%</span></td></tr>
                <tr style="border-bottom:1px solid #eee;"><th style="padding:12px 8px; color:#475569;">괴리율 (지표A vs 중간)</th><td><span style="padding:4px 8px; border-radius:12px; background:${(data.disparities.ind_a_vs_median || 0) > 0 ? '#dcfce7' : '#fee2e2'}; color:${(data.disparities.ind_a_vs_median || 0) > 0 ? '#166534' : '#991b1b'};">${(data.disparities.ind_a_vs_median || 0).toFixed(2)}%</span></td></tr>
            `;
            if(data.special_rule_applied) {
                html += `<tr><td colspan="2" style="color:#ef4444; font-size:0.9em; padding-top:10px;"><i class="fa-solid fa-triangle-exclamation"></i> 지하 매물 부족으로 1층 시세의 70% 특례 적용됨</td></tr>`;
            }
            document.getElementById('naverPriceTableBody').innerHTML = html;
            
            let propsHtml = '';
            if(data.properties && data.properties.length > 0) {
                data.properties.forEach(p => {
                    propsHtml += `
                        <tr style="border-bottom:1px solid #f1f5f9;">
                            <td style="padding:12px 10px; font-size:0.95em;">${p.address}</td>
                            <td style="padding:12px 10px; font-size:0.9em; color:#64748b;">${p.floor_cat}</td>
                            <td style="padding:12px 10px; font-size:0.9em; color:#64748b;">${p.pyeong}평</td>
                            <td style="padding:12px 10px; text-align:right; font-weight:500;">${(p.price || 0).toFixed(2)}</td>
                        </tr>
                    `;
                });
            } else {
                propsHtml = `<tr><td colspan="4" style="text-align:center; padding:30px; color:#94a3b8;">유사 조건의 사례 부동산이 없습니다.</td></tr>`;
            }
            document.getElementById('naverPricePropsBody').innerHTML = propsHtml;
            
        } else {
            throw new Error(res.message || "Unknown error");
        }
    } catch (err) {
        document.getElementById('naverPriceLoading').style.display = 'none';
        document.getElementById('naverPriceError').style.display = 'block';
        document.getElementById('naverPriceError').innerText = "오류 발생: " + err.message;
    }
}
</script>"""

if script_pattern.search(content):
    content = script_pattern.sub(new_script, content)
else:
    print("Could not find script block in map.html!")

# Fix the header just in case it still says 억억원 or 평당가
content = content.replace('매물호가(억원)억원', '매물호가(억원)')
content = content.replace('매물호가(억원)원', '매물호가(억원)')
content = content.replace('평당가(원)', '매물호가(억원)')

with open(map_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Cleaned up map.html")


# 2. FIX backend/naver_price_analyzer.py
# - Use '사용승인일' to compute age. Categories: 10년 이하, 25년 이하, 25년 초과.
# - Categorize floor for properties list.

file_path = r'backend\naver_price_analyzer.py'
with open(file_path, 'r', encoding='utf-8') as f:
    analyzer = f.read()

# Replace the text-based age category logic with '사용승인일' based one
old_age = """    def get_age_category_from_text(text):
        if pd.isna(text): return "알수없음"
        text = str(text)
        if "10년" in text and ("이내" in text or "이하" in text):
            return "10년 이하"
        elif "25년" in text and ("이상" in text or "초과" in text):
            return "30년 초과"
        elif "30년" in text and ("이상" in text or "초과" in text):
            return "30년 초과"
        return "30년 이하"
        
    df['age_cat'] = df['보조설명'].apply(get_age_category_from_text)"""

new_age = """    def get_age_category(val):
        try:
            val_str = str(val).strip()
            # YYYYMMDD format expected in '사용승인일'
            if len(val_str) >= 4 and val_str[:4].isdigit():
                year = int(val_str[:4])
                age = 2026 - year
                if age <= 10: return "10년 이하"
                if age <= 25: return "25년 이하"
                return "25년 초과"
            return "알수없음"
        except:
            return "알수없음"
            
    if '사용승인일' in df.columns:
        df['age_cat'] = df['사용승인일'].apply(get_age_category)
    else:
        df['age_cat'] = "알수없음" """

analyzer = analyzer.replace(old_age, new_age)

# Fix properties list floor output
# change `"floor": row.get('층수', ''),` to `"floor_cat": row.get('floor_cat', row.get('층수', '')),`
analyzer = analyzer.replace('"floor": row.get(\'층수\', \'\'),', '"floor_cat": row.get(\'floor_cat\', row.get(\'층수\', \'\')),')

# Fix JSON return keys
# 'avg_per_pyeong' -> 'avg_price'
# 'median_per_pyeong' -> 'median_price'
# 'min_per_pyeong' -> 'min_price'
analyzer = analyzer.replace('"median_per_pyeong": median_price', '"median_price": median_price')
analyzer = analyzer.replace('"avg_per_pyeong": avg_price', '"avg_price": avg_price')
analyzer = analyzer.replace('"min_per_pyeong": min_price', '"min_price": min_price')

# Make sure age_cat logic matches in the request payload matching
# The user wants "10년 이하 25년 이하 25년 초과".
old_target_age_cat = """    target_age = 2026 - int(str(target_build_year)[:4]) if str(target_build_year)[:4].isdigit() else 15
    if target_age <= 10: target_age_cat = "10년 이하"
    elif target_age <= 30: target_age_cat = "30년 이하"
    else: target_age_cat = "30년 초과" """

new_target_age_cat = """    target_age = 2026 - int(str(target_build_year)[:4]) if str(target_build_year)[:4].isdigit() else 15
    if target_age <= 10: target_age_cat = "10년 이하"
    elif target_age <= 25: target_age_cat = "25년 이하"
    else: target_age_cat = "25년 초과" """

analyzer = analyzer.replace(old_target_age_cat, new_target_age_cat)

# Expense ratio
old_expense_ratio = """    if target_age_cat == "10년 이하":
        expense_ratio = 0.1
    elif target_age_cat == "30년 이하":
        expense_ratio = 0.5
    else:
        expense_ratio = 0.7"""

new_expense_ratio = """    if target_age_cat == "10년 이하":
        expense_ratio = 0.1
    elif target_age_cat == "25년 이하":
        expense_ratio = 0.5
    else:
        expense_ratio = 0.7"""

analyzer = analyzer.replace(old_expense_ratio, new_expense_ratio)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(analyzer)
print("Updated naver_price_analyzer.py")
