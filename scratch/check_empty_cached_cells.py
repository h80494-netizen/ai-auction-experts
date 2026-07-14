import sqlite3
import os

db_path = 'backend/data/map_data.db'
if not os.path.exists(db_path):
    db_path = 'map_data.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all cached grids
cursor.execute("SELECT lat_idx, lng_idx FROM road_cache_grids")
cached_cells = cursor.fetchall()
print(f"Total cached cells in road_cache_grids: {len(cached_cells)}")

empty_cells = []
for lat_idx, lng_idx in cached_cells:
    min_lat = lat_idx * 0.01
    max_lat = (lat_idx + 1) * 0.01
    min_lng = lng_idx * 0.01
    max_lng = (lng_idx + 1) * 0.01
    
    # Check if there are any segments in this cell
    cursor.execute("""
        SELECT COUNT(*) FROM road_cache_segments 
        WHERE max_lat >= ? AND min_lat <= ? AND max_lng >= ? AND min_lng <= ?
    """, (min_lat, max_lat, min_lng, max_lng))
    count = cursor.fetchone()[0]
    
    if count == 0:
        empty_cells.append((lat_idx, lng_idx))

print(f"Number of cached cells with 0 segments: {len(empty_cells)}")
if empty_cells:
    print("Sample empty cells (first 10):", empty_cells[:10])

conn.close()
