import sqlite3
import os
import time

db_path = 'backend/data/map_data.db'
if not os.path.exists(db_path):
    db_path = 'map_data.db'

print(f"Connecting to {db_path}...")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

start_time = time.time()

# 1. Get all cached grids
cursor.execute("SELECT lat_idx, lng_idx FROM road_cache_grids")
grids = set(cursor.fetchall())
print(f"Total cached cells in road_cache_grids: {len(grids)}")

# 2. Get all segments bounds
cursor.execute("SELECT min_lat, max_lat, min_lng, max_lng FROM road_cache_segments")
segments = cursor.fetchall()
print(f"Total segments in road_cache_segments: {len(segments)}")

# 3. Mark cells that contain segments
cells_with_segments = set()
for min_lat, max_lat, min_lng, max_lng in segments:
    lat_start = int(min_lat / 0.01)
    lat_end = int(max_lat / 0.01)
    lng_start = int(min_lng / 0.01)
    lng_end = int(max_lng / 0.01)
    for la in range(lat_start, lat_end + 1):
        for ln in range(lng_start, lng_end + 1):
            cells_with_segments.add((la, ln))

# 4. Find empty cells
empty_cells = [g for g in grids if g not in cells_with_segments]
print(f"Found {len(empty_cells)} empty cached grid cells.")

if empty_cells:
    print("Deleting empty grid cells from road_cache_grids...")
    cursor.executemany("DELETE FROM road_cache_grids WHERE lat_idx = ? AND lng_idx = ?", empty_cells)
    conn.commit()
    print("Empty grid cells deleted successfully.")

print(f"Duration: {time.time() - start_time:.4f} seconds")
conn.close()
