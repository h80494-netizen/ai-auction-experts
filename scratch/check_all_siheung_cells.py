import sqlite3
db_path = 'backend/data/map_data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cells = [(3737, 12679), (3737, 12680), (3738, 12679), (3738, 12680)]
for lat_idx, lng_idx in cells:
    cursor.execute("SELECT COUNT(*) FROM road_cache_grids WHERE lat_idx=? AND lng_idx=?", (lat_idx, lng_idx))
    print(f"Cell ({lat_idx}, {lng_idx}) cached?", cursor.fetchone()[0])
conn.close()
