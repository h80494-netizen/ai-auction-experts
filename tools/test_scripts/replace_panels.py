import re

with open('public/map.html', encoding='utf-8') as f:
    lines = f.readlines()

new_html = """    <!-- Left Panel: Layer List -->
    <div class="floating-panel" id="left-panel">
        <div class="panel-header">
            <span><i class="fa-solid fa-layer-group"></i> 레이어 목록</span>
        </div>
        <div class="panel-content">

            <div class="layer-group-title">기본 인프라</div>
            <div class="toggle-row"
                style="flex-direction: column; align-items: stretch; gap: 5px; padding-bottom: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div class="toggle-label"><i class="fa-solid fa-train-subway" style="color: #10b981;"></i> 지하철역
                    </div>
                    <label class="switch"><input type="checkbox" id="toggle-subways" checked><span
                            class="slider"></span></label>
                </div>
                <div
                    style="font-size: 0.75rem; color: var(--text-muted); display: flex; align-items: center; gap: 5px;">
                    버퍼: <input type="number" id="buffer-subways" value="500"
                        style="width: 50px; padding: 2px; border: 1px solid var(--border-color); border-radius: 4px;"
                        onchange="fetchInfraData()"> m
                </div>
            </div>
            <div class="toggle-row">
                <div class="toggle-label">
                    <div>
                        <i class="fa-solid fa-bus" style="color: #0ea5e9;"></i> 버스정류장
                        <span class="toggle-desc">화면 이동 시 자동 로딩</span>
                    </div>
                </div>
                <label class="switch"><input type="checkbox" id="toggle-bus"><span class="slider"></span></label>
            </div>
            <div class="toggle-row"
                style="flex-direction: column; align-items: stretch; gap: 5px; padding-bottom: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div class="toggle-label"><i class="fa-solid fa-industry" style="color: #f59e0b;"></i> 산업단지</div>
                    <label class="switch"><input type="checkbox" id="toggle-inds"><span
                            class="slider"></span></label>
                </div>
                <div
                    style="font-size: 0.75rem; color: var(--text-muted); display: flex; align-items: center; gap: 5px;">
                    버퍼: <input type="number" id="buffer-inds" value="500"
                        style="width: 50px; padding: 2px; border: 1px solid var(--border-color); border-radius: 4px;"
                        onchange="fetchInfraData()"> m
                </div>
            </div>
            <div class="toggle-row">
                <div class="toggle-label">
                    <div>
                        <i class="fa-solid fa-store" style="color: #8b5cf6;"></i> 서울 상권
                        <span class="toggle-desc">화면 이동 시 자동 로딩</span>
                    </div>
                </div>
                <label class="switch"><input type="checkbox" id="toggle-commercial"><span class="slider"></span></label>
            </div>

            <div class="layer-group-title" style="margin-top: 15px;">교육 및 학군</div>
            <div class="toggle-row"
                style="flex-direction: column; align-items: stretch; gap: 5px; padding-bottom: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div class="toggle-label">
                        <div>
                            <i class="fa-solid fa-school" style="color: #f43f5e;"></i> 중학교
                            <span class="toggle-desc">특목고 10%대 배정구역 표시</span>
                        </div>
                    </div>
                    <label class="switch"><input type="checkbox" id="toggle-middles"><span
                            class="slider"></span></label>
                </div>
                <div
                    style="font-size: 0.75rem; color: var(--text-muted); display: flex; align-items: center; gap: 5px;">
                    버퍼: <input type="number" id="buffer-middles" value="500"
                        style="width: 50px; padding: 2px; border: 1px solid var(--border-color); border-radius: 4px;"
                        onchange="fetchInfraData()"> m
                </div>
            </div>
            <div class="toggle-row"
                style="flex-direction: column; align-items: stretch; gap: 5px; padding-bottom: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div class="toggle-label"><i class="fa-solid fa-graduation-cap" style="color: #3b82f6;"></i> 대학교
                    </div>
                    <label class="switch"><input type="checkbox" id="toggle-univs"><span
                            class="slider"></span></label>
                </div>
                <div
                    style="font-size: 0.75rem; color: var(--text-muted); display: flex; align-items: center; gap: 5px;">
                    버퍼: <input type="number" id="buffer-univs" value="" placeholder="500"
                        style="width: 50px; padding: 2px; border: 1px solid var(--border-color); border-radius: 4px;"
                        onchange="fetchInfraData()"> m
                </div>
            </div>
            <div class="toggle-row" style="background: #f3e8ff; padding: 10px; border-radius: 8px; margin-top: 5px;">
                <div class="toggle-label">
                    <div>
                        <i class="fa-solid fa-building-columns" style="color: var(--color-hagwon);"></i> 학원가 폴리곤
                        <span class="toggle-desc" style="color: #7e22ce;">학원 밀집 구역 시각화 (보라색 히트맵)</span>
                    </div>
                </div>
                <label class="switch"><input type="checkbox" id="toggle-hagwons"><span
                        class="slider"></span></label>
            </div>

            <div class="toggle-row" style="background: #fff1f2; padding: 10px; border-radius: 8px; margin-top: 5px;">
                <div class="toggle-label">
                    <div>
                        <i class="fa-solid fa-fire" style="color: #e11d48;"></i> 유동인구 히트맵 (250m)
                        <span class="toggle-desc" style="color: #be123c;">서울의 생활인구 변화를 시각화</span>
                    </div>
                </div>
                <label class="switch"><input type="checkbox" id="toggle-heatmap"><span
                        class="slider"></span></label>
            </div>

            <div class="toggle-row" style="background: #fff7ed; padding: 10px; border-radius: 8px; margin-top: 5px;">
                <div class="toggle-label">
                    <div>
                        <i class="fa-solid fa-building-circle-exclamation" style="color: #ea580c;"></i> 노후화 집중 구역
                        <span class="toggle-desc" style="color: #c2410c;">500가구 60% 이상 또는 1000가구 이상 밀집 격자</span>
                    </div>
                </div>
                <label class="switch"><input type="checkbox" id="toggle-old-buildings"><span
                        class="slider"></span></label>
            </div>

            <div class="layer-group-title" style="margin-top: 15px;">개발구역 (준비중)</div>
            <div class="toggle-row">
                <div class="toggle-label"><i class="fa-solid fa-map" style="color: #64748b;"></i> 택지지구</div>
                <label class="switch"><input type="checkbox" id="toggle-dev1" disabled><span class="slider"
                        style="background-color: #e2e8f0;"></span></label>
            </div>
            <div class="toggle-row">
                <div class="toggle-label"><i class="fa-solid fa-map" style="color: #64748b;"></i> 지구단위계획구역</div>
                <label class="switch"><input type="checkbox" id="toggle-dev2"><span class="slider"></span></label>
            </div>
            <div class="toggle-row">
                <div class="toggle-label"><i class="fa-solid fa-map" style="color: #64748b;"></i> 재개발/재건축구역</div>
                <label class="switch"><input type="checkbox" id="toggle-dev3" disabled><span class="slider"
                        style="background-color: #e2e8f0;"></span></label>
            </div>

        </div>
    </div>

    <!-- Right Panel: Filters -->
    <div class="floating-panel" id="right-panel">
        <div class="panel-header">
            <span><i class="fa-solid fa-filter"></i> 경공매 표시 설정</span>
            <i class="fa-solid fa-xmark" style="cursor: pointer; color: var(--text-muted);"
                onclick="toggleRightPanel()"></i>
        </div>
        <div class="panel-content">

            <div class="layer-group-title">부동산 종류 다중 선택</div>
            <div class="checkbox-grid">
                <label class="checkbox-item"><input type="checkbox" value="아파트" checked> 아파트</label>
                <label class="checkbox-item"><input type="checkbox" value="다세대,빌라"> 다세대/빌라</label>
                <label class="checkbox-item"><input type="checkbox" value="오피스텔"> 오피스텔</label>
                <label class="checkbox-item"><input type="checkbox" value="상가,근린"> 상가/점포</label>
                <label class="checkbox-item"><input type="checkbox" value="토지,대지,임야"> 토지</label>
                <label class="checkbox-item"><input type="checkbox" value="공장"> 공장</label>
            </div>

            <div class="layer-group-title" style="margin-top: 15px;">최저가율 필터 (감정가 대비)</div>
            <div class="range-container">
                <div class="range-labels">
                    <span>0%</span>
                    <span id="rate-val" style="color: var(--primary-blue); font-weight: 700; font-size: 1rem;">100%
                        이하</span>
                </div>
                <input type="range" id="rate-slider" min="0" max="100" value="100"
                    oninput="document.getElementById('rate-val').innerText = this.value + '% 이하'"
                    onchange="loadAuctions()">
            </div>

            <div class="layer-group-title" style="margin-top: 15px;">전용면적 (평)</div>
            <div style="display: flex; gap: 10px; align-items: center;">
                <input type="number" id="min-area" placeholder="최소"
                    style="width: 100%; padding: 6px; border: 1px solid var(--border-color); border-radius: 6px;">
                <span>~</span>
                <input type="number" id="max-area" placeholder="최대"
                    style="width: 100%; padding: 6px; border: 1px solid var(--border-color); border-radius: 6px;">
            </div>

            <div class="layer-group-title" style="margin-top: 15px;">추가 조건</div>
            <div style="display: flex; flex-direction: column; gap: 8px;">
                <label class="checkbox-item" style="border: none; padding: 0;">
                    <input type="checkbox" id="req-elite-school"> 명문학군 포함 (주택 전체)
                </label>
                <div style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem;">
                    <span>세대수</span>
                    <input type="number" id="min-households" placeholder="ex) 300"
                        style="width: 80px; padding: 4px; border: 1px solid var(--border-color); border-radius: 4px;">
                    <span style="color: var(--text-muted);">(아파트 전용)</span>
                </div>
            </div>

            <div style="margin-top: 20px;">
                <button class="btn-primary" style="width: 100%;" onclick="loadAuctions()">
                    <i class="fa-solid fa-download"></i> 조건에 맞는 데이터 가져오기
                </button>
                <button onclick="exportToExcel()"
                    style="width: 100%; margin-top: 10px; background: #10b981; color: white; border: none; padding: 12px; border-radius: 8px; font-weight: bold; cursor: pointer; display: flex; justify-content: center; align-items: center; gap: 8px;">
                    <i class="fa-solid fa-file-excel"></i> 왼쪽 조건 중첩 물건 추출 (Excel)
                </button>
            </div>

            <div style="font-size: 0.75rem; color: var(--text-muted); text-align: center; margin-top: 10px;">
                현재 화면(BBox) 기준으로 데이터를 불러옵니다.
            </div>

        </div>
    </div>\n"""

start_idx = -1
end_idx = -1

for i, line in enumerate(lines):
    if "<!-- Left Panel: Layer List -->" in line:
        start_idx = i
    if "<!-- Leaflet JS -->" in line:
        end_idx = i
        break

if start_idx != -1 and end_idx != -1:
    lines[start_idx:end_idx] = [new_html]
    with open('public/map.html', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("Replaced panels successfully")
else:
    print(f"Failed to find indices: {start_idx}, {end_idx}")
