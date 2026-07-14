import os
import sys

# Add backend directory to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend'))
sys.path.insert(0, backend_dir)

from app import get_grid_demographics

# Bundang BBox:
# min_lat=37.339, max_lat=37.342, min_lng=127.100, max_lng=127.112
res_res = get_grid_demographics(
    min_lat=37.339,
    max_lat=37.342,
    min_lng=127.100,
    max_lng=127.112,
    type="residential",
    regions="서울,경기,인천"
)

print("Residential Grid Results (Bundang):")
print(f"Status: {res_res.get('status')}")
print(f"Number of grids: {len(res_res.get('data', []))}")
if res_res.get('data'):
    print("Sample grid:", res_res.get('data')[0])

res_work = get_grid_demographics(
    min_lat=37.339,
    max_lat=37.342,
    min_lng=127.100,
    max_lng=127.112,
    type="workplace",
    regions="서울,경기,인천"
)

print("\nWorkplace Grid Results (Bundang):")
print(f"Status: {res_work.get('status')}")
print(f"Number of grids: {len(res_work.get('data', []))}")
if res_work.get('data'):
    print("Sample grid:", res_work.get('data')[0])
