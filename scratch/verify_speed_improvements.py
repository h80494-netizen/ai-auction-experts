import sys
import os
import time

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from app import get_grid_demographics, get_road_flows

def run_benchmark():
    # Bundang (cached)
    b_lat, b_lng = 37.3825, 127.1225
    # Completely new coords for uncached test
    u_lat, u_lng = 37.2050, 126.9550
    
    lat_span, lng_span = 0.007, 0.009
    
    print("====================================================")
    print("       SPEED & COMPILATION BENCHMARK REPORT         ")
    print("====================================================")
    
    # 1. Cached Demographics
    t0 = time.time()
    res = get_grid_demographics(
        min_lat=b_lat - lat_span/2, max_lat=b_lat + lat_span/2,
        min_lng=b_lng - lng_span/2, max_lng=b_lng + lng_span/2,
        type="residential", regions="서울,경기,인천"
    )
    t_cached_demo = time.time() - t0
    print(f"1. Cached Demographics: {t_cached_demo:.4f}s (Returned {len(res.get('data', []))} grids)")
    
    # 2. Uncached Demographics
    t0 = time.time()
    res = get_grid_demographics(
        min_lat=u_lat - lat_span/2, max_lat=u_lat + lat_span/2,
        min_lng=u_lng - lng_span/2, max_lng=u_lng + lng_span/2,
        type="residential", regions="서울,경기,인천"
    )
    t_uncached_demo = time.time() - t0
    print(f"2. Uncached Demographics: {t_uncached_demo:.4f}s (Returned {len(res.get('data', []))} grids)")
    
    # 3. Cached Road Flows
    t0 = time.time()
    res = get_road_flows(
        min_lat=b_lat - lat_span/2, max_lat=b_lat + lat_span/2,
        min_lng=b_lng - lng_span/2, max_lng=b_lng + lng_span/2,
        day="weekday", time_of_day="day"
    )
    t_cached_road = time.time() - t0
    print(f"3. Cached Road Flows: {t_cached_road:.4f}s (Returned {len(res.get('data', {}).get('features', []))} segments)")
    
    # 4. Uncached Road Flows (with parallel download)
    t0 = time.time()
    res = get_road_flows(
        min_lat=u_lat - lat_span/2, max_lat=u_lat + lat_span/2,
        min_lng=u_lng - lng_span/2, max_lng=u_lng + lng_span/2,
        day="weekday", time_of_day="day"
    )
    t_uncached_road = time.time() - t0
    print(f"4. Uncached Road Flows (Parallel Fetch): {t_uncached_road:.4f}s (Returned {len(res.get('data', {}).get('features', []))} segments)")
    
    # 5. Hot-Cache Road Flows (after caching the above uncached area)
    t0 = time.time()
    res = get_road_flows(
        min_lat=u_lat - lat_span/2, max_lat=u_lat + lat_span/2,
        min_lng=u_lng - lng_span/2, max_lng=u_lng + lng_span/2,
        day="weekday", time_of_day="day"
    )
    t_hot_road = time.time() - t0
    print(f"5. Hot-Cache Road Flows: {t_hot_road:.4f}s (Returned {len(res.get('data', {}).get('features', []))} segments)")
    
    print("====================================================")
    print("Benchmark complete. All endpoints compile & run successfully.")

if __name__ == "__main__":
    run_benchmark()
