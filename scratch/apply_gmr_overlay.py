import sys
sys.stdout.reconfigure(encoding='utf-8')

# Read map.html in UTF-8
with open('public/map.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Define the exact text to match and replace
target = """            document.getElementById('toggle-workplace-heatmap').addEventListener('change', (e) => {
                if (e.target.checked) {
                    fetchWorkplaceHeatmap();
                }
            });

            document.getElementById('toggle-road-flows').addEventListener('change', (e) => {
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

replacement = """            document.getElementById('toggle-workplace-heatmap').addEventListener('change', (e) => {
                if (e.target.checked) {
                    fetchWorkplaceHeatmap();
                }
            });

            document.getElementById('toggle-road-flows').addEventListener('change', (e) => {
                if (e.target.checked) {
                    fetchRoadFlows();
                    document.getElementById('road-flow-legend').style.display = 'block';
                } else {
                    layers.roadFlows.clearLayers();
                    cachedRoadFlowBounds = null;
                    cachedRoadFlowZoom = null;
                    document.getElementById('road-flow-legend').style.display = 'none';
                }
            });

            // --- 경기도상권분석서비스 (상존인구 WMS) 관련 연동 로직 ---
            const gmrWmsTile = L.tileLayer.wms('https://sbiz.gmr.or.kr/gis/comm/wms.do', {
                layers: 'vw_gis_pop_road',
                format: 'image/png',
                transparent: true,
                version: '1.1.1',
                crs: L.CRS.EPSG3857,
                viewparams: 'stdr:20253;flag:time;val:20;radius:100;',
                store: 'gmr_new',
                maxZoom: 20,
                minZoom: 10,
                opacity: 0.75
            });

            document.getElementById('toggle-gmr-pop-road').addEventListener('change', (e) => {
                if (e.target.checked) {
                    layers.gmrPopRoad.clearLayers();
                    gmrWmsTile.addTo(layers.gmrPopRoad);
                    map.addLayer(layers.gmrPopRoad);
                } else {
                    map.removeLayer(layers.gmrPopRoad);
                    layers.gmrPopRoad.clearLayers();
                }
            });

            const gmrRow = document.getElementById('gmr-pop-road-row');
            const gmrToggle = document.getElementById('toggle-gmr-pop-road');

            const checkGmrRowVisibility = () => {
                const gyeonggiChecked = Array.from(document.querySelectorAll('.region-checkbox:checked')).some(cb => cb.value === '경기');
                if (gmrRow) {
                    gmrRow.style.display = gyeonggiChecked ? 'flex' : 'none';
                    if (!gyeonggiChecked && gmrToggle && gmrToggle.checked) {
                        gmrToggle.checked = false;
                        gmrToggle.dispatchEvent(new Event('change'));
                    }
                }
            };

            document.querySelectorAll('.region-checkbox').forEach(cb => {
                cb.addEventListener('change', checkGmrRowVisibility);
            });

            checkGmrRowVisibility();
            // ----------------------------------------------------"""

if target in content:
    content = content.replace(target, replacement)
    with open('public/map.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("SUCCESS: GMR WMS layer integration applied successfully to map.html!")
else:
    print("ERROR: Target string not found in map.html! Let's check spacing.")
    # Check if a smaller string matches
    mini_target = "document.getElementById('toggle-road-flows').addEventListener('change'"
    if mini_target in content:
        print("Mini target found! There are probably indentation differences.")
    else:
        print("Mini target NOT found!")
