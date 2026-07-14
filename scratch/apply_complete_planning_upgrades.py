import re
import os

file_path = r"c:\Users\llll\Documents\두인경매\바이브코딩\public\map.html"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Normalize line endings to LF
content_lf = content.replace("\r\n", "\n")

replacements = []

# 1. Add new layers to Leaflet layers object
layers_target = """        const layers = {
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
        };"""

layers_replacement = """        const layers = {
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
            auction: L.layerGroup().addTo(map)
        };"""

replacements.append((layers_target, layers_replacement))

# 2. Add layers to Highlighter activeFilterIds so highlight overlap counts them
highlighter_target = """            const activeFilterIds = [
                { id: 'toggle-subways', layer: layers.subway },
                { id: 'toggle-univs', layer: layers.univ },
                { id: 'toggle-inds', layer: layers.ind },
                { id: 'toggle-middles', layer: layers.middle },
                { id: 'toggle-commercial', layer: layers.commercial },
                { id: 'toggle-hagwons', layer: layers.hagwon },
                { id: 'toggle-dev1', layer: layers.dev1 },
                { id: 'toggle-dev2', layer: layers.dev2 },
                { id: 'toggle-old-buildings', layer: layers.oldBuildings }
            ];"""

highlighter_replacement = """            const activeFilterIds = [
                { id: 'toggle-subways', layer: layers.subway },
                { id: 'toggle-univs', layer: layers.univ },
                { id: 'toggle-inds', layer: layers.ind },
                { id: 'toggle-middles', layer: layers.middle },
                { id: 'toggle-commercial', layer: layers.commercial },
                { id: 'toggle-hagwons', layer: layers.hagwon },
                { id: 'toggle-dev1', layer: layers.dev1 },
                { id: 'toggle-dev2', layer: layers.dev2 },
                { id: 'toggle-dev3', layer: layers.dev3 },
                { id: 'toggle-zoning', layer: layers.zoning },
                { id: 'toggle-planning-road', layer: layers.planningRoad },
                { id: 'toggle-old-buildings', layer: layers.oldBuildings }
            ];"""

replacements.append((highlighter_target, highlighter_replacement))

# 3. Replace HTML Layer panel toggles block in Left Panel
html_target = """            <div class="layer-group-title" style="margin-top: 15px;">개발구역 (준비중)</div>
            <div class="toggle-row">
                <div class="toggle-label"><i class="fa-solid fa-map" style="color: #64748b;"></i> 택지지구</div>
                <label class="switch"><input type="checkbox" id="toggle-dev1"><span class="slider"></span></label>
            </div>
            <div class="toggle-row">
                <div class="toggle-label"><i class="fa-solid fa-map" style="color: #64748b;"></i> 지구단위계획구역</div>
                <label class="switch"><input type="checkbox" id="toggle-dev2"><span class="slider"></span></label>
            </div>
            <div class="toggle-row">
                <div class="toggle-label"><i class="fa-solid fa-map" style="color: #64748b;"></i> 재개발/재건축구역</div>
                <label class="switch"><input type="checkbox" id="toggle-dev3" disabled><span class="slider"
                        style="background-color: #e2e8f0;"></span></label>
            </div>"""

html_replacement = """            <div class="layer-group-title" style="margin-top: 15px;">개발구역 및 도시계획</div>
            
            <!-- 단계별 택지지구 -->
            <div class="toggle-row" style="flex-direction: column; align-items: stretch; gap: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
                    <div class="toggle-label"><i class="fa-solid fa-map" style="color: #3b82f6;"></i> 택지지구</div>
                    <label class="switch"><input type="checkbox" id="toggle-dev1"><span class="slider"></span></label>
                </div>
                <div id="dev1-sub-container" style="display: none; padding-left: 20px; margin-top: 4px;">
                    <div style="font-size: 0.75rem; color: #64748b; margin-bottom: 4px; display: flex; justify-content: space-between; align-items: center;">
                        <span>단계 선택 (중복 가능)</span>
                        <span style="font-size: 0.7rem; color: var(--primary-blue); cursor: pointer; font-weight: 500;" onclick="toggleAllCheckboxes('dev1-stage-check', true)">전체선택</span>
                    </div>
                    <div id="dev1-stages-list" style="border: 1px solid var(--border-color); border-radius: 6px; padding: 6px 10px; background: #fff; display: flex; flex-direction: column; gap: 6px; box-shadow: inset 0 1px 2px rgba(0,0,0,0.05);">
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; cursor: pointer; color: var(--text-dark);"><input type="checkbox" class="dev1-stage-check" value="초기" checked> 초기 단계 (지구지정 등)</label>
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; cursor: pointer; color: var(--text-dark);"><input type="checkbox" class="dev1-stage-check" value="중기" checked> 중기 단계 (지구계획승인 등)</label>
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; cursor: pointer; color: var(--text-dark);"><input type="checkbox" class="dev1-stage-check" value="후기" checked> 후기 단계 (착공/분양 등)</label>
                    </div>
                </div>
            </div>

            <!-- 지구단위계획구역 -->
            <div class="toggle-row">
                <div class="toggle-label"><i class="fa-solid fa-map" style="color: #10b981;"></i> 지구단위계획구역</div>
                <label class="switch"><input type="checkbox" id="toggle-dev2"><span class="slider"></span></label>
            </div>

            <!-- 단계별 재개발/재건축구역 -->
            <div class="toggle-row" style="flex-direction: column; align-items: stretch; gap: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
                    <div class="toggle-label"><i class="fa-solid fa-map" style="color: #8b5cf6;"></i> 재개발/재건축구역</div>
                    <label class="switch"><input type="checkbox" id="toggle-dev3"><span class="slider"></span></label>
                </div>
                <div id="dev3-sub-container" style="display: none; padding-left: 20px; margin-top: 4px;">
                    <div style="font-size: 0.75rem; color: #64748b; margin-bottom: 4px; display: flex; justify-content: space-between; align-items: center;">
                        <span>단계 선택 (중복 가능)</span>
                        <span style="font-size: 0.7rem; color: var(--primary-blue); cursor: pointer; font-weight: 500;" onclick="toggleAllCheckboxes('dev3-stage-check', true)">전체선택</span>
                    </div>
                    <div id="dev3-stages-list" style="border: 1px solid var(--border-color); border-radius: 6px; padding: 6px 10px; background: #fff; display: flex; flex-direction: column; gap: 6px; box-shadow: inset 0 1px 2px rgba(0,0,0,0.05);">
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; cursor: pointer; color: var(--text-dark);"><input type="checkbox" class="dev3-stage-check" value="초기" checked> 초기 단계 (조합설립 등)</label>
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; cursor: pointer; color: var(--text-dark);"><input type="checkbox" class="dev3-stage-check" value="중기" checked> 중기 단계 (사업시행 등)</label>
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; cursor: pointer; color: var(--text-dark);"><input type="checkbox" class="dev3-stage-check" value="후기" checked> 후기 단계 (관리처분 등)</label>
                    </div>
                </div>
            </div>

            <!-- 용도지역 (중복 선택) -->
            <div class="toggle-row" style="flex-direction: column; align-items: stretch; gap: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
                    <div class="toggle-label"><i class="fa-solid fa-layer-group" style="color: #f59e0b;"></i> 용도지역 (도시지역)</div>
                    <label class="switch"><input type="checkbox" id="toggle-zoning"><span class="slider"></span></label>
                </div>
                <div id="zoning-sub-container" style="display: none; padding-left: 20px; margin-top: 4px;">
                    <div style="font-size: 0.75rem; color: #64748b; margin-bottom: 4px; display: flex; justify-content: space-between; align-items: center;">
                        <span>용도지역 선택 (중복 가능)</span>
                        <span style="font-size: 0.7rem; color: var(--primary-blue); cursor: pointer; font-weight: 500;" onclick="toggleAllCheckboxes('zoning-class-check', true)">전체선택</span>
                    </div>
                    <div id="zoning-stages-list" style="border: 1px solid var(--border-color); border-radius: 6px; padding: 6px 10px; background: #fff; display: flex; flex-direction: column; gap: 6px; box-shadow: inset 0 1px 2px rgba(0,0,0,0.05); max-height: 180px; overflow-y: auto;">
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; cursor: pointer; color: var(--text-dark);"><input type="checkbox" class="zoning-class-check" value="전용주거지역" checked> 전용주거지역</label>
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; cursor: pointer; color: var(--text-dark);"><input type="checkbox" class="zoning-class-check" value="1종일반주거지역" checked> 1종일반주거지역</label>
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; cursor: pointer; color: var(--text-dark);"><input type="checkbox" class="zoning-class-check" value="2종일반주거지역" checked> 2종일반주거지역</label>
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; cursor: pointer; color: var(--text-dark);"><input type="checkbox" class="zoning-class-check" value="3종일반주거지역" checked> 3종일반주거지역</label>
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; cursor: pointer; color: var(--text-dark);"><input type="checkbox" class="zoning-class-check" value="준주거지역" checked> 준주거지역</label>
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; cursor: pointer; color: var(--text-dark);"><input type="checkbox" class="zoning-class-check" value="상업지역" checked> 상업지역</label>
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; cursor: pointer; color: var(--text-dark);"><input type="checkbox" class="zoning-class-check" value="전용공업지역" checked> 전용공업지역</label>
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; cursor: pointer; color: var(--text-dark);"><input type="checkbox" class="zoning-class-check" value="일반공업지역" checked> 일반공업지역</label>
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; cursor: pointer; color: var(--text-dark);"><input type="checkbox" class="zoning-class-check" value="준공업지역" checked> 준공업지역</label>
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; cursor: pointer; color: var(--text-dark);"><input type="checkbox" class="zoning-class-check" value="녹지지역" checked> 녹지지역</label>
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; cursor: pointer; color: var(--text-dark);"><input type="checkbox" class="zoning-class-check" value="기타" checked> 기타 용도지역</label>
                    </div>
                </div>
            </div>

            <!-- 도시계획도로 (중복 선택 및 10m 버퍼) -->
            <div class="toggle-row" style="flex-direction: column; align-items: stretch; gap: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
                    <div class="toggle-label"><i class="fa-solid fa-road" style="color: #6b7280;"></i> 도시계획도로</div>
                    <label class="switch"><input type="checkbox" id="toggle-planning-road"><span class="slider"></span></label>
                </div>
                <div id="planning-road-sub-container" style="display: none; padding-left: 20px; margin-top: 4px;">
                    <div style="font-size: 0.75rem; color: #64748b; margin-bottom: 4px; display: flex; justify-content: space-between; align-items: center;">
                        <span>도로종류 선택 (중복 가능)</span>
                        <span style="font-size: 0.7rem; color: var(--primary-blue); cursor: pointer; font-weight: 500;" onclick="toggleAllCheckboxes('planning-road-class-check', true)">전체선택</span>
                    </div>
                    <div style="border: 1px solid var(--border-color); border-radius: 6px; padding: 6px 10px; background: #fff; display: flex; flex-direction: column; gap: 6px; box-shadow: inset 0 1px 2px rgba(0,0,0,0.05); max-height: 180px; overflow-y: auto;">
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; cursor: pointer; color: var(--text-dark);"><input type="checkbox" class="planning-road-class-check" value="대로" checked> 대로 (폭 25m 이상)</label>
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; cursor: pointer; color: var(--text-dark);"><input type="checkbox" class="planning-road-class-check" value="중로" checked> 중로 (폭 12m ~ 25m)</label>
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; cursor: pointer; color: var(--text-dark);"><input type="checkbox" class="planning-road-class-check" value="소로1류" checked> 소로 1류 (폭 10m ~ 12m)</label>
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; cursor: pointer; color: var(--text-dark);"><input type="checkbox" class="planning-road-class-check" value="소로2류" checked> 소로 2류 (폭 8m ~ 10m)</label>
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; cursor: pointer; color: var(--text-dark);"><input type="checkbox" class="planning-road-class-check" value="소로3류" checked> 소로 3류 (폭 8m 미만)</label>
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; cursor: pointer; color: var(--text-dark);"><input type="checkbox" class="planning-road-class-check" value="기타" checked> 기타 도로시설</label>
                    </div>
                    <div style="margin-top: 8px; display: flex; align-items: center; gap: 8px;">
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; cursor: pointer; color: var(--text-dark); font-weight: 600;">
                            <input type="checkbox" id="toggle-planning-road-buffer" onchange="fetchPlanningRoads()"> <i class="fa-solid fa-circle-dot" style="color: #ec4899;"></i> 도로에 대한 버퍼 10m 중첩
                        </label>
                    </div>
                </div>
            </div>"""

replacements.append((html_target, html_replacement))

# 4. Add new toggles to toggleMap
togglemap_target = """            const toggleMap = {
                'toggle-subways': [layers.subway, layers.subwayLine],
                'toggle-univs': [layers.univ],
                'toggle-middles': [layers.middle],
                'toggle-inds': [layers.ind],
                'toggle-commercial': [layers.commercial],
                'toggle-dev2': [layers.dev2],
                
                'toggle-residential-heatmap': [layers.resHeatmap],
                'toggle-workplace-heatmap': [layers.workHeatmap],
                'toggle-road-flows': [layers.roadFlows]
            };"""

togglemap_replacement = """            const toggleMap = {
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
            };"""

replacements.append((togglemap_target, togglemap_replacement))

# Apply the clean replacements first
success_count = 0
for idx, (target, replacement) in enumerate(replacements):
    target_lf = target.replace("\r\n", "\n")
    replacement_lf = replacement.replace("\r\n", "\n")
    if target_lf in content_lf:
        content_lf = content_lf.replace(target_lf, replacement_lf)
        print(f"SUCCESS: Replaced segment {idx+1}")
        success_count += 1
    else:
        print(f"ERROR: Target block for segment {idx+1} not found in map.html!")

# 5. Overwrite the old fetchDistrictUnits block and define new functions using Regex
new_fetch_district_units = """        async function fetchDistrictUnits() {
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
                                color: '#4ade80', // 연한 초록색
                                fillColor: '#4ade80',
                                fillOpacity: 0.15,
                                weight: 2,
                                dashArray: '5, 5'
                            }
                        }).bindPopup(`<b>지구단위계획구역</b><br>${item.name}`).addTo(layers.dev2);
                    });
                }
            } catch (err) { console.error(err); } finally { triggerHighlighter(); }
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
                if (['PP2001', 'PP2002', 'PP2003', 'PP2004'].includes(code)) return '초기';
                if (['PP2005'].includes(code)) return '중기';
                if (['PP2006', 'PP2007'].includes(code)) return '후기';
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
                    const stepCode = props.stepCode || props.zoneCode || props.zone_cd || '';
                    let stageName = '초기 단계';
                    if (['PP2001', 'PP2002', 'PP2003', 'PP2004'].includes(stepCode)) stageName = '초기 단계 (지구지정 등)';
                    else if (stepCode === 'PP2005') stageName = '중기 단계 (지구계획승인 등)';
                    else if (['PP2006', 'PP2007'].includes(stepCode)) stageName = '후기 단계 (착공/분양 등)';
                    
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

        // --- 개발구역 및 도시계획 레이어 추가 함수 끝 ---"""

pattern = re.compile(r'async function fetchDistrictUnits\(\)\s*\{.*?\n\s*\}', re.DOTALL)
if pattern.search(content_lf):
    content_lf = pattern.sub(new_fetch_district_units, content_lf)
    print("SUCCESS: Replaced fetchDistrictUnits and injected new drawing functions!")
    success_count += 1
else:
    print("ERROR: Could not find fetchDistrictUnits block using regex!")

# 6. Hook functions to map moveend debouncer
moveend_pattern = re.compile(r'(updateCenterAddress\(\);\s*fetchInfraData\(\);\s*fetchDistrictUnits\(\);)', re.DOTALL)
if moveend_pattern.search(content_lf):
    content_lf = moveend_pattern.sub(r'updateCenterAddress();\n                    fetchInfraData();\n                    fetchDistrictUnits();\n                    updateTaekjiLayer();\n                    fetchRedevelopmentZones();\n                    fetchZoningPolygons();\n                    fetchPlanningRoads();', content_lf)
    print("SUCCESS: Hooked new functions to moveend debouncer!")
    success_count += 1
else:
    print("ERROR: Could not find moveend pattern in map.html!")

# 7. Add specific change handlers for sub-containers and checkboxes using dynamic search
general_listener_pattern = re.compile(
    r'Object\.keys\(toggleMap\)\.forEach\(id => \{\s*document\.getElementById\(id\)\.addEventListener\(\'change\', \((?:e|event)\) => \{.*?\}\);\s*\}\);', 
    re.DOTALL
)

general_listener_replacement = """Object.keys(toggleMap).forEach(id => {
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
            });"""

if general_listener_pattern.search(content_lf):
    content_lf = general_listener_pattern.sub(general_listener_replacement, content_lf)
    print("SUCCESS: Injected event listeners using regex!")
    success_count += 1
else:
    print("ERROR: Could not find general listener target block using regex!")

# Final check
if success_count == 7:
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content_lf)
    print("\nALL UPGRADES APPLIED TO MAP.HTML SUCCESSFULLY!")
else:
    print(f"\nFailed to apply upgrades. Applied {success_count}/7.")
