import sys
import os
import time

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from app import get_grid_demographics, get_road_flows

def measure_grid(type_name, lat, lng, lat_span=0.007, lng_span=0.009):
    min_lat = lat - lat_span/2
    max_lat = lat + lat_span/2
    min_lng = lng - lng_span/2
    max_lng = lng + lng_span/2
    
    print(f"\n--- Measuring get_grid_demographics ({type_name}) ---")
    start = time.time()
    try:
        res = get_grid_demographics(
            min_lat=min_lat, max_lat=max_lat, min_lng=min_lng, max_lng=max_lng,
            type=type_name, regions="서울,경기,인천"
        )
        duration = time.time() - start
        print(f"Status: {res.get('status')}")
        print(f"Grids returned: {len(res.get('data', []))}")
        print(f"Duration: {duration:.4f} seconds")
    except Exception as e:
        print("Error:", e)

def measure_road_flows(lat, lng, lat_span=0.007, lng_span=0.009):
    min_lat = lat - lat_span/2
    max_lat = lat + lat_span/2
    min_lng = lng - lng_span/2
    max_lng = lng + lng_span/2
    
    print(f"\n--- Measuring get_road_flows ---")
    start = time.time()
    try:
        res = get_road_flows(
            min_lat=min_lat, max_lat=max_lat, min_lng=min_lng, max_lng=max_lng,
            day="weekday", time_of_day="day"
        )
        duration = time.time() - start
        print(f"Status: {res.get('status')}")
        features = res.get('data', {}).get('features', [])
        print(f"Features returned: {len(features)}")
        print(f"Duration: {duration:.4f} seconds")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    # Bundang coordinates
    lat, lng = 37.3825, 127.1225
    measure_grid("residential", lat, lng)
    measure_grid("workplace", lat, lng)
    measure_road_flows(lat, lng)
