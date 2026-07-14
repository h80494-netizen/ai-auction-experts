import sys
import os
import time

# Add backend directory to sys.path
sys.path.append(os.path.abspath('backend'))

import app
import sqlite3

# Initialize app-like globals if needed
app.DB_PATH = 'backend/data/map_data.db'

print("Running demographics test...")
lat, lng = 37.380, 126.803
pad_lat = 0.003
pad_lng = 0.004

min_lat = lat - pad_lat
max_lat = lat + pad_lat
min_lng = lng - pad_lng
max_lng = lng + pad_lng

start = time.time()
try:
    res = app.get_grid_demographics(
        min_lat=min_lat,
        max_lat=max_lat,
        min_lng=min_lng,
        max_lng=max_lng,
        type="floating",
        regions="서울,경기,인천"
    )
    duration = time.time() - start
    print("Status:", res.get("status"))
    print("Grids count:", len(res.get("data", [])))
    print("Duration:", duration, "seconds")
except Exception as e:
    print("Error:", e)
