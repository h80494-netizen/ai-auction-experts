import sqlite3
import json
import os
import sys

# Add backend directory to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend'))
sys.path.insert(0, backend_dir)

from app import get_map_auctions

# Coordinates with known auctions:
# lat: 37.3400460812357, lng: 127.106971003356
res = get_map_auctions(
    min_lat=37.339,
    max_lat=37.342,
    min_lng=127.100,
    max_lng=127.112,
    regions="서울,경기,인천"
)

print("Bundang results with regions=서울,경기,인천:")
print(f"Status: {res.get('status')}")
print(f"Count: {len(res.get('data', []))}")
if res.get('data'):
    print("Sample auction address:", res.get('data')[0].get('address'))

res_default = get_map_auctions(
    min_lat=37.339,
    max_lat=37.342,
    min_lng=127.100,
    max_lng=127.112,
    regions="서울" # default when only Seoul checked
)
print("\nBundang results with regions=서울:")
print(f"Count: {len(res_default.get('data', []))}")

res_no_regions = get_map_auctions(
    min_lat=37.339,
    max_lat=37.342,
    min_lng=127.100,
    max_lng=127.112,
    regions=None # no regions filter
)
print("\nBundang results with regions=None:")
print(f"Count: {len(res_no_regions.get('data', []))}")
