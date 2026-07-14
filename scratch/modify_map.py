import re

map_html_path = 'public/map.html'
with open(map_html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add toggle for unexecuted auctions in right panel
toggle_html = """
            <div class="toggle-row">
                <div class="toggle-label"><i class="fa-solid fa-road-barrier" style="color: #ef4444;"></i> 보상예정(장기미집행)</div>
                <label class="switch"><input type="checkbox" id="toggle-unexecuted-auctions" onchange="loadAuctions()"><span class="slider"></span></label>
            </div>
"""

# Insert before max-area or somewhere in right-panel filters
content = content.replace('<!-- Right Panel - Filters -->', '<!-- Right Panel - Filters -->\n' + toggle_html)

# 2. Add parameter to buildAuctionUrl
if 'const reqElite =' in content:
    content = content.replace('const reqElite =', "const unexecutedOnly = document.getElementById('toggle-unexecuted-auctions') ? document.getElementById('toggle-unexecuted-auctions').checked : false;\n            const reqElite =")
    
if 'if (checkedTypes.length > 0) url += `&property_types=${checkedTypes.join(\',\')}`;' in content:
    content = content.replace('if (checkedTypes.length > 0) url += `&property_types=${checkedTypes.join(\',\')}`;', 'if (checkedTypes.length > 0) url += `&property_types=${checkedTypes.join(\',\')}`;\n            if (unexecutedOnly) url += `&unexecuted_only=true`;')

with open(map_html_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Modified map.html")
