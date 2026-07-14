import sys
import os

sys.path.append(os.path.abspath("backend"))
from app import get_road_flows

print("Calling get_road_flows for Gangnam directly in Python...")
try:
    res = get_road_flows(
        min_lat=37.490,
        max_lat=37.510,
        min_lng=127.020,
        max_lng=127.050
    )
    print("Result Status:", res.get("status"))
    features = res.get("data", {}).get("features", []) if isinstance(res.get("data"), dict) else res.get("data", [])
    print("Features count:", len(features))
    if features:
        print("First 5 features properties:")
        for f in features[:5]:
            print(" -", f.get("properties"))
except Exception as e:
    import traceback
    traceback.print_exc()
