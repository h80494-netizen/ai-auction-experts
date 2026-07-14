import urllib.request
import json

lat, lng = 37.380, 126.803
pad_lat = 0.003
pad_lng = 0.004

min_lat = lat - pad_lat
max_lat = lat + pad_lat
min_lng = lng - pad_lng
max_lng = lng + pad_lng

url = f"http://localhost:8000/api/map/road_flows?min_lat={min_lat}&max_lat={max_lat}&min_lng={min_lng}&max_lng={max_lng}"
print(f"Testing Siheung City Hall:")
print(f"URL: {url}")
try:
    response = urllib.request.urlopen(url, timeout=20)
    res_data = json.loads(response.read().decode('utf-8'))
    print("Status:", res_data.get("status"))
    features = res_data.get("data", {}).get("features", [])
    print("Number of features returned:", len(features))
    if features:
        # Check first 10 features' road names
        names = [f.get("properties", {}).get("road_name") for f in features[:15]]
        print("Sample road names:", names)
    else:
        print("No features returned.")
except Exception as e:
    print("Error:", e)
