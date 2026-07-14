import os

html_path = 'public/map.html'
analysis_path = 'public/analysis.html'

if not os.path.exists(html_path) or not os.path.exists(analysis_path):
    print("Error: Files not found.")
    exit(1)

# =========================================================================
# 1. Update public/map.html
# =========================================================================
with open(html_path, 'r', encoding='utf-8') as f:
    code = f.read()

# A. Insert fetchRedevelopmentZones() into map.on('moveend')
old_moveend = """                fetchRoadFlows();
                fetchCrosswalks();
                loadAuctions();"""

new_moveend = """                fetchRoadFlows();
                fetchCrosswalks();
                fetchRedevelopmentZones();
                loadAuctions();"""

if old_moveend in code:
    code = code.replace(old_moveend, new_moveend)
    print("Injected fetchRedevelopmentZones into moveend.")
else:
    old_moveend_lf = old_moveend.replace('\r\n', '\n')
    new_moveend_lf = new_moveend.replace('\r\n', '\n')
    if old_moveend_lf in code:
        code = code.replace(old_moveend_lf, new_moveend_lf)
        print("Injected fetchRedevelopmentZones into moveend (LF).")

# B. Add zoom correction to toggle-road-flows event listener
old_road_flow_toggle = """        document.getElementById('toggle-road-flows').addEventListener('change', (e) => {
            const headerBtn = document.getElementById('btn-road-flows-toggle');
            if (e.target.checked) {
                fetchRoadFlows();"""

new_road_flow_toggle = """        document.getElementById('toggle-road-flows').addEventListener('change', (e) => {
            const headerBtn = document.getElementById('btn-road-flows-toggle');
            if (e.target.checked) {
                if (map.getZoom() < 14) {
                    map.setZoom(14);
                }
                fetchRoadFlows();"""

if old_road_flow_toggle in code:
    code = code.replace(old_road_flow_toggle, new_road_flow_toggle)
    print("Injected zoom correction to toggle-road-flows.")
else:
    old_road_flow_toggle_lf = old_road_flow_toggle.replace('\r\n', '\n')
    new_road_flow_toggle_lf = new_road_flow_toggle.replace('\r\n', '\n')
    if old_road_flow_toggle_lf in code:
        code = code.replace(old_road_flow_toggle_lf, new_road_flow_toggle_lf)
        print("Injected zoom correction to toggle-road-flows (LF).")

# C. Shrink and compact road-flow-legend HTML
old_legend = """    <div id="road-flow-legend"
        style="display: none; position: absolute; bottom: 30px; left: 50%; transform: translateX(-50%); z-index: 1000; background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); padding: 12px 24px; border-radius: 20px; box-shadow: 0 10px 35px rgba(0,0,0,0.18); border: 1px solid rgba(226, 232, 240, 0.85); font-family: 'Noto Sans KR', sans-serif; display: flex; align-items: center; gap: 24px; pointer-events: auto; white-space: nowrap; flex-wrap: nowrap;">
        <!-- Left: Title -->
        <div style="display: flex; align-items: center; gap: 8px;">
            <div
                style="font-weight: 800; font-size: 0.9rem; color: #1e293b; display: flex; align-items: center; gap: 6px;">
                <i class="fa-solid fa-route" style="color: #059669; font-size: 1.05rem;"></i>
                <span>소도로 유동동선</span>
            </div>
            <span
                style="font-size: 0.68rem; color: #059669; background: #e6f7ed; padding: 2px 8px; border-radius: 12px; font-weight: 800; border: 1px solid rgba(16, 185, 129, 0.2);">반경
                500m</span>
        </div>

        <!-- Divider -->
        <div style="width: 1px; height: 24px; background: rgba(226, 232, 240, 0.8);"></div>

        <!-- Center: 4 Tabs -->
        <div style="display: flex; gap: 6px;">
            <button class="flow-tab-btn active" id="btn-flow-wd-day" onclick="setRoadFlowSlot('1', '02')"
                style="padding: 6px 12px;">평일 낮 (오후)</button>
            <button class="flow-tab-btn" id="btn-flow-wd-night" onclick="setRoadFlowSlot('1', '04')"
                style="padding: 6px 12px;">평일 밤 (저녁)</button>
            <button class="flow-tab-btn" id="btn-flow-we-day" onclick="setRoadFlowSlot('2', '02')"
                style="padding: 6px 12px;">주말 낮 (오후)</button>
            <button class="flow-tab-btn" id="btn-flow-we-night" onclick="setRoadFlowSlot('2', '04')"
                style="padding: 6px 12px;">주말 밤 (저녁)</button>
        </div>

        <!-- Divider -->
        <div style="width: 1px; height: 24px; background: rgba(226, 232, 240, 0.8);"></div>

        <!-- Right: 5 Levels horizontally -->
        <div style="display: flex; align-items: center; gap: 14px; font-size: 0.78rem;">
            <div style="display: flex; align-items: center; gap: 6px;">
                <div
                    style="width: 16px; height: 5px; background: #ef4444; border-radius: 2px; box-shadow: 0 0 4px rgba(239, 68, 68, 0.4);">
                </div>
                <span style="font-weight: 800; color: #ef4444;">Level 5 (5,000명+)</span>
            </div>
            <div style="display: flex; align-items: center; gap: 6px;">
                <div style="width: 16px; height: 4px; background: #f97316; border-radius: 2px;"></div>
                <span style="font-weight: 700; color: #f97316;">Level 4 (3,000명+)</span>
            </div>
            <div style="display: flex; align-items: center; gap: 6px;">
                <div style="width: 16px; height: 3px; background: #f59e0b; border-radius: 2.0px;"></div>
                <span style="font-weight: 700; color: #d97706;">Level 3 (2,000명+)</span>
            </div>
            <div style="display: flex; align-items: center; gap: 6px;">
                <div style="width: 16px; height: 2px; background: #10b981; border-radius: 1px;"></div>
                <span style="font-weight: 600; color: #059669;">Level 2 (1,500명+)</span>
            </div>
            <div style="display: flex; align-items: center; gap: 6px;">
                <div style="width: 16px; height: 1.5px; background: #06b6d4; border-radius: 1px;"></div>
                <span style="font-weight: 600; color: #0891b2;">Level 1 (1,000명+)</span>
            </div>
        </div>
    </div>"""

new_legend = """    <div id="road-flow-legend"
        style="display: none; position: absolute; bottom: 30px; left: calc(50% - 220px); z-index: 1000; background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); padding: 5px 12px; border-radius: 12px; box-shadow: 0 5px 20px rgba(0,0,0,0.15); border: 1px solid rgba(226, 232, 240, 0.85); font-family: 'Noto Sans KR', sans-serif; display: flex; align-items: center; gap: 12px; pointer-events: auto; white-space: nowrap; flex-wrap: nowrap; resize: both; overflow: hidden; min-width: 320px; min-height: 38px;">
        <!-- Left: Title -->
        <div style="display: flex; align-items: center; gap: 4px;">
            <div style="font-weight: 800; font-size: 0.78rem; color: #1e293b; display: flex; align-items: center; gap: 4px;">
                <i class="fa-solid fa-route" style="color: #059669; font-size: 0.9rem;"></i>
                <span>소도로 유동</span>
            </div>
            <span style="font-size: 0.6rem; color: #059669; background: #e6f7ed; padding: 1px 4px; border-radius: 8px; font-weight: 800; border: 1px solid rgba(16, 185, 129, 0.2);">500m</span>
        </div>

        <!-- Divider -->
        <div style="width: 1px; height: 16px; background: rgba(226, 232, 240, 0.8);"></div>

        <!-- Center: 4 Tabs -->
        <div style="display: flex; gap: 4px;">
            <button class="flow-tab-btn active" id="btn-flow-wd-day" onclick="setRoadFlowSlot('1', '02')" style="padding: 3px 6px; font-size: 0.7rem; border-radius: 4px;">평일 낮</button>
            <button class="flow-tab-btn" id="btn-flow-wd-night" onclick="setRoadFlowSlot('1', '04')" style="padding: 3px 6px; font-size: 0.7rem; border-radius: 4px;">평일 밤</button>
            <button class="flow-tab-btn" id="btn-flow-we-day" onclick="setRoadFlowSlot('2', '02')" style="padding: 3px 6px; font-size: 0.7rem; border-radius: 4px;">주말 낮</button>
            <button class="flow-tab-btn" id="btn-flow-we-night" onclick="setRoadFlowSlot('2', '04')" style="padding: 3px 6px; font-size: 0.7rem; border-radius: 4px;">주말 밤</button>
        </div>

        <!-- Divider -->
        <div style="width: 1px; height: 16px; background: rgba(226, 232, 240, 0.8);"></div>

        <!-- Right: 5 Levels horizontally -->
        <div style="display: flex; align-items: center; gap: 8px; font-size: 0.7rem;">
            <div style="display: flex; align-items: center; gap: 3px;">
                <div style="width: 10px; height: 3px; background: #ef4444; border-radius: 1px;"></div>
                <span style="font-weight: 800; color: #ef4444;">L5</span>
            </div>
            <div style="display: flex; align-items: center; gap: 3px;">
                <div style="width: 10px; height: 3px; background: #f97316; border-radius: 1px;"></div>
                <span style="font-weight: 700; color: #f97316;">L4</span>
            </div>
            <div style="display: flex; align-items: center; gap: 3px;">
                <div style="width: 10px; height: 3px; background: #f59e0b; border-radius: 1px;"></div>
                <span style="font-weight: 700; color: #d97706;">L3</span>
            </div>
            <div style="display: flex; align-items: center; gap: 3px;">
                <div style="width: 10px; height: 3px; background: #10b981; border-radius: 1px;"></div>
                <span style="font-weight: 600; color: #059669;">L2</span>
            </div>
            <div style="display: flex; align-items: center; gap: 3px;">
                <div style="width: 10px; height: 3px; background: #06b6d4; border-radius: 1px;"></div>
                <span style="font-weight: 600; color: #0891b2;">L1</span>
            </div>
        </div>
    </div>"""

if old_legend in code:
    code = code.replace(old_legend, new_legend)
    print("Replaced road-flow-legend markup.")
else:
    old_legend_lf = old_legend.replace('\r\n', '\n')
    new_legend_lf = new_legend.replace('\r\n', '\n')
    if old_legend_lf in code:
        code = code.replace(old_legend_lf, new_legend_lf)
        print("Replaced road-flow-legend markup (LF).")

# D. Upgrade checkPointInLayerGroup to support 50m buffer for both lines and polygons
old_buffer_logic = """        function checkPointInLayerGroup(pt, layerGroup, latlng) {
            let isInside = false;
            layerGroup.eachLayer(layer => {
                if (isInside) return;

                if (layer.eachLayer) {
                    isInside = checkPointInLayerGroup(pt, layer, latlng);
                } else if (layer.feature) {
                    const geomType = layer.feature.geometry.type;
                    if (layerGroup === layers.planningRoads) {
                        if (window.turf) {
                            let lineFeature = layer.feature;
                            if (geomType === 'Polygon' || geomType === 'MultiPolygon') {
                                try {
                                    lineFeature = turf.polygonToLine(layer.feature);
                                } catch (e) { }
                            }
                            try {
                                const dist = turf.pointToLineDistance(pt, lineFeature, { units: 'meters' });
                                if (dist <= 10) { // 10m buffer for planning roads!
                                    isInside = true;
                                }
                            } catch (e) {
                                if (geomType.includes('Polygon') && turf.booleanPointInPolygon(pt, layer.feature)) {
                                    isInside = true;
                                }
                            }
                        }
                    } else if (geomType === 'Polygon' || geomType === 'MultiPolygon') {
                        if (layer.getBounds && layer.getBounds().contains(latlng)) {
                            if (window.turf && turf.booleanPointInPolygon(pt, layer.feature)) {
                                isInside = true;
                            }
                        }
                    } else if (geomType === 'LineString' || geomType === 'MultiLineString') {
                        if (window.turf) {
                            try {
                                const dist = turf.pointToLineDistance(pt, layer.feature, { units: 'meters' });
                                if (dist <= 10) {
                                    isInside = true;
                                }
                            } catch (e) { }
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
        }"""

new_buffer_logic = """        function checkPointInLayerGroup(pt, layerGroup, latlng) {
            let isInside = false;
            layerGroup.eachLayer(layer => {
                if (isInside) return;

                if (layer.eachLayer) {
                    isInside = checkPointInLayerGroup(pt, layer, latlng);
                } else if (layer.feature) {
                    const geomType = layer.feature.geometry.type;
                    
                    if (geomType === 'Polygon' || geomType === 'MultiPolygon') {
                        // 1. First check if strictly inside the polygon
                        if (layer.getBounds && layer.getBounds().contains(latlng)) {
                            if (window.turf && turf.booleanPointInPolygon(pt, layer.feature)) {
                                isInside = true;
                            }
                        }
                        // 2. If not strictly inside, check if within a 50m buffer of the polygon boundary line
                        if (!isInside && window.turf) {
                            try {
                                let polyLine = turf.polygonToLine(layer.feature);
                                if (polyLine.type === 'FeatureCollection') {
                                    polyLine.features.forEach(f => {
                                        const dist = turf.pointToLineDistance(pt, f, { units: 'meters' });
                                        if (dist <= 50) isInside = true;
                                    });
                                } else {
                                    const dist = turf.pointToLineDistance(pt, polyLine, { units: 'meters' });
                                    if (dist <= 50) {
                                        isInside = true;
                                    }
                                }
                            } catch (e) { }
                        }
                    } else if (geomType === 'LineString' || geomType === 'MultiLineString') {
                        if (window.turf) {
                            try {
                                const dist = turf.pointToLineDistance(pt, layer.feature, { units: 'meters' });
                                if (dist <= 50) { // 50m buffer for all line layers
                                    isInside = true;
                                }
                            } catch (e) { }
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
        }"""

if old_buffer_logic in code:
    code = code.replace(old_buffer_logic, new_buffer_logic)
    print("Replaced checkPointInLayerGroup buffer logic.")
else:
    old_buffer_logic_lf = old_buffer_logic.replace('\r\n', '\n')
    new_buffer_logic_lf = new_buffer_logic.replace('\r\n', '\n')
    if old_buffer_logic_lf in code:
        code = code.replace(old_buffer_logic_lf, new_buffer_logic_lf)
        print("Replaced checkPointInLayerGroup buffer logic (LF).")

# E. Add makeDraggable helper and bind left-panel, right-panel, and road-flow-legend
draggable_script = """
        // Drag-and-drop & Resizing Helper
        function makeDraggable(el, handleClass) {
            let pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
            const handle = el.querySelector(handleClass) || el;
            handle.style.cursor = 'move';
            
            handle.onmousedown = dragMouseDown;

            function dragMouseDown(e) {
                e = e || window.event;
                // Avoid dragging when clicking form controls
                if (['INPUT', 'BUTTON', 'SELECT', 'SPAN', 'LABEL', 'I'].includes(e.target.tagName) || e.target.closest('.switch') || e.target.closest('.flow-tab-btn')) {
                    return;
                }
                
                // Avoid dragging when clicking near the resize handle (bottom-right edge)
                const rect = el.getBoundingClientRect();
                const borderWidth = 15;
                if (e.clientX > rect.right - borderWidth && e.clientY > rect.bottom - borderWidth) {
                    return; // Allow browser resizing
                }
                
                e.preventDefault();
                
                // Clear transform translation if active to avoid jumping
                if (el.style.transform && el.style.transform !== 'none') {
                    el.style.transform = 'none';
                    el.style.left = rect.left + 'px';
                    el.style.top = rect.top + 'px';
                    el.style.bottom = 'auto';
                    el.style.right = 'auto';
                }
                
                pos3 = e.clientX;
                pos4 = e.clientY;
                document.onmouseup = closeDragElement;
                document.onmousemove = elementDrag;
            }

            function elementDrag(e) {
                e = e || window.event;
                e.preventDefault();
                pos1 = pos3 - e.clientX;
                pos2 = pos4 - e.clientY;
                pos3 = e.clientX;
                pos4 = e.clientY;
                
                el.style.top = (el.offsetTop - pos2) + "px";
                el.style.left = (el.offsetLeft - pos1) + "px";
                el.style.bottom = 'auto';
                el.style.right = 'auto';
            }

            function closeDragElement() {
                document.onmouseup = null;
                document.onmousemove = null;
            }
        }

        // Initialize drag-and-drop
        document.addEventListener('DOMContentLoaded', () => {
            const leftPanel = document.getElementById('left-panel');
            const rightPanel = document.getElementById('right-panel');
            const legendPanel = document.getElementById('road-flow-legend');
            
            if (leftPanel) makeDraggable(leftPanel, '.panel-header');
            if (rightPanel) makeDraggable(rightPanel, '.panel-header');
            if (legendPanel) makeDraggable(legendPanel);
        });
"""

# Insert makeDraggable right before </body> tag
code = code.replace("</body>", draggable_script + "\n</body>")
print("Injected draggable script helper.")

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Map.html fixes completed successfully.")

# =========================================================================
# 2. Update public/analysis.html (Compact descriptions to exactly 2 lines)
# =========================================================================
with open(analysis_path, 'r', encoding='utf-8') as f:
    acode = f.read()

old_desc_style = """        .analysis-desc {
            font-size: 0.72rem;
            color: var(--text-muted);
            line-height: 1.4;
            text-align: justify;
        }"""

new_desc_style = """        .analysis-desc {
            font-size: 0.65rem; /* 2/3 size */
            color: var(--text-muted);
            line-height: 1.35;
            text-align: justify;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            text-overflow: ellipsis;
            height: 2.7em; /* precisely 2 lines */
        }"""

if old_desc_style in acode:
    acode = acode.replace(old_desc_style, new_desc_style)
    print("Compacted analysis descriptions in analysis.html styling.")
else:
    old_desc_style_lf = old_desc_style.replace('\r\n', '\n')
    new_desc_style_lf = new_desc_style.replace('\r\n', '\n')
    if old_desc_style_lf in acode:
        acode = acode.replace(old_desc_style_lf, new_desc_style_lf)
        print("Compacted analysis descriptions in analysis.html styling (LF).")

with open(analysis_path, 'w', encoding='utf-8') as f:
    f.write(acode)

print("Analysis.html fixes completed successfully.")
