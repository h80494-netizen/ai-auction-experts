with open('public/analysis.html', 'r', encoding='utf-8') as f:
    content = f.read()
if 'id="right-panel"' in content:
    print("Found right-panel in analysis.html")
else:
    print("Not found")
