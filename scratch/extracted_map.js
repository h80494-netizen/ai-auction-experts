
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

        // --- Smart Caching Bounds and Data ---
        let cachedPoisData = null;
        let cachedPoisBounds = null;
        let cachedPoisZoom = null;
        let cachedPoisRegions = '';

        let cachedDistrictUnitsData = null;
        let cachedDistrictUnitsBounds = null;
        let cachedDistrictUnitsZoom = null;

        let cachedRedevelopmentZonesData = null;
        let cachedRedevelopmentZonesBounds = null;
        let cachedRedevelopmentZonesZoom = null;

        let cachedZoningPolygonsData = null;
        let cachedZoningPolygonsBounds = null;
        let cachedZoningPolygonsZoom = null;

        let cachedPlanningRoadsData = null;
        let cachedPlanningRoadsBounds = null;
        let cachedPlanningRoadsZoom = null;

        let cachedResHeatmapData = null;
        let cachedResHeatmapBounds = null;
        let cachedResHeatmapZoom = null;
        let cachedResHeatmapRegions = '';

        let cachedWorkHeatmapData = null;
        let cachedWorkHeatmapBounds = null;
        let cachedWorkHeatmapZoom = null;
        let cachedWorkHeatmapRegions = '';

        let cachedAuctionsData = null;
        let cachedAuctionsBounds = null;
        let cachedAuctionsZoom = null;
        let cachedAuctionsFilterState = '';

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
            dev3: L.layerGroup(),
            zoning: L.layerGroup(),
            planningRoad: L.layerGroup(),
            popHeatmap: L.layerGroup(),
            resHeatmap: L.layerGroup(),
            workHeatmap: L.layerGroup(),
            oldBuildings: L.layerGroup(),
            roadFlows: L.layerGroup(),
            eliteSchools: L.layerGroup(),
            realpriceGrid: L.layerGroup(),
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
            const modeContainer = document.getElementById('highlighter-mode-container');
            if (this.classList.contains('active')) {
                this.style.color = '#c026d3';
                this.style.borderColor = '#c026d3';
                this.style.background = '#fdf4ff';
                if (modeContainer) modeContainer.style.display = 'inline-flex';
            } else {
                this.style.color = '#94a3b8';
                this.style.borderColor = 'var(--border-color)';
                this.style.background = 'transparent';
                if (modeContainer) modeContainer.style.display = 'none';
            }
            triggerHighlighter();
        });

        window.highlighterMode = 'AND';
        window.setHighlighterMode = function(mode) {
            window.highlighterMode = mode;
            const btnAnd = document.getElementById('btn-mode-and');
            const btnOr = document.getElementById('btn-mode-or');
            if (mode === 'AND') {
                btnAnd.classList.add('active');
                btnAnd.style.background = '#fff';
                btnAnd.style.boxShadow = '0 1px 2px rgba(0,0,0,0.1)';
                btnAnd.style.color = 'var(--text-dark)';
                
                btnOr.classList.remove('active');
                btnOr.style.background = 'transparent';
                btnOr.style.boxShadow = 'none';
                btnOr.style.color = '#64748b';
            } else {
                btnOr.classList.add('active');
                btnOr.style.background = '#fff';
                btnOr.style.boxShadow = '0 1px 2px rgba(0,0,0,0.1)';
                btnOr.style.color = 'var(--text-dark)';
                
                btnAnd.classList.remove('active');
                btnAnd.style.background = 'transparent';
                btnAnd.style.boxShadow = 'none';
                btnAnd.style.color = '#64748b';
            }
            triggerHighlighter();
        };

        function getClosestPointOnSegment(p, v, w) {
            const sqr = x => x * x;
            const l2 = sqr(v.lat - w.lat) + sqr(v.lng - w.lng);
            if (l2 === 0) return v;
            let t = ((p.lat - v.lat) * (w.lat - v.lat) + (p.lng - v.lng) * (w.lng - v.lng)) / l2;
            t = Math.max(0, Math.min(1, t));
            return {
                lat: v.lat + t * (w.lat - v.lat),
                lng: v.lng + t * (w.lng - v.lng)
            };
        }

        function checkPointNearPolyline(p, polyline, maxDistanceMeters = 20) {
            const latlngs = polyline.getLatLngs();
            if (!latlngs || latlngs.length === 0) return false;
            
            function getSegments(arr) {
                let segments = [];
                if (arr[0] instanceof L.LatLng || (arr[0] && typeof arr[0].lat === 'number')) {
                    for (let i = 0; i < arr.length - 1; i++) {
                        segments.push([arr[i], arr[i+1]]);
                    }
                } else if (Array.isArray(arr)) {
                    arr.forEach(sub => {
                        segments = segments.concat(getSegments(sub));
                    });
                }
                return segments;
            }
            
            const segments = getSegments(latlngs);
            for (let i = 0; i < segments.length; i++) {
                const [v, w] = segments[i];
                const closest = getClosestPointOnSegment(p, v, w);
                const dist = map.distance(p, L.latLng(closest.lat, closest.lng));
                if (dist <= maxDistanceMeters) {
                    return true;
                }
            }
            return false;
        }

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
                } else if (layer.getLatLngs && typeof layer.getLatLngs === 'function') {
                    if (checkPointNearPolyline(latlng, layer, 20)) {
                        isInside = true;
                    }
                }
            });
            return isInside;
        }

        let highlightedCaseNos = [];

        function applyHighlighter() {
            const btnHighlighter = document.getElementById('btn-highlighter');
            const countEl = document.getElementById('highlight-count');
            const modeContainer = document.getElementById('highlighter-mode-container');
            highlightedCaseNos = [];

            if (!btnHighlighter || !btnHighlighter.classList.contains('active')) {
                layers.auction.eachLayer(marker => {
                    marker.setStyle({
                        radius: 6, color: '#fff', weight: 2, fillColor: marker.typeColor, fillOpacity: 1
                    });
                });
                if (countEl) countEl.style.display = 'none';
                if (modeContainer) modeContainer.style.display = 'none';
                return;
            }

            if (modeContainer) modeContainer.style.display = 'inline-flex';

            const activeFilterIds = [
                { id: 'toggle-subways', layer: layers.subway, isLine: false },
                { id: 'toggle-bus', layer: layers.bus, isLine: false },
                { id: 'toggle-univs', layer: layers.univ, isLine: false },
                { id: 'toggle-inds', layer: layers.ind, isLine: false },
                { id: 'toggle-middles', layer: layers.middle, isLine: false },
                { id: 'toggle-commercial', layer: layers.commercial, isLine: false },
                { id: 'toggle-hagwons', layer: layers.hagwon, isLine: false },
                { id: 'toggle-dev1', layer: layers.dev1, isLine: false },
                { id: 'toggle-dev2', layer: layers.dev2, isLine: false },
                { id: 'toggle-dev3', layer: layers.dev3, isLine: false },
                { id: 'toggle-zoning', layer: layers.zoning, isLine: false },
                { id: 'toggle-planning-road', layer: layers.planningRoad, isLine: true },
                { id: 'toggle-road-flows', layer: layers.roadFlows, isLine: true },
                { id: 'toggle-old-buildings', layer: layers.oldBuildings, isLine: false }
            ];
            
            const activeLayers = [];
            const activeNonLineLayers = [];
            activeFilterIds.forEach(f => {
                const el = document.getElementById(f.id);
                if (el && el.checked) {
                    activeLayers.push(f.layer);
                    if (!f.isLine) {
                        activeNonLineLayers.push(f.layer);
                    }
                }
            });

            if (activeLayers.length === 0) {
                layers.auction.eachLayer(marker => {
                    marker.setStyle({
                        radius: 6, color: '#fff', weight: 2, fillColor: marker.typeColor, fillOpacity: 1
                    });
                });
                if (countEl) countEl.style.display = 'none';
                return;
            }

            const mode = window.highlighterMode || 'AND';

            layers.auction.eachLayer(marker => {
                const latlng = marker.getLatLng();
                const pt = window.turf ? turf.point([latlng.lng, latlng.lat]) : null;
                
                const matchedLayersList = [];
                const matchedNonLineLayersList = [];
                activeFilterIds.forEach(f => {
                    const el = document.getElementById(f.id);
                    if (el && el.checked) {
                        if (checkPointInLayerGroup(pt, f.layer, latlng)) {
                            matchedLayersList.push(f.layer);
                            if (!f.isLine) {
                                matchedNonLineLayersList.push(f.layer);
                            }
                        }
                    }
                });

                let isInside = false;
                if (mode === 'AND') {
                    // AND는 유동동선 등 라인을 빼고 레이어목록의 조건을 모두 충족할 때
                    isInside = (activeNonLineLayers.length > 0 && matchedNonLineLayersList.length === activeNonLineLayers.length);
                } else {
                    // OR은 하나라도 중첩되는 경우
                    isInside = (matchedLayersList.length >= 1);
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
                    
                    countEl.style.cursor = 'pointer';
                    countEl.style.background = '#c026d3';
                    countEl.style.color = '#ffffff';
                    countEl.style.borderColor = '#c026d3';
                    countEl.title = 'AI 입지/개발 중첩 분석 보고서 보기';
                    
                    const btnAnalysis = document.getElementById('btn-show-analysis');
                    if (btnAnalysis) btnAnalysis.style.display = 'inline-flex';
                } else {
                    countEl.style.display = 'none';
                    const btnAnalysis = document.getElementById('btn-show-analysis');
                    if (btnAnalysis) btnAnalysis.style.display = 'none';
                }
            }
        }

        window.openOverlapAnalysis = function() {
            const btnHighlighter = document.getElementById('btn-highlighter');
            if (!btnHighlighter || !btnHighlighter.classList.contains('active')) {
                alert('형광펜을 켠 후 필터를 선택해주세요.');
                return;
            }

            const activeFilterIds = [
                { id: 'toggle-subways', layer: layers.subway, name: '지하철역', isLine: false },
                { id: 'toggle-bus', layer: layers.bus, name: '버스정류장', isLine: false },
                { id: 'toggle-univs', layer: layers.univ, name: '대학교', isLine: false },
                { id: 'toggle-inds', layer: layers.ind, name: '산업단지', isLine: false },
                { id: 'toggle-middles', layer: layers.middle, name: '중학교', isLine: false },
                { id: 'toggle-commercial', layer: layers.commercial, name: '상권', isLine: false },
                { id: 'toggle-hagwons', layer: layers.hagwon, name: '학원가', isLine: false },
                { id: 'toggle-dev1', layer: layers.dev1, name: '택지지구', isLine: false },
                { id: 'toggle-dev2', layer: layers.dev2, name: '지구단위계획', isLine: false },
                { id: 'toggle-dev3', layer: layers.dev3, name: '재개발/재건축', isLine: false },
                { id: 'toggle-zoning', layer: layers.zoning, name: '용도지역', isLine: false },
                { id: 'toggle-planning-road', layer: layers.planningRoad, name: '도시계획도로', isLine: true },
                { id: 'toggle-road-flows', layer: layers.roadFlows, name: '유동동선', isLine: true },
                { id: 'toggle-old-buildings', layer: layers.oldBuildings, name: '노후지', isLine: false }
            ];

            const activeLayers = [];
            const activeNonLineLayers = [];
            activeFilterIds.forEach(f => {
                const el = document.getElementById(f.id);
                if (el && el.checked) {
                    activeLayers.push({ layer: f.layer, name: f.name, isLine: f.isLine });
                    if (!f.isLine) {
                        activeNonLineLayers.push({ layer: f.layer, name: f.name });
                    }
                }
            });

            if (activeLayers.length === 0) {
                alert('필터를 선택해주세요.');
                return;
            }

            const matchedAuctions = [];
            const mode = window.highlighterMode || 'AND';

            layers.auction.eachLayer(marker => {
                const latlng = marker.getLatLng();
                const pt = window.turf ? turf.point([latlng.lng, latlng.lat]) : null;
                
                const matchedLayersList = [];
                const matchedNonLineLayersList = [];

                activeLayers.forEach(l => {
                    if (checkPointInLayerGroup(pt, l.layer, latlng)) {
                        matchedLayersList.push(l.name);
                        if (!l.isLine) {
                            matchedNonLineLayersList.push(l.name);
                        }
                    }
                });

                let isInside = false;
                if (mode === 'AND') {
                    // AND는 유동동선 등 라인을 빼고 레이어목록의 조건을 모두 충족할 때
                    isInside = (activeNonLineLayers.length > 0 && matchedNonLineLayersList.length === activeNonLineLayers.length);
                } else {
                    // OR은 하나라도 중첩되는 경우
                    isInside = (matchedLayersList.length >= 1);
                }

                if (isInside && matchedLayersList.length > 0) {
                    matchedAuctions.push({
                        case_no: marker.auctionData.case_no,
                        property_type: marker.auctionData.property_type || '주택',
                        address: marker.auctionData.address || marker.auctionData.road_address || '',
                        appraisal_price: marker.auctionData.appraisal_price || 0,
                        min_price: marker.auctionData.min_price || 0,
                        overlap_count: matchedLayersList.length,
                        matched_layers: matchedLayersList,
                        special_notes: marker.auctionData.special_notes || ''
                    });
                }
            });

            if (matchedAuctions.length === 0) {
                alert('필터 조건에 부합하는 중첩된 물건이 없습니다.');
                return;
            }

            console.log("Saving highlighted auctions count:", matchedAuctions.length);
            console.log("Saving highlighted auctions data:", matchedAuctions);
            // Save to local storage
            localStorage.setItem('highlighted_auctions', JSON.stringify(matchedAuctions));
            console.log("Saved to localStorage: highlighted_auctions");
            
            // Open in a new tab/window
            window.open('analysis.html', '_blank');
        };

        async function fetchInfraData() {
            if (map.getZoom() < minZoomRequired) return;
            const bounds = map.getBounds();
            const checkedRegions = Array.from(document.querySelectorAll('.region-checkbox:checked')).map(cb => cb.value);
            const regionsStr = checkedRegions.join(',');

            const isCached = cachedPoisZoom === map.getZoom() && 
                             cachedPoisBounds && 
                             cachedPoisBounds.contains(bounds) && 
                             cachedPoisRegions === regionsStr &&
                             cachedPoisData;

            let data;
            if (isCached) {
                console.log("POIs loaded from cache (within bounds).");
                data = cachedPoisData;
            } else {
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

                let url = `/api/map/pois?min_lat=${paddedBounds.getSouth()}&max_lat=${paddedBounds.getNorth()}&min_lng=${paddedBounds.getWest()}&max_lng=${paddedBounds.getEast()}`;
                if (checkedRegions.length > 0) url += `&regions=${checkedRegions.join(',')}`;

                try {
                    const res = await fetch(url);
                    const json = await res.json();
                    if (json.status === 'success') {
                        cachedPoisData = json.data;
                        cachedPoisBounds = paddedBounds;
                        cachedPoisZoom = map.getZoom();
                        cachedPoisRegions = regionsStr;
                        data = cachedPoisData;
                    } else {
                        return;
                    }
                } catch (err) {
                    console.error("Failed to fetch POIs:", err);
                    return;
                }
            }

            try {
                // Populate Subway markers
                layers.subway.clearLayers();
                if (data.subways) {
                    data.subways.forEach(s => {
                        let radius = parseInt(document.getElementById('buffer-subways').value) || 500;
                        let color = getGlobalLineColor(s.line);
                        L.circle([s.lat, s.lng], { color: color, fillColor: color, fillOpacity: 0.1, radius: radius, weight: 1, dashArray: '4, 4' }).addTo(layers.subway);
                        createDotMarker(s.lat, s.lng, color, `<b>${s.name}</b><br>${s.line}`).addTo(layers.subway);
                    });
                }

                // Populate Universities markers
                layers.univ.clearLayers();
                if (data.universities) {
                    data.universities.forEach(u => {
                        let radius = parseInt(document.getElementById('buffer-univs').value) || 500;
                        L.circle([u.lat, u.lng], { color: '#3b82f6', fillColor: '#3b82f6', fillOpacity: 0.1, radius: radius, weight: 1, dashArray: '4, 4' }).addTo(layers.univ);
                        createDotMarker(u.lat, u.lng, '#3b82f6', `<b>${u.name}</b><br>대학교`).addTo(layers.univ);
                    });
                }

                // Populate Industrial Complexes markers
                layers.ind.clearLayers();
                if (data.industrial_complexes) {
                    data.industrial_complexes.forEach(i => {
                        let radius = parseInt(document.getElementById('buffer-inds').value) || 500;
                        L.circle([i.lat, i.lng], { color: '#f59e0b', fillColor: '#f59e0b', fillOpacity: 0.1, radius: radius, weight: 1, dashArray: '4, 4' }).addTo(layers.ind);
                        createDotMarker(i.lat, i.lng, '#f59e0b', `<b>${i.name}</b><br>산업단지`).addTo(layers.ind);
                    });
                }

                // Populate Middle Schools markers
                layers.middle.clearLayers();
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

                // Populate Bus Stops markers
                layers.bus.clearLayers();
                if (data.bus_stops) {
                    let radius = parseInt(document.getElementById('buffer-bus').value) || 20;
                    data.bus_stops.forEach(b => {
                        L.circle([b.lat, b.lng], { color: '#0ea5e9', fillColor: '#0ea5e9', fillOpacity: 0.1, radius: radius, weight: 1, dashArray: '4, 4' }).addTo(layers.bus);
                        createDotMarker(b.lat, b.lng, '#0ea5e9', `<b>${b.name}</b><br>버스 (${b.city})`, 3).addTo(layers.bus);
                    });
                }

                // Populate Commercial Areas
                layers.commercial.clearLayers();
                if (data.commercial_areas) {
                    const pops = data.commercial_areas.map(c => c.population || 0).sort((a, b) => a - b);
                    const popData = {};
                    data.commercial_areas.forEach(c => {
                        popData[c.name] = c.population || 0;
                    });

                    const getTierStyle = (pop) => {
                        if (pop === 0 || pops.length === 0) return null;
                        const idx = pops.findIndex(p => p >= pop);
                        const percentile = (idx + 1) / pops.length;
                        const tier = Math.ceil(percentile * 10) || 1;
                        if (tier <= 6) return null;
                        const colors = { 10: '#08306b', 9: '#08519c', 8: '#2171b5', 7: '#4292c6' };
                        return { color: colors[tier] || '#ffffff', fillColor: colors[tier] || '#ffffff', fillOpacity: 0.5, weight: 0 };
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
                                layer.bindTooltip(`<b>${name}</b><br>상권<br>유동인구: ${popStr}`, { sticky: true, className: 'custom-tooltip' });
                            }
                        });
                        geoJsonLayer.addTo(layers.commercial);
                    }
                }
            } catch (err) {
                console.error(err);
            } finally {
                triggerHighlighter();
            }
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
            const isCached = cachedDistrictUnitsZoom === map.getZoom() && 
                             cachedDistrictUnitsBounds && 
                             cachedDistrictUnitsBounds.contains(bounds) && 
                             cachedDistrictUnitsData;

            let data;
            if (isCached) {
                console.log("District units loaded from cache (within bounds).");
                data = cachedDistrictUnitsData;
            } else {
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
                    const res = await fetch(`/api/map/district_units?min_lat=${paddedBounds.getSouth()}&max_lat=${paddedBounds.getNorth()}&min_lng=${paddedBounds.getWest()}&max_lng=${paddedBounds.getEast()}`);
                    const json = await res.json();
                    if (json.status === 'success') {
                        cachedDistrictUnitsData = json.data;
                        cachedDistrictUnitsBounds = paddedBounds;
                        cachedDistrictUnitsZoom = map.getZoom();
                        data = cachedDistrictUnitsData;
                    } else {
                        return;
                    }
                } catch (err) {
                    console.error("Failed to fetch district units:", err);
                    return;
                }
            }

            layers.dev2.clearLayers();
            data.forEach(item => {
                let geojson = JSON.parse(item.geojson);
                L.geoJSON(geojson, {
                    style: {
                        color: '#4ade80', // 연한 초록색
                        fillColor: '#4ade80',
                        fillOpacity: 0.15,
                        weight: 2,
                        dashArray: '5, 5'
                    }
                }).bindPopup(`<b>지구단위계획구역</b><br>${item.name}`).addTo(layers.dev2);
            });
            triggerHighlighter();
        }

        // --- 개발구역 및 도시계획 레이어 추가 함수 시작 ---
        
        let cachedTaekjiGeoJSON = null;

        async function updateTaekjiLayer() {
            const subContainer = document.getElementById('dev1-sub-container');
            const mainToggle = document.getElementById('toggle-dev1');
            
            if (!mainToggle.checked) {
                if (subContainer) subContainer.style.display = 'none';
                layers.dev1.clearLayers();
                map.removeLayer(layers.dev1);
                triggerHighlighter();
                return;
            }
            
            if (subContainer) subContainer.style.display = 'block';
            map.addLayer(layers.dev1);
            layers.dev1.clearLayers();
            
            const checkedStages = Array.from(document.querySelectorAll('.dev1-stage-check:checked')).map(cb => cb.value);
            if (checkedStages.length === 0) {
                triggerHighlighter();
                return;
            }
            
            if (!cachedTaekjiGeoJSON) {
                const loadingOverlay = document.getElementById('loading');
                if (loadingOverlay) loadingOverlay.style.display = 'flex';
                try {
                    const res = await fetch('/data/taekji.geojson');
                    if (!res.ok) throw new Error('Network response was not ok');
                    cachedTaekjiGeoJSON = await res.json();
                } catch (error) {
                    console.error('Error loading taekji:', error);
                    alert('택지지구 데이터를 불러오는 데 실패했습니다.');
                    if (loadingOverlay) loadingOverlay.style.display = 'none';
                    return;
                } finally {
                    if (loadingOverlay) loadingOverlay.style.display = 'none';
                }
            }
            
            function getTaekjiStage(stepCode) {
                if (!stepCode) return '초기';
                const code = stepCode.toUpperCase();
                if (['SA'].includes(code)) return '초기';
                if (['DA', 'RA', 'PC'].includes(code)) return '중기';
                if (['CP'].includes(code)) return '후기';
                return '초기';
            }
            
            const filteredFeatures = {
                type: 'FeatureCollection',
                features: cachedTaekjiGeoJSON.features.filter(f => {
                    const stepCode = f.properties.stepCode || f.properties.zoneCode || f.properties.zone_cd || ''; 
                    const stage = getTaekjiStage(stepCode);
                    return checkedStages.includes(stage);
                })
            };
            
            L.geoJSON(filteredFeatures, {
                style: function (feature) {
                    return {
                        fillColor: '#3b82f6',
                        weight: 2,
                        opacity: 0.8,
                        color: '#2563eb',
                        dashArray: '4',
                        fillOpacity: 0.15
                    };
                },
                onEachFeature: function (feature, layer) {
                    const props = feature.properties;
                    const stepCode = (props.stepCode || props.zoneCode || props.zone_cd || '').toUpperCase();
                    let stageName = '초기 단계 (지구지정 등)';
                    if (['SA'].includes(stepCode)) stageName = '초기 단계 (지구지정 등)';
                    else if (['DA', 'RA', 'PC'].includes(stepCode)) stageName = '중기 단계 (지구계획승인 등)';
                    else if (['CP'].includes(stepCode)) stageName = '후기 단계 (착공/분양/완료 등)';
                    
                    layer.bindTooltip(`<b>택지지구 (${stageName})</b><br>${props.zoneName || '이름 없음'}`, {
                        sticky: true,
                        className: 'custom-tooltip'
                    });
                }
            }).addTo(layers.dev1);
            
            triggerHighlighter();
        }

        function getRedevelopmentStage(propelCd) {
            if (!propelCd) return '초기';
            const code = propelCd.toUpperCase();
            
            const middleCodes = [
                'PP0208', 'PP0305', 'PP0503', 'PP0603', 'PP0704', 'PP1110', 'PP1504',
                'PP1401', 'PP1402', 'PP1403', 'PP1404', 'PP1405'
            ];
            if (middleCodes.includes(code)) return '중기';
            
            const lateCodes = [
                'PP0209', 'PP0210', 'PP0211',
                'PP0504', 'PP0505',
                'PP0604', 'PP0605',
                'PP0705', 'PP0706',
                'PP1111', 'PP1112', 'PP1113',
                'PP1206', 'PP1207', 'PP1208', 'PP1209',
                'PP1306',
                'PP1406', 'PP1407',
                'PP1505', 'PP1506', 'PP1507',
                'PP1604',
                'PP1809', 'PP1810',
                'PP1901',
                'PP2006', 'PP2007'
            ];
            if (lateCodes.includes(code)) return '후기';
            
            return '초기';
        }

        async function fetchRedevelopmentZones() {
            if (map.getZoom() < minZoomRequired) return;
            if (!document.getElementById('toggle-dev3').checked) return;
            
            const checkedStages = Array.from(document.querySelectorAll('.dev3-stage-check:checked')).map(cb => cb.value);
            if (checkedStages.length === 0) {
                layers.dev3.clearLayers();
                triggerHighlighter();
                return;
            }
            
            const bounds = map.getBounds();
            const isCached = cachedRedevelopmentZonesZoom === map.getZoom() && 
                             cachedRedevelopmentZonesBounds && 
                             cachedRedevelopmentZonesBounds.contains(bounds) && 
                             cachedRedevelopmentZonesData;

            let data;
            if (isCached) {
                console.log("Redevelopment zones loaded from cache (within bounds).");
                data = cachedRedevelopmentZonesData;
            } else {
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
                    const res = await fetch(`/api/map/redevelopment_zones?min_lat=${paddedBounds.getSouth()}&max_lat=${paddedBounds.getNorth()}&min_lng=${paddedBounds.getWest()}&max_lng=${paddedBounds.getEast()}`);
                    const json = await res.json();
                    if (json.status === 'success') {
                        cachedRedevelopmentZonesData = json.data;
                        cachedRedevelopmentZonesBounds = paddedBounds;
                        cachedRedevelopmentZonesZoom = map.getZoom();
                        data = cachedRedevelopmentZonesData;
                    } else {
                        return;
                    }
                } catch (err) {
                    console.error("Failed to fetch redevelopment zones:", err);
                    return;
                }
            }

            layers.dev3.clearLayers();
            data.forEach(item => {
                const stage = getRedevelopmentStage(item.propel_cd);
                if (!checkedStages.includes(stage)) return;
                
                let geojson = JSON.parse(item.geojson);
                let stageLabel = '초기 단계 (조합설립 등)';
                if (stage === '중기') stageLabel = '중기 단계 (사업시행 등)';
                else if (stage === '후기') stageLabel = '후기 단계 (관리처분 등)';
                
                L.geoJSON(geojson, {
                    style: {
                        color: '#f97316',
                        fillColor: '#f97316',
                        fillOpacity: 0.15,
                        weight: 2,
                        dashArray: '5, 5'
                    }
                }).bindPopup(`<b>재개발/재건축구역 (${stageLabel})</b><br>${item.name}`).addTo(layers.dev3);
            });
            triggerHighlighter();
        }

        async function fetchZoningPolygons() {
            if (map.getZoom() < minZoomRequired) return;
            if (!document.getElementById('toggle-zoning').checked) return;
            
            const checkedZonings = Array.from(document.querySelectorAll('.zoning-class-check:checked')).map(cb => cb.value);
            if (checkedZonings.length === 0) {
                layers.zoning.clearLayers();
                triggerHighlighter();
                return;
            }
            
            const bounds = map.getBounds();
            const isCached = cachedZoningPolygonsZoom === map.getZoom() && 
                             cachedZoningPolygonsBounds && 
                             cachedZoningPolygonsBounds.contains(bounds) && 
                             cachedZoningPolygonsData;

            let data;
            if (isCached) {
                console.log("Zoning polygons loaded from cache (within bounds).");
                data = cachedZoningPolygonsData;
            } else {
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
                    const res = await fetch(`/api/map/zoning?min_lat=${paddedBounds.getSouth()}&max_lat=${paddedBounds.getNorth()}&min_lng=${paddedBounds.getWest()}&max_lng=${paddedBounds.getEast()}`);
                    const json = await res.json();
                    if (json.status === 'success') {
                        cachedZoningPolygonsData = json.data;
                        cachedZoningPolygonsBounds = paddedBounds;
                        cachedZoningPolygonsZoom = map.getZoom();
                        data = cachedZoningPolygonsData;
                    } else {
                        return;
                    }
                } catch (err) {
                    console.error("Failed to fetch zoning polygons:", err);
                    return;
                }
            }

            layers.zoning.clearLayers();
            data.forEach(item => {
                let geojson = JSON.parse(item.geojson);
                
                let color = '#6366f1';
                let zoningType = '기타';
                let name = item.name;

                if (name.includes('전용주거')) {
                    color = '#fef08a';
                    zoningType = '전용주거지역';
                } else if (name.includes('1종일반주거') || name.includes('제1종일반주거')) {
                    color = '#fef9c3';
                    zoningType = '1종일반주거지역';
                } else if (name.includes('2종일반주거') || name.includes('제2종일반주거')) {
                    color = '#fde047';
                    zoningType = '2종일반주거지역';
                } else if (name.includes('3종일반주거') || name.includes('제3종일반주거')) {
                    color = '#ca8a04';
                    zoningType = '3종일반주거지역';
                } else if (name.includes('준주거')) {
                    color = '#f97316';
                    zoningType = '준주거지역';
                } else if (name.includes('상업')) {
                    color = '#ef4444';
                    zoningType = '상업지역';
                } else if (name.includes('준공업')) {
                    color = '#94a3b8';
                    zoningType = '준공업지역';
                } else if (name.includes('일반공업')) {
                    color = '#64748b';
                    zoningType = '일반공업지역';
                } else if (name.includes('전용공업')) {
                    color = '#334155';
                    zoningType = '전용공업지역';
                } else if (name.includes('녹지') || name.includes('개발제한구역')) {
                    color = '#22c55e';
                    zoningType = '녹지지역';
                }

                if (!checkedZonings.includes(zoningType)) return;

                L.geoJSON(geojson, {
                    style: {
                        color: color,
                        fillColor: color,
                        fillOpacity: 0.12,
                        weight: 1.5,
                        opacity: 0.6
                    }
                }).bindPopup(`<b>용도지역 (${zoningType})</b><br>${item.name}`).addTo(layers.zoning);
            });
            triggerHighlighter();
        }

        async function fetchPlanningRoads() {
            if (map.getZoom() < minZoomRequired) return;
            if (!document.getElementById('toggle-planning-road').checked) return;
            
            const checkedRoads = Array.from(document.querySelectorAll('.planning-road-class-check:checked')).map(cb => cb.value);
            const isBufferEnabled = document.getElementById('toggle-planning-road-buffer').checked;
            
            if (checkedRoads.length === 0) {
                layers.planningRoad.clearLayers();
                triggerHighlighter();
                return;
            }
            
            const bounds = map.getBounds();
            const isCached = cachedPlanningRoadsZoom === map.getZoom() && 
                             cachedPlanningRoadsBounds && 
                             cachedPlanningRoadsBounds.contains(bounds) && 
                             cachedPlanningRoadsData;

            let data;
            if (isCached) {
                console.log("Planning roads loaded from cache (within bounds).");
                data = cachedPlanningRoadsData;
            } else {
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
                    const res = await fetch(`/api/map/planning_roads?min_lat=${paddedBounds.getSouth()}&max_lat=${paddedBounds.getNorth()}&min_lng=${paddedBounds.getWest()}&max_lng=${paddedBounds.getEast()}`);
                    const json = await res.json();
                    if (json.status === 'success') {
                        cachedPlanningRoadsData = json.data;
                        cachedPlanningRoadsBounds = paddedBounds;
                        cachedPlanningRoadsZoom = map.getZoom();
                        data = cachedPlanningRoadsData;
                    } else {
                        return;
                    }
                } catch (err) {
                    console.error("Failed to fetch planning roads:", err);
                    return;
                }
            }

            layers.planningRoad.clearLayers();
            data.forEach(item => {
                let geojson = JSON.parse(item.geojson);
                const roadClass = item.road_class || '';
                
                let roadType = '기타';
                let color = '#94a3b8';
                let weight = 1.5;
                let dashArray = '3, 3';
                
                if (roadClass.includes('대로')) {
                    roadType = '대로';
                    color = '#ef4444';
                    weight = 3;
                    dashArray = null;
                } else if (roadClass.includes('중로')) {
                    roadType = '중로';
                    color = '#f59e0b';
                    weight = 2.5;
                    dashArray = null;
                } else if (roadClass.includes('소로1')) {
                    roadType = '소로1류';
                    color = '#10b981';
                    weight = 2;
                    dashArray = null;
                } else if (roadClass.includes('소로2')) {
                    roadType = '소로2류';
                    color = '#3b82f6';
                    weight = 2;
                    dashArray = null;
                } else if (roadClass.includes('소로3')) {
                    roadType = '소로3류';
                    color = '#10b981';
                    weight = 2;
                    dashArray = '2, 3'; // 촘촘한 녹색 점선/파선
                }
                
                if (!checkedRoads.includes(roadType)) return;
                
                // 1. 도로 선 렌더링
                L.geoJSON(geojson, {
                    style: {
                        color: color,
                        weight: weight,
                        opacity: 0.85,
                        dashArray: dashArray
                    }
                }).bindPopup(`<b>도시계획도로 (${roadClass})</b><br>${item.name || '이름 없음'}`).addTo(layers.planningRoad);
                
                // 2. 10m 버퍼 렌더링 (Turf.js 사용)
                if (isBufferEnabled) {
                    try {
                        const buffered = turf.buffer(geojson, 0.01, {units: 'kilometers'});
                        L.geoJSON(buffered, {
                            style: {
                                color: '#ec4899',
                                fillColor: '#ec4899',
                                fillOpacity: 0.15,
                                weight: 1.5,
                                dashArray: '3, 3'
                            }
                        }).bindPopup(`<b>도시계획도로 10m 완충구역</b><br>${item.name || '이름 없음'}`).addTo(layers.planningRoad);
                    } catch (bufferErr) {
                        console.error('Turf buffer error:', bufferErr);
                    }
                }
            });
            triggerHighlighter();
        }

        window.toggleAllCheckboxes = function(className, checked) {
            const checkboxes = document.querySelectorAll('.' + className);
            checkboxes.forEach(cb => {
                cb.checked = checked;
            });
            if (className === 'dev1-stage-check') {
                const dev1Toggle = document.getElementById('toggle-dev1');
                if (dev1Toggle && dev1Toggle.checked) {
                    updateTaekjiLayer();
                }
            } else if (className === 'dev3-stage-check') {
                const dev3Toggle = document.getElementById('toggle-dev3');
                if (dev3Toggle && dev3Toggle.checked) {
                    fetchRedevelopmentZones();
                }
            } else if (className === 'zoning-class-check') {
                const zoningToggle = document.getElementById('toggle-zoning');
                if (zoningToggle && zoningToggle.checked) {
                    fetchZoningPolygons();
                }
            } else if (className === 'planning-road-class-check') {
                const roadToggle = document.getElementById('toggle-planning-road');
                if (roadToggle && roadToggle.checked) {
                    fetchPlanningRoads();
                }
            }
        };

        // --- 개발구역 및 도시계획 레이어 추가 함수 끝 ---





        let cachedRoadFlowBounds = null;
        let cachedRoadFlowZoom = null;

        async function fetchRoadFlows() {
            const roadFlowMinZoom = 16;
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
            
            // Read active day/time filters
            const dayVal = document.querySelector('input[name="road-flow-day"]:checked')?.value || 'weekday';
            const timeVal = document.querySelector('input[name="road-flow-time"]:checked')?.value || 'day';
            
            try {
                const res = await fetch(`/api/map/road_flows?min_lat=${paddedBounds.getSouth()}&max_lat=${paddedBounds.getNorth()}&min_lng=${paddedBounds.getWest()}&max_lng=${paddedBounds.getEast()}&day=${dayVal}&time_of_day=${timeVal}`);
                const json = await res.json();
                if (json.status === 'success') {
                    layers.roadFlows.clearLayers();
                    
                    // 획기적인 메모리 절감: SVGRenderer 강제를 해제하여 DOM 엘리먼트 부담 없이 글로벌 Canvas에 직접 렌더링
                    L.geoJSON(json.data, {
                        style: function (feature) {
                            const flow = feature.properties.avg_hourly_flow || 0;
                            let color = '#a3e635'; // 1,000명 미만: 연두색
                            let strokeWidth = 1.1;

                            if (flow >= 4000) {
                                color = '#7f1d1d'; // 4,000명 이상: 진한 자주/붉은색
                                strokeWidth = 4.5;
                            } else if (flow >= 3000) {
                                color = '#ef4444'; // 3,000명 이상: 붉은색
                                strokeWidth = 3.2;
                            } else if (flow >= 2000) {
                                color = '#f97316'; // 2,000명 이상: 주황색
                                strokeWidth = 2.2;
                            } else if (flow >= 1000) {
                                color = '#22c55e'; // 1,000명 이상: 초록색
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
                                if (e.target.options.opacity === 0) return;
                                e.target.setStyle({
                                    weight: e.target.options.weight + 1.5,
                                    opacity: 1.0
                                });
                            });

                            layer.on('mouseout', function (e) {
                                if (e.target.options.opacity === 0) return;
                                const flow = feature.properties.avg_hourly_flow || 0;
                                let originalWeight = 1.1;
                                if (flow >= 4000) originalWeight = 4.5;
                                else if (flow >= 3000) originalWeight = 3.2;
                                else if (flow >= 2000) originalWeight = 2.2;
                                else if (flow >= 1000) originalWeight = 1.6;
                                
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

                    // Apply current legend filter
                    const currentFilterVal = document.getElementById('legend-flow-filter').value;
                    filterRoadFlowsByLegend(currentFilterVal);
                }
            } catch (err) {
                console.error("Failed to fetch road flows:", err);
            } finally {
                triggerHighlighter();
            }
        }

        window.updateRoadFlowFilters = function() {
            cachedRoadFlowBounds = null;
            cachedRoadFlowZoom = null;
            fetchRoadFlows();
        };

        window.filterRoadFlowsByLegend = function(val) {
            const minFlowMap = {
                1: 0,
                2: 1000,
                3: 2000,
                4: 3000,
                5: 4000
            };
            const minFlow = minFlowMap[val] || 0;
            
            // Update UI value label
            const labelMap = {
                1: "전체",
                2: "1000명 이상",
                3: "2000명 이상",
                4: "3000명 이상",
                5: "4000명 이상"
            };
            const filterValLabel = document.getElementById('legend-filter-val');
            if (filterValLabel) {
                filterValLabel.textContent = labelMap[val];
            }
            
            // Update legend items visual styling (dim filtered out levels)
            for (let i = 1; i <= 5; i++) {
                const item = document.getElementById(`legend-item-${i}`);
                if (item) {
                    if (i < val) {
                        item.style.opacity = '0.25';
                        item.style.textDecoration = 'line-through';
                    } else {
                        item.style.opacity = '1';
                        item.style.textDecoration = 'none';
                    }
                }
            }
            
            // Filter map layers
            if (layers.roadFlows) {
                layers.roadFlows.eachLayer(function(geoJsonLayer) {
                    if (typeof geoJsonLayer.eachLayer === 'function') {
                        geoJsonLayer.eachLayer(function(layer) {
                            const flow = layer.feature.properties.avg_hourly_flow || 0;
                            if (flow < minFlow) {
                                layer.setStyle({ opacity: 0 });
                                layer.options.interactive = false;
                            } else {
                                layer.setStyle({ opacity: 0.85 });
                                layer.options.interactive = true;
                            }
                        });
                    }
                });
            }
        };

        window.makeElementDraggable = function(el) {
            if (!el) return;
            let pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
            const header = document.getElementById(el.id + '-header') || el;
            
            header.addEventListener('mousedown', dragStart);
            header.addEventListener('touchstart', dragStart, { passive: false });

            function dragStart(e) {
                if (e.target.tagName === 'INPUT' || e.target.closest('input')) {
                    return;
                }
                const clientX = e.type === 'touchstart' ? e.touches[0].clientX : e.clientX;
                const clientY = e.type === 'touchstart' ? e.touches[0].clientY : e.clientY;
                
                pos3 = clientX;
                pos4 = clientY;
                
                if (e.type === 'mousedown') {
                    e.preventDefault();
                    document.addEventListener('mouseup', dragEnd);
                    document.addEventListener('mousemove', dragMove);
                } else {
                    document.addEventListener('touchend', dragEnd);
                    document.addEventListener('touchmove', dragMove, { passive: false });
                }
            }

            function dragMove(e) {
                const clientX = e.type === 'touchmove' ? e.touches[0].clientX : e.clientX;
                const clientY = e.type === 'touchmove' ? e.touches[0].clientY : e.clientY;
                
                pos1 = pos3 - clientX;
                pos2 = pos4 - clientY;
                pos3 = clientX;
                pos4 = clientY;
                
                let newTop = el.offsetTop - pos2;
                let newLeft = el.offsetLeft - pos1;
                
                const maxLeft = window.innerWidth - el.offsetWidth;
                const maxTop = window.innerHeight - el.offsetHeight;
                if (newLeft < 0) newLeft = 0;
                if (newTop < 0) newTop = 0;
                if (newLeft > maxLeft) newLeft = maxLeft;
                if (newTop > maxTop) newTop = maxTop;
                
                el.style.top = newTop + "px";
                el.style.left = newLeft + "px";
                el.style.right = "auto";
            }

            function dragEnd(e) {
                document.removeEventListener('mouseup', dragEnd);
                document.removeEventListener('mousemove', dragMove);
                document.removeEventListener('touchend', dragEnd);
                document.removeEventListener('touchmove', dragMove);
            }
        };

        async function fetchPopulationHeatmap() {
            // No-op function (deleted population heatmap layer)
            return;
        }

        async function fetchResidentialHeatmap() {
            if (map.getZoom() < minZoomRequired) return;
            if (!document.getElementById('toggle-residential-heatmap').checked) return;
            const bounds = map.getBounds();
            const checkedRegions = Array.from(document.querySelectorAll('.region-checkbox:checked')).map(cb => cb.value);
            const regionsStr = checkedRegions.join(',');
            const regionsParam = checkedRegions.length > 0 ? `&regions=${checkedRegions.join(',')}` : '&regions=서울';
            
            const isCached = cachedResHeatmapZoom === map.getZoom() && 
                             cachedResHeatmapBounds && 
                             cachedResHeatmapBounds.contains(bounds) && 
                             cachedResHeatmapRegions === regionsStr &&
                             cachedResHeatmapData;

            let data;
            let lat_step = 0.00225;
            let lng_step = 0.0028;

            if (isCached) {
                console.log("Residential Heatmap loaded from cache.");
                data = cachedResHeatmapData.data;
                lat_step = cachedResHeatmapData.lat_step;
                lng_step = cachedResHeatmapData.lng_step;
            } else {
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
                    const res = await fetch(`/api/map/grid_demographics?type=residential&min_lat=${paddedBounds.getSouth()}&max_lat=${paddedBounds.getNorth()}&min_lng=${paddedBounds.getWest()}&max_lng=${paddedBounds.getEast()}${regionsParam}`);
                    const json = await res.json();
                    if (json.status === 'success') {
                        cachedResHeatmapData = {
                            data: json.data,
                            lat_step: json.lat_step || 0.00225,
                            lng_step: json.lng_step || 0.0028
                        };
                        cachedResHeatmapBounds = paddedBounds;
                        cachedResHeatmapZoom = map.getZoom();
                        cachedResHeatmapRegions = regionsStr;
                        
                        data = cachedResHeatmapData.data;
                        lat_step = cachedResHeatmapData.lat_step;
                        lng_step = cachedResHeatmapData.lng_step;
                    } else {
                        return;
                    }
                } catch (err) {
                    console.error("Residential Heatmap fetch error:", err);
                    return;
                }
            }

            layers.resHeatmap.clearLayers();
            
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
                        
                        // 하위 7단계 삭제 (상위 30%만 표시)
                        if (step <= 7) return;

                        let color;
                        let classification;
                        if (step === 10) {
                            color = '#ea580c'; // 상위 10% (진한 오렌지)
                            classification = "상위 10% 이내";
                        } else {
                            color = '#facc15'; // 상위 30% (노란색)
                            classification = "상위 30% 이내";
                        }
                        
                        const lat = item.lat;
                        const lng = item.lng;
                        
                        // 250m x 250m grid rectangle centered around lat/lng
                        const halfLat = lat_step / 2;
                        const halfLng = lng_step / 2;
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
                        }).bindPopup(`<b>거주인구 격자 (${regionLabel})</b><br>구분: ${classification}<br>밀집도: ${step}단계<br>인구수: ${Math.round(item.avg_population).toLocaleString()}명`)
                          .addTo(layers.resHeatmap);
                    });

                });
            }
        }

        async function fetchWorkplaceHeatmap() {
            if (map.getZoom() < minZoomRequired) return;
            if (!document.getElementById('toggle-workplace-heatmap').checked) return;
            const bounds = map.getBounds();
            const checkedRegions = Array.from(document.querySelectorAll('.region-checkbox:checked')).map(cb => cb.value);
            const regionsStr = checkedRegions.join(',');
            const regionsParam = checkedRegions.length > 0 ? `&regions=${checkedRegions.join(',')}` : '&regions=서울';
            
            const isCached = cachedWorkHeatmapZoom === map.getZoom() && 
                             cachedWorkHeatmapBounds && 
                             cachedWorkHeatmapBounds.contains(bounds) && 
                             cachedWorkHeatmapRegions === regionsStr &&
                             cachedWorkHeatmapData;

            let data;
            let lat_step = 0.00225;
            let lng_step = 0.0028;

            if (isCached) {
                console.log("Workplace Heatmap loaded from cache.");
                data = cachedWorkHeatmapData.data;
                lat_step = cachedWorkHeatmapData.lat_step;
                lng_step = cachedWorkHeatmapData.lng_step;
            } else {
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
                    const res = await fetch(`/api/map/grid_demographics?type=workplace&min_lat=${paddedBounds.getSouth()}&max_lat=${paddedBounds.getNorth()}&min_lng=${paddedBounds.getWest()}&max_lng=${paddedBounds.getEast()}${regionsParam}`);
                    const json = await res.json();
                    if (json.status === 'success') {
                        cachedWorkHeatmapData = {
                            data: json.data,
                            lat_step: json.lat_step || 0.00225,
                            lng_step: json.lng_step || 0.0028
                        };
                        cachedWorkHeatmapBounds = paddedBounds;
                        cachedWorkHeatmapZoom = map.getZoom();
                        cachedWorkHeatmapRegions = regionsStr;
                        
                        data = cachedWorkHeatmapData.data;
                        lat_step = cachedWorkHeatmapData.lat_step;
                        lng_step = cachedWorkHeatmapData.lng_step;
                    } else {
                        return;
                    }
                } catch (err) {
                    console.error("Workplace Heatmap fetch error:", err);
                    return;
                }
            }

            layers.workHeatmap.clearLayers();
            
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
                        
                        // 하위 7단계 삭제 (상위 30%만 표시)
                        if (step <= 7) return;

                        let color;
                        let classification;
                        if (step === 10) {
                            color = '#6366f1'; // 상위 10% (진한 보라)
                            classification = "상위 10% 이내";
                        } else {
                            color = '#c084fc'; // 상위 30% (연한 보라)
                            classification = "상위 30% 이내";
                        }
                        
                        const lat = item.lat;
                        const lng = item.lng;
                        
                        // 250m x 250m grid rectangle centered around lat/lng
                        const halfLat = lat_step / 2;
                        const halfLng = lng_step / 2;
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
                        }).bindPopup(`<b>직장인구 격자 (${regionLabel})</b><br>구분: ${classification}<br>밀집도: ${step}단계<br>종사자수: ${Math.round(item.avg_population).toLocaleString()}명`)
                          .addTo(layers.workHeatmap);
                    });

                });
            }
        }

        function getAuctionFilterState() {
            const isAuctionActive = document.getElementById('btn-auction').classList.contains('active');
            const isPublicActive = document.getElementById('btn-public').classList.contains('active');
            const checkedTypes = Array.from(document.querySelectorAll('#property-type-grid input:checked')).map(cb => cb.value).join(',');
            const checkedSpecialRights = Array.from(document.querySelectorAll('#special-rights-grid input:checked')).map(cb => cb.value).join(',');
            const checkedLandPrices = Array.from(document.querySelectorAll('#land-price-grid input:checked')).map(cb => cb.value).join(',');
            const rateLimit = document.getElementById('rate-slider').value;
            const minArea = document.getElementById('min-area').value;
            const maxArea = document.getElementById('max-area').value;
            const useSubwayDist = document.getElementById('toggle-subways').checked;
            const useUnivDist = document.getElementById('toggle-univs').checked;
            const useIndDist = document.getElementById('toggle-inds').checked;
            const subwayDist = document.getElementById('buffer-subways').value;
            const univDist = document.getElementById('buffer-univs').value;
            const indDist = document.getElementById('buffer-inds').value;
            const reqElite = document.getElementById('toggle-middles') ? document.getElementById('toggle-middles').checked : false;
            const minHouseholds = document.getElementById('min-households') ? document.getElementById('min-households').value : '';
            const checkedRegions = Array.from(document.querySelectorAll('.region-checkbox:checked')).map(cb => cb.value).join(',');

            return `${isAuctionActive}_${isPublicActive}_${checkedTypes}_${checkedSpecialRights}_${checkedLandPrices}_${rateLimit}_${minArea}_${maxArea}_${useSubwayDist}_${useUnivDist}_${useIndDist}_${subwayDist}_${univDist}_${indDist}_${reqElite}_${minHouseholds}_${checkedRegions}`;
        }

        function buildAuctionUrl(basePath, customBounds) {
            const bounds = customBounds || map.getBounds();
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
                cachedAuctionsData = null;
                cachedAuctionsBounds = null;
                cachedAuctionsZoom = null;
                cachedAuctionsFilterState = '';
                return;
            } else {
                if (zoomWarning) {
                    zoomWarning.style.opacity = '0';
                    setTimeout(() => { zoomWarning.style.display = 'none'; }, 300);
                }
            }

            const bounds = map.getBounds();
            const currentFilterState = getAuctionFilterState();

            const isCached = cachedAuctionsZoom === map.getZoom() && 
                             cachedAuctionsBounds && 
                             cachedAuctionsBounds.contains(bounds) && 
                             cachedAuctionsFilterState === currentFilterState &&
                             cachedAuctionsData;

            let data;
            if (isCached) {
                console.log("Auctions loaded from cache.");
                data = cachedAuctionsData;
            } else {
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

                const url = buildAuctionUrl('/api/map/auctions', paddedBounds);
                if (!url) {
                    layers.auction.clearLayers();
                    return;
                }

                try {
                    const res = await fetch(url);
                    const json = await res.json();

                    if (json.status === 'success') {
                        cachedAuctionsData = json.data;
                        cachedAuctionsBounds = paddedBounds;
                        cachedAuctionsZoom = map.getZoom();
                        cachedAuctionsFilterState = currentFilterState;
                        data = cachedAuctionsData;
                    } else {
                        return;
                    }
                } catch (err) {
                    console.error("Auction load error:", err);
                    return;
                }
            }

            layers.auction.clearLayers();

            data.forEach(item => {
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
                    
                    let cleanNotes = d.special_notes ? d.special_notes.replace(/0|#|A|미해당/gi, '').replace(/,/g, ' ').replace(/\s+/g, ' ').trim() : '';
                    let escapedAddress = (d.address || '').replace(/'/g, "\\'");

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
                            <button onclick="openDemandPanel(${d.lat}, ${d.lng}, '${d.case_no}', '${escapedAddress}', '${d.property_type}', ${d.area_size || 0}); map.closePopup();" style="width:100%; background:#8b5cf6; color:white; border:none; padding:12px 10px; border-radius:6px; cursor:pointer; font-size:1rem; font-weight:bold; margin-top: 8px; touch-action:manipulation;"><i class="fa-solid fa-chart-simple"></i> 환경분석</button>
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

            triggerHighlighter();
        } // End of loadAuctions

        // Toggles mapping
            const toggleMap = {
                'toggle-subways': [layers.subway, layers.subwayLine],
                'toggle-univs': [layers.univ],
                'toggle-middles': [layers.middle],
                'toggle-inds': [layers.ind],
                'toggle-commercial': [layers.commercial],
                'toggle-dev2': [layers.dev2],
                'toggle-dev3': [layers.dev3],
                'toggle-zoning': [layers.zoning],
                'toggle-planning-road': [layers.planningRoad],
                
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

            // 개발구역 및 도시계획 세부 컨트롤러 이벤트 리스너 바인딩
            document.getElementById('toggle-dev1').addEventListener('change', updateTaekjiLayer);
            document.querySelectorAll('.dev1-stage-check').forEach(cb => {
                cb.addEventListener('change', updateTaekjiLayer);
            });

            document.getElementById('toggle-dev3').addEventListener('change', (e) => {
                const subContainer = document.getElementById('dev3-sub-container');
                if (e.target.checked) {
                    if (subContainer) subContainer.style.display = 'block';
                    fetchRedevelopmentZones();
                } else {
                    if (subContainer) subContainer.style.display = 'none';
                    layers.dev3.clearLayers();
                }
            });
            document.querySelectorAll('.dev3-stage-check').forEach(cb => {
                cb.addEventListener('change', fetchRedevelopmentZones);
            });

            document.getElementById('toggle-zoning').addEventListener('change', (e) => {
                const subContainer = document.getElementById('zoning-sub-container');
                if (e.target.checked) {
                    if (subContainer) subContainer.style.display = 'block';
                    fetchZoningPolygons();
                } else {
                    if (subContainer) subContainer.style.display = 'none';
                    layers.zoning.clearLayers();
                }
            });
            document.querySelectorAll('.zoning-class-check').forEach(cb => {
                cb.addEventListener('change', fetchZoningPolygons);
            });

            document.getElementById('toggle-planning-road').addEventListener('change', (e) => {
                const subContainer = document.getElementById('planning-road-sub-container');
                if (e.target.checked) {
                    if (subContainer) subContainer.style.display = 'block';
                    fetchPlanningRoads();
                } else {
                    if (subContainer) subContainer.style.display = 'none';
                    layers.planningRoad.clearLayers();
                }
            });
            document.querySelectorAll('.planning-road-class-check').forEach(cb => {
                cb.addEventListener('change', fetchPlanningRoads);
            });

            document.getElementById('toggle-bus').addEventListener('change', (e) => {
                e.target.checked ? (map.addLayer(layers.bus), loadBusStops()) : map.removeLayer(layers.bus);
            });

            let cachedRealpriceData = null;
            let cachedRealpriceBounds = null;
            let cachedRealpriceZoom = null;
            let cachedRealpricePropType = '';
            let cachedRealpriceIndicator = '';

            async function fetchRealpriceGrids() {
                const toggle = document.getElementById('toggle-realprice-grids');
                if (!toggle || !toggle.checked) return;
                
                const minZoom = 14;
                if (map.getZoom() < minZoom) {
                    layers.realpriceGrid.clearLayers();
                    return;
                }
                
                const bounds = map.getBounds();
                const propType = document.getElementById('realprice-prop-type').value;
                const indicator = document.getElementById('realprice-indicator').value;
                
                const isCached = cachedRealpriceZoom === map.getZoom() && 
                                 cachedRealpriceBounds && 
                                 cachedRealpriceBounds.contains(bounds) && 
                                 cachedRealpricePropType === propType &&
                                 cachedRealpriceIndicator === indicator &&
                                 cachedRealpriceData;
                                 
                let data;
                if (isCached) {
                    data = cachedRealpriceData;
                } else {
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
                    
                    const url = `/api/map/realprice_indicators?min_lat=${paddedBounds.getSouth()}&max_lat=${paddedBounds.getNorth()}&min_lng=${paddedBounds.getWest()}&max_lng=${paddedBounds.getEast()}&property_type=${encodeURIComponent(propType)}&indicator_type=${indicator}`;
                    
                    try {
                        const res = await fetch(url);
                        const json = await res.json();
                        if (json.status === 'success') {
                            cachedRealpriceData = json.data;
                            cachedRealpriceBounds = paddedBounds;
                            cachedRealpriceZoom = map.getZoom();
                            cachedRealpricePropType = propType;
                            cachedRealpriceIndicator = indicator;
                            data = cachedRealpriceData;
                        } else {
                            return;
                        }
                    } catch (err) {
                        console.error("Failed to fetch real price indicators:", err);
                        return;
                    }
                }
                
                layers.realpriceGrid.clearLayers();
                if (!data || data.length === 0) return;
                
                // Calculate color scales based on value ranges
                const vals = data.map(d => d.val).filter(v => v > 0).sort((a, b) => a - b);
                if (vals.length === 0) return;
                
                const getGridColor = (val) => {
                    if (val <= 0) return '#ffffff';
                    const idx = vals.findIndex(v => v >= val);
                    const percentile = (idx + 1) / vals.length;
                    
                    // Color ramp depending on indicator type
                    if (indicator === 'jeonse_ratio') {
                        // Jeonse ratio: green scale
                        if (percentile >= 0.8) return '#065f46';
                        if (percentile >= 0.6) return '#047857';
                        if (percentile >= 0.4) return '#10b981';
                        if (percentile >= 0.2) return '#34d399';
                        return '#a7f3d0';
                    } else if (indicator === 'transaction_count') {
                        // Transaction count: blue scale
                        if (percentile >= 0.8) return '#1e3a8a';
                        if (percentile >= 0.6) return '#1d4ed8';
                        if (percentile >= 0.4) return '#3b82f6';
                        if (percentile >= 0.2) return '#60a5fa';
                        return '#93c5fd';
                    } else {
                        // Prices and ratios: red/orange scale
                        if (percentile >= 0.8) return '#991b1b';
                        if (percentile >= 0.6) return '#dc2626';
                        if (percentile >= 0.4) return '#f97316';
                        if (percentile >= 0.2) return '#fb923c';
                        return '#fed7aa';
                    }
                };
                
                const lat_step = 0.00225;
                const lng_step = 0.0028;
                const halfLat = lat_step / 2;
                const halfLng = lng_step / 2;
                
                data.forEach(item => {
                    if (item.val <= 0) return;
                    const rectBounds = [
                        [item.lat - halfLat, item.lng - halfLng],
                        [item.lat + halfLat, item.lng + halfLng]
                    ];
                    
                    const color = getGridColor(item.val);
                    
                    // Formulate value labels
                    let valStr = '';
                    let label = '';
                    if (indicator === 'avg_price_per_pyeong') {
                        valStr = `${Math.round(item.avg_price).toLocaleString()}만원/평`;
                        label = '평균 매매 평당가';
                    } else if (indicator === 'avg_deposit_per_pyeong') {
                        valStr = `${Math.round(item.avg_deposit).toLocaleString()}만원/평`;
                        label = '평균 전세 평당가';
                    } else if (indicator === 'jeonse_ratio') {
                        valStr = `${item.jeonse_ratio.toFixed(1)}%`;
                        label = '전세가율';
                    } else if (indicator === 'transaction_count') {
                        valStr = `${Math.round(item.count)}건`;
                        label = '최근 1년 거래량';
                    } else if (indicator === 'std_price_per_pyeong') {
                        valStr = `${Math.round(item.std_price).toLocaleString()}만원`;
                        label = '평당가 표준편차';
                    } else if (indicator === 'age_premium_ratio') {
                        valStr = item.age_premium > 0 ? `${item.age_premium.toFixed(2)}배` : '신/구축 정보없음';
                        label = '신축/구축 프리미엄 격차';
                    } else if (indicator === 'floor_sensitivity') {
                        valStr = item.floor_sensitivity > 0 ? `${item.floor_sensitivity.toFixed(2)}배` : '층별 정보없음';
                        label = '로얄층/저층 민감도';
                    }
                    
                    const rect = L.rectangle(rectBounds, {
                        color: color,
                        weight: 1,
                        opacity: 0.3,
                        fillColor: color,
                        fillOpacity: 0.4
                    });
                    
                    const popupContent = `
                        <div style="font-family:'Noto Sans KR'; min-width:180px; padding: 5px;">
                            <strong style="color:var(--primary-blue); font-size:0.95rem; display:block; margin-bottom:6px;">실거래 분석 격자 (${propType})</strong>
                            <table style="width:100%; font-size:0.8rem; border-collapse:collapse;">
                                <tr style="border-bottom:1px solid #f1f5f9;"><td style="color:gray; padding:4px 0;">지표명</td><td style="text-align:right; font-weight:bold; color:var(--text-dark);">${label}</td></tr>
                                <tr style="border-bottom:1px solid #f1f5f9;"><td style="color:gray; padding:4px 0;">현재 지표값</td><td style="text-align:right; font-weight:800; color:#ef4444;">${valStr}</td></tr>
                                <tr style="border-bottom:1px solid #f1f5f9;"><td style="color:gray; padding:4px 0;">평균 매매가</td><td style="text-align:right; font-weight:500;">${item.avg_price > 0 ? Math.round(item.avg_price).toLocaleString() + '만원/평' : '-'}</td></tr>
                                <tr style="border-bottom:1px solid #f1f5f9;"><td style="color:gray; padding:4px 0;">평균 전세가</td><td style="text-align:right; font-weight:500;">${item.avg_deposit > 0 ? Math.round(item.avg_deposit).toLocaleString() + '만원/평' : '-'}</td></tr>
                                <tr style="border-bottom:1px solid #f1f5f9;"><td style="color:gray; padding:4px 0;">전세가율</td><td style="text-align:right; font-weight:500;">${item.jeonse_ratio > 0 ? item.jeonse_ratio.toFixed(1) + '%' : '-'}</td></tr>
                                <tr style="border-bottom:1px solid #f1f5f9;"><td style="color:gray; padding:4px 0;">연간 거래수</td><td style="text-align:right; font-weight:500;">${item.count}건</td></tr>
                                <tr style="border-bottom:1px solid #f1f5f9;"><td style="color:gray; padding:4px 0;">신구축 격차</td><td style="text-align:right; font-weight:500;">${item.age_premium > 0 ? item.age_premium.toFixed(2) + '배' : '-'}</td></tr>
                                <tr><td style="color:gray; padding:4px 0;">로얄층 민감도</td><td style="text-align:right; font-weight:500;">${item.floor_sensitivity > 0 ? item.floor_sensitivity.toFixed(2) + '배' : '-'}</td></tr>
                            </table>
                        </div>
                    `;
                    
                    rect.bindPopup(popupContent);
                    rect.addTo(layers.realpriceGrid);
                });
            }

            window.updateRealpriceGrids = function() {
                cachedRealpriceBounds = null;
                cachedRealpriceZoom = null;
                fetchRealpriceGrids();
            };

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
                    
                    // 각 레이어 스위치가 실제로 활성화되어 있을 때만 API를 호출하도록 리팩토링
                    if (document.getElementById('toggle-subways').checked || 
                        document.getElementById('toggle-univs').checked || 
                        document.getElementById('toggle-middles').checked || 
                        document.getElementById('toggle-inds').checked || 
                        document.getElementById('toggle-commercial').checked) {
                        fetchInfraData();
                    }
                    if (document.getElementById('toggle-dev3').checked) {
                        fetchDistrictUnits();
                    }
                    if (document.getElementById('toggle-dev2').checked) {
                        updateTaekjiLayer();
                    }
                    if (document.getElementById('toggle-zoning').checked) {
                        fetchZoningPolygons();
                    }
                    if (document.getElementById('toggle-planning-road').checked) {
                        fetchPlanningRoads();
                    }
                    if (document.getElementById('toggle-residential-heatmap').checked) {
                        fetchResidentialHeatmap();
                    }
                    if (document.getElementById('toggle-workplace-heatmap').checked) {
                        fetchWorkplaceHeatmap();
                    }
                    if (document.getElementById('toggle-road-flows').checked) {
                        fetchRoadFlows();
                    }
                    
                    // 가격데이터 오버레이가 활성화되어 있을 때만 가격데이터를 업데이트하여 속도 최적화
                    const rpToggle = document.getElementById('toggle-realprice-grids');
                    if (rpToggle && rpToggle.checked) {
                        fetchRealpriceGrids();
                    }
                    
                    loadAuctions();
                }, 400); // 400ms debounce
            });

            document.getElementById('toggle-realprice-grids').addEventListener('change', (e) => {
                const subContainer = document.getElementById('realprice-sub-container');
                if (e.target.checked) {
                    if (subContainer) subContainer.style.display = 'flex';
                    map.addLayer(layers.realpriceGrid);
                    fetchRealpriceGrids();
                } else {
                    if (subContainer) subContainer.style.display = 'none';
                    layers.realpriceGrid.clearLayers();
                    map.removeLayer(layers.realpriceGrid);
                }
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
                const legend = document.getElementById('residential-legend');
                if (legend) legend.style.display = e.target.checked ? 'block' : 'none';
                if (e.target.checked) {
                    fetchResidentialHeatmap();
                }
            });

            document.getElementById('toggle-workplace-heatmap').addEventListener('change', (e) => {
                const legend = document.getElementById('workplace-legend');
                if (legend) legend.style.display = e.target.checked ? 'block' : 'none';
                if (e.target.checked) {
                    fetchWorkplaceHeatmap();
                }
            });

            document.getElementById('toggle-road-flows').addEventListener('change', (e) => {
                const subContainer = document.getElementById('road-flows-sub-container');
                const legend = document.getElementById('road-flow-legend');
                const slider = document.getElementById('legend-flow-filter');
                
                if (e.target.checked) {
                    if (slider) slider.value = 1;
                    fetchRoadFlows();
                    if (legend) legend.style.display = 'block';
                    if (subContainer) subContainer.style.display = 'block';
                } else {
                    layers.roadFlows.clearLayers();
                    cachedRoadFlowBounds = null;
                    cachedRoadFlowZoom = null;
                    if (legend) legend.style.display = 'none';
                    if (subContainer) subContainer.style.display = 'none';
                }
            });

            document.getElementById('toggle-old-buildings').addEventListener('change', async (e) => {
                if (e.target.checked) {
                    map.addLayer(layers.oldBuildings);
                    
                    const updateUIFromResolution = () => {
                        let resVal = '1km';
                        layers.oldBuildings.eachLayer(l => {
                            // Leaflet L.geoJson stores feature inside each layer or in a sub-group
                            const layersList = typeof l.getLayers === 'function' ? l.getLayers() : [l];
                            layersList.forEach(singleL => {
                                if (singleL.feature && singleL.feature.properties && singleL.feature.properties.resolution) {
                                    resVal = singleL.feature.properties.resolution;
                                }
                            });
                        });
                        const descSpan = document.querySelector('#toggle-old-buildings').closest('.toggle-row').querySelector('.toggle-desc');
                        if (descSpan) {
                            if (resVal === '250m') {
                                descSpan.textContent = '250m 격자 (250가구 이상, 노후도 60%~100% 밀집)';
                            } else {
                                descSpan.textContent = '1km 격자 (500가구 60% 이상 또는 1000가구 이상 밀집)';
                            }
                        }
                    };

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
                                    const resVal = props.resolution || '1km';
                                    const gridLabel = resVal === '250m' ? '250m 격자' : '1km 격자';
                                    layer.bindTooltip(`<b>노후화 집중 구역 (${gridLabel})</b><br>건축물: ${props.val} / ${props.total_val}개<br>노후화 비율: ${props.ratio_pct}%`, {
                                        sticky: true,
                                        className: 'custom-tooltip'
                                    });
                                }
                            }).addTo(layers.oldBuildings);
                            
                            updateUIFromResolution();
                        } catch (error) {
                            console.error('Error loading old buildings:', error);
                            alert('노후 건축물 데이터를 불러오는 데 실패했습니다.');
                        } finally {
                            if (loadingOverlay) loadingOverlay.style.display = 'none';
                        }
                    } else {
                        updateUIFromResolution();
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

            // Initialize road flow legend dragging
            makeElementDraggable(document.getElementById('road-flow-legend'));

            // Check initial state of toggle-road-flows
            const initialRoadFlowsToggle = document.getElementById('toggle-road-flows');
            if (initialRoadFlowsToggle && initialRoadFlowsToggle.checked) {
                const subContainer = document.getElementById('road-flows-sub-container');
                if (subContainer) subContainer.style.display = 'block';
                const legend = document.getElementById('road-flow-legend');
                if (legend) legend.style.display = 'block';
            }

            // Check initial state of population heatmap toggles
            const resToggle = document.getElementById('toggle-residential-heatmap');
            if (resToggle && resToggle.checked) {
                const resLegend = document.getElementById('residential-legend');
                if (resLegend) resLegend.style.display = 'block';
            }
            const workToggle = document.getElementById('toggle-workplace-heatmap');
            if (workToggle && workToggle.checked) {
                const workLegend = document.getElementById('workplace-legend');
                if (workLegend) workLegend.style.display = 'block';
            }

            // Remove loading overlay immediately so the user sees the map interface without delay
            const loadingOverlay = document.getElementById('loading');
            if (loadingOverlay) loadingOverlay.style.display = 'none';
            
            // Load main auction data in the background
            loadAuctions();
            setTimeout(() => {
                updateCenterAddress();
                
                // 초기 지연 실행 시에도 각 토글 스위치가 켜져 있을 때만 데이터를 비동기 로딩
                if (document.getElementById('toggle-subways') && document.getElementById('toggle-subways').checked) {
                    fetchSubwayLines();
                }
                if ((document.getElementById('toggle-subways') && document.getElementById('toggle-subways').checked) || 
                    (document.getElementById('toggle-univs') && document.getElementById('toggle-univs').checked) || 
                    (document.getElementById('toggle-middles') && document.getElementById('toggle-middles').checked) || 
                    (document.getElementById('toggle-inds') && document.getElementById('toggle-inds').checked) || 
                    (document.getElementById('toggle-commercial') && document.getElementById('toggle-commercial').checked)) {
                    fetchInfraData();
                }
                if (document.getElementById('toggle-hagwons') && document.getElementById('toggle-hagwons').checked) {
                    fetchHagwonPolygons();
                }
                if (document.getElementById('toggle-dev3') && document.getElementById('toggle-dev3').checked) {
                    fetchDistrictUnits();
                }
                if (document.getElementById('toggle-dev2') && document.getElementById('toggle-dev2').checked) {
                    updateTaekjiLayer();
                }
                if ((document.getElementById('toggle-residential-heatmap') && document.getElementById('toggle-residential-heatmap').checked) || 
                    (document.getElementById('toggle-workplace-heatmap') && document.getElementById('toggle-workplace-heatmap').checked)) {
                    fetchPopulationHeatmap();
                }
                if (document.getElementById('toggle-road-flows') && document.getElementById('toggle-road-flows').checked) {
                    fetchRoadFlows();
                }
            }, 100);

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

            async function openDemandPanel(lat, lng, caseNo, address, propType, areaSize) {
                const panel = document.getElementById('demand-panel');
                if (!panel) return;

                // Show the drawer panel
                panel.classList.add('open');

                // Display skeleton state while fetching
                showDemandSkeleton();

                // 주택 여부 판별
                const isRes = isResidential(propType);

                if (isRes) {
                    // 주택인 경우: 인구/지하철 분석과 실거래가 가격지표를 모두 패칭하여 융합 렌더링
                    try {
                        let demoUrl = `/api/map/demographics?lat=${lat}&lng=${lng}`;
                        if (address) {
                            demoUrl += `&address=${encodeURIComponent(address)}`;
                        }
                        if (areaSize !== undefined && areaSize !== null) {
                            demoUrl += `&area_size=${areaSize}`;
                        }
                        
                        const demoRes = await fetch(demoUrl);
                        if (!demoRes.ok) throw new Error('Demographics API request failed');
                        const demoJson = await demoRes.json();
                        
                        // 실거래가 가격지표 BBox 가져오기 (주변 250m 격자 포괄)
                        const minLat = lat - 0.003;
                        const maxLat = lat + 0.003;
                        const minLng = lng - 0.004;
                        const maxLng = lng + 0.004;
                        
                        let normPropType = '아파트';
                        if (propType.includes('다세대') || propType.includes('빌라')) {
                            normPropType = '다세대';
                        } else if (propType.includes('단독') || propType.includes('다중') || propType.includes('주거용건물')) {
                            normPropType = '단독';
                        } else if (propType.includes('오피스텔')) {
                            normPropType = '오피스텔';
                        }
                        
                        const priceUrl = `/api/map/realprice_indicators?min_lat=${minLat}&max_lat=${maxLat}&min_lng=${minLng}&max_lng=${maxLng}&property_type=${encodeURIComponent(normPropType)}&indicator_type=avg_price_per_pyeong`;
                        
                        const priceRes = await fetch(priceUrl);
                        if (!priceRes.ok) throw new Error('Price indicators API request failed');
                        const priceJson = await priceRes.json();
                        
                        if (demoJson.status === 'success' && priceJson.status === 'success') {
                            renderResidentialDemandData(demoJson, priceJson, caseNo, address, propType, lat, lng);
                        } else {
                            if (demoJson.status === 'success') {
                                renderResidentialDemandData(demoJson, { status: 'success', data: [] }, caseNo, address, propType, lat, lng);
                            } else {
                                throw new Error(demoJson.message || '인구 분석 데이터 오류');
                            }
                        }
                    } catch (err) {
                        console.error("Failed to load residential analytics:", err);
                        document.getElementById('demand-panel-content').innerHTML = `
                            <div class="demand-card" style="text-align: center; padding: 25px; color: #ef4444;">
                                <i class="fa-solid fa-triangle-exclamation" style="font-size: 2rem; margin-bottom: 10px;"></i>
                                <p style="font-weight: bold; margin: 0;">네트워크 및 데이터 분석 오류</p>
                                <p style="font-size: 0.8rem; color: var(--text-muted); margin-top: 5px;">백엔드 서버로부터 정보를 가져올 수 없습니다.</p>
                            </div>
                        `;
                    }
                } else {
                    // 비주택(구분상가, 건물, 지식산업센터 등)인 경우: 기존 배후수요 및 인구분석 사용
                    try {
                        let url = `/api/map/demographics?lat=${lat}&lng=${lng}`;
                        if (address) {
                            url += `&address=${encodeURIComponent(address)}`;
                        }
                        if (areaSize !== undefined && areaSize !== null) {
                            url += `&area_size=${areaSize}`;
                        }
                        const res = await fetch(url);
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

            function isResidential(propType) {
                if (!propType) return false;
                const p = propType.trim();
                return p.includes('아파트') || 
                       p.includes('다세대') || 
                       p.includes('단독') || 
                       p.includes('오피스텔') || 
                       p.includes('빌라') || 
                       p.includes('주상복합') || 
                       p.includes('다중주택') ||
                       p.includes('기타주거용건물');
            }

            function renderResidentialDemandData(resData, priceData, caseNo, address, propType, lat, lng) {
                const content = document.getElementById('demand-panel-content');
                if (!content) return;

                const sub = resData.subway_proximity;
                const demo = resData.demographics;

                // 250m 격자 매핑
                const latStep = 0.00225;
                const lngStep = 0.0028;
                const targetLatIdx = Math.floor(lat / latStep);
                const targetLngIdx = Math.floor(lng / lngStep);

                let matchedGrid = null;
                if (priceData && priceData.status === 'success' && priceData.data) {
                    matchedGrid = priceData.data.find(g => g.lat_idx === targetLatIdx && g.lng_idx === targetLngIdx);
                    if (!matchedGrid && priceData.data.length > 0) {
                        let minDist = Infinity;
                        priceData.data.forEach(g => {
                            const dist = Math.pow(g.lat - lat, 2) + Math.pow(g.lng - lng, 2);
                            if (dist < minDist) {
                                minDist = dist;
                                matchedGrid = g;
                            }
                        });
                    }
                }

                // 지하철 역 HTML 생성
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

                let gradeBadgeClass = 'subway-grade-비역세권';
                if (sub.grade === '초역세권') gradeBadgeClass = 'subway-grade-초역세권';
                else if (sub.grade === '역세권') gradeBadgeClass = 'subway-grade-역세권';

                // 실거래가 기반 가격지표 카드 렌더링 구성
                let priceCardHtml = "";
                let guideHtml = "";

                if (matchedGrid) {
                    const avgPriceStr = matchedGrid.avg_price > 0 ? `${(matchedGrid.avg_price).toFixed(0).toLocaleString()}만원` : '정보없음';
                    const avgDepositStr = matchedGrid.avg_deposit > 0 ? `${(matchedGrid.avg_deposit).toFixed(0).toLocaleString()}만원` : '정보없음';
                    const avgRentStr = matchedGrid.avg_rent > 0 ? `${(matchedGrid.avg_rent).toFixed(0).toLocaleString()}만원` : '정보없음';
                    const jeonseRatioStr = matchedGrid.jeonse_ratio > 0 ? `${matchedGrid.jeonse_ratio.toFixed(1)}%` : '정보없음';
                    const txCount = matchedGrid.count || 0;
                    
                    // 전세가율 진단 및 게이지
                    let jeonseStatus = "정보없음";
                    let jeonseColor = "var(--text-muted)";
                    let jeonseBarWidth = "0%";
                    if (matchedGrid.jeonse_ratio > 0) {
                        jeonseBarWidth = `${Math.min(100, matchedGrid.jeonse_ratio)}%`;
                        if (matchedGrid.jeonse_ratio >= 80) {
                            jeonseStatus = "⚠️ 매우 높음 (깡통유의/갭투자용이)";
                            jeonseColor = "#d97706";
                        } else if (matchedGrid.jeonse_ratio >= 65) {
                            jeonseStatus = "✅ 안정적 (임대수요 풍부)";
                            jeonseColor = "#16a34a";
                        } else if (matchedGrid.jeonse_ratio >= 50) {
                            jeonseStatus = "ℹ️ 보통 (실거주 양호)";
                            jeonseColor = "#2563eb";
                        } else {
                            jeonseStatus = "📉 낮음 (투자금 높음/매매강세)";
                            jeonseColor = "#dc2626";
                        }
                    }

                    // 거래 활성 등급
                    let txStatus = "정보없음";
                    let txColor = "var(--text-muted)";
                    if (txCount >= 15) {
                        txStatus = "🔥 매우 활발 (환금성 최우수)";
                        txColor = "#dc2626";
                    } else if (txCount >= 5) {
                        txStatus = "✅ 보통 (환금성 안정)";
                        txColor = "#16a34a";
                    } else {
                        txStatus = "⚠️ 다소 저조 (환금성 유의)";
                        txColor = "#cbd5e1";
                    }

                    // 연식 프리미엄 진단
                    let agePremStr = "정보없음";
                    if (matchedGrid.age_premium > 0) {
                        agePremStr = `${matchedGrid.age_premium.toFixed(2)}배`;
                        if (matchedGrid.age_premium >= 1.15) {
                            agePremStr += " (신축선호 우수)";
                        } else if (matchedGrid.age_premium >= 1.0) {
                            agePremStr += " (연식 영향 보통)";
                        } else {
                            agePremStr += " (구축 선호/재건축 기대)";
                        }
                    }

                    // 층수 민감도 진단
                    let floorSensStr = "정보없음";
                    if (matchedGrid.floor_sensitivity > 0) {
                        floorSensStr = `${matchedGrid.floor_sensitivity.toFixed(2)}배`;
                        if (matchedGrid.floor_sensitivity >= 1.1) {
                            floorSensStr += " (로얄층 선호 뚜렷)";
                        } else {
                            floorSensStr += " (층별 영향 미미)";
                        }
                    }

                    priceCardHtml = `
                        <!-- Realprice indicator stats -->
                        <div class="demand-card">
                            <div class="demand-card-title">
                                <i class="fa-solid fa-coins" style="color: #eab308;"></i> 최근 1년 실거래 가격지표 (250m 격자)
                            </div>
                            <div class="demand-grid" style="margin-bottom: 12px;">
                                <div class="demand-stat-item">
                                    <div class="demand-stat-label">평당 평균매매가</div>
                                    <div class="demand-stat-value" style="color: #ef4444;">${avgPriceStr}</div>
                                </div>
                                <div class="demand-stat-item">
                                    <div class="demand-stat-label">평당 평균전세가</div>
                                    <div class="demand-stat-value" style="color: #3b82f6;">${avgDepositStr}</div>
                                </div>
                            </div>
                            
                            <!-- Detailed parameters -->
                            <div style="font-size: 0.75rem; display: flex; flex-direction: column; gap: 8px;">
                                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(226,232,240,0.5); padding-bottom: 4px;">
                                    <span style="color: var(--text-muted);">평균 월세금액</span>
                                    <span style="font-weight: bold; color: var(--text-dark);">${avgRentStr}</span>
                                </div>
                                
                                <div style="display: flex; flex-direction: column; gap: 3px; border-bottom: 1px solid rgba(226,232,240,0.5); padding-bottom: 6px;">
                                    <div style="display: flex; justify-content: space-between; align-items: center;">
                                        <span style="color: var(--text-muted);">전세가율</span>
                                        <span style="font-weight: bold; color: ${jeonseColor};">${jeonseRatioStr} (${jeonseStatus})</span>
                                    </div>
                                    \${matchedGrid.jeonse_ratio > 0 ? `
                                    <div style="height: 6px; background: #e2e8f0; border-radius: 3px; overflow: hidden; width: 100%;">
                                        <div style="width: \${jeonseBarWidth}; height: 100%; background: \${jeonseColor}; border-radius: 3px;"></div>
                                    </div>
                                    ` : ''}
                                </div>

                                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(226,232,240,0.5); padding-bottom: 4px;">
                                    <span style="color: var(--text-muted);">최근 1년 거래건수</span>
                                    <span style="font-weight: bold; color: var(--text-dark);">\${txCount}건 <span style="font-size:0.7rem; color:\${txColor}; font-weight:bold;">(\${txStatus})</span></span>
                                </div>

                                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(226,232,240,0.5); padding-bottom: 4px;">
                                    <span style="color: var(--text-muted);">신축 프리미엄비율</span>
                                    <span style="font-weight: bold; color: var(--text-dark);">\${agePremStr}</span>
                                </div>

                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <span style="color: var(--text-muted);">로얄층 민감도</span>
                                    <span style="font-weight: bold; color: var(--text-dark);">\${floorSensStr}</span>
                                </div>
                            </div>
                        </div>
                    `;

                    // 가이드 텍스트 자동 구성
                    let strategy = "";
                    if (matchedGrid.jeonse_ratio >= 75) {
                        strategy += `본 격자는 전세가율이 <strong>\${matchedGrid.jeonse_ratio.toFixed(1)}%</strong>로 높은 편에 속합니다. 매매가 대비 임차 보증금이 많아 적은 자기자본으로 갭투자가 가능하지만, 임차인 보증금 미반환 리스크(역전세)가 있을 수 있으므로 주의깊게 검토하십시오. `;
                    } else if (matchedGrid.jeonse_ratio >= 60) {
                        strategy += `본 격자는 전세가율이 <strong>\${matchedGrid.jeonse_ratio.toFixed(1)}%</strong>로 안정적인 범위를 보입니다. 주거 및 임대 배후수요가 견고하여 임차 매칭이 원활할 것으로 판단됩니다. `;
                    } else if (matchedGrid.jeonse_ratio > 0) {
                        strategy += `본 격자는 전세가율이 <strong>\${matchedGrid.jeonse_ratio.toFixed(1)}%</strong>로 비교적 낮게 형성되어 있습니다. 레버리지 효과가 낮으므로 인수 후 실거주 매도 전략이나 대출 비중 등 자금 조달 계획을 꼼꼼히 설계하십시오. `;
                    } else {
                        strategy += `전세 실거래 정보가 집계되지 않았습니다. 실거주용 매매 가치 산정에 포커스를 맞추시기 바랍니다. `;
                    }

                    if (txCount >= 15) {
                        strategy += `또한 최근 1년 거래 건수가 <strong>\${txCount}건</strong>으로 시장 회전률이 뛰어난 곳이므로 매도 시 환금성이 최우수합니다.`;
                    } else if (txCount >= 5) {
                        strategy += `또한 최근 1년 거래 건수는 <strong>\${txCount}건</strong> 수준으로 평이한 수준의 유동성을 보입니다.`;
                    } else {
                        strategy += `또한 최근 1년 간 격자 거래량이 <strong>\${txCount}건</strong>으로 침체되어 있으므로 매도 시 처분 기간이 길어질 위험을 감수하고 가격 경쟁력을 확보해야 합니다.`;
                    }

                    guideHtml = `
                        <div class="demand-card" style="background: rgba(37, 99, 235, 0.05); border: 1px dashed rgba(37, 99, 235, 0.3);">
                            <div class="demand-card-title" style="color: var(--primary-blue); font-size: 0.9rem; margin-bottom: 5px;">
                                <i class="fa-solid fa-lightbulb"></i> 주택 매매 및 임대 전략 가이드
                            </div>
                            <div style="font-size: 0.8rem; line-height: 1.5; color: var(--text-dark); word-break: keep-all;">
                                \${strategy}
                            </div>
                        </div>
                    `;

                } else {
                    priceCardHtml = `
                        <div class="demand-card">
                            <div class="demand-card-title" style="color: #ea580c;">
                                <i class="fa-solid fa-coins"></i> 실거래 가격 정보 (250m 격자)
                            </div>
                            <div style="text-align: center; color: var(--text-muted); font-size: 0.75rem; padding: 20px 0;">
                                <i class="fa-solid fa-circle-exclamation" style="font-size: 1.5rem; margin-bottom: 5px; color:#cbd5e1;"></i>
                                <br>이 지역 격자 내에 최근 1년간 수집된<br>\${propType} 실거래 데이터가 부족합니다.
                            </div>
                        </div>
                    `;

                    guideHtml = `
                        <div class="demand-card" style="background: rgba(239, 68, 68, 0.05); border: 1px dashed rgba(239, 68, 68, 0.3);">
                            <div class="demand-card-title" style="color: #ef4444; font-size: 0.9rem; margin-bottom: 5px;">
                                <i class="fa-solid fa-triangle-exclamation"></i> 투자 유의 사항
                            </div>
                            <div style="font-size: 0.8rem; line-height: 1.5; color: var(--text-dark); word-break: keep-all;">
                                현재 경공매 물건 근방에 실거래가 축적되지 않았습니다. 실거래가 지표가 낮을 시 지도의 '실거래 가격지표' 오버레이 기능을 활성화하여 더 넓은 반경의 시세 흐름을 분석하시길 권장합니다.
                            </div>
                        </div>
                    `;
                }

                // 주거 인구 정보 요약도 함께 보여줌
                const resPop = demo.residential_population || 0;
                const house = demo.households || 0;

                content.innerHTML = `
                    <!-- Address & Case Metadata -->
                    <div class="demand-card" style="border-left: 4px solid var(--primary-blue); background: rgba(255, 255, 255, 0.9);">
                        <div style="font-size: 0.75rem; font-weight: bold; color: var(--primary-blue); margin-bottom: 2px;">
                            \${propType} | \${caseNo}
                        </div>
                        <div style="font-size: 0.95rem; font-weight: bold; color: var(--text-dark); margin-bottom: 4px; line-height: 1.3;">
                            \${address}
                        </div>
                        <div style="font-size: 0.7rem; color: var(--text-muted); display: flex; align-items: center; gap: 4px;">
                            <i class="fa-solid fa-house"></i> 주택 입지 및 거래/임대지표 분석 정보
                        </div>
                    </div>

                    <!-- Real Price Indicators -->
                    \${priceCardHtml}

                    <!-- Subway Proximity -->
                    <div class="demand-card">
                        <div class="demand-card-title" style="margin-bottom: 6px;">
                            <i class="fa-solid fa-train-subway" style="color: #10b981;"></i> 대중교통 입지 분석
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <span style="font-size: 0.8rem; font-weight: bold; color: var(--text-dark);">지하철 접근성</span>
                            <span class="demand-subway-badge \${gradeBadgeClass}">\${sub.grade}</span>
                        </div>
                        <div class="demand-subway-list">
                            \${subwayListHtml}
                        </div>
                    </div>

                    <!-- Residential Population & Households -->
                    <div class="demand-card">
                        <div class="demand-card-title">
                            <i class="fa-solid fa-house-chimney-user" style="color: #ea580c;"></i> 반경 500m 거주 배후수요
                        </div>
                        <div class="demand-grid">
                            <div class="demand-stat-item">
                                <div class="demand-stat-label">거주인구</div>
                                <div class="demand-stat-value" style="color: #ea580c;">\${Number(resPop).toLocaleString()}<span style="font-size: 0.75rem; font-weight: normal; margin-left: 2px;">명</span></div>
                            </div>
                            <div class="demand-stat-item">
                                <div class="demand-stat-label">세대수</div>
                                <div class="demand-stat-value">\${Number(house).toLocaleString()}<span style="font-size: 0.75rem; font-weight: normal; margin-left: 2px;">세대</span></div>
                            </div>
                        </div>
                    </div>

                    <!-- Strategy Guide -->
                    \${guideHtml}
                `;
            }
        
