file_path = r"c:\Users\llll\Documents\두인경매\바이브코딩\public\map.html"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Normalize line endings to LF
content_lf = content.replace("\r\n", "\n")

replacements = []

# 1. HTML Layer panel change
replacements.append((
    """            <div class="toggle-row">
                <div class="toggle-label"><i class="fa-solid fa-map" style="color: #64748b;"></i> 용도지역 (도시지역)</div>
                <label class="switch"><input type="checkbox" id="toggle-zoning"><span class="slider"></span></label>
            </div>""",
    """            <div class="toggle-row" style="flex-direction: column; align-items: stretch; gap: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
                    <div class="toggle-label"><i class="fa-solid fa-map" style="color: #64748b;"></i> 용도지역 (도시지역)</div>
                    <label class="switch"><input type="checkbox" id="toggle-zoning"><span class="slider"></span></label>
                </div>
                <div id="zoning-sub-container" style="display: none; padding-left: 20px; margin-top: -4px;">
                    <select id="select-zoning-sub" style="width: 100%; padding: 6px 10px; border-radius: 6px; border: 1px solid var(--border-color); background-color: #fff; font-size: 0.8rem; font-family: inherit; color: var(--text-dark); cursor: pointer;">
                        <option value="all">전체</option>
                        <option value="전용주거지역">전용주거지역</option>
                        <option value="1종일반주거지역">1종일반주거지역</option>
                        <option value="2종일반주거지역">2종일반주거지역</option>
                        <option value="3종일반주거지역">3종일반주거지역</option>
                        <option value="준주거지역">준주거지역</option>
                        <option value="상업지역">상업지역</option>
                        <option value="전용공업지역">전용공업지역</option>
                        <option value="일반공업지역">일반공업지역</option>
                        <option value="준공업지역">준공업지역</option>
                        <option value="녹지지역">녹지지역</option>
                        <option value="기타">기타</option>
                    </select>
                </div>
            </div>"""
))

# 2. Toggle listener block
replacements.append((
    """            Object.keys(toggleMap).forEach(id => {
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
            });""",
    """            Object.keys(toggleMap).forEach(id => {
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
                        if (id === 'toggle-zoning') {
                            fetchZoningPolygons();
                            document.getElementById('zoning-sub-container').style.display = 'block';
                        }
                    } else {
                        layerList.forEach(l => map.removeLayer(l));
                        if (id === 'toggle-zoning') {
                            document.getElementById('zoning-sub-container').style.display = 'none';
                        }
                    }
                    triggerHighlighter();
                });
            });

            // 용도지역 세부 분류 선택 이벤트 리스너
            document.getElementById('select-zoning-sub').addEventListener('change', () => {
                fetchZoningPolygons();
            });"""
))

# 3. fetchZoningPolygons signature & bounds
replacements.append((
    """        async function fetchZoningPolygons() {
            if (map.getZoom() < minZoomRequired) return;
            if (!document.getElementById('toggle-zoning').checked) return;
            const bounds = map.getBounds();
            try {""",
    """        async function fetchZoningPolygons() {
            if (map.getZoom() < minZoomRequired) return;
            if (!document.getElementById('toggle-zoning').checked) return;
            const bounds = map.getBounds();
            const subType = document.getElementById('select-zoning-sub').value;
            try {"""
))

# 4. fetchZoningPolygons filter condition insertion
replacements.append((
    """                        } else if (name.includes('녹지') || name.includes('개발제한구역')) {
                            color = '#22c55e'; // 녹지지역
                            zoningType = '녹지지역';
                        }

                        L.geoJSON(geojson, {""",
    """                        } else if (name.includes('녹지') || name.includes('개발제한구역')) {
                            color = '#22c55e'; // 녹지지역
                            zoningType = '녹지지역';
                        }

                        // 세부 분류 필터링 조건
                        if (subType !== 'all' && zoningType !== subType) {
                            return;
                        }

                        L.geoJSON(geojson, {"""
))

success_count = 0
for idx, (target, replacement) in enumerate(replacements):
    target_lf = target.replace("\r\n", "\n")
    replacement_lf = replacement.replace("\r\n", "\n")
    if target_lf in content_lf:
        content_lf = content_lf.replace(target_lf, replacement_lf)
        print(f"SUCCESS: Replaced subselection segment {idx+1}")
        success_count += 1
    else:
        print(f"ERROR: Target block for subselection segment {idx+1} not found in map.html!")

if success_count == len(replacements):
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content_lf)
    print("\nALL ZONING SUBSELECTION UPGRADES APPLIED SUCCESSFULLY!")
else:
    print(f"\nFailed to apply upgrades. Applied {success_count}/{len(replacements)}.")
