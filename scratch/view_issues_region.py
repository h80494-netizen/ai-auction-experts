import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('public/issues.html', 'r', encoding='utf-8') as f:
    content = f.read()

pos = content.find("DOMContentLoaded")
if pos != -1:
    print(content[pos-100:pos+1500])
else:
    print("Not found")
