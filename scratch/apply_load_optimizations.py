import re

file_path = r"c:\Users\llll\Documents\두인경매\바이브코딩\public\map.html"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

content_lf = content.replace("\r\n", "\n")

# 1. Replace the moveend debouncer to remove updateTaekjiLayer()
moveend_target = """                    fetchInfraData();
                    fetchDistrictUnits();
                    updateTaekjiLayer();
                    fetchRedevelopmentZones();"""

moveend_replacement = """                    fetchInfraData();
                    fetchDistrictUnits();
                    // updateTaekjiLayer()는 static GeoJSON이므로 드래그 시마다 다시 그리지 않고 최초 로드 및 필터 변경 시에만 그리도록 최적화
                    fetchRedevelopmentZones();"""

content_lf = content_lf.replace(moveend_target, moveend_replacement)

# 2. Overwrite fetchRedevelopmentZones, fetchZoningPolygons, and fetchPlanningRoads with smart bounds caching & zoom-level limits
old_functions_pattern = re.compile(
    r'async function fetchRedevelopmentZones\(\)\s*\{.*?async function fetchZoningPolygons\(\)\s*\{.*?async function fetchPlanningRoads\(\)\s*\{.*?\}\s*\}', 
    re.DOTALL
)

# Wait, let's look at the exact block from L1945 to L2145 using regex
# We can do this easily by writing replacement blocks for each function precisely!

redev_old = """        async function fetchRedevelopmentZones() {
            if (map.getZoom() < minZoomRequired) return;
            if (!document.getElementById('toggle-dev3').checked) return;
            
            const checkedStages = Array.from(document.querySelectorAll('.dev3-stage-check:checked')).map(cb => cb.value);
            if (checkedStages.length === 0) {
                layers.dev3.clearLayers();
                triggerHighlighter();
                return;
            }
            
            const bounds = map.getBounds();
            try {
                const res = await fetch(`/api/map/redevelopment_zones?min_lat=${bounds.getSouth()}&max_lat=${bounds.getNorth()}&min_lng=${bounds.getWest()}&max_lng=${bounds.getEast()}`);
                const json = await res.json();
                if (json.status === 'success') {
                    layers.dev3.clearLayers();
                    json.data.forEach(item => {
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
                }
            } catch (err) { console.error(err); } finally { triggerHighlighter(); }
        }"""

redev_new = """        // 스마트 캐싱용 바운더리 및 줌 레벨 저장 변수
        let cachedRedevBounds = null;
        let cachedRedevZoom = null;

        async function fetchRedevelopmentZones() {
            const redevMinZoom = 13;
            const currentZoom = map.getZoom();
            if (currentZoom < redevMinZoom) {
                layers.dev3.clearLayers();
                cachedRedevBounds = null;
                cachedRedevZoom = null;
                return;
            }
            if (!document.getElementById('toggle-dev3').checked) return;
            
            const checkedStages = Array.from(document.querySelectorAll('.dev3-stage-check:checked')).map(cb => cb.value);
            if (checkedStages.length === 0) {
                layers.dev3.clearLayers();
                triggerHighlighter();
                return;
            }
            
            const bounds = map.getBounds();
            
            // 스마트 캐싱: 줌 레벨이 동일하고, 현재 영역이 캐싱된 패딩 영역 내에 완전히 존재하면 재요청 생략
            if (cachedRedevZoom === currentZoom && cachedRedevBounds && cachedRedevBounds.contains(bounds)) {
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
            
            cachedRedevBounds = paddedBounds;
            cachedRedevZoom = currentZoom;
            
            try {
                const res = await fetch(`/api/map/redevelopment_zones?min_lat=${paddedBounds.getSouth()}&max_lat=${paddedBounds.getNorth()}&min_lng=${paddedBounds.getWest()}&max_lng=${paddedBounds.getEast()}`);
                const json = await res.json();
                if (json.status === 'success') {
                    layers.dev3.clearLayers();
                    json.data.forEach(item => {
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
                }
            } catch (err) { console.error(err); } finally { triggerHighlighter(); }
        }"""

content_lf = content_lf.replace(redev_old, redev_new)

zoning_old = """        async function fetchZoningPolygons() {
            if (map.getZoom() < minZoomRequired) return;
            if (!document.getElementById('toggle-zoning').checked) return;
            
            const checkedZonings = Array.from(document.querySelectorAll('.zoning-class-check:checked')).map(cb => cb.value);
            if (checkedZonings.length === 0) {
                layers.zoning.clearLayers();
                triggerHighlighter();
                return;
            }
            
            const bounds = map.getBounds();
            try {
                const res = await fetch(`/api/map/zoning?min_lat=${bounds.getSouth()}&max_lat=${bounds.getNorth()}&min_lng=${bounds.getWest()}&max_lng=${bounds.getEast()}`);
                const json = await res.json();
                if (json.status === 'success') {
                    layers.zoning.clearLayers();
                    json.data.forEach(item => {
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
                }
            } catch (err) { console.error(err); } finally { triggerHighlighter(); }
        }"""

zoning_new = """        let cachedZoningBounds = null;
        let cachedZoningZoom = null;

        async function fetchZoningPolygons() {
            // 용도지역은 지도가 넓을 때 수천개 폴리곤이 로드되어 줌 14 이상일 때만 로드하도록 제한하여 로딩 속도 획기적 개선
            const zoningMinZoom = 14;
            const currentZoom = map.getZoom();
            if (currentZoom < zoningMinZoom) {
                layers.zoning.clearLayers();
                cachedZoningBounds = null;
                cachedZoningZoom = null;
                return;
            }
            if (!document.getElementById('toggle-zoning').checked) return;
            
            const checkedZonings = Array.from(document.querySelectorAll('.zoning-class-check:checked')).map(cb => cb.value);
            if (checkedZonings.length === 0) {
                layers.zoning.clearLayers();
                triggerHighlighter();
                return;
            }
            
            const bounds = map.getBounds();
            
            // 스마트 캐싱: 줌 레벨이 동일하고, 현재 영역이 캐싱된 패딩 영역 내에 완전히 존재하면 재요청 생략
            if (cachedZoningZoom === currentZoom && cachedZoningBounds && cachedZoningBounds.contains(bounds)) {
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
            
            cachedZoningBounds = paddedBounds;
            cachedZoningZoom = currentZoom;
            
            try {
                const res = await fetch(`/api/map/zoning?min_lat=${paddedBounds.getSouth()}&max_lat=${paddedBounds.getNorth()}&min_lng=${paddedBounds.getWest()}&max_lng=${paddedBounds.getEast()}`);
                const json = await res.json();
                if (json.status === 'success') {
                    layers.zoning.clearLayers();
                    json.data.forEach(item => {
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
                }
            } catch (err) { console.error(err); } finally { triggerHighlighter(); }
        }"""

content_lf = content_lf.replace(zoning_old, zoning_new)

roads_old = """        async function fetchPlanningRoads() {
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
            try {
                const res = await fetch(`/api/map/planning_roads?min_lat=${bounds.getSouth()}&max_lat=${bounds.getNorth()}&min_lng=${bounds.getWest()}&max_lng=${bounds.getEast()}`);
                const json = await res.json();
                if (json.status === 'success') {
                    layers.planningRoad.clearLayers();
                    json.data.forEach(item => {
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
                }
            } catch (err) { console.error(err); } finally { triggerHighlighter(); }
        }"""

roads_new = """        let cachedRoadBounds = null;
        let cachedRoadZoom = null;

        async function fetchPlanningRoads() {
            // 도로 레이어는 연산이 무거우므로 줌 레벨 14 이상에서만 가져오고 Turf.js 실시간 연산을 실행하도록 최적화
            const roadMinZoom = 14;
            const currentZoom = map.getZoom();
            if (currentZoom < roadMinZoom) {
                layers.planningRoad.clearLayers();
                cachedRoadBounds = null;
                cachedRoadZoom = null;
                return;
            }
            if (!document.getElementById('toggle-planning-road').checked) return;
            
            const checkedRoads = Array.from(document.querySelectorAll('.planning-road-class-check:checked')).map(cb => cb.value);
            const isBufferEnabled = document.getElementById('toggle-planning-road-buffer').checked;
            
            if (checkedRoads.length === 0) {
                layers.planningRoad.clearLayers();
                triggerHighlighter();
                return;
            }
            
            const bounds = map.getBounds();
            
            // 스마트 캐싱: 줌 레벨이 동일하고, 현재 영역이 캐싱된 패딩 영역 내에 완전히 존재하면 재요청 생략
            if (cachedRoadZoom === currentZoom && cachedRoadBounds && cachedRoadBounds.contains(bounds)) {
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
            
            cachedRoadBounds = paddedBounds;
            cachedRoadZoom = currentZoom;
            
            try {
                const res = await fetch(`/api/map/planning_roads?min_lat=${paddedBounds.getSouth()}&max_lat=${paddedBounds.getNorth()}&min_lng=${paddedBounds.getWest()}&max_lng=${paddedBounds.getEast()}`);
                const json = await res.json();
                if (json.status === 'success') {
                    layers.planningRoad.clearLayers();
                    json.data.forEach(item => {
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
                }
            } catch (err) { console.error(err); } finally { triggerHighlighter(); }
        }"""

content_lf = content_lf.replace(roads_old, roads_new)

# 3. Add cache clearing when toggles are unchecked or window.toggleAllCheckboxes is called
toggle_listeners_old = """            document.getElementById('toggle-dev3').addEventListener('change', (e) => {
                const subContainer = document.getElementById('dev3-sub-container');
                if (e.target.checked) {
                    if (subContainer) subContainer.style.display = 'block';
                    fetchRedevelopmentZones();
                } else {
                    if (subContainer) subContainer.style.display = 'none';
                    layers.dev3.clearLayers();
                }
            });"""

toggle_listeners_new = """            document.getElementById('toggle-dev3').addEventListener('change', (e) => {
                const subContainer = document.getElementById('dev3-sub-container');
                if (e.target.checked) {
                    if (subContainer) subContainer.style.display = 'block';
                    fetchRedevelopmentZones();
                } else {
                    if (subContainer) subContainer.style.display = 'none';
                    layers.dev3.clearLayers();
                    cachedRedevBounds = null;
                    cachedRedevZoom = null;
                }
            });"""

content_lf = content_lf.replace(toggle_listeners_old, toggle_listeners_new)

zoning_listener_old = """            document.getElementById('toggle-zoning').addEventListener('change', (e) => {
                const subContainer = document.getElementById('zoning-sub-container');
                if (e.target.checked) {
                    if (subContainer) subContainer.style.display = 'block';
                    fetchZoningPolygons();
                } else {
                    if (subContainer) subContainer.style.display = 'none';
                    layers.zoning.clearLayers();
                }
            });"""

zoning_listener_new = """            document.getElementById('toggle-zoning').addEventListener('change', (e) => {
                const subContainer = document.getElementById('zoning-sub-container');
                if (e.target.checked) {
                    if (subContainer) subContainer.style.display = 'block';
                    fetchZoningPolygons();
                } else {
                    if (subContainer) subContainer.style.display = 'none';
                    layers.zoning.clearLayers();
                    cachedZoningBounds = null;
                    cachedZoningZoom = null;
                }
            });"""

content_lf = content_lf.replace(zoning_listener_old, zoning_listener_new)

road_listener_old = """            document.getElementById('toggle-planning-road').addEventListener('change', (e) => {
                const subContainer = document.getElementById('planning-road-sub-container');
                if (e.target.checked) {
                    if (subContainer) subContainer.style.display = 'block';
                    fetchPlanningRoads();
                } else {
                    if (subContainer) subContainer.style.display = 'none';
                    layers.planningRoad.clearLayers();
                }
            });"""

road_listener_new = """            document.getElementById('toggle-planning-road').addEventListener('change', (e) => {
                const subContainer = document.getElementById('planning-road-sub-container');
                if (e.target.checked) {
                    if (subContainer) subContainer.style.display = 'block';
                    fetchPlanningRoads();
                } else {
                    if (subContainer) subContainer.style.display = 'none';
                    layers.planningRoad.clearLayers();
                    cachedRoadBounds = null;
                    cachedRoadZoom = null;
                }
            });"""

content_lf = content_lf.replace(road_listener_old, road_listener_new)

# 4. Clear caches when subcheck-boxes or toggleAllCheckboxes is triggered to force immediate redrawing
toggleall_old = """        window.toggleAllCheckboxes = function(className, checked) {
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
        };"""

toggleall_new = """        window.toggleAllCheckboxes = function(className, checked) {
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
                cachedRedevBounds = null;
                cachedRedevZoom = null;
                const dev3Toggle = document.getElementById('toggle-dev3');
                if (dev3Toggle && dev3Toggle.checked) {
                    fetchRedevelopmentZones();
                }
            } else if (className === 'zoning-class-check') {
                cachedZoningBounds = null;
                cachedZoningZoom = null;
                const zoningToggle = document.getElementById('toggle-zoning');
                if (zoningToggle && zoningToggle.checked) {
                    fetchZoningPolygons();
                }
            } else if (className === 'planning-road-class-check') {
                cachedRoadBounds = null;
                cachedRoadZoom = null;
                const roadToggle = document.getElementById('toggle-planning-road');
                if (roadToggle && roadToggle.checked) {
                    fetchPlanningRoads();
                }
            }
        };"""

content_lf = content_lf.replace(toggleall_old, toggleall_new)

# 5. Clear caches when subcheck-boxes themselves change to allow immediate redrawing
subcheck_listener_old = """            document.querySelectorAll('.dev3-stage-check').forEach(cb => {
                cb.addEventListener('change', fetchRedevelopmentZones);
            });"""

subcheck_listener_new = """            document.querySelectorAll('.dev3-stage-check').forEach(cb => {
                cb.addEventListener('change', () => {
                    cachedRedevBounds = null;
                    cachedRedevZoom = null;
                    fetchRedevelopmentZones();
                });
            });"""

content_lf = content_lf.replace(subcheck_listener_old, subcheck_listener_new)

zoning_subcheck_old = """            document.querySelectorAll('.zoning-class-check').forEach(cb => {
                cb.addEventListener('change', fetchZoningPolygons);
            });"""

zoning_subcheck_new = """            document.querySelectorAll('.zoning-class-check').forEach(cb => {
                cb.addEventListener('change', () => {
                    cachedZoningBounds = null;
                    cachedZoningZoom = null;
                    fetchZoningPolygons();
                });
            });"""

content_lf = content_lf.replace(zoning_subcheck_old, zoning_subcheck_new)

road_subcheck_old = """            document.querySelectorAll('.planning-road-class-check').forEach(cb => {
                cb.addEventListener('change', fetchPlanningRoads);
            });"""

road_subcheck_new = """            document.querySelectorAll('.planning-road-class-check').forEach(cb => {
                cb.addEventListener('change', () => {
                    cachedRoadBounds = null;
                    cachedRoadZoom = null;
                    fetchPlanningRoads();
                });
            });"""

content_lf = content_lf.replace(road_subcheck_old, road_subcheck_new)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content_lf)

print("SUCCESS: Performance optimizations applied cleanly!")
