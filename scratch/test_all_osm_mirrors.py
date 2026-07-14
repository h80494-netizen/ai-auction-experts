import requests

c_min_lat, c_min_lng = 37.50, 127.03
c_max_lat, c_max_lng = 37.51, 127.04

query = f"""
[out:json][timeout:5];
(
  way["highway"~"residential|service|unclassified|pedestrian|path|footway|living_street"]({c_min_lat},{c_min_lng},{c_max_lat},{c_max_lng});
);
out geom 5;
"""

mirrors = [
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://overpass.n.openstreetmap.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.openstreetmap.ru/cgi/interpreter",
    "https://overpass.osm.rambler.ru/cgi/interpreter"
]

for url in mirrors:
    print(f"Testing {url}...")
    try:
        res = requests.post(url, data={"data": query}, timeout=8.0)
        print(f" - Status: {res.status_code}")
        if res.status_code == 200:
            elements = res.json().get("elements", [])
            print(f" - Elements: {len(elements)}")
    except Exception as e:
        print(f" - Error: {e}")
