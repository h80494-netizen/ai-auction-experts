
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
let naverLayerGroup = null;

function toggleNaverRealEstate() {
    const isChecked = document.getElementById('toggle-naver').checked;
    const selector = document.getElementById('naver-type-selector');
    if (isChecked) {
        selector.style.display = 'block';
        fetchNaverRealEstate();
        map.on('moveend', fetchNaverRealEstate);
    } else {
        selector.style.display = 'none';
        map.off('moveend', fetchNaverRealEstate);
        if (naverLayerGroup) {
            map.removeLayer(naverLayerGroup);
            naverLayerGroup = null;
        }
    }
}

async function fetchNaverRealEstate() {
    const isChecked = document.getElementById('toggle-naver').checked;
    if (!isChecked) return;
    
    const type = document.getElementById('naver-type').value;
    const bounds = map.getBounds();
    const min_lat = bounds.getSouthWest().lat;
    const max_lat = bounds.getNorthEast().lat;
    const min_lng = bounds.getSouthWest().lng;
    const max_lng = bounds.getNorthEast().lng;
    
    if (naverLayerGroup) {
        map.removeLayer(naverLayerGroup);
    }
    naverLayerGroup = L.markerClusterGroup({
        chunkedLoading: true,
        disableClusteringAtZoom: 16,
        maxClusterRadius: 60,
        clusterPane: 'naverPane'
    }).addTo(map);
    
    try {
        const res = await fetch(`/api/naver-realestate?estate_type=${encodeURIComponent(type)}&min_lat=${min_lat}&max_lat=${max_lat}&min_lng=${min_lng}&max_lng=${max_lng}`);
        const json = await res.json();
        
        if (json.status === 'success' && json.data) {
            const markers = [];
            json.data.forEach(item => {
                const markerHtml = `<div style="background-color: black; border-radius: 50%; width: 14px; height: 14px; border: 2px solid white; box-shadow: 0 0 4px rgba(0,0,0,0.5); pointer-events: none;"></div>`;
                const icon = L.divIcon({
                    html: markerHtml,
                    className: 'leaflet-div-icon',
                    iconSize: [14, 14],
                    iconAnchor: [7, 7]
                });

                function formatPrice(priceVal) {
                    if (isNaN(priceVal) || priceVal == 0) return '-';
                    let uk = Math.floor(priceVal / 100000000);
                    let man = Math.floor((priceVal % 100000000) / 10000);
                    return (uk > 0 ? uk + '억' : '') + (man > 0 ? (uk > 0 ? ' ' : '') + man + '만' : '');
                }

                let pyungRows = '';
                if (item.pyung_groups) {
                    item.pyung_groups.forEach(pg => {
                        let minP = formatPrice(pg.min_price);
                        let maxP = formatPrice(pg.max_price);
                        let minPPP_str = formatPrice(pg.min_price_per_pyung);
                        let maxPPP_str = formatPrice(pg.max_price_per_pyung);
                        
                        let idsStr = pg.estate_ids.slice(0, 5).join(", ");
                        if (pg.estate_ids.length > 5) idsStr += " 외 " + (pg.estate_ids.length - 5) + "건";
                        
                        pyungRows += `
                            <tr style="border-bottom: 1px dashed #eee;">
                                <td style="padding:4px 0; font-weight:bold; color:#000; white-space:nowrap;">${pg.pyung}</td>
                                <td style="padding:4px 0; text-align:right; font-weight:bold; color:#3b82f6; white-space:nowrap;">${pg.count}건</td>
                                <td style="padding:4px 0; text-align:right; color:#ef4444; white-space:nowrap;">${minP} ~ ${maxP}</td>
                                <td style="padding:4px 0; text-align:right; font-size:0.8rem; color:gray; white-space:nowrap;">당 ${minPPP_str}~${maxPPP_str}</td>
                            </tr>
                            <tr style="border-bottom: 2px solid #eaeaea;">
                                <td colspan="4" style="padding:0 0 6px 0; font-size:0.75rem; color:gray; text-align:right;">매물번호: ${idsStr}</td>
                            </tr>
                        `;
                    });
                }
                
                const hoverContent = `<div style="font-family:'Noto Sans KR'; font-weight:bold; font-size:1rem;">${type} 총 ${item.total_count}건</div>`;
                
                const popupContent = `
                    <div style="font-family:'Noto Sans KR'; min-width: 480px; padding-bottom: 5px;">
                        <div style="font-size:1.1rem;"><span style="color:#00c73c;font-weight:bold;">[네이버 매물]</span> <b style="font-size:0.9rem;">${item.address}</b></div>
                        ${item.age_info ? `<div style="font-size:0.85rem; color:#f59e0b; font-weight:bold; margin-top:2px;">⏱ [건축/노후도] ${item.age_info}</div>` : ''}
                        <div style="color:gray; font-size:0.85rem; margin-bottom:8px; margin-top:4px;">해당 필지 내 총 <b>${item.total_count}건</b>의 매물이 존재합니다.</div>
                        <div style="max-height: 300px; overflow-y: auto;">
                            <table style="width:100%; font-size:0.9rem; border-collapse: collapse; margin-bottom: 10px;">
                                <thead>
                                    <tr style="border-bottom: 2px solid #ccc;">
                                        <th style="text-align:left; padding:4px 0; white-space:nowrap;">평형</th>
                                        <th style="text-align:right; padding:4px 0; white-space:nowrap;">건수</th>
                                        <th style="text-align:right; padding:4px 0; white-space:nowrap;">최저~최고가</th>
                                        <th style="text-align:right; padding:4px 0; white-space:nowrap;">평당 최저~최고</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${pyungRows}
                                </tbody>
                            </table>
                        </div>
                        <button onclick="window.open('https://new.land.naver.com/complexes?ms=${item.lat},${item.lng},18&a=APT:OPST:VL:OR:ONE:GO:CST:DDD:SG:HO:EN', '_blank')" style="box-sizing: border-box; width:100%; padding:8px; background:#00c73c; color:white; border:none; border-radius:4px; font-weight:bold; cursor:pointer; font-size:1rem; margin-top:5px;">
                            <i class="fa-solid fa-arrow-up-right-from-square"></i> 네이버 부동산 원문 보기
                        </button>
                        <button onclick="showNaverDetails(${item.lat}, ${item.lng}, '${type}', '${item.address}')" style="box-sizing: border-box; width:100%; padding:8px; background:#475569; color:white; border:none; border-radius:4px; font-weight:bold; cursor:pointer; font-size:1rem; margin-top:5px;">
                            <i class="fa-solid fa-list"></i> 세부 매물 리스트 보기
                        </button>
                    </div>
                `;
                
                const marker = L.marker([item.lat, item.lng], { icon: icon, pane: 'naverPane' })
                 .bindTooltip(popupContent, { direction: 'top', offset: [0, -10], opacity: 1, className: 'naver-tooltip' })
                 .bindPopup(popupContent, { offset: [0, -10], maxWidth: 600 });
                
                markers.push(marker);
            });
            naverLayerGroup.addLayers(markers);
        } else {
            console.warn(json.message);
        }
    } catch (e) {
        console.error('Error fetching Naver real estate:', e);
    }
}
async function showNaverDetails(lat, lng, estateType, address) {
    document.getElementById('naverDetailsAddress').innerText = "- " + address;
    const tbody = document.getElementById('naverDetailsTableBody');
    tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; padding: 20px;">로딩 중...</td></tr>';
    document.getElementById('naverDetailsModal').style.display = 'flex';
    
    try {
        const response = await fetch(`/api/naver-realestate-details?lat=${lat}&lng=${lng}&estate_type=${encodeURIComponent(estateType)}`);
        const json = await response.json();
        
        if (json.status === 'success' && json.data) {
            if (json.data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; padding: 20px;">매물 데이터가 없습니다.</td></tr>';
                return;
            }
            
            let html = '';
            json.data.forEach(item => {
                const dealType = item.deal_type || '-';
                let priceStr = item.price || '-';
                if (item.rent && item.rent !== '0') {
                    priceStr += ` / ${item.rent}`;
                }
                
                let pppStr = '-';
                if (item.price_per_pyung > 0) {
                    pppStr = item.price_per_pyung.toLocaleString() + '만';
                }
                
                const floorStr = item.floor || '-';
                const areaStr = item.area || '-';
                const pyungStr = item.pyung ? `${item.pyung}평` : '-';
                const ageInfo = item.age_info || '-';
                const typeDetail = item.type_detail || '-';
                const estateId = item.estate_id || '-';
                
                html += `
                    <tr style="border-bottom: 1px solid #e2e8f0;">
                        <td style="padding:8px 10px; text-align:center;"><a href="https://new.land.naver.com/complexes?ms=${lat},${lng},18&a=APT:OPST:VL:OR:ONE:GO:CST:DDD:SG:HO:EN&articleNo=${estateId}" target="_blank" style="color:#2563eb; text-decoration:none; font-weight:bold;">${estateId}</a></td>
                        <td style="padding:8px 10px; text-align:center;"><span style="background:#e0f2fe; color:#0369a1; padding:2px 6px; border-radius:4px; font-size:0.8rem; font-weight:bold;">${dealType}</span></td>
                        <td style="padding:8px 10px; text-align:right; font-weight:bold; color:#b91c1c;">${priceStr}</td>
                        <td style="padding:8px 10px; text-align:right; color:#475569;">${pppStr}</td>
                        <td style="padding:8px 10px; text-align:center;">${floorStr}</td>
                        <td style="padding:8px 10px; text-align:right;">${pyungStr}<br><span style="font-size:0.75rem; color:gray;">(${areaStr})</span></td>
                        <td style="padding:8px 10px; text-align:center; color:#f59e0b;">${ageInfo}</td>
                        <td style="padding:8px 10px; text-align:left;">${typeDetail}</td>
                    </tr>
                `;
            });
            tbody.innerHTML = html;
        } else {
            tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; padding: 20px; color:red;">에러: ${json.message}</td></tr>`;
        }
    } catch (e) {
        console.error('Error fetching Naver details:', e);
        tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; padding: 20px; color:red;">데이터를 불러오는 중 오류가 발생했습니다.</td></tr>';
    }
}
