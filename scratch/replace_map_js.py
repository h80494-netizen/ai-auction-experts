import os

file_path = 'public/map.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Normalize line endings
content = content.replace('\r\n', '\n')

# 1. Replacement of applyHighlighter
old_highlighter = """        function applyHighlighter() {
            const btnHighlighter = document.getElementById('btn-highlighter');
            const countEl = document.getElementById('highlight-count');
            highlightedCaseNos = [];

            if (!btnHighlighter || !btnHighlighter.classList.contains('active')) {
                layers.auction.eachLayer(marker => {
                    marker.setStyle({
                        radius: 6, color: '#fff', weight: 2, fillColor: marker.typeColor, fillOpacity: 1
                    });
                });
                if (countEl) countEl.style.display = 'none';
                return;
            }

            const activeFilterIds = [
                { id: 'toggle-subways', layer: layers.subway },
                { id: 'toggle-univs', layer: layers.univ },
                { id: 'toggle-inds', layer: layers.ind },
                { id: 'toggle-middles', layer: layers.middle },
                { id: 'toggle-commercial', layer: layers.commercial },
                { id: 'toggle-hagwons', layer: layers.hagwon },
                { id: 'toggle-dev1', layer: layers.dev1 },
                { id: 'toggle-dev2', layer: layers.dev2 },
                { id: 'toggle-old-buildings', layer: layers.oldBuildings }
            ];
            
            const activeLayers = [];
            activeFilterIds.forEach(f => {
                const el = document.getElementById(f.id);
                if (el && el.checked) {
                    activeLayers.push(f.layer);
                }
            });

            if (activeLayers.length === 0) {
                layers.auction.eachLayer(marker => {
                    marker.setStyle({
                        radius: 6, color: '#fff', weight: 2, fillColor: marker.typeColor, fillOpacity: 1
                    });
                });
                return;
            }

            layers.auction.eachLayer(marker => {
                const latlng = marker.getLatLng();
                const pt = window.turf ? turf.point([latlng.lng, latlng.lat]) : null;
                let isInside = true;

                for (let i = 0; i < activeLayers.length; i++) {
                    if (!checkPointInLayerGroup(pt, activeLayers[i], latlng)) {
                        isInside = false;
                        break;
                    }
                }

                if (isInside) {
                    marker.setStyle({
                        radius: 10, color: '#c026d3', weight: 4, fillColor: marker.typeColor, fillOpacity: 1
                    });
                    if (marker.bringToFront) marker.bringToFront();
                    highlightedCaseNos.push(marker.auctionData.case_no);
                } else {
                    marker.setStyle({
                        radius: 4, color: '#94a3b8', weight: 1, fillColor: marker.typeColor, fillOpacity: 0.3
                    });
                }
            });

            if (countEl) {
                if (activeLayers.length > 0) {
                    countEl.innerText = `${highlightedCaseNos.length}건 중첩`;
                    countEl.style.display = 'inline-block';
                } else {
                    countEl.style.display = 'none';
                }
            }
        }"""

new_highlighter = """        let highlightedAuctions = [];

        function applyHighlighter() {
            const btnHighlighter = document.getElementById('btn-highlighter');
            const countEl = document.getElementById('highlight-count');
            const analysisBtn = document.getElementById('btn-show-analysis');
            highlightedCaseNos = [];
            highlightedAuctions = [];

            if (!btnHighlighter || !btnHighlighter.classList.contains('active')) {
                layers.auction.eachLayer(marker => {
                    marker.setStyle({
                        radius: 6, color: '#fff', weight: 2, fillColor: marker.typeColor, fillOpacity: 1
                    });
                });
                if (countEl) countEl.style.display = 'none';
                if (analysisBtn) analysisBtn.style.display = 'none';
                return;
            }

            const activeFilterIds = [
                { id: 'toggle-subways', layer: layers.subway, name: '지하철역' },
                { id: 'toggle-univs', layer: layers.univ, name: '대학교' },
                { id: 'toggle-inds', layer: layers.ind, name: '산업단지' },
                { id: 'toggle-middles', layer: layers.middle, name: '학군(중학교)' },
                { id: 'toggle-commercial', layer: layers.commercial, name: '상권' },
                { id: 'toggle-hagwons', layer: layers.hagwon, name: '학원가' },
                { id: 'toggle-dev1', layer: layers.dev1, name: '택지지구' },
                { id: 'toggle-dev2', layer: layers.dev2, name: '지구단위계획구역' },
                { id: 'toggle-dev3', layer: layers.dev3, name: '재개발/재건축구역' },
                { id: 'toggle-zoning', layer: layers.zoning, name: '용도지역' },
                { id: 'toggle-planning-road', layer: layers.planningRoad, name: '도시계획도로' },
                { id: 'toggle-old-buildings', layer: layers.oldBuildings, name: '노후건물' }
            ];

            const activeLayers = [];
            activeFilterIds.forEach(f => {
                const el = document.getElementById(f.id);
                if (el && el.checked) {
                    activeLayers.push(f);
                }
            });

            if (activeLayers.length === 0) {
                layers.auction.eachLayer(marker => {
                    marker.setStyle({
                        radius: 6, color: '#fff', weight: 2, fillColor: marker.typeColor, fillOpacity: 1
                    });
                });
                if (countEl) countEl.style.display = 'none';
                if (analysisBtn) analysisBtn.style.display = 'none';
                return;
            }

            layers.auction.eachLayer(marker => {
                const latlng = marker.getLatLng();
                const pt = window.turf ? turf.point([latlng.lng, latlng.lat]) : null;

                let matchCount = 0;
                let matchedNames = [];

                activeLayers.forEach(al => {
                    if (checkPointInLayerGroup(pt, al.layer, latlng)) {
                        matchCount++;
                        matchedNames.push(al.name);
                    }
                });

                const isInside = (matchCount > 0);

                if (isInside) {
                    marker.setStyle({
                        radius: 10, color: '#c026d3', weight: 4, fillColor: marker.typeColor, fillOpacity: 1
                    });
                    if (marker.bringToFront) marker.bringToFront();
                    highlightedCaseNos.push(marker.auctionData.case_no);

                    highlightedAuctions.push({
                        case_no: marker.auctionData.case_no,
                        address: marker.auctionData.address,
                        property_type: marker.auctionData.property_type,
                        appraisal_price: marker.auctionData.appraisal_price,
                        min_price: marker.auctionData.min_price,
                        special_notes: marker.auctionData.special_notes || '',
                        overlap_count: matchCount,
                        matched_layers: matchedNames,
                        min_bid_rate: marker.auctionData.min_bid_rate || 100,
                        lat: latlng.lat,
                        lng: latlng.lng
                    });
                } else {
                    marker.setStyle({
                        radius: 4, color: '#94a3b8', weight: 1, fillColor: marker.typeColor, fillOpacity: 0.3
                    });
                }
            });

            if (countEl) {
                if (activeLayers.length > 0) {
                    countEl.innerText = `${highlightedCaseNos.length}건 중첩`;
                    countEl.style.display = 'inline-block';
                    if (highlightedCaseNos.length >= 3) {
                        countEl.style.cursor = 'pointer';
                        countEl.title = '클릭하여 중첩 분석 보고서 보기';
                    } else {
                        countEl.style.cursor = 'default';
                        countEl.title = '';
                    }
                } else {
                    countEl.style.display = 'none';
                }
            }

            if (analysisBtn) {
                if (highlightedCaseNos.length >= 3) {
                    analysisBtn.style.display = 'inline-block';
                } else {
                    analysisBtn.style.display = 'none';
                }
            }
        }

        function openAnalysisScreen() {
            if (highlightedAuctions && highlightedAuctions.length >= 3) {
                localStorage.setItem('highlighted_auctions', JSON.stringify(highlightedAuctions));
                window.open('analysis.html', '_blank');
            } else {
                alert('중첩 개수가 3개 이상일 때만 분석 보고서를 열 수 있습니다.');
            }
        }"""

content = content.replace(old_highlighter, new_highlighter)

# 2. Replacement of fetchInfraData
old_infra = """        async function fetchInfraData() {
            if (map.getZoom() < minZoomRequired) return;
            const bounds = map.getBounds();
            const checkedRegions = Array.from(document.querySelectorAll('.region-checkbox:checked')).map(cb => cb.value);
            let url = `/api/map/pois?min_lat=${bounds.getSouth()}&max_lat=${bounds.getNorth()}&min_lng=${bounds.getWest()}&max_lng=${bounds.getEast()}`;
            if (checkedRegions.length > 0) url += `&regions=${checkedRegions.join(',')}`;
            
            try {
                const res = await fetch(url);
                const json = await res.json();

                if (json.status === 'success') {
                    const data = json.data;

                    if (data.subways && document.getElementById('toggle-subways').checked) {
                        layers.subway.clearLayers();
                        data.subways.forEach(s => {
                            let radius = parseInt(document.getElementById('buffer-subways').value) || 500;
                            let color = getGlobalLineColor(s.line);
                            L.circle([s.lat, s.lng], { color: color, fillColor: color, fillOpacity: 0.1, radius: radius, weight: 1, dashArray: '4, 4' }).addTo(layers.subway);
                            createDotMarker(s.lat, s.lng, color, `<b>${s.name}</b><br>${s.line}`)
                                .addTo(layers.subway);
                        });
                    }

                    if (data.universities && document.getElementById('toggle-univs').checked) {
                        layers.univ.clearLayers();
                        data.universities.forEach(u => {
                            let radius = parseInt(document.getElementById('buffer-univs').value) || 500;
                            L.circle([u.lat, u.lng], { color: '#3b82f6', fillColor: '#3b82f6', fillOpacity: 0.1, radius: radius, weight: 1, dashArray: '4, 4' }).addTo(layers.univ);
                            createDotMarker(u.lat, u.lng, '#3b82f6', `<b>${u.name}</b><br>대학교`).addTo(layers.univ);
                        });
                    }

                    if (data.industrial_complexes && document.getElementById('toggle-inds').checked) {
                        layers.ind.clearLayers();
                        data.industrial_complexes.forEach(i => {
                            let radius = parseInt(document.getElementById('buffer-inds').value) || 500;
                            L.circle([i.lat, i.lng], { color: '#f59e0b', fillColor: '#f59e0b', fillOpacity: 0.1, radius: radius, weight: 1, dashArray: '4, 4' }).addTo(layers.ind);
                            createDotMarker(i.lat, i.lng, '#f59e0b', `<b>${i.name}</b><br>산업단지`).addTo(layers.ind);
                        });
                    }

                    if (data.middle_schools && document.getElementById('toggle-middles') && document.getElementById('toggle-middles').checked) {
                        layers.middle.clearLayers();
                        data.middle_schools.forEach(m => {
                            let color = '#94a3b8';
                            let label = `특목고 진학률 ${parseFloat(m.special_hs_rate).toFixed(1)}%`;
                            let markerRadius = 4;
                            if (m.special_hs_rate >= 10) {
                                color = '#f43f5e';
                                markerRadius = 6;
                                let radius = parseInt(document.getElementById('buffer-middles').value) || 500;
                                L.circle([m.lat, m.lng], { color: '#f43f5e', fillColor: '#f43f5e', fillOpacity: 0.1, radius: radius, weight: 1, dashArray: '4, 4' }).addTo(layers.middle);
                            }
                            createDotMarker(m.lat, m.lng, color, `<b>${m.name}</b><br>${label}`, markerRadius).addTo(layers.middle);
                        });
                    }
                    
                    if (document.getElementById('toggle-bus').checked && map.getZoom() >= minZoomRequired && data.bus_stops) {
                        layers.bus.clearLayers();
                        let radius = parseInt(document.getElementById('buffer-bus').value) || 20;
                        data.bus_stops.forEach(b => {
                            L.circle([b.lat, b.lng], { color: '#0ea5e9', fillColor: '#0ea5e9', fillOpacity: 0.1, radius: radius, weight: 1, dashArray: '4, 4' }).addTo(layers.bus);
                            createDotMarker(b.lat, b.lng, '#0ea5e9', `<b>${b.name}</b><br>버스 (${b.city})`, 3).addTo(layers.bus);
                        });
                    }
                    if (document.getElementById('toggle-commercial').checked && data.commercial_areas) {
                        
                        // 인구수 배열 생성 및 정렬 (백분위 계산용)
                        const pops = data.commercial_areas.map(c => c.population || 0).sort((a, b) => a - b);
                        
                        // ?곴텒 ?대쫫(name)蹂??멸뎄??留ㅽ븨
                        const popData = {};
                        data.commercial_areas.forEach(c => {
                            popData[c.name] = c.population || 0;
                        });

                        const getTierStyle = (pop) => {
                            if (pop === 0 || pops.length === 0) return null;
                            
                            // ?댁쭊 ?먯깋 ?€??媛꾨떒???꾩튂 李얘린 (?곗씠?곌? 留롮? ?딆쑝誘€濡?
                            const idx = pops.findIndex(p => p >= pop);
                            const percentile = (idx + 1) / pops.length;
                            const tier = Math.ceil(percentile * 10) || 1; // 1 ~ 10 단계
                            
                            if (tier <= 6) return null;
                            
                            const colors = {
                                10: '#08306b', 9: '#08519c', 8: '#2171b5', 7: '#4292c6'
                            };
                            
                            return {
                                color: colors[tier] || '#ffffff',
                                fillColor: colors[tier] || '#ffffff',
                                fillOpacity: 0.5,
                                weight: 0
                            };
                        };

                        if (!window.commercialGeoJsonData) {
                            try {
                                const res = await fetch('/data/seoul_commercial.geojson');
                                window.commercialGeoJsonData = await res.json();
                            } catch (err) {
                                console.error('Failed to load commercial geojson:', err);
                            }
                        }

                        if (window.commercialGeoJsonData) {
                            layers.commercial.clearLayers();
                            const geoJsonLayer = L.geoJSON(window.commercialGeoJsonData, {
                                filter: function(feature) {
                                    const name = feature.properties.TRDAR_CD_N;
                                    const pop = popData[name] || 0;
                                    const style = getTierStyle(pop);
                                    return style !== null;
                                },
                                style: function(feature) {
                                    const name = feature.properties.TRDAR_CD_N;
                                    const pop = popData[name] || 0;
                                    return getTierStyle(pop);
                                },
                                onEachFeature: function(feature, layer) {
                                    const name = feature.properties.TRDAR_CD_N;
                                    const pop = popData[name] || 0;
                                    let popStr = pop > 0 ? (pop / 10000).toFixed(0) + '만 명' : '데이터 없음';
                                    layer.bindTooltip(`<b>${name}</b><br>상권<br>유동인구: ${popStr}`, {
                                        sticky: true,
                                        className: 'custom-tooltip'
                                    });
                                }
                            });
                            geoJsonLayer.addTo(layers.commercial);
                        }
                    }
                }
            } catch (err) { console.error(err); } finally { triggerHighlighter(); }
        }"""

new_infra = """        let cachedInfraBounds = null;
        let cachedInfraZoom = null;
        let cachedInfraTogglesKey = "";

        function getInfraTogglesKey() {
            return [
                document.getElementById('toggle-subways').checked,
                document.getElementById('toggle-univs').checked,
                document.getElementById('toggle-inds').checked,
                document.getElementById('toggle-middles')?.checked || false,
                document.getElementById('toggle-bus')?.checked || false,
                document.getElementById('toggle-commercial')?.checked || false,
                document.getElementById('buffer-subways')?.value || '',
                document.getElementById('buffer-univs')?.value || '',
                document.getElementById('buffer-inds')?.value || '',
                document.getElementById('buffer-middles')?.value || '',
                document.getElementById('buffer-bus')?.value || '',
                document.getElementById('buffer-commercial')?.value || ''
            ].join('_');
        }

        async function fetchInfraData() {
            if (map.getZoom() < minZoomRequired) return;

            let activeTypes = [];
            if (document.getElementById('toggle-subways').checked) activeTypes.push('subways');
            if (document.getElementById('toggle-univs').checked) activeTypes.push('universities');
            if (document.getElementById('toggle-inds').checked) activeTypes.push('industrial_complexes');
            if (document.getElementById('toggle-middles')?.checked) activeTypes.push('middle_schools');
            if (document.getElementById('toggle-bus')?.checked) activeTypes.push('bus_stops');
            if (document.getElementById('toggle-commercial')?.checked) activeTypes.push('commercial_areas');

            if (activeTypes.length === 0) {
                layers.subway.clearLayers();
                layers.univ.clearLayers();
                layers.ind.clearLayers();
                layers.middle.clearLayers();
                layers.bus.clearLayers();
                layers.commercial.clearLayers();
                cachedInfraBounds = null;
                cachedInfraZoom = null;
                cachedInfraTogglesKey = "";
                triggerHighlighter();
                return;
            }

            const currentZoom = map.getZoom();
            const currentTogglesKey = getInfraTogglesKey();
            const bounds = map.getBounds();

            if (cachedInfraZoom === currentZoom && 
                cachedInfraTogglesKey === currentTogglesKey && 
                cachedInfraBounds && 
                cachedInfraBounds.contains(bounds)) {
                return;
            }

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

            cachedInfraBounds = paddedBounds;
            cachedInfraZoom = currentZoom;
            cachedInfraTogglesKey = currentTogglesKey;

            const checkedRegions = Array.from(document.querySelectorAll('.region-checkbox:checked')).map(cb => cb.value);
            let url = `/api/map/pois?min_lat=${paddedBounds.getSouth()}&max_lat=${paddedBounds.getNorth()}&min_lng=${paddedBounds.getWest()}&max_lng=${paddedBounds.getEast()}`;
            if (checkedRegions.length > 0) url += `&regions=${checkedRegions.join(',')}`;
            url += `&types=${activeTypes.join(',')}`;

            try {
                const res = await fetch(url);
                const json = await res.json();

                if (json.status === 'success') {
                    const data = json.data;

                    if (!activeTypes.includes('subways')) layers.subway.clearLayers();
                    if (!activeTypes.includes('universities')) layers.univ.clearLayers();
                    if (!activeTypes.includes('industrial_complexes')) layers.ind.clearLayers();
                    if (!activeTypes.includes('middle_schools')) layers.middle.clearLayers();
                    if (!activeTypes.includes('bus_stops')) layers.bus.clearLayers();
                    if (!activeTypes.includes('commercial_areas')) layers.commercial.clearLayers();

                    if (data.subways && document.getElementById('toggle-subways').checked) {
                        layers.subway.clearLayers();
                        data.subways.forEach(s => {
                            let radius = parseInt(document.getElementById('buffer-subways').value) || 500;
                            let color = getGlobalLineColor(s.line);
                            L.circle([s.lat, s.lng], { color: color, fillColor: color, fillOpacity: 0.1, radius: radius, weight: 1, dashArray: '4, 4' }).addTo(layers.subway);
                            createDotMarker(s.lat, s.lng, color, `<b>${s.name}</b><br>${s.line}`).addTo(layers.subway);
                        });
                    }

                    if (data.universities && document.getElementById('toggle-univs').checked) {
                        layers.univ.clearLayers();
                        data.universities.forEach(u => {
                            let radius = parseInt(document.getElementById('buffer-univs').value) || 500;
                            L.circle([u.lat, u.lng], { color: '#3b82f6', fillColor: '#3b82f6', fillOpacity: 0.1, radius: radius, weight: 1, dashArray: '4, 4' }).addTo(layers.univ);
                            createDotMarker(u.lat, u.lng, '#3b82f6', `<b>${u.name}</b><br>대학교`).addTo(layers.univ);
                        });
                    }

                    if (data.industrial_complexes && document.getElementById('toggle-inds').checked) {
                        layers.ind.clearLayers();
                        data.industrial_complexes.forEach(i => {
                            let radius = parseInt(document.getElementById('buffer-inds').value) || 500;
                            L.circle([i.lat, i.lng], { color: '#f59e0b', fillColor: '#f59e0b', fillOpacity: 0.1, radius: radius, weight: 1, dashArray: '4, 4' }).addTo(layers.ind);
                            createDotMarker(i.lat, i.lng, '#f59e0b', `<b>${i.name}</b><br>산업단지`).addTo(layers.ind);
                        });
                    }

                    if (data.middle_schools && document.getElementById('toggle-middles') && document.getElementById('toggle-middles').checked) {
                        layers.middle.clearLayers();
                        data.middle_schools.forEach(m => {
                            let color = '#94a3b8';
                            let label = `특목고 진학률 ${parseFloat(m.special_hs_rate).toFixed(1)}%`;
                            let markerRadius = 4;
                            if (m.special_hs_rate >= 10) {
                                color = '#f43f5e';
                                markerRadius = 6;
                                let radius = parseInt(document.getElementById('buffer-middles').value) || 500;
                                L.circle([m.lat, m.lng], { color: '#f43f5e', fillColor: '#f43f5e', fillOpacity: 0.1, radius: radius, weight: 1, dashArray: '4, 4' }).addTo(layers.middle);
                            }
                            createDotMarker(m.lat, m.lng, color, `<b>${m.name}</b><br>${label}`, markerRadius).addTo(layers.middle);
                        });
                    }
                    
                    if (document.getElementById('toggle-bus') && document.getElementById('toggle-bus').checked && map.getZoom() >= minZoomRequired && data.bus_stops) {
                        layers.bus.clearLayers();
                        let radius = parseInt(document.getElementById('buffer-bus').value) || 20;
                        data.bus_stops.forEach(b => {
                            L.circle([b.lat, b.lng], { color: '#0ea5e9', fillColor: '#0ea5e9', fillOpacity: 0.1, radius: radius, weight: 1, dashArray: '4, 4' }).addTo(layers.bus);
                            createDotMarker(b.lat, b.lng, '#0ea5e9', `<b>${b.name}</b>`, 3).addTo(layers.bus);
                        });
                    }
                    if (document.getElementById('toggle-commercial').checked && data.commercial_areas) {
                        const pops = data.commercial_areas.map(c => c.population || 0).sort((a, b) => a - b);
                        const popData = {};
                        data.commercial_areas.forEach(c => {
                            popData[c.name] = c.population || 0;
                        });

                        const getTierStyle = (pop) => {
                            if (pop === 0 || pops.length === 0) return null;
                            const idx = pops.findIndex(p => p >= pop);
                            const percentile = (idx + 1) / pops.length;
                            const tier = Math.ceil(percentile * 10) || 1;
                            if (tier <= 6) return null;
                            const colors = { 10: '#08306b', 9: '#08519c', 8: '#2171b5', 7: '#4292c6' };
                            return { color: colors[tier] || '#ffffff', fillColor: colors[tier] || '#ffffff', fillOpacity: 0.5, weight: 0 };
                        };

                        if (!window.commercialGeoJsonData) {
                            try {
                                const res = await fetch('/data/seoul_commercial.geojson');
                                window.commercialGeoJsonData = await res.json();
                            } catch (err) {
                                console.error('Failed to load commercial geojson:', err);
                            }
                        }

                        if (window.commercialGeoJsonData) {
                            layers.commercial.clearLayers();
                            const geoJsonLayer = L.geoJSON(window.commercialGeoJsonData, {
                                filter: function(feature) {
                                    const name = feature.properties.TRDAR_CD_N;
                                    const pop = popData[name] || 0;
                                    return getTierStyle(pop) !== null;
                                },
                                style: function(feature) {
                                    const name = feature.properties.TRDAR_CD_N;
                                    const pop = popData[name] || 0;
                                    return getTierStyle(pop);
                                },
                                onEachFeature: function(feature, layer) {
                                    const name = feature.properties.TRDAR_CD_N;
                                    const pop = popData[name] || 0;
                                    let popStr = pop > 0 ? (pop / 10000).toFixed(0) + '만 명' : '데이터 없음';
                                    layer.bindTooltip(`<b>${name}</b><br>상권<br>유동인구: ${popStr}`, { sticky: true, className: 'custom-tooltip' });
                                }
                            });
                            geoJsonLayer.addTo(layers.commercial);
                        }
                    }
                }
            } catch (err) { console.error(err); } finally { triggerHighlighter(); }
        }"""

content = content.replace(old_infra, new_infra)

print("SUCCESS: applyHighlighter and fetchInfraData replacement completed")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Saved map.html")
