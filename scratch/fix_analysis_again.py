import re

with open('public/analysis.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Replace the analysis-section inner HTML
pattern = re.compile(r'<div class="analysis-section">.*?</div>\s*</div>\s*</div>\s*`;', re.DOTALL)
match = pattern.search(content)

if match:
    new_html = """<div class="analysis-section">
                        <div class="analysis-item">
                            <div class="analysis-title" style="color: #ec4899; font-weight: bold;">
                                <i class="fa-solid fa-coins"></i> 1. 수익성 분석 (Profitability)
                            </div>
                            <div class="analysis-desc">${profitAnalysis}</div>
                        </div>
                        <div class="analysis-item">
                            <div class="analysis-title" style="color: #3b82f6; font-weight: bold;">
                                <i class="fa-solid fa-arrow-up-right-dots"></i> 2. 성장성 분석 (Growth Potential)
                            </div>
                            <div class="analysis-desc">${valueAnalysis}</div>
                        </div>
                        <div class="analysis-item">
                            <div class="analysis-title" style="color: #10b981; font-weight: bold;">
                                <i class="fa-solid fa-shield-halved"></i> 3. 안전성 분석 (Safety)
                            </div>
                            <div class="analysis-desc">${claimsAnalysis}<br><br>${uncertaintyAnalysis}</div>
                        </div>
                    </div>
                `;"""
    content = content[:match.start()] + new_html + content[match.end():]
    print("Replaced analysis-section")
else:
    print("Could not find analysis-section pattern")

with open('public/analysis.html', 'w', encoding='utf-8') as f:
    f.write(content)
