import sys
import os
sys.path.append('backend')
from app import get_road_flows

def test_region(name, min_lat, max_lat, min_lng, max_lng):
    print(f"\n--- Testing {name} ({min_lat}, {min_lng}) ---")
    res = get_road_flows(
        min_lat=min_lat, max_lat=max_lat,
        min_lng=min_lng, max_lng=max_lng,
        day="weekday", time_of_day="day"
    )
    print("Status:", res.get("status"))
    features = res.get("data", {}).get("features", [])
    print("Features count:", len(features))
    if features:
        # Check if first feature is procedural/fallback
        # Fallback names look like "물건지 앞...", "번화가길...", "정류장배후...", "마을...", "주거지..."
        # Real road names are OSM names (like "정자일로", "성남대로", "소도로", etc.)
        sample_names = [f["properties"].get("road_name") for f in features[:10]]
        print("Sample road names:", sample_names)
        
        # Check if any road name contains "물건지", "번화가", "정류장", "마을", "주거지"
        fallback_indicators = ["물건지", "번화가", "정류장", "마을", "주거지", "맛집골목"]
        is_fallback = any(any(ind in name for ind in fallback_indicators) for name in sample_names if name)
        if is_fallback:
            print("Verdict: FALLBACK (Procedural lines)")
        else:
            print("Verdict: CACHE SUCCESS (Actual OSM road segments)")
    else:
        print("Verdict: Empty roads")

# Test Bundang (37.38, 127.12)
test_region("Bundang", 37.375, 37.385, 127.115, 127.125)

# Test Siheung (37.38, 126.80)
test_region("Siheung", 37.377, 37.385, 126.795, 126.816)

# Test Bupyeong (Incheon) (37.49, 126.72)
test_region("Bupyeong", 37.485, 37.495, 126.715, 126.725)
