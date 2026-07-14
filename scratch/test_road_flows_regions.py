import requests
import json

# Test Bundang (Gyeonggi)
# center around lat=37.38, lng=127.12
# min_lat=37.375, max_lat=37.385, min_lng=127.115, max_lng=127.125
url_gg = "http://localhost:8000/api/map/road_flows?min_lat=37.375&max_lat=37.385&min_lng=127.115&max_lng=127.125"

# Test Bupyeong (Incheon)
# center around lat=37.49, lng=126.72
# min_lat=37.485, max_lat=37.495, min_lng=126.715, max_lng=126.725
url_ic = "http://localhost:8000/api/map/road_flows?min_lat=37.485&max_lat=37.495&min_lng=126.715&max_lng=126.725"

def check_url(url, region_name):
    print(f"\n--- Checking {region_name} ---")
    try:
        res = requests.get(url, timeout=10)
        print("Status Code:", res.status_code)
        if res.status_code == 200:
            data = res.json()
            if data.get("status") == "success":
                geojson = data.get("data", {})
                features = geojson.get("features", [])
                print("Total features:", len(features))
                
                # Check road names to identify if it is procedural or real
                road_names = [f["properties"].get("road_name") for f in features[:15]]
                print("First 15 road names:")
                for name in road_names:
                    print(f" - {name}")
            else:
                print("API error:", data.get("message"))
        else:
            print("Response text:", res.text[:200])
    except Exception as e:
        print("Error connecting:", e)

check_url(url_gg, "Gyeonggi (Bundang)")
check_url(url_ic, "Incheon (Bupyeong)")
