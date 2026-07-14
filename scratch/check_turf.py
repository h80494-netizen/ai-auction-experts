with open('public/map.html', 'r', encoding='utf-8') as f:
    content = f.read()

print("Turf.js in map.html:", "turf" in content.lower())
# Find scripts
import re
scripts = re.findall(r'<script[^>]*src="([^"]+)"', content)
print("Scripts loaded:")
for s in scripts:
    print(" -", s)
