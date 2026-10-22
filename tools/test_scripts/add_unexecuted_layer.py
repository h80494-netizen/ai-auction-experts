import os

def insert_after(lines, search_text, insert_lines):
    for i, line in enumerate(lines):
        if search_text in line:
            return lines[:i+1] + insert_lines + lines[i+1:]
    print(f"Warning: '{search_text}' not found")
    return lines

def main():
    map_html_path = 'public/map.html'
    
    with open(map_html_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    # 1. Add toggle UI after 개발행위허가제한지역
    lines = insert_after(lines, 'id="toggle-dev2"', [
        '            <!-- 장기미집행 10년 이상 -->\n',
        '            <div class="toggle-row">\n',
        '                <div class="toggle-label"><i class="fa-solid fa-map" style="color: #a855f7;"></i> 장기미집행 10년 이상</div>\n',
        '                <label class="switch"><input type="checkbox" id="toggle-unexecuted"><span class="slider"></span></label>\n',
        '            </div>\n',
        '\n'
    ])
    
    # 2. Add cache variables
    lines = insert_after(lines, 'let cachedDistrictUnitsZoom = null;', [
        '        let cachedUnexecutedData = null;\n',
        '        let cachedUnexecutedBounds = null;\n',
        '        let cachedUnexecutedZoom = null;\n'
    ])
    
    # 3. Add to layers object
    lines = insert_after(lines, 'dev2: L.layerGroup(),', [
        '            unexecuted: L.layerGroup(),\n'
    ])
    
    # 4. Add to layer toggles mapping
    lines = insert_after(lines, "{ id: 'toggle-dev2', layer: layers.dev2, isLine: false },", [
        "            { id: 'toggle-unexecuted', layer: layers.unexecuted, isLine: false },\n"
    ])
    
    lines = insert_after(lines, "{ id: 'toggle-dev2', layer: layers.dev2, name: '개발행위허가제한지역', isLine: false },", [
        "            { id: 'toggle-unexecuted', layer: layers.unexecuted, name: '장기미집행 10년이상', isLine: false },\n"
    ])
    
    lines = insert_after(lines, "'toggle-dev2': [layers.dev2],", [
        "            'toggle-unexecuted': [layers.unexecuted],\n"
    ])
    
    # 5. Add fetchUnexecutedFacilities function
    fetch_func = """
        async function fetchUnexecutedFacilities() {
            if (map.getZoom() < minZoomRequired) return;
            if (!document.getElementById('toggle-unexecuted').checked) return;
            
            const bounds = map.getBounds();
            const isCached = cachedUnexecutedZoom === map.getZoom() && 
                             cachedUnexecutedBounds && 
                             cachedUnexecutedBounds.contains(bounds) && 
                             cachedUnexecutedData;

            let data;
            if (isCached) {
                console.log("Unexecuted facilities loaded from cache.");
                data = cachedUnexecutedData;
            } else {
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

                try {
                    const res = await fetch(`/api/map/unexecuted_facilities?min_lat=${paddedBounds.getSouth()}&max_lat=${paddedBounds.getNorth()}&min_lng=${paddedBounds.getWest()}&max_lng=${paddedBounds.getEast()}`);
                    const json = await res.json();
                    if (json.status === 'success') {
                        cachedUnexecutedData = json.data;
                        cachedUnexecutedBounds = paddedBounds;
                        cachedUnexecutedZoom = map.getZoom();
                        data = cachedUnexecutedData;
                    } else {
                        return;
                    }
                } catch (err) {
                    console.error("Failed to fetch unexecuted facilities:", err);
                    return;
                }
            }

            layers.unexecuted.clearLayers();
            data.forEach(item => {
                let geojson = JSON.parse(item.geojson);
                L.geoJSON(geojson, {
                    style: {
                        color: '#a855f7', // 보라색 계열
                        fillColor: '#a855f7',
                        fillOpacity: 0.2,
                        weight: 2,
                        dashArray: '3, 3'
                    }
                }).bindPopup(`<b>장기미집행 10년 이상</b><br>${item.name}`).addTo(layers.unexecuted);
            });
            triggerHighlighter();
        }
"""
    lines = insert_after(lines, 'addTo(layers.dev2);', fetch_func.splitlines(keepends=True))
    
    # 6. Call it inside event handlers
    lines = insert_after(lines, "if (document.getElementById('toggle-dev2').checked) {", [
        "                if (document.getElementById('toggle-unexecuted') && document.getElementById('toggle-unexecuted').checked) {\n",
        "                    fetchUnexecutedFacilities();\n",
        "                }\n"
    ])
    
    # And there is another place for toggle-dev2
    # Find the one inside document.getElementById('toggle-dev2').addEventListener('change', ...)
    for i, line in enumerate(lines):
        if "document.getElementById('toggle-dev2').addEventListener('change'" in line:
            # Insert after the block
            # Actually just inject the listener directly
            lines.insert(i-1, """
            document.getElementById('toggle-unexecuted').addEventListener('change', function() {
                if (this.checked) {
                    if (map.getZoom() >= minZoomRequired) {
                        fetchUnexecutedFacilities();
                    }
                } else {
                    layers.unexecuted.clearLayers();
                    triggerHighlighter();
                }
            });
            """)
            break

    with open(map_html_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
        
    print("map.html successfully updated!")

if __name__ == '__main__':
    main()
