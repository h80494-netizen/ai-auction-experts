import sys

file_path = r'c:\Users\llll\Documents\두인경매\바이브코딩\public\map.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Target block
target = """                            pointToLayer: function (feature, latlng) {
                                return L.circleMarker(latlng, {
                                    radius: 6,
                                    fillColor: '#0ea5e9',
                                    color: '#fff',
                                    weight: 1,
                                    opacity: 1,
                                    fillOpacity: 0.8
                                });
                            },"""

# Replacement block
replacement = """                            pointToLayer: function (feature, latlng) {
                                const props = feature.properties;
                                const marker = L.circleMarker(latlng, {
                                    radius: 6,
                                    fillColor: '#0ea5e9',
                                    color: '#fff',
                                    weight: 1,
                                    opacity: 1,
                                    fillOpacity: 0.8
                                });
                                
                                const tooltipContent = `<div style="text-align:center; line-height:1.2;">
                                    <span style="font-weight:bold; color:#0369a1; text-shadow:1px 1px 0 #fff, -1px -1px 0 #fff, 1px -1px 0 #fff, -1px 1px 0 #fff;">${props.name}</span><br>
                                    <span style="font-size:0.8em; font-weight:bold; color:#ef4444; text-shadow:1px 1px 0 #fff, -1px -1px 0 #fff, 1px -1px 0 #fff, -1px 1px 0 #fff;">${props.households}세대 / 주차 ${props.parking_ratio}</span>
                                </div>`;
                                
                                marker.bindTooltip(tooltipContent, {
                                    permanent: true,
                                    direction: 'top',
                                    className: 'apt-label-tooltip',
                                    offset: [0, -5],
                                    opacity: 0.9
                                });
                                return marker;
                            },"""

if target in content:
    content = content.replace(target, replacement)
    
    # Also add the zoom listener to show/hide the tooltips to prevent clutter
    zoom_listener = """        map.on('zoomend', function() {
            if (map.getZoom() < 14) {
                document.querySelectorAll('.apt-label-tooltip').forEach(el => el.style.display = 'none');
            } else {
                document.querySelectorAll('.apt-label-tooltip').forEach(el => el.style.display = 'block');
            }
        });
"""
    if "map.on('zoomend', function() {" not in content:
        # inject after aptInfoLayer is created
        insert_target = "aptInfoLayer = L.geoJSON(geoData, {"
        content = content.replace(insert_target, zoom_listener + "\n                        " + insert_target)

    # And add CSS for the tooltip
    css_target = "</style>"
    css = """
        .apt-label-tooltip {
            background: transparent;
            border: none;
            box-shadow: none;
            font-family: 'Noto Sans KR', sans-serif;
            font-size: 0.8rem;
            white-space: nowrap;
        }
        .leaflet-tooltip-left.apt-label-tooltip::before,
        .leaflet-tooltip-right.apt-label-tooltip::before,
        .leaflet-tooltip-top.apt-label-tooltip::before,
        .leaflet-tooltip-bottom.apt-label-tooltip::before {
            display: none; /* Hide the tooltip arrow */
        }
"""
    if ".apt-label-tooltip" not in content:
        content = content.replace(css_target, css + "\n    " + css_target)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Successfully replaced map.html to display permanent labels on zoom.")
else:
    print("Target block not found. Already replaced or modified.")
