import os

html_path = 'public/map.html'
if not os.path.exists(html_path):
    print("Error: public/map.html not found")
    exit(1)

with open(html_path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update sub-checkboxes default state (Only "초기" should have checked)
# Housing District (dev1) stage checks
old_dev1_checkboxes = """                    <div id="dev1-stages-list" style="border: 1px solid var(--border-color); border-radius: 6px; padding: 6px 10px; background: #fff; display: flex; flex-direction: column; gap: 6px; box-shadow: inset 0 1px 2px rgba(0,0,0,0.05);">
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; cursor: pointer; color: var(--text-dark);"><input type="checkbox" class="dev1-stage-check" value="초기" checked> 초기 단계 (지구지정 등)</label>
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; cursor: pointer; color: var(--text-dark);"><input type="checkbox" class="dev1-stage-check" value="중기" checked> 중기 단계 (지구계획승인 등)</label>
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; cursor: pointer; color: var(--text-dark);"><input type="checkbox" class="dev1-stage-check" value="후기" checked> 후기 단계 (착공/분양 등)</label>
                    </div>"""

new_dev1_checkboxes = """                    <div id="dev1-stages-list" style="border: 1px solid var(--border-color); border-radius: 6px; padding: 6px 10px; background: #fff; display: flex; flex-direction: column; gap: 6px; box-shadow: inset 0 1px 2px rgba(0,0,0,0.05);">
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; cursor: pointer; color: var(--text-dark);"><input type="checkbox" class="dev1-stage-check" value="초기" checked> 초기 단계 (지구지정 등)</label>
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; cursor: pointer; color: var(--text-dark);"><input type="checkbox" class="dev1-stage-check" value="중기"> 중기 단계 (지구계획승인 등)</label>
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; cursor: pointer; color: var(--text-dark);"><input type="checkbox" class="dev1-stage-check" value="후기"> 후기 단계 (착공/분양 등)</label>
                    </div>"""

if old_dev1_checkboxes in code:
    code = code.replace(old_dev1_checkboxes, new_dev1_checkboxes)
    print("Updated dev1 checkboxes.")
else:
    old_dev1_checkboxes_lf = old_dev1_checkboxes.replace('\r\n', '\n')
    new_dev1_checkboxes_lf = new_dev1_checkboxes.replace('\r\n', '\n')
    if old_dev1_checkboxes_lf in code:
        code = code.replace(old_dev1_checkboxes_lf, new_dev1_checkboxes_lf)
        print("Updated dev1 checkboxes (LF version).")
    else:
        print("Warning: Could not find dev1 checkboxes target.")

# Redevelopment (dev3) stage checks
old_dev3_checkboxes = """                    <div id="dev3-stages-list" style="border: 1px solid var(--border-color); border-radius: 6px; padding: 6px 10px; background: #fff; display: flex; flex-direction: column; gap: 6px; box-shadow: inset 0 1px 2px rgba(0,0,0,0.05);">
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; cursor: pointer; color: var(--text-dark);"><input type="checkbox" class="dev3-stage-check" value="초기" checked> 초기 단계 (조합설립 등)</label>
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; cursor: pointer; color: var(--text-dark);"><input type="checkbox" class="dev3-stage-check" value="중기" checked> 중기 단계 (사업시행 등)</label>
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; cursor: pointer; color: var(--text-dark);"><input type="checkbox" class="dev3-stage-check" value="후기" checked> 후기 단계 (관리처분 등)</label>
                    </div>"""

new_dev3_checkboxes = """                    <div id="dev3-stages-list" style="border: 1px solid var(--border-color); border-radius: 6px; padding: 6px 10px; background: #fff; display: flex; flex-direction: column; gap: 6px; box-shadow: inset 0 1px 2px rgba(0,0,0,0.05);">
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; cursor: pointer; color: var(--text-dark);"><input type="checkbox" class="dev3-stage-check" value="초기" checked> 초기 단계 (조합설립 등)</label>
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; cursor: pointer; color: var(--text-dark);"><input type="checkbox" class="dev3-stage-check" value="중기"> 중기 단계 (사업시행 등)</label>
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; cursor: pointer; color: var(--text-dark);"><input type="checkbox" class="dev3-stage-check" value="후기"> 후기 단계 (관리처분 등)</label>
                    </div>"""

if old_dev3_checkboxes in code:
    code = code.replace(old_dev3_checkboxes, new_dev3_checkboxes)
    print("Updated dev3 checkboxes.")
else:
    old_dev3_checkboxes_lf = old_dev3_checkboxes.replace('\r\n', '\n')
    new_dev3_checkboxes_lf = new_dev3_checkboxes.replace('\r\n', '\n')
    if old_dev3_checkboxes_lf in code:
        code = code.replace(old_dev3_checkboxes_lf, new_dev3_checkboxes_lf)
        print("Updated dev3 checkboxes (LF version).")
    else:
        print("Warning: Could not find dev3 checkboxes target.")

# 2. Update getTaekjiStage mapping
old_get_taekji = """            function getTaekjiStage(stepCode) {
                if (!stepCode) return '초기';
                const code = stepCode.toUpperCase();
                if (['PP2001', 'PP2002', 'PP2003', 'PP2004'].includes(code)) return '초기';
                if (['PP2005'].includes(code)) return '중기';
                if (['PP2006', 'PP2007'].includes(code)) return '후기';
                return '초기';
            }"""

new_get_taekji = """            function getTaekjiStage(stepCode) {
                if (!stepCode) return '초기';
                const code = stepCode.toUpperCase();
                if (['PC', 'PP2001', 'PP2002', 'PP2003', 'PP2004'].includes(code)) return '초기';
                if (['SA', 'DA', 'PP2005'].includes(code)) return '중기';
                if (['RA', 'CP', 'PP2006', 'PP2007'].includes(code)) return '후기';
                return '초기';
            }"""

if old_get_taekji in code:
    code = code.replace(old_get_taekji, new_get_taekji)
    print("Updated getTaekjiStage function.")
else:
    old_get_taekji_lf = old_get_taekji.replace('\r\n', '\n')
    new_get_taekji_lf = new_get_taekji.replace('\r\n', '\n')
    if old_get_taekji_lf in code:
        code = code.replace(old_get_taekji_lf, new_get_taekji_lf)
        print("Updated getTaekjiStage function (LF version).")
    else:
        print("Warning: Could not find getTaekjiStage function target.")

# 3. Update tooltip stageName mapping
old_tooltip = """                    let stageName = '초기 단계';
                    if (['PP2001', 'PP2002', 'PP2003', 'PP2004'].includes(stepCode)) stageName = '초기 단계 (지구지정 등)';
                    else if (stepCode === 'PP2005') stageName = '중기 단계 (지구계획승인 등)';
                    else if (['PP2006', 'PP2007'].includes(stepCode)) stageName = '후기 단계 (착공/분양 등)';"""

new_tooltip = """                    let stageName = '초기 단계';
                    if (['PC', 'PP2001', 'PP2002', 'PP2003', 'PP2004'].includes(stepCode)) stageName = '초기 단계 (지구지정 등)';
                    else if (['SA', 'DA', 'PP2005'].includes(stepCode)) stageName = '중기 단계 (지구계획승인 등)';
                    else if (['RA', 'CP', 'PP2006', 'PP2007'].includes(stepCode)) stageName = '후기 단계 (착공/분양/완료 등)';"""

if old_tooltip in code:
    code = code.replace(old_tooltip, new_tooltip)
    print("Updated tooltip stageName mapping.")
else:
    old_tooltip_lf = old_tooltip.replace('\r\n', '\n')
    new_tooltip_lf = new_tooltip.replace('\r\n', '\n')
    if old_tooltip_lf in code:
        code = code.replace(old_tooltip_lf, new_tooltip_lf)
        print("Updated tooltip stageName mapping (LF version).")
    else:
        print("Warning: Could not find tooltip stageName mapping target.")

# 4. Remove duplicate toggle-dev1 event listener (lines 2967-3008 approx)
old_duplicate_listener = """        document.getElementById('toggle-dev1').addEventListener('change', async (e) => {
            if (e.target.checked) {
                map.addLayer(layers.dev1);
                if (layers.dev1.getLayers().length === 0) {
                    const loadingOverlay = document.getElementById('loading');
                    if (loadingOverlay) loadingOverlay.style.display = 'flex';
                    try {
                        const res = await fetch('/data/taekji.geojson');
                        if (!res.ok) throw new Error('Network response was not ok');
                        const geojsonData = await res.json();

                        L.geoJSON(geojsonData, {
                            style: function (feature) {
                                return {
                                    fillColor: '#3b82f6', // 파란색
                                    weight: 2,
                                    opacity: 0.8,
                                    color: '#2563eb',
                                    dashArray: '4',
                                    fillOpacity: 0.2
                                };
                            },
                            onEachFeature: function (feature, layer) {
                                const props = feature.properties;
                                layer.bindTooltip(`<b>택지지구</b><br>${props.zoneName || '이름 없음'}`, {
                                    sticky: true,
                                    className: 'custom-tooltip'
                                });
                            }
                        }).addTo(layers.dev1);
                    } catch (error) {
                        console.error('Error loading taekji:', error);
                        alert('택지지구 데이터를 불러오는 데 실패했습니다.');
                    } finally {
                        if (loadingOverlay) loadingOverlay.style.display = 'none';
                    }
                }
            } else {
                map.removeLayer(layers.dev1);
                triggerHighlighter();
            }
        });"""

if old_duplicate_listener in code:
    code = code.replace(old_duplicate_listener, "")
    print("Removed duplicate toggle-dev1 event listener.")
else:
    old_duplicate_listener_lf = old_duplicate_listener.replace('\r\n', '\n')
    if old_duplicate_listener_lf in code:
        code = code.replace(old_duplicate_listener_lf, "")
        print("Removed duplicate toggle-dev1 event listener (LF version).")
    else:
        print("Warning: Could not find duplicate toggle-dev1 listener target.")

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Map.html changes applied successfully!")
