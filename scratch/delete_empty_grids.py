import sqlite3
import os

db_path = 'backend/data/map_data.db'
if not os.path.exists(db_path):
    db_path = 'map_data.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get empty cached grids using a fast SQL EXISTS check
print("Querying empty cells from database...")
cursor.execute("""
    SELECT lat_idx, lng_idx FROM road_cache_grids g
    WHERE NOT EXISTS (
        SELECT 1 FROM road_cache_segments s
        WHERE s.max_lat >= g.lat_idx * 0.01 
          AND s.min_lat <= (g.lat_idx + 1) * 0.01 
          AND s.max_lng >= g.lng_idx * 0.01 
          AND s.min_lng <= (g.lng_idx + 1) * 0.01
    )
""")
empty_grids = cursor.fetchall()
print(f"Found {len(empty_grids)} empty grid cells in road_cache_grids.")

if empty_grids:
    print("Deleting empty grid cells from road_cache_grids...")
    cursor.executemany("""
        DELETE FROM road_cache_grids WHERE lat_idx = ? AND lng_idx = ?
    """, empty_grids)
    conn.commit()
    print("Empty grid cells deleted successfully.")

conn.close()
