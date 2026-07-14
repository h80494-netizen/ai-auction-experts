import re
import os

map_path = r'public\map.html'
with open(map_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add the new button
button_code = """<div class="icon-btn" id="btn-naver-price" title="네이버 시세 분석" onclick="openNaverPriceModal()"><i class="fa-solid fa-chart-line"></i></div>"""
# Find a place to insert it. We'll search for 'id="btn-highlighter"' or 'fa-highlighter'
if 'id="btn-highlighter"' in content:
    content = content.replace('id="btn-highlighter"', 'id="btn-highlighter"') # Just to be sure
    # Insert right after the highlighter button closing div
    # Let's just use regex
    content = re.sub(r'(<div[^>]*id="btn-highlighter"[^>]*>.*?</div>)', r'\1\n            ' + button_code, content, flags=re.DOTALL)
else:
    # If not found, just append to a known menu container like action-bar or right-panel
    if '<div class="map-controls">' in content:
        content = content.replace('<div class="map-controls">', '<div class="map-controls">\n        ' + button_code)

# 2. Add the Modal HTML
modal_code = """
<!-- Naver Price Analysis Modal -->
<div id="naverPriceModal" class="modal-overlay" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 10000; align-items: center; justify-content: center;">
    <div class="modal-content" style="background: white; padding: 20px; border-radius: 10px; width: 600px; max-width: 90%; max-height: 80vh; overflow-y: auto;">
        <h2><i class="fa-solid fa-chart-line"></i> 네이버 시세 분석</h2>
        <div id="naverPriceLoading" style="display: none; text-align: center; padding: 20px;">
            <i class="fa-solid fa-spinner fa-spin fa-2x"></i>
            <p>시세 데이터를 분석 중입니다...</p>
        </div>
        <div id="naverPriceResult" style="display: none;">
            <table style="width: 100%; border-collapse: collapse; margin-top: 15px; text-align: left;">
                <tbody id="naverPriceTableBody">
                </tbody>
            </table>
        </div>
        <div id="naverPriceError" style="display: none; color: red; margin-top: 15px;"></div>
        <div style="text-align: right; margin-top: 20px;">
            <button onclick="document.getElementById('naverPriceModal').style.display='none'" style="padding: 8px 16px; cursor: pointer; border-radius: 4px; border: 1px solid #ccc; background: #eee;">닫기</button>
        </div>
    </div>
</div>
"""
if 'naverPriceModal' not in content:
    content = content.replace('</body>', modal_code + '\n</body>')

with open(map_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Injected UI successfully")
