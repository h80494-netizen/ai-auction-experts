import re

with open('public/map.html', 'r', encoding='utf-8') as f:
    map_html = f.read()

# Change 1: UI
map_html = map_html.replace('value="자연취락지구"> 자연취락지구</label>', 'value="취락지구"> 취락지구</label>')

# Change 2 & 3: JS Logic
old_typeMap = """            const typeMap = {
                '개발행위허가제한지역': 'LT_C_UD801',
                // '개발진흥지구': 'LT_C_UD080', // Handled locally
                '복합용도지구': 'LT_C_UD110',
                '입지규제최소구역': 'LT_C_UD061',
                '방재지구': 'LT_C_UD090',
                '자연취락지구': 'LT_C_UQ111'
            };"""

new_typeMap = """            const typeMap = {
                '개발행위허가제한지역': 'LT_C_UD801',
                // '개발진흥지구': 'LT_C_UD080', // Handled locally
                '복합용도지구': 'LT_C_UD110',
                '입지규제최소구역': 'LT_C_UD061',
                '방재지구': 'LT_C_UD090'
                // '취락지구': 'LT_C_UQ111' // Handled locally
            };"""

map_html = map_html.replace(old_typeMap, new_typeMap)

old_dev_logic = """                if (typeName === '개발진흥지구') {
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
                }"""

new_dev_logic = old_dev_logic + """

                if (typeName === '취락지구') {
                    if (!window.settlementLayer) {
                        try {
                            const res = await fetch('/settlement.geojson');
                            const data = await res.json();
                            window.settlementLayer = L.geoJSON(data, {
                                style: {
                                    color: '#0ea5e9',
                                    fillColor: '#0ea5e9',
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
                            console.error('Failed to load 취락지구:', err);
                        }
                    }
                    if (window.settlementLayer) {
                        window.settlementLayer.addTo(layers.dev4);
                    }
                    continue;
                }"""

map_html = map_html.replace(old_dev_logic, new_dev_logic)

with open('public/map.html', 'w', encoding='utf-8') as f:
    f.write(map_html)

print("Updated map.html for settlement layer")
