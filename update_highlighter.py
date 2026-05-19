import re

with open('public/map.html', encoding='utf-8') as f:
    content = f.read()

new_js = """
// Helper functions for polygon intersection
function getActivePolygonLayers() {
    let activeLayers = [];
    if (map.hasLayer(layers.commercial)) activeLayers.push(layers.commercial);
    if (map.hasLayer(layers.hagwon)) activeLayers.push(layers.hagwon);
    if (map.hasLayer(layers.dev2)) activeLayers.push(layers.dev2);
    if (map.hasLayer(layers.oldBuildings)) activeLayers.push(layers.oldBuildings);
    return activeLayers;
}

function isPointInPolygonGeoJSON(pt, polygonCoords) {
    var x = pt[0], y = pt[1];
    var inside = false;
    for (var i = 0, j = polygonCoords.length - 1; i < polygonCoords.length; j = i++) {
        var xi = polygonCoords[i][0], yi = polygonCoords[i][1];
        var xj = polygonCoords[j][0], yj = polygonCoords[j][1];
        var intersect = ((yi > y) != (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi);
        if (intersect) inside = !inside;
    }
    return inside;
}

function isPointInLayer(ptLngLat, layerGroup) {
    let inside = false;
    layerGroup.eachLayer(function(l) {
        if (inside) return; 
        if (l.feature && l.feature.geometry) {
            let geom = l.feature.geometry;
            if (geom.type === 'Polygon') {
                if (isPointInPolygonGeoJSON(ptLngLat, geom.coordinates[0])) inside = true;
            } else if (geom.type === 'MultiPolygon') {
                for (let i=0; i<geom.coordinates.length; i++) {
                    if (isPointInPolygonGeoJSON(ptLngLat, geom.coordinates[i][0])) {
                        inside = true;
                        break;
                    }
                }
            }
        }
    });
    return inside;
}

// 3. 형광펜 데이터 (Highlighter)
let isHighlighterOn = false;
function toggleHighlighter() {
    isHighlighterOn = !isHighlighterOn;
    const btn = document.getElementById('btn-highlighter');
    if (isHighlighterOn) {
        let activeLayers = getActivePolygonLayers();
        if (activeLayers.length === 0) {
            alert('활성화된 다각형 영역(상권, 학원가, 지구단위계획구역, 노후건축물 등)이 없습니다. 왼쪽 레이어 창에서 먼저 영역을 켜주세요.');
            isHighlighterOn = false;
            return;
        }

        btn.querySelector('i').style.color = '#bd00ff';
        btn.querySelector('i').style.textShadow = '0 0 15px #bd00ff';
        
        let highlightCount = 0;
        layers.auction.eachLayer(function(marker) {
            let d = marker.auctionData;
            if(!marker.originalStyle) {
                marker.originalStyle = {
                    radius: marker.options.radius,
                    color: marker.options.color,
                    fillColor: marker.options.fillColor,
                    weight: marker.options.weight,
                    opacity: marker.options.opacity,
                    fillOpacity: marker.options.fillOpacity
                };
            }
            
            let pt = [d.lng, d.lat];
            let overlapsAll = true;
            for (let i=0; i<activeLayers.length; i++) {
                if (!isPointInLayer(pt, activeLayers[i])) {
                    overlapsAll = false;
                    break;
                }
            }
            
            if(overlapsAll) {
                highlightCount++;
                marker.setStyle({
                    radius: 10,
                    color: '#bd00ff',
                    weight: 4,
                    fillColor: '#bd00ff',
                    fillOpacity: 0.8,
                    opacity: 1
                });
                marker.bringToFront();
            } else {
                marker.setStyle({
                    opacity: 0.1,
                    fillOpacity: 0.1
                });
            }
        });
        alert('형광펜 ON: 중복 영역(선택한 켜져있는 영역 모두 포함) 내 경공매 물건 ' + highlightCount + '건이 집중 강조됩니다.');
    } else {
        btn.querySelector('i').style.color = '';
        btn.querySelector('i').style.textShadow = '';
        
        layers.auction.eachLayer(function(marker) {
            if(marker.originalStyle) {
                marker.setStyle(marker.originalStyle);
                delete marker.originalStyle;
            }
        });
    }
}
"""

start_str = "// 3. 형광펜 데이터 (Highlighter)"
if start_str in content:
    start_idx = content.find(start_str)
    # find the end of toggleHighlighter
    end_str = "    }\n}\n"
    end_idx = content.find(end_str, start_idx) + len(end_str)
    
    content = content[:start_idx] + new_js + content[end_idx:]
    
    with open('public/map.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated")
else:
    print("Not found")
