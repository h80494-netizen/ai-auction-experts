import sqlite3

db_path = 'backend/data/map_data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check cached cells around Bundang (37.38, 127.12) -> cell index: lat_idx = 3738, lng_idx = 12712
cursor.execute("SELECT * FROM road_cache_grids WHERE lat_idx=3738 AND lng_idx=12712")
print("Bundang grid cell in cache:", cursor.fetchall())

# Check road cache segments in the BBox
min_lat, max_lat, min_lng, max_lng = 37.380, 37.385, 127.120, 127.125
cursor.execute('''
    SELECT COUNT(*) FROM road_cache_segments
    WHERE max_lat >= ? AND min_lat <= ? AND max_lng >= ? AND min_lng <= ?
''', (min_lat, max_lat, min_lng, max_lng))
count = cursor.fetchone()[0]
print(f"Number of road segments in BBox: {count}")

conn.close()
