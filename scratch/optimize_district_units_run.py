import re

file_path = "public/map.html"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Make sure we use LF for robust matching
content_lf = content.replace("\r\n", "\n")

# 1. Locate and replace fetchDistrictUnits()
pattern = re.compile(r"(\s+async function fetchDistrictUnits\(\)\s*\{.*?^\s*\})", re.DOTALL | re.MULTILINE)
matches = pattern.findall(content_lf)

if not matches:
    print("ERROR: fetchDistrictUnits function not found using regex!")
    exit(1)

original_func = matches[0]
print("Found original fetchDistrictUnits function block of length:", len(original_func))

# Let's replace the function with the new cached version
replacement_func = """        let cachedDistrictBounds = null;
        let cachedDistrictZoom = null;

        async function fetchDistrictUnits() {
            const districtMinZoom = 14;
            const currentZoom = map.getZoom();
            if (currentZoom < districtMinZoom) {
                layers.dev2.clearLayers();
                cachedDistrictBounds = null;
                cachedDistrictZoom = null;
                return;
            }
            if (!document.getElementById('toggle-dev2').checked) return;
            
            const bounds = map.getBounds();
            
            // 스마트 캐싱: 줌 레벨이 동일하고, 현재 영역이 캐싱된 패딩 영역 내에 완전히 존재하면 재요청 생략
            if (cachedDistrictZoom === currentZoom && cachedDistrictBounds && cachedDistrictBounds.contains(bounds)) {
                return;
            }
            
            // 25% 패딩을 주어 더 넓은 영역을 한 번에 가져오고 캐싱합니다
            const southWest = bounds.getSouthWest();
            const northEast = bounds.getNorthEast();
            const latDiff = northEast.lat - southWest.lat;
            const lngDiff = northEast.lng - southWest.lng;
            const padLat = latDiff * 0.25;
            const padLng = lngDiff * 0.25;
            
            const paddedBounds = L.latLngBounds(
                L.latLng(southWest.lat - padLat, southWest.lng - padLng),
                L.latLng(northEast.lat + padLat, northEast.lng + padLng)
            );
            
            cachedDistrictBounds = paddedBounds;
            cachedDistrictZoom = currentZoom;
            
            try {
                const res = await fetch(`/api/map/district_units?min_lat=${paddedBounds.getSouth()}&max_lat=${paddedBounds.getNorth()}&min_lng=${paddedBounds.getWest()}&max_lng=${paddedBounds.getEast()}`);
                const json = await res.json();
                if (json.status === 'success') {
                    layers.dev2.clearLayers();
                    json.data.forEach(item => {
                        let geojson = JSON.parse(item.geojson);
                        L.geoJSON(geojson, {
                            style: {
                                color: '#4ade80', // 연한 연두색
                                fillColor: '#4ade80',
                                fillOpacity: 0.15,
                                weight: 2,
                                dashArray: '5, 5'
                            }
                        }).bindPopup(`<b>지구단위계획구역</b><br>${item.name}`).addTo(layers.dev2);
                    });
                }
            } catch (err) { console.error(err); } finally { triggerHighlighter(); }
        }"""

content_lf = content_lf.replace(original_func, replacement_func)

# 2. Add event listener for toggle-dev2
toggle_dev1_target = """            // 개발구역 및 도시계획 세부 컨트롤러 이벤트 리스너 바인딩
            document.getElementById('toggle-dev1').addEventListener('change', updateTaekjiLayer);"""

toggle_dev2_addition = """            // 개발구역 및 도시계획 세부 컨트롤러 이벤트 리스너 바인딩
            document.getElementById('toggle-dev1').addEventListener('change', updateTaekjiLayer);
            document.getElementById('toggle-dev2').addEventListener('change', (e) => {
                if (e.target.checked) {
                    fetchDistrictUnits();
                } else {
                    layers.dev2.clearLayers();
                    cachedDistrictBounds = null;
                    cachedDistrictZoom = null;
                }
            });"""

if toggle_dev1_target in content_lf:
    content_lf = content_lf.replace(toggle_dev1_target, toggle_dev2_addition)
    print("SUCCESS: toggle-dev2 listener added!")
else:
    # Try alternate target without comment
    toggle_dev1_target_alt = "document.getElementById('toggle-dev1').addEventListener('change', updateTaekjiLayer);"
    toggle_dev2_addition_alt = """document.getElementById('toggle-dev1').addEventListener('change', updateTaekjiLayer);
            document.getElementById('toggle-dev2').addEventListener('change', (e) => {
                if (e.target.checked) {
                    fetchDistrictUnits();
                } else {
                    layers.dev2.clearLayers();
                    cachedDistrictBounds = null;
                    cachedDistrictZoom = null;
                }
            });"""
    if toggle_dev1_target_alt in content_lf:
        content_lf = content_lf.replace(toggle_dev1_target_alt, toggle_dev2_addition_alt)
        print("SUCCESS: toggle-dev2 listener added (alt matching)!")
    else:
        print("WARNING: Could not find toggle-dev1 event listener to inject toggle-dev2 listener!")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content_lf)

print("SUCCESS: District units caching applied cleanly!")
