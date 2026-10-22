import re

content = open('public/map.html', encoding='utf-8').read()

js_code = ''
if '// --- GIS 고도화 기능 ---' in content:
    parts = content.split('// --- GIS 고도화 기능 ---')
    before = parts[0]
    
    if 'leaflet-heat.js">' in before:
        before = before.replace('leaflet-heat.js">', 'leaflet-heat.js"></script>\n')
    
    rest = '// --- GIS 고도화 기능 ---' + parts[1]
    
    end_script_idx = rest.find('</script>')
    if end_script_idx != -1:
        js_code = rest[:end_script_idx]
        after = rest[end_script_idx + len('</script>'):]
    else:
        js_code = rest
        after = ''
        
    content = before + after

if '</body>' not in content:
    content += '\n<!-- Mobile Tab Bar -->\n<div class="mobile-tab-bar">\n<button class="mobile-tab-btn active" onclick="switchMobileTab(\'map\')">\n<i class="fa-solid fa-map"></i>\n<span>지도</span>\n</button>\n<button class="mobile-tab-btn" onclick="switchMobileTab(\'left\')">\n<i class="fa-solid fa-layer-group"></i>\n<span>레이어</span>\n</button>\n<button class="mobile-tab-btn" onclick="switchMobileTab(\'right\')">\n<i class="fa-solid fa-sliders"></i>\n<span>필터</span>\n</button>\n</div>\n</body>\n</html>'

if js_code:
    if content.endswith('</html>'):
        content = content.replace('</html>', '')
    if content.endswith('</body>\n'):
        content = content.replace('</body>\n', '')
        
    # We just put the js_code at the very end of the <script> block, but before Mobile Tab Bar
    # Let's find the last </script>
    last_script_pos = content.rfind('</script>')
    if last_script_pos != -1:
        content = content[:last_script_pos] + '\n' + js_code + '\n' + content[last_script_pos:]
        
    if '</body>' not in content:
        content += '\n</body>\n</html>'

with open('public/map.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Fully Restored')
