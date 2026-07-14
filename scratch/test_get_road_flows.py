import os
import sys

# Add backend directory to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend'))
sys.path.insert(0, backend_dir)

from app import get_road_flows

# Query an UNCACHED Gyeonggi-do area:
# lat: 37.340 ~ 37.345, lng: 127.140 ~ 127.145
print("Querying uncached Gyeonggi-do area...")
res = get_road_flows(
    min_lat=37.340,
    max_lat=37.345,
    min_lng=127.140,
    max_lng=127.145,
    day="weekday",
    time_of_day="day"
)

print("Status:", res.get("status"))
if res.get("status") == "success":
    features = res.get("data", {}).get("features", [])
    print("Number of road flow features returned:", len(features))
    if features:
        sample_feat = features[0]
        print("\nSample feature properties:")
        print(sorted(sample_feat.get("properties", {}).items()))
        print("Sample feature coordinates:", sample_feat.get("geometry", {}).get("coordinates", []))
else:
    print("Error message:", res.get("message"))
