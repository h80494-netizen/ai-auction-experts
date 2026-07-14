import time
import requests

base_url = "http://localhost:8000"

params_wide = {
    "min_lat": 37.0,
    "max_lat": 38.0,
    "min_lng": 126.0,
    "max_lng": 128.0
}

apis = [
    ("/api/map/auctions", params_wide),
    ("/api/map/pois", params_wide),
    ("/api/map/district_units", params_wide),
    ("/api/map/road_flows", params_wide)
]

print("Testing WIDE API Response Times:")
for path, params in apis:
    url = f"{base_url}{path}"
    start = time.time()
    try:
        r = requests.get(url, params=params, timeout=15)
        dur = time.time() - start
        if r.status_code == 200:
            data = r.json()
            status = data.get("status")
            items = data.get("data", [])
            if isinstance(items, dict):
                count = sum(len(v) for v in items.values() if isinstance(v, list))
            else:
                count = len(items)
            print(f" - {path}: {dur:.3f}s, Status: {status}, Count: {count}")
        else:
            print(f" - {path}: Failed with code {r.status_code}")
    except Exception as e:
        print(f" - {path}: Error: {e}")
