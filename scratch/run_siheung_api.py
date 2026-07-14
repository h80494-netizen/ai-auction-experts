import urllib.request
import json

url = "http://localhost:8000/api/map/road_flows?min_lat=37.37714868232716&max_lat=37.38543524621681&min_lng=126.79498851299287&max_lng=126.81684315204622&day=weekday&time_of_day=day"
print("Querying exact Siheung URL from log:")
try:
    response = urllib.request.urlopen(url, timeout=10)
    data = json.loads(response.read().decode('utf-8'))
    print("Status:", data.get("status"))
    features = data.get("data", {}).get("features", [])
    print("Number of features returned:", len(features))
    if features:
        sample_names = [f.get("properties", {}).get("road_name") for f in features[:15]]
        print("Sample road names:", sample_names)
except Exception as e:
    print("Error:", e)
