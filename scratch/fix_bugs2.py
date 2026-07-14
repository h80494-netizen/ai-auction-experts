import re

with open('public/analysis.html', 'r', encoding='utf-8') as f:
    analysis_html = f.read()

# Fix innerHTML 2
analysis_html = re.sub(
    r'(\s*)} else {\s*reportContentEl\.innerHTML = `<div[^>]*>분석 리포트 생성에 실패했습니다\.\s*</div>`;\s*}',
    r'\1} else {\n\1    if (reportContentEl) {\n\1        reportContentEl.innerHTML = `<div style="text-align: center; color: #f43f5e; padding: 10px;">분석 리포트 생성에 실패했습니다.</div>`;\n\1    }\n\1}',
    analysis_html
)

# Fix innerHTML 3
analysis_html = re.sub(
    r'(\s*)document\.getElementById\(\'ai-report-content\'\)\.innerHTML = `<div[^>]*>분석 리포트 요청 중 오류가 발생했습니다\.\s*</div>`;',
    r'\1const reportContentEl = document.getElementById(\'ai-report-content\');\n\1if (reportContentEl) {\n\1    reportContentEl.innerHTML = `<div style="text-align: center; color: #f43f5e; padding: 10px;">분석 리포트 요청 중 오류가 발생했습니다.</div>`;\n\1}',
    analysis_html
)

with open('public/analysis.html', 'w', encoding='utf-8') as f:
    f.write(analysis_html)
print("Regex replacements executed")
