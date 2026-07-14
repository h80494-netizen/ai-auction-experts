import requests
import time

urls = [
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.osm.ch/api/interpreter"
]

# Bundang area BBox
c_min_lat = 37.380
c_max_lat = 37.385
c_min_lng = 127.120
c_max_lng = 127.125

query = f"""
[out:json][timeout:10];
(
  way["highway"~"residential|service|unclassified|pedestrian|path|footway|living_street"]({c_min_lat},{c_min_lng},{c_max_lat},{c_max_lng});
);
out geom;
"""

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "http://localhost:8000/",
}

for url in urls:
    print(f"\nTesting Overpass mirror: {url}")
    t0 = time.time()
    try:
        response = requests.post(url, data={"data": query}, headers=headers, timeout=12.0)
        t1 = time.time()
        print(f"Status Code: {response.status_code}")
        print(f"Time Taken: {t1 - t0:.3f} seconds")
        if response.status_code == 200:
            data = response.json()
            elements = data.get("elements", [])
            print(f"Success! Found {len(elements)} elements.")
            if elements:
                break
    except Exception as e:
        print(f"Failed: {e}")
