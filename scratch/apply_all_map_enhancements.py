file_path = r"c:\Users\llll\Documents\두인경매\바이브코딩\public\map.html"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Normalize line endings to LF to avoid matching issues
content_lf = content.replace("\r\n", "\n")

replacements = []

# 1. Layers object declaration
replacements.append((
    """            dev1: L.layerGroup(),
            dev2: L.layerGroup(),
            popHeatmap: L.layerGroup(),""",
    """            dev1: L.layerGroup(),
            dev2: L.layerGroup(),
            dev3: L.layerGroup(),
            zoning: L.layerGroup(),
            popHeatmap: L.layerGroup(),"""
))

# 2. activeFilterIds list in applyHighlighter
replacements.append((
    """            const activeFilterIds = [
                { id: 'toggle-subways', layer: layers.subway },
                { id: 'toggle-univs', layer: layers.univ },
                { id: 'toggle-inds', layer: layers.ind },
                { id: 'toggle-middles', layer: layers.middle },
                { id: 'toggle-commercial', layer: layers.commercial },
                { id: 'toggle-hagwons', layer: layers.hagwon },
                { id: 'toggle-dev1', layer: layers.dev1 },
                { id: 'toggle-dev2', layer: layers.dev2 },
                { id: 'toggle-old-buildings', layer: layers.oldBuildings }
            ];""",
    """            const activeFilterIds = [
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
                { id: 'toggle-old-buildings', layer: layers.oldBuildings }
            ];"""
))

# 3. HTML layer panel toggles
replacements.append((
    """            <div class="layer-group-title" style="margin-top: 15px;">개발구역 (준비중)</div>
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
            </div>""",
    """            <div class="layer-group-title" style="margin-top: 15px;">개발구역 (진행중)</div>
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
                <label class="switch"><input type="checkbox" id="toggle-dev3"><span class="slider"></span></label>
            </div>
            <div class="toggle-row">
                <div class="toggle-label"><i class="fa-solid fa-map" style="color: #64748b;"></i> 용도지역 (도시지역)</div>
                <label class="switch"><input type="checkbox" id="toggle-zoning"><span class="slider"></span></label>
            </div>"""
))

# 4. toggleMap and change listeners
replacements.append((
    """            const toggleMap = {
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
            });""",
    """            const toggleMap = {
                'toggle-subways': [layers.subway, layers.subwayLine],
                'toggle-univs': [layers.univ],
                'toggle-middles': [layers.middle],
                'toggle-inds': [layers.ind],
                'toggle-commercial': [layers.commercial],
                'toggle-dev2': [layers.dev2],
                'toggle-dev3': [layers.dev3],
                'toggle-zoning': [layers.zoning],
                
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
                        if (id === 'toggle-dev2') fetchDistrictUnits();
                        if (id === 'toggle-dev3') fetchRedevelopmentZones();
                        if (id === 'toggle-zoning') fetchZoningPolygons();
                    } else {
                        layerList.forEach(l => map.removeLayer(l));
                    }
                    triggerHighlighter();
                });
            });"""
))

# 5. moveend event listener fetches
replacements.append((
    """                    updateCenterAddress();
                    fetchInfraData();
                    fetchDistrictUnits();
                    fetchPopulationHeatmap();""",
    """                    updateCenterAddress();
                    fetchInfraData();
                    fetchDistrictUnits();
                    fetchRedevelopmentZones();
                    fetchZoningPolygons();
                    fetchPopulationHeatmap();"""
))

# 6. initial load deferred fetches
replacements.append((
    """                    fetchSubwayLines();
                    fetchHagwonPolygons();
                    fetchDistrictUnits();
                    fetchPopulationHeatmap();""",
    """                    fetchSubwayLines();
                    fetchHagwonPolygons();
                    fetchDistrictUnits();
                    fetchRedevelopmentZones();
                    fetchZoningPolygons();
                    fetchPopulationHeatmap();"""
))

success_count = 0
for idx, (target, replacement) in enumerate(replacements):
    target_lf = target.replace("\r\n", "\n")
    replacement_lf = replacement.replace("\r\n", "\n")
    if target_lf in content_lf:
        content_lf = content_lf.replace(target_lf, replacement_lf)
        print(f"SUCCESS: Replaced enhancement {idx+1}")
        success_count += 1
    else:
        print(f"ERROR: Target block for enhancement {idx+1} not found in map.html!")

if success_count == len(replacements):
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content_lf)
    print("\nALL ENHANCEMENTS APPLIED SUCCESSFULLY!")
else:
    print(f"\nFailed to apply all enhancements. Applied {success_count}/{len(replacements)}.")
