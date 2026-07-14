import os

file_path = 'public/map.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Normalize to LF
content = content.replace('\r\n', '\n')

# 1. Replace const layers object
old_layers = """        const layers = {
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

new_layers = """        const layers = {
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

content = content.replace(old_layers, new_layers)

# 2. Replace html toggles block
old_html_toggles = """            <div class="layer-group-title" style="margin-top: 15px;">개발구역 (준비중)</div>
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

new_html_toggles = """            <div class="layer-group-title" style="margin-top: 15px;">개발구역 및 도시계획</div>
            
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

content = content.replace(old_html_toggles, new_html_toggles)

# 3. Add analysis button HTML to top navigation bar
old_top_actions = """        <div class="top-actions">
            <span id="highlight-count" style="display: none; font-size: 0.85rem; font-weight: bold; color: #c026d3; margin-right: 10px; background: #fdf4ff; padding: 4px 8px; border-radius: 12px; border: 1px solid #c026d3;">0건 중첩</span>
            <div class="icon-btn" id="btn-highlighter" title="형광펜 켜기/끄기 (필터와 중첩된 물건 강조)" style="color: #94a3b8;"><i class="fa-solid fa-highlighter"></i></div>"""

new_top_actions = """        <div class="top-actions">
            <span id="highlight-count" style="display: none; font-size: 0.85rem; font-weight: bold; color: #c026d3; margin-right: 10px; background: #fdf4ff; padding: 4px 8px; border-radius: 12px; border: 1px solid #c026d3;">0건 중첩</span>
            <button id="btn-show-analysis" style="display: none; font-size: 0.85rem; font-weight: bold; color: #fff; background: #c026d3; border: none; padding: 5px 12px; border-radius: 12px; cursor: pointer; transition: all 0.2s; white-space: nowrap; margin-right: 10px; box-shadow: 0 2px 4px rgba(192, 38, 211, 0.2);" onclick="openAnalysisScreen()">
                <i class="fa-solid fa-chart-line"></i> 분석 결과 & BEST 3
            </button>
            <div class="icon-btn" id="btn-highlighter" title="형광펜 켜기/끄기 (필터와 중첩된 물건 강조)" style="color: #94a3b8;"><i class="fa-solid fa-highlighter"></i></div>"""

content = content.replace(old_top_actions, new_top_actions)

print("Map.html basic replacements done, now writing script parts...")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Saved map.html")
