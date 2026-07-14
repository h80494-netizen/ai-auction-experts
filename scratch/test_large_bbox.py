import sys
import os

sys.path.append(os.path.abspath("backend"))

from app import get_road_flows

print("Calling get_road_flows for large Gyeonggi area directly in Python (should load via single BBox query)...")
try:
    res = get_road_flows(
        min_lat=37.30625,
        max_lat=37.33942,
        min_lng=126.90597,
        max_lng=126.99339
    )
    print("Result Status:", res.get("status"))
    features = res.get("data", {}).get("features", [])
    print("Features count:", len(features))
    if features:
        print("First feature properties:", features[0].get("properties"))
except Exception as e:
    import traceback
    print("EXCEPTION OCCURRED:")
    traceback.print_exc()
