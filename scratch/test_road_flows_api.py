import requests
import json
import time

url = "http://127.0.0.1:8000/api/map/road_flows"

# Bounding box for testing (Seoul Jamsil/Songpa area)
params = {
    "min_lat": 37.510,
    "max_lat": 37.515,
    "min_lng": 127.070,
    "max_lng": 127.075
}

print(f"Requesting road flows with parameters: {params}")

# Measure request time
t0 = time.time()
try:
    response = requests.get(url, params=params, timeout=15)
    t1 = time.time()
    print(f"Status Code: {response.status_code}")
    print(f"Time Taken: {t1 - t0:.3f} seconds")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Status in Response: {data.get('status')}")
        features = data.get("data", {}).get("features", []) if isinstance(data.get("data"), dict) else data.get("data", [])
        print(f"Number of road segments returned: {len(features)}")
        if len(features) > 0:
            print("First road segment properties:")
            print(json.dumps(features[0].get("properties"), indent=2, ensure_ascii=False))
            print("First road segment geometry coordinates count:")
            print(len(features[0].get("geometry", {}).get("coordinates", [])))
            
except Exception as e:
    print(f"Request failed: {e}")
