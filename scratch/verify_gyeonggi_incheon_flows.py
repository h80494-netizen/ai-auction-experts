import urllib.request
import json

def test_area(name, min_lat, max_lat, min_lng, max_lng):
    url = f"http://localhost:8000/api/map/road_flows?min_lat={min_lat}&max_lat={max_lat}&min_lng={min_lng}&max_lng={max_lng}"
    print(f"\n--- Testing {name} ---")
    print(f"URL: {url}")
    try:
        response = urllib.request.urlopen(url, timeout=15)
        res_data = json.loads(response.read().decode('utf-8'))
        status = res_data.get("status")
        print(f"Status: {status}")
        if status == "success":
            features = res_data.get("data", {}).get("features", [])
            print(f"Number of road flow lines returned: {len(features)}")
            if features:
                print("First line properties:", json.dumps(features[0].get("properties"), ensure_ascii=False))
                print("First line geometry coordinates count:", len(features[0].get("geometry", {}).get("coordinates", [])))
            else:
                print("WARNING: 0 features returned.")
        else:
            print("ERROR: API returned failure status")
    except Exception as e:
        print("ERROR: Request failed:", e)

# 1. Bundang, Gyeonggi-do
test_area("Gyeonggi-do (Bundang)", 37.380, 37.385, 127.120, 127.125)

# 2. Bupyeong, Incheon
test_area("Incheon (Bupyeong)", 37.488, 37.493, 126.718, 126.723)
