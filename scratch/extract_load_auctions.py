import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('public/map.html', 'r', encoding='utf-8') as f:
    content = f.read()

pos = content.find("async function loadAuctions()")
if pos != -1:
    print(content[pos:pos+3000])
else:
    print("Not found")
