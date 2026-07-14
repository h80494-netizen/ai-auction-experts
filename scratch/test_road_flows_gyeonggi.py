import sys
import os
sys.path.append('backend')
from app import get_road_flows

# Test for Bundang (approx lat=37.38, lng=127.12)
res = get_road_flows(
    min_lat=37.375, max_lat=37.385,
    min_lng=127.115, max_lng=127.125,
    day="weekday", time_of_day="day"
)
print("Status:", res.get("status"))
if "data" in res:
    features = res["data"].get("features", [])
    print("Number of road flow features:", len(features))
    if features:
        print("Sample feature properties:", features[0]["properties"])
else:
    print("Message:", res.get("message"))
