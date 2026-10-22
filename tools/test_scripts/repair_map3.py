import re

with open('public/map.html', encoding='utf-8') as f:
    content = f.read()

# 1. Fix the leaflet-heat tag
content = content.replace('<script src="https://unpkg.com/leaflet.heat@0.2.0/dist/leaflet-heat.js">\n// --- GIS 고도화 기능 ---', '<script src="https://unpkg.com/leaflet.heat@0.2.0/dist/leaflet-heat.js"></script>\n<script>\n// --- GIS 고도화 기능 ---')
# Wait, let's just extract the GIS code.
if '// --- GIS 고도화 기능 ---' in content:
    start_idx = content.find('// --- GIS 고도화 기능 ---')
    # Find where the GIS block ends. It ends at `    }\n}\n` which is toggleHighlighter's closing brace.
    end_text = "    }\n}\n"
    end_idx = content.find(end_text, start_idx)
    if end_idx != -1:
        end_idx += len(end_text)
        gis_code = content[start_idx:end_idx]
        
        # Remove it from its current location
        content = content[:start_idx] + content[end_idx:]
        
        # Clean up any broken script tags around it
        content = content.replace('<script src="https://unpkg.com/leaflet.heat@0.2.0/dist/leaflet-heat.js">\n</script>', '<script src="https://unpkg.com/leaflet.heat@0.2.0/dist/leaflet-heat.js"></script>')
        content = content.replace('<script src="https://unpkg.com/leaflet.heat@0.2.0/dist/leaflet-heat.js">\n', '<script src="https://unpkg.com/leaflet.heat@0.2.0/dist/leaflet-heat.js"></script>\n')
        
        # We want to put gis_code into the MAIN script block at the end
        # The main script block ends with:
        #             }
        #     
        # </script>
        # Let's find the last </script> that comes BEFORE the mobile-tab-bar
        
        # The last script tag before mobile tab bar is usually the one closing the embedded script.
        # Let's just insert it before the last `</script>`
        last_script_pos = content.rfind('</script>')
        
        # We need to make sure the GIS code goes inside the script
        content = content[:last_script_pos] + '\n' + gis_code + '\n' + content[last_script_pos:]

with open('public/map.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Repaired 3')
