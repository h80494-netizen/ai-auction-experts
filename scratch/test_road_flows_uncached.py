import os
import sys

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend'))
sys.path.insert(0, backend_dir)

from app import get_road_flows

# Query an UNCACHED Gyeonggi-do area in Anseong:
print("Querying uncached Gyeonggi-do area (Anseong)...")
res = get_road_flows(
    min_lat=37.045,
    max_lat=37.050,
    min_lng=127.028,
    max_lng=127.034,
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
