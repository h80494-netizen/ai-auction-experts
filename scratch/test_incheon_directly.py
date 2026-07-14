import sys
import os

# Add backend dir to sys.path
sys.path.append(os.path.abspath("backend"))

from app import get_road_flows

print("Calling get_road_flows for Incheon (Bupyeong) directly in Python...")
try:
    res = get_road_flows(
        min_lat=37.488,
        max_lat=37.493,
        min_lng=126.718,
        max_lng=126.723
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
