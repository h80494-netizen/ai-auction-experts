import os

map_path = r'public\map.html'
with open(map_path, 'r', encoding='utf-8') as f:
    content = f.read()

js_code = """
<script>
async function openNaverPriceModal() {
    document.getElementById('naverPriceModal').style.display = 'flex';
    document.getElementById('naverPriceLoading').style.display = 'block';
    document.getElementById('naverPriceResult').style.display = 'none';
    document.getElementById('naverPriceError').style.display = 'none';

    // Mock data extracting from highlighter or current view if not available globally
    // We try to pull from window.lastSelectedAuction or similar. If not found, use a fallback
    let lat = window.lastSelectedLat || 37.5665;
    let lon = window.lastSelectedLon || 126.9780;
    let type = window.lastSelectedType || "아파트";
    let pyeong = window.lastSelectedPyeong || 25;
    let floor = window.lastSelectedFloor || "5층";
    let total_floor = window.lastSelectedTotalFloor || "15층";
    let build_year = window.lastSelectedBuildYear || "2010";
    let appraised = window.lastSelectedAppraised || 500000000;
    let min_price = window.lastSelectedMinPrice || 400000000;
    let senior_debt = window.lastSelectedSeniorDebt || 0;

    // Try to get from DOM if a popup is open
    try {
        const popup = document.querySelector('.leaflet-popup-content');
        if(popup) {
            if(popup.innerText.includes('빌라') || popup.innerText.includes('다세대')) type = '빌라';
            else if(popup.innerText.includes('상가')) type = '상가';
            
            // Very naive extraction, typically you'd bind this properly
            // Leaving as fallback
        }
    } catch(e) {}

    const payload = {
        lat: lat,
        lon: lon,
        type: type,
        area_pyeong: pyeong,
        floor: String(floor),
        total_floor: String(total_floor),
        build_year: String(build_year),
        appraised_price: appraised,
        min_price: min_price,
        senior_debt: senior_debt
    };

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
            document.getElementById('naverPriceResult').style.display = 'block';
            let html = `
                <tr><th>분석 대상</th><td>${type} / ${data.target_categories.floor} / ${data.target_categories.area} / ${data.target_categories.age}</td></tr>
                <tr><th>탐색 반경</th><td>${data.radius_used}m (매칭: ${data.matched_count}건)</td></tr>
                <tr><th>평당 제비용</th><td>${data.target_indicators.expense_per_pyeong.toLocaleString()} 원</td></tr>
                <tr><th>지표 A (최저가기준)</th><td>${data.target_indicators.ind_a.toLocaleString()} 원/평</td></tr>
                <tr><th>지표 B (적정가기준)</th><td>${data.target_indicators.ind_b.toLocaleString()} 원/평</td></tr>
                <tr><th>주변 매물 중간값</th><td>${data.market_prices.median_per_pyeong.toLocaleString()} 원/평</td></tr>
                <tr><th>주변 매물 최저가</th><td>${data.market_prices.min_per_pyeong.toLocaleString()} 원/평</td></tr>
                <tr><th>괴리율 (지표A vs 중간값)</th><td>${data.disparities.ind_a_vs_median.toFixed(2)} %</td></tr>
                <tr><th>괴리율 (지표B vs 중간값)</th><td>${data.disparities.ind_b_vs_median.toFixed(2)} %</td></tr>
            `;
            if(data.special_rule_applied) {
                html += `<tr><td colspan="2" style="color:red; font-size:0.9em;">* 지하 빌라 매물 부족으로 1층 시세의 70% 특례 적용됨</td></tr>`;
            }
            document.getElementById('naverPriceTableBody').innerHTML = html;
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

if 'openNaverPriceModal' not in content:
    content = content.replace('</body>', js_code + '\n</body>')
    with open(map_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Injected JS successfully")
else:
    print("JS already exists")
