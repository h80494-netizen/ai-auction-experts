import os

html_path = 'public/map.html'
if not os.path.exists(html_path):
    print("Cannot find public/map.html")
    exit(1)

with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update region checkboxes container styles
old_region_div = '<div class="region-toggles" style="display: flex; gap: 15px; align-items: center; padding: 0 15px;">'
new_region_div = '<div class="region-toggles" style="display: flex; gap: 10px; align-items: center; padding: 0 10px; flex-shrink: 0; white-space: nowrap; flex-wrap: nowrap;">'
if old_region_div in content:
    content = content.replace(old_region_div, new_region_div)
    print("Updated region checkboxes container style.")
else:
    print("WARNING: Could not find old_region_div")

# 2. Add road flow legend after zoom-warning
zoom_warning_str = """    <div id="zoom-warning" style="display: none; position: absolute; top: 90px; left: 50%; transform: translateX(-50%); z-index: 2000; background: rgba(225, 29, 72, 0.9); color: white; padding: 10px 20px; border-radius: 20px; font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: opacity 0.3s; pointer-events: none;">
        <i class="fa-solid fa-magnifying-glass-plus"></i> 지도를 동네 수준으로 확대해야 물건이 표시됩니다.
    </div>"""

legend_html = """
    <!-- 유동동선 라인맵 5단계 범례 -->
    <div id="road-flow-legend" style="display: none; position: absolute; top: 90px; right: 20px; z-index: 1000; background: white; padding: 12px 15px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.15); border: 1px solid var(--border-color); font-family: 'Noto Sans KR', sans-serif; min-width: 140px; pointer-events: auto;">
        <div style="font-weight: bold; font-size: 0.9rem; margin-bottom: 10px; color: #1e293b; text-align: center; border-bottom: 1px solid #f1f5f9; padding-bottom: 6px;">유동 강도 범례</div>
        <div style="display: flex; flex-direction: column; gap: 8px;">
            <div style="display: flex; align-items: center; justify-content: space-between; font-size: 0.8rem;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="width: 25px; height: 5px; background: #7f1d1d; border-radius: 2px;"></div>
                    <span style="font-weight: 500; color: #334155;">매우 높음</span>
                </div>
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between; font-size: 0.8rem;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="width: 25px; height: 4px; background: #ef4444; border-radius: 2px;"></div>
                    <span style="font-weight: 500; color: #334155;">높음</span>
                </div>
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between; font-size: 0.8rem;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="width: 25px; height: 3px; background: #f97316; border-radius: 2px;"></div>
                    <span style="font-weight: 500; color: #334155;">중간</span>
                </div>
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between; font-size: 0.8rem;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="width: 25px; height: 2px; background: #22c55e; border-radius: 2px;"></div>
                    <span style="font-weight: 500; color: #334155;">낮음</span>
                </div>
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between; font-size: 0.8rem;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="width: 25px; height: 1.5px; background: #a3e635; border-radius: 2px;"></div>
                    <span style="font-weight: 500; color: #334155;">매우 낮음</span>
                </div>
            </div>
        </div>
    </div>"""

if zoom_warning_str in content:
    content = content.replace(zoom_warning_str, zoom_warning_str + legend_html)
    print("Added road flow legend HTML.")
else:
    # Try with unix line endings
    zoom_warning_unix = zoom_warning_str.replace('\r\n', '\n')
    if zoom_warning_unix in content:
        content = content.replace(zoom_warning_unix, zoom_warning_unix + legend_html)
        print("Added road flow legend HTML (unix).")
    else:
        print("WARNING: Could not find zoom-warning string")

# 3. Delete the toggle-heatmap HTML block
heatmap_toggle_block = """            <div class="toggle-row" style="background: #fff1f2; padding: 10px; border-radius: 8px; margin-top: 5px;">
                <div class="toggle-label">
                    <div>
                        <i class="fa-solid fa-fire" style="color: #e11d48;"></i> 유동인구 히트맵 (250m)
                        <span class="toggle-desc" style="color: #be123c;">서울의 생활인구 변화를 시각화</span>
                    </div>
                </div>
                <label class="switch"><input type="checkbox" id="toggle-heatmap"><span
                        class="slider"></span></label>
            </div>"""

if heatmap_toggle_block in content:
    content = content.replace(heatmap_toggle_block, "")
    print("Removed heatmap toggle from sidebar HTML.")
else:
    heatmap_toggle_unix = heatmap_toggle_block.replace('\r\n', '\n')
    if heatmap_toggle_unix in content:
        content = content.replace(heatmap_toggle_unix, "")
        print("Removed heatmap toggle from sidebar HTML (unix).")
    else:
        # Fallback regex-free line search for toggle-heatmap
        lines = content.split('\n')
        start_idx = -1
        end_idx = -1
        for idx, l in enumerate(lines):
            if 'id="toggle-heatmap"' in l:
                # Find surrounding toggle-row
                for back in range(idx, idx-10, -1):
                    if 'class="toggle-row"' in lines[back]:
                        start_idx = back
                        break
                for fwd in range(idx, idx+10):
                    if '</div>' in lines[fwd] and (fwd+1 < len(lines) and lines[fwd+1].strip() == '' or 'toggle-row' in lines[fwd+1]):
                        end_idx = fwd
                        break
                break
        if start_idx != -1 and end_idx != -1:
            print(f"Deleting lines {start_idx} to {end_idx} programmatically.")
            lines[start_idx:end_idx+2] = [] # delete it
            content = '\n'.join(lines)
            print("Removed heatmap toggle from sidebar HTML via line range.")
        else:
            print("WARNING: Could not find toggle-heatmap in HTML")

# 4. Remove toggle-heatmap from toggleMap mapping
old_toggle_map = "'toggle-heatmap': [layers.popHeatmap],"
if old_toggle_map in content:
    content = content.replace(old_toggle_map, "")
    print("Removed toggle-heatmap from toggleMap mapping.")
else:
    print("WARNING: Could not find old_toggle_map in javascript")

# 5. Remove toggle-heatmap change event listener
listener_str = """            document.getElementById('toggle-heatmap').addEventListener('change', (e) => {
                if (e.target.checked) {
                    fetchPopulationHeatmap();
                }
            });"""

if listener_str in content:
    content = content.replace(listener_str, "")
    print("Removed toggle-heatmap change listener.")
else:
    listener_unix = listener_str.replace('\r\n', '\n')
    if listener_unix in content:
        content = content.replace(listener_unix, "")
        print("Removed toggle-heatmap change listener (unix).")
    else:
        print("WARNING: Could not find toggle-heatmap event listener")

# 6. Make fetchPopulationHeatmap() a no-op function
# Locate fetchPopulationHeatmap definition and replace it
lines = content.split('\n')
start_idx = -1
end_idx = -1
for idx, l in enumerate(lines):
    if 'async function fetchPopulationHeatmap()' in l:
        start_idx = idx
        # Find ending brace of the function
        # Simple counting of braces
        braces = 0
        for fwd in range(idx, len(lines)):
            braces += lines[fwd].count('{')
            braces -= lines[fwd].count('}')
            if braces == 0 and fwd > idx:
                end_idx = fwd
                break
        break

if start_idx != -1 and end_idx != -1:
    print(f"Replacing fetchPopulationHeatmap function from line {start_idx} to {end_idx}")
    lines[start_idx:end_idx+1] = [
        "        async function fetchPopulationHeatmap() {",
        "            // No-op function (deleted population heatmap layer)",
        "            return;",
        "        }"
    ]
    content = '\n'.join(lines)
    print("Successfully replaced fetchPopulationHeatmap with no-op.")
else:
    print("WARNING: Could not find fetchPopulationHeatmap function indices")

# 7. Update style rendering and hover in fetchRoadFlows
# Let's locate the Leaflet geoJSON in fetchRoadFlows
old_style_block = """                    L.geoJSON(json.data, {
                        style: function (feature) {
                            const intensity = feature.properties.flow_intensity || 0.5;
                            let color = '#fca5a5'; // Step 8: 연한 빨간색
                            let strokeWidth = 1.1;

                            if (intensity >= 0.8) {
                                color = '#b91c1c'; // Step 10: 진한 빨간색
                                strokeWidth = 2.2;
                            } else if (intensity >= 0.5) {
                                color = '#ef4444'; // Step 9: 중간 빨간색
                                strokeWidth = 1.6;
                            }

                            return {
                                color: color,
                                weight: strokeWidth,
                                opacity: 0.85
                            };
                        },"""

new_style_block = """                    L.geoJSON(json.data, {
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
                        },"""

if old_style_block in content:
    content = content.replace(old_style_block, new_style_block)
    print("Successfully replaced road flows style mapping.")
else:
    old_style_unix = old_style_block.replace('\r\n', '\n')
    new_style_unix = new_style_block.replace('\r\n', '\n')
    if old_style_unix in content:
        content = content.replace(old_style_unix, new_style_unix)
        print("Successfully replaced road flows style mapping (unix).")
    else:
        print("WARNING: Could not find old_style_block in fetchRoadFlows")

# 7-2. Update mouseout style behavior in fetchRoadFlows
old_mouseout_block = """                            layer.on('mouseout', function (e) {
                                const intensity = feature.properties.flow_intensity || 0.5;
                                const originalWeight = intensity >= 0.8 ? 2.2 :
                                                       intensity >= 0.5 ? 1.6 : 1.1;
                                e.target.setStyle({
                                    weight: originalWeight,
                                    opacity: 0.85
                                });
                            });"""

new_mouseout_block = """                            layer.on('mouseout', function (e) {
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
                            });"""

if old_mouseout_block in content:
    content = content.replace(old_mouseout_block, new_mouseout_block)
    print("Successfully replaced road flows mouseout mapping.")
else:
    old_mouseout_unix = old_mouseout_block.replace('\r\n', '\n')
    new_mouseout_unix = new_mouseout_block.replace('\r\n', '\n')
    if old_mouseout_unix in content:
        content = content.replace(old_mouseout_unix, new_mouseout_unix)
        print("Successfully replaced road flows mouseout mapping (unix).")
    else:
        print("WARNING: Could not find old_mouseout_block in fetchRoadFlows")

# 8. Show/hide legend in toggle-road-flows change event listener
old_toggle_flows = """            document.getElementById('toggle-road-flows').addEventListener('change', (e) => {
                if (e.target.checked) {
                    fetchRoadFlows();
                } else {
                    layers.roadFlows.clearLayers();
                    cachedRoadFlowBounds = null;
                    cachedRoadFlowZoom = null;
                }
            });"""

new_toggle_flows = """            document.getElementById('toggle-road-flows').addEventListener('change', (e) => {
                if (e.target.checked) {
                    fetchRoadFlows();
                    document.getElementById('road-flow-legend').style.display = 'block';
                } else {
                    layers.roadFlows.clearLayers();
                    cachedRoadFlowBounds = null;
                    cachedRoadFlowZoom = null;
                    document.getElementById('road-flow-legend').style.display = 'none';
                }
            });"""

if old_toggle_flows in content:
    content = content.replace(old_toggle_flows, new_toggle_flows)
    print("Successfully replaced toggle-road-flows listener.")
else:
    old_toggle_flows_unix = old_toggle_flows.replace('\r\n', '\n')
    new_toggle_flows_unix = new_toggle_flows.replace('\r\n', '\n')
    if old_toggle_flows_unix in content:
        content = content.replace(old_toggle_flows_unix, new_toggle_flows_unix)
        print("Successfully replaced toggle-road-flows listener (unix).")
    else:
        print("WARNING: Could not find old_toggle_flows in map.html")

# Write modified map.html back
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Successfully finished updating public/map.html!")
