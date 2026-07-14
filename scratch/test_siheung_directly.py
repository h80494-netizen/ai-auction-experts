import sys
import os
sys.path.append('backend')
from app import get_road_flows

# Test for Siheung (approx lat=37.38, lng=126.80)
res = get_road_flows(
    min_lat=37.37714868232716, max_lat=37.38543524621681,
    min_lng=126.79498851299287, max_lng=126.81684315204622,
    day="weekday", time_of_day="day"
)
print("Status:", res.get("status"))
if "data" in res:
    features = res["data"].get("features", [])
    print("Number of road flow features:", len(features))
    if features:
        print("Sample feature properties:")
        for idx, f in enumerate(features[:5]):
            print(f" - {idx}: {f['properties']}")
else:
    print("Message:", res.get("message"))
