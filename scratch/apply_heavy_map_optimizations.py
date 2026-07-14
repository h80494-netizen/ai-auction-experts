import re

file_path = "public/map.html"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

content_lf = content.replace("\r\n", "\n")

# 1. Replace buildAuctionUrl signature and bounds initialization
old_build_url_start = """        function buildAuctionUrl(basePath) {
            const bounds = map.getBounds();"""

new_build_url_start = """        function buildAuctionUrl(basePath, customBounds) {
            const bounds = customBounds || map.getBounds();"""

if old_build_url_start in content_lf:
    content_lf = content_lf.replace(old_build_url_start, new_build_url_start)
    print("SUCCESS: buildAuctionUrl signature updated!")
else:
    print("WARNING: Could not find buildAuctionUrl signature to update!")

# 2. Replace fetchInfraData function with cached & toggle-optimized version
infra_pattern = re.compile(r"(\s+async function fetchInfraData\(\)\s*\{.*?^\s*\})", re.DOTALL | re.MULTILINE)
infra_matches = infra_pattern.findall(content_lf)

if not infra_matches:
    print("ERROR: fetchInfraData not found!")
    exit(1)

original_infra = infra_matches[0]
print("Found original fetchInfraData function of length:", len(original_infra))

optimized_infra = """        let cachedInfraBounds = null;
        let cachedInfraZoom = null;
        let cachedInfraTogglesKey = "";

        function getInfraTogglesKey() {
            return [
                document.getElementById('toggle-subways').checked,
                document.getElementById('toggle-univs').checked,
                document.getElementById('toggle-inds').checked,
                document.getElementById('toggle-middles')?.checked || false,
                document.getElementById('toggle-bus')?.checked || false,
                document.getElementById('toggle-commercial')?.checked || false,
                document.getElementById('buffer-subways')?.value || '',
                document.getElementById('buffer-univs')?.value || '',
                document.getElementById('buffer-inds')?.value || '',
                document.getElementById('buffer-middles')?.value || '',
                document.getElementById('buffer-bus')?.value || '',
                document.getElementById('buffer-commercial')?.value || ''
            ].join('_');
        }

        async function fetchInfraData() {
            if (map.getZoom() < minZoomRequired) return;

            // 만약 아무 인프라 토글도 켜져 있지 않다면 API 요청 자체를 생략
            const anyInfraChecked = 
                document.getElementById('toggle-subways').checked ||
                document.getElementById('toggle-univs').checked ||
                document.getElementById('toggle-inds').checked ||
                (document.getElementById('toggle-middles') && document.getElementById('toggle-middles').checked) ||
                (document.getElementById('toggle-bus') && document.getElementById('toggle-bus').checked) ||
                (document.getElementById('toggle-commercial') && document.getElementById('toggle-commercial').checked);

            if (!anyInfraChecked) {
                layers.subway.clearLayers();
                layers.univ.clearLayers();
                layers.ind.clearLayers();
                layers.middle.clearLayers();
                layers.bus.clearLayers();
                layers.commercial.clearLayers();
                cachedInfraBounds = null;
                cachedInfraZoom = null;
                cachedInfraTogglesKey = "";
                triggerHighlighter();
                return;
            }

            const currentZoom = map.getZoom();
            const currentTogglesKey = getInfraTogglesKey();
            const bounds = map.getBounds();

            // 스마트 캐싱: 줌 레벨과 토글 상태가 동일하고, 현재 영역이 캐싱된 패딩 영역 내에 완전히 존재하면 재요청 생략
            if (cachedInfraZoom === currentZoom && 
                cachedInfraTogglesKey === currentTogglesKey && 
                cachedInfraBounds && 
                cachedInfraBounds.contains(bounds)) {
                return;
            }

            // 25% 패딩을 주어 더 넓은 영역을 한 번에 가져오고 캐싱합니다
            const southWest = bounds.getSouthWest();
            const northEast = bounds.getNorthEast();
            const latDiff = northEast.lat - southWest.lat;
            const lngDiff = northEast.lng - southWest.lng;
            const padLat = latDiff * 0.25;
            const padLng = lngDiff * 0.25;
            
            const paddedBounds = L.latLngBounds(
                L.latLng(southWest.lat - padLat, southWest.lng - padLng),
                L.latLng(northEast.lat + padLat, northEast.lng + padLng)
            );

            cachedInfraBounds = paddedBounds;
            cachedInfraZoom = currentZoom;
            cachedInfraTogglesKey = currentTogglesKey;

            const checkedRegions = Array.from(document.querySelectorAll('.region-checkbox:checked')).map(cb => cb.value);
            let url = `/api/map/pois?min_lat=${paddedBounds.getSouth()}&max_lat=${paddedBounds.getNorth()}&min_lng=${paddedBounds.getWest()}&max_lng=${paddedBounds.getEast()}`;
            if (checkedRegions.length > 0) url += `&regions=${checkedRegions.join(',')}`;

            try {
                const res = await fetch(url);
                const json = await res.json();

                if (json.status === 'success') {
                    const data = json.data;

                    if (data.subways && document.getElementById('toggle-subways').checked) {
                        layers.subway.clearLayers();
                        data.subways.forEach(s => {
                            let radius = parseInt(document.getElementById('buffer-subways').value) || 500;
                            let color = getGlobalLineColor(s.line);
                            L.circle([s.lat, s.lng], { color: color, fillColor: color, fillOpacity: 0.1, radius: radius, weight: 1, dashArray: '4, 4' }).addTo(layers.subway);
                            createDotMarker(s.lat, s.lng, color, `<b>${s.name}</b><br>${s.line}`)
                                .addTo(layers.subway);
                        });
                    }

                    if (data.universities && document.getElementById('toggle-univs').checked) {
                        layers.univ.clearLayers();
                        data.universities.forEach(u => {
                            let radius = parseInt(document.getElementById('buffer-univs').value) || 500;
                            L.circle([u.lat, u.lng], { color: '#3b82f6', fillColor: '#3b82f6', fillOpacity: 0.1, radius: radius, weight: 1, dashArray: '4, 4' }).addTo(layers.univ);
                            createDotMarker(u.lat, u.lng, '#3b82f6', `<b>${u.name}</b><br>대학교`).addTo(layers.univ);
                        });
                    }

                    if (data.industrial_complexes && document.getElementById('toggle-inds').checked) {
                        layers.ind.clearLayers();
                        data.industrial_complexes.forEach(i => {
                            let radius = parseInt(document.getElementById('buffer-inds').value) || 500;
                            L.circle([i.lat, i.lng], { color: '#f59e0b', fillColor: '#f59e0b', fillOpacity: 0.1, radius: radius, weight: 1, dashArray: '4, 4' }).addTo(layers.ind);
                            createDotMarker(i.lat, i.lng, '#f59e0b', `<b>${i.name}</b><br>산업단지`).addTo(layers.ind);
                        });
                    }

                    if (data.middle_schools && document.getElementById('toggle-middles') && document.getElementById('toggle-middles').checked) {
                        layers.middle.clearLayers();
                        data.middle_schools.forEach(m => {
                            let color = '#94a3b8';
                            let label = `특목고 진학률 ${parseFloat(m.special_hs_rate).toFixed(1)}%`;
                            let markerRadius = 4;
                            if (m.special_hs_rate >= 10) {
                                color = '#f43f5e';
                                markerRadius = 6;
                                let radius = parseInt(document.getElementById('buffer-middles').value) || 500;
                                L.circle([m.lat, m.lng], { color: '#f43f5e', fillColor: '#f43f5e', fillOpacity: 0.1, radius: radius, weight: 1, dashArray: '4, 4' }).addTo(layers.middle);
                            }
                            createDotMarker(m.lat, m.lng, color, `<b>${m.name}</b><br>${label}`, markerRadius).addTo(layers.middle);
                        });
                    }
                    
                    if (document.getElementById('toggle-bus').checked && map.getZoom() >= minZoomRequired && data.bus_stops) {
                        layers.bus.clearLayers();
                        let radius = parseInt(document.getElementById('buffer-bus').value) || 20;
                        data.bus_stops.forEach(b => {
                            L.circle([b.lat, b.lng], { color: '#0ea5e9', fillColor: '#0ea5e9', fillOpacity: 0.1, radius: radius, weight: 1, dashArray: '4, 4' }).addTo(layers.bus);
                            createDotMarker(b.lat, b.lng, '#0ea5e9', `<b>${b.name}</b><br>버스 (${b.city})`, 3).addTo(layers.bus);
                        });
                    }
                    if (document.getElementById('toggle-commercial').checked && data.commercial_areas) {
                        
                        // 인구수 배열 생성 및 정렬 (백분위 계산용)
                        const pops = data.commercial_areas.map(c => c.population || 0).sort((a, b) => a - b);
                        
                        // ?곴텒 ?대쫫(name)蹂??멸뎄??留ㅽ븨
                        const popData = {};
                        data.commercial_areas.forEach(c => {
                            popData[c.name] = c.population || 0;
                        });

                        const getTierStyle = (pop) => {
                            if (pop === 0 || pops.length === 0) return null;
                            
                            // ?댁쭊 ?먯깋 ?€??媛꾨떒???꾩튂 李얘린 (?곗씠?곌? 留롮? ?딆쑝誘€濡?
                            const idx = pops.findIndex(p => p >= pop);
                            const percentile = (idx + 1) / pops.length;
                            const tier = Math.ceil(percentile * 10) || 1; // 1 ~ 10 단계
                            
                            if (tier <= 6) return null;
                            
                            const colors = {
                                10: '#08306b', 9: '#08519c', 8: '#2171b5', 7: '#4292c6'
                            };
                            
                            return {
                                color: colors[tier] || '#ffffff',
                                fillColor: colors[tier] || '#ffffff',
                                fillOpacity: 0.5,
                                weight: 0
                            };
                        };

                        if (!window.commercialGeoJsonData) {
                            try {
                                const res = await fetch('/data/seoul_commercial.geojson');
                                window.commercialGeoJsonData = await res.json();
                            } catch (err) {
                                console.error('Failed to load commercial geojson:', err);
                            }
                        }

                        if (window.commercialGeoJsonData) {
                            layers.commercial.clearLayers();
                            const geoJsonLayer = L.geoJSON(window.commercialGeoJsonData, {
                                filter: function(feature) {
                                    const name = feature.properties.TRDAR_CD_N;
                                    const pop = popData[name] || 0;
                                    const style = getTierStyle(pop);
                                    return style !== null;
                                },
                                style: function(feature) {
                                    const name = feature.properties.TRDAR_CD_N;
                                    const pop = popData[name] || 0;
                                    return getTierStyle(pop);
                                },
                                onEachFeature: function(feature, layer) {
                                    const name = feature.properties.TRDAR_CD_N;
                                    const pop = popData[name] || 0;
                                    let popStr = pop > 0 ? (pop / 10000).toFixed(0) + '만 명' : '데이터 없음';
                                    layer.bindTooltip(`<b>${name}</b><br>상권<br>유동인구: ${popStr}`, {
                                        sticky: true,
                                        className: 'custom-tooltip'
                                    });
                                }
                            });
                            geoJsonLayer.addTo(layers.commercial);
                        }
                    }
                }
            } catch (err) { console.error(err); } finally { triggerHighlighter(); }
        }"""

content_lf = content_lf.replace(original_infra, optimized_infra)
print("SUCCESS: fetchInfraData function optimized in memory!")

# 3. Replace loadAuctions function with cached version
load_auctions_pattern = re.compile(r"(\s+async function loadAuctions\(\)\s*\{.*?^\s*\})", re.DOTALL | re.MULTILINE)
load_auctions_matches = load_auctions_pattern.findall(content_lf)

if not load_auctions_matches:
    print("ERROR: loadAuctions not found!")
    exit(1)

original_load_auctions = load_auctions_matches[0]
print("Found original loadAuctions function of length:", len(original_load_auctions))

optimized_load_auctions = """        let cachedAuctionBounds = null;
        let cachedAuctionZoom = null;
        let cachedAuctionFilterKey = "";

        async function loadAuctions() {
            const zoomWarning = document.getElementById('zoom-warning');
            const currentZoom = map.getZoom();

            if (currentZoom < minZoomRequired) {
                layers.auction.clearLayers();
                cachedAuctionBounds = null;
                cachedAuctionZoom = null;
                cachedAuctionFilterKey = "";
                if (zoomWarning) {
                    zoomWarning.style.display = 'block';
                    setTimeout(() => { zoomWarning.style.opacity = '1'; }, 10);
                }
                return;
            } else {
                if (zoomWarning) {
                    zoomWarning.style.opacity = '0';
                    setTimeout(() => { zoomWarning.style.display = 'none'; }, 300);
                }
            }

            const bounds = map.getBounds();
            
            // 필터 키 생성 (lat, lng 바운즈 파라미터 제외한 나머지 쿼리스트링 조합)
            const fullUrl = buildAuctionUrl('/api/map/auctions');
            if (!fullUrl) return;
            const filterKey = fullUrl.replace(/min_lat=[^&]*&max_lat=[^&]*&min_lng=[^&]*&max_lng=[^&]*&?/, '');

            // 스마트 캐싱: 줌 레벨과 필터 상태가 동일하고, 현재 영역이 캐싱된 패딩 영역 내에 완전히 존재하면 재요청 생략
            if (cachedAuctionZoom === currentZoom && 
                cachedAuctionFilterKey === filterKey && 
                cachedAuctionBounds && 
                cachedAuctionBounds.contains(bounds)) {
                return;
            }

            // 25% 패딩을 주어 더 넓은 영역을 한 번에 가져오고 캐싱합니다
            const southWest = bounds.getSouthWest();
            const northEast = bounds.getNorthEast();
            const latDiff = northEast.lat - southWest.lat;
            const lngDiff = northEast.lng - southWest.lng;
            const padLat = latDiff * 0.25;
            const padLng = lngDiff * 0.25;
            
            const paddedBounds = L.latLngBounds(
                L.latLng(southWest.lat - padLat, southWest.lng - padLng),
                L.latLng(northEast.lat + padLat, northEast.lng + padLng)
            );

            // 캐시 정보 업데이트
            cachedAuctionBounds = paddedBounds;
            cachedAuctionZoom = currentZoom;
            cachedAuctionFilterKey = filterKey;

            layers.auction.clearLayers();

            const url = buildAuctionUrl('/api/map/auctions', paddedBounds);
            if (!url) return;

            try {
                const res = await fetch(url);
                const json = await res.json();

                if (json.status === 'success') {
                    json.data.forEach(item => {
                        let isPublic = item.sale_type.includes('공');
                        let typeColor = isPublic ? '#3b82f6' : '#ef4444';

                        let marker = L.circleMarker([item.lat, item.lng], {
                            radius: 6, fillColor: typeColor, color: '#fff', weight: 2, opacity: 1, fillOpacity: 1,
                            pane: 'auctionPane'
                        });
                        marker.auctionData = item;
                        marker.isPublic = isPublic;
                        marker.typeColor = typeColor;

                        marker.on('click', function(e) {
                            openDemandPanel(item.lat, item.lng, item.case_no, item.address, item.property_type);
                        });

                        marker.bindPopup(function(layer) {
                            let d = layer.auctionData;
                            let isPub = layer.isPublic;
                            let tColor = layer.typeColor;
                            let typeLabelStr = isPub ? '공' : '경';
                            let typeLabel = `<span style="color:${tColor};font-weight:bold;">[${typeLabelStr}]</span>`;

                            let cleanNotes = d.special_notes ? d.special_notes.replace(/0|#|A|해당/gi, '').replace(/,/g, ' ').replace(/\s+/g, ' ').trim() : '';

                            return `
                                <div style="font-family:'Noto Sans KR'; min-width: 220px; padding-bottom: 5px;">
                                    <div style="font-size:1.1rem;">${typeLabel} <b>${d.case_no}</b></div>
                                    <div style="color:gray; font-size:0.85rem; margin-bottom:8px;">${d.property_type} | ${d.address}</div>
                                    <table style="width:100%; font-size:0.9rem; border-collapse: collapse; margin-bottom: 10px;">
                                        <tr><td style="color:gray; padding:3px 0;">감정가</td><td style="text-align:right; font-weight:bold;">${(d.appraisal_price / 100000000).toFixed(1)}억</td></tr>
                                        <tr><td style="color:gray; padding:3px 0;">최저가</td><td style="text-align:right; font-weight:bold; color:${tColor};">${d.min_bid_rate}% (${(d.min_price / 100000000).toFixed(1)}억)</td></tr>
                                        <tr><td style="color:gray; padding:3px 0;">매각기일</td><td style="text-align:right; font-weight:bold;">${d.sale_date ? d.sale_date : '-'}</td></tr>
                                        <tr><td style="color:gray; padding:3px 0;">건물/토지</td><td style="text-align:right;">${d.area_size ? d.area_size.toFixed(1) : 0}평 / ${d.land_size ? d.land_size.toFixed(1) : 0}평</td></tr>
                                        <tr><td style="color:gray; padding:3px 0;">평당최저가</td><td style="text-align:right;">${d.min_price_per_pyeong ? (d.min_price_per_pyeong).toFixed(0) + '만' : '-'}</td></tr>
                                        <tr><td style="color:gray; padding:3px 0;">공시지가</td><td style="text-align:right;">${d.official_land_price && d.official_land_price > 0 ? (d.official_land_price / 100000000).toFixed(2) + '억' : '정보없음'}</td></tr>
                                        ${cleanNotes ? `<tr><td style="color:#ef4444; padding:3px 0; font-weight:bold;">특이사항</td><td style="text-align:right; font-size:0.8rem; color:#ef4444; word-break:keep-all;">${cleanNotes}</td></tr>` : ''}
                                    </table>
                                    <button onclick="window.innerWidth <= 768 ? window.location.href='/?case=${d.case_no}' : (window.opener ? (window.opener.location.href='/?case=${d.case_no}', window.opener.focus()) : window.open('/?case=${d.case_no}', '_blank'))" style="width:100%; background:var(--primary-blue); color:white; border:none; padding:12px 10px; border-radius:6px; cursor:pointer; font-size:1rem; font-weight:bold; touch-action:manipulation;">입지분석 리포트 이동</button>
                                </div>
                            `;
                        });

                        if (!L.Browser.mobile && window.innerWidth > 768) {
                            marker.bindTooltip(function(layer) {
                                let d = layer.auctionData;
                                return `
                                    <div style="font-family:'Noto Sans KR'; font-size:0.85rem; padding: 5px; line-height: 1.4;">
                                        <b>사건번호:</b> ${d.case_no}<br>
                                        <b>종류:</b> ${d.property_type}<br>
                                        <b>감정가:</b> ${(d.appraisal_price / 100000000).toFixed(1)}억<br>
                                        <b>최저가:</b> ${(d.min_price / 100000000).toFixed(1)}억<br>
                                        <b>최저비율:</b> ${d.min_bid_rate}%<br>
                                        <b>매각일:</b> ${d.sale_date ? d.sale_date : '-'}<br>
                                        <b>건물면적:</b> ${d.area_size ? d.area_size.toFixed(1) : 0}평<br>
                                        <b>토지면적:</b> ${d.land_size ? d.land_size.toFixed(1) : 0}평<br>
                                        <b>평당최저가:</b> ${d.min_price_per_pyeong ? (d.min_price_per_pyeong).toFixed(0) + '만' : '-'}<br>
                                        <b>공시지가:</b> ${d.official_land_price && d.official_land_price > 0 ? (d.official_land_price / 100000000).toFixed(2) + '억' : '정보없음'}
                                    </div>
                                `;
                            }, { direction: 'top', className: 'custom-tooltip' });
                        }

                        marker.on('contextmenu', function(e) {
                            marker.openPopup();
                        });

                        marker.addTo(layers.auction);
                    });
                }
            } catch (e) {
                console.error("Auction load error:", e);
            } finally {
                triggerHighlighter();
            }
        }"""

content_lf = content_lf.replace(original_load_auctions, optimized_load_auctions)
print("SUCCESS: loadAuctions function optimized in memory!")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content_lf)

print("SUCCESS: Heavy map optimizations applied successfully to map.html!")
