
// --- GIS 고도화 기능 ---

// 1. 객체 선택 모드 (Select Object)
let isSelectMode = false;
function toggleSelectMode() {
    isSelectMode = !isSelectMode;
    const btn = document.getElementById('btn-select-object');
    if (isSelectMode) {
        btn.querySelector('i').style.color = 'var(--primary-blue)';
        btn.querySelector('i').style.textShadow = '0 0 10px var(--primary-blue)';
        document.getElementById('map').style.cursor = 'crosshair';
        alert("객체 선택 모드 ON: 지도 상의 마커를 클릭하면 간편 상세 정보가 표시됩니다.");
        
        layers.auction.eachLayer(function(marker) {
            marker.on('click.select', function(e) {
                if(isSelectMode && marker.auctionData) {
                    let d = marker.auctionData;
                    alert([선택된 경공매 객체]\n사건번호: \n종류: \n감정가: 억\n최저가: 억 (%));
                }
            });
        });
    } else {
        btn.querySelector('i').style.color = '';
        btn.querySelector('i').style.textShadow = '';
        document.getElementById('map').style.cursor = '';
        
        layers.auction.eachLayer(function(marker) {
            marker.off('click.select');
        });
    }
}

// 2. 통계 분석 모달 (Statistical Analysis)
function showStatisticsModal() {
    let totalCount = 0;
    let totalAppraised = 0;
    let totalMinPrice = 0;
    let typeCounts = {};
    let currentBounds = map.getBounds();

    layers.auction.eachLayer(function(marker) {
        if (currentBounds.contains(marker.getLatLng())) {
            totalCount++;
            let d = marker.auctionData;
            if(d) {
                let pt = d.property_type || '기타';
                typeCounts[pt] = (typeCounts[pt] || 0) + 1;
                totalAppraised += (d.appraisal_price || 0);
                totalMinPrice += (d.min_price || 0);
            }
        }
    });

    if(totalCount === 0) {
        alert("현재 화면에 표시된 경공매 물건이 없습니다.");
        return;
    }

    let avgAppraised = (totalAppraised / totalCount / 100000000).toFixed(2) + '억 원';
    let avgMinPrice = (totalMinPrice / totalCount / 100000000).toFixed(2) + '억 원';
    let avgRate = ((totalMinPrice / totalAppraised) * 100).toFixed(1) + '%';

    let typeHtml = '';
    for(let t in typeCounts) {
        typeHtml += <div style="display:flex; justify-content:space-between; padding:5px 0; border-bottom:1px solid rgba(255,255,255,0.1);">
            <span></span> <span style="color:var(--neon-blue); font-weight:bold;">건</span>
        </div>;
    }

    let modalHtml = 
        <div id="gis-stat-modal" style="position:fixed; top:50%; left:50%; transform:translate(-50%, -50%); 
            background:rgba(10,12,16,0.95); border:1px solid var(--primary-blue); border-radius:12px; 
            padding:25px; z-index:9999; min-width:320px; box-shadow:0 0 30px rgba(0,238,255,0.2); color:white; font-family: 'Malgun Gothic', sans-serif;">
            
            <h3 style="color: var(--primary-blue); margin-top:0; border-bottom:2px solid var(--primary-blue); padding-bottom:10px;">
                <i class="fa-solid fa-chart-pie"></i> 화면 내 통계 분석
            </h3>
            
            <div style="margin: 20px 0; font-size:1.1rem; line-height: 1.6;">
                <div style="display:flex; justify-content:space-between;"><span>조회 물건 수:</span> <strong>건</strong></div>
                <div style="display:flex; justify-content:space-between;"><span>평균 감정가:</span> <strong></strong></div>
                <div style="display:flex; justify-content:space-between;"><span>평균 최저가:</span> <strong></strong></div>
                <div style="display:flex; justify-content:space-between; color:var(--danger);"><span>가중 평균 최저가율:</span> <strong></strong></div>
            </div>
            
            <h4 style="margin-bottom:10px; color:#aaa;">[용도별 비중]</h4>
            <div style="max-height:150px; overflow-y:auto;">
                
            </div>
            
            <div style="text-align:center; margin-top:25px;">
                <button onclick="document.getElementById('gis-stat-modal').remove()" 
                    style="background:var(--primary-blue); color:#000; border:none; padding:10px 25px; border-radius:8px; font-weight:bold; cursor:pointer;">
                    닫기
                </button>
            </div>
        </div>
    ;

    let existing = document.getElementById('gis-stat-modal');
    if(existing) existing.remove();
    document.body.insertAdjacentHTML('beforeend', modalHtml);
}

// 3. 형광펜 데이터 (Highlighter)
let isHighlighterOn = false;
function toggleHighlighter() {
    isHighlighterOn = !isHighlighterOn;
    const btn = document.getElementById('btn-highlighter');
    if (isHighlighterOn) {
        btn.querySelector('i').style.color = '#bd00ff'; // neon-purple
        btn.querySelector('i').style.textShadow = '0 0 15px #bd00ff';
        
        let highlightCount = 0;
        layers.auction.eachLayer(function(marker) {
            let d = marker.auctionData;
            // Backup original style
            marker.originalStyle = {
                radius: marker.options.radius,
                color: marker.options.color,
                fillColor: marker.options.fillColor,
                weight: marker.options.weight,
                opacity: marker.options.opacity,
                fillOpacity: marker.options.fillOpacity
            };
            
            if(d && d.min_bid_rate <= 50) {
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
        alert(형광펜 ON: 반값 경매(최저가율 50% 이하) 물건 건이 집중 강조됩니다.);
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
