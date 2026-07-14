import re

with open('public/analysis.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove AI Report HTML
ai_report_pattern = re.compile(r'<!-- AI Overlap Report Section -->.*?</div>\s*</div>\s*<!-- Table Section -->', re.DOTALL)
content = ai_report_pattern.sub('<!-- Table Section -->', content)

# 2. Modify analysis-section in JS
old_analysis_html = """                    <div class="analysis-section">
                        <div class="analysis-item">
                            <div class="analysis-title">
                                <i class="fa-solid fa-arrow-up-right-dots"></i> 미래 가치 및 성장 동력
                            </div>
                            <div class="analysis-desc">${valueAnalysis}</div>
                        </div>
                        <div class="analysis-item">
                            <div class="analysis-title">
                                <i class="fa-solid fa-shield-halved"></i> 인수 리스크 (권리 분석)
                            </div>
                            <div class="analysis-desc">${claimsAnalysis}</div>
                        </div>
                        <div class="analysis-item">
                            <div class="analysis-title">
                                <i class="fa-solid fa-circle-check"></i> 판매 소요 기간 및 확실성
                            </div>
                            <div class="analysis-desc">${uncertaintyAnalysis}</div>
                        </div>
                    </div>"""

new_analysis_html = """                    <div class="analysis-section">
                        <div class="analysis-item">
                            <div class="analysis-title" style="color: #ec4899;">
                                <i class="fa-solid fa-coins"></i> 1. 수익성 분석 (Profitability)
                            </div>
                            <div class="analysis-desc">${profitAnalysis}</div>
                        </div>
                        <div class="analysis-item">
                            <div class="analysis-title" style="color: #3b82f6;">
                                <i class="fa-solid fa-arrow-up-right-dots"></i> 2. 성장성 분석 (Growth Potential)
                            </div>
                            <div class="analysis-desc">${valueAnalysis}</div>
                        </div>
                        <div class="analysis-item">
                            <div class="analysis-title" style="color: #10b981;">
                                <i class="fa-solid fa-shield-halved"></i> 3. 안전성 분석 (Safety)
                            </div>
                            <div class="analysis-desc">${claimsAnalysis} <br><br> ${uncertaintyAnalysis}</div>
                        </div>
                    </div>"""

content = content.replace(old_analysis_html, new_analysis_html)

# 3. Add profitAnalysis JS
insert_point = """                // 2. Differentiated Claims/Takeover Risk analysis"""
profit_js = """                // 1.5. Profitability Analysis
                let profitAnalysis = "";
                if (yieldRate >= 10) {
                    profitAnalysis = `감정가 대비 <strong>${(100 - minBidRate).toFixed(1)}% 할인</strong>된 가격(${formatPrice(minBidPrice)})으로 접근 가능하여, 보수적 산정 시에도 <strong>${yieldRate.toFixed(1)}%의 우수한 예상 마진율</strong>이 기대됩니다. 가격 방어력이 높아 수익성 확보가 매우 용이합니다.`;
                } else if (yieldRate >= 0) {
                    profitAnalysis = `현재 최저가는 감정가 대비 <strong>${(100 - minBidRate).toFixed(1)}% 할인</strong>되어 있으며, 예상 마진율은 <strong>${yieldRate.toFixed(1)}%</strong> 수준입니다. 단기 차익보다는 실거주 및 중장기적 가치 투자 관점에서의 접근을 권장합니다.`;
                } else {
                    profitAnalysis = `현재 최저가는 감정가 대비 <strong>${(100 - minBidRate).toFixed(1)}% 할인</strong>되어 있으나, 인수 금액 등 추가 비용 부담으로 실질 마진율이 <strong>${yieldRate.toFixed(1)}%</strong>로 산출됩니다. 유찰을 더 기다리거나 매우 보수적인 투찰가 산정이 필수적입니다.`;
                }

"""

content = content.replace(insert_point, profit_js + insert_point)

# 4. Remove JS that fetches /api/agent/overlap_report
fetch_report_pattern = re.compile(r'\s*// Fetch AI Overlap Report.*?document\.getElementById\(\'ai-report-content\'\)\.innerHTML = `<div style="text-align: center; color: var\(--text-muted\); padding: 10px;">중첩 분석 데이터가 존재하지 않습니다\.</div>`;\n\s*\}', re.DOTALL)
content = fetch_report_pattern.sub('', content)

with open('public/analysis.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Modified analysis.html successfully")
