import re

with open('public/map.html', 'r', encoding='utf-8') as f:
    content = f.read()

old_func = """                const typeMap = {
                '개발행위허가제한지역': 'LT_C_UD801',
                '개발진흥지구': 'LT_C_UD080',
                '복합용도지구': 'LT_C_UD110',
                '입지규제최소구역': 'LT_C_UD061',
                '방재지구': 'LT_C_UD090',
                '자연취락지구': 'LT_C_UQ111'
            };

            for (const typeName of checkedTypes) {
                const layerCode = typeMap[typeName];
                if (!layerCode) continue;
                
                try {
                    const res = await fetch(`/api/proxy/vworld?data=${layerCode}&geomFilter=${geomFilter}`);
                    const json = await res.json();
                    if (json && json.response && json.response.result && json.response.result.featureCollection) {
                        L.geoJSON(json.response.result.featureCollection, {
                            style: {
                                color: '#ec4899',
                                fillColor: '#ec4899',
                                fillOpacity: 0.2,
                                weight: 2,
                                dashArray: '5, 5'
                            },
                            onEachFeature: function(feature, layer) {
                                layer.bindPopup(`<b>${typeName}</b>`);
                                // Custom layer name tag for highlighter intersection logic
                                layer.layerName = typeName;
                            }
                        }).addTo(layers.dev4);
                    }
                } catch (err) {
                    console.error(`Failed to fetch ${typeName} from VWorld:`, err);
                }
            }"""

new_func = """                const typeMap = {
                '개발행위허가제한지역': 'LT_C_UD801',
                // 개발진흥지구 is handled separately via local GeoJSON
                '복합용도지구': 'LT_C_UD110',
                '입지규제최소구역': 'LT_C_UD061',
                '방재지구': 'LT_C_UD090',
                '자연취락지구': 'LT_C_UQ111'
            };

            for (const typeName of checkedTypes) {
                if (typeName === '개발진흥지구') {
                    if (!window.devPromotionLayer) {
                        try {
                            const res = await fetch('/dev_promotion.geojson');
                            const data = await res.json();
                            window.devPromotionLayer = L.geoJSON(data, {
                                style: {
                                    color: '#ec4899',
                                    fillColor: '#ec4899',
                                    fillOpacity: 0.2,
                                    weight: 2,
                                    dashArray: '5, 5'
                                },
                                onEachFeature: function(feature, layer) {
                                    layer.bindPopup(`<b>${typeName}</b>`);
                                    layer.layerName = typeName;
                                }
                            });
                        } catch (err) {
                            console.error('Failed to load 개발진흥지구:', err);
                        }
                    }
                    if (window.devPromotionLayer) {
                        window.devPromotionLayer.addTo(layers.dev4);
                    }
                    continue;
                }

                const layerCode = typeMap[typeName];
                if (!layerCode) continue;
                
                try {
                    const res = await fetch(`/api/proxy/vworld?data=${layerCode}&geomFilter=${geomFilter}`);
                    const json = await res.json();
                    if (json && json.response && json.response.result && json.response.result.featureCollection) {
                        L.geoJSON(json.response.result.featureCollection, {
                            style: {
                                color: '#ec4899',
                                fillColor: '#ec4899',
                                fillOpacity: 0.2,
                                weight: 2,
                                dashArray: '5, 5'
                            },
                            onEachFeature: function(feature, layer) {
                                layer.bindPopup(`<b>${typeName}</b>`);
                                // Custom layer name tag for highlighter intersection logic
                                layer.layerName = typeName;
                            }
                        }).addTo(layers.dev4);
                    }
                } catch (err) {
                    console.error(`Failed to fetch ${typeName} from VWorld:`, err);
                }
            }"""

if old_func in content:
    content = content.replace(old_func, new_func)
    with open('public/map.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Successfully updated fetchDeregulationZones in map.html")
else:
    print("Could not find the target code block in map.html")
