import requests
import json
import time

query = """
[out:json][timeout:25];
(
  way["highway"~"residential|service|unclassified|pedestrian|path|footway|living_street"](37.38,127.12,37.39,127.13);
);
out geom;
"""

urls = [
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "http://localhost:8000/"
}

for url in urls:
    print(f"\nTesting mirror: {url}")
    try:
        t0 = time.time()
        res = requests.post(url, data={"data": query}, headers=headers, timeout=30.0)
        t1 = time.time()
        print(f"Status: {res.status_code} in {t1 - t0:.2f}s")
        if res.status_code == 200:
            data = res.json()
            elements = data.get("elements", [])
            print(f"Retrieved {len(elements)} elements.")
        else:
            print("Error output:", res.text[:200])
    except Exception as e:
        print("Error:", e)
