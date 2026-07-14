import os

filepath = 'public/analysis.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Normalize to LF
content = content.replace('\r\n', '\n')

target = """                        <div class="matched-badges">
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
            });"""

replacement = """                        <div class="matched-badges">
                            ${(item.matched_layers || []).map(layer => `<span class="matched-badge">${layer}</span>`).join('')}
                        </div>

                        <!-- Demographics Panel (Dynamic) -->
                        <div class="demographics-container" id="demo-container-${index}" style="margin-top: 15px; padding-top: 12px; border-top: 1px dashed rgba(255,255,255,0.15); display: none;">
                            <div style="font-size: 0.8rem; font-weight: bold; color: var(--text-highlight); margin-bottom: 8px; display: flex; align-items: center; gap: 6px;">
                                <i class="fa-solid fa-chart-pie"></i> 입지 배후수요 및 인구 분석
                            </div>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 8px;">
                                <div style="background: rgba(0,0,0,0.25); padding: 6px 8px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.05);">
                                    <div style="font-size: 0.65rem; color: var(--text-muted); margin-bottom: 2px;">거주인구 (세대수)</div>
                                    <div style="font-size: 0.8rem; font-weight: bold; color: #fff;" id="demo-pop-${index}">-명 (-세대)</div>
                                </div>
                                <div style="background: rgba(0,0,0,0.25); padding: 6px 8px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.05);">
                                    <div style="font-size: 0.65rem; color: var(--text-muted); margin-bottom: 2px;">직장인구 (업체수)</div>
                                    <div style="font-size: 0.8rem; font-weight: bold; color: #fff;" id="demo-work-${index}">-명 (-개)</div>
                                </div>
                            </div>
                            <div style="font-size: 0.72rem; color: var(--text-muted); margin-bottom: 8px;" id="demo-subway-${index}">
                                대중교통: -
                            </div>
                            <div style="display: flex; flex-direction: column; gap: 3px; font-size: 0.7rem; background: rgba(0,0,0,0.15); padding: 8px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.03);" id="demo-age-dist-${index}">
                                <!-- Age distribution bars -->
                            </div>
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

                // 비동기로 배후수요 로드 실행
                loadDemographicsForCard(item, index);
            });"""

# Handle potential Korean decoding issues in comparison by removing non-ascii or matching strictly.
# The target has "개발 가치 및 상승 잠재력", "인수액 리스크 (선순위 분석)", "권리 투명성 및 불확실성".
# Python in utf-8 will read it correctly. Let's do the check.

if target in content:
    content = content.replace(target, replacement)
    # Convert back to Windows CRLF since it's Windows
    content = content.replace('\n', '\r\n')
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Success: Replacement applied!")
else:
    print("Error: Target content not found!")
