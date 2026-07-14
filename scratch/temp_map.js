
        // 1. Initialize Standard Light Map (Kakao Map Style)
        const map = L.map('map', { zoomControl: false, preferCanvas: true }).setView([37.4979, 127.0276], 13);
        L.control.zoom({ position: 'bottomright' }).addTo(map);
        
        // Define min zoom required for loading demographic grids and other features
        const minZoomRequired = (L.Browser.mobile || window.innerWidth <= 768) ? 11 : 13;

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

        L.tileLayer('https://xdworld.vworld.kr/2d/Base/service/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '&copy; VWorld'
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
            dev1: L.layerGroup(),
            dev2: L.layerGroup(),
            popHeatmap: L.layerGroup(),
            resHeatmap: L.layerGroup(),
            workHeatmap: L.layerGroup(),
            oldBuildings: L.layerGroup(),
            roadFlows: L.layerGroup(),
            eliteSchools: L.layerGroup(),
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

        let highlightTimeout;
        function triggerHighlighter() {
            clearTimeout(highlightTimeout);
            highlightTimeout = setTimeout(applyHighlighter, 200);
        }

        document.getElementById('btn-highlighter').addEventListener('click', function() {
            this.classList.toggle('active');
            if (this.classList.contains('active')) {
                this.style.color = '#c026d3';
                this.style.borderColor = '#c026d3';
                this.style.background = '#fdf4ff';
            } else {
                this.style.color = '#94a3b8';
                this.style.borderColor = 'var(--border-color)';
                this.style.background = 'transparent';
            }
            triggerHighlighter();
        });

        function checkPointInLayerGroup(pt, layerGroup, latlng) {
            let isInside = false;
            layerGroup.eachLayer(layer => {
                if (isInside) return;
                
                if (layer.eachLayer) { 
                    isInside = checkPointInLayerGroup(pt, layer, latlng);
                } else if (layer.feature && (layer.feature.geometry.type === 'Polygon' || layer.feature.geometry.type === 'MultiPolygon')) {
                    if (layer.getBounds && layer.getBounds().contains(latlng)) {
                        if (window.turf && turf.booleanPointInPolygon(pt, layer.feature)) {
                            isInside = true;
                        }
                    }
                } else if (layer.getRadius && typeof layer.getRadius === 'function') {
                    if (layer._mRadius || (layer.options && layer.options.dashArray === '4, 4')) {
                        if (layer.getBounds && layer.getBounds().contains(latlng)) {
                            if (map.distance(layer.getLatLng(), latlng) <= layer.getRadius()) {
                                isInside = true;
                            }
                        }
                    }
                }
            });
            return isInside;
        }

        let highlightedCaseNos = [];

        function applyHighlighter() {
            const btnHighlighter = document.getElementById('btn-highlighter');
            const countEl = document.getElementById('highlight-count');
            highlightedCaseNos = [];

            if (!btnHighlighter || !btnHighlighter.classList.contains('active')) {
                layers.auction.eachLayer(marker => {
                    marker.setStyle({
                        radius: 6, color: '#fff', weight: 2, fillColor: marker.typeColor, fillOpacity: 1
                    });
                });
                if (countEl) countEl.style.display = 'none';
                return;
            }

            const activeFilterIds = [
                { id: 'toggle-subways', layer: layers.subway },
                { id: 'toggle-univs', layer: layers.univ },
                { id: 'toggle-inds', layer: layers.ind },
                { id: 'toggle-middles', layer: layers.middle },
                { id: 'toggle-commercial', layer: layers.commercial },
                { id: 'toggle-hagwons', layer: layers.hagwon },
                { id: 'toggle-dev1', layer: layers.dev1 },
                { id: 'toggle-dev2', layer: layers.dev2 },
                { id: 'toggle-old-buildings', layer: layers.oldBuildings }
            ];
            
            const activeLayers = [];
            activeFilterIds.forEach(f => {
                const el = document.getElementById(f.id);
                if (el && el.checked) {
                    activeLayers.push(f.layer);
                }
            });

            if (activeLayers.length === 0) {
                layers.auction.eachLayer(marker => {
                    marker.setStyle({
                        radius: 6, color: '#fff', weight: 2, fillColor: marker.typeColor, fillOpacity: 1
                    });
                });
                return;
            }

            layers.auction.eachLayer(marker => {
                const latlng = marker.getLatLng();
                const pt = window.turf ? turf.point([latlng.lng, latlng.lat]) : null;
                let isInside = true;

                for (let i = 0; i < activeLayers.length; i++) {
                    if (!checkPointInLayerGroup(pt, activeLayers[i], latlng)) {
                        isInside = false;
                        break;
                    }
                }

                if (isInside) {
                    marker.setStyle({
                        radius: 10, color: '#c026d3', weight: 4, fillColor: marker.typeColor, fillOpacity: 1
                    });
                    if (marker.bringToFront) marker.bringToFront();
                    highlightedCaseNos.push(marker.auctionData.case_no);
                } else {
                    marker.setStyle({
                        radius: 4, color: '#94a3b8', weight: 1, fillColor: marker.typeColor, fillOpacity: 0.3
                    });
                }
            });

            if (countEl) {
                if (activeLayers.length > 0) {
                    countEl.innerText = `${highlightedCaseNos.length}건 중첩`;
                    countEl.style.display = 'inline-block';
                } else {
                    countEl.style.display = 'none';
                }
            }
        }

        // 4. Data Loading Logic
        async function fetchInfraData() {
            if (map.getZoom() < minZoomRequired) return;
            const bounds = map.getBounds();
            const checkedRegions = Array.from(document.querySelectorAll('.region-checkbox:checked')).map(cb => cb.value);
            let url = `/api/map/pois?min_lat=${bounds.getSouth()}&max_lat=${bounds.getNorth()}&min_lng=${bounds.getWest()}&max_lng=${bounds.getEast()}`;
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
                            
                            // ?댁쭊 ?먯깋 ???媛꾨떒???꾩튂 李얘린 (?곗씠?곌? 留롮? ?딆쑝誘濡?
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
        }

        async function fetchSubwayLines() {
            if (!document.getElementById('toggle-subways').checked) return;
            if (layers.subwayLine.getLayers().length > 0) return;
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
            if (map.getZoom() < minZoomRequired) return;
            if (!document.getElementById('toggle-hagwons').checked) return;
            if (layers.hagwon.getLayers().length > 0) return;
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

                        const polygonLayer = L.polygon(coords, {
                            color: color,
                            fillColor: color,
                            fillOpacity: 0.5,
                            opacity: 0.5,
                            weight: 2
                        }).bindPopup(`<b>학원 밀집가</b><br>반경 200m 내 ${poly.count}개 학원 밀집`);
                        
                        const geojsonCoords = coords.map(c => [c[1], c[0]]);
                        polygonLayer.feature = {
                            type: 'Feature',
                            geometry: {
                                type: 'Polygon',
                                coordinates: [geojsonCoords]
                            }
                        };
                        polygonLayer.addTo(layers.hagwon);
                    });
                    if (document.getElementById('toggle-hagwons').checked) {
                        map.addLayer(layers.hagwon);
                    }
                }
            } catch (err) { console.error(err); } finally { triggerHighlighter(); }
        }

        async function fetchDistrictUnits() {
            if (map.getZoom() < minZoomRequired) return;
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
            } catch (err) { console.error(err); } finally { triggerHighlighter(); }
        }

        let cachedRoadFlowBounds = null;
        let cachedRoadFlowZoom = null;

        async function fetchRoadFlows() {
            const roadFlowMinZoom = 14;
            const currentZoom = map.getZoom();
            if (currentZoom < roadFlowMinZoom) {
                layers.roadFlows.clearLayers();
                cachedRoadFlowBounds = null;
                cachedRoadFlowZoom = null;
                return;
            }
            if (!document.getElementById('toggle-road-flows').checked) return;
            
            const bounds = map.getBounds();
            
            // 스마트 캐싱: 줌 레벨이 동일하고, 현재 영역이 캐싱된 패딩 영역 내에 완전히 존재하면 재요청 생략
            if (cachedRoadFlowZoom === currentZoom && cachedRoadFlowBounds && cachedRoadFlowBounds.contains(bounds)) {
                console.log("Road flows loaded from cache (within bounds).");
                return;
            }
            
            // 25% 패딩을 주어 더 넓은 영역을 한 번에 가져오고 캐싱합니다 (미세 이동 시 뚝뚝 끊김 방지)
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
            
            try {
                const res = await fetch(`/api/map/road_flows?min_lat=${paddedBounds.getSouth()}&max_lat=${paddedBounds.getNorth()}&min_lng=${paddedBounds.getWest()}&max_lng=${paddedBounds.getEast()}`);
                const json = await res.json();
                if (json.status === 'success') {
                    layers.roadFlows.clearLayers();
                    
                    // 획기적인 메모리 절감: SVGRenderer 강제를 해제하여 DOM 엘리먼트 부담 없이 글로벌 Canvas에 직접 렌더링
                    L.geoJSON(json.data, {
                        style: function (feature) {
                            const intensity = feature.properties.flow_intensity || 0.5;
                            let color = '#a3e635'; // 매우 낮음: 연두색
                            let strokeWidth = 1.1;

                            if (intensity >= 0.8) {
                                color = '#7f1d1d'; // 매우 높음: 진한 자주/붉은색
                                strokeWidth = 4.5;
                            } else if (intensity >= 0.6) {
                                color = '#ef4444'; // 높음: 붉은색
                                strokeWidth = 3.2;
                            } else if (intensity >= 0.4) {
                                color = '#f97316'; // 중간: 주황색
                                strokeWidth = 2.2;
                            } else if (intensity >= 0.2) {
                                color = '#22c55e'; // 낮음: 초록색
                                strokeWidth = 1.6;
                            }

                            return {
                                color: color,
                                weight: strokeWidth,
                                opacity: 0.85
                            };
                        },
                        onEachFeature: function (feature, layer) {
                            const props = feature.properties;
                            const flowDesc = props.flow_type || '이면도로 보행자';
                            const hourlyCount = props.avg_hourly_flow || 0;
                            const pctVal = Math.round(props.flow_intensity * 100);
                            
                            let popupContent = `
                                <div style="font-family: 'Noto Sans KR', sans-serif; min-width: 180px; padding: 5px;">
                                    <div style="font-weight: bold; font-size: 0.95rem; margin-bottom: 6px; color: #1e293b; display: flex; align-items: center; gap: 5px;">
                                        <i class="fa-solid fa-route" style="color: #b91c1c;"></i>
                                        <span>${props.road_name || '이면도로 보행동선'}</span>
                                    </div>
                                    <table style="width: 100%; font-size: 0.8rem; border-collapse: collapse;">
                                        <tr>
                                            <td style="color: #64748b; padding: 3px 0;">동선 구분</td>
                                            <td style="text-align: right; font-weight: bold; color: #334155;">${flowDesc}</td>
                                        </tr>
                                        <tr>
                                            <td style="color: #64748b; padding: 3px 0;">시간당 유동량</td>
                                            <td style="text-align: right; font-weight: 800; color: #dc2626;">${hourlyCount.toLocaleString()}명/시간</td>
                                        </tr>
                                        <tr>
                                            <td style="color: #64748b; padding: 3px 0;">지역 내 유동 상위</td>
                                            <td style="text-align: right; font-weight: bold; color: #ea580c;">상위 ${(100 - pctVal)}%</td>
                                        </tr>
                                    </table>
                                </div>
                            `;

                            layer.bindPopup(popupContent);

                            layer.on('mouseover', function (e) {
                                e.target.setStyle({
                                    weight: e.target.options.weight + 1.5,
                                    opacity: 1.0
                                });
                            });

                            layer.on('mouseout', function (e) {
                                const intensity = feature.properties.flow_intensity || 0.5;
                                let originalWeight = 1.1;
                                if (intensity >= 0.8) originalWeight = 4.5;
                                else if (intensity >= 0.6) originalWeight = 3.2;
                                else if (intensity >= 0.4) originalWeight = 2.2;
                                else if (intensity >= 0.2) originalWeight = 1.6;
                                
                                e.target.setStyle({
                                    weight: originalWeight,
                                    opacity: 0.85
                                });
                            });
                        }
                    }).addTo(layers.roadFlows);
                    
                    // 캐싱 바운드 및 줌 레벨 업데이트
                    cachedRoadFlowBounds = paddedBounds;
                    cachedRoadFlowZoom = currentZoom;
                }
            } catch (err) {
                console.error("Failed to fetch road flows:", err);
            } finally {
                triggerHighlighter();
            }
        }

        async function fetchPopulationHeatmap() {
            // No-op function (deleted population heatmap layer)
            return;
        }

        async function fetchResidentialHeatmap() {
            if (map.getZoom() < minZoomRequired) return;
            if (!document.getElementById('toggle-residential-heatmap').checked) return;
            const bounds = map.getBounds();
            const checkedRegions = Array.from(document.querySelectorAll('.region-checkbox:checked')).map(cb => cb.value);
            const regionsParam = checkedRegions.length > 0 ? `&regions=${checkedRegions.join(',')}` : '&regions=서울';
            
            try {
                const res = await fetch(`/api/map/grid_demographics?type=residential&min_lat=${bounds.getSouth()}&max_lat=${bounds.getNorth()}&min_lng=${bounds.getWest()}&max_lng=${bounds.getEast()}${regionsParam}`);
                const json = await res.json();
                if (json.status === 'success') {
                    layers.resHeatmap.clearLayers();
                    
                    const data = json.data;
                    if (data && data.length > 0) {
                        // region별 그룹화
                        const groups = {};
                        data.forEach(item => {
                            const r = item.region || 'seoul';
                            if (!groups[r]) groups[r] = [];
                            groups[r].push(item);
                        });

                        // Modern 5-color palette for Residential (Yellow to Orange)
                        const colors = ['#fef08a', '#fde047', '#facc15', '#ea580c', '#c2410c'];

                        // 각 그룹별 독립 로컬 10단계 분위수 정규화
                        Object.keys(groups).forEach(rName => {
                            const groupData = groups[rName];
                            
                            // 분위수 기준 10단계 부여를 위해 오름차순 정렬
                            const sortedGroupData = [...groupData].sort((a, b) => a.avg_population - b.avg_population);
                            const N = sortedGroupData.length;

                            sortedGroupData.forEach((item, index) => {
                                let step = Math.floor((index / N) * 10) + 1;
                                step = Math.min(step, 10);
                                
                                // 하위 5단계 삭제
                                if (step <= 5) return;

                                const colorIdx = step - 6;
                                const color = colors[colorIdx] || colors[colors.length - 1];
                                
                                const lat = item.lat;
                                const lng = item.lng;
                                
                                // 250m x 250m grid rectangle centered around lat/lng
                                const halfLat = (json.lat_step || 0.00225) / 2;
                                const halfLng = (json.lng_step || 0.0028) / 2;
                                const rectBounds = [
                                    [lat - halfLat, lng - halfLng],
                                    [lat + halfLat, lng + halfLng]
                                ];

                                const regionLabel = rName === 'seoul' ? '서울' : (rName === 'gyeonggi' ? '경기' : '인천');

                                L.rectangle(rectBounds, {
                                    color: color,
                                    weight: 0.5,
                                    opacity: 0.3,
                                    fillColor: color,
                                    fillOpacity: 0.3
                                }).bindPopup(`<b>거주인구 격자 (${regionLabel})</b><br>밀집도: ${step}단계 (상위 ${11 - step}0%)<br>인구수: ${Math.round(item.avg_population).toLocaleString()}명`)
                                  .addTo(layers.resHeatmap);
                            });
                        });
                    }
                }
            } catch (err) { console.error("Residential Heatmap fetch error:", err); }
        }

        async function fetchWorkplaceHeatmap() {
            if (map.getZoom() < minZoomRequired) return;
            if (!document.getElementById('toggle-workplace-heatmap').checked) return;
            const bounds = map.getBounds();
            const checkedRegions = Array.from(document.querySelectorAll('.region-checkbox:checked')).map(cb => cb.value);
            const regionsParam = checkedRegions.length > 0 ? `&regions=${checkedRegions.join(',')}` : '&regions=서울';
            
            try {
                const res = await fetch(`/api/map/grid_demographics?type=workplace&min_lat=${bounds.getSouth()}&max_lat=${bounds.getNorth()}&min_lng=${bounds.getWest()}&max_lng=${bounds.getEast()}${regionsParam}`);
                const json = await res.json();
                if (json.status === 'success') {
                    layers.workHeatmap.clearLayers();
                    
                    const data = json.data;
                    if (data && data.length > 0) {
                        // region별 그룹화
                        const groups = {};
                        data.forEach(item => {
                            const r = item.region || 'seoul';
                            if (!groups[r]) groups[r] = [];
                            groups[r].push(item);
                        });

                        // Modern 5-color palette for Workplace (Purple to Indigo)
                        const colors = ['#e9d5ff', '#d8b4fe', '#c084fc', '#8b5cf6', '#6366f1'];

                        // 각 그룹별 독립 로컬 10단계 분위수 정규화
                        Object.keys(groups).forEach(rName => {
                            const groupData = groups[rName];
                            
                            // 분위수 기준 10단계 부여를 위해 오름차순 정렬
                            const sortedGroupData = [...groupData].sort((a, b) => a.avg_population - b.avg_population);
                            const N = sortedGroupData.length;

                            sortedGroupData.forEach((item, index) => {
                                let step = Math.floor((index / N) * 10) + 1;
                                step = Math.min(step, 10);
                                
                                // 하위 5단계 삭제
                                if (step <= 5) return;

                                const colorIdx = step - 6;
                                const color = colors[colorIdx] || colors[colors.length - 1];
                                
                                const lat = item.lat;
                                const lng = item.lng;
                                
                                // 250m x 250m grid rectangle centered around lat/lng
                                const halfLat = (json.lat_step || 0.00225) / 2;
                                const halfLng = (json.lng_step || 0.0028) / 2;
                                const rectBounds = [
                                    [lat - halfLat, lng - halfLng],
                                    [lat + halfLat, lng + halfLng]
                                ];

                                const regionLabel = rName === 'seoul' ? '서울' : (rName === 'gyeonggi' ? '경기' : '인천');

                                L.rectangle(rectBounds, {
                                    color: color,
                                    weight: 0.5,
                                    opacity: 0.3,
                                    fillColor: color,
                                    fillOpacity: 0.3
                                }).bindPopup(`<b>직장인구 격자 (${regionLabel})</b><br>밀집도: ${step}단계 (상위 ${11 - step}0%)<br>종사자수: ${Math.round(item.avg_population).toLocaleString()}명`)
                                  .addTo(layers.workHeatmap);
                            });
                        });
                    }
                }
            } catch (err) { console.error("Workplace Heatmap fetch error:", err); }
        }

        function buildAuctionUrl(basePath) {
            const bounds = map.getBounds();
            const isAuctionActive = document.getElementById('btn-auction').classList.contains('active');
            const isPublicActive = document.getElementById('btn-public').classList.contains('active');

            const checkedTypes = Array.from(document.querySelectorAll('#property-type-grid input:checked')).map(cb => cb.value);
            const checkedSpecialRights = Array.from(document.querySelectorAll('#special-rights-grid input:checked')).map(cb => cb.value);
            const checkedLandPrices = Array.from(document.querySelectorAll('#land-price-grid input:checked')).map(cb => cb.value);
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
            
            if (checkedSpecialRights.length > 0) url += `&special_rights=${checkedSpecialRights.join(',')}`;
            if (checkedLandPrices.length > 0) url += `&land_prices=${checkedLandPrices.join(',')}`;

            return url;
        }

        async function loadAuctions() {
            const zoomWarning = document.getElementById('zoom-warning');
            
            if (map.getZoom() < minZoomRequired) {
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

                        marker.on('click', function(e) {
                            openDemandPanel(item.lat, item.lng, item.case_no, item.address, item.property_type);
                        });

                        marker.bindPopup(function(layer) {
                            let d = layer.auctionData;
                            let isPub = layer.isPublic;
                            let tColor = layer.typeColor;
                            let typeLabelStr = isPub ? '공매' : '경매';
                            let typeLabel = `<span style="color:${tColor};font-weight:bold;">[${typeLabelStr}]</span>`;
                            
                            let cleanNotes = d.special_notes ? d.special_notes.replace(/0|#|A|미해당/gi, '').replace(/,/g, ' ').replace(/\s+/g, ' ').trim() : '';

                            return `
                                <div style="font-family:'Noto Sans KR'; min-width: 220px; padding-bottom: 5px;">
                                    <div style="font-size:1.1rem;">${typeLabel} <b>${d.case_no}</b></div>
                                    <div style="color:gray; font-size:0.85rem; margin-bottom:8px;">${d.property_type} | ${d.address}</div>
                                    <table style="width:100%; font-size:0.9rem; border-collapse: collapse; margin-bottom: 10px;">
                                        <tr><td style="color:gray; padding:3px 0;">감정가</td><td style="text-align:right; font-weight:bold;">${(d.appraisal_price / 100000000).toFixed(1)}억</td></tr>
                                        <tr><td style="color:gray; padding:3px 0;">최저가</td><td style="text-align:right; font-weight:bold; color:${tColor};">${d.min_bid_rate}% (${(d.min_price / 100000000).toFixed(1)}억)</td></tr>
                                        <tr><td style="color:gray; padding:3px 0;">매각기일</td><td style="text-align:right; font-weight:bold;">${d.sale_date ? d.sale_date : '정보없음'}</td></tr>
                                        <tr><td style="color:gray; padding:3px 0;">건물/대지</td><td style="text-align:right;">${d.area_size ? d.area_size.toFixed(1) : 0}평 / ${d.land_size ? d.land_size.toFixed(1) : 0}평</td></tr>
                                        <tr><td style="color:gray; padding:3px 0;">최저가 평당가</td><td style="text-align:right;">${d.min_price_per_pyeong ? (d.min_price_per_pyeong).toFixed(0) + '만원' : '-'}</td></tr>
                                        <tr><td style="color:gray; padding:3px 0;">공시지가</td><td style="text-align:right;">${d.official_land_price && d.official_land_price > 0 ? (d.official_land_price / 100000000).toFixed(2) + '억' : '정보없음'}</td></tr>
                                        ${cleanNotes ? `<tr><td style="color:#ef4444; padding:3px 0; font-weight:bold;">특수권리</td><td style="text-align:right; font-size:0.8rem; color:#ef4444; word-break:keep-all;">${cleanNotes}</td></tr>` : ''}
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
                                        <b>매각기일:</b> ${d.sale_date ? d.sale_date : '정보없음'}<br>
                                        <b>건물평수:</b> ${d.area_size ? d.area_size.toFixed(1) : 0}평<br>
                                        <b>대지평수:</b> ${d.land_size ? d.land_size.toFixed(1) : 0}평<br>
                                        <b>최저가 기준 평당가:</b> ${d.min_price_per_pyeong ? (d.min_price_per_pyeong).toFixed(0) + '만원' : '-'}<br>
                                        <b>공시지가:</b> ${d.official_land_price && d.official_land_price > 0 ? (d.official_land_price / 100000000).toFixed(2) + '억' : '정보없음'}
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
            } finally {
                triggerHighlighter();
            }
        } // End of loadAuctions

        // Toggles mapping
            const toggleMap = {
                'toggle-subways': [layers.subway, layers.subwayLine],
                'toggle-univs': [layers.univ],
                'toggle-middles': [layers.middle],
                'toggle-inds': [layers.ind],
                'toggle-commercial': [layers.commercial],
                'toggle-dev2': [layers.dev2],
                
                'toggle-residential-heatmap': [layers.resHeatmap],
                'toggle-workplace-heatmap': [layers.workHeatmap],
                'toggle-road-flows': [layers.roadFlows]
            };

            Object.keys(toggleMap).forEach(id => {
                document.getElementById(id).addEventListener('change', (e) => {
                    const layerList = toggleMap[id];
                    if (e.target.checked) {
                        layerList.forEach(l => map.addLayer(l));
                        if (['toggle-subways', 'toggle-univs', 'toggle-middles', 'toggle-inds', 'toggle-commercial'].includes(id)) {
                            updateCenterAddress();
                    fetchInfraData();
                        }
                    } else {
                        layerList.forEach(l => map.removeLayer(l));
                    }
                    triggerHighlighter();
                });
            });

            document.getElementById('toggle-bus').addEventListener('change', (e) => {
                e.target.checked ? (map.addLayer(layers.bus), loadBusStops()) : map.removeLayer(layers.bus);
            });

            // Fetch infra when map moves
            let moveEndTimeout;
            
        let centerMarker = null;

        function updateCenterAddress() {
            const center = map.getCenter();
            fetch(`https://dapi.kakao.com/v2/local/geo/coord2address.json?x=${center.lng}&y=${center.lat}`, {
                headers: { 'Authorization': 'KakaoAK 9e5265220f87e54e4379077cb60071bb' }
            })
            .then(res => res.json())
            .then(data => {
                let addressText = "주소 정보를 찾을 수 없습니다";
                if (data.documents && data.documents.length > 0) {
                    const doc = data.documents[0];
                    addressText = doc.road_address ? doc.road_address.address_name : doc.address.address_name;
                }
                document.getElementById('center-address-text').innerText = addressText;
            })
            .catch(err => {
                console.error('Failed to reverse geocode', err);
                document.getElementById('center-address-text').innerText = "주소 변환 실패";
            });
        }

        function addCenterMarker() {
            const center = map.getCenter();
            if (centerMarker) {
                map.removeLayer(centerMarker);
            }
            centerMarker = L.marker([center.lat, center.lng], {
                icon: L.divIcon({
                    html: '<div style="color: #ef4444; font-size: 24px;"><i class="fa-solid fa-location-dot"></i></div>',
                    className: 'custom-center-marker',
                    iconSize: [24, 24],
                    iconAnchor: [12, 24]
                })
            }).addTo(map);
            
            // Re-center map to exactly the clicked center to provide feedback
            map.setView(center, map.getZoom());
        }

        let placeMarker = null;

        function searchPlaceName() {
            const query = document.getElementById('search-place-input').value.trim();
            if (!query) {
                alert('검색할 지명이나 명소를 입력해주세요.');
                return;
            }
            
            fetch(`https://dapi.kakao.com/v2/local/search/keyword.json?query=${encodeURIComponent(query)}`, {
                headers: { 'Authorization': 'KakaoAK 9e5265220f87e54e4379077cb60071bb' }
            })
            .then(res => res.json())
            .then(data => {
                if (data.documents && data.documents.length > 0) {
                    const place = data.documents[0];
                    const lat = parseFloat(place.y);
                    const lng = parseFloat(place.x);
                    
                    // 기존 검색 마커가 있다면 제거
                    if (placeMarker) {
                        map.removeLayer(placeMarker);
                    }
                    
                    // 지도 중심 이동 및 줌 레벨 조정
                    map.setView([lat, lng], 16);
                    
                    // 세련된 장소 표시 마커 생성
                    placeMarker = L.marker([lat, lng], {
                        icon: L.divIcon({
                            html: '<div style="color: #ef4444; font-size: 28px; animation: bounce 0.5s infinite alternate;"><i class="fa-solid fa-location-dot"></i></div>',
                            className: 'search-place-marker',
                            iconSize: [28, 28],
                            iconAnchor: [14, 28]
                        })
                    }).addTo(map);
                    
                    // 명소 팝업 피드백 바인딩 및 즉시 표시
                    placeMarker.bindPopup(`
                        <div style="font-family:'Noto Sans KR', sans-serif; padding:6px 12px; min-width:180px;">
                            <strong style="color:var(--primary-blue); font-size:1.05rem; display:block; margin-bottom:4px;">${place.place_name}</strong>
                            <div style="font-size:0.8rem; color:#64748b; line-height:1.3; margin-bottom:2px;">지명 검색 결과</div>
                            <div style="font-size:0.85rem; color:#334155; font-weight:500;">${place.road_address_name || place.address_name}</div>
                        </div>
                    `).openPopup();
                } else {
                    alert('검색 결과를 찾을 수 없습니다. 지명을 좀 더 정확하게 입력해주세요. (예: 잠실야구장)');
                }
            })
            .catch(err => {
                console.error('Failed to search place via Kakao API', err);
                alert('지명 검색 중 통신 오류가 발생했습니다.');
            });
        }
        
        // Initial call
        updateCenterAddress();

            map.on('moveend', () => {
                clearTimeout(moveEndTimeout);
                moveEndTimeout = setTimeout(() => {
                    updateCenterAddress();
                    fetchInfraData();
                    fetchDistrictUnits();
                    fetchPopulationHeatmap();
                    fetchResidentialHeatmap();
                    fetchWorkplaceHeatmap();
                    fetchRoadFlows();
                    loadAuctions();
                }, 400); // 400ms debounce
            });

            document.getElementById('toggle-hagwons').addEventListener('change', (e) => {
                if (e.target.checked) {
                    if (layers.hagwon.getLayers().length === 0) {
                        fetchHagwonPolygons();
                    } else {
                        map.addLayer(layers.hagwon);
                        triggerHighlighter();
                    }
                } else {
                    map.removeLayer(layers.hagwon);
                    triggerHighlighter();
                }
            });



            document.getElementById('toggle-residential-heatmap').addEventListener('change', (e) => {
                if (e.target.checked) {
                    fetchResidentialHeatmap();
                }
            });

            document.getElementById('toggle-workplace-heatmap').addEventListener('change', (e) => {
                if (e.target.checked) {
                    fetchWorkplaceHeatmap();
                }
            });

            document.getElementById('toggle-road-flows').addEventListener('change', (e) => {
                if (e.target.checked) {
                    fetchRoadFlows();
                    document.getElementById('road-flow-legend').style.display = 'block';
                } else {
                    layers.roadFlows.clearLayers();
                    cachedRoadFlowBounds = null;
                    cachedRoadFlowZoom = null;
                    document.getElementById('road-flow-legend').style.display = 'none';
                }
            });

            // --- 경기도상권분석서비스 (상존인구 WMS) 관련 연동 로직 ---
            const gmrWmsTile = L.tileLayer.wms('https://sbiz.gmr.or.kr/gis/comm/wms.do', {
                layers: 'vw_gis_pop_road',
                format: 'image/png',
                transparent: true,
                version: '1.1.1',
                crs: L.CRS.EPSG3857,
                viewparams: 'stdr:20253;flag:time;val:20;radius:100;',
                store: 'gmr_new',
                maxZoom: 20,
                minZoom: 10,
                opacity: 0.75
            });

            document.getElementById('toggle-gmr-pop-road').addEventListener('change', (e) => {
                if (e.target.checked) {
                    layers.gmrPopRoad.clearLayers();
                    gmrWmsTile.addTo(layers.gmrPopRoad);
                    map.addLayer(layers.gmrPopRoad);
                } else {
                    map.removeLayer(layers.gmrPopRoad);
                    layers.gmrPopRoad.clearLayers();
                }
            });

            const gmrRow = document.getElementById('gmr-pop-road-row');
            const gmrToggle = document.getElementById('toggle-gmr-pop-road');

            const checkGmrRowVisibility = () => {
                const gyeonggiChecked = Array.from(document.querySelectorAll('.region-checkbox:checked')).some(cb => cb.value === '경기');
                if (gmrRow) {
                    gmrRow.style.display = gyeonggiChecked ? 'flex' : 'none';
                    if (!gyeonggiChecked && gmrToggle && gmrToggle.checked) {
                        gmrToggle.checked = false;
                        gmrToggle.dispatchEvent(new Event('change'));
                    }
                }
            };

            document.querySelectorAll('.region-checkbox').forEach(cb => {
                cb.addEventListener('change', checkGmrRowVisibility);
            });

            checkGmrRowVisibility();
            // ----------------------------------------------------

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
                    triggerHighlighter();
                }
            });

            document.getElementById('toggle-dev1').addEventListener('change', async (e) => {
                if (e.target.checked) {
                    map.addLayer(layers.dev1);
                    if (layers.dev1.getLayers().length === 0) {
                        const loadingOverlay = document.getElementById('loading');
                        if (loadingOverlay) loadingOverlay.style.display = 'flex';
                        try {
                            const res = await fetch('/data/taekji.geojson');
                            if (!res.ok) throw new Error('Network response was not ok');
                            const geojsonData = await res.json();
                            
                            L.geoJSON(geojsonData, {
                                style: function (feature) {
                                    return {
                                        fillColor: '#3b82f6', // 파란색
                                        weight: 2,
                                        opacity: 0.8,
                                        color: '#2563eb',
                                        dashArray: '4',
                                        fillOpacity: 0.2
                                    };
                                },
                                onEachFeature: function (feature, layer) {
                                    const props = feature.properties;
                                    layer.bindTooltip(`<b>택지지구</b><br>${props.zoneName || '이름 없음'}`, {
                                        sticky: true,
                                        className: 'custom-tooltip'
                                    });
                                }
                            }).addTo(layers.dev1);
                        } catch (error) {
                            console.error('Error loading taekji:', error);
                            alert('택지지구 데이터를 불러오는 데 실패했습니다.');
                        } finally {
                            if (loadingOverlay) loadingOverlay.style.display = 'none';
                        }
                    }
                } else {
                    map.removeLayer(layers.dev1);
                    triggerHighlighter();
                }
            });

            document.getElementById('req-elite-school').addEventListener('change', async (e) => {
                if (e.target.checked) {
                    map.addLayer(layers.eliteSchools);
                    if (layers.eliteSchools.getLayers().length === 0) {
                        const loadingOverlay = document.getElementById('loading');
                        if (loadingOverlay) loadingOverlay.style.display = 'flex';
                        try {
                            const res = await fetch('/data/elite_school_dongs.geojson');
                            if (!res.ok) throw new Error('Network response was not ok');
                            const geojsonData = await res.json();
                            
                            L.geoJSON(geojsonData, {
                                style: function (feature) {
                                    return {
                                        fillColor: '#3b82f6', // 파란색
                                        weight: 1.5,
                                        opacity: 0.8,
                                        color: '#2563eb', // 약간 더 진한 파란색
                                        fillOpacity: 0.5 // 투명도 50%
                                    };
                                },
                                onEachFeature: function (feature, layer) {
                                    const props = feature.properties;
                                    const districtsStr = (props.school_districts || []).join(', ');
                                    layer.bindTooltip(`<b>명문학군 행정동</b><br>동이름: ${props.dong_name} (${props.sido_name} ${props.sgg_name})<br>배정 학군: ${districtsStr}`, {
                                        sticky: true,
                                        className: 'custom-tooltip'
                                    });
                                }
                            }).addTo(layers.eliteSchools);
                        } catch (error) {
                            console.error('Error loading elite school dongs:', error);
                            alert('명문학군 행정동 데이터를 불러오는 데 실패했습니다.');
                        } finally {
                            if (loadingOverlay) loadingOverlay.style.display = 'none';
                        }
                    }
                } else {
                    map.removeLayer(layers.eliteSchools);
                    triggerHighlighter();
                }
            });

            // Load main auction data first to show results quickly
            loadAuctions().finally(() => {
                const loadingOverlay = document.getElementById('loading');
                if (loadingOverlay) loadingOverlay.style.display = 'none';
                
                // Defer loading heavy infra data to prevent main thread blocking
                setTimeout(() => {
                    updateCenterAddress();
                    fetchInfraData();
                    fetchSubwayLines();
                    fetchHagwonPolygons();
                    fetchDistrictUnits();
                    fetchPopulationHeatmap();
                    fetchRoadFlows();
                }, 100);
            });

            // Right panel fetch button
            document.querySelector('#right-panel .btn-primary').addEventListener('click', loadAuctions);

            function exportToExcel() {
                let url = buildAuctionUrl('/api/map/auctions/export');
                if (url) {
                    const btnHighlighter = document.getElementById('btn-highlighter');
                    if (btnHighlighter && btnHighlighter.classList.contains('active') && highlightedCaseNos.length > 0) {
                        url += `&cases=${highlightedCaseNos.join(',')}`;
                    }
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

            // --- Demand Side Panel JavaScript Helpers ---
            function showDemandSkeleton() {
                const content = document.getElementById('demand-panel-content');
                if (!content) return;
                content.innerHTML = `
                    <!-- Address & Meta Skeleton -->
                    <div class="demand-card" style="border-left: 4px solid var(--primary-blue); background: rgba(255, 255, 255, 0.9);">
                        <div class="skeleton" style="height: 18px; width: 60%; margin-bottom: 8px;"></div>
                        <div class="skeleton" style="height: 14px; width: 80%; margin-bottom: 5px;"></div>
                        <div class="skeleton" style="height: 12px; width: 40%;"></div>
                    </div>

                    <!-- 1km Radius Circular Demand Summary -->
                    <div class="demand-card">
                        <div class="demand-card-title">
                            <i class="fa-solid fa-users" style="color: var(--primary-blue);"></i> 반경 1km 배후인구 및 가구
                        </div>
                        <div class="demand-grid">
                            <div class="demand-stat-item">
                                <div class="demand-stat-label">거주인구</div>
                                <div class="skeleton" style="height: 20px; width: 70%; margin: 4px auto 0 auto;"></div>
                            </div>
                            <div class="demand-stat-item">
                                <div class="demand-stat-label">세대수</div>
                                <div class="skeleton" style="height: 20px; width: 70%; margin: 4px auto 0 auto;"></div>
                            </div>
                        </div>
                    </div>

                    <!-- Workplace & Business Summary -->
                    <div class="demand-card">
                        <div class="demand-card-title">
                            <i class="fa-solid fa-briefcase" style="color: var(--primary-blue);"></i> 직장인 및 업체수
                        </div>
                        <div class="demand-grid">
                            <div class="demand-stat-item">
                                <div class="demand-stat-label">직장인구</div>
                                <div class="skeleton" style="height: 20px; width: 70%; margin: 4px auto 0 auto;"></div>
                            </div>
                            <div class="demand-stat-item">
                                <div class="demand-stat-label">업체수</div>
                                <div class="skeleton" style="height: 20px; width: 70%; margin: 4px auto 0 auto;"></div>
                            </div>
                        </div>
                    </div>

                    <!-- Age Distribution -->
                    <div class="demand-card">
                        <div class="demand-card-title">
                            <i class="fa-solid fa-chart-column" style="color: var(--primary-blue);"></i> 연령대별 인구 분포
                        </div>
                        <div style="display: flex; flex-direction: column; gap: 10px;">
                            <div class="skeleton" style="height: 18px; width: 100%;"></div>
                            <div class="skeleton" style="height: 18px; width: 100%;"></div>
                            <div class="skeleton" style="height: 18px; width: 100%;"></div>
                            <div class="skeleton" style="height: 18px; width: 100%;"></div>
                        </div>
                    </div>

                    <!-- Subway Proximity -->
                    <div class="demand-card">
                        <div class="demand-card-title">
                            <i class="fa-solid fa-train-subway" style="color: var(--primary-blue);"></i> 인근 지하철역
                        </div>
                        <div class="skeleton" style="height: 24px; width: 50%; margin-bottom: 8px;"></div>
                        <div style="display: flex; flex-direction: column; gap: 6px;">
                            <div class="skeleton" style="height: 16px; width: 100%;"></div>
                            <div class="skeleton" style="height: 16px; width: 100%;"></div>
                        </div>
                    </div>

                    <!-- Comprehensive Evaluation -->
                    <div class="demand-card" style="background: rgba(37, 99, 235, 0.05); border: 1px dashed rgba(37, 99, 235, 0.3);">
                        <div class="skeleton" style="height: 18px; width: 40%; margin-bottom: 8px;"></div>
                        <div class="skeleton" style="height: 14px; width: 90%; margin-bottom: 6px;"></div>
                        <div class="skeleton" style="height: 14px; width: 85%;"></div>
                    </div>
                `;
            }

            function closeDemandPanel() {
                const panel = document.getElementById('demand-panel');
                if (panel) {
                    panel.classList.remove('open');
                }
            }

            async function openDemandPanel(lat, lng, caseNo, address, propType) {
                const panel = document.getElementById('demand-panel');
                if (!panel) return;

                // Show the drawer panel
                panel.classList.add('open');

                // Display skeleton state while fetching
                showDemandSkeleton();

                try {
                    const res = await fetch(`/api/map/demographics?lat=${lat}&lng=${lng}`);
                    if (!res.ok) throw new Error('API request failed');
                    const json = await res.json();
                    
                    if (json.status === 'success') {
                        renderDemandData(json, caseNo, address, propType);
                    } else {
                        document.getElementById('demand-panel-content').innerHTML = `
                            <div class="demand-card" style="text-align: center; padding: 25px; color: #ef4444;">
                                <i class="fa-solid fa-triangle-exclamation" style="font-size: 2rem; margin-bottom: 10px;"></i>
                                <p style="font-weight: bold; margin: 0;">데이터 분석 실패</p>
                                <p style="font-size: 0.8rem; color: var(--text-muted); margin-top: 5px;">${json.message || '인구 통계 데이터를 가져오지 못했습니다.'}</p>
                            </div>
                        `;
                    }
                } catch (err) {
                    console.error("Failed to load demographics analysis:", err);
                    document.getElementById('demand-panel-content').innerHTML = `
                        <div class="demand-card" style="text-align: center; padding: 25px; color: #ef4444;">
                            <i class="fa-solid fa-triangle-exclamation" style="font-size: 2rem; margin-bottom: 10px;"></i>
                            <p style="font-weight: bold; margin: 0;">네트워크 오류 발생</p>
                            <p style="font-size: 0.8rem; color: var(--text-muted); margin-top: 5px;">백엔드 서버와 통신할 수 없습니다.</p>
                        </div>
                    `;
                }
            }

            function renderDemandData(resData, caseNo, address, propType) {
                const content = document.getElementById('demand-panel-content');
                if (!content) return;

                const sub = resData.subway_proximity;
                const demo = resData.demographics;
                const eval = resData.assessment;

                let evalDetail = eval.detail || "";
                if (eval.recom_biz && evalDetail.includes('[입지 기반 추천 업종]')) {
                    evalDetail = evalDetail.split('[입지 기반 추천 업종]')[0].trim();
                }

                const resPop = demo.residential_population;
                const house = demo.households;
                const companies = demo.companies;
                const workPop = demo.workplace_population;

                // Age distribution calculations
                const age = demo.age_distribution;
                const totalAgePop = (age.under_20s || 0) + (age.twenties || 0) + (age.thirties || 0) + (age.forties || 0) + (age.fifties || 0) + (age.sixties_plus || 0);

                const getAgePct = (val) => {
                    if (!totalAgePop) return 0;
                    return ((val / totalAgePop) * 100).toFixed(1);
                };

                // Subway stations render
                let subwayListHtml = '';
                if (sub.all_stations_in_1km && sub.all_stations_in_1km.length > 0) {
                    subwayListHtml = sub.all_stations_in_1km.map(s => {
                        const lineColor = getGlobalLineColor(s.line);
                        return `
                            <div class="demand-subway-item">
                                <span class="demand-subway-name">
                                    <span class="demand-subway-dot" style="background-color: ${lineColor};"></span>
                                    <span>${s.name}역 (${s.line})</span>
                                </span>
                                <span style="font-weight: 700; color: var(--text-dark);">${s.distance}m</span>
                            </div>
                        `;
                    }).join('');
                } else {
                    subwayListHtml = `<div style="text-align: center; color: var(--text-muted); font-size: 0.75rem; padding: 10px 0;">반경 1km 이내 지하철역이 없습니다.</div>`;
                }

                // Age groups list
                const ageGroups = [
                    { label: '20세 미만', val: age.under_20s || 0, color: '#3b82f6' },
                    { label: '20대', val: age.twenties || 0, color: '#ec4899' },
                    { label: '30대', val: age.thirties || 0, color: '#8b5cf6' },
                    { label: '40대', val: age.forties || 0, color: '#10b981' },
                    { label: '50대', val: age.fifties || 0, color: '#f59e0b' },
                    { label: '60대 이상', val: age.sixties_plus || 0, color: '#64748b' }
                ];

                const ageChartHtml = ageGroups.map(grp => {
                    const pct = getAgePct(grp.val);
                    return `
                        <div class="age-chart-row">
                            <div class="age-chart-label-row">
                                <span style="font-weight: 500;">${grp.label}</span>
                                <span style="font-weight: bold; color: var(--text-dark);">${Number(grp.val).toLocaleString()}명 (${pct}%)</span>
                            </div>
                            <div class="age-chart-progress-bg">
                                <div class="age-chart-progress-bar" style="width: ${pct}%; background-color: ${grp.color};"></div>
                            </div>
                        </div>
                    `;
                }).join('');

                // Subway grade class & icon
                let gradeBadgeClass = 'subway-grade-비역세권';
                if (sub.grade === '초역세권') gradeBadgeClass = 'subway-grade-초역세권';
                else if (sub.grade === '역세권') gradeBadgeClass = 'subway-grade-역세권';

                // Source description badge
                const sourceBadge = `<span style="font-size: 0.65rem; color: #fff; background-color: ${demo.source.includes('SGIS') ? '#10b981' : '#6366f1'}; padding: 2px 6px; border-radius: 4px; font-weight: 700; margin-left: 6px;">${demo.source}</span>`;

                content.innerHTML = `
                    <!-- Address & Case Metadata -->
                    <div class="demand-card" style="border-left: 4px solid var(--primary-blue); background: rgba(255, 255, 255, 0.9);">
                        <div style="font-size: 0.75rem; font-weight: bold; color: var(--primary-blue); margin-bottom: 2px;">
                            ${propType} | ${caseNo}
                        </div>
                        <div style="font-size: 0.95rem; font-weight: bold; color: var(--text-dark); margin-bottom: 4px; line-height: 1.3;">
                            ${address}
                        </div>
                        <div style="font-size: 0.7rem; color: var(--text-muted); display: flex; align-items: center; gap: 4px;">
                            <i class="fa-solid fa-location-dot"></i> 반경 500m 배후수요 입지 분석 정보 ${sourceBadge}
                        </div>
                    </div>

                    <!-- 500m Radius Circular Population & Households -->
                    <div class="demand-card">
                        <div class="demand-card-title">
                            <i class="fa-solid fa-house-chimney-user" style="color: #ea580c;"></i> 반경 500m 주거 배후수요
                        </div>
                        <div class="demand-grid">
                            <div class="demand-stat-item">
                                <div class="demand-stat-label">거주인구</div>
                                <div class="demand-stat-value" style="color: #ea580c;">${Number(resPop).toLocaleString()}<span style="font-size: 0.75rem; font-weight: normal; margin-left: 2px;">명</span></div>
                            </div>
                            <div class="demand-stat-item">
                                <div class="demand-stat-label">세대수</div>
                                <div class="demand-stat-value">${Number(house).toLocaleString()}<span style="font-size: 0.75rem; font-weight: normal; margin-left: 2px;">세대</span></div>
                            </div>
                        </div>
                    </div>

                    <!-- Business & Workplace Population -->
                    <div class="demand-card">
                        <div class="demand-card-title">
                            <i class="fa-solid fa-building" style="color: #6366f1;"></i> 반경 500m 직장인 및 일자리 배후수요
                        </div>
                        <div class="demand-grid">
                            <div class="demand-stat-item">
                                <div class="demand-stat-label">직장인구</div>
                                <div class="demand-stat-value" style="color: #6366f1;">${Number(workPop).toLocaleString()}<span style="font-size: 0.75rem; font-weight: normal; margin-left: 2px;">명</span></div>
                            </div>
                            <div class="demand-stat-item">
                                <div class="demand-stat-label">등록업체수</div>
                                <div class="demand-stat-value">${Number(companies).toLocaleString()}<span style="font-size: 0.75rem; font-weight: normal; margin-left: 2px;">개</span></div>
                            </div>
                        </div>
                    </div>

                    <!-- Age Distribution -->
                    <div class="demand-card">
                        <div class="demand-card-title">
                            <i class="fa-solid fa-chart-column" style="color: #8b5cf6;"></i> 연령대별 인구 분포
                        </div>
                        <div style="display: flex; flex-direction: column; gap: 4px;">
                            ${ageChartHtml}
                        </div>
                    </div>

                    <!-- Subway Proximity -->
                    <div class="demand-card">
                        <div class="demand-card-title" style="margin-bottom: 6px;">
                            <i class="fa-solid fa-train-subway" style="color: #10b981;"></i> 대중교통 분석
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <span style="font-size: 0.8rem; font-weight: bold; color: var(--text-dark);">지하철 접근성</span>
                            <span class="demand-subway-badge ${gradeBadgeClass}">${sub.grade}</span>
                        </div>
                        <div class="demand-subway-list">
                            ${subwayListHtml}
                        </div>
                    </div>

                    <!-- Expert Evaluation -->
                    <div class="demand-card" style="background: rgba(37, 99, 235, 0.05); border: 1px dashed rgba(37, 99, 235, 0.3);">
                        <div class="demand-card-title" style="color: var(--primary-blue); font-size: 0.9rem; margin-bottom: 5px;">
                            <i class="fa-solid fa-ribbon"></i> AI 입지 종합 평가
                        </div>
                        <div class="demand-eval-grade">
                            <i class="fa-solid fa-circle-check" style="color: var(--primary-blue);"></i>
                            <span>${eval.class}</span>
                        </div>
                        <div class="demand-eval-detail" style="line-height: 1.5; font-size: 0.8rem; color: #334155;">
                            ${evalDetail.replace(/\n/g, '<br>')}
                        </div>

                        <!-- Segmented Floating Population (250m Radius) -->
                        <div id="demand-floating-box" style="margin-top: 15px; padding-top: 15px; border-top: 1px dashed rgba(37, 99, 235, 0.2);">
                            <div style="font-size: 0.8rem; font-weight: bold; color: var(--text-dark); margin-bottom: 10px; display: flex; align-items: center; gap: 5px;">
                                <i class="fa-solid fa-fire" style="color: #ef4444;"></i> 반경 250m 유동인구 세부 특징
                            </div>
                            <div class="floating-grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
                                <div class="floating-item" style="background: rgba(255, 255, 255, 0.8); padding: 8px 10px; border-radius: 6px; border: 1px solid rgba(226, 232, 240, 0.8);">
                                    <div style="font-size: 0.7rem; color: var(--text-muted); margin-bottom: 2px;">주중 일평균</div>
                                    <div style="font-size: 0.85rem; font-weight: bold; color: #1e293b;">${Number(demo.floating_population_250.weekday).toLocaleString()}명</div>
                                </div>
                                <div class="floating-item" style="background: rgba(255, 255, 255, 0.8); padding: 8px 10px; border-radius: 6px; border: 1px solid rgba(226, 232, 240, 0.8);">
                                    <div style="font-size: 0.7rem; color: var(--text-muted); margin-bottom: 2px;">주말 일평균</div>
                                    <div style="font-size: 0.85rem; font-weight: bold; color: #ea580c;">${Number(demo.floating_population_250.weekend).toLocaleString()}명</div>
                                </div>
                                <div class="floating-item" style="background: rgba(255, 255, 255, 0.8); padding: 8px 10px; border-radius: 6px; border: 1px solid rgba(226, 232, 240, 0.8);">
                                    <div style="font-size: 0.7rem; color: var(--text-muted); margin-bottom: 2px;">점심 (11~14시)</div>
                                    <div style="font-size: 0.85rem; font-weight: bold; color: #0284c7;">${Number(demo.floating_population_250.lunch).toLocaleString()}명</div>
                                </div>
                                <div class="floating-item" style="background: rgba(255, 255, 255, 0.8); padding: 8px 10px; border-radius: 6px; border: 1px solid rgba(226, 232, 240, 0.8);">
                                    <div style="font-size: 0.7rem; color: var(--text-muted); margin-bottom: 2px;">저녁 (18~21시)</div>
                                    <div style="font-size: 0.85rem; font-weight: bold; color: #4f46e5;">${Number(demo.floating_population_250.dinner).toLocaleString()}명</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Recommended Business Card -->
                    ${eval.recom_biz ? `
                    <div class="demand-card" style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.08), rgba(5, 150, 105, 0.03)); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 12px; margin-top: 15px; padding: 14px;">
                        <div class="demand-card-title" style="color: #059669; font-size: 0.88rem; margin-bottom: 8px; display: flex; align-items: center; gap: 6px;">
                            <i class="fa-solid fa-store" style="color: #10b981;"></i> 입지 기반 추천 업종 및 활용 제안
                        </div>
                        <div style="font-size: 0.82rem; font-weight: 700; color: #065f46; margin-bottom: 6px; line-height: 1.4;">
                            권장 업종: <span style="font-weight: 800; color: #047857;">${eval.recom_biz}</span>
                        </div>
                        <div style="font-size: 0.76rem; line-height: 1.5; color: #374151; word-break: keep-all;">
                            ${eval.recom_desc}
                        </div>
                    </div>
                    ` : ''}
                `;
            }
        