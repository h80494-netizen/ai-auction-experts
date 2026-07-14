import urllib.request
import re

url = "https://wiki.openstreetmap.org/wiki/Overpass_API"
print("Fetching OSM wiki page...")
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8')
    
    # Find all links containing interpreter
    matches = re.findall(r'https?://[a-zA-Z0-9./_-]+/api/interpreter', html)
    print("Found interpreter URLs:")
    for m in set(matches):
        print(f" - {m}")
except Exception as e:
    print("Failed to fetch/parse:", e)
