
// Script block 2


// 2. 통계 분석 모달 (Statistical Analysis)
function showStatisticsModal() {
    let totalCount = 0;
    let totalAppraised = 0;
    let totalMinPrice = 0;
    let typeCounts = {};
    let currentBounds = map.getBounds();

    layers.auction.eachLayer(function(marker) {
        if (currentBounds.contains(marker.getLatLng())) {
            totalCount++;
            let d = marker.auctionData;
            if(d) {
                let pt = d.property_type || '기타';
                typeCounts[pt] = (typeCounts[pt] || 0) + 1;
                totalAppraised += (d.appraisal_price || 0);
                totalMinPrice += (d.min_price || 0);
            }
        }
    });

    if(totalCount === 0) {
        alert('현재 화면에 표시된 경공매 물건이 없습니다.');
        return;
    }

    let avgAppraised = (totalAppraised / totalCount / 100000000).toFixed(2) + '억 원';
    let avgMinPrice = (totalMinPrice / totalCount / 100000000).toFixed(2) + '억 원';
    let avgRate = ((totalMinPrice / totalAppraised) * 100).toFixed(1) + '%';

    let typeHtml = '';
    for(let t in typeCounts) {
        typeHtml += '<div style="display:flex; justify-content:space-between; padding:5px 0; border-bottom:1px solid rgba(255,255,255,0.1);">' +
            '<span>' + t + '</span> <span style="color:var(--neon-blue); font-weight:bold;">' + typeCounts[t] + '건</span>' +
        '</div>';
    }

    let modalHtml = 
        '<div id="gis-stat-modal" style="position:fixed; top:50%; left:50%; transform:translate(-50%, -50%); ' +
            'background:rgba(10,12,16,0.95); border:1px solid var(--primary-blue); border-radius:12px; ' +
            'padding:25px; z-index:9999; min-width:320px; box-shadow:0 0 30px rgba(0,238,255,0.2); color:white; font-family: \'Malgun Gothic\', sans-serif;">' +
            
            '<h3 style="color: var(--primary-blue); margin-top:0; border-bottom:2px solid var(--primary-blue); padding-bottom:10px;">' +
                '<i class="fa-solid fa-chart-pie"></i> 화면 내 통계 분석' +
            '</h3>' +
            
            '<div style="margin: 20px 0; font-size:1.1rem; line-height: 1.6;">' +
                '<div style="display:flex; justify-content:space-between;"><span>조회 물건 수:</span> <strong>' + totalCount + '건</strong></div>' +
                '<div style="display:flex; justify-content:space-between;"><span>평균 감정가:</span> <strong>' + avgAppraised + '</strong></div>' +
                '<div style="display:flex; justify-content:space-between;"><span>평균 최저가:</span> <strong>' + avgMinPrice + '</strong></div>' +
                '<div style="display:flex; justify-content:space-between; color:var(--danger);"><span>가중 평균 최저가율:</span> <strong>' + avgRate + '</strong></div>' +
            '</div>' +
            
            '<h4 style="margin-bottom:10px; color:#aaa;">[용도별 비중]</h4>' +
            '<div style="max-height:150px; overflow-y:auto;">' +
                typeHtml +
            '</div>' +
            
            '<div style="text-align:center; margin-top:25px;">' +
                '<button onclick="document.getElementById(\'gis-stat-modal\').remove()" ' +
                    'style="background:var(--primary-blue); color:#000; border:none; padding:10px 25px; border-radius:8px; font-weight:bold; cursor:pointer;">' +
                    '닫기' +
                '</button>' +
            '</div>' +
        '</div>';

    let existing = document.getElementById('gis-stat-modal');
    if(existing) existing.remove();
    document.body.insertAdjacentHTML('beforeend', modalHtml);
}


// Helper functions for polygon intersection
function getActivePolygonLayers() {
    let activeLayers = [];
    if (map.hasLayer(layers.commercial)) activeLayers.push(layers.commercial);
    if (map.hasLayer(layers.hagwon)) activeLayers.push(layers.hagwon);
    if (map.hasLayer(layers.dev2)) activeLayers.push(layers.dev2);
    if (map.hasLayer(layers.oldBuildings)) activeLayers.push(layers.oldBuildings);
    return activeLayers;
}

function isPointInPolygonGeoJSON(pt, polygonCoords) {
    var x = pt[0], y = pt[1];
    var inside = false;
    for (var i = 0, j = polygonCoords.length - 1; i < polygonCoords.length; j = i++) {
        var xi = polygonCoords[i][0], yi = polygonCoords[i][1];
        var xj = polygonCoords[j][0], yj = polygonCoords[j][1];
        var intersect = ((yi > y) != (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi);
        if (intersect) inside = !inside;
    }
    return inside;
}

function isPointInLayer(ptLngLat, layerGroup) {
    let inside = false;
    layerGroup.eachLayer(function(l) {
        if (inside) return; 
        if (l.feature && l.feature.geometry) {
            let geom = l.feature.geometry;
            if (geom.type === 'Polygon') {
                if (isPointInPolygonGeoJSON(ptLngLat, geom.coordinates[0])) inside = true;
            } else if (geom.type === 'MultiPolygon') {
                for (let i=0; i<geom.coordinates.length; i++) {
                    if (isPointInPolygonGeoJSON(ptLngLat, geom.coordinates[i][0])) {
                        inside = true;
                        break;
                    }
                }
            }
        }
    });
    return inside;
}

// 3. 형광펜 데이터 (Highlighter)
let isHighlighterOn = false;
function toggleHighlighter() {
    isHighlighterOn = !isHighlighterOn;
    const btn = document.getElementById('btn-highlighter');
    if (isHighlighterOn) {
        let activeLayers = getActivePolygonLayers();
        if (activeLayers.length === 0) {
            alert('활성화된 다각형 영역(상권, 학원가, 지구단위계획구역, 노후건축물 등)이 없습니다. 왼쪽 레이어 창에서 먼저 영역을 켜주세요.');
            isHighlighterOn = false;
            return;
        }

        btn.querySelector('i').style.color = '#bd00ff';
        btn.querySelector('i').style.textShadow = '0 0 15px #bd00ff';
        
        let highlightCount = 0;
        layers.auction.eachLayer(function(marker) {
            let d = marker.auctionData;
            if(!marker.originalStyle) {
                marker.originalStyle = {
                    radius: marker.options.radius,
                    color: marker.options.color,
                    fillColor: marker.options.fillColor,
                    weight: marker.options.weight,
                    opacity: marker.options.opacity,
                    fillOpacity: marker.options.fillOpacity
                };
            }
            
            let pt = [d.lng, d.lat];
            let overlapsAll = true;
            for (let i=0; i<activeLayers.length; i++) {
                if (!isPointInLayer(pt, activeLayers[i])) {
                    overlapsAll = false;
                    break;
                }
            }
            
            if(overlapsAll) {
                highlightCount++;
                marker.setStyle({
                    radius: 10,
                    color: '#bd00ff',
                    weight: 4,
                    fillColor: '#bd00ff',
                    fillOpacity: 0.8,
                    opacity: 1
                });
                marker.bringToFront();
            } else {
                marker.setStyle({
                    opacity: 0.1,
                    fillOpacity: 0.1
                });
            }
        });
        alert('형광펜 ON: 중복 영역(선택한 켜져있는 영역 모두 포함) 내 경공매 물건 ' + highlightCount + '건이 집중 강조됩니다.');
    } else {
        btn.querySelector('i').style.color = '';
        btn.querySelector('i').style.textShadow = '';
        
        layers.auction.eachLayer(function(marker) {
            if(marker.originalStyle) {
                marker.setStyle(marker.originalStyle);
                delete marker.originalStyle;
            }
        });
    }
}



// --- GIS 고도화 기능 ---

// 1. 객체 선택 모드 (Select Object)
let isSelectMode = false;
function toggleSelectMode() {
    isSelectMode = !isSelectMode;
    const btn = document.getElementById('btn-select-object');
    if (isSelectMode) {
        btn.querySelector('i').style.color = 'var(--primary-blue)';
        btn.querySelector('i').style.textShadow = '0 0 10px var(--primary-blue)';
        document.getElementById('map').style.cursor = 'crosshair';
        alert('객체 선택 모드 ON: 지도 상의 경공매 마커를 클릭하면 간편 상세 정보가 표시됩니다.');
        
        layers.auction.eachLayer(function(marker) {
            marker.on('click.select', function(e) {
                if(isSelectMode && marker.auctionData) {
                    let d = marker.auctionData;
                    alert('[선택된 경공매 객체]\n사건번호: ' + d.case_no + '\n종류: ' + d.property_type + '\n감정가: ' + (d.appraisal_price/100000000).toFixed(1) + '억\n최저가: ' + (d.min_price/100000000).toFixed(1) + '억 (' + d.min_bid_rate + '%)');
                }
            });
        });
    } else {
        btn.querySelector('i').style.color = '';
        btn.querySelector('i').style.textShadow = '';
        document.getElementById('map').style.cursor = '';
        
        layers.auction.eachLayer(function(marker) {
            marker.off('click.select');
        });
    }
}


// Script block 3

        // 1. Initialize Standard Light Map (Kakao Map Style)
        const map = L.map('map', { zoomControl: false, preferCanvas: true }).setView([37.4979, 127.0276], 13);
        L.control.zoom({ position: 'bottomright' }).addTo(map);

        // Make popups draggable so users can see the map underneath
        map.on('popupopen', function(e) {
            var popupWrapper = e.popup._wrapper.parentNode;
            var pos, dragStartPos;
            
            // Allow clicking through without closing popup if dragged
            popupWrapper.style.cursor = 'move';
            
            var onMouseDown = function(event) {
                if(event.target.tagName.toLowerCase() === 'button' || event.target.tagName.toLowerCase() === 'a') return;
                var evt = event.type.startsWith('touch') ? event.touches[0] : event;
                pos = { x: evt.clientX, y: evt.clientY };
                
                dragStartPos = {
                    left: parseInt(popupWrapper.style.marginLeft || 0, 10),
                    top: parseInt(popupWrapper.style.marginTop || 0, 10)
                };
                
                document.addEventListener('mousemove', onMouseMove);
                document.addEventListener('mouseup', onMouseUp);
                document.addEventListener('touchmove', onMouseMove, {passive: false});
                document.addEventListener('touchend', onMouseUp);
            };

            var onMouseMove = function(event) {
                if(event.type.startsWith('touch') && event.cancelable) event.preventDefault();
                var evt = event.type.startsWith('touch') ? event.touches[0] : event;
                var dx = evt.clientX - pos.x;
                var dy = evt.clientY - pos.y;
                
                popupWrapper.style.marginLeft = (dragStartPos.left + dx) + 'px';
                popupWrapper.style.marginTop = (dragStartPos.top + dy) + 'px';
            };

            var onMouseUp = function() {
                document.removeEventListener('mousemove', onMouseMove);
                document.removeEventListener('mouseup', onMouseUp);
                document.removeEventListener('touchmove', onMouseMove);
                document.removeEventListener('touchend', onMouseUp);
            };

            popupWrapper.addEventListener('mousedown', onMouseDown);
            popupWrapper.addEventListener('touchstart', onMouseDown, {passive: false});
            
            map.once('popupclose', function() {
                popupWrapper.removeEventListener('mousedown', onMouseDown);
                popupWrapper.removeEventListener('touchstart', onMouseDown);
                onMouseUp();
                popupWrapper.style.marginLeft = '0px';
                popupWrapper.style.marginTop = '0px';
            });
        });

        L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
            maxZoom: 19,
            attribution: '짤 OpenStreetMap 짤 CARTO'
        }).addTo(map);

        // 2. Map Layers Initialization
        map.createPane('auctionPane');
        map.getPane('auctionPane').style.zIndex = 650;

        // 2. Layer Groups
        const layers = {
            subway: L.layerGroup().addTo(map),
            subwayLine: L.layerGroup().addTo(map),
            univ: L.layerGroup(),
            middle: L.layerGroup(),
            ind: L.layerGroup(),
            bus: L.layerGroup(),
            commercial: L.layerGroup(),
            hagwon: L.layerGroup(),
            dev2: L.layerGroup(),
            popHeatmap: L.layerGroup(),
            oldBuildings: L.layerGroup(),
            auction: L.layerGroup().addTo(map)
        };

        function createDotMarker(lat, lng, color, popupHtml, radius = 5) {
            return L.circleMarker([lat, lng], {
                radius: radius,
                fillColor: color,
                color: '#fff',
                weight: 1.5,
                opacity: 1,
                fillOpacity: 1
            }).bindPopup(popupHtml);
        }

                const SUBWAY_COLORS = {
            '1호선': '#0052A4', '2호선': '#00A84D', '3호선': '#EF7C1C', '4호선': '#00A4E3',
            '5호선': '#996CAC', '6호선': '#CD7C2F', '7호선': '#747F00', '8호선': '#E6186C',
            '9호선': '#BDB092', '경의중앙선': '#77C4A3', '수인분당선': '#FABE00', '경춘선': '#0C8E72',
            '신분당선': '#D4003B', '우이신설': '#B0CE18', '경강선': '#003499', 
            '김포골드': '#A17E46', '서해선': '#8FC31F', '공항철도': '#0090D2', '인천2호선': '#ED8B00',
            '인천1호선': '#7CA8D5', '용인에버': '#56C343', '신림선': '#6789CA'
        };

        function getGlobalLineColor(lineName) {
            if (!lineName) return '#94a3b8';
            for (let key in SUBWAY_COLORS) {
                if (lineName.includes(key)) return SUBWAY_COLORS[key];
            }
            return '#94a3b8'; // default
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
                    layers.commercial.clearLayers();

                    setTimeout(() => {
                        if (data.subways) {
                            data.subways.forEach(s => {
                                let radius = parseInt(document.getElementById('buffer-subways').value) || 500;
                                let color = getGlobalLineColor(s.line);
                                L.circle([s.lat, s.lng], { color: color, fillColor: color, fillOpacity: 0.1, radius: radius, weight: 1, dashArray: '4, 4' }).addTo(layers.subway);
                                createDotMarker(s.lat, s.lng, color, `<b>${s.name}</b><br>${s.line}`).addTo(layers.subway);
                            });
                        }
                    }, 0);

                    setTimeout(() => {
                        if (data.universities) {
                            data.universities.forEach(u => {
                                let radius = parseInt(document.getElementById('buffer-univs').value) || 500;
                                L.circle([u.lat, u.lng], { color: '#3b82f6', fillColor: '#3b82f6', fillOpacity: 0.1, radius: radius, weight: 1, dashArray: '4, 4' }).addTo(layers.univ);
                                createDotMarker(u.lat, u.lng, '#3b82f6', `<b>${u.name}</b><br>대학교`).addTo(layers.univ);
                            });
                        }
                    }, 50);

                    setTimeout(() => {
                        if (data.industrial_complexes) {
                            data.industrial_complexes.forEach(i => {
                                let radius = parseInt(document.getElementById('buffer-inds').value) || 500;
                                L.circle([i.lat, i.lng], { color: '#f59e0b', fillColor: '#f59e0b', fillOpacity: 0.1, radius: radius, weight: 1, dashArray: '4, 4' }).addTo(layers.ind);
                                createDotMarker(i.lat, i.lng, '#f59e0b', `<b>${i.name}</b><br>산업단지`).addTo(layers.ind);
                            });
                        }
                    }, 100);

                    setTimeout(() => {
                        if (data.middle_schools) {
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
                    }, 150);
                    
                    if (document.getElementById('toggle-bus').checked && map.getZoom() >= 13 && data.bus_stops) {
                        layers.bus.clearLayers();
                        data.bus_stops.forEach(b => createDotMarker(b.lat, b.lng, '#0ea5e9', `<b>${b.name}</b><br>踰꾩뒪 (${b.city})`, 3).addTo(layers.bus));
                    }
                    if (document.getElementById('toggle-commercial').checked && data.commercial_areas) {
                        layers.commercial.clearLayers();
                        
                        // ?멸뎄??諛곗뿴 ?앹꽦 諛??뺣젹 (諛깅텇??怨꾩궛??
                        const pops = data.commercial_areas.map(c => c.population || 0).sort((a, b) => a - b);
                        
                        // ?곴텒 ?대쫫(name)蹂??멸뎄??留ㅽ븨
                        const popData = {};
                        data.commercial_areas.forEach(c => {
                            popData[c.name] = c.population || 0;
                        });

                        const getTierStyle = (pop) => {
                            if (pop === 0 || pops.length === 0) return null;
                            
                            // ?댁쭊 ?먯깋 ???媛꾨떒???꾩튂 李얘린 (?곗씠?곌? 留롮? ?딆쑝誘濡?
                            const idx = pops.findIndex(p => p >= pop);
                            const percentile = (idx + 1) / pops.length;
                            const tier = Math.ceil(percentile * 10) || 1; // 1 ~ 10 ?④퀎
                            
                            // 3?④퀎 이하???뚮뜑留곹븯吏 ?딆쓬
                            if (tier <= 3) return null;
                            
                            // 吏꾪븳 ?뚮???10?④퀎) -> ?섏???1?④퀎)
                            const colors = {
                                10: '#08306b',
                                9: '#08519c',
                                8: '#2171b5',
                                7: '#4292c6',
                                6: '#6baed6',
                                5: '#9ecae1',
                                4: '#c6dbef'
                            };
                            
                            return {
                                color: colors[tier] || '#ffffff', // ?뚮몢由??됱긽 (?ㅼ젣濡쒕뒗 weight: 0?쇰줈 ?덈낫??
                                fillColor: colors[tier] || '#ffffff',
                                fillOpacity: 0.5,
                                weight: 0 // ?뚮몢由??놁쓬
                            };
                        };

                        if (!window.commercialGeoJsonLayer) {
                            fetch('/data/seoul_commercial.geojson')
                                .then(res => res.json())
                                .then(geojsonData => {
                                    window.commercialGeoJsonLayer = L.geoJSON(geojsonData, {
                                        filter: function(feature) {
                                            const name = feature.properties.TRDAR_CD_N;
                                            const pop = popData[name] || 0;
                                            const style = getTierStyle(pop);
                                            return style !== null; // 3?④퀎 이하??필터留???젣)
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
                                    window.commercialGeoJsonLayer.addTo(layers.commercial);
                                });
                        } else {
                            // ?대? 濡쒕뱶??寃쎌슦 레이어?ш뎄??(filter ?곸슜???꾪빐 clear ???ㅼ떆 濡쒕뱶)
                            // L.geoJSON? 珥덇린???쒖뿉留?filter媛 ?곸슜?섎?濡??곗씠?곕? ?좎??섍퀬 ?ъ깮?깊빀?덈떎.
                            fetch('/data/seoul_commercial.geojson')
                                .then(res => res.json())
                                .then(geojsonData => {
                                    window.commercialGeoJsonLayer = L.geoJSON(geojsonData, {
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
                                    window.commercialGeoJsonLayer.addTo(layers.commercial);
                                });
                        }
                    }
                }
            } catch (err) { console.error(err); }
        }

        async function fetchSubwayLines() {
            try {
                const res = await fetch('/api/map/subway_lines');
                const json = await res.json();
                
                if (json.status === 'success') {
                    layers.subwayLine.clearLayers();
                    json.data.forEach(line => {
                        let coords = JSON.parse(line.coordinates_json);
                        let color = getGlobalLineColor(line.line);
                        L.polyline(coords, { color: color, weight: 4, opacity: 0.8 })
                            .bindPopup(`<b>${line.line}</b>`).addTo(layers.subwayLine);
                        // Start/End points
                        if (coords.length > 0) {
                            createDotMarker(coords[0][0], coords[0][1], color, `<b>${line.line} 기점</b>`).addTo(layers.subwayLine);
                            createDotMarker(coords[coords.length - 1][0], coords[coords.length - 1][1], color, `<b>${line.line} 종점</b>`).addTo(layers.subwayLine);
                        }
                    });
                }
            } catch (err) { console.error(err); }
        }

        async function loadBusStops() {
            // Deprecated, handled in fetchInfraData
        }

        async function fetchHagwonPolygons() {
            if (!document.getElementById('toggle-hagwons').checked) return;
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

                        L.polygon(coords, {
                            color: color,
                            fillColor: color,
                            fillOpacity: 0.5,
                            opacity: 0.5,
                            weight: 2
                        }).bindPopup(`<b>학원 밀집가</b><br>반경 200m 내 ${poly.count}개 학원 밀집`).addTo(layers.hagwon);
                    });
                }
            } catch (err) { console.error(err); }
        }

        async function fetchDistrictUnits() {
            if (!document.getElementById('toggle-dev2').checked) return;
            const bounds = map.getBounds();
            try {
                const res = await fetch(`/api/map/district_units?min_lat=${bounds.getSouth()}&max_lat=${bounds.getNorth()}&min_lng=${bounds.getWest()}&max_lng=${bounds.getEast()}`);
                const json = await res.json();
                if (json.status === 'success') {
                    layers.dev2.clearLayers();
                    json.data.forEach(item => {
                        let geojson = JSON.parse(item.geojson);
                        L.geoJSON(geojson, {
                            style: {
                                color: '#4ade80', // 연한 초록색                                fillColor: '#4ade80',
                                fillOpacity: 0.25,
                                weight: 2,
                                dashArray: '5, 5'
                            }
                        }).bindPopup(`<b>吏援щ떒?꾧퀎?띻뎄??/b><br>${item.name}`).addTo(layers.dev2);
                    });
                }
            } catch (err) { console.error(err); }
        }

        async function fetchPopulationHeatmap() {
            if (!document.getElementById('toggle-heatmap').checked) return;
            const bounds = map.getBounds();
            try {
                const res = await fetch(`/api/map/population_heatmap?min_lat=${bounds.getSouth()}&max_lat=${bounds.getNorth()}&min_lng=${bounds.getWest()}&max_lng=${bounds.getEast()}`);
                const json = await res.json();
                if (json.status === 'success') {
                    layers.popHeatmap.clearLayers();
                    
                    let heatData = [];
                    let maxPop = 0;
                    json.data.forEach(item => {
                        if (item.avg_population > maxPop) maxPop = item.avg_population;
                        heatData.push([item.lat, item.lng, item.avg_population]);
                    });

                    if (heatData.length > 0) {
                        const heatLayer = L.heatLayer(heatData, {
                            radius: 40,
                            blur: 30,
                            maxZoom: 15,
                            max: 9000,
                            gradient: {
                                0.1: '#fee5d9', 
                                0.2: '#fcbba1', 
                                0.3: '#fc9272', 
                                0.4: '#fb6a4a', 
                                0.5: '#ef3b2c', 
                                0.6: '#cb181d', 
                                0.7: '#a50f15', 
                                0.8: '#85000e', 
                                0.9: '#67000d', 
                                1.0: '#4a000a'  // Dark Red
                            }
                        });
                        heatLayer.addTo(layers.popHeatmap);
                        if (heatLayer._canvas) {
                            heatLayer._canvas.style.opacity = '0.5'; // 50% transparency for the entire heatmap
                        }
                    }
                }
            } catch (err) { console.error("Heatmap fetch error:", err); }
        }
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

            const reqElite = document.getElementById('toggle-middles') ? document.getElementById('toggle-middles').checked : false;
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

        async function loadAuctions() {
            const zoomWarning = document.getElementById('zoom-warning');
            
            if (map.getZoom() < 13) {
                layers.auction.clearLayers();
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

            layers.auction.clearLayers();

            const url = buildAuctionUrl('/api/map/auctions');
            if (!url) return;

            try {
                const res = await fetch(url);
                const json = await res.json();

                if (json.status === 'success') {
                    json.data.forEach(item => {
                        let isPublic = item.sale_type.includes('공매');
                        let typeColor = isPublic ? '#3b82f6' : '#ef4444';
                        
                        let marker = L.circleMarker([item.lat, item.lng], {
                            radius: 6, fillColor: typeColor, color: '#fff', weight: 2, opacity: 1, fillOpacity: 1,
                            pane: 'auctionPane'
                        });
                        marker.auctionData = item;
                        marker.isPublic = isPublic;
                        marker.typeColor = typeColor;

                        marker.bindPopup(function(layer) {
                            let d = layer.auctionData;
                            let isPub = layer.isPublic;
                            let tColor = layer.typeColor;
                            let typeLabelStr = isPub ? '공매' : '경매';
                            let typeLabel = `<span style="color:${tColor};font-weight:bold;">[${typeLabelStr}]</span>`;
                            return `
                                <div style="font-family:'Noto Sans KR'; min-width: 220px; padding-bottom: 5px;">
                                    <div style="font-size:1.1rem;">${typeLabel} <b>${d.case_no}</b></div>
                                    <div style="color:gray; font-size:0.85rem; margin-bottom:8px;">${d.property_type} | ${d.address}</div>
                                    <table style="width:100%; font-size:0.9rem; border-collapse: collapse; margin-bottom: 10px;">
                                        <tr><td style="color:gray; padding:3px 0;">감정가</td><td style="text-align:right; font-weight:bold;">${(d.appraisal_price / 100000000).toFixed(1)}억</td></tr>
                                        <tr><td style="color:gray; padding:3px 0;">최저가</td><td style="text-align:right; font-weight:bold; color:${tColor};">${d.min_bid_rate}% (${(d.min_price / 100000000).toFixed(1)}억)</td></tr>
                                        <tr><td style="color:gray; padding:3px 0;">건물/대지</td><td style="text-align:right;">${d.area_size ? d.area_size.toFixed(1) : 0}평 / ${d.land_size ? d.land_size.toFixed(1) : 0}평</td></tr>
                                        <tr><td style="color:gray; padding:3px 0;">최저가 평당가</td><td style="text-align:right;">${d.min_price_per_pyeong ? (d.min_price_per_pyeong).toFixed(0) + '만원' : '-'}</td></tr>
                                    </table>
                                    <button onclick="window.innerWidth <= 768 ? window.location.href='/?case=${d.case_no}' : (window.opener ? (window.opener.location.href='/?case=${d.case_no}', window.opener.focus()) : window.open('/?case=${d.case_no}', '_blank'))" style="width:100%; background:var(--primary-blue); color:white; border:none; padding:12px 10px; border-radius:6px; cursor:pointer; font-size:1rem; font-weight:bold; touch-action:manipulation;">권리분석 리포트 보기</button>
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
                                        <b>최저가율:</b> ${d.min_bid_rate}%<br>
                                        <b>건물평수:</b> ${d.area_size ? d.area_size.toFixed(1) : 0}평<br>
                                        <b>대지평수:</b> ${d.land_size ? d.land_size.toFixed(1) : 0}평<br>
                                        <b>최저가 기준 평당가:</b> ${d.min_price_per_pyeong ? (d.min_price_per_pyeong).toFixed(0) + '만원' : '-'}
                                    </div>
                                `;
                            }, { direction: 'top', className: 'custom-tooltip' });
                        }
                        
                        // 오른쪽 클릭 시 고정 팝업 열기
                        marker.on('contextmenu', function(e) {
                            marker.openPopup();
                        });
                        
                        marker.addTo(layers.auction);
                    });
                }
            } catch (e) {
                console.error("Auction load error:", e);
            }
            // Toggles mapping
            const toggleMap = {
                'toggle-subways': [layers.subway, layers.subwayLine],
                'toggle-univs': [layers.univ],
                'toggle-middles': [layers.middle],
                'toggle-inds': [layers.ind],
                'toggle-commercial': [layers.commercial],
                'toggle-hagwons': [layers.hagwon],
                'toggle-dev2': [layers.dev2],
                'toggle-heatmap': [layers.popHeatmap]
            };

            Object.keys(toggleMap).forEach(id => {
                document.getElementById(id).addEventListener('change', (e) => {
                    const layerList = toggleMap[id];
                    if (e.target.checked) {
                        layerList.forEach(l => map.addLayer(l));
                    } else {
                        layerList.forEach(l => map.removeLayer(l));
                    }
                });
            });

            document.getElementById('toggle-bus').addEventListener('change', (e) => {
                e.target.checked ? (map.addLayer(layers.bus), loadBusStops()) : map.removeLayer(layers.bus);
            });
            document.getElementById('toggle-commercial').addEventListener('change', (e) => {
                e.target.checked ? map.addLayer(layers.commercial) : map.removeLayer(layers.commercial);
                if(e.target.checked) fetchInfraData();
            });

            // Fetch infra when map moves
            let moveEndTimeout;
            map.on('moveend', () => {
                clearTimeout(moveEndTimeout);
                moveEndTimeout = setTimeout(() => {
                    fetchInfraData();
                    fetchDistrictUnits();
                    fetchPopulationHeatmap();
                    loadAuctions();
                }, 400); // 400ms debounce
            });

            document.getElementById('toggle-hagwons').addEventListener('change', (e) => {
                if (e.target.checked && layers.hagwon.getLayers().length === 0) {
                    fetchHagwonPolygons();
                }
            });

            document.getElementById('toggle-heatmap').addEventListener('change', (e) => {
                if (e.target.checked) {
                    fetchPopulationHeatmap();
                }
            });

            document.getElementById('toggle-old-buildings').addEventListener('change', async (e) => {
                if (e.target.checked) {
                    map.addLayer(layers.oldBuildings);
                    if (layers.oldBuildings.getLayers().length === 0) {
                        const loadingOverlay = document.getElementById('loading');
                        if (loadingOverlay) loadingOverlay.style.display = 'flex';
                        try {
                            const res = await fetch('/data/old_buildings_ratio.geojson');
                            if (!res.ok) throw new Error('Network response was not ok');
                            const geojsonData = await res.json();
                            
                            L.geoJSON(geojsonData, {
                                style: function (feature) {
                                    return {
                                        fillColor: '#e11d48', // 짙은 분홍색
                                        weight: 1,
                                        opacity: 0.3,
                                        color: 'white',
                                        dashArray: '3',
                                        fillOpacity: 0.5 // 투명도 50% 이상
                                    };
                                },
                                onEachFeature: function (feature, layer) {
                                    const props = feature.properties;
                                    layer.bindTooltip(`<b>노후화 집중 구역</b><br>건축물: ${props.val} / ${props.total_val}개<br>노후화 비율: ${props.ratio_pct}%`, {
                                        sticky: true,
                                        className: 'custom-tooltip'
                                    });
                                }
                            }).addTo(layers.oldBuildings);
                        } catch (error) {
                            console.error('Error loading old buildings:', error);
                            alert('노후 건축물 데이터를 불러오는 데 실패했습니다.');
                        } finally {
                            if (loadingOverlay) loadingOverlay.style.display = 'none';
                        }
                    }
                } else {
                    map.removeLayer(layers.oldBuildings);
                }
            });

            // Load main auction data first to show results quickly
            loadAuctions().finally(() => {
                const loadingOverlay = document.getElementById('loading');
                if (loadingOverlay) loadingOverlay.style.display = 'none';
                
                // Defer loading heavy infra data to prevent main thread blocking
                setTimeout(() => {
                    fetchInfraData();
                    fetchSubwayLines();
                    fetchHagwonPolygons();
                    fetchDistrictUnits();
                    fetchPopulationHeatmap();
                }, 100);
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

            function switchMobileTab(tab) {
                if (window.innerWidth > 768) return;

                const leftPanel = document.getElementById('left-panel');
                const rightPanel = document.getElementById('right-panel');
                const btns = document.querySelectorAll('.mobile-tab-btn');

                btns.forEach(b => b.classList.remove('active'));

                if (tab === 'map') {
                    leftPanel.classList.remove('active-panel');
                    rightPanel.classList.remove('active-panel');
                    btns[0].classList.add('active');
                } else if (tab === 'left') {
                    leftPanel.classList.add('active-panel');
                    rightPanel.classList.remove('active-panel');
                    btns[1].classList.add('active');
                } else if (tab === 'right') {
                    leftPanel.classList.remove('active-panel');
                    rightPanel.classList.add('active-panel');
                    btns[2].classList.add('active');
                }
            }
        