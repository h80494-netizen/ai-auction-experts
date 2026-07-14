import os

html_path = 'public/map.html'
if not os.path.exists(html_path):
    print("Error: public/map.html not found")
    exit(1)

with open(html_path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. UI Button Injection
old_span = """            <span id="highlight-count"
                style="display: none; font-size: 0.85rem; font-weight: bold; color: #c026d3; margin-right: 5px; background: #fdf4ff; padding: 4px 8px; border-radius: 12px; border: 1px solid #c026d3; white-space: nowrap;">0건
                중첩</span>"""

new_span_btn = """            <span id="highlight-count"
                style="display: none; font-size: 0.85rem; font-weight: bold; color: #c026d3; margin-right: 5px; background: #fdf4ff; padding: 4px 8px; border-radius: 12px; border: 1px solid #c026d3; white-space: nowrap;">0건
                중첩</span>
            <button id="btn-show-analysis"
                style="display: none; font-size: 0.85rem; font-weight: bold; color: #fff; background: #c026d3; border: none; padding: 5px 12px; border-radius: 12px; cursor: pointer; transition: all 0.2s; white-space: nowrap; box-shadow: 0 2px 4px rgba(192, 38, 211, 0.2);"
                onclick="openAnalysisScreen()">
                <i class="fa-solid fa-chart-line"></i> 분석 결과 & BEST 3
            </button>"""

if old_span in code:
    code = code.replace(old_span, new_span_btn)
    print("Successfully injected analysis button into map.html")
else:
    old_span_lf = old_span.replace('\r\n', '\n')
    new_span_btn_lf = new_span_btn.replace('\r\n', '\n')
    if old_span_lf in code:
        code = code.replace(old_span_lf, new_span_btn_lf)
        print("Successfully injected analysis button into map.html (LF version)")
    else:
        print("Failed to find highlight-count span in map.html!")
        exit(1)

# 2. applyHighlighter function replacement
old_highlighter_fn = """        let highlightedCaseNos = [];

        function applyHighlighter() {
            const btnHighlighter = document.getElementById('btn-highlighter');
            const countEl = document.getElementById('highlight-count');
            highlightedCaseNos = [];

            if (!btnHighlighter || !btnHighlighter.classList.contains('active')) {
                layers.auction.eachLayer(marker => {
                    marker.setStyle({
                        radius: 6, color: '#fff', weight: 2, fillColor: marker.typeColor, fillOpacity: 1
                    });
                });
                if (countEl) countEl.style.display = 'none';
                return;
            }

            const activeFilterIds = [
                { id: 'toggle-subways', layer: layers.subway },
                { id: 'toggle-univs', layer: layers.univ },
                { id: 'toggle-inds', layer: layers.ind },
                { id: 'toggle-middles', layer: layers.middle },
                { id: 'toggle-commercial', layer: layers.commercial },
                { id: 'toggle-hagwons', layer: layers.hagwon },
                { id: 'toggle-dev1', layer: layers.dev1 },
                { id: 'toggle-dev2', layer: layers.dev2 },
                { id: 'toggle-planning-road', layer: layers.planningRoads },
                { id: 'toggle-old-buildings', layer: layers.oldBuildings }
            ];

            const activeLayers = [];
            activeFilterIds.forEach(f => {
                const el = document.getElementById(f.id);
                if (el && el.checked) {
                    activeLayers.push(f.layer);
                }
            });

            if (activeLayers.length === 0) {
                layers.auction.eachLayer(marker => {
                    marker.setStyle({
                        radius: 6, color: '#fff', weight: 2, fillColor: marker.typeColor, fillOpacity: 1
                    });
                });
                return;
            }

            layers.auction.eachLayer(marker => {
                const latlng = marker.getLatLng();
                const pt = window.turf ? turf.point([latlng.lng, latlng.lat]) : null;
                
                const modeEl = document.querySelector('input[name="highlighter-mode"]:checked');
                const mode = modeEl ? modeEl.value : 'OR';

                let isInside = false;
                if (mode === 'AND') {
                    isInside = true;
                    for (let i = 0; i < activeLayers.length; i++) {
                        if (!checkPointInLayerGroup(pt, activeLayers[i], latlng)) {
                            isInside = false;
                            break;
                        }
                    }
                } else {
                    isInside = false;
                    for (let i = 0; i < activeLayers.length; i++) {
                        if (checkPointInLayerGroup(pt, activeLayers[i], latlng)) {
                            isInside = true;
                            break;
                        }
                    }
                }

                if (isInside) {
                    marker.setStyle({
                        radius: 10, color: '#c026d3', weight: 4, fillColor: marker.typeColor, fillOpacity: 1
                    });
                    if (marker.bringToFront) marker.bringToFront();
                    highlightedCaseNos.push(marker.auctionData.case_no);
                } else {
                    marker.setStyle({
                        radius: 4, color: '#94a3b8', weight: 1, fillColor: marker.typeColor, fillOpacity: 0.3
                    });
                }
            });

            if (countEl) {
                if (activeLayers.length > 0) {
                    countEl.innerText = `${highlightedCaseNos.length}건 중첩`;
                    countEl.style.display = 'inline-block';
                } else {
                    countEl.style.display = 'none';
                }
            }
        }"""

new_highlighter_fn = """        let highlightedCaseNos = [];
        let highlightedAuctions = [];

        function applyHighlighter() {
            const btnHighlighter = document.getElementById('btn-highlighter');
            const countEl = document.getElementById('highlight-count');
            const analysisBtn = document.getElementById('btn-show-analysis');
            highlightedCaseNos = [];
            highlightedAuctions = [];

            if (!btnHighlighter || !btnHighlighter.classList.contains('active')) {
                layers.auction.eachLayer(marker => {
                    marker.setStyle({
                        radius: 6, color: '#fff', weight: 2, fillColor: marker.typeColor, fillOpacity: 1
                    });
                });
                if (countEl) countEl.style.display = 'none';
                if (analysisBtn) analysisBtn.style.display = 'none';
                return;
            }

            const activeFilterIds = [
                { id: 'toggle-subways', layer: layers.subway, name: '지하철역' },
                { id: 'toggle-univs', layer: layers.univ, name: '대학교' },
                { id: 'toggle-inds', layer: layers.ind, name: '산업단지' },
                { id: 'toggle-middles', layer: layers.middle, name: '학군(중학교)' },
                { id: 'toggle-commercial', layer: layers.commercial, name: '상권' },
                { id: 'toggle-hagwons', layer: layers.hagwon, name: '학원가' },
                { id: 'toggle-dev1', layer: layers.dev1, name: '택지지구' },
                { id: 'toggle-dev2', layer: layers.dev2, name: '지구단위계획구역' },
                { id: 'toggle-planning-road', layer: layers.planningRoads, name: '도시계획도로' },
                { id: 'toggle-old-buildings', layer: layers.oldBuildings, name: '노후건물' },
                { id: 'toggle-crosswalks', layer: layers.crosswalk, name: '횡단보도' },
                { id: 'toggle-dev3', layer: layers.dev3, name: '재개발/재건축구역' }
            ];

            const activeLayers = [];
            activeFilterIds.forEach(f => {
                const el = document.getElementById(f.id);
                if (el && el.checked) {
                    activeLayers.push(f);
                }
            });

            if (activeLayers.length === 0) {
                layers.auction.eachLayer(marker => {
                    marker.setStyle({
                        radius: 6, color: '#fff', weight: 2, fillColor: marker.typeColor, fillOpacity: 1
                    });
                });
                if (countEl) countEl.style.display = 'none';
                if (analysisBtn) analysisBtn.style.display = 'none';
                return;
            }

            layers.auction.eachLayer(marker => {
                const latlng = marker.getLatLng();
                const pt = window.turf ? turf.point([latlng.lng, latlng.lat]) : null;
                
                const modeEl = document.querySelector('input[name="highlighter-mode"]:checked');
                const mode = modeEl ? modeEl.value : 'OR';

                let matchCount = 0;
                let matchedNames = [];

                activeLayers.forEach(al => {
                    if (checkPointInLayerGroup(pt, al.layer, latlng)) {
                        matchCount++;
                        matchedNames.push(al.name);
                    }
                });

                let isInside = false;
                if (mode === 'AND') {
                    isInside = (matchCount === activeLayers.length);
                } else {
                    isInside = (matchCount > 0);
                }

                if (isInside) {
                    marker.setStyle({
                        radius: 10, color: '#c026d3', weight: 4, fillColor: marker.typeColor, fillOpacity: 1
                    });
                    if (marker.bringToFront) marker.bringToFront();
                    highlightedCaseNos.push(marker.auctionData.case_no);
                    
                    highlightedAuctions.push({
                        case_no: marker.auctionData.case_no,
                        address: marker.auctionData.address,
                        property_type: marker.auctionData.property_type,
                        appraisal_price: marker.auctionData.appraisal_price,
                        min_price: marker.auctionData.min_price,
                        special_notes: marker.auctionData.special_notes || '',
                        overlap_count: matchCount,
                        matched_layers: matchedNames,
                        lat: latlng.lat,
                        lng: latlng.lng
                    });
                } else {
                    marker.setStyle({
                        radius: 4, color: '#94a3b8', weight: 1, fillColor: marker.typeColor, fillOpacity: 0.3
                    });
                }
            });

            if (countEl) {
                if (activeLayers.length > 0) {
                    countEl.innerText = `${highlightedCaseNos.length}건 중첩`;
                    countEl.style.display = 'inline-block';
                } else {
                    countEl.style.display = 'none';
                }
            }

            if (analysisBtn) {
                if (highlightedCaseNos.length > 0) {
                    analysisBtn.style.display = 'inline-block';
                } else {
                    analysisBtn.style.display = 'none';
                }
            }
        }

        function openAnalysisScreen() {
            if (highlightedAuctions && highlightedAuctions.length > 0) {
                localStorage.setItem('highlighted_auctions', JSON.stringify(highlightedAuctions));
                window.open('analysis.html', '_blank');
            } else {
                alert('형광펜으로 중첩된 경매 물건이 없습니다.');
            }
        }"""

if old_highlighter_fn in code:
    code = code.replace(old_highlighter_fn, new_highlighter_fn)
    print("Successfully replaced applyHighlighter in map.html")
else:
    old_highlighter_fn_lf = old_highlighter_fn.replace('\r\n', '\n')
    new_highlighter_fn_lf = new_highlighter_fn.replace('\r\n', '\n')
    if old_highlighter_fn_lf in code:
        code = code.replace(old_highlighter_fn_lf, new_highlighter_fn_lf)
        print("Successfully replaced applyHighlighter in map.html (LF version)")
    else:
        print("Failed to find applyHighlighter function block in map.html!")
        exit(1)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Map.html modifications complete!")
