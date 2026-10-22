import json

with open('public/map.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add toggle-dev4
target1 = '''            <!-- 단계별 재개발/재건축구역 -->
            <div class="toggle-row" style="flex-direction: column; align-items: stretch; gap: 8px;">'''
replacement1 = '''            <!-- 규제완화지구 -->
            <div class="toggle-row">
                <div class="toggle-label"><i class="fa-solid fa-map" style="color: #ec4899;"></i> 규제완화지구</div>
                <label class="switch"><input type="checkbox" id="toggle-dev4"><span class="slider"></span></label>
            </div>

            <!-- 단계별 재개발/재건축구역 -->
            <div class="toggle-row" style="flex-direction: column; align-items: stretch; gap: 8px;">'''
content = content.replace(target1, replacement1)

# 2. Add layer dev4
target2 = '''            dev3: L.layerGroup(),
            busStops: L.layerGroup(),'''
replacement2 = '''            dev3: L.layerGroup(),
            dev4: L.layerGroup(),
            busStops: L.layerGroup(),'''
content = content.replace(target2, replacement2)

# 3. Add to overlays
target3 = '''                { id: 'toggle-dev3', layer: layers.dev3, isLine: false },'''
replacement3 = '''                { id: 'toggle-dev3', layer: layers.dev3, isLine: false },
                { id: 'toggle-dev4', layer: layers.dev4, isLine: false },'''
content = content.replace(target3, replacement3)

# 4. Add to highlight list
target4 = '''                { id: 'toggle-dev3', layer: layers.dev3, name: '재개발/재건축구역', isLine: false },'''
replacement4 = '''                { id: 'toggle-dev3', layer: layers.dev3, name: '재개발/재건축구역', isLine: false },
                { id: 'toggle-dev4', layer: layers.dev4, name: '규제완화지구', isLine: false },'''
content = content.replace(target4, replacement4)

# 5. Add fetchDeregulationZones function
target5 = '''        async function fetchDistrictUnits() {'''
replacement5 = '''        async function fetchDeregulationZones() {
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
        }

        async function fetchDistrictUnits() {'''
content = content.replace(target5, replacement5)

# 6. Bind events
target6 = '''            fetchDistrictUnits();'''
replacement6 = '''            fetchDistrictUnits();
            fetchDeregulationZones();'''
content = content.replace(target6, replacement6)

target7 = '''        document.getElementById('toggle-dev2').addEventListener('change', function() {
            if (this.checked) fetchDistrictUnits();
            else layers.dev2.clearLayers();
            updateHighlighterPanel();
        });'''
replacement7 = target7 + '''
        document.getElementById('toggle-dev4').addEventListener('change', function() {
            if (this.checked) fetchDeregulationZones();
            else layers.dev4.clearLayers();
            updateHighlighterPanel();
        });'''
content = content.replace(target7, replacement7)

# 7. Add to search mapping
target8 = '''                'toggle-dev2': [layers.dev2],'''
replacement8 = '''                'toggle-dev2': [layers.dev2],
                'toggle-dev4': [layers.dev4],'''
content = content.replace(target8, replacement8)

# 8. Add to active layers check in map info update
target9 = '''                if (document.getElementById('toggle-dev2') && document.getElementById('toggle-dev2').checked) {
                    activeLayers.push('개발행위허가제한지역');
                }'''
replacement9 = target9 + '''
                if (document.getElementById('toggle-dev4') && document.getElementById('toggle-dev4').checked) {
                    activeLayers.push('규제완화지구');
                }'''
content = content.replace(target9, replacement9)

# 9. Add to triggerHighlighter active checks
target10 = '''                if (document.getElementById('toggle-dev2') && document.getElementById('toggle-dev2').checked) {
                    activeLayers.push({ id: 'toggle-dev2', name: '개발행위허가제한지역' });
                }'''
replacement10 = target10 + '''
                if (document.getElementById('toggle-dev4') && document.getElementById('toggle-dev4').checked) {
                    activeLayers.push({ id: 'toggle-dev4', name: '규제완화지구' });
                }'''
content = content.replace(target10, replacement10)

with open('public/map.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done replacing map.html")
