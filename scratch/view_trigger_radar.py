import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('public/issues.html', 'r', encoding='utf-8') as f:
    content = f.read()

pos = content.find("function triggerRadarScan")
if pos != -1:
    print(content[pos+1500:pos+3000])
else:
    print("Not found")
