import time
import requests

base_url = "http://localhost:8000"

# Gangnam bounds at zoom 13
# South-West: 37.45, 126.98
# North-East: 37.54, 127.08
params_bounds = {
    "min_lat": 37.45,
    "max_lat": 37.54,
    "min_lng": 126.98,
    "max_lng": 127.08
}

apis = [
    ("/api/map/auctions", params_bounds),
    ("/api/map/pois", params_bounds),
    ("/api/map/subway_lines", {}),
    ("/api/map/hagwon_polygons", {}),
    ("/api/map/district_units", params_bounds),
    ("/api/map/road_flows", params_bounds)
]

print("Testing API Response Times:")
for path, params in apis:
    url = f"{base_url}{path}"
    start = time.time()
    try:
        r = requests.get(url, params=params, timeout=10)
        dur = time.time() - start
        if r.status_code == 200:
            data = r.json()
            status = data.get("status")
            # count elements
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
