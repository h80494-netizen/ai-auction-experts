import sys
import os

# Add backend dir to sys.path
sys.path.append(os.path.abspath("backend"))

from app import get_road_flows

# Let's call get_road_flows directly for Bundang
print("Calling get_road_flows for Bundang (37.380, 127.120) directly in Python...")
try:
    res = get_road_flows(
        min_lat=37.380,
        max_lat=37.385,
        min_lng=127.120,
        max_lng=127.125
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
