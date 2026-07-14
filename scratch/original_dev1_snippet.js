2380:                                         dashArray: '3',
2381:                                         fillOpacity: 0.5 // 투명도 50% 이상
2382:                                     };
2383:                                 },
2384:                                 onEachFeature: function (feature, layer) {
2385:                                     const props = feature.properties;
2386:                                     layer.bindTooltip(`<b>노후화 집중 구역</b><br>건축물: ${props.val} / ${props.total_val}개<br>노후화 비율: ${props.ratio_pct}%`, {
2387:                                         sticky: true,
2388:                                         className: 'custom-tooltip'
2389:                                     });
2390:                                 }
2391:                             }).addTo(layers.oldBuildings);
2392:                         } catch (error) {
2393:                             console.error('Error loading old buildings:', error);
2394:                             alert('노후 건축물 데이터를 불러오는 데 실패했습니다.');
2395:                         } finally {
2396:                             if (loadingOverlay) loadingOverlay.style.display = 'none';
2397:                         }
2398:                     }
2399:                 } else {
2400:                     map.removeLayer(layers.oldBuildings);
2401:                     triggerHighlighter();
2402:                 }
2403:             });
2404: 
2405:             document.getElementById('toggle-dev1').addEventListener('change', async (e) => {
2406:                 if (e.target.checked) {
2407:                     map.addLayer(layers.dev1);
2408:                     if (layers.dev1.getLayers().length === 0) {
2409:                         const loadingOverlay = document.getElementById('loading');
2410:                         if (loadingOverlay) loadingOverlay.style.display = 'flex';
2411:                         try {
2412:                             const res = await fetch('/data/taekji.geojson');
2413:                             if (!res.ok) throw new Error('Network response was not ok');
2414:                             const geojsonData = await res.json();
2415:                             
2416:                             L.geoJSON(geojsonData, {
2417:                                 style: function (feature) {
2418:                                     return {
2419:                                         fillColor: '#3b82f6', // 파란색
2420:                                         weight: 2,
2421:                                         opacity: 0.8,
2422:                                         color: '#2563eb',
2423:                                         dashArray: '4',
2424:                                         fillOpacity: 0.2
2425:                                     };
2426:                                 },
2427:                                 onEachFeature: function (feature, layer) {
2428:                                     const props = feature.properties;
2429:                                     layer.bindTooltip(`<b>택지지구</b><br>${props.zoneName || '이름 없음'}`, {
2430:                                         sticky: true,
2431:                                         className: 'custom-tooltip'
2432:                                     });
2433:                                 }
2434:                             }).addTo(layers.dev1);
2435:                         } catch (error) {
2436:                             console.error('Error loading taekji:', error);
2437:                             alert('택지지구 데이터를 불러오는 데 실패했습니다.');
2438:                         } finally {
2439:                             if (loadingOverlay) loadingOverlay.style.display = 'none';
2440:                         }
2441:                     }
2442:                 } else {
2443:                     map.removeLayer(layers.dev1);
2444:                     triggerHighlighter();
2445:                 }
2446:             });
2447: 
2448:             document.getElementById('req-elite-school').addEventListener('change', async (e) => {
2449:                 if (e.target.checked) {
2450:                     map.addLayer(layers.eliteSchools);
2451:                     if (layers.eliteSchools.getLayers().length === 0) {
2452:                         const loadingOverlay = document.getElementById('loading');
2453:                         if (loadingOverlay) loadingOverlay.style.display = 'flex';
2454:                         try {
2455:                             const res = await fetch('/data/elite_school_dongs.geojson');
2456:                             if (!res.ok) throw new Error('Network response was not ok');
2457:                             const geojsonData = await res.json();
2458:                             
2459:                             L.geoJSON(geojsonData, {
2460:                                 style: function (feature) {
2461:                                     return {
2462:                                         fillColor: '#3b82f6', // 파란색
2463:                                         weight: 1.5,
2464:                                         opacity: 0.8,
2465:                                         color: '#2563eb', // 약간 더 진한 파란색
2466:                                         fillOpacity: 0.5 // 투명도 50%
2467:                                     };
2468:                                 },
2469:                                 onEachFeature: function (feature, layer) {
2470:                                     const props = feature.properties;
