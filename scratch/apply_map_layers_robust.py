file_path = r"c:\Users\llll\Documents\두인경매\바이브코딩\public\map.html"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

start_str = "async function fetchDistrictUnits()"
end_str = "let cachedRoadFlowBounds = null;"

start_idx = content.find(start_str)
end_idx = content.find(end_str)

if start_idx == -1:
    print("ERROR: Could not find start string!")
    exit(1)

if end_idx == -1:
    print("ERROR: Could not find end string!")
    exit(1)

print(f"Found start at {start_idx}, end at {end_idx}")

# The replacement block containing clean fetchDistrictUnits, fetchRedevelopmentZones, and fetchZoningPolygons
replacement_block = """async function fetchDistrictUnits() {
            if (map.getZoom() < minZoomRequired) return;
            if (!document.getElementById('toggle-dev2').checked) return;
            const bounds = map.getBounds();
            try {
                const res = await fetch(`/api/map/district_units?min_lat=${bounds.getSouth()}&max_lat=${bounds.getNorth()}&min_lng=${bounds.getWest()}&max_lng=${bounds.getEast()}`);
                const json = await res.json();
                if (json.status === 'success') {
                    layers.dev2.clearLayers();
                    json.data.forEach(item => {
                        let geojson = JSON.parse(item.geojson);
                        L.geoJSON(geojson, {
                            style: {
                                color: '#4ade80', // 연한 초록색
                                fillColor: '#4ade80',
                                fillOpacity: 0.25,
                                weight: 2,
                                dashArray: '5, 5'
                            }
                        }).bindPopup(`<b>지구단위계획구역</b><br>${item.name}`).addTo(layers.dev2);
                    });
                }
            } catch (err) { console.error(err); } finally { triggerHighlighter(); }
        }

        async function fetchRedevelopmentZones() {
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
        }

        async function fetchZoningPolygons() {
            if (map.getZoom() < minZoomRequired) return;
            if (!document.getElementById('toggle-zoning').checked) return;
            const bounds = map.getBounds();
            try {
                const res = await fetch(`/api/map/zoning?min_lat=${bounds.getSouth()}&max_lat=${bounds.getNorth()}&min_lng=${bounds.getWest()}&max_lng=${bounds.getEast()}`);
                const json = await res.json();
                if (json.status === 'success') {
                    layers.zoning.clearLayers();
                    json.data.forEach(item => {
                        let geojson = JSON.parse(item.geojson);
                        
                        let color = '#6366f1'; // 기타 (Indigo/Purple)
                        let zoningType = '기타';
                        let name = item.name;

                        if (name.includes('전용주거')) {
                            color = '#fef08a'; // 전용주거지역
                            zoningType = '전용주거지역';
                        } else if (name.includes('1종일반주거') || name.includes('제1종일반주거')) {
                            color = '#fef9c3'; // 1종일반주거지역
                            zoningType = '1종일반주거지역';
                        } else if (name.includes('2종일반주거') || name.includes('제2종일반주거')) {
                            color = '#fde047'; // 2종일반주거지역
                            zoningType = '2종일반주거지역';
                        } else if (name.includes('3종일반주거') || name.includes('제3종일반주거')) {
                            color = '#ca8a04'; // 3종일반주거지역
                            zoningType = '3종일반주거지역';
                        } else if (name.includes('준주거')) {
                            color = '#f97316'; // 준주거지역
                            zoningType = '준주거지역';
                        } else if (name.includes('상업')) {
                            color = '#ef4444'; // 상업지역
                            zoningType = '상업지역';
                        } else if (name.includes('준공업')) {
                            color = '#94a3b8'; // 준공업지역
                            zoningType = '준공업지역';
                        } else if (name.includes('일반공업')) {
                            color = '#64748b'; // 일반공업지역
                            zoningType = '일반공업지역';
                        } else if (name.includes('전용공업')) {
                            color = '#334155'; // 전용공업지역
                            zoningType = '전용공업지역';
                        } else if (name.includes('녹지') || name.includes('개발제한구역')) {
                            color = '#22c55e'; // 녹지지역
                            zoningType = '녹지지역';
                        }

                        L.geoJSON(geojson, {
                            style: {
                                color: color,
                                fillColor: color,
                                fillOpacity: 0.25,
                                weight: 1.5,
                                opacity: 0.7
                            }
                        }).bindPopup(`<b>용도지역 (${zoningType})</b><br>${item.name}`).addTo(layers.zoning);
                    });
                }
            } catch (err) { console.error(err); } finally { triggerHighlighter(); }
        }

        """

# Replace content from start_idx to end_idx
new_content = content[:start_idx] + replacement_block + content[end_idx:]

with open(file_path, "w", encoding="utf-8") as f:
    f.write(new_content)

print("SUCCESS: Cleanly and robustly replaced fetchDistrictUnits and added fetchRedevelopmentZones & fetchZoningPolygons!")
