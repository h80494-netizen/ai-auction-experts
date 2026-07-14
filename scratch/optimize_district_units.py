import os

file_path = r"public/map.html"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

content_lf = content.replace("\r\n", "\n")

# 1. Update fetchDistrictUnits with smart caching
old_district_func = """                async function fetchDistrictUnits() {
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
                                color: '#4ade80', //  ʷϻ
                                fillColor: '#4ade80',
                                fillOpacity: 0.15,
                                weight: 2,
                                dashArray: '5, 5'
                            }
                        }).bindPopup(`<b>ȹ</b><br>${item.name}`).addTo(layers.dev2);
                    });
                }
            } catch (err) { console.error(err); } finally { triggerHighlighter(); }
        }"""

# Note: We need to match the original text encoding precisely.
# Let's inspect the original string in public/map.html using python to find out what exactly is there,
# or we can do a regex-based or simpler exact search.
# Let's print out what is there from lines 1800 to 1823.
# Wait, let's write a python script that replaces the function dynamically using a regex or simple start/end.
