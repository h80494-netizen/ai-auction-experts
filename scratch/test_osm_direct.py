import requests
import urllib.parse

c_min_lat, c_min_lng = 37.50, 127.03
c_max_lat, c_max_lng = 37.51, 127.04

query = f"""
[out:json][timeout:10];
(
  way["highway"~"residential|service|unclassified|pedestrian|path|footway|living_street"]({c_min_lat},{c_min_lng},{c_max_lat},{c_max_lng});
);
out geom 5;
"""

mirrors = [
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter"
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

for url in mirrors:
    print(f"\nTesting mirror: {url}")
    # Method 1: POST with form data
    print("Method 1 (POST with form-data):")
    try:
        res = requests.post(url, data={"data": query}, headers=headers, timeout=10.0)
        print(f" - Status: {res.status_code}")
        if res.status_code == 200:
            print(f" - Elements: {len(res.json().get('elements', []))}")
    except Exception as e:
        print(f" - Error: {e}")
        
    # Method 2: GET with params
    print("Method 2 (GET with query params):")
    try:
        res = requests.get(url, params={"data": query}, headers=headers, timeout=10.0)
        print(f" - Status: {res.status_code}")
        if res.status_code == 200:
            print(f" - Elements: {len(res.json().get('elements', []))}")
    except Exception as e:
        print(f" - Error: {e}")
