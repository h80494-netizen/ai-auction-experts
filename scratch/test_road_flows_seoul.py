import sys
import os
sys.path.append('backend')
from app import get_road_flows

# Test for Seoul (approx Gangnam)
res = get_road_flows(
    min_lat=37.50, max_lat=37.51,
    min_lng=127.03, max_lng=127.04,
    day="weekday", time_of_day="day"
)
print("Status:", res.get("status"))
if "data" in res:
    features = res["data"].get("features", [])
    print("Number of road flow features in Seoul:", len(features))
else:
    print("Message:", res.get("message"))
