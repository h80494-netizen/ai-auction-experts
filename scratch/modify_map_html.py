import os
import sys

file_path = "c:/Users/llll/Documents/두인경매/바이브코딩/public/map.html"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add 예정도로 (100m 버퍼) toggle
planned_road_html = """
            <!-- 예정도로 (100m 버퍼) -->
            <div class="toggle-row" style="flex-direction: column; align-items: stretch; gap: 8px; background: #fff5f5; padding: 10px; border-radius: 8px; margin-top: 5px; border: 1px dashed rgba(239, 68, 68, 0.4);">
                <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
                    <div class="toggle-label"><i class="fa-solid fa-road-circle-exclamation" style="color: #ef4444;"></i> 예정도로 (100m 버퍼)</div>
                    <label class="switch"><input type="checkbox" id="toggle-planned-road-100m" onchange="togglePlannedRoads100m()"><span class="slider"></span></label>
                </div>
            </div>
"""

if "toggle-planned-road-100m" not in content:
    target1 = '<!-- 실거래 가격지표 레이어 -->'
    content = content.replace(target1, planned_road_html + '\n            ' + target1)

# 2. Add 아파트 단지 정보 toggle
apt_info_html = """
            <!-- 아파트 단지 정보 -->
            <div class="toggle-row" style="background: #e0f2fe; padding: 10px; border-radius: 8px; margin-top: 5px;">
                <div class="toggle-label">
                    <div>
                        <i class="fa-solid fa-building" style="color: #0284c7;"></i> 아파트 단지 정보
                        <span class="toggle-desc" style="color: #0369a1;">주거인구 히트맵 기반 상세 단지 정보</span>
                    </div>
                </div>
                <label class="switch"><input type="checkbox" id="toggle-apt-info" onchange="toggleAptInfo()"><span class="slider"></span></label>
            </div>
"""

if "toggle-apt-info" not in content:
    target2 = '<!-- 격자형 직장인구 히트맵 -->'
    if target2 in content:
        content = content.replace(target2, apt_info_html + '\n            ' + target2)
    else:
        # fallback
        target2b = '<div class="toggle-row" style="background: #f5f3ff; padding: 10px;'
        content = content.replace(target2b, apt_info_html + '\n            ' + target2b)

# 3. Add Layer Initialization and JS Logic
js_logic = """
        // [AI_ADDED] Planned Roads and Apartment Info Layers
        let plannedRoadsLayer = null;
        let aptInfoLayer = null;

        async function togglePlannedRoads100m() {
            const isChecked = document.getElementById('toggle-planned-road-100m').checked;
            if (isChecked) {
                if (!plannedRoadsLayer) {
                    try {
                        const res = await fetch('/data/planned_roads_100m.geojson');
                        if (!res.ok) throw new Error("Failed to load geojson");
                        const geoData = await res.json();
                        plannedRoadsLayer = L.geoJSON(geoData, {
                            style: {
                                color: '#ef4444',
                                weight: 2,
                                dashArray: '5, 5',
                                fillColor: '#ef4444',
                                fillOpacity: 0.15
                            },
                            onEachFeature: (feature, layer) => {
                                layer.bindPopup('<b>예정도로 (100m 버퍼)</b>');
                            }
                        }).addTo(map);
                    } catch (e) {
                        console.error('예정도로 버퍼 로딩 실패:', e);
                        alert('예정도로 데이터가 준비되지 않았습니다.');
                        document.getElementById('toggle-planned-road-100m').checked = false;
                    }
                } else {
                    map.addLayer(plannedRoadsLayer);
                }
            } else {
                if (plannedRoadsLayer) map.removeLayer(plannedRoadsLayer);
            }
        }

        async function fetchVWorldParcel(lat, lng, aptInfo) {
            // Call VWorld API to get parcel polygon
            // URL: https://api.vworld.kr/req/data?service=data&request=GetFeature&data=lp_pa_cbnd_bubun&key=OUR_KEY&geomFilter=POINT(lng lat)&crs=EPSG:4326
            // We use the proxy to avoid CORS/Key exposure
            try {
                const res = await fetch(`/api/proxy/vworld?data=lp_pa_cbnd_bubun&geomFilter=POINT(${lng} ${lat})`);
                const data = await res.json();
                if (data.response && data.response.result && data.response.result.featureCollection) {
                    return data.response.result.featureCollection;
                }
            } catch(e) {
                console.error("VWorld parcel fetch error:", e);
            }
            return null;
        }

        let currentHighlightedParcel = null;

        async function toggleAptInfo() {
            const isChecked = document.getElementById('toggle-apt-info').checked;
            if (isChecked) {
                if (!aptInfoLayer) {
                    try {
                        const res = await fetch('/data/apt_info.geojson');
                        if (!res.ok) throw new Error("Failed to load apt geojson");
                        const geoData = await res.json();
                        
                        aptInfoLayer = L.geoJSON(geoData, {
                            pointToLayer: function (feature, latlng) {
                                return L.circleMarker(latlng, {
                                    radius: 6,
                                    fillColor: '#0ea5e9',
                                    color: '#fff',
                                    weight: 1,
                                    opacity: 1,
                                    fillOpacity: 0.8
                                });
                            },
                            onEachFeature: (feature, layer) => {
                                layer.on('click', async (e) => {
                                    // Remove previous highlight
                                    if (currentHighlightedParcel) {
                                        map.removeLayer(currentHighlightedParcel);
                                    }
                                    
                                    const props = feature.properties;
                                    const lat = e.latlng.lat;
                                    const lng = e.latlng.lng;
                                    
                                    // Fetch Parcel
                                    const parcelGeojson = await fetchVWorldParcel(lat, lng, props);
                                    
                                    let popupContent = `<div style="font-family:'Noto Sans KR'; min-width:180px;">`;
                                    popupContent += `<h4 style="margin:0 0 5px 0; color:#0284c7; font-size:15px;">${props.name}</h4>`;
                                    popupContent += `<p style="margin:0 0 5px 0; font-size:12px; color:#64748b;">${props.address}</p>`;
                                    popupContent += `<hr style="margin:5px 0; border-top:1px solid #e2e8f0;">`;
                                    popupContent += `<div style="font-size:13px; font-weight:bold;">세대수: ${props.households} (<span style="color:#ef4444;">${props.parking_ratio}</span>)</div>`;
                                    popupContent += `<div style="font-size:13px;">건축년도: ${props.build_year}년</div>`;
                                    popupContent += `</div>`;
                                    
                                    if (parcelGeojson) {
                                        currentHighlightedParcel = L.geoJSON(parcelGeojson, {
                                            style: {
                                                color: '#0284c7',
                                                weight: 3,
                                                fillColor: '#0284c7',
                                                fillOpacity: 0.3
                                            }
                                        }).addTo(map);
                                        
                                        currentHighlightedParcel.bindPopup(popupContent).openPopup();
                                    } else {
                                        // Fallback if no parcel found
                                        L.popup()
                                            .setLatLng(e.latlng)
                                            .setContent(popupContent)
                                            .openOn(map);
                                    }
                                });
                            }
                        }).addTo(map);
                    } catch (e) {
                        console.error('아파트 정보 로딩 실패:', e);
                        alert('아파트 데이터가 준비되지 않았습니다.');
                        document.getElementById('toggle-apt-info').checked = false;
                    }
                } else {
                    map.addLayer(aptInfoLayer);
                }
            } else {
                if (aptInfoLayer) map.removeLayer(aptInfoLayer);
                if (currentHighlightedParcel) map.removeLayer(currentHighlightedParcel);
            }
        }
        // [/AI_ADDED]
"""

if "// [AI_ADDED] Planned Roads and Apartment Info Layers" not in content:
    # insert before the closing script tag or end of a major logic block
    target3 = "function resetAllLayers() {"
    if target3 in content:
        content = content.replace(target3, js_logic + '\n        ' + target3)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated map.html.")
