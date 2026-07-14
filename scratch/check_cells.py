import sqlite3
conn = sqlite3.connect('backend/data/map_data.db')
print("road_cache_grids count for 3737, 12712:", conn.execute("SELECT COUNT(*) FROM road_cache_grids WHERE lat_idx=3737 AND lng_idx=12712").fetchone()[0])
print("road_cache_segments count for min_lat between 37.37 and 37.38:", conn.execute("SELECT COUNT(*) FROM road_cache_segments WHERE min_lat BETWEEN 37.37 AND 37.38").fetchone()[0])
conn.close()
