import sys

file_path = r'c:\Users\llll\Documents\두인경매\바이브코딩\public\map.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update min-households input
target_input = '<input type="number" id="min-households" placeholder="ex) 300"'
if target_input in content:
    content = content.replace(target_input, '<input type="number" id="min-households" value="500" placeholder="ex) 500"')

# 2. Update toggleAptInfo logic
target_fetch = "const res = await fetch('/data/apt_info.geojson');"
if target_fetch in content:
    content = content.replace(target_fetch, "const res = await fetch('/data/apt_info_500_polygons.geojson');")

# We need to completely replace the aptInfoLayer initialization
target_layer_start = "aptInfoLayer = L.geoJSON(geoData, {"
target_layer_end = "}).addTo(map);"

if target_layer_start in content and target_layer_end in content:
    start_idx = content.find(target_layer_start)
    end_idx = content.find(target_layer_end, start_idx) + len(target_layer_end)
    
    old_block = content[start_idx:end_idx]
    
    new_block = """aptInfoLayer = L.geoJSON(geoData, {
                            style: {
                                color: '#0ea5e9',
                                weight: 2,
                                fillColor: '#0ea5e9',
                                fillOpacity: 0.4
                            },
                            onEachFeature: (feature, layer) => {
                                const props = feature.properties;
                                
                                const tooltipContent = `<div style="text-align:center; line-height:1.2;">
                                    <span style="font-weight:bold; color:#0369a1; text-shadow:1px 1px 0 #fff, -1px -1px 0 #fff, 1px -1px 0 #fff, -1px 1px 0 #fff;">${props.name}</span><br>
                                    <span style="font-size:0.8em; font-weight:bold; color:#ef4444; text-shadow:1px 1px 0 #fff, -1px -1px 0 #fff, 1px -1px 0 #fff, -1px 1px 0 #fff;">${props.households}세대 / 주차 ${props.parking_ratio}</span>
                                </div>`;
                                
                                layer.bindTooltip(tooltipContent, {
                                    direction: 'center',
                                    offset: [0, 0],
                                    opacity: 0.9
                                });
                                
                                layer.on('click', (e) => {
                                    let popupContent = `<div style="font-family:'Noto Sans KR'; min-width:180px;">`;
                                    popupContent += `<h4 style="margin:0 0 5px 0; color:#0284c7; font-size:15px;">${props.name}</h4>`;
                                    popupContent += `<p style="margin:0 0 5px 0; font-size:12px; color:#64748b;">${props.address}</p>`;
                                    popupContent += `<hr style="margin:5px 0; border-top:1px solid #e2e8f0;">`;
                                    popupContent += `<div style="font-size:13px; font-weight:bold;">세대수: ${props.households} (<span style="color:#ef4444;">${props.parking_ratio}</span>)</div>`;
                                    popupContent += `<div style="font-size:13px;">건축년도: ${props.build_year}년</div>`;
                                    popupContent += `</div>`;
                                    
                                    L.popup().setLatLng(e.latlng).setContent(popupContent).openOn(map);
                                });
                            }
                        }).addTo(map);"""
                        
    content = content.replace(old_block, new_block)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated map.html successfully.")
