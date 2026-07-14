import requests

url_gg = "http://localhost:8000/api/map/road_flows?min_lat=37.375&max_lat=37.385&min_lng=127.115&max_lng=127.125"
url_ic = "http://localhost:8000/api/map/road_flows?min_lat=37.485&max_lat=37.495&min_lng=126.715&max_lng=126.725"

def check_coords(url, label):
    print(f"\n--- Coords for {label} ---")
    res = requests.get(url).json()
    features = res.get("data", {}).get("features", [])
    if features:
        print(f"Total features: {len(features)}")
        first_feat = features[0]
        print("First feature properties:", first_feat["properties"])
        print("First feature geometry coords:", first_feat["geometry"]["coordinates"][:5])
    else:
        print("No features returned.")

check_coords(url_gg, "Gyeonggi")
check_coords(url_ic, "Incheon")
