with open('public/map.html', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Replace the HTML toggles block
old_html = """            <div class="layer-group-title" style="margin-top: 15px;">개발구역 (진행중)</div>
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
            </div>"""

new_html = """            <div class="layer-group-title" style="margin-top: 15px;">개발구역</div>
            <div class="toggle-row" style="flex-direction: column; align-items: stretch; gap: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
                    <div class="toggle-label"><i class="fa-solid fa-map" style="color: #3b82f6;"></i> 택지지구</div>
                    <label class="switch"><input type="checkbox" id="toggle-dev1"><span class="slider"></span></label>
                </div>
                <div id="dev1-sub-container" style="display: none; padding-left: 20px; margin-top: 4px;">
                    <div style="font-size: 0.75rem; color: #64748b; margin-bottom: 4px; display: flex; justify-content: space-between; align-items: center;">
                        <span>단계 선택 (중복 가능)</span>
                        <span style="font-size: 0.7rem; color: var(--primary-color); cursor: pointer; font-weight: 500;" onclick="toggleAllCheckboxes('dev1-stage-check', true)">전체선택</span>
                    </div>
                    <div id="dev1-stages-list" style="border: 1px solid var(--border-color); border-radius: 6px; padding: 6px 10px; background: #fff; display: flex; flex-direction: column; gap: 6px; box-shadow: inset 0 1px 2px rgba(0,0,0,0.05);">
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; cursor: pointer; color: var(--text-dark);"><input type="checkbox" class="dev1-stage-check" value="초기" checked> 초기 단계 (지구지정 등)</label>
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; cursor: pointer; color: var(--text-dark);"><input type="checkbox" class="dev1-stage-check" value="중기" checked> 중기 단계 (지구계획승인 등)</label>
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; cursor: pointer; color: var(--text-dark);"><input type="checkbox" class="dev1-stage-check" value="후기" checked> 후기 단계 (착공/분양 등)</label>
                    </div>
                </div>
            </div>
            <div class="toggle-row">
                <div class="toggle-label"><i class="fa-solid fa-map" style="color: #64748b;"></i> 지구단위계획구역</div>
                <label class="switch"><input type="checkbox" id="toggle-dev2"><span class="slider"></span></label>
            </div>
            <div class="toggle-row" style="flex-direction: column; align-items: stretch; gap: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
                    <div class="toggle-label"><i class="fa-solid fa-map" style="color: #8b5cf6;"></i> 재개발/재건축구역</div>
                    <label class="switch"><input type="checkbox" id="toggle-dev3"><span class="slider"></span></label>
                </div>
                <div id="dev3-sub-container" style="display: none; padding-left: 20px; margin-top: 4px;">
                    <div style="font-size: 0.75rem; color: #64748b; margin-bottom: 4px; display: flex; justify-content: space-between; align-items: center;">
                        <span>단계 선택 (중복 가능)</span>
                        <span style="font-size: 0.7rem; color: var(--primary-color); cursor: pointer; font-weight: 500;" onclick="toggleAllCheckboxes('dev3-stage-check', true)">전체선택</span>
                    </div>
                    <div id="dev3-stages-list" style="border: 1px solid var(--border-color); border-radius: 6px; padding: 6px 10px; background: #fff; display: flex; flex-direction: column; gap: 6px; box-shadow: inset 0 1px 2px rgba(0,0,0,0.05);">
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; cursor: pointer; color: var(--text-dark);"><input type="checkbox" class="dev3-stage-check" value="초기" checked> 초기 단계 (조합설립 등)</label>
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; cursor: pointer; color: var(--text-dark);"><input type="checkbox" class="dev3-stage-check" value="중기" checked> 중기 단계 (사업시행 등)</label>
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; cursor: pointer; color: var(--text-dark);"><input type="checkbox" class="dev3-stage-check" value="후기" checked> 후기 단계 (관리처분 등)</label>
                    </div>
                </div>
            </div>"""

code = code.replace(old_html.replace('\r\n', '\n'), new_html.replace('\r\n', '\n'))
code = code.replace(old_html, new_html)

# 2. Replace the fetchRedevelopmentZones function
old_fn = """        async function fetchRedevelopmentZones() {
            if (map.getZoom() < minZoomRequired) return;
            if (!document.getElementById('toggle-dev3').checked) return;
            const bounds = map.getBounds();
            try {
                const res = await fetch(`/api/map/redevelopment_zones?min_lat=${bounds.getSouth()}&max_lat=${bounds.getNorth()}&min_lng=${bounds.getWest()}&max_lng=${bounds.getEast()}`);
                const json = await res.json();
                if (json.status === 'success') {
                    layers.dev3.clearLayers();
                    json.data.forEach(item => {
                        let geojson = JSON.parse(item.geojson);
                        L.geoJSON(geojson, {
                            style: {
                                color: '#f97316', // 주황색 (Orange)
                                fillColor: '#f97316',
                                fillOpacity: 0.25,
                                weight: 2,
                                dashArray: '5, 5'
                            }
                        }).bindPopup(`<b>재개발/재건축구역</b><br>${item.name}`).addTo(layers.dev3);
                    });
                }
            } catch (err) { console.error(err); } finally { triggerHighlighter(); }
        }"""

new_fn = """        function getRedevelopmentStage(propelCd) {
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
                                color: '#f97316', // 주황색 (Orange)
                                fillColor: '#f97316',
                                fillOpacity: 0.25,
                                weight: 2,
                                dashArray: '5, 5'
                            }
                        }).bindPopup(`<b>재개발/재건축구역 (${stageLabel})</b><br>${item.name}`).addTo(layers.dev3);
                    });
                }
            } catch (err) { console.error(err); } finally { triggerHighlighter(); }
        }"""

code = code.replace(old_fn.replace('\r\n', '\n'), new_fn.replace('\r\n', '\n'))
code = code.replace(old_fn, new_fn)

# 3. Replace the toggleMap handling
old_toggles = """                        if (id === 'toggle-dev2') fetchDistrictUnits();
                        if (id === 'toggle-dev3') fetchRedevelopmentZones();
                        if (id === 'toggle-zoning') {
                            fetchZoningPolygons();
                            document.getElementById('zoning-sub-container').style.display = 'block';
                        }
                        if (id === 'toggle-planning-road') {
                            fetchPlanningRoads();
                            document.getElementById('planning-road-sub-container').style.display = 'block';
                        }
                    } else {
                        layerList.forEach(l => map.removeLayer(l));
                        if (id === 'toggle-zoning') {
                            document.getElementById('zoning-sub-container').style.display = 'none';
                        }
                        if (id === 'toggle-planning-road') {
                            document.getElementById('planning-road-sub-container').style.display = 'none';
                        }
                    }"""

new_toggles = """                        if (id === 'toggle-dev2') fetchDistrictUnits();
                        if (id === 'toggle-dev3') {
                            fetchRedevelopmentZones();
                            document.getElementById('dev3-sub-container').style.display = 'block';
                        }
                        if (id === 'toggle-zoning') {
                            fetchZoningPolygons();
                            document.getElementById('zoning-sub-container').style.display = 'block';
                        }
                        if (id === 'toggle-planning-road') {
                            fetchPlanningRoads();
                            document.getElementById('planning-road-sub-container').style.display = 'block';
                        }
                    } else {
                        layerList.forEach(l => map.removeLayer(l));
                        if (id === 'toggle-dev3') {
                            document.getElementById('dev3-sub-container').style.display = 'none';
                        }
                        if (id === 'toggle-zoning') {
                            document.getElementById('zoning-sub-container').style.display = 'none';
                        }
                        if (id === 'toggle-planning-road') {
                            document.getElementById('planning-road-sub-container').style.display = 'none';
                        }
                    }"""

code = code.replace(old_toggles.replace('\r\n', '\n'), new_toggles.replace('\r\n', '\n'))
code = code.replace(old_toggles, new_toggles)

# 4. Replace the checkbox event listeners and add .dev3-stage-check listener and toggleAllCheckboxes logic
old_checkboxes = """            // 용도지역 세부 분류 체크박스 이벤트 리스너
            document.querySelectorAll('.zoning-class-check').forEach(cb => {
                cb.addEventListener('change', () => {
                    fetchZoningPolygons();
                });
            });

            // 도시계획도로 세부 분류 체크박스 이벤트 리스너
            document.querySelectorAll('.planning-road-class-check').forEach(cb => {
                cb.addEventListener('change', () => {
                    fetchPlanningRoads();
                });
            });

            // 전체선택 / 전체해제 헬퍼 함수
            window.toggleAllCheckboxes = function(className, checked) {
                const checkboxes = document.querySelectorAll('.' + className);
                checkboxes.forEach(cb => {
                    cb.checked = checked;
                });
                // Trigger change event once to redraw
                if (className === 'zoning-class-check') {
                    fetchZoningPolygons();
                } else if (className === 'planning-road-class-check') {
                    fetchPlanningRoads();
                }
            };"""

new_checkboxes = """            // 용도지역 세부 분류 체크박스 이벤트 리스너
            document.querySelectorAll('.zoning-class-check').forEach(cb => {
                cb.addEventListener('change', () => {
                    fetchZoningPolygons();
                });
            });

            // 도시계획도로 세부 분류 체크박스 이벤트 리스너
            document.querySelectorAll('.planning-road-class-check').forEach(cb => {
                cb.addEventListener('change', () => {
                    fetchPlanningRoads();
                });
            });

            // 재개발/재건축 세부 분류 체크박스 이벤트 리스너
            document.querySelectorAll('.dev3-stage-check').forEach(cb => {
                cb.addEventListener('change', () => {
                    fetchRedevelopmentZones();
                });
            });

            // 전체선택 / 전체해제 헬퍼 함수
            window.toggleAllCheckboxes = function(className, checked) {
                const checkboxes = document.querySelectorAll('.' + className);
                checkboxes.forEach(cb => {
                    cb.checked = checked;
                });
                // Trigger change event once to redraw
                if (className === 'zoning-class-check') {
                    fetchZoningPolygons();
                } else if (className === 'planning-road-class-check') {
                    fetchPlanningRoads();
                } else if (className === 'dev1-stage-check') {
                    const toggleDev1 = document.getElementById('toggle-dev1');
                    if (toggleDev1 && toggleDev1.checked) {
                        toggleDev1.dispatchEvent(new Event('change'));
                    }
                } else if (className === 'dev3-stage-check') {
                    fetchRedevelopmentZones();
                }
            };"""

code = code.replace(old_checkboxes.replace('\r\n', '\n'), new_checkboxes.replace('\r\n', '\n'))
code = code.replace(old_checkboxes, new_checkboxes)

# 5. Replace the toggle-dev1 listener
old_dev1 = """            document.getElementById('toggle-dev1').addEventListener('change', async (e) => {
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

new_dev1 = """            let cachedTaekjiGeoJSON = null;

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
                            fillOpacity: 0.2
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

            document.getElementById('toggle-dev1').addEventListener('change', updateTaekjiLayer);
            document.querySelectorAll('.dev1-stage-check').forEach(cb => {
                cb.addEventListener('change', updateTaekjiLayer);
            });"""

code = code.replace(old_dev1.replace('\r\n', '\n'), new_dev1.replace('\r\n', '\n'))
code = code.replace(old_dev1, new_dev1)

with open('public/map.html', 'w', encoding='utf-8') as f:
    f.write(code)

print("HTML and JS Modification complete!")
