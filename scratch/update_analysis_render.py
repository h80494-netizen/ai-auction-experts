import os

html_path = r"c:\Users\llll\Documents\두인경매\바이브코딩\public\analysis.html"
with open(html_path, "r", encoding="utf-8") as f:
    content = f.read()

target_start = "if (auctions.length > 0) {"
target_end = """        .catch(err => {
            console.error(err);
            document.getElementById('ai-report-content').innerHTML = `<div style="color: #ef4444; padding: 10px;">⚠️ AI 분석 요청 중 오류가 발생했습니다.</div>`;
        });"""

replacement = """if (auctions.length > 0) {
        // Calculate recommendation score for each item
        auctions.forEach(item => {
            item.score = calculateRecommendationScore(item);
        });

        // Sort by score DESC
        auctions.sort((a, b) => b.score - a.score);

        // Core rendering function
        function renderBestCardsAndTable(itemsList) {
            document.getElementById('stat-total').innerText = itemsList.length;
            const maxOverlap = Math.max(...itemsList.map(a => a.overlap_count || 0), 0);
            document.getElementById('stat-max-overlap').innerText = maxOverlap;
            document.getElementById('stat-best').innerText = Math.min(itemsList.length, 3);

            const best3 = itemsList.slice(0, 3);
            const bestContainer = document.getElementById('best-cards-container');
            bestContainer.innerHTML = '';
            
            best3.forEach((item, index) => {
                const matchedLayers = item.matched_layers || [];
                const matchedLayersStr = matchedLayers.join(', ');
                
                // 1. Differentiated Value/Development analysis
                let valueAnalysis = "";
                const subwayDist = item.subway_dist !== undefined ? Math.round(item.subway_dist) : null;
                const subwayStr = (subwayDist !== null && subwayDist !== 0) ? `지하철역과의 거리가 약 ${subwayDist}m로 매우 인접한 역세권 수혜를 받으며` : "대중교통 접근성이 우수하고 양호한 보행권 내에 위치하며";
                
                let devDetails = [];
                if (matchedLayers.some(l => l.includes('재개발') || l.includes('재건축') || l.includes('정비'))) {
                    devDetails.push("정비사업지구 추진 호재와 직결되어 인근 노후 지역의 정비 및 현대화에 따른 프리미엄 지가 상승 여력이 대단히 강력합니다.");
                }
                if (matchedLayers.some(l => l.includes('택지'))) {
                    devDetails.push("택지개발지구에 정밀 연접하여 대규모 공공 주거지 조성에 따른 도로 확장, 신축 배후 단지 등 신흥 주거 벨트 형성의 가치 상승 혜택을 선점합니다.");
                }
                if (matchedLayers.some(l => l.includes('지구단위'))) {
                    devDetails.push("지구단위계획 수혜 권역으로 지정되어 상업/업무 기능 확충이나 건축 기준 완화 인센티브를 부여받아 체계적인 주변 인프라 고도화 혜택을 입게 됩니다.");
                }
                if (matchedLayers.some(l => l.includes('도로') || l.includes('노선') || l.includes('계획선'))) {
                    devDetails.push("도시계획도로 신설 및 진입로 연결 호재선에 걸쳐 차량 및 보행자 접근성이 획기적으로 향상되는 지가 상승 트리거를 갖췄습니다.");
                }
                
                if (devDetails.length > 0) {
                    valueAnalysis = `본 물건은 <strong>${matchedLayersStr}</strong> 권역 내에 위치하고 있습니다. ${subwayStr}, ${devDetails.join(' ')}`;
                } else {
                    valueAnalysis = `본 물건은 ${subwayStr}, 기본 배후 임대수요 및 정주 생활권 인프라가 견고하게 유지되는 지점입니다. 하방 경직성이 강력하여 시세 하락 리스크가 매우 낮고 중장기 지가 안정이 확실시됩니다.`;
                }

                // 2. Differentiated Claims/Takeover Risk analysis (선순위 인수금액 정밀 분석)
                let claimsAnalysis = "";
                const notes = (item.special_notes || "").toLowerCase();
                
                if (notes.includes('선순위임차') || notes.includes('대항력') || notes.includes('임차')) {
                    claimsAnalysis = `<strong>[주의: 선순위 임차 리스크]</strong> 특별권리사항에 대항력 있는 선순위 임차인이 포착되었습니다. 대항력 보증금 중 미배당금은 낙찰자가 전액 부담해야 하므로, 보증금 액수 및 확정일자/배당요구를 면밀히 확인해야 하며 최종 인수예상금액의 차감이 필수적입니다.`;
                } else if (notes.includes('유치권')) {
                    claimsAnalysis = `<strong>[주의: 유치권 접수 필지]</strong> 유치권 신고서가 제출되어 실질 점유 유무 및 피담보채권 성립 여부에 따른 사후 인도명령 거부, 소송 해결 비용 등의 추가 비용 리스크 인수가 발생할 우려가 높은 특수 물건입니다.`;
                } else if (notes.includes('지상권')) {
                    claimsAnalysis = `<strong>[주의: 법정지상권 우려]</strong> 건물 단독 매각 또는 제시외 건물 등으로 인해 토지 임료(지료) 징수 분쟁이나 토지 인도 소송 등의 사후 출구 전략 비용 인수 부담이 우려되는 필지입니다.`;
                } else if (notes.includes('위반')) {
                    claimsAnalysis = `<strong>[행정처분: 위반건축물]</strong> 건축물대장상 위반 명세에 따른 연간 이행강제금 납부의 승계 또는 위반부위 원상복구 공사비 인수가 수반되므로, 해당 감안액을 투찰 마진에서 차감 설계해야 합니다.`;
                } else {
                    claimsAnalysis = `<strong>[인수 리스크 없음: 깨끗한 권리]</strong> 특별권리사항에 선순위 임차인, 유치권, 전세권 등 낙찰 이외에 매수인이 추가로 변제하거나 안아야 할 선순위 인수금액 부담이 일체 존재하지 않는 안전한 물건입니다. 추가 인수금액은 <strong>0원</strong>입니다.`;
                }

                // 3. Differentiated Uncertainty analysis
                let uncertaintyAnalysis = "";
                if (notes.includes('유치권') || notes.includes('지상권') || notes.includes('임차')) {
                    uncertaintyAnalysis = `특수 권리 및 점유 상황에 따른 권리 관계의 복잡성으로 인해 통상적인 인도 절차보다 명도 난이도가 높으며, 인도명령 집행 또는 합의에 최소 3~6개월의 시일이 예상되므로 적정 금융비용을 입찰가에 미리 선반영해야 합니다.`;
                } else {
                    uncertaintyAnalysis = `잔금 납부와 동시에 등기부본상 하자가 일체 말소되는 완전 소멸주의 물건입니다. 점유자는 대항력 없는 인도명령 대상자로만 구성되어 통상적인 이사 조율이나 신속한 인도결정을 통해 최단기 명도 완료가 보장됩니다.`;
                }

                const card = document.createElement('div');
                card.className = 'best-card';
                card.style.cursor = 'pointer';
                card.onclick = () => openCaseInDashboard(item.case_no);
                
                const appraisalPrice = item.appraisal_price || item.appraised_value || 0;
                const minBidPrice = item.min_price || item.minimum_value || 0;
                
                card.innerHTML = `
                    <div>
                        <span class="rank-badge rank-${index + 1}">
                            <i class="fa-solid fa-crown"></i> BEST ${index + 1}
                        </span>
                        <div class="card-header" style="margin-top: 10px;">
                            <div class="case-number">${item.case_no}</div>
                            <span class="property-type-badge">${item.property_type}</span>
                            <div class="address" title="${item.address}">${item.address}</div>
                        </div>

                        <div class="price-section">
                            <div class="price-row">
                                <span class="price-lbl">감정가</span>
                                <span class="price-val">${formatPrice(appraisalPrice)}</span>
                            </div>
                            <div class="price-row">
                                <span class="price-lbl">최저가</span>
                                <span class="price-val min-price">${formatPrice(minBidPrice)}</span>
                            </div>
                            ${item.min_price_per_pyeong ? `
                            <div class="price-row" style="margin-top: 4px; font-size: 0.72rem; color: var(--text-muted);">
                                <span>평당 최저가</span>
                                <span>${item.min_price_per_pyeong.toLocaleString()} 원/평</span>
                            </div>
                            ` : ''}
                        </div>

                        <div class="overlap-indicator">
                            <div class="overlap-count-circle">${item.score}점</div>
                            <div class="overlap-text">
                                <div>추천 지수: <strong>${item.score}점</strong> (중첩 ${item.overlap_count}개)</div>
                                <div style="font-size: 0.68rem; color: var(--text-muted); display: flex; align-items: center; gap: 4px;">
                                    등급: ${renderStars(item.score)}
                                </div>
                            </div>
                        </div>

                        <div class="matched-badges">
                            ${(item.matched_layers || []).map(layer => `<span class="matched-badge">${layer}</span>`).join('')}
                        </div>
                    </div>

                    <div class="analysis-section">
                        <div class="analysis-item">
                            <div class="analysis-title">
                                <i class="fa-solid fa-arrow-up-right-dots"></i> 개발 가치 및 상승 잠재력
                            </div>
                            <div class="analysis-desc">${valueAnalysis}</div>
                        </div>
                        <div class="analysis-item">
                            <div class="analysis-title">
                                <i class="fa-solid fa-shield-halved"></i> 인수액 리스크 (선순위 분석)
                            </div>
                            <div class="analysis-desc">${claimsAnalysis}</div>
                        </div>
                        <div class="analysis-item">
                            <div class="analysis-title">
                                <i class="fa-solid fa-circle-check"></i> 권리 투명성 및 불확실성
                            </div>
                            <div class="analysis-desc">${uncertaintyAnalysis}</div>
                        </div>
                    </div>
                `;
                bestContainer.appendChild(card);
            });

            // Render entire table
            const tableBody = document.getElementById('table-body');
            tableBody.innerHTML = '';

            itemsList.forEach(item => {
                const tr = document.createElement('tr');
                tr.style.cursor = 'pointer';
                tr.onclick = () => openCaseInDashboard(item.case_no);
                
                const appraisalPrice = item.appraisal_price || item.appraised_value || 0;
                const minBidPrice = item.min_price || item.minimum_value || 0;
                const matchedLayersList = item.matched_layers || [];

                tr.innerHTML = `
                    <td class="case-cell">${item.case_no}</td>
                    <td><span class="property-type-badge" style="margin-bottom:0;">${item.property_type}</span></td>
                    <td style="font-size: 0.78rem; font-weight: 500;">${item.address}</td>
                    <td class="badges-cell">
                        <div style="display:flex; flex-wrap:wrap; gap:3px;">
                            ${matchedLayersList.map(layer => `<span class="matched-badge" style="font-size:0.65rem; padding: 1px 4px; border-radius:4px;">${layer}</span>`).join('')}
                        </div>
                    </td>
                    <td style="text-align: center; font-weight: 800; font-family:'Outfit',sans-serif; color:var(--text-highlight); font-size: 0.95rem;">${item.overlap_count}개</td>
                    <td style="text-align: center; font-size: 0.8rem;">
                        ${renderStars(item.score)}
                        <div style="font-size: 0.7rem; color: var(--text-muted); margin-top: 2px;">${item.score}점</div>
                    </td>
                    <td class="price-cell">${formatPrice(appraisalPrice)}</td>
                    <td class="price-cell min">${formatPrice(minBidPrice)}</td>
                `;
                tableBody.appendChild(tr);
            });
        }

        // Run initial render with localStorage local data
        renderBestCardsAndTable(auctions);

        // Build payload data for backend
        const caseNos = auctions.map(a => a.case_no);
        const scores = {};
        const overlapCounts = {};
        const matchedLayers = {};
        auctions.forEach(item => {
            scores[item.case_no] = item.score;
            overlapCounts[item.case_no] = item.overlap_count;
            matchedLayers[item.case_no] = item.matched_layers;
        });

        // Fetch AI Overlap Report using sorted case_nos and helper dicts
        fetch('/api/map/overlap_analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                case_nos: caseNos,
                scores: scores,
                overlap_counts: overlapCounts,
                matched_layers: matchedLayers
            })
        })
        .then(res => res.json())
        .then(data => {
            const reportContentEl = document.getElementById('ai-report-content');
            if (data.status === 'success') {
                // Re-render cards and table with full DB data from server
                if (data.items && data.items.length > 0) {
                    data.items.forEach(srvItem => {
                        const localItem = auctions.find(a => a.case_no === srvItem.case_no);
                        if (localItem) {
                            srvItem.score = localItem.score;
                            srvItem.overlap_count = localItem.overlap_count;
                            srvItem.matched_layers = localItem.matched_layers;
                        }
                    });
                    data.items.sort((a, b) => (b.score || 0) - (a.score || 0));
                    renderBestCardsAndTable(data.items);
                }

                if (window.marked && typeof window.marked.parse === 'function') {
                    reportContentEl.innerHTML = window.marked.parse(data.report);
                } else {
                    reportContentEl.innerHTML = `<pre style="white-space: pre-wrap; font-family: inherit; color: var(--text-main); font-size: 0.85rem;">${data.report}</pre>`;
                }
            } else {
                reportContentEl.innerHTML = `<div style="color: #ef4444; padding: 10px;">⚠️ AI 분석 호출 실패: ${data.message}</div>`;
            }
        })
        .catch(err => {
            console.error(err);
            document.getElementById('ai-report-content').innerHTML = `<div style="color: #ef4444; padding: 10px;">⚠️ AI 분석 요청 중 오류가 발생했습니다.</div>`;
        });"""

# Find target indices (ignoring exact CRLF endings to locate indices)
idx_start = content.find(target_start)

# We can find target_end by matching text (normalized)
# Since CRLF can vary, let's normalize both to get exact position
norm_content = content.replace("\r\n", "\n")
norm_target_end = target_end.replace("\r\n", "\n")

idx_end_norm = norm_content.find(norm_target_end)

if idx_start != -1 and idx_end_norm != -1:
    # Map normalized index back to CRLF index
    # We can reconstruct it simply:
    # Count how many \n are before idx_end_norm, which adds to \r count
    num_newlines = norm_content[:idx_end_norm].count("\n")
    idx_end = idx_end_norm + num_newlines
    
    # Verify we hit the right spot
    # The snippet at idx_end should match target_end first line
    snippet = content[idx_end:idx_end+50]
    print(f"Match verify at raw index {idx_end}: {repr(snippet)}")
    
    new_content = content[:idx_start] + replacement + content[idx_end + len(target_end):]
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Success: analysis.html updated successfully via script!")
else:
    print(f"Error: indices not found: start={idx_start}, end_norm={idx_end_norm}")
