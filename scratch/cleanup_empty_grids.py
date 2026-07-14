import sqlite3
import os

db_path = 'backend/data/map_data.db'
if not os.path.exists(db_path):
    db_path = 'map_data.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all cached grids
cursor.execute("SELECT lat_idx, lng_idx FROM road_cache_grids")
grids = cursor.fetchall()
print(f"Total cached grids: {len(grids)}")

empty_grids = []
for lat_idx, lng_idx in grids:
    c_min_lat = lat_idx * 0.01
    c_max_lat = (lat_idx + 1) * 0.01
    c_min_lng = lng_idx * 0.01
    c_max_lng = (lng_idx + 1) * 0.01
    
    cursor.execute("""
        SELECT COUNT(*) FROM road_cache_segments
        WHERE max_lat >= ? AND min_lat <= ? AND max_lng >= ? AND min_lng <= ?
    """, (c_min_lat, c_max_lat, c_min_lng, c_max_lng))
    count = cursor.fetchone()[0]
    
    if count == 0:
        empty_grids.append((lat_idx, lng_idx))

print(f"Found {len(empty_grids)} empty cached grids.")
if empty_grids:
    print("Sample empty grids:", empty_grids[:10])
    # Delete them
    cursor.executemany("DELETE FROM road_cache_grids WHERE lat_idx = ? AND lng_idx = ?", empty_grids)
    conn.commit()
    print("Successfully deleted empty grids from road_cache_grids.")

conn.close()
