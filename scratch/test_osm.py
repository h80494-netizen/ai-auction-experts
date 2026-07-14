import requests
import json
import re

c_min_lat, c_max_lat = 37.43, 37.44
c_min_lng, c_max_lng = 127.15, 127.16

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "http://localhost:8000/",
}

# Try OSM Main API
try:
    osm_url = f"https://api.openstreetmap.org/api/0.6/map?bbox={c_min_lng},{c_min_lat},{c_max_lng},{c_max_lat}"
    print(f"Fetching from OSM Main API: {osm_url}")
    res = requests.get(osm_url, headers=headers, timeout=10.0)
    print("OSM Main API Status:", res.status_code)
    if res.status_code == 200:
        print("OSM Main API Success, content length:", len(res.content))
    else:
        print("OSM Main API Response:", res.text[:200])
except Exception as e:
    print("OSM Main API Error:", e)

# Try Overpass API
urls = [
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter"
]
query = f"""
[out:json][timeout:10];
(
  way["highway"~"residential|service|unclassified|pedestrian|path|footway|living_street"]({c_min_lat},{c_min_lng},{c_max_lat},{c_max_lng});
);
out geom;
"""

for url in urls:
    try:
        print(f"Fetching from Overpass: {url}")
        res = requests.post(url, data={"data": query}, headers=headers, timeout=10.0)
        print("Overpass Status:", res.status_code)
        if res.status_code == 200:
            data = res.json()
            elements = data.get("elements", [])
            print(f"Overpass Success, parsed {len(elements)} elements")
            break
        else:
            print("Overpass Response:", res.text[:200])
    except Exception as e:
        print("Overpass Error:", e)
