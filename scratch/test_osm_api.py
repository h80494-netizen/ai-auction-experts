import requests
import xml.etree.ElementTree as ET

# Seohyeon station area, Bundang (0.002 x 0.002 bbox - very small to avoid server overload)
left = 127.118
bottom = 37.378
right = 127.120
top = 37.380

url = f"https://api.openstreetmap.org/api/0.6/map?bbox={left},{bottom},{right},{top}"
print(f"Querying OSM API: {url}")
try:
    response = requests.get(url, timeout=15.0)
    print("Status:", response.status_code)
    if response.status_code == 200:
        print("Success! Response size:", len(response.content))
        # Parse XML
        root = ET.fromstring(response.content)
        ways = root.findall('way')
        print(f"Found {len(ways)} way elements.")
        for w in ways[:3]:
            tags = {tag.get('k'): tag.get('v') for tag in w.findall('tag')}
            print(f"Way ID: {w.get('id')}, Name: {tags.get('name')}, Highway: {tags.get('highway')}")
except Exception as e:
    print("Failed:", e)
