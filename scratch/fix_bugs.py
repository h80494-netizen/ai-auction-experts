import re

with open('public/map.html', 'r', encoding='utf-8') as f:
    map_html = f.read()

# Fix 1: Hide btn-show-analysis in applyHighlighter() early return
old_code = """                if (countEl) countEl.style.display = 'none';
                if (modeContainer) modeContainer.style.display = 'none';
                return;"""

new_code = """                if (countEl) countEl.style.display = 'none';
                if (modeContainer) modeContainer.style.display = 'none';
                const btnAnalysis = document.getElementById('btn-show-analysis');
                if (btnAnalysis) btnAnalysis.style.display = 'none';
                return;"""

if old_code in map_html:
    map_html = map_html.replace(old_code, new_code)
    print("Fixed early return in applyHighlighter")

with open('public/map.html', 'w', encoding='utf-8') as f:
    f.write(map_html)


with open('public/analysis.html', 'r', encoding='utf-8') as f:
    analysis_html = f.read()

# Fix 2: Check if reportContentEl exists before using it
old_fetch_then = """        .then(data => {
            const reportContentEl = document.getElementById('ai-report-content');
            if (data.status === 'success') {"""

new_fetch_then = """        .then(data => {
            const reportContentEl = document.getElementById('ai-report-content');
            if (data.status === 'success') {"""

old_innerHTML_1 = """                if (window.marked && typeof window.marked.parse === 'function') {
                    reportContentEl.innerHTML = window.marked.parse(data.report);
                } else {
                    reportContentEl.innerHTML = `<pre style="white-space: pre-wrap; font-family: inherit; color: var(--text-main); font-size: 0.85rem;">${data.report}</pre>`;
                }"""

new_innerHTML_1 = """                if (reportContentEl) {
                    if (window.marked && typeof window.marked.parse === 'function') {
                        reportContentEl.innerHTML = window.marked.parse(data.report);
                    } else {
                        reportContentEl.innerHTML = `<pre style="white-space: pre-wrap; font-family: inherit; color: var(--text-main); font-size: 0.85rem;">${data.report}</pre>`;
                    }
                }"""

old_innerHTML_2 = """            } else {
                reportContentEl.innerHTML = `<div style="text-align: center; color: #f43f5e; padding: 10px;">분석 리포트 생성에 실패했습니다.</div>`;
            }"""

new_innerHTML_2 = """            } else {
                if (reportContentEl) {
                    reportContentEl.innerHTML = `<div style="text-align: center; color: #f43f5e; padding: 10px;">분석 리포트 생성에 실패했습니다.</div>`;
                }
            }"""

old_innerHTML_3 = """        .catch(err => {
            console.error('Failed to fetch overlap report:', err);
            document.getElementById('ai-report-content').innerHTML = `<div style="text-align: center; color: #f43f5e; padding: 10px;">분석 리포트 요청 중 오류가 발생했습니다.</div>`;
        });"""

new_innerHTML_3 = """        .catch(err => {
            console.error('Failed to fetch overlap report:', err);
            const reportContentEl = document.getElementById('ai-report-content');
            if (reportContentEl) {
                reportContentEl.innerHTML = `<div style="text-align: center; color: #f43f5e; padding: 10px;">분석 리포트 요청 중 오류가 발생했습니다.</div>`;
            }
        });"""

if old_innerHTML_1 in analysis_html:
    analysis_html = analysis_html.replace(old_innerHTML_1, new_innerHTML_1)
    print("Fixed innerHTML 1")

if old_innerHTML_2 in analysis_html:
    analysis_html = analysis_html.replace(old_innerHTML_2, new_innerHTML_2)
    print("Fixed innerHTML 2")

if old_innerHTML_3 in analysis_html:
    analysis_html = analysis_html.replace(old_innerHTML_3, new_innerHTML_3)
    print("Fixed innerHTML 3")

with open('public/analysis.html', 'w', encoding='utf-8') as f:
    f.write(analysis_html)
