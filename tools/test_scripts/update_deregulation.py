import re

with open('public/map.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update the toggle-dev4 HTML structure
target_html = '''            <!-- 규제완화지구 -->
            <div class="toggle-row">
                <div class="toggle-label"><i class="fa-solid fa-map" style="color: #ec4899;"></i> 규제완화지구</div>
                <label class="switch"><input type="checkbox" id="toggle-dev4"><span class="slider"></span></label>
            </div>'''
            
replacement_html = '''            <!-- 규제완화지구 -->
            <div class="toggle-row" style="flex-direction: column; align-items: stretch; gap: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
                    <div class="toggle-label"><i class="fa-solid fa-map" style="color: #ec4899;"></i> 규제완화지구</div>
                    <label class="switch"><input type="checkbox" id="toggle-dev4"><span class="slider"></span></label>
                </div>
                <div id="dev4-sub-container" style="display: none; padding-left: 20px; margin-top: 4px;">
                    <div style="font-size: 0.75rem; color: #64748b; margin-bottom: 4px; display: flex; justify-content: space-between; align-items: center;">
                        <span>세부 지구 선택 (중복 가능)</span>
                        <span style="font-size: 0.7rem; color: var(--primary-blue); cursor: pointer; font-weight: 500;" onclick="toggleAllCheckboxes('dev4-type-check', true)">전체선택</span>
                    </div>
                    <div id="dev4-types-list" style="border: 1px solid var(--border-color); border-radius: 6px; padding: 6px 10px; background: #fff; display: flex; flex-direction: column; gap: 6px; box-shadow: inset 0 1px 2px rgba(0,0,0,0.05);">
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; cursor: pointer; color: var(--text-dark);"><input type="checkbox" class="dev4-type-check" value="개발행위허가제한지역" checked> 개발행위허가제한지역</label>
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; cursor: pointer; color: var(--text-dark);"><input type="checkbox" class="dev4-type-check" value="개발진흥지구" checked> 개발진흥지구</label>
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; cursor: pointer; color: var(--text-dark);"><input type="checkbox" class="dev4-type-check" value="복합용도지구" checked> 복합용도지구</label>
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; cursor: pointer; color: var(--text-dark);"><input type="checkbox" class="dev4-type-check" value="입지규제최소구역" checked> 입지규제최소구역</label>
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; cursor: pointer; color: var(--text-dark);"><input type="checkbox" class="dev4-type-check" value="방재지구" checked> 방재지구</label>
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; cursor: pointer; color: var(--text-dark);"><input type="checkbox" class="dev4-type-check" value="자연취락지구" checked> 자연취락지구</label>
                    </div>
                </div>
            </div>'''
content = content.replace(target_html, replacement_html)

# 2. Add event listener logic to toggle the sub-container display
target_event = '''        document.getElementById('toggle-dev4').addEventListener('change', function() {
            if (this.checked) fetchDeregulationZones();
            else layers.dev4.clearLayers();
            updateHighlighterPanel();
        });'''
replacement_event = '''        document.getElementById('toggle-dev4').addEventListener('change', function() {
            const subContainer = document.getElementById('dev4-sub-container');
            if (subContainer) subContainer.style.display = this.checked ? 'block' : 'none';
            if (this.checked) fetchDeregulationZones();
            else layers.dev4.clearLayers();
            updateHighlighterPanel();
        });
        
        document.querySelectorAll('.dev4-type-check').forEach(cb => {
            cb.addEventListener('change', function() {
                if (document.getElementById('toggle-dev4').checked) fetchDeregulationZones();
            });
        });'''
content = content.replace(target_event, replacement_event)

# 3. Update active layers push in map info
target_active = '''                if (document.getElementById('toggle-dev4') && document.getElementById('toggle-dev4').checked) {
                    activeLayers.push('규제완화지구');
                }'''
replacement_active = '''                if (document.getElementById('toggle-dev4') && document.getElementById('toggle-dev4').checked) {
                    const checkedTypes = Array.from(document.querySelectorAll('.dev4-type-check:checked')).map(cb => cb.value);
                    if (checkedTypes.length > 0) activeLayers.push('규제완화지구 (' + checkedTypes.join(', ') + ')');
                    else activeLayers.push('규제완화지구');
                }'''
content = content.replace(target_active, replacement_active)

# 4. Update triggerHighlighter mapping so it counts sub-types
target_trigger = '''                if (document.getElementById('toggle-dev4') && document.getElementById('toggle-dev4').checked) {
                    activeLayers.push({ id: 'toggle-dev4', name: '규제완화지구' });
                }'''
replacement_trigger = '''                if (document.getElementById('toggle-dev4') && document.getElementById('toggle-dev4').checked) {
                    const checkedTypes = Array.from(document.querySelectorAll('.dev4-type-check:checked')).map(cb => cb.value);
                    checkedTypes.forEach(type => {
                        activeLayers.push({ id: 'toggle-dev4', name: type });
                    });
                }'''
content = content.replace(target_trigger, replacement_trigger)

# 5. Add VWorld Proxy fetching to fetchDeregulationZones
target_fetch = '''        async function fetchDeregulationZones() {
            if (map.getZoom() < minZoomRequired) return;
            if (!document.getElementById('toggle-dev4').checked) return;
            
            const bounds = map.getBounds();
            const southWest = bounds.getSouthWest();
            const northEast = bounds.getNorthEast();
            
            try {
                const res = await fetch(`/api/map/deregulation_zones?min_lat=${southWest.lat}&max_lat=${northEast.lat}&min_lng=${southWest.lng}&max_lng=${northEast.lng}`);
                const json = await res.json();
                if (json.status === 'success') {
                    layers.dev4.clearLayers();
                    json.data.forEach(item => {
                        let geojson = JSON.parse(item.geojson);
                        L.geoJSON(geojson, {
                            style: {
                                color: '#ec4899', // 핑크색
                                fillColor: '#ec4899',
                                fillOpacity: 0.15,
                                weight: 2,
                                dashArray: '5, 5'
                            }
                        }).bindPopup(`<b>규제완화지구</b><br>${item.name}`).addTo(layers.dev4);
                    });
                    triggerHighlighter();
                }
            } catch (err) {
                console.error("Failed to fetch deregulation zones:", err);
            }
        }'''
replacement_fetch = '''        async function fetchDeregulationZones() {
            if (map.getZoom() < minZoomRequired) return;
            if (!document.getElementById('toggle-dev4').checked) return;
            
            layers.dev4.clearLayers();
            const bounds = map.getBounds();
            const southWest = bounds.getSouthWest();
            const northEast = bounds.getNorthEast();
            const geomFilter = `BOX(${southWest.lng},${southWest.lat},${northEast.lng},${northEast.lat})`;
            
            const checkedTypes = Array.from(document.querySelectorAll('.dev4-type-check:checked')).map(cb => cb.value);
            if (checkedTypes.length === 0) return;

            const typeMap = {
                '개발행위허가제한지역': 'LT_C_UD801',
                '개발진흥지구': 'LT_C_UD080',
                '복합용도지구': 'LT_C_UD110',
                '입지규제최소구역': 'LT_C_UD061',
                '방재지구': 'LT_C_UD090',
                '자연취락지구': 'LT_C_UQ111'
            };

            for (const typeName of checkedTypes) {
                const layerCode = typeMap[typeName];
                if (!layerCode) continue;
                
                try {
                    const res = await fetch(`/api/proxy/vworld?data=${layerCode}&geomFilter=${geomFilter}`);
                    const json = await res.json();
                    if (json && json.response && json.response.result && json.response.result.featureCollection) {
                        L.geoJSON(json.response.result.featureCollection, {
                            style: {
                                color: '#ec4899',
                                fillColor: '#ec4899',
                                fillOpacity: 0.2,
                                weight: 2,
                                dashArray: '5, 5'
                            },
                            onEachFeature: function(feature, layer) {
                                layer.bindPopup(`<b>${typeName}</b>`);
                                // Custom layer name tag for highlighter intersection logic
                                layer.layerName = typeName;
                            }
                        }).addTo(layers.dev4);
                    }
                } catch (err) {
                    console.error(`Failed to fetch ${typeName} from VWorld:`, err);
                }
            }
            triggerHighlighter();
        }'''
content = content.replace(target_fetch, replacement_fetch)

with open('public/map.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done updating map.html with detailed deregulation checkboxes and VWorld API.")
