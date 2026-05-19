
        // 1. Initialize Standard Light Map (Kakao Map Style)
        const map = L.map('map', { zoomControl: false }).setView([37.4979, 127.0276], 13);
        L.control.zoom({ position: 'bottomright' }).addTo(map);

        L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
            maxZoom: 19,
            attribution: '© OpenStreetMap © CARTO'
        }).addTo(map);

        // 2. Layer Groups
        const layers = {
            subway: L.layerGroup().addTo(map),
            univ: L.layerGroup().addTo(map),
            middle: L.layerGroup().addTo(map),
            ind: L.layerGroup().addTo(map),
            bus: L.layerGroup(),
            hagwon: L.layerGroup().addTo(map),
            auction: L.layerGroup().addTo(map)
        };

        function createDotMarker(lat, lng, color, popupHtml, radius = 5) {
            return L.circleMarker([lat, lng], {
                radius: radius,
                fillColor: color,
                color: '#fff',
                weight: 1.5,
                opacity: 1,
                fillOpacity: 0.8
            }).bindPopup(popupHtml);
        }

        // 3. UI Interactions
        function toggleRightPanel() {
            const panel = document.getElementById('right-panel');
            panel.style.display = panel.style.display === 'none' ? 'flex' : 'none';
        }

        document.getElementById('btn-auction').addEventListener('click', function () {
            this.classList.toggle('active');
            loadAuctions();
        });
        document.getElementById('btn-public').addEventListener('click', function () {
            this.classList.toggle('active');
            loadAuctions();
        });

        // 4. Data Loading Logic
        async function fetchInfraData() {
            const bounds = map.getBounds();
            try {
                const res = await fetch(`/api/map/pois?min_lat=${bounds.getSouth()}&max_lat=${bounds.getNorth()}&min_lng=${bounds.getWest()}&max_lng=${bounds.getEast()}`);
                const json = await res.json();

                if (json.status === 'success') {
                    const data = json.data;
                    layers.subway.clearLayers();
                    layers.univ.clearLayers();
                    layers.ind.clearLayers();
                    layers.middle.clearLayers();

                    data.subways.forEach(s => {
                        let radius = parseInt(document.getElementById('buffer-subways').value) || 500;
                        L.circle([s.lat, s.lng], { color: '#10b981', fillColor: '#10b981', fillOpacity: 0.1, radius: radius, weight: 1, dashArray: '4, 4' }).addTo(layers.subway);
                        createDotMarker(s.lat, s.lng, '#10b981', `<b>${s.name}</b><br>${s.line}`).addTo(layers.subway);
                    });

                    // Load Subways (Lines) via separate API or Points if lines fail
                    fetchSubwayLines();

                    data.universities.forEach(u => {
                        let radius = parseInt(document.getElementById('buffer-univs').value) || 500;
                        L.circle([u.lat, u.lng], { color: '#3b82f6', fillColor: '#3b82f6', fillOpacity: 0.1, radius: radius, weight: 1, dashArray: '4, 4' }).addTo(layers.univ);
                        createDotMarker(u.lat, u.lng, '#3b82f6', `<b>${u.name}</b><br>${u.address}`).addTo(layers.univ);
                    });

                    data.industrial_complexes.forEach(i => {
                        let radius = parseInt(document.getElementById('buffer-inds').value) || 500;
                        L.circle([i.lat, i.lng], { color: '#f59e0b', fillColor: '#f59e0b', fillOpacity: 0.1, radius: radius, weight: 1, dashArray: '4, 4' }).addTo(layers.ind);
                        createDotMarker(i.lat, i.lng, '#f59e0b', `<b>${i.name}</b><br>산업단지`).addTo(layers.ind);
                    });

                    data.middle_schools.forEach(m => {
                        let color = '#94a3b8';
                        let label = `특목고 진학률: ${m.special_hs_rate}%`;
                        let markerRadius = 4;
                        if (m.special_hs_rate >= 10) {
                            color = '#f43f5e';
                            markerRadius = 6;
                            let radius = parseInt(document.getElementById('buffer-middles').value) || 500;
                            L.circle([m.lat, m.lng], { color: '#f43f5e', fillColor: '#f43f5e', fillOpacity: 0.1, radius: radius, weight: 1, dashArray: '4, 4' }).addTo(layers.middle);
                        }
                        createDotMarker(m.lat, m.lng, color, `<b>${m.name}</b><br>${label}`, markerRadius).addTo(layers.middle);
                    });
                    
                    if (document.getElementById('toggle-bus').checked && map.getZoom() >= 13 && data.bus_stops) {
                        layers.bus.clearLayers();
                        data.bus_stops.forEach(b => createDotMarker(b.lat, b.lng, '#0ea5e9', `<b>${b.name}</b><br>버스 (${b.city})`, 3).addTo(layers.bus));
                    }
                }
            } catch (err) { console.error(err); }
        }

        async function fetchSubwayLines() {
            try {
                const res = await fetch('/api/map/subway_lines');
                const json = await res.json();
                if (json.status === 'success') {
                    layers.subway.clearLayers();
                    json.data.forEach(line => {
                        let coords = JSON.parse(line.coordinates_json);
                        L.polyline(coords, { color: '#10b981', weight: 4, opacity: 0.8 })
                            .bindPopup(`<b>${line.line}</b>`).addTo(layers.subway);
                        // Start/End points
                        if (coords.length > 0) {
                            createDotMarker(coords[0][0], coords[0][1], '#10b981', `<b>${line.line} 기점</b>`).addTo(layers.subway);
                            createDotMarker(coords[coords.length - 1][0], coords[coords.length - 1][1], '#10b981', `<b>${line.line} 종점</b>`).addTo(layers.subway);
                        }
                    });
                }
            } catch (err) { console.error(err); }
        }

        async function loadBusStops() {
            // Deprecated, handled in fetchInfraData
        }

        async function fetchHagwonPolygons() {
            try {
                const res = await fetch('/api/map/hagwon_polygons');
                const json = await res.json();
                if (json.status === 'success') {
                    layers.hagwon.clearLayers();
                    json.data.forEach(poly => {
                        let coords = JSON.parse(poly.coordinates_json);
                        let count = poly.count;
                        let intensity = Math.min(count / 200, 1); // Cap at 200 for spread

                        // 10 steps from White to Red
                        let step = Math.ceil(intensity * 10);
                        if (step < 1) step = 1;
                        if (step > 10) step = 10;

                        let color;
                        switch (step) {
                            case 1: color = '#fff5f5'; break;
                            case 2: color = '#ffe3e3'; break;
                            case 3: color = '#ffc9c9'; break;
                            case 4: color = '#ffa8a8'; break;
                            case 5: color = '#ff8787'; break;
                            case 6: color = '#ff6b6b'; break;
                            case 7: color = '#fa5252'; break;
                            case 8: color = '#f03e3e'; break;
                            case 9: color = '#e03131'; break;
                            case 10: color = '#c92a2a'; break;
                        }

                        let opacity = 0.4 + (intensity * 0.4); // 0.4 to 0.8 opacity

                        L.polygon(coords, {
                            color: color,
                            fillColor: color,
                            fillOpacity: opacity,
                            weight: 2
                        }).bindPopup(`<b>학원 밀집가</b><br>반경 200m 내 ${poly.count}개 학원 밀집`).addTo(layers.hagwon);
                    });
                }
            } catch (err) { console.error(err); }
        }

        async function loadAuctions() {
            layers.auction.clearLayers();
            function buildAuctionUrl(basePath) {
                const bounds = map.getBounds();
                const isAuctionActive = document.getElementById('btn-auction').classList.contains('active');
                const isPublicActive = document.getElementById('btn-public').classList.contains('active');

                const checkedTypes = Array.from(document.querySelectorAll('.checkbox-item input:checked')).map(cb => cb.value);
                const rateLimit = document.getElementById('rate-slider').value;

                if (!isAuctionActive && !isPublicActive) return null;

                let saleType = '전체';
                if (isAuctionActive && !isPublicActive) saleType = '경매';
                if (!isAuctionActive && isPublicActive) saleType = '공매';

                let url = `${basePath}?min_lat=${bounds.getSouth()}&max_lat=${bounds.getNorth()}&min_lng=${bounds.getWest()}&max_lng=${bounds.getEast()}`;
                
                const checkedRegions = Array.from(document.querySelectorAll('.region-checkbox:checked')).map(cb => cb.value);
                if (checkedRegions.length > 0) url += `&regions=${checkedRegions.join(',')}`;
                
                if (checkedTypes.length > 0) url += `&property_types=${checkedTypes.join(',')}`;
                url += `&min_rate=${rateLimit}&sale_type=${saleType}`;

                const minArea = document.getElementById('min-area').value;
                const maxArea = document.getElementById('max-area').value;

                // Read distance filters from the Left Panel
                const useSubwayDist = document.getElementById('toggle-subways').checked;
                const useUnivDist = document.getElementById('toggle-univs').checked;
                const useIndDist = document.getElementById('toggle-inds').checked;
                const subwayDist = document.getElementById('buffer-subways').value;
                const univDist = document.getElementById('buffer-univs').value;
                const indDist = document.getElementById('buffer-inds').value;

                const reqElite = document.getElementById('req-elite-school') ? document.getElementById('req-elite-school').checked : false;
                const minHouseholds = document.getElementById('min-households') ? document.getElementById('min-households').value : '';

                if (minArea) url += `&min_area=${minArea}`;
                if (maxArea) url += `&max_area=${maxArea}`;
                if (useSubwayDist && subwayDist) url += `&subway_dist_max=${subwayDist}`;
                if (useUnivDist && univDist) url += `&univ_dist_max=${univDist}`;
                if (useIndDist && indDist) url += `&ind_dist_max=${indDist}`;
                if (reqElite) url += `&req_elite_school=true`;
                if (minHouseholds) url += `&min_households=${minHouseholds}`;

                return url;
            }

            const url = buildAuctionUrl('/api/map/auctions');
                if (!url) return;

                try {
                    const res = await fetch(url);
                    const json = await res.json();

                    if (json.status === 'success') {
                        json.data.forEach(item => {
                            let typeLabel = item.sale_type.includes('공매') ? '<span style="color:var(--color-auction);font-weight:bold;">[공매]</span>' : '<span style="color:var(--color-auction);font-weight:bold;">[경매]</span>';
                            let html = `
                            <div style="font-family:'Noto Sans KR'; min-width: 180px;">
                                <div style="font-size:1.1rem;">${typeLabel} <b>${item.case_no}</b></div>
                                <div style="color:gray; font-size:0.85rem; margin-bottom:8px;">${item.property_type} | ${item.address}</div>
                                <table style="width:100%; font-size:0.9rem; border-collapse: collapse;">
                                    <tr><td style="color:gray; padding:2px 0;">감정가</td><td style="text-align:right; font-weight:bold;">${(item.appraisal_price / 100000000).toFixed(1)}억</td></tr>
                                    <tr><td style="color:gray; padding:2px 0;">최저가</td><td style="text-align:right; font-weight:bold; color:var(--color-auction);">${item.min_bid_rate}% (${(item.min_price / 100000000).toFixed(1)}억)</td></tr>
                                </table>
                                <button onclick="window.open('/?case=${item.case_no}', '_blank')" style="width:100%; margin-top:10px; background:var(--primary-blue); color:white; border:none; padding:8px; border-radius:4px; cursor:pointer;">권리분석 리포트 보기</button>
                            </div>
                        `;

                            let tooltipHtml = `
                            <div style="font-family:'Noto Sans KR'; font-size:0.85rem; padding: 5px; line-height: 1.4;">
                                <b>사건번호:</b> ${item.case_no}<br>
                                <b>종류:</b> ${item.property_type}<br>
                                <b>최저가율:</b> ${item.min_bid_rate}%<br>
                                <b>건물평수:</b> ${item.area_size ? item.area_size.toFixed(1) : 0}평<br>
                                <b>대지평수:</b> ${item.land_size ? item.land_size.toFixed(1) : 0}평<br>
                                <b>최저가 기준 평당가:</b> ${item.min_price_per_pyeong ? (item.min_price_per_pyeong / 10000).toFixed(0) + '만' : '-'}
                            </div>
                        `;

                            let color = 'var(--color-auction)';
                            L.circleMarker([item.lat, item.lng], {
                                radius: 6, fillColor: color, color: '#fff', weight: 2, opacity: 1, fillOpacity: 1
                            }).bindPopup(html).bindTooltip(tooltipHtml, { direction: 'top', className: 'custom-tooltip' }).addTo(layers.auction);
                        });
                    }
                } catch (e) {
                    console.error("Auction load error:", e);
                }
            }

            // Toggles mapping
            const toggleMap = {
                'toggle-subways': layers.subway,
                'toggle-univs': layers.univ,
                'toggle-middles': layers.middle,
                'toggle-inds': layers.ind,
                'toggle-hagwons': layers.hagwon
            };

            Object.keys(toggleMap).forEach(id => {
                document.getElementById(id).addEventListener('change', (e) => {
                    e.target.checked ? map.addLayer(toggleMap[id]) : map.removeLayer(toggleMap[id]);
                });
            });

            document.getElementById('toggle-bus').addEventListener('change', (e) => {
                e.target.checked ? (map.addLayer(layers.bus), loadBusStops()) : map.removeLayer(layers.bus);
            });

            // Fetch infra when map moves
            map.on('moveend', fetchInfraData);

            // Load initial data
            Promise.all([
                fetchInfraData(),
                fetchHagwonPolygons(),
                loadAuctions()
            ]).finally(() => {
                const loadingOverlay = document.getElementById('loading');
                if (loadingOverlay) loadingOverlay.style.display = 'none';
            });

            // Right panel fetch button
            document.querySelector('#right-panel .btn-primary').addEventListener('click', loadAuctions);

            function exportToExcel() {
                const url = buildAuctionUrl('/api/map/auctions/export');
                if (url) {
                    window.location.href = url;
                } else {
                    alert('경공매 표시를 먼저 활성화해주세요.');
                }
            }
    