import re

with open('public/analysis.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove HTML section for AI report
start_html = content.find('<!-- AI Overlap Report Section -->')
end_html = content.find('<!-- Complete list of matched auctions -->')
if start_html != -1 and end_html != -1:
    content = content[:start_html] + content[end_html:]

# 2. Remove JS fetch section
start_js = content.find('// Build payload data for backend')
end_js = content.find('    </script>\n</body>')
if start_js != -1 and end_js != -1:
    content = content[:start_js] + content[end_js:]

with open('public/analysis.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Removed AI report successfully.")
