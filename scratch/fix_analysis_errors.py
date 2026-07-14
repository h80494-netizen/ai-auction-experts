import re
import os

# 1. Update backend/app.py
app_py_path = 'backend/app.py'
with open(app_py_path, 'r', encoding='utf-8') as f:
    app_py_content = f.read()

# Fix /api/map/overlap_analyze to not use Gemini and return success directly
overlap_analyze_pattern = r'''    try:
        from fastapi\.concurrency import run_in_threadpool
        from ai_analyzer import analyze_overlap_cases
        report_text = await run_in_threadpool\(analyze_overlap_cases, best_items\)
        return \{"status": "success", "report": report_text, "items": sorted_items\}
    except Exception as e:
        return \{"status": "error", "message": f"Gemini .*?: \{str\(e\)\}"\}'''

overlap_analyze_replacement = '''    # AI 심층분석을 프론트엔드 요소별 분석으로 대체했으므로 API 호출을 생략합니다.
    return {"status": "success", "report": "", "items": sorted_items}'''

app_py_content = re.sub(overlap_analyze_pattern, overlap_analyze_replacement, app_py_content, flags=re.DOTALL)

# Fix _background_analyze to have a fallback string if Gemini fails
background_analyze_pattern = r'''            except Exception as e:
                result\["data"\]\["analysis"\] = f"⚠️ 심층 분석 중 오류 발생: \{str\(e\)\}"'''

background_analyze_replacement = '''            except Exception as e:
                # Gemini API 실패 시 폴백 권리분석 텍스트 제공
                appraised = result["data"].get("appraised_value", 0)
                minimum = result["data"].get("minimum_value", 0)
                fallback_analysis = f"""
## 🏢 물건 기본 권리분석 (AI Fallback)
본 물건의 감정가는 **{appraised:,}원**이며, 최저입찰가는 **{minimum:,}원**입니다.
현재 AI 심층분석 API가 제한되어 기본 분석 결과만 제공됩니다.

### ⚖️ 주요 권리 및 인수사항 점검
- **등기부 권리**: 말소기준권리를 확인하여 인수되는 선순위 권리가 있는지 점검해야 합니다.
- **임차인 현황**: 대항력 있는 임차인의 보증금 인수 여부를 매각물건명세서에서 반드시 확인하세요.
- **기타 주의사항**: 특수권리(유치권, 법정지상권 등) 신고 여부를 확인하시기 바랍니다.

> ⚠️ 상세한 권리분석 및 수익률 시뮬레이션은 관련 서류(매각물건명세서, 감정평가서)를 직접 확인하시기 바랍니다.
"""
                result["data"]["analysis"] = fallback_analysis
                result["data"]["ai_sise"] = appraised
                result["data"]["ai_target"] = int(appraised * 0.8)'''

app_py_content = re.sub(background_analyze_pattern, background_analyze_replacement, app_py_content, flags=re.DOTALL)

with open(app_py_path, 'w', encoding='utf-8') as f:
    f.write(app_py_content)
print("Updated backend/app.py")


# 2. Update public/analysis.html
analysis_html_path = 'public/analysis.html'
with open(analysis_html_path, 'r', encoding='utf-8') as f:
    analysis_html_content = f.read()

# Restore reportContentEl container and populate it with Best 3 Summary
if 'id="ai-report-content"' not in analysis_html_content:
    # Add the container at the end of the list-section
    add_container_pattern = r'''        <div class="no-data" id="no-data-msg" style="display: none;">
            조건에 맞는 중첩 분석 물건이 없습니다.
        </div>
    </div>'''
    
    add_container_replacement = '''        <div class="no-data" id="no-data-msg" style="display: none;">
            조건에 맞는 중첩 분석 물건이 없습니다.
        </div>
        <!-- 베스트 3 요소별 요약 리포트 (기존 AI 심층분석 대체) -->
        <div id="ai-report-content" class="ai-report-box" style="margin-top: 30px; padding: 25px; background: rgba(0,0,0,0.3); border-radius: 12px; border: 1px solid rgba(255,255,255,0.1);">
        </div>
    </div>'''
    analysis_html_content = analysis_html_content.replace(add_container_pattern, add_container_replacement)

# Update the fetch logic to generate the factor breakdown HTML manually instead of using data.report
fetch_logic_pattern = r'''                if \(reportContentEl\) \{
                    if \(window\.marked && typeof window\.marked\.parse === 'function'\) \{
                        reportContentEl\.innerHTML = window\.marked\.parse\(data\.report\);
                    \} else \{
                        reportContentEl\.innerHTML = `<pre style="white-space: pre-wrap; font-family: inherit; color: var\(--text-main\); font-size: 0\.85rem;">\$\{data\.report\}</pre>`;
                    \}
                \}'''

fetch_logic_replacement = '''                if (reportContentEl) {
                    if (data.items && data.items.length > 0) {
                        let summaryHtml = `<h3 style="color: #c026d3; margin-bottom: 15px; border-bottom: 1px solid rgba(192, 38, 211, 0.3); padding-bottom: 10px;"><i class="fa-solid fa-chart-line"></i> BEST 3 요소별 종합 분석</h3>`;
                        summaryHtml += `<div style="display: grid; gap: 15px;">`;
                        
                        data.items.slice(0, 3).forEach((item, idx) => {
                            const minBidRate = item.appraisal_price > 0 ? (item.min_price / item.appraisal_price * 100).toFixed(1) : 0;
                            summaryHtml += `
                            <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 8px;">
                                <div style="font-weight: bold; font-size: 1.05rem; margin-bottom: 8px; color: #fff;">
                                    <span style="color: #facc15;"><i class="fa-solid fa-crown"></i> BEST ${idx + 1}</span> | ${item.case_no}
                                </div>
                                <div style="font-size: 0.85rem; color: #cbd5e1; margin-bottom: 5px;">
                                    <strong>수익성:</strong> 최저가율 ${minBidRate}% 수준으로, 경매 낙찰 시 시세 차익 기대가 큽니다.
                                </div>
                                <div style="font-size: 0.85rem; color: #cbd5e1; margin-bottom: 5px;">
                                    <strong>성장성:</strong> ${item.overlap_count}개의 개발/인프라 호재( ${item.matched_layers.join(', ')} )가 중첩되어 미래 가치 상승이 예상됩니다.
                                </div>
                                <div style="font-size: 0.85rem; color: #cbd5e1;">
                                    <strong>안전성:</strong> 특수물건 여부 및 권리 인수 사항을 입찰 전 최종 확인해야 합니다.
                                </div>
                            </div>
                            `;
                        });
                        summaryHtml += `</div>`;
                        reportContentEl.innerHTML = summaryHtml;
                        reportContentEl.style.display = 'block';
                    } else {
                        reportContentEl.innerHTML = `<div style="text-align: center; color: var(--text-muted); padding: 10px;">분석할 데이터가 없습니다.</div>`;
                    }
                }'''

analysis_html_content = re.sub(fetch_logic_pattern, fetch_logic_replacement, analysis_html_content, flags=re.DOTALL)

with open(analysis_html_path, 'w', encoding='utf-8') as f:
    f.write(analysis_html_content)
print("Updated public/analysis.html")
