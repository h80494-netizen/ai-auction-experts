import re
import os

map_path = r'public\map.html'
with open(map_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove old button
content = re.sub(r'<div class="icon-btn" id="btn-naver-price".*?</div>', '', content)

# 2. Inject popup button
popup_btn = """                            <button onclick="openNaverPriceModal('${d.case_no}', ${d.lat}, ${d.lng}, '${d.property_type}', ${d.area_size || 0});" style="width:100%; background:#f59e0b; color:white; border:none; padding:10px; border-radius:6px; cursor:pointer; font-size:0.95rem; font-weight:bold; margin-top: 8px; touch-action:manipulation;"><i class="fa-solid fa-chart-line"></i> 네이버 시세 분석</button>\n"""

# Find the 상권분석 button and insert after it
pattern = r'(<button onclick="openDemandPanel[^>]*>.*?상권분석.*?</button>)'
content = re.sub(pattern, r'\1\n' + popup_btn, content)

# 3. Update Modal HTML
new_modal_html = """
<!-- Naver Price Analysis Split Modal -->
<div id="naverPriceModal" class="modal-overlay" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 10000; align-items: center; justify-content: center;">
    <div class="modal-content" style="background: white; padding: 20px; border-radius: 10px; width: 1000px; max-width: 95%; height: 80vh; max-height: 800px; display: flex; flex-direction: column;">
        <h2 style="margin-bottom:15px; border-bottom:1px solid #eee; padding-bottom:10px;"><i class="fa-solid fa-chart-line"></i> 네이버 시세 분석</h2>
        <div id="naverPriceLoading" style="display: none; text-align: center; padding: 50px;">
            <i class="fa-solid fa-spinner fa-spin fa-3x"></i>
            <p style="margin-top:15px; font-size:1.1rem;">사례 부동산 탐색 및 시세 분석 중입니다...</p>
        </div>
        
        <div id="naverPriceResult" style="display: none; flex: 1; flex-direction: row; gap: 20px; overflow: hidden;">
            <!-- Left: Properties List -->
            <div style="flex: 1; border-right: 1px solid #ddd; padding-right: 20px; overflow-y: auto;">
                <h3 style="font-size:1.2rem; margin-bottom:10px;"><i class="fa-solid fa-list"></i> 유사 사례 부동산 리스트</h3>
                <table style="width: 100%; border-collapse: collapse; text-align: left;">
                    <thead>
                        <tr style="background:#f1f5f9; border-bottom:2px solid #cbd5e1;">
                            <th style="padding:10px;">위치</th>
                            <th style="padding:10px;">층수</th>
                            <th style="padding:10px;">면적</th>
                            <th style="padding:10px; text-align:right;">평당가(원)</th>
                        </tr>
                    </thead>
                    <tbody id="naverPricePropsBody">
                    </tbody>
                </table>
            </div>
            
            <!-- Right: Stats -->
            <div style="flex: 1; padding-left: 10px; overflow-y: auto;">
                <h3 style="font-size:1.2rem; margin-bottom:10px;"><i class="fa-solid fa-chart-pie"></i> 시세 요약 통계</h3>
                <table style="width: 100%; border-collapse: collapse; text-align: left;">
                    <tbody id="naverPriceTableBody">
                    </tbody>
                </table>
            </div>
        </div>
        
        <div id="naverPriceError" style="display: none; color: red; margin-top: 15px; padding: 20px; background:#fef2f2; border:1px solid #fca5a5; border-radius:5px;"></div>
        
        <div style="text-align: right; margin-top: 20px; border-top:1px solid #eee; padding-top:15px;">
            <button onclick="document.getElementById('naverPriceModal').style.display='none'" style="padding: 10px 20px; cursor: pointer; border-radius: 6px; border: none; background: #64748b; color:white; font-weight:bold;">닫기</button>
        </div>
    </div>
</div>
"""
# Replace the old modal
content = re.sub(r'<!-- Naver Price Analysis Modal -->.*?</div>\s*</div>\s*</div>', new_modal_html, content, flags=re.DOTALL)

# 4. Update JS Logic
new_js_logic = """
<script>
async function openNaverPriceModal(caseNo, lat, lng, type, size) {
    document.getElementById('naverPriceModal').style.display = 'flex';
    document.getElementById('naverPriceLoading').style.display = 'block';
    document.getElementById('naverPriceResult').style.display = 'none';
    document.getElementById('naverPriceError').style.display = 'none';

    // Build payload
    const payload = {
        lat: lat || 37.5665,
        lon: lng || 126.9780,
        type: type || "아파트",
        area_pyeong: size ? (size / 3.3058).toFixed(2) : 25,
        floor: "5층", // Fallback, could be extracted from case details if available globally
        total_floor: "15층",
        build_year: "2010",
        appraised_price: 500000000,
        min_price: 400000000,
        senior_debt: 0
    };
    
    // In a real integration, you might pull real appraised_price, min_price from a global auction cache using caseNo
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
            
            // Render Right side (Stats)
            let html = `
                <tr style="border-bottom:1px solid #eee;"><th style="padding:12px 8px; width:45%; color:#475569;">분석 대상</th><td style="font-weight:bold;">${type} / ${data.target_categories.floor} / ${data.target_categories.area}</td></tr>
                <tr style="border-bottom:1px solid #eee;"><th style="padding:12px 8px; color:#475569;">탐색 반경</th><td style="color:#0284c7; font-weight:bold;">${data.radius_used}m <span style="font-size:0.9em; color:#64748b;">(매칭: ${data.matched_count}건)</span></td></tr>
                <tr style="border-bottom:1px solid #eee;"><th style="padding:12px 8px; color:#475569;">평당 제비용</th><td>${data.target_indicators.expense_per_pyeong.toLocaleString()} 원</td></tr>
                <tr style="border-bottom:1px solid #eee; background:#f8fafc;"><th style="padding:12px 8px; color:#475569;">지표 A (최저가+비용)</th><td style="font-weight:bold; color:#0f172a;">${Math.round(data.target_indicators.ind_a).toLocaleString()} 원/평</td></tr>
                <tr style="border-bottom:1px solid #eee; background:#f8fafc;"><th style="padding:12px 8px; color:#475569;">지표 B (적정가+비용)</th><td style="font-weight:bold; color:#0f172a;">${Math.round(data.target_indicators.ind_b).toLocaleString()} 원/평</td></tr>
                
                <tr style="border-bottom:1px solid #eee;"><th style="padding:12px 8px; color:#475569;">사례 평균가</th><td>${Math.round(data.market_prices.avg_per_pyeong).toLocaleString()} 원/평</td></tr>
                <tr style="border-bottom:1px solid #eee;"><th style="padding:12px 8px; color:#475569;">사례 중간값</th><td>${Math.round(data.market_prices.median_per_pyeong).toLocaleString()} 원/평</td></tr>
                <tr style="border-bottom:1px solid #eee;"><th style="padding:12px 8px; color:#475569;">평균 90% 수준</th><td style="color:#16a34a; font-weight:bold;">${Math.round(data.market_prices.avg_90).toLocaleString()} 원/평</td></tr>
                <tr style="border-bottom:1px solid #eee;"><th style="padding:12px 8px; color:#475569;">중간 90% 수준</th><td style="color:#16a34a; font-weight:bold;">${Math.round(data.market_prices.median_90).toLocaleString()} 원/평</td></tr>
                <tr style="border-bottom:1px solid #eee;"><th style="padding:12px 8px; color:#475569;">사례 최저가</th><td style="color:#dc2626; font-weight:bold;">${Math.round(data.market_prices.min_per_pyeong).toLocaleString()} 원/평</td></tr>
                
                <tr style="border-bottom:1px solid #eee;"><th style="padding:12px 8px; color:#475569;">괴리율 (지표A vs 평균)</th><td><span style="padding:4px 8px; border-radius:12px; background:${data.disparities.ind_a_vs_avg > 0 ? '#dcfce7' : '#fee2e2'}; color:${data.disparities.ind_a_vs_avg > 0 ? '#166534' : '#991b1b'};">${data.disparities.ind_a_vs_avg.toFixed(2)}%</span></td></tr>
                <tr style="border-bottom:1px solid #eee;"><th style="padding:12px 8px; color:#475569;">괴리율 (지표A vs 중간)</th><td><span style="padding:4px 8px; border-radius:12px; background:${data.disparities.ind_a_vs_median > 0 ? '#dcfce7' : '#fee2e2'}; color:${data.disparities.ind_a_vs_median > 0 ? '#166534' : '#991b1b'};">${data.disparities.ind_a_vs_median.toFixed(2)}%</span></td></tr>
            `;
            if(data.special_rule_applied) {
                html += `<tr><td colspan="2" style="color:#ef4444; font-size:0.9em; padding-top:10px;"><i class="fa-solid fa-triangle-exclamation"></i> 지하 매물 부족으로 1층 시세의 70% 특례 적용됨</td></tr>`;
            }
            document.getElementById('naverPriceTableBody').innerHTML = html;
            
            // Render Left side (Properties)
            let propsHtml = '';
            if(data.properties && data.properties.length > 0) {
                data.properties.forEach(p => {
                    propsHtml += `
                        <tr style="border-bottom:1px solid #f1f5f9;">
                            <td style="padding:12px 10px; font-size:0.95em;">${p.address}</td>
                            <td style="padding:12px 10px; font-size:0.9em; color:#64748b;">${p.floor}</td>
                            <td style="padding:12px 10px; font-size:0.9em; color:#64748b;">${p.pyeong}평</td>
                            <td style="padding:12px 10px; text-align:right; font-weight:500;">${Math.round(p.price).toLocaleString()}</td>
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
</script>
"""
# Replace old JS
content = re.sub(r'<script>\s*async function openNaverPriceModal.*?<\/script>', new_js_logic, content, flags=re.DOTALL)

with open(map_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated map.html successfully")
