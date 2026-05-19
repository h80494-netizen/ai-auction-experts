import re

file_path = 'public/map.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update buffer-inds value to 1000
content = content.replace('id="buffer-inds" value="500"', 'id="buffer-inds" value="1000"')

# 2. Add address UI in top-center
address_ui = '''
            <div id="center-address-box" style="display: flex; align-items: center; justify-content: center; background: #fff; padding: 6px 12px; border-radius: 8px; border: 1px solid var(--border-color); font-weight: bold; color: var(--text-dark); cursor: pointer; min-width: 250px; text-align: center; margin: 0 15px;" onclick="addCenterMarker()">
                <i class="fa-solid fa-location-crosshairs" style="color: #ef4444; margin-right: 8px;"></i>
                <span id="center-address-text">위치 불러오는 중...</span>
            </div>
'''
# We will inject this before <div class="region-toggles"
content = content.replace('<div class="region-toggles"', address_ui + '            <div class="region-toggles"')

# 3. Add JS functions
js_code = '''
        let centerMarker = null;

        function updateCenterAddress() {
            const center = map.getCenter();
            fetch(`https://dapi.kakao.com/v2/local/geo/coord2address.json?x=${center.lng}&y=${center.lat}`, {
                headers: { 'Authorization': 'KakaoAK 9e5265220f87e54e4379077cb60071bb' }
            })
            .then(res => res.json())
            .then(data => {
                let addressText = "주소 정보를 찾을 수 없습니다";
                if (data.documents && data.documents.length > 0) {
                    const doc = data.documents[0];
                    addressText = doc.road_address ? doc.road_address.address_name : doc.address.address_name;
                }
                document.getElementById('center-address-text').innerText = addressText;
            })
            .catch(err => {
                console.error('Failed to reverse geocode', err);
                document.getElementById('center-address-text').innerText = "주소 변환 실패";
            });
        }

        function addCenterMarker() {
            const center = map.getCenter();
            if (centerMarker) {
                map.removeLayer(centerMarker);
            }
            centerMarker = L.marker([center.lat, center.lng], {
                icon: L.divIcon({
                    html: '<div style="color: #ef4444; font-size: 24px;"><i class="fa-solid fa-location-dot"></i></div>',
                    className: 'custom-center-marker',
                    iconSize: [24, 24],
                    iconAnchor: [12, 24]
                })
            }).addTo(map);
            
            // Re-center map to exactly the clicked center to provide feedback
            map.setView(center, map.getZoom());
        }
        
        // Initial call
        updateCenterAddress();
'''

# Find a good place to inject the new JS functions, maybe just before map.on('moveend'
content = content.replace("map.on('moveend', () => {", js_code + "\n            map.on('moveend', () => {")

# Also inject updateCenterAddress() inside the moveend debounce block
content = content.replace("fetchInfraData();", "updateCenterAddress();\n                    fetchInfraData();")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Map updated successfully")
