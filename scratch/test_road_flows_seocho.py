import sys
import os
import json

sys.path.append(os.path.abspath("backend"))
from app import get_road_flows

print("Calling get_road_flows for Seocho-dong directly in Python...")
try:
    res = get_road_flows(
        min_lat=37.490,
        max_lat=37.500,
        min_lng=127.025,
        max_lng=127.035
    )
    print("Result Status:", res.get("status"))
    features = res.get("data", {}).get("features", []) if isinstance(res.get("data"), dict) else res.get("data", [])
    print("Features count:", len(features))
    for idx, f in enumerate(features):
        print(f"Segment {idx+1}:")
        print("  Properties:", f.get("properties"))
        print("  Coordinates count:", len(f.get("geometry", {}).get("coordinates", [])))
except Exception as e:
    import traceback
    traceback.print_exc()
