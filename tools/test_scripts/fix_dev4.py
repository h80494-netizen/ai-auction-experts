import re

with open('public/map.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove the standalone 'toggle-dev2' HTML block
target_dev2_html = """            <!-- 개발행위허가제한지역 -->
            <div class="toggle-row">
                <div class="toggle-label"><i class="fa-solid fa-map" style="color: #10b981;"></i> 개발행위허가제한지역</div>
                <label class="switch"><input type="checkbox" id="toggle-dev2"><span class="slider"></span></label>
            </div>"""

if target_dev2_html in content:
    content = content.replace(target_dev2_html, "")
else:
    print("Could not find target_dev2_html exact match. Trying regex.")
    content = re.sub(r'<!--\s*개발행위허가제한지역\s*-->\s*<div class="toggle-row">\s*<div class="toggle-label">.*?개발행위허가제한지역</div>\s*<label class="switch"><input type="checkbox" id="toggle-dev2"><span class="slider"></span></label>\s*</div>', '', content, flags=re.DOTALL)


# 2. Insert event listener for toggle-dev4
target_listener = """            document.getElementById('toggle-dev3').addEventListener('change', (e) => {"""
replacement_listener = """            document.getElementById('toggle-dev4').addEventListener('change', (e) => {
                const subContainer = document.getElementById('dev4-sub-container');
                if (e.target.checked) {
                    if (subContainer) subContainer.style.display = 'block';
                    fetchDeregulationZones();
                } else {
                    if (subContainer) subContainer.style.display = 'none';
                    layers.dev4.clearLayers();
                }
            });
            document.querySelectorAll('.dev4-type-check').forEach(cb => {
                cb.addEventListener('change', fetchDeregulationZones);
            });

            document.getElementById('toggle-dev3').addEventListener('change', (e) => {"""

if target_listener in content:
    content = content.replace(target_listener, replacement_listener)
else:
    print("Could not find target_listener exact match.")

with open('public/map.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done updating map.html: removed dev2 standalone and added dev4 event listeners.")
